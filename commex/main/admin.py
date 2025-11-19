from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .forms import MessengerUserCreationForm, MessengerUserChangeForm
from .models import MessengerUser, Chat, TextMessage


@admin.register(MessengerUser)
class MessengerUserAdmin(UserAdmin):
    add_form = MessengerUserCreationForm      
    form = MessengerUserChangeForm             
    model = MessengerUser

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('email', 'birthday', 'profile_image', 'status')}),
        ('Разрешения', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'birthday', 'profile_image', 'status', 'password1', 'password2'),
        }),
    )

    list_display = ('username', 'email', 'birthday', 'status', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'status')
    search_fields = ('username', 'email')

admin.site.register(Chat)
admin.site.register(TextMessage)