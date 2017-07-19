# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def get_thumbnail(file_, geometry_string, **options):
    from shrinkmeister.base import get_thumbnail as _get_thumbnail
    return _get_thumbnail(file_, geometry_string, **options)
