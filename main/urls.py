from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    path('chats/', ChatListView.as_view(), name='chat_list'),
    path('chats/search/', ChatSearchList.as_view(), name='chat_search'),
    path('chat/<int:pk>/', ChatView.as_view(), name='chat_detail'),
    
    path('chat/<int:chat_id>/delete/', delete_chat, name='delete_chat'),
    path('message/<int:message_id>/delete/', delete_message, name='delete_message'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
]