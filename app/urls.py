from django import views

from .views import home, about, contact, savedata
from django.urls import path 
from . import views


urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('savedata/', savedata, name='savedata'),
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
    path('history/', views.chat_history, name='chat_history'),
    path('history/<int:id>/', views.chat_detail, name='chat_detail'),
]