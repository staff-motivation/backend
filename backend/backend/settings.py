from pathlib import Path
import os

from django.conf import settings
from django.conf.locale.ru import formats as ru_formats

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-m18q#kk2ku()fjg*kc5rp9%6h=ynfc4x2b4cqj1&@i2*xqy*k='

DEBUG = True

ALLOWED_HOSTS = ['185.41.163.109', '127.0.0.1', 'localhost', 'web']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework.documentation',
    # 'django_filters',
    'djoser',
    'drf_yasg',
    'import_export',
    'api.apps.ApiConfig',
    'users.apps.UsersConfig',
    'news.apps.NewsConfig',
    'tasks.apps.TasksConfig',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DJOSER = {
    'HIDE_USERS': False,
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'api.serializers.CustomUserCreateSerializer',
        'user': 'api.serializers.CustomUserRetrieveSerializer',
        'current_user': 'api.serializers.CustomUserRetrieveSerializer',
        'profile_info': 'api.serializers.UserPublicSerializer',

    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.IsAuthenticated'],
        'user': ['api.permissions.CanEditUserFields'],
        'user_delete': ['rest_framework.permissions.IsAdminUser'],
        'profile_info': ['rest_framework.permissions.IsAuthenticated'],
    },
    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
    'EMAIL_FILE_PATH': os.path.join(BASE_DIR, 'mails')
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE'),
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('POSTGRES_USER'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT')
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE'),
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('POSTGRES_USER'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT')
#     }
# }

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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MAX_LENGTH_USERNAME = 255
MAX_LENGTH_EMAIL = 255

AUTH_USER_MODEL = 'users.User'

settings.DATE_FORMAT = 'd.m.Y'
ru_formats.DATE_FORMAT = 'd.m.Y'

# Вариант рассылки для отладки кода
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'sys.motivation@gmail.com'
EMAIL_HOST_PASSWORD = 'Motivate!123'
EMAIL_USE_TLS = False

# Продуктовый вариант - требует указать почту яндекса
# и приложить к ней пароль приложения.

# EMAIL_HOST = 'smtp.yandex.ru'
# EMAIL_PORT = 465
# EMAIL_USE_SSL = True
# DEFAULT_FROM_EMAIL = 'exmple@yandex.ru'
# # емейл, который будет указан в поле "От кого".
# EMAIL_HOST_USER = 'exmple@yandex.ru'
# # ваш емейл на Яндексе. Как правило, идентичен предыдущему пункту
# EMAIL_HOST_PASSWORD = 'тут-долже-быть-пароль-приложения'
# # пароль ПРИЛОЖЕНИЯ, который нужно создать в настройках Яндекса заранее.
# #  Это не пароль от вашего емейла!
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
