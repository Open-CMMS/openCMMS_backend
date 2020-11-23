"""
Django base settings for openCMMS project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from datetime import timedelta

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k&-js5nc7p%#$pk_bj+3fqd0($w5!6^#dy+a+b&p6($3r$a-%k'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1'
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)

BASE_URL = 'http://127.0.0.1:8000/'


INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles', 'rest_framework', 'rest_framework_swagger', 'drf_yasg',
    'usersmanagement.apps.UsersmanagementConfig', 'maintenancemanagement.apps.MaintenancemanagementConfig',
    'utils.apps.UtilsConfig', 'django_inlinecss'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'openCMMS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'utils/templates/')],
        'APP_DIRS': True,
        'OPTIONS':
            {
                'context_processors':
                    [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
            },
    },
]

WSGI_APPLICATION = 'openCMMS.wsgi.application'

AUTH_USER_MODEL = 'usersmanagement.UserProfile'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'django',
            'USER': 'django',
            'PASSWORD': 'django',
            'HOST': 'localhost',
            'PORT': '',
        }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS':
        'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES':
        (
            'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
            'rest_framework.authentication.SessionAuthentication'
        ),
}

SWAGGER_SETTINGS = {'LOGIN_URL': "/api/admin/login"}

################################################################
############################ STATIC ############################
################################################################

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "utils/templates/"),
)

STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles')

################################################################
############################## JWT #############################
################################################################

JWT_AUTH = {
    'JWT_ENCODE_HANDLER': 'rest_framework_jwt.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER': 'rest_framework_jwt.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USER_ID_HANDLER': 'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_response_payload_handler',
    'JWT_SECRET_KEY': 'SECRET_KEY',
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': timedelta(days=1),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=15),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUTH_COOKIE': None,
}

################################################################
############################# MEDIA ############################
################################################################

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


################################################################
############################# EMAIL ############################
################################################################

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'

################################################################
############################ LOGGING ###########################
################################################################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':
        {
            'verbose_http':
                {
                    'format':
                        '{levelname} {asctime} {process:d} {thread:d} "{request.user} did {request.method} on {request.path} with {request.POST} and got {status_code}"',
                    'style':
                        '{',
                },
            'verbose_sql':
                {
                    'format': '{levelname} {asctime} {process:d} {thread:d} {message} {sql} {params}',
                    'style': '{',
                },
            'verbose_base':
                {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
    'handlers':
        {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple'
            },
            'file_http':
                {
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(BASE_DIR, 'log/', 'requests.log'),
                    'level': 'DEBUG',
                    'formatter': 'verbose_http'
                },
            'file_sql':
                {
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(BASE_DIR, 'log/', 'sql.log'),
                    'level': 'INFO',
                    'formatter': 'verbose_sql'
                },
            'file_utils':
                {
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(BASE_DIR, 'utils/log/', 'infos.log'),
                    'level': 'INFO',
                    'formatter': 'verbose_base'
                },
            'file_users':
                {
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(BASE_DIR, 'usersmanagement/log/', 'infos.log'),
                    'level': 'INFO',
                    'formatter': 'verbose_base'
                },
            'file_maintenance':
                {
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(BASE_DIR, 'maintenancemanagement/log/', 'infos.log'),
                    'level': 'INFO',
                    'formatter': 'verbose_base'
                },
            'mail_error': {
                'class': 'django.utils.log.AdminEmailHandler',
                'level': 'ERROR',
            }
        },
    'loggers':
        {
            'django.request': {
                'handlers': ['file_http'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django.db.backends': {
                'handlers': ['file_sql'],
                'level': 'INFO',
                'propagate': False,
            },
            'utils': {
                'handlers': ['file_utils', 'console', 'mail_error'],
                'level': 'INFO',
            },
            'usersmanagement': {
                'handlers': ['file_users', 'console', 'mail_error'],
                'level': 'INFO'
            },
            'maintenancemanagement': {
                'handlers': ['file_maintenance', 'console', 'mail_error'],
                'level': 'INFO'
            }
        }
}
