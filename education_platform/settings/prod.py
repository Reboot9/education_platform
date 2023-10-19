import os
from .base import *


DEBUG = False

ADMINS = [
    ('Admin', 'admin@example.com'),
]

ALLOWED_HOSTS = ['*', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST':  os.environ.get('POSTGRES_HOST'),  # This is container name
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

STATIC_ROOT = BASE_DIR / 'static'

REDIS_URL = 'redis://cache:6379'
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]
