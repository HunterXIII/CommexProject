from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    path('chats/', ChatListView.as_view(), name='chat_list'),
    path('chats/search/', ChatSearchList.as_view(), name='chat_search'),
    path('chats/start/<int:user_id>/', StartChatView.as_view(), name='chat_start'),
    path('chat/<int:pk>/', ChatView.as_view(), name='chat_detail'),
    
    path('chat/<int:chat_id>/delete/', ChatDeleteView.as_view(), name='delete_chat'),
    path('message/<int:message_id>/delete/', MessageDeleteView.as_view(), name='delete_message'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
]