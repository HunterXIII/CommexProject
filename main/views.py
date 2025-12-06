from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import TemplateView
from django.views.generic import * 
from .mixins import *
from .models import *
from .forms import *
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST

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
        chats = (Chat.objects
                 .filter(users=self.request.user)
                 .prefetch_related('users', 'messages')
                 .order_by('-date_of_creation'))
        for chat in chats:
            chat.companion = chat.get_companion(self.request.user)
        context["chats"] = chats
        return context
    
    
class ChatSearchList(ListView):
    model = MessengerUser
    template_name = "main/chats/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("username")
        if search:
            context["search_users"] = MessengerUser.objects.filter(username__icontains=search).difference(MessengerUser.objects.filter(username=self.request.user.username))
        else:
            context["search_users"] = MessengerUser.objects.none()
        return context
    

class ChatView(ChatAccessMixin, DetailView):
    model = Chat
    template_name = "main/chats/chat_detail.html"
    context_object_name = "chat"

    def get_context_data(self, **kwargs):
        chat = get_object_or_404(Chat, id=self.kwargs.get('pk'))
        context = super().get_context_data(**kwargs)
        context["companion"] = chat.get_companion(self.request.user)
        context["messages"] = chat.messages.all()
        return context
    
    def post(self, *args, **kwargs):
        chat = get_object_or_404(Chat, id=self.kwargs.get('pk'))
        companion = chat.get_companion(self.request.user)
        content = self.request.POST.get('content').strip()
        if content:
            TextMessage.objects.create(chat=chat, sender=self.request.user, content=content)
            if companion:
                chat.messages.filter(sender=companion, is_read=False).update(is_read=True)
        return redirect('chat_detail', self.kwargs.get('pk'))


@login_required
@require_POST
def start_chat(request, user_id):
    companion = get_object_or_404(MessengerUser, id=user_id)
    if companion == request.user:
        return redirect('chat_search')

    chat = (Chat.objects
            .filter(users=request.user)
            .filter(users=companion)
            .distinct()
            .first())

    if chat is None:
        chat = Chat.objects.create(name=f"Chat {request.user.username}-{companion.username}")
        chat.users.add(request.user, companion)

    return redirect('chat_detail', chat.pk)


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(TextMessage, id=message_id)
    if message.sender != request.user:
        return HttpResponseForbidden("You are not allowed to delete this message")
    cancel_url = reverse('chat_detail', args=[message.chat.id])
    if request.method == 'POST':
        message.delete()
        return redirect(cancel_url)
    context = {
        "object_type": "message",
        "title": "Удалить сообщение",
        "description": "Сообщение исчезнет для всех участников этого чата. "
                       "Действие необратимо.",
        "form_action": reverse('delete_message', args=[message.id]),
        "cancel_url": cancel_url,
        "message": message,
    }
    return render(request, 'main/chats/delete_confirm.html', context)


@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if not chat.has_participant(request.user):
        return HttpResponseForbidden("You are not allowed to delete this chat")
    if request.method == 'POST':
        chat.delete()
        return redirect('chat_list')
    companion = chat.get_companion(request.user)
    companion_name = companion.username if companion else "неизвестным пользователем"
    context = {
        "object_type": "chat",
        "title": "Удалить чат",
        "description": f"Вся история общения с {companion_name} будет удалена без возможности восстановления.",
        "form_action": reverse('delete_chat', args=[chat.id]),
        "cancel_url": reverse('chat_detail', args=[chat.id]),
        "chat": chat,
        "companion": companion,
        "messages_count": chat.messages.count(),
    }
    return render(request, 'main/chats/delete_confirm.html', context)


class ProfileView(DetailView):
    model = MessengerUser
    template_name = "main/profile.html"
    context_object_name = "profile"