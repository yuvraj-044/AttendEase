"""
Production settings for AttendEase.
Inherits from base.py and applies production hardening.
"""

import os
from .base import *  # noqa: F401,F403

# Override base settings for production
DEBUG = False

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# HTTPS / Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files — configure for your CDN or storage
# STATIC_ROOT = BASE_DIR / 'staticfiles'
