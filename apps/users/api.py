"""JSON endpoints shared by the React application."""

from functools import wraps

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie


def api_role_required(*roles):
    """Require a signed-in user and, optionally, one of the supplied roles."""
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required.'}, status=401)
            if roles and request.user.role not in roles:
                return JsonResponse({'error': 'You do not have permission to perform this action.'}, status=403)
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


@ensure_csrf_cookie
@api_role_required()
def session(request):
    """Return the signed-in user's profile and a CSRF token for mutations."""
    user = request.user
    return JsonResponse({
        'user': {
            'id': user.pk,
            'role': user.role,
            'role_label': user.get_role_display(),
            'full_name': user.get_full_name() or user.username,
            'username': user.username,
            'email': user.email,
            'department': user.department,
            'division': user.get_division_display() if user.division else '',
            'grade': user.get_grade_display() if user.grade else '',
            'student_id': user.student_id,
        },
        'csrf_token': get_token(request),
    })
