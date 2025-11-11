from .settings import *

# Use SQLite for Docker simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/app/db.sqlite3',
    }
}

# Disable some security features for demo
DEBUG = True
ALLOWED_HOSTS = ['*']
