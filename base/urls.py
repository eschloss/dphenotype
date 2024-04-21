"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from base import views

urlpatterns = [
    path('', views.home),
    path('gather_question_instances/', views.gather_question_instances),
    path('gather_question_instances_ff/', views.gather_question_instances_ff),
    path('set_notification_token/', views.set_notification_token),
    path('set_question_instance/', views.set_question_instance),
    path('set_emoji/', views.set_emoji),
    path('get_past_emojis/', views.get_past_emojis),
    path('get_average_emojis/', views.get_average_emojis),
    path('passive/add/', views.add_passive_data),
    path('login/', views.login),
]
