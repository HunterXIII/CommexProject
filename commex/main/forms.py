from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = MessengerUser
        fields = ('username', 'email', 'birthday', 'profile_image', 'password')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = MessengerUser
        fields = ('username', 'email', 'birthday', 'profile_image', 'password')
