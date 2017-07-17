# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

from shrink_gun.utils import get_thumbnail

register = template.Library()

register.simple_tag(func=get_thumbnail, name='thumbnail')
