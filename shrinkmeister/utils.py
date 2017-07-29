# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core import signing
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.urls.base import reverse
from django.utils.six.moves.urllib.parse import urljoin

from shrinkmeister.engine import Engine
from shrinkmeister.helpers import tokey, serialize, ImageLikeObject
from shrinkmeister.parsers import parse_geometry


shrinkmeister_cache = caches[getattr(settings, 'THUMBNAIL_CACHE_NAME')]


def generate_cache_key(url='', bucket='', key='', geometry_string='',
                       **options):
    """
    Generate hash key for cache for specific image.
    """
    cache_key = tokey(url, bucket, key, geometry_string, serialize(options))
    return cache_key


def generate_lazy_thumbnail_url(**url_data):
    signed_data = signing.dumps(url_data, key=settings.THUMBNAIL_SECRET_KEY)
    if not settings.THUMBNAIL_SERVER_URL.startswith('http') or \
            not settings.THUMBNAIL_SERVER_URL.endswith('/'):
        raise ImproperlyConfigured(
            'THUMBNAIL_SERVER_URL must start with "http" and end with "/"')
    relative_url = reverse('thumbnail_from_hash', kwargs={'hash': signed_data})
    url = urljoin(settings.THUMBNAIL_SERVER_URL, relative_url)
    return url


def create_thumbnail(image, geometry_string, options):
    engine = Engine()
    ratio = float(image.width) / image.height
    geometry = parse_geometry(geometry_string, ratio)
    thumbnail = engine.create(image, geometry, options)
    return thumbnail


def store_thumbnail(thumbnail, cache_key, endpoint_url=None):
    thumbnail_filename = '{}.{}'.format(cache_key, thumbnail.format)

    client = boto3.client('s3', endpoint_url=endpoint_url)

    # TODO Extra Args should be passed via arguments?
    try:
        client.upload_fileobj(
            Fileobj=ContentFile(thumbnail.make_blob(),
                                name=thumbnail_filename),
            Bucket=settings.THUMBNAIL_BUCKET, Key=thumbnail_filename,
            ExtraArgs={'StorageClass': 'REDUCED_REDUNDANCY'})
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchBucket":
            client.create_bucket(Bucket=settings.THUMBNAIL_BUCKET)
            return store_thumbnail(thumbnail, cache_key, endpoint_url)
        raise e

    thumbnail_url = client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': settings.THUMBNAIL_BUCKET,
                'Key': thumbnail_filename},
        ExpiresIn=settings.THUMBNAIL_TTL)

    shrinkmeister_cache.set(cache_key, ImageLikeObject(
        url=thumbnail_url, width=thumbnail.width, height=thumbnail.height))

    return thumbnail_url
