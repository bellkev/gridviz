# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(PROJECT_ROOT, 'db.sqlite3'),
    }
}

SECRET_KEY = ')9d0jv%kf48f28sbuo03uzpheaf_&jc-o8$wx@x(8&0&=^iyxy'

DEBUG = True

TEMPLATE_DEBUG = True