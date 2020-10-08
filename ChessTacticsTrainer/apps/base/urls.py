from django.contrib import admin
from django.urls import path


from . import views

urlpatterns = [
    path('', views.home),
    path('login', views.submit_login),
    path('register', views.register),
    path('try-without-account', views.no_auth_home),
    path('start-training', views.start_training),
    path('progress', views.progress),
    path('settings', views.settings),
    path('update_settings', views.update_settings),
    path('logout', views.submit_logout),
    path('make_move', views.stockfish_reply)
]