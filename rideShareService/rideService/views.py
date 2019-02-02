from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .models import Sharer, Driver, Request
from .form import UserRegisterForm
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView
)

def index(request):
    return HttpResponse("Hello, world. You're at the rideService index.")

def home(request):
    accounts = User.objects.order_by('username')[:5]
    context = {'accounts' : accounts}
    return render(request, 'rideService/index.html', context)

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

def role(request):
    # return render(request, 'rideService/role.html')
    context = {'isDriver' : True}
    try:
        driver = Driver.objects.get(account=request.user)
    except Driver.DoesNotExist:
        context = {'isDriver' : False}
    return render(request, 'rideService/role.html', context)

def ownerRequest(request):
    context = {
        'requests': Request.objects.filter(ride_owner=request.user)
    }
    return render(request, 'rideService/owner_request.html', context)

def driverRequest(request):
    thisDriver = Driver.objects.get(account=request.user)
    context = {
        'requests': Request.objects.filter(status='open')
    }
    return render(request, 'rideService/owner_request.html', context)



class RequestCreateView(LoginRequiredMixin, CreateView):
    model = Request
    fields = ['destination', 'arrival_time', 'num_passengers', 'shareable', 'special_request']
    success_url = reverse_lazy('owner-all-requests')

    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        form.instance.confirmed = False
        form.instance.status = "open"
        return super().form_valid(form)

class RequestUpdateView(LoginRequiredMixin, UpdateView):
    model = Request
    fields = ['destination', 'arrival_time', 'num_passengers', 'shareable', 'special_request']
    template_name = 'rideService/request_update.html'
    success_url = reverse_lazy('owner-all-requests')

    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        form.instance.confirmed = False
        form.instance.status = "request created"
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
