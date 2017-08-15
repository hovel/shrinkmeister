# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import boto3
from django.conf import settings
from django.core import signing
from django.core.cache import caches
from django.http import HttpResponseRedirect, Http404
from django.utils.six.moves.urllib.request import urlopen
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from wand.image import Image

from forms import ImageURLForm
from shrinkmeister.helpers import merge_with_defaults
from shrinkmeister.parsers import parse_geometry
from shrinkmeister.utils import generate_cache_key, store_thumbnail, \
    create_thumbnail

shrinkmeister_cache = caches['shrinkmeister']
s3_endpoint_url = getattr(settings, 'AWS_S3_HOST', None)
alternative_resolutions = getattr(settings, 'THUMBNAIL_ALTERNATIVE_RESOLUTIONS', True)
alternative_resolutions.append(1)
alternative_resolutions.sort(reverse=True)


# TODO avoid code duplication

def generate_thumbnails(image, geometry_string, cache_key, options, alt_resolutions=None, s3_endpoint_url=None):
    if not alt_resolutions:
        alt_resolutions = [1]
    for resolution in alt_resolutions:
        options['scale_factor'] = resolution
        thumbnail = create_thumbnail(image, geometry_string, options)
        if resolution != 1:
            new_key = '{}@{}x'.format(cache_key, resolution)
        else:
            new_key = cache_key
        thumbnail.url = store_thumbnail(thumbnail, new_key, s3_endpoint_url)
    return thumbnail.url

class ThumbnailFromURL(FormView):
    form_class = ImageURLForm
    template_name = 'shrinkmeister/url_form.html'
    # TODO This should be readed from GET
    sample_geometry_string = '500x500'

    def dispatch(self, request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404()
        return super(ThumbnailFromURL, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        url = form.cleaned_data['url']
        geometry_string = self.sample_geometry_string
        options = merge_with_defaults({})

        cache_key = generate_cache_key(
            url=url, geometry_string=geometry_string, **options)

        cached_thumbnail = shrinkmeister_cache.get(cache_key, None)
        if cached_thumbnail:
            return cached_thumbnail.url

        stream = urlopen(url)
        image = Image(file=stream)
        url = generate_thumbnails(image, geometry_string, cache_key, options, alternative_resolutions, s3_endpoint_url)
        return HttpResponseRedirect(url)


class ThumbnailFromHash(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        try:
            data = signing.loads(kwargs['hash'],
                                 key=settings.THUMBNAIL_SECRET_KEY)
        except Exception as e:
            raise Http404()

        try:
            bucket = data['bucket']
            key = data['key']
            geometry_string = data['geometry_string']
            options = merge_with_defaults(data['options'])
        except KeyError:
            raise Http404()

        cache_key = generate_cache_key(
            bucket=bucket, key=key, geometry_string=geometry_string, **options)

        cached_thumbnail = shrinkmeister_cache.get(cache_key, None)
        if cached_thumbnail:
            return cached_thumbnail.url

        client = boto3.client('s3')
        stream = client.get_object(Bucket=bucket, Key=key)
        image = Image(file=stream['Body'])
        url = generate_thumbnails(image, geometry_string, cache_key, options, alternative_resolutions, s3_endpoint_url)
        return url
