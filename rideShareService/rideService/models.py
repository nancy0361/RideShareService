from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
# from rideService.models import Sharer, Driver, Request

class Sharer(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=200)

    def __str__(self):
        return self.account.username + " : " + self.status


class Driver(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=200)
    license_number = models.CharField(max_length=200)
    max_passengers = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    special_info = models.TextField(blank=True)

    def __str__(self):
        return self.account.username + " and a car " + self.vehicle_type


class Request(models.Model):
    ride_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=1000)
    arrival_time = models.DateTimeField()
    num_passengers = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    shareable = models.BooleanField(default=False)
    special_request = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=1000)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        print("---------------------------")
        print("Created by:\t" + self.ride_owner.username)
        print("Destination:\t" + self.destination)
        print("Status:\t\t" + self.status)
        return str(self.id)