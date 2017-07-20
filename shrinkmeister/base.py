# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache

from shrinkmeister.engine import Engine
from shrinkmeister.utils import generate_cache_key, generate_thumbnail_url
from shrinkmeister.helpers import ThumbnailError, ImageLikeObject, \
    merge_with_defaults
from shrinkmeister.parsers import parse_geometry


def get_thumbnail(file_, geometry_string, **options):
    options = merge_with_defaults(options)

    storage_file = getattr(file_, 'file', None)
    key_object = getattr(storage_file, 'key', None)
    if not key_object:
        raise ThumbnailError('Only S3 objects are supported')

    bucket = key_object.bucket.name
    key = key_object.key

    cache_key = generate_cache_key(
        bucket=bucket, key=key, geometry_string=geometry_string, **options)
    thumbnail = cache.get(cache_key, None)
    if thumbnail:
        return thumbnail

    if not hasattr(file_, 'width') or not hasattr(file_, 'height'):
        raise ThumbnailError('Wrong image instance')

    engine = Engine()
    placeholder = ImageLikeObject('', file_.width, file_.height)
    ratio = float(file_.width) / file_.height
    geometry = parse_geometry(geometry_string, ratio)

    thumbnail = engine.create(placeholder, geometry, options)

    url_data = {
        'bucket': bucket,
        'key': key,
        'geometry_string': geometry_string,
        'options': options
    }
    thumbnail.url = generate_thumbnail_url(**url_data)

    return thumbnail
