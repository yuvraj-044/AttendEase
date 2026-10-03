"""Users app URL configuration."""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login/firebase/', views.firebase_login_view, name='firebase_login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
]
