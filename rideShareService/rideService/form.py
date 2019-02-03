from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SharerSearchForm(forms.Form):
    destinationFromSharer = forms.CharField(label='destination_Sharer', max_length=100)
    arrival_timeFromSharer = forms.DateTimeField()
    num_sharer = forms.IntegerField(max_value=10, min_value=1)