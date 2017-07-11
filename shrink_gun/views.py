# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.views.generic.edit import FormView
from forms import ImageURLForm
from urllib2 import urlopen
from wand.image import Image
import boto
import cStringIO

class ThumbnailFromURL(FormView):
    form_class = ImageURLForm
    template_name = 'shrink_gun/url_form.html'

    def form_valid(self, form):
        stream = urlopen(form.cleaned_data['url'])
        img = Image(file=stream)
        img.sample(100,100)
        out_img = cStringIO.StringIO()
        img.format = 'jpg'
        img.save(file=out_img)
        conn = boto.connect_s3()
        b = conn.get_bucket('shrinktest')
        k = b.new_key('example.jpg')
        k.set_contents_from_string(out_img.getvalue())
        url = k.generate_url(expires_in=300)
        stream.close()
        return HttpResponseRedirect(url)
