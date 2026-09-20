"""
Supabase Authentication Backend for Django.

Authenticates users against Supabase Auth, then maps them to Django's
CustomUser model so the role-based permission system continues to work.

Flow:
  1. User submits email + password via Django login form.
  2. This backend calls Supabase Auth (sign_in_with_password).
  3. If Supabase succeeds → look up the matching Django CustomUser by email.
  4. Return the Django user object so Django's session system takes over.

The Django ModelBackend is kept as a fallback so superusers created via
`createsuperuser` (who don't exist in Supabase) can still log in.
"""

import logging
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def get_supabase_client():
    """
    Create and return a Supabase client instance.
    Returns None if Supabase is not configured.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        logger.warning('Supabase URL or Anon Key not configured. Skipping Supabase auth.')
        return None

    try:
        from supabase import create_client
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    except Exception as e:
        logger.error(f'Failed to create Supabase client: {e}')
        return None


class SupabaseAuthBackend:
    """
    Custom Django authentication backend that delegates password
    verification to Supabase Auth.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user via Supabase.

        Args:
            username: Can be a username or email address.
            password: The user's password.

        Returns:
            CustomUser instance on success, None on failure.
        """
        if not username or not password:
            return None

        # Resolve username to email if needed
        email = self._resolve_email(username)
        if not email:
            return None

        # Attempt Supabase authentication
        supabase = get_supabase_client()
        if supabase is None:
            return None

        try:
            response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password,
            })

            if response and response.user:
                # Supabase auth succeeded — find the matching Django user
                try:
                    user = User.objects.get(email__iexact=email)
                    return user
                except User.DoesNotExist:
                    logger.warning(
                        f'Supabase auth succeeded for {email} but no '
                        f'matching Django user found.'
                    )
                    return None

        except Exception as e:
            # Supabase auth failed (wrong password, user not found, etc.)
            logger.debug(f'Supabase auth failed for {email}: {e}')
            return None

        return None

    def get_user(self, user_id):
        """Retrieve user by primary key (required by Django auth framework)."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _resolve_email(self, username):
        """
        If the username looks like an email, return it directly.
        Otherwise, look up the user's email from the database.
        """
        if '@' in username:
            return username.lower().strip()

        try:
            user = User.objects.get(username=username)
            return user.email
        except User.DoesNotExist:
            return None
