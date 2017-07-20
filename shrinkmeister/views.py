# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.http import HttpResponseRedirect, Http404
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from forms import ImageURLForm
from shrinkmeister.engine import Engine
from shrinkmeister.helpers import merge_with_defaults
from shrinkmeister.parsers import parse_geometry
from shrinkmeister.utils import image_from_url, image_from_s3, \
    generate_cache_key, store_thumbnail


# TODO avoid code duplication


class ThumbnailFromURL(FormView):
    form_class = ImageURLForm
    template_name = 'shrinkmeister/url_form.html'
    # TODO This should be readed from GET
    sample_geometry_string = '500x500'

    def form_valid(self, form):
        url = form.cleaned_data['url']

        cache_key = generate_cache_key(
            url=url, geometry_string=self.sample_geometry_string)
        thumbnail = cache.get(cache_key, None)
        if thumbnail:
            return thumbnail.url

        engine = Engine()
        image = image_from_url(url)
        ratio = float(image.width) / image.height
        geometry = parse_geometry(self.sample_geometry_string, ratio)

        thumbnail = engine.create(image, geometry, merge_with_defaults({}))
        store_thumbnail(thumbnail, cache_key)

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
            options = data['options']
        except KeyError:
            raise Http404()

        cache_key = generate_cache_key(
            bucket=bucket, key=key, geometry_string=geometry_string, **options)
        thumbnail = cache.get(cache_key, None)
        if thumbnail:
            return thumbnail.url

        engine = Engine()
        image = image_from_s3(bucket, key)
        ratio = float(image.width) / image.height
        geometry = parse_geometry(geometry_string, ratio)

        thumbnail = engine.create(image, geometry, options)
        store_thumbnail(thumbnail, cache_key)

        return thumbnail.url
