from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import TemplateView
from django.views.generic import * 
from django.db.models import Q
from .mixins import *
from .models import *
from .forms import *


class HomeView(TemplateView):
    template_name = "main/home.html"


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


class ChatListView(ListView):
    model = Chat
    template_name = "main/chats/chat_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chats"] = Chat.objects.filter(Q(user1=self.request.user) | Q(user2=self.request.user)).order_by('-date_of_creation')
        return context
    

class ChatView(ChatAccessMixin, DetailView):
    model = Chat
    template_name = "main/chats/chat_detail.html"

    def get_context_data(self, **kwargs):
        chat = get_object_or_404(Chat, id=self.kwargs.get('pk'))
        context = super().get_context_data(**kwargs)
        context["companion"] = chat.user2 if self.request.user == chat.user1 else chat.user1
        context["messages"] = chat.messages.all()
        return context
    
    def post(self, *args, **kwargs):
        chat = get_object_or_404(Chat, id=self.kwargs.get('pk'))
        companion = chat.user2 if self.request.user == chat.user1 else chat.user1
        content = self.request.POST.get('content').strip()
        if content:
            TextMessage.objects.create(chat=chat, sender=self.request.user, content=content)
            chat.messages.filter(sender=companion, is_read=False).update(is_read=True)
        return redirect('chat_detail', self.kwargs.get('pk'))
