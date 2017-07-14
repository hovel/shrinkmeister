# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from hashlib import md5

import boto3
from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.six.moves.urllib.request import urlopen
from wand.image import Image

# TODO Alert "Not configured" during systemcheck if constants are not specified
THUMBNAIL_SERVER_URL = getattr(settings, 'THUMBNAIL_SERVER_URL')
THUMBNAIL_BUCKET = getattr(settings, 'THUMBNAIL_BUCKET')
GEOMETRY_PATTERN = re.compile(r'^(?P<x>\d+)?(?:x(?P<y>\d+))?$')


class ThumbnailError(Exception):
    pass


class ImageLikeObject(object):
    """
    Image object imitator for templates
    provides easy replacement for easy_thumbnail
    """

    def __init__(self, url, width, height):
        super(ImageLikeObject, self).__init__()
        self.url = url
        self.width = width
        self.height = height


def parse_geometry(geometry, ratio=None):
    m = GEOMETRY_PATTERN.match(geometry)
    if not m:
        raise ThumbnailError('Wrong geometry')
    x = m.group('x')
    y = m.group('y')
    if x is None and y is None:
        raise ThumbnailError('Wrong geometry')
    if x is not None:
        x = int(x)
    if y is not None:
        y = int(y)
    if ratio is not None:
        ratio = float(ratio)
        if x is None:
            x = int(round(y * ratio)) or 1
        elif y is None:
            y = int(round(x / ratio)) or 1
    return x, y


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
    img = Image(file=stream['Body'])  # FIXME maybe `blob`?
    return img


def generate_cache_key(url='', bucket='', key='', geometry_string='', extra='',
                       **options):
    """
    Generate hash key for cache for specific image.
    Pass any addional params (such as database primary key)
    to 'extra' for better detection.
    """
    # TODO options
    md = md5(url + bucket + key + geometry_string + extra)
    return md.hexdigest()


def generate_thumbnail_url(**url_data):
    signed_data = signing.dumps(url_data)
    url = urljoin(urljoin(THUMBNAIL_SERVER_URL, 'hash/'), signed_data)
    return url


def shrink_and_store(img, cache_key, geometry_string, **options):
    """
    Sample image to target size,
    Store it on S3

    For 'size' provide imagemagick options
    http://www.imagemagick.org/script/command-line-processing.php#geometry
    """
    img.transform(resize=geometry_string)
    thumb_filename = '{}.{}'.format(cache_key, img.format)
    client = boto3.client('s3')
    # TODO Extra Args should be passed via arguments?
    client.upload_fileobj(
        Fileobj=ContentFile(img.make_blob(), name=thumb_filename),
        Bucket=THUMBNAIL_BUCKET, Key=thumb_filename,
        ExtraArgs={'StorageClass': 'REDUCED_REDUNDANCY'})
    url = client.generate_presigned_url(ClientMethod='get_object',
                                        Params={'Bucket': THUMBNAIL_BUCKET,
                                                'Key': thumb_filename})
    thumb = ImageLikeObject(url=url, width=img.width, height=img.height)
    cache.set(cache_key, thumb)
    return thumb


def get_thumbnail(file_, geometry_string, **options):
    if not hasattr(file_, 'key'):
        raise ThumbnailError('Only S3 objects are supported')

    bucket = file_.key.bucket
    key = file_.key.key

    cache_key = generate_cache_key(
        bucket=bucket, key=key, geometry_string=geometry_string, **options)
    thumb = cache.get(cache_key, None)
    if thumb:
        return thumb

    if not hasattr(file_, 'width') or not hasattr(file_, 'height'):
        raise ThumbnailError('Wrong image instance')

    ratio = float(file_.width) / file_.height
    thumb_width, thumb_height = parse_geometry(geometry_string, ratio)

    url_data = {
        'bucket': bucket,
        'key': key,
        'geometry_string': geometry_string,
        'options': options
    }
    thumb_url = generate_thumbnail_url(**url_data)

    thumb = ImageLikeObject(thumb_url, thumb_width, thumb_height)
    return thumb
