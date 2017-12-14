# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'shrinkmeister',
    'sorl.thumbnail',
    'tests.imagestorage',
)

MIDDLEWARE_CLASSES = ()

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

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

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'DEBUG'
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = True

# SHRINKMEISTER SETTINGS
THUMBNAIL_SECRET_KEY = os.environ['THUMBNAIL_SECRET_KEY']
THUMBNAIL_SERVER_URL = os.environ.get('THUMBNAIL_SERVER_URL', 'http://localhost:8001/')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET', 'DEBUG')
THUMBNAIL_TTL = os.environ.get('THUMBNAIL_TTL', 60 * 60 * 24 * 7)  # 7 days



THUMBNAIL_CACHE_NAME = os.environ.get('THUMBNAIL_CACHE_NAME', 'shrinkmeister')
THUMBNAIL_CACHE_BACKEND = os.environ.get('THUMBNIAL_CACHE_BACKEND', 'django_redis.cache.RedisCache')
THUMBNAIL_CACHE_LOCATION = os.environ.get('THUMBNAIL_CACHE_LOCATION', 'redis://127.0.0.1')
THUMBNAIL_CACHE_KEY_PREFIX = os.environ.get('THUMBNAIL_CACHE_KEY_PREFIX', 'shrinkmeister')
THUMBNAIL_ALTERNATIVE_RESOLUTIONS = [2]

THUMBNAIL_BACKEND = 'shrinkmeister.sorl.backend.ShrinkmeisterThumbnailBackend'
THUMBNAIL_ENGINE = 'shrinkmeister.sorl.engine.DummyEngine'

AWS_S3_HOST = os.environ.get('AWS_S3_HOST', None)

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdatabase.sqlite',
    }
}

