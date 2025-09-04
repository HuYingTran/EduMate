from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/start/', views.start_chat, name='start_chat'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/history/<str:session_id>/', views.get_chat_history, name='chat_history'),
    path('chat/save-info/', views.save_user_info, name='save_user_info'),
]