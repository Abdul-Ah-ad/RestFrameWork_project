"""
Sample local.py for development overrides.
Rename to local.py and update as needed.
"""

from .base import *

DEBUG = True

SECRET_KEY = 'django-insecure-zpge6kx-4@_5bx(+%n9e78y@qy^mdj(kw3ima18wy%!pn919fp'

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cric_stats_db',
        'USER': 'cric_ahad',
        'PASSWORD': 'cric_ahad',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}



EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Optional for API testing
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']
