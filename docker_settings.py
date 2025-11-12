from .settings import *
import os

# Use SQLite for Docker simplicity - compute BASE_DIR and store DB inside project
BASE_DIR = Path(__file__).resolve().parent
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'db.sqlite3'),
    }
}

# Disable some security features for demo
DEBUG = True
ALLOWED_HOSTS = ['*']
