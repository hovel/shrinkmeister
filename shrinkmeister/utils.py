# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils.six.moves.urllib.request import urlopen
from wand.image import Image

from shrinkmeister.engine import Engine
from shrinkmeister.helpers import tokey, serialize, ImageLikeObject
from shrinkmeister.parsers import parse_geometry


def image_from_url(url):
    """
    Return Wand Image from target url
    """
    stream = urlopen(url)
    img = Image(file=stream)
    return img


def image_from_s3(bucket, key):
    """
    Return Wand Image from S3 bucket/key pair
    """
    client = boto3.client('s3')
    stream = client.get_object(Bucket=bucket, Key=key)
    img = Image(file=stream['Body'])
    return img


def generate_cache_key(url='', bucket='', key='', geometry_string='',
                       **options):
    """
    Generate hash key for cache for specific image.
    """
    cache_key = tokey(url, bucket, key, geometry_string, serialize(options))
    return cache_key


def generate_lazy_thumbnail_url(**url_data):
    signed_data = signing.dumps(url_data, key=settings.THUMBNAIL_SECRET_KEY)
    url = '/'.join(part.rstrip('/') for part in
                   [settings.THUMBNAIL_SERVER_URL, 'hash', signed_data])
    return url


def create_thumbnail(image, geometry_string, options):
    engine = Engine()
    ratio = float(image.width) / image.height
    geometry = parse_geometry(geometry_string, ratio)
    thumbnail = engine.create(image, geometry, options)
    return thumbnail


def store_thumbnail(thumbnail, cache_key, endpoint_url=None):
    thumbnail_filename = '{}.{}'.format(cache_key, thumbnail.format)

    import botocore.session
    from botocore.client import Config

    client = boto3.client('s3', endpoint_url=endpoint_url)

    # TODO Extra Args should be passed via arguments?
    try:
        client.upload_fileobj(
            Fileobj=ContentFile(thumbnail.make_blob(), name=thumbnail_filename),
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

    cache.set(cache_key, ImageLikeObject(
        url=thumbnail_url, width=thumbnail.width, height=thumbnail.height))

    return thumbnail_url
