# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms


class ImageURLForm(forms.Form):
    url = forms.URLField()
