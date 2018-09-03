"""
Django settings for ta_platform project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import sys
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .secrets import (
    SECRET_KEY,
    RABBITMQ_VHOST_PASSWD,
    POSTGRES_PASSWD,
    EMAIL_HOST_PASSWORD,
)

DEFAULT_BRAND_DICT = {
    'COMPANY_NAME': 'JED Talent Acquisition',
    'DEFAULT_FROM_EMAIL': 'no-reply@jedtac.com',
    'HEADER_LOGO': 'img/LinekodelogoW.png',
    'FAVICON': 'img/LinekodeIconB2.png',
    'DEFAULT_AVATAR_MALE': '<i class="fas fa-chess-king"></i>',
    'DEFAULT_AVATAR_FEMALE': '<i class="fas fa-chess-queen"></i>',
    'DEFAULT_STYLESHEET': 'css/default-styles.css',
}


BRANDING = False
BRAND_DICT = DEFAULT_BRAND_DICT


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '+%g=v(%s4v6!%k5swwrox2cdo4kd=k4^crjia6j&l$b%)o^g2!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'guardian',
    'channels',
    'simple_history',
    'crispy_forms',
    # 'issue_tracker',
    'debug_toolbar',
    'admin_console',
    'accounts',
    'applications',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# GUARDIAN_GET_INIT_ANONYMOUS_USER = 'accounts.models.get_anonymous_user_instance'
ANONYMOUS_USER_NAME = None

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'ta_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'common', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.get_brand_dict',
                'common.context_processors.get_brand_bool',
            ],
        },
    },
]
WSGI_APPLICATION = 'ta_platform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'TEST': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'testdb.sqlite3'),
        }
    }
}
if 'test' in sys.argv and '--keepdb' in sys.argv:
    DATABASES['default']['TEST']['NAME'] = '/dev/shm/ta_platform.test.db.sqlite3'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.USER'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'denis.angulo'
# EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = DEFAULT_BRAND_DICT['DEFAULT_FROM_EMAIL']


LOGIN_REDIRECT_URL = reverse_lazy('home')

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/


LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    # os.path.join(BASE_DIR, 'default_branding'), # off in the meantime
    os.path.join(BASE_DIR, 'assets'),
)
INTERNAL_IPS = ['127.0.0.1']

# Application settings
ENFORCE_MIN_AGE = True
MINIMUM_AGE_ALLOWED = 18 # ignored if ENFORCE_MIN_AGE is False


CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# Django-channels settings

ASGI_APPLICATION = 'ta_platform.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)]
        }
    }
}

# crispy-forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap4'
# CRISPY_CLASS_CONVERTERS = {
#     'textinput': 'form-control',

# }

if BRANDING:
    DEFAULT_FROM_EMAIL = BRAND_DICT['DEFAULT_FROM_EMAIL']
