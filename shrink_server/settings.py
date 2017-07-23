# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['THUMBNAIL_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', False)=='True')
#DEBUG = True

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST', '127.0.0.1')]


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shrinkmeister',
)

MIDDLEWARE_CLASSES = (
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# SHRINKMEISTER SETTINGS
THUMBNAIL_SECRET_KEY = SECRET_KEY
THUMBNAIL_SERVER_URL = os.environ['THUMBNAIL_SERVER_URL']
THUMBNAIL_BUCKET = os.environ['THUMBNAIL_BUCKET']
THUMBNAIL_TTL = os.environ.get('THUMBNAIL_TTL', 60 * 60 * 24 * 7)  # 7 days
S3_ENDPOINT = os.environ.get('S3_ENDPOINT', None)

# Cache (Used to store thumbnails information):
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': os.environ.get('CACHE_LOCATION', '127.0.0.1:11211'),
        'TIMEOUT': THUMBNAIL_TTL,
        'KEY_PREFIX': os.environ.get('CACHE_KEY_PREFIX', 'shrinkmeister'),
        # 'OPTIONS': {
        #     'MAX_ENTRIES': os.environ.get('CACHE_MAX_ENTRIES', 30000)
        # },
    }
}
