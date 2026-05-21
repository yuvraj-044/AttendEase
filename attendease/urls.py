"""
AttendEase — Project-level URL configuration.
Routes to users, events, and attendance apps.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from datetime import datetime


@login_required
def about_view(request):
    """About AttendEase page with contributors."""
    return render(request, 'about.html', {'current_year': datetime.now().year})


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Root redirects to dashboard (or login if not authenticated)
    path('', lambda request: redirect('users:redirect_dashboard') if request.user.is_authenticated else redirect('users:login')),

    # About page
    path('about/', about_view, name='about'),

    # App URLs
    path('auth/', include('users.urls')),
    path('events/', include('events.urls')),
    path('attendance/', include('attendance.urls')),
]
