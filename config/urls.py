"""AttendEase project-level URL configuration."""

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import include, path
from django.views.decorators.csrf import ensure_csrf_cookie

from attendance import api as attendance_api
from config.views import about, react_app
from events import api as events_api
from users import api as users_api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', login_required(ensure_csrf_cookie(react_app)), name='react_app'),
    path('api/session/', users_api.session, name='api_session'),
    path('api/events/', events_api.events, name='api_events'),
    path('api/dashboard/', attendance_api.dashboard, name='api_dashboard'),
    path('api/requests/', attendance_api.create_request, name='api_create_request'),
    path('api/requests/<int:pk>/review/', attendance_api.review_request, name='api_review_request'),
    path('api/requests/<int:pk>/attendance/', attendance_api.mark_attendance, name='api_mark_attendance'),
    path('', lambda request: (
        redirect('users:redirect_dashboard')
        if request.user.is_authenticated
        else redirect('users:login')
    )),
    path('about/', about, name='about'),
    path('auth/', include('users.urls')),
    path('events/', include('events.urls')),
    path('attendance/', include('attendance.urls')),
]
