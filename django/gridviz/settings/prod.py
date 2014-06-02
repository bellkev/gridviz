# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from os import environ

from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gridviz',
        'USER': environ['DB_USER'],
        'PASSWORD': environ['DB_PASS'],
        'HOST': environ['DB_HOST']
    }
}

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    join(SYSTEM_ROOT, 'angular'),
    join(SYSTEM_ROOT, 'compiled_static_dev'),
    join(SYSTEM_ROOT, 'bower_components'),
)

SECRET_KEY = environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = [host.strip() for host in environ['ALLOWED_HOSTS'].split(',')]
