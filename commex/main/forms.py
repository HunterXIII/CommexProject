from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MessengerUser

class MessengerUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MessengerUser
        fields = ('username', 'email', 'birthday', 'profile_image')

class MessengerUserChangeForm(UserChangeForm):
    class Meta:
        model = MessengerUser
        fields = ('username', 'email', 'birthday', 'profile_image', 'status')