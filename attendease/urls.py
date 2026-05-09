"""
AttendEAse — Project-level URL configuration.
Routes to users, events, and attendance apps.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Root redirects to dashboard (or login if not authenticated)
    path('', lambda request: redirect('users:redirect_dashboard') if request.user.is_authenticated else redirect('users:login')),

    # App URLs
    path('auth/', include('users.urls')),
    path('events/', include('events.urls')),
    path('attendance/', include('attendance.urls')),
]
