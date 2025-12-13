from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.views.generic.base import TemplateView
from django.views.generic import * 
from .mixins import *
from .models import *
from .forms import *
from django.http import HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.views import View

from .crypto.aes import decrypt_message

class HomeView(TemplateView):
    template_name = "main/home.html"


class RegisterView(FormView):
    template_name = "main/registration/register.html"
    form_class = MessengerUserCreationForm
    success_url = reverse_lazy('chat_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class UserLoginView(DjangoLoginView):
    template_name = "main/registration/login.html"
    authentication_form = AuthenticationForm

    def get_success_url(self):
        return reverse('chat_list')


class UserLogoutView(DjangoLogoutView):
    next_page = 'home'


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
        messages = []
        for message in chat.messages.all():
            decode_message = message
            decode_message.content = decrypt_message(message.content, message.iv)
            messages.append(decode_message)
        context["messages"] = messages
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


class StartChatView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, user_id, *args, **kwargs):
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


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = TextMessage
    template_name = "main/chats/delete_confirm.html"
    context_object_name = "message"
    pk_url_kwarg = "message_id"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.sender != request.user:
            return HttpResponseForbidden("You are not allowed to delete this message")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cancel_url = reverse('chat_detail', args=[self.object.chat.id])
        context.update({
            "object_type": "message",
            "title": "Удалить сообщение",
            "description": "Сообщение исчезнет для всех участников этого чата. "
                           "Действие необратимо.",
            "form_action": reverse('delete_message', args=[self.object.id]),
            "cancel_url": cancel_url,
        })
        return context

    def get_success_url(self):
        return reverse('chat_detail', args=[self.object.chat.id])


class ChatDeleteView(LoginRequiredMixin, DeleteView):
    model = Chat
    template_name = "main/chats/delete_confirm.html"
    context_object_name = "chat"
    pk_url_kwarg = "chat_id"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.has_participant(request.user):
            return HttpResponseForbidden("You are not allowed to delete this chat")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        companion = self.object.get_companion(self.request.user)
        companion_name = companion.username if companion else "неизвестным пользователем"
        context.update({
            "object_type": "chat",
            "title": "Удалить чат",
            "description": f"Вся история общения с {companion_name} будет удалена без возможности восстановления.",
            "form_action": reverse('delete_chat', args=[self.object.id]),
            "cancel_url": reverse('chat_detail', args=[self.object.id]),
            "companion": companion,
            "messages_count": self.object.messages.count(),
        })
        return context

    def get_success_url(self):
        return reverse('chat_list')


class ProfileView(DetailView):
    model = MessengerUser
    template_name = "main/profile.html"
    context_object_name = "profile"