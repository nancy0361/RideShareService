from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Driver, Request
from .form import UserRegisterForm, SharerSearchForm
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

# Test
def index(request):
    return HttpResponse("Hello, world. You're at the rideService index.")

def home(request):
    accounts = User.objects.order_by('username')[:5]
    context = {'accounts' : accounts}
    return render(request, 'rideService/index.html', context)


# Account
def register(request):
    if request.method == 'POST':  # data sent by user
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # this will save Car info to database
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'rideService/register.html', {'form':form})


# Homepage
def role(request):
    context = {'isDriver' : True}
    try:
        driver = Driver.objects.get(account=request.user)
    except Driver.DoesNotExist:
        context = {'isDriver' : False}
    return render(request, 'rideService/role.html', context)


# Ride Create/Edit/Delete (Owner)
class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Request
    fields = ['destination', 'arrival_time', 'num_passengers', 'shareable', 'vehicle_type', 'special_request']
    success_url = reverse_lazy('owner-all-requests')

    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        form.instance.confirmed = False
        form.instance.status = "open"
        return super().form_valid(form)

class RequestUpdateView(LoginRequiredMixin, UpdateView):
    model = Request
    fields = ['destination', 'arrival_time', 'num_passengers', 'shareable', 'vehicle_type', 'special_request']
    template_name = 'rideService/request_update.html'
    success_url = reverse_lazy('owner-all-requests')

    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        form.instance.confirmed = False
        return super().form_valid(form)

    def test_func(self):
        current = self.get_object()
        if self.request.user == current.ride_owner:
            return True
        return False

class RequestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Request
    success_url = reverse_lazy('owner-all-requests')

    def test_func(self):
        current = self.get_object()
        if self.request.user == current.ride_owner:
            return True
        return False


# Ride Searching/Status Viewing (Owner)
def ownerRequest(request):
    context = {
        'request_confirmed': Request.objects.filter(ride_owner=request.user, status='confirmed'),
        'requests_unconfirmed': Request.objects.filter(ride_owner=request.user, status='open')
    }
    return render(request, 'rideService/owner_request.html', context)

class RequestDetailView(DetailView):
    model = Request


# Ride Searching/Status Viewing (Driver)
def driverFindRequest(request):
    thisDriver = Driver.objects.get(account=request.user)
    requests = []
    candidateRequests = Request.objects.filter(
        status='open',
        arrival_time__gt=datetime.now()
        )
    for req in candidateRequests:
        num = req.num_passengers + req.num_sharer
        if num > thisDriver.max_passengers:
            continue
        if req.vehicle_type and req.vehicle_type != thisDriver.vehicle_type:
            continue
        if req.special_request and req.special_request != thisDriver.special_info:
            continue
        requests.append(req)
    
    context = {
        'driver': thisDriver,
        'requests': requests
    }
    
    return render(request, 'rideService/driver_find_request.html', context)

def driverAccpetRequest(request, pk, timestamp):
    print(timestamp)
    thisRequest = Request.objects.get(id=pk)
    if timestamp != thisRequest.last_updated:
        print("timestamp doesn't match")


    thisRequest.driver = Driver.objects.get(account=request.user)
    thisRequest.status = 'confirmed'
    thisRequest.save()
    return render(request, 'rideService/role.html', {'isDriver' : True})

def driverConfirmedRides(request):
    thisDriver = Driver.objects.get(account=request.user)
    context = {
        'driver': thisDriver,
        'requests': Request.objects.filter(driver=thisDriver, status='confirmed')
    }
    return render(request, 'rideService/driver_confirmed_request.html', context)

class DriverRequestDetailView(DetailView):
    model = Request
    template_name = 'rideService/driver_request_detail.html'

def DriverCompleteRides(request, pk):
    thisRequest = Request.objects.get(id=pk)
    thisRequest.status = 'complete'
    thisRequest.save()
    # sendCloseEmail(pk)
    return driverConfirmedRides(request)

# Registration/Edit (Driver)
class DriverCreateView(LoginRequiredMixin, CreateView):
    model = Driver
    fields = ['vehicle_type', 'license_number', 'max_passengers', 'special_info']
    success_url = reverse_lazy('role')

    def form_valid(self, form):
        form.instance.account = self.request.user
        return super().form_valid(form)

class DriverUpdateView(LoginRequiredMixin, UpdateView):
    model = Driver
    fields = ['vehicle_type', 'license_number', 'max_passengers', 'special_info']

    def form_valid(self, form):
        form.instance.account = self.request.user
        return super().form_valid(form)

    def test_func(self):
        current = self.get_object()
        if self.request.user == current.account:
            return True
        return False

# Ride Searching (Sharer)
@login_required
def SharerSearchView(request):
    if request.method == 'POST':
        form = SharerSearchForm(request.POST)
        if form.is_valid():
            des = form.cleaned_data.get('destinationFromSharer')
            time = form.cleaned_data.get('arrival_timeFromSharer')
            num_sharer = form.cleaned_data.get('num_sharer')
            context = {
                'num_sharer' : num_sharer,
                'Certified_Request': Request.objects.filter(destination=des, 
                                                            arrival_time = time, 
                                                            shareable = True,
                                                            status='open'),
            }
            return render(request, 'rideService/sharer_allrequests.html', context)
    else:
        form = SharerSearchForm()
    return render(request, 'rideService/sharer_search.html', {'form':form})


def sharerJoinRide(request, pk, num_sharer):
    thisRequest = Request.objects.get(id=pk)
    if thisRequest.status != "open" or thisRequest.shareable == False:
        print("This ride cannot be joined")
        return render(request, 'rideService/role.html', {'isDriver' : True})
    thisRequest.sharer = request.user
    thisRequest.num_sharer = num_sharer
    thisRequest.save()
    print("join success")
    return render(request, 'rideService/role.html', {'isDriver' : True})

def sharerLeaveRide(request, pk):
    thisRequest = Request.objects.get(id=pk)
    if thisRequest.status != "open":
        print("You cannot edit this request")
        return render(request, 'rideService/role.html', {'isDriver' : True})
    thisRequest.sharer = None
    thisRequest.num_sharer = 0
    thisRequest.save()
    print("leave ride " + pk)
    return render(request, 'rideService/role.html', {'isDriver' : True})

def sharerViewRides(request):
    context = {
        'requests': Request.objects.filter(sharer=request.user)
    }
    return render(request, 'rideService/sharer_request_detail.html', context)






# def sendCloseEmail(pk):
#     thisRequest = Request.objects.get(id=pk)
#     subject = "Your Ride to " + thisRequest.destination + " is Complete"
#     message = "Thank you fro riding with Xber! Your Ride to " + thisRequest.destination + " is Complete"
#     fromMail = "xBer@ece.com"
#     toMail = [thisRequest.ride_owner.email]
#     if thisRequest.num_sharer > 0:
#         toMail.append(thisRequest.sharer.email)
#     send_mail(subject, message, fromMail, toMail)


