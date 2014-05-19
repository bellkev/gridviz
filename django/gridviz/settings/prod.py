# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from os import environ

from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gridviz',
        'USER': environ['DB_USER'],
        'PASSWORD': environ['DB_PASS']
    }
}

STATIC_URL = '/static/'

SECRET_KEY = environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = [environ['GRIDVIZ_HOSTNAME']]
