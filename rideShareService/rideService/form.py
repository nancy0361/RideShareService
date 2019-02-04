from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SharerSearchForm(forms.Form):
    destinationFromSharer = forms.CharField(label='Destination', max_length=100)
    arrival_time_after = forms.DateTimeField(label='Arrive After')
    arrival_time_before = forms.DateTimeField(label='Arrive Before')
    num_sharer = forms.IntegerField(label='Passenger Number', max_value=10, min_value=1)