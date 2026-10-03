"""
Authentication views: login, logout, register, dashboard redirect.

Registration creates the user in both Supabase Auth and Django's CustomUser.
Login authenticates via the Supabase backend (see backends.py).
Logout clears both Django session and Supabase session.
"""

import logging
import hashlib
import json
from pathlib import Path
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ALLOWED_EMAIL_DOMAIN, CustomUserCreationForm, CustomLoginForm
from .backends import get_supabase_client
from .models import CustomUser

logger = logging.getLogger(__name__)


class FirebaseConfigurationError(Exception):
    pass


def _build_auth_context(login_form, register_form, mode):
    """Helper to build template context with both forms."""
    return {
        'login_form': login_form,
        'register_form': register_form,
        'mode': mode,
        'firebase_web_config': settings.FIREBASE_WEB_CONFIG,
    }


def _firebase_admin_app():
    """Initialize Firebase Admin once using a local service account or ADC."""
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError as exc:
        raise FirebaseConfigurationError('firebase-admin is not installed.') from exc

    app_name = 'attendease'
    try:
        return firebase_admin.get_app(app_name)
    except ValueError:
        if not settings.FIREBASE_PROJECT_ID:
            raise FirebaseConfigurationError('FIREBASE_PROJECT_ID is not configured.')

        try:
            credential_path = settings.FIREBASE_ADMIN_CREDENTIALS
            credential = (
                credentials.Certificate(Path(credential_path))
                if credential_path
                else credentials.ApplicationDefault()
            )
            return firebase_admin.initialize_app(
                credential,
                {'projectId': settings.FIREBASE_PROJECT_ID},
                name=app_name,
            )
        except Exception as exc:
            raise FirebaseConfigurationError('Firebase Admin credentials are invalid or unavailable.') from exc


@require_POST
def firebase_login_view(request):
    """Verify a Firebase ID token, then sign in or provision the matching Django user."""
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid sign-in request.'}, status=400)

    id_token = payload.get('idToken') if isinstance(payload, dict) else None
    if not isinstance(id_token, str) or not id_token:
        return JsonResponse({'error': 'Google sign-in token is missing.'}, status=400)

    try:
        from firebase_admin import auth
        admin_app = _firebase_admin_app()
    except FirebaseConfigurationError:
        logger.exception('Firebase Admin is not configured.')
        return JsonResponse({'error': 'Google sign-in is not configured on this server.'}, status=503)

    try:
        claims = auth.verify_id_token(id_token, app=admin_app, check_revoked=True)
    except Exception:
        logger.warning('Firebase ID token verification failed.')
        return JsonResponse({'error': 'Google sign-in token is invalid or expired.'}, status=401)

    email = (claims.get('email') or '').strip().lower()
    if not claims.get('email_verified') or not email:
        return JsonResponse({'error': 'Use a verified Google account to sign in.'}, status=403)
    if email.rsplit('@', 1)[-1] != ALLOWED_EMAIL_DOMAIN:
        return JsonResponse(
            {'error': f'Use your @{ALLOWED_EMAIL_DOMAIN} Google account.'},
            status=403,
        )

    display_name = (claims.get('name') or '').strip().split(maxsplit=1)
    first_name = display_name[0] if display_name else ''
    last_name = display_name[1] if len(display_name) > 1 else ''
    username = f"firebase_{hashlib.sha256(claims['uid'].encode()).hexdigest()[:20]}"

    with transaction.atomic():
        user = CustomUser.objects.filter(email__iexact=email).first()
        if user is None:
            user = CustomUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=CustomUser.Role.STUDENT,
            )
            user.set_unusable_password()
            user.save()
        elif not user.is_active:
            return JsonResponse({'error': 'This account is disabled. Contact an administrator.'}, status=403)
        else:
            changed_fields = []
            if not user.first_name and first_name:
                user.first_name = first_name
                changed_fields.append('first_name')
            if not user.last_name and last_name:
                user.last_name = last_name
                changed_fields.append('last_name')
            if changed_fields:
                user.save(update_fields=changed_fields)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'redirect_url': reverse(settings.LOGIN_REDIRECT_URL)})


def register_view(request):
    """
    Handle user registration.
    1. Validate the Django form.
    2. Create the user in Supabase Auth (email + password).
    3. Save the Django CustomUser with role, division, etc.
    4. Log the user in.
    """
    if request.user.is_authenticated:
        return redirect('users:redirect_dashboard')

    login_form = CustomLoginForm()

    if request.method == 'POST':
        register_form = CustomUserCreationForm(request.POST)
        if register_form.is_valid():
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password1']

            # Step 1: Create user in Supabase Auth
            supabase_user_created = False
            supabase = get_supabase_client()

            if supabase:
                try:
                    supabase_response = supabase.auth.sign_up({
                        'email': email,
                        'password': password,
                    })
                    if supabase_response and supabase_response.user:
                        supabase_user_created = True
                        logger.info(f'Supabase user created for {email}')
                except Exception as e:
                    logger.error(f'Supabase sign_up failed for {email}: {e}')
                    messages.warning(
                        request,
                        'Account created locally. Supabase sync will retry on next login.'
                    )
            else:
                logger.warning('Supabase not configured. Creating local-only user.')

            # Step 2: Create Django user regardless of Supabase result
            user = register_form.save()

            # Step 3: Log the user in via Django
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(
                request,
                f'Welcome to AttendEase, {user.first_name or user.username}!'
            )
            return redirect('users:redirect_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        register_form = CustomUserCreationForm()

    ctx = _build_auth_context(login_form, register_form, mode='register')
    return render(request, 'users/auth.html', ctx)


def login_view(request):
    """
    Handle user login.
    Tries Supabase auth backend first, falls back to Django ModelBackend.
    """
    if request.user.is_authenticated:
        return redirect('users:redirect_dashboard')

    register_form = CustomUserCreationForm()

    if request.method == 'POST':
        login_form = CustomLoginForm(request, data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('users:redirect_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        login_form = CustomLoginForm()

    ctx = _build_auth_context(login_form, register_form, mode='login')
    return render(request, 'users/auth.html', ctx)


def logout_view(request):
    """
    Log out the user from both Django and Supabase.
    """
    # Sign out from Supabase (best-effort)
    supabase = get_supabase_client()
    if supabase:
        try:
            supabase.auth.sign_out()
        except Exception as e:
            logger.debug(f'Supabase sign_out failed (non-critical): {e}')

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
