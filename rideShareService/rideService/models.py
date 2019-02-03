from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
# from rideService.models import Driver, Request

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
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, default=None, null=True)
    sharer = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True, related_name='sharer_request')
    destination = models.CharField(max_length=1000)
    arrival_time = models.DateTimeField()
    num_passengers = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    num_sharer = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ]
    )
    shareable = models.BooleanField(default=False)
    vehicle_type = models.CharField(max_length=200, null=True, blank=True)
    special_request = models.TextField(blank=True)
    status = models.CharField(max_length=1000)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        print("---------------------------")
        print("Created by:\t" + self.ride_owner.username)
        print("Destination:\t" + self.destination)
        print("Status:\t\t" + self.status)
        return str(self.id)
