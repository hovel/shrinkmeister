# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import json
import math
from collections import namedtuple

from django.utils.encoding import force_text


def encode(value, charset='utf-8', errors='ignore'):
    """
    WARNING: this function does not convert non-utf-8 byte strings to utf-8
    """
    if isinstance(value, bytes):
        return value
    return value.encode(charset, errors=errors)


class ThumbnailError(Exception):
    pass


class SortedJSONEncoder(json.JSONEncoder):
    """
    A json encoder that sorts the dict keys
    """

    def __init__(self, **kwargs):
        kwargs['sort_keys'] = True
        super(SortedJSONEncoder, self).__init__(**kwargs)


def toint(number):
    """
    Helper to return rounded int for a float or just the int it self.
    """
    if isinstance(number, float):
        if number > 1:
            number = round(number, 0)
        else:
            # The following solves when image has small dimensions (like 1x54)
            # then scale factor 1 * 0.296296 and `number` will store `0`
            # that will later raise ZeroDivisionError.
            number = round(math.ceil(number), 0)
    return int(number)


def tokey(*args):
    """
    Computes a unique key from arguments given.
    """
    salt = '||'.join([force_text(arg) for arg in args])
    hash_ = hashlib.md5(encode(salt))
    return hash_.hexdigest()


def serialize(obj):
    return json.dumps(obj, cls=SortedJSONEncoder)


def deserialize(s):
    if isinstance(s, bytes):
        return json.loads(s.decode('utf-8'))
    return json.loads(s)


class ImageLikeObject(object):
    """
    Image object imitator for templates
    provides easy replacement for easy_thumbnail
    """

    def __init__(self, name, width=None, height=None, format='jpeg', storage=None):
        super(ImageLikeObject, self).__init__()
        self.width = width
        self.height = height
        self.format = format
        if storage:
            self.file = namedtuple('file', ['storage'])
            self.file.key = namedtuple('key', ['bucket', 'key'])
            self.file.key.bucket = namedtuple('bucket', ['name'])
            self.file.key.key = storage['key']
            self.file.key.bucket.name = storage['bucket']

    def resize(self, width, height):
        self.width = width
        self.height = height

    def crop(self, x_offset, y_offset, width, height):
        self.width = width
        self.height = height

    @property
    def url(self):
        return  '{}/{}'.format(settings.THUMBNAIL_SERVER_URL, self.name)


def merge_with_defaults(options):
    # FIXME several options will or may be ignored
    default_options = {
        'format': 'JPEG',  # will be ignored (format is always preserved)
        'quality': 80,  # will be ignored
        'colorspace': 'RGB',  # will be ignored
        'upscale': False,  # may be ignored
        'crop': False,
        'cropbox': None,  # may be ignored
        'rounded': None,  # will be ignored
        'padding': False,  # will be ignored
        'padding_color': '#ffffff',  # will be ignored
    }
    for key, value in default_options.items():
        options.setdefault(key, value)
    return options
