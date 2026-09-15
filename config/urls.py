"""
AttendEase — project-level URL configuration.
Delegates to each app's own urls.py for app-specific routes.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

from config.views import about

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Root — send authenticated users to their dashboard, others to login
    path('', lambda request: (
        redirect('users:redirect_dashboard')
        if request.user.is_authenticated
        else redirect('users:login')
    )),

    # Project-wide pages
    path('about/', about, name='about'),

    # App routes
    path('auth/',        include('users.urls')),
    path('events/',      include('events.urls')),
    path('attendance/',  include('attendance.urls')),
]
