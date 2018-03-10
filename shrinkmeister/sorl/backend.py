import logging
from copy import copy

from django.utils.six import string_types
from django.core.cache import caches

from sorl.thumbnail.base import ThumbnailBackend
from sorl.thumbnail.conf import settings, defaults as default_settings
from sorl.thumbnail.helpers import tokey, serialize
from sorl.thumbnail.images import BaseImageFile, DummyImageFile, ImageFile as IFile
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry
from storages.backends.s3boto3 import S3Boto3Storage
from shrinkmeister.utils import generate_cache_key, generate_lazy_thumbnail_url
from django.conf import settings as django_settings


shrinkmeister_cache = caches['shrinkmeister']

THUMBNAIL_BUCKET = settings.THUMBNAIL_BUCKET
THUMBNAIL_TTL = settings.THUMBNAIL_TTL
SHRINKMEISTER_SIGNED_URLS = getattr(settings, 'SHRINKMEISTER_SIGNED_URLS', False)

logger = logging.getLogger(__name__)

class ImageFile(IFile):
    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['storage']
        state['storage_bucket'] = self.storage.bucket_name
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.storage = S3Boto3Storage(bucket=state['storage_bucket'])

    @property
    def url(self):
        if SHRINKMEISTER_SIGNED_URLS:
            return self.storage.url(self.name)
        else:
            return 'https://s3.amazonaws.com/{}/{}'.format(self.storage.bucket_name, self.name)

class ImageLikeObject(BaseImageFile):
    def __init__(self, geometry_string, ratio, name, url):
        '''
        Pass ImageFile as source
        '''
        self.name = name
        self._url = url
        self.size = parse_geometry(geometry_string, ratio)

    @property
    def url(self):
        return self._url
    
    def exists(self):
        return True

    


class ShrinkmeisterThumbnailBackend(ThumbnailBackend):
    def get_thumbnail(self, file_, geometry_string, **options):
        """
        Returns thumbnail as an ImageFile instance for file with geometry and
        options given. First it will try to get it from the key value store,
        secondly it will create it.
        """
        logger.debug('Getting thumbnail for file [%s] at [%s]', file_, geometry_string)

        name = None
        if 'cache_key' in options:
            name = options['cache_key']
            options.pop('cache_key')

        options_orig = copy(options)

        if file_:
            source = ImageFile(file_)
        else:
            if settings.THUMBNAIL_DUMMY:
                return DummyImageFile(geometry_string)
            else:
                logger.error('missing file_ argument in get_thumbnail()')
                return

        # preserve image filetype
        if settings.THUMBNAIL_PRESERVE_FORMAT:
            options.setdefault('format', self._get_format(source))

        for key, value in self.default_options.items():
            options.setdefault(key, value)

        # For the future I think it is better to add options only if they
        # differ from the default settings as below. This will ensure the same
        # filenames being generated for new options at default.
        for key, attr in self.extra_options:
            value = getattr(settings, attr)
            if value != getattr(default_settings, attr):
                options.setdefault(key, value)

        if not name:
            name = generate_cache_key('', source.storage.bucket, source.name,
                    geometry_string, **options)
        cached = shrinkmeister_cache.get(name, None)
        if cached:
            return cached

        if getattr(django_settings, 'SHRINKMEISTER_SERVER_NODE', False):
            thumbnail = ImageFile(name, default.storage)
            source_image = default.engine.get_image(source)
            self._create_thumbnail(source_image, geometry_string, options,
                                    thumbnail)
            self._create_alternative_resolutions(source_image, geometry_string,
                                                    options, thumbnail.name)
            cached = shrinkmeister_cache.set(name, thumbnail, THUMBNAIL_TTL)
            return thumbnail
        data = {}
        data['bucket'] = source.storage.bucket_name
        data['key'] = source.name
        data['geometry_string'] = geometry_string
        data['cache_key'] = name
        # Send only specified options without defaults for url shorten
        # Should be configurable in future
        data['options'] = options_orig
        ratio = None
        url = generate_lazy_thumbnail_url(data)
        return ImageLikeObject(geometry_string, ratio, name, url)