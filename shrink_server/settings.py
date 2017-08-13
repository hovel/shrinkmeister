# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

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
    'corsheaders'
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

# SHRINKMEISTER SETTINGS
THUMBNAIL_SECRET_KEY = os.environ['THUMBNAIL_SECRET_KEY']
THUMBNAIL_SERVER_URL = os.environ['THUMBNAIL_SERVER_URL']
THUMBNAIL_BUCKET = os.environ['THUMBNAIL_BUCKET']
THUMBNAIL_TTL = os.environ.get('THUMBNAIL_TTL', 60 * 60 * 24 * 7)  # 7 days
THUMBNAIL_CACHE_NAME = os.environ.get('THUMBNAIL_CACHE_NAME', 'shrinkmeister')
THUMBNIAL_CACHE_BACKEND = os.environ.get('THUMBNIAL_CACHE_BACKEND', 'django.core.cache.backends.memcached.MemcachedCache')
THUMBNAIL_CACHE_LOCATION = os.environ.get('THUMBNAIL_CACHE_LOCATION', '127.0.0.1:11211')
THUMBNAIL_CACHE_KEY_PREFIX = os.environ.get('THUMBNAIL_CACHE_KEY_PREFIX', 'shrinkmeister')
<<<<<<< HEAD
THUMBNAIL_CACHE_BACKEND = os.environ.get('THUMBNAIL_CACHE_BACKEND', 'django.core.cache.backends.memcached.MemcachedCache')
=======
>>>>>>> e16c2d7457aec71af44cac4553960d2e635bab8a

AWS_S3_HOST = os.environ.get('AWS_S3_HOST', None)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = THUMBNAIL_SECRET_KEY

# Cache (Used to store thumbnails information):
CACHES = {
    'default': {
<<<<<<< HEAD
        'BACKEND': THUMBNAIL_CACHE_BACKEND,
=======
        'BACKEND': os.environ.get('CACHE_BACKEND', THUMBNIAL_CACHE_BACKEND),
>>>>>>> e16c2d7457aec71af44cac4553960d2e635bab8a
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
