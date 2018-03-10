# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.core.exceptions import ImproperlyConfigured
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', False)=='True')
#DEBUG = True

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST', '127.0.0.1'), 'localhost']


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shrinkmeister',
    'corsheaders',
    'sorl.thumbnail'
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'shrink_server.urls'

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

WSGI_APPLICATION = 'shrink_server.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATABASES = {}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# SHRINKMEISTER SERVER SETTINGS

SHRINKMEISTER_SERVER_NODE = True

THUMBNAIL_SECRET_KEY = os.environ.get('THUMBNAIL_SECRET_KEY', '')
THUMBNAIL_SERVER_URL = os.environ.get('THUMBNAIL_SERVER_URL', '')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET', '')
THUMBNAIL_TTL = os.environ.get('THUMBNAIL_TTL', 60 * 60 * 24 * 7)  # 7 days
THUMBNAIL_CACHE_NAME = os.environ.get('THUMBNAIL_CACHE_NAME', 'shrinkmeister')
THUMBNAIL_CACHE_BACKEND = os.environ.get('THUMBNIAL_CACHE_BACKEND', 'django_redis.cache.RedisCache')
THUMBNAIL_CACHE_LOCATION = os.environ.get('THUMBNAIL_CACHE_LOCATION', 'redis://127.0.0.1')
THUMBNAIL_CACHE_KEY_PREFIX = os.environ.get('THUMBNAIL_CACHE_KEY_PREFIX', 'shrinkmeister')
THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [2]

THUMBNAIL_BACKEND = 'shrinkmeister.sorl.backend.ShrinkmeisterThumbnailBackend'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_HOST = os.environ.get('AWS_S3_HOST', None)
AWS_STORAGE_BUCKET_NAME = 'SHRINKMEISTER_STORAGE'
AWS_AUTO_CREATE_BUCKET = True


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = THUMBNAIL_SECRET_KEY

# Cache (Used to store thumbnails information):
CACHES = {
    'default': {
        'BACKEND': THUMBNAIL_CACHE_BACKEND,
        'LOCATION': os.environ.get('CACHE_LOCATION', THUMBNAIL_CACHE_LOCATION),
        'KEY_PREFIX': os.environ.get('CACHE_KEY_PREFIX', 'shrinkmeister-default'),
    },
    THUMBNAIL_CACHE_NAME: {
        'BACKEND': THUMBNAIL_CACHE_BACKEND,
        'LOCATION': THUMBNAIL_CACHE_LOCATION,
        'TIMEOUT': THUMBNAIL_TTL,
        'KEY_PREFIX': THUMBNAIL_CACHE_KEY_PREFIX,
    }
}

# CORS Headers
CORS_ORIGIN_ALLOW_ALL = True

try:
    from settings_local import *
except:
    pass

if not THUMBNAIL_SECRET_KEY:
    raise ImproperlyConfigured('THUMBNAIL_SECRET_KEY is empty!')

if not THUMBNAIL_SERVER_URL:
    raise ImproperlyConfigured('THUMBNAIL_SERVER_URL is empty!')

if not THUMBNAIL_BUCKET:
    raise ImproperlyConfigured('THUMBNAIL_BUCKET is empty!')

