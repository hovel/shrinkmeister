# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core import signing
from django.core.cache import caches
from django.http import HttpResponseRedirect, Http404
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from forms import ImageURLForm
from shrinkmeister.helpers import merge_with_defaults
from shrinkmeister.utils import image_from_url, image_from_s3, \
    generate_cache_key, store_thumbnail, create_thumbnail

shrinkmeister_cache = caches['shrinkmeister']


# TODO avoid code duplication


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

        image = image_from_url(url)
        thumbnail = create_thumbnail(image, geometry_string, options)
        thumbnail.url = store_thumbnail(thumbnail, cache_key,
                                        settings.S3_ENDPOINT)

        return HttpResponseRedirect(thumbnail.url)


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

        image = image_from_s3(bucket, key)
        thumbnail = create_thumbnail(image, geometry_string, options)
        thumbnail.url = store_thumbnail(thumbnail, cache_key,
                                        settings.S3_ENDPOINT)

        return thumbnail.url
