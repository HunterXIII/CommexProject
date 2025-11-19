from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import *
from .models import *


@admin.register(MessengerUser)
class MessengerUserAdmin(UserAdmin):
    add_form = MessengerUserCreationForm
    form = MessengerUserChangeForm
    model = MessengerUser

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('email', 'birthday', 'profile_image', 'status')}),
        ('Разрешения', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'birthday', 'profile_image', 'status', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'username', 'birthday', 'status')

admin.site.register(Chat)
admin.site.register(TextMessage)

