# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseRedirect, Http404

from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView
from forms import ImageURLForm
from urllib2 import urlopen
from wand.image import Image
import boto3
from django.core.files.base import ContentFile
from django.conf import settings
from utils import image_from_url, image_from_s3, shrink_and_store, generate_cache_key
from django.core import signing


class ThumbnailFromURL(FormView):
    form_class = ImageURLForm
    template_name = 'shrink_gun/url_form.html'
    #TODO Alert "Not configured" during systemcheck if bucket not specified
    bucket = getattr(settings, 'SHRINK_BUCKET', 'shrinktest')
    #TODO This should be readed from GET
    sample_size = '500x500'

    def form_valid(self, form):
        url = form.cleaned_data['url']
        img = image_from_url(url)
        key = generate_cache_key(url=url, size=self.sample_size)
        img_info = shrink_and_store(img, self.sample_size, self.bucket, key+'.jpeg', key)
        return HttpResponseRedirect(img_info['url'])


class ThumbnailFromHash(RedirectView):
    bucket = getattr(settings, 'SHRINK_BUCKET', 'shrinktest')
    def get_redirect_url(self, *args, **kwargs):
        obj = kwargs['hash']
        try:
            obj = signing.loads(obj)
        except:
            raise Http404
        img = image_from_s3(obj['bucket'], obj['key'])
        key = generate_cache_key(bucket=obj['bucket'], key=obj['key'], size=obj['size'])
        img_info = shrink_and_store(img, obj['size'], self.bucket, key+'.jpeg', key)
        return img_info['url']
                    