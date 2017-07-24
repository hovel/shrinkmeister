# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache

from shrinkmeister.utils import generate_cache_key, \
    generate_lazy_thumbnail_url, create_thumbnail
from shrinkmeister.helpers import ThumbnailError, ImageLikeObject, \
    merge_with_defaults


def get_thumbnail(file_, geometry_string, **options):
    """Return cached or lazy thumbnail"""

    storage_file = getattr(file_, 'file', None)
    key_object = getattr(storage_file, 'key', None)
    if not key_object:
        raise ThumbnailError('Only S3 objects are supported')

    bucket = key_object.bucket.name
    key = key_object.key
    options = merge_with_defaults(options)

    # TODO to use cache here we need same config for "client" and "server"
    # cache_key = generate_cache_key(
    #     bucket=bucket, key=key, geometry_string=geometry_string, **options)
    #
    # cached_thumbnail = cache.get(cache_key, None)
    # if cached_thumbnail:
    #     return cached_thumbnail

    if not hasattr(file_, 'width') or not hasattr(file_, 'height'):
        raise ThumbnailError('Wrong image instance')

    placeholder = ImageLikeObject('', file_.width, file_.height)
    lazy_thumbnail = create_thumbnail(placeholder, geometry_string, options)
    lazy_thumbnail.url = generate_lazy_thumbnail_url(
        bucket=bucket, key=key, geometry_string=geometry_string,
        options=options)

    return lazy_thumbnail
