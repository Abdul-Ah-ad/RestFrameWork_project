"""
Sample local.py for development overrides.
Rename to local.py and update as needed.
"""

from .base import *

DEBUG = True

SECRET_KEY = 'your secret key'

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_name',
        'USER': 'db_user',
        'PASSWORD': 'user_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}



EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Optional for API testing
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']
