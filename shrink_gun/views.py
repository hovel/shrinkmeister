# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import signing
from django.core.cache import cache
from django.http import HttpResponseRedirect, Http404
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from forms import ImageURLForm
from utils import image_from_url, image_from_s3, shrink_and_store, \
    generate_cache_key


class ThumbnailFromURL(FormView):
    form_class = ImageURLForm
    template_name = 'shrink_gun/url_form.html'
    # TODO This should be readed from GET
    sample_geometry_string = '500x500'

    def form_valid(self, form):
        url = form.cleaned_data['url']

        cache_key = generate_cache_key(
            url=url, geometry_string=self.sample_geometry_string)
        thumb = cache.get(cache_key, None)
        if thumb:
            return thumb.url

        img = image_from_url(url)
        thumb = shrink_and_store(img, cache_key, self.sample_geometry_string)
        return HttpResponseRedirect(thumb.url)


class ThumbnailFromHash(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            data = signing.loads(kwargs['hash'])
        except Exception as e:
            raise Http404()

        bucket = data['bucket']
        key = data['key']
        geometry_string = data['geometry_string']
        options = data['options']

        cache_key = generate_cache_key(
            bucket=bucket, key=key, geometry_string=geometry_string, **options)
        thumb = cache.get(cache_key, None)
        if thumb:
            return thumb.url

        img = image_from_s3(bucket, key)
        thumb = shrink_and_store(img, cache_key, geometry_string, **options)
        return thumb.url
