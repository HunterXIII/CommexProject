from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
]