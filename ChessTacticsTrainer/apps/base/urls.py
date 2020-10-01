from django.contrib import admin
from django.urls import path


from . import views

urlpatterns = [
    path('', views.home),
    path('login', views.submit_login),
    path('register', views.register),
    path('start-training', views.start_training),
    path('progress', views.progress),
    path('preferences', views.preferences),
    path('logout', views.submit_logout)
]