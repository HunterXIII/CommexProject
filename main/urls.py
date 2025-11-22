from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('chats/', ChatListView.as_view(), name='chat_list'),
    path('chat/<int:pk>/', ChatView.as_view(), name='chat_detail'),
]