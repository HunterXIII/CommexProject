# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MessengerUser


class MessengerUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MessengerUser
        fields = ('username', 'email', 'birthday', 'profile_image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем стандартные английские подсказки
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Добавляем красивые классы Bootstrap
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class MessengerUserChangeForm(UserChangeForm):
    class Meta:
        model = MessengerUser
        fields = ('username', 'email', 'birthday', 'profile_image', 'status')