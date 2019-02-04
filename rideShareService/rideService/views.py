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
from django.contrib.messages.views import SuccessMessageMixin

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

def email(request):
    subject = "Test Email from django"
    message = "Happy New Year!"
    fromMail = "xBer@ece.com"
    toMail = ["naixin.yu@duke.edu"]
    send_mail(subject, message, fromMail, toMail, fail_silently=False)
    return HttpResponse("Send E-mail Success!")

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
@login_required
def role(request):
    context = {'isDriver' : True}
    try:
        driver = Driver.objects.get(account=request.user)
        print(driver.id)
        context = {'isDriver' : True,
                    'driverID' : driver.id}
    except Driver.DoesNotExist:
        context = {'isDriver' : False}
    return render(request, 'rideService/role.html', context)


# Ride Create/Edit/Delete (Owner)
class RequestCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Request
    fields = ['destination', 'arrival_time', 'num_passengers', 'shareable', 'vehicle_type', 'special_request']
    success_url = reverse_lazy('owner-all-requests')
    success_message = "Route %(destination)s was created successfully!"
    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        form.instance.confirmed = False
        form.instance.status = "open"
        return super().form_valid(form)

class RequestUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Request
    fields = ['destination', 'arrival_time', 'num_passengers', 'shareable', 'vehicle_type', 'special_request']
    template_name = 'rideService/request_update.html'
    success_url = reverse_lazy('owner-all-requests')
    success_message = "Route %(destination)s was updated successfully!"
    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        form.instance.confirmed = False
        return super().form_valid(form)

    def test_func(self):
        current = self.get_object()
        if self.request.user == current.ride_owner:
            return True
        return False

class RequestDeleteView(LoginRequiredMixin, SuccessMessageMixin,UserPassesTestMixin, DeleteView):
    model = Request
    success_url = reverse_lazy('owner-all-requests')
    success_message = "Route was deleted sucessfully!"
    def test_func(self):
        current = self.get_object()
        if self.request.user == current.ride_owner:
            return True
        return False


# Ride Searching/Status Viewing (Owner)
@login_required
def ownerRequest(request):
    context = {
        'request_confirmed': Request.objects.filter(ride_owner=request.user, status='confirmed'),
        'requests_unconfirmed': Request.objects.filter(ride_owner=request.user, status='open'),
        'request_complete': Request.objects.filter(ride_owner=request.user, status='complete'),
    }
    num = len(context['request_confirmed']) + len(context['requests_unconfirmed']) + len(context['request_complete'])
    context['num'] = num
    return render(request, 'rideService/owner_request.html', context)

class RequestDetailView(LoginRequiredMixin,DetailView):
    model = Request


# Ride Searching/Status Viewing (Driver)
@login_required
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

@login_required
def driverAccpetRequest(request, pk, time):
    thisRequest = Request.objects.get(id=pk)
    timestamp = time[:15]
    original_timestamp = str(thisRequest.last_updated)[:15]
    if timestamp != original_timestamp:
        print("timestamp doesn't match")
        return redirect('role')
    messages.success(request, 'Requset Confirmed')
    thisRequest.driver = Driver.objects.get(account=request.user)
    thisRequest.status = 'confirmed'
    thisRequest.save()
    sendCloseEmail(pk)
    return redirect('role')

@login_required
def driverConfirmedRides(request):
    thisDriver = Driver.objects.get(account=request.user)
    context = {
        'driver': thisDriver,
        'requests': Request.objects.filter(driver=thisDriver, status='confirmed')
    }
    return render(request, 'rideService/driver_confirmed_request.html', context)

class DriverRequestDetailView(LoginRequiredMixin,DetailView):
    model = Request
    template_name = 'rideService/driver_request_detail.html'

class DriverConfirmedRequestDetailView(LoginRequiredMixin,DetailView):
    model = Request
    template_name = 'rideService/driver_confirmed_request_detail.html'


@login_required
def DriverCompleteRides(request, pk):
    thisRequest = Request.objects.get(id=pk)
    thisRequest.status = 'complete'
    thisRequest.save()
    return driverConfirmedRides(request)

# Registration/Edit (Driver)
class DriverCreateView(LoginRequiredMixin, CreateView):
    model = Driver
    fields = ['vehicle_type', 'license_number', 'max_passengers', 'special_info']
    success_url = reverse_lazy('role')
    success_message = "You have been registed as driver successfully"
    def form_valid(self, form):
        form.instance.account = self.request.user
        return super().form_valid(form)

class DriverUpdateView(LoginRequiredMixin, UpdateView):
    model = Driver
    fields = ['vehicle_type', 'license_number', 'max_passengers', 'special_info']
    success_url = reverse_lazy('role')
    success_message = "Your profile has been updated successfully"
    def form_valid(self, form):
        form.instance.account = self.request.user
        return super().form_valid(form)

    def test_func(self):
        current = self.get_object()
        if self.request.user == current.account:
            return True
        return False

class DriverDetailView(LoginRequiredMixin,DetailView):
    model = Driver
    template_name = 'rideService/driver_profile.html'


# Ride Searching (Sharer)
@login_required
def SharerSearchView(request):
    if request.method == 'POST':
        form = SharerSearchForm(request.POST)
        if form.is_valid():
            des = form.cleaned_data.get('destinationFromSharer')
            time_before = form.cleaned_data.get('arrival_time_before')
            time_after = form.cleaned_data.get('arrival_time_after')
            num_sharer = form.cleaned_data.get('num_sharer')
            context = {
                'num_sharer' : num_sharer,
                'Certified_Request': Request.objects.filter(destination=des, 
                                                            arrival_time__gt = time_after, 
                                                            arrival_time__lt = time_before,
                                                            shareable = True,
                                                            status='open'),
            }
            return render(request, 'rideService/sharer_allrequests.html', context)
    else:
        form = SharerSearchForm()
    return render(request, 'rideService/sharer_search.html', {'form':form})

@login_required
def sharerJoinRide(request, pk, num_sharer):
    thisRequest = Request.objects.get(id=pk)
    if thisRequest.status != "open" or thisRequest.shareable == False:
        print("This ride cannot be joined")
        return redirect('role')
    thisRequest.sharer = request.user
    thisRequest.num_sharer = num_sharer
    thisRequest.save()
    print("join success")
    return redirect('role')

@login_required
def sharerLeaveRide(request, pk):
    thisRequest = Request.objects.get(id=pk)
    if thisRequest.status != "open":
        print("You cannot edit this request")
        return redirect('role')
    thisRequest.sharer = None
    thisRequest.num_sharer = 0
    thisRequest.save()
    return redirect('role')

@login_required
def sharerViewRides(request):
    context = {
        'requests': Request.objects.filter(sharer=request.user)
    }
    return render(request, 'rideService/sharer_request_detail.html', context)


def sendCloseEmail(pk):
    thisRequest = Request.objects.get(id=pk)
    subject = "Your Ride to " + thisRequest.destination + " is Complete"
    message = "Thank you for riding with Xber! Your Ride to " + thisRequest.destination + " is Confirmed."
    toMail = [thisRequest.ride_owner.email]
    if thisRequest.num_sharer > 0:
        toMail.append(thisRequest.sharer.email)
    send_mail(subject, message, "xBer@ece.com", toMail)


