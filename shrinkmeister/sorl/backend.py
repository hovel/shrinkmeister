import logging

from django.utils.six import string_types
from django.core.cache import caches

from sorl.thumbnail.base import ThumbnailBackend
from sorl.thumbnail.conf import settings, defaults as default_settings
from sorl.thumbnail.helpers import tokey, serialize
from sorl.thumbnail.images import ImageFile, BaseImageFile
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry
from storages.backends.s3boto3 import S3Boto3Storage


shrinkmeister_cache = caches['shrinkmeister']

THUMBNAIL_BUCKET = settings.THUMBNAIL_BUCKET
SHRINKMEISTER_SERVER_NODE = getattr(settings, 'SHRINKMEISTER_SERVER_NODE', False)

logger = logging.getLogger(__name__)

class ImageLikeObject(BaseImageFile):
    def __init__(self, geometry_string, ratio, name):
        '''
        Pass ImageFile as source
        '''
        self.name = name
        self.size = parse_geometry(geometry_string, ratio)
        
    def exists(self):
        return True

    @property
    def url(self):
        return  '{}/{}'.format(settings.THUMBNAIL_SERVER_URL, self.name)


class ShrinkmeisterThumbnailBackend(ThumbnailBackend):
    def get_thumbnail(self, file_, geometry_string, **options):
        """
        Returns thumbnail as an ImageFile instance for file with geometry and
        options given. First it will try to get it from the key value store,
        secondly it will create it.
        """
        logger.debug('Getting thumbnail for file [%s] at [%s]', file_, geometry_string)

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

        name = self._get_thumbnail_filename(source, geometry_string, options)
        cached = shrinkmeister_cache.get(name, None)

        if cached:
            return cached

        if SHRINKMEISTER_SERVER_NODE:
            thumbnail = ImageFile(name, default.storage)
            source_image = default.engine.get_image(source)
            self._create_thumbnail(source_image, geometry_string, options,
                                    thumbnail)
            self._create_alternative_resolutions(source_image, geometry_string,
                                                    options, thumbnail.name)
            cached = shrinkmeister_cache.set(name, thumbnail)
            return thumbnail
        ratio = default.engine.get_image_ratio(source, options)
        return ImageLikeObject(geometry_string, ratio, name)