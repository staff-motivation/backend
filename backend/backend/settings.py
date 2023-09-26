import os
from pathlib import Path

from django.conf import settings
from django.conf.locale.ru import formats as ru_formats
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', default='yours-secret-key')

DEBUG = os.getenv('DEBUG', default=True)

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
    'corsheaders',
    'django_filters',
    'djoser',
    'drf_spectacular',
    'import_export',
    'scheduler',
    'api.apps.ApiConfig',
    'users.apps.UsersConfig',
    'news.apps.NewsConfig',
    'tasks.apps.TasksConfig',
    'notifications.apps.NotificationsConfig',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

PROD_DB = os.getenv('PROD_DB', default='True')
if os.getenv('PROD_DB', default=True) is True:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv(
                'DB_ENGINE', default='django.db.backends.postgresql'
            ),
            'NAME': os.getenv('DB_NAME', default='postgres'),
            'USER': os.getenv('POSTGRES_USER', default='postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
            'HOST': os.getenv('DB_HOST', default='db'),
            'PORT': os.getenv('DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': f'{BASE_DIR}/db.sqlite3',
        }
    }

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

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
DEFAULT_FROM_EMAIL = 'motivation-system@yandex.ru'


DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SERIALIZERS': {
        'user_create': 'api.serializers.CustomUserCreateSerializer',
        'user': 'api.serializers.CustomUserRetrieveSerializer',
        'current_user': 'api.serializers.CustomUserRetrieveSerializer',
        'profile_info': 'api.serializers.UserPublicSerializer',
        'upload_avatar': 'api.serializers.UserImageSerializer',
    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.IsAuthenticated'],
        'user': ['api.permissions.CanEditUserFields'],
        'user_delete': ['rest_framework.permissions.IsAdminUser'],
        'profile_info': ['rest_framework.permissions.IsAuthenticated'],
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'My API Documentation',
    'DESCRIPTION': 'Documentation for Staff-motivation API built with DRF',
    'VERSION': '1.0.0',
}

if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'skvmrelay.netangels.ru'
    EMAIL_PORT = 25


CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
