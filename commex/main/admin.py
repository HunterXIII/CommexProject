from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import MessengerUser

class MessengerUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = MessengerUser
    list_display = ['email', 'username', 'birthday']

admin.site.register(MessengerUser, MessengerUserAdmin)