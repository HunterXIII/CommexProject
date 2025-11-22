from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import *
from django.db.models import Q
from .models import *
from .forms import *


def home(request):
    return render(request, 'main/home.html')


def register(request):
    if request.method == 'POST':
        form = MessengerUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_list')
    else:
        form = MessengerUserCreationForm()
    return render(request, 'main/registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('chat_list')
    else:
        form = AuthenticationForm()
    return render(request, 'main/registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def chat_list(request):
    chats = Chat.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by('-date_of_creation')
    return render(request, 'main/chats/chat_list.html', {'chats': chats})


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in (chat.user1, chat.user2):
        return redirect('chat_list')

    companion = chat.user2 if request.user == chat.user1 else chat.user1
    messages = chat.messages.all()

    if request.method == 'POST':
        content = request.POST.get('content').strip()
        if content:
            TextMessage.objects.create(chat=chat, sender=request.user, content=content)
            chat.messages.filter(sender=companion, is_read=False).update(is_read=True)
        return redirect('chat_detail', chat_id)

    return render(request, 'main/chats/chat_detail.html', {
        'chat': chat,
        'companion': companion,
        'messages': messages
    })