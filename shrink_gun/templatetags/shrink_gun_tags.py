# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django import template

from shrink_gun.utils import get_thumbnail

register = template.Library()

if django.VERSION >= (1, 9):
    register.simple_tag(func=get_thumbnail, name='thumbnail')
else:
    register.assignment_tag(func=get_thumbnail, name='thumbnail')


@register.simple_tag
def endthumbnail():
    return ''
