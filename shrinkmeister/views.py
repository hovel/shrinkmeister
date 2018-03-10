# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import boto3
from django.conf import settings
from django.core import signing
from django.core.cache import caches
from django.http import HttpResponseRedirect, Http404
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from shrinkmeister.helpers import merge_with_defaults
from shrinkmeister.utils import generate_cache_key
from storages.backends.s3boto3 import S3Boto3Storage, S3Boto3StorageFile

from sorl import get_thumbnail

shrinkmeister_cache = caches['shrinkmeister']
s3_endpoint_url = getattr(settings, 'AWS_S3_HOST', None)
alternative_resolutions = getattr(settings, 'THUMBNAIL_ALTERNATIVE_RESOLUTIONS', True)
alternative_resolutions.append(1)
alternative_resolutions.sort(reverse=True)


# TODO avoid code duplication
class ThumbnailFromHash(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        try:
            data = signing.loads(kwargs['hash'],
                            key=settings.THUMBNAIL_SECRET_KEY)
            bucket = data['bucket']
            key = data['key']
            geometry_string = data['geometry_string']
        except KeyError:
            raise Http404()

        if 'options' in data:
            options = merge_with_defaults(data['options'])
        else:
            options = {}

        if 'cache_key' in data:
            cache_key = data['cache_key']
        else:
            # !!! WARNING !!!
            # Generating same cache_key on both sides may be tricky
            # Preferred way is to transfer cache_key from client side
            cache_key = generate_cache_key(
                bucket=bucket, key=key, geometry_string=geometry_string, **options)

        # Multiple calls for same image during thumbnail generation scenario
        cached_thumbnail = shrinkmeister_cache.get(cache_key, None)
#        if cached_thumbnail:
#            return cached_thumbnail.url

        client = boto3.client('s3')
        storage = S3Boto3Storage(bucket=bucket)
        s3_file = S3Boto3StorageFile(name=key, mode='r', storage=storage)
        # Mock model Image field
        # S3Boto3StorageFile store storage information in ._storage wich is not checked by 
        # ImageFile during storage identification
        s3_file.storage = storage
        options['cache_key'] = cache_key
        thumbnail = get_thumbnail(s3_file, geometry_string, **options)
        return thumbnail.url
