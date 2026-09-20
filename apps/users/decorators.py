"""
Role-based access control decorator.
Used to restrict views to specific user roles (student, coordinator, teacher).
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Decorator that restricts access to users with specific roles.
    Usage: @role_required('student') or @role_required('coordinator', 'teacher')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('users:login')
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('users:redirect_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
