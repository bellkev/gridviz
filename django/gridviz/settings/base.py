# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

# Build paths inside the project like this: join(BASE_DIR, ...)
from os.path import dirname, join

# The python module named 'gridviz'
MODULE_ROOT = dirname(dirname(__file__))

# The root of the django project, where manage.py lives
PROJECT_ROOT = dirname(MODULE_ROOT)

# All of gridviz, where README is
SYSTEM_ROOT = dirname(PROJECT_ROOT)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')9d0jv%kf48f28sbuo03uzpheaf_&jc-o8$wx@x(8&0&=^iyxy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ws4redis',
    'bootstrapform',
    'gridviz',
    'registration',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'gridviz.urls'

WSGI_APPLICATION = 'ws4redis.django_runserver.application'

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    join(SYSTEM_ROOT, 'static'),
    join(SYSTEM_ROOT, 'bower_components'),
    join(SYSTEM_ROOT, 'angular'),
)

STATIC_ROOT = join(SYSTEM_ROOT, 'collected_static')

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
    'ws4redis.context_processors.default',
)

TEMPLATE_DIRS = (
    join(PROJECT_ROOT, 'templates'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

# Websockets

WS4REDIS_SUBSCRIBER = 'gridviz.subscriber.DatabaseSubscriber'

WS4REDIS_EXPIRE = 0

WEBSOCKET_URL = '/ws/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default'
    }
}

# SVG Store

SVG_STORE = 'gridviz'

# Email confirmations

EMAIL_BACKEND = 'django_ses.SESBackend'

ACCOUNT_ACTIVATION_DAYS = 1

AWS_SES_REGION_NAME = 'us-west-2'

AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

DEFAULT_FROM_EMAIL = 'kevin.a.bell@gmail.com'

LOGIN_REDIRECT_URL = '/drawings/'