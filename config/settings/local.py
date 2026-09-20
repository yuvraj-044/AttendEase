"""
Local development settings for AttendEase.
Inherits from base.py and adds development-specific overrides.
"""

from .base import *  # noqa: F401,F403

# Override base settings for local development
DEBUG = True
ALLOWED_HOSTS = ['*']

# Optional: Add django-debug-toolbar or other local apps here
# INSTALLED_APPS += ['debug_toolbar']
