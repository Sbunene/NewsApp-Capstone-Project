from .settings import *
import os

# Use SQLite for Docker simplicity - use absolute path that works everywhere
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Disable some security features for demo
DEBUG = True
ALLOWED_HOSTS = ['*']