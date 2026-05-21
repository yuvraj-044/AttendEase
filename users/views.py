"""
Authentication views: login, logout, register, dashboard redirect.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm


def register_view(request):
    """Handle user registration with role selection."""
    if request.user.is_authenticated:
        return redirect('users:redirect_dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to AttendEase, {user.first_name or user.username}!')
            return redirect('users:redirect_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Handle user login and redirect to role-specific dashboard."""
    if request.user.is_authenticated:
        return redirect('users:redirect_dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('users:redirect_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Log out the user and redirect to login page."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('users:login')


@login_required
def redirect_dashboard(request):
    """
    Redirect users to their role-specific dashboard.
    This is the central routing point after login.
    """
    user = request.user
    if user.is_student:
        return redirect('attendance:student_dashboard')
    elif user.is_coordinator:
        return redirect('attendance:coordinator_dashboard')
    elif user.is_teacher:
        return redirect('attendance:teacher_dashboard')
    else:
        # Fallback for superusers or unknown roles
        return redirect('attendance:student_dashboard')
