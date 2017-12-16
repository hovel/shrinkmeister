# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shrinkmeister.helpers import toint
from shrinkmeister.parsers import parse_cropbox, parse_crop
from sorl.thumbnail.engines.base import EngineBase

from django.conf import settings

class DummyEngine(EngineBase):

    def create(self, image, geometry, options):
        """
        Processing conductor, returns the thumbnail as an image engine instance
        """
        image = self.cropbox(image, geometry, options)
        image = self.scale(image, geometry, options)
        image = self.crop(image, geometry, options)
        return image

    def get_image_size(self, image):
        return image.size

    def get_image_info(self, image):
        return image.info or {}

    def is_valid_image(self, raw_data):
        return True

    def _cropbox(self, image, x, y, x2, y2):
        image.set_size(size=(x2-x, y2-y))
        return image

    def _orientation(self, image):
        return image

    def _scale(self, image, width, height):
        return image.set_size(width, height)

    def _crop(self, image, width, height, x_offset, y_offset):
        return image.set_size(width, height)

    def _rounded(self, image, r):
        return image

    def _blur(self, image, radius):
        return image

    def _padding(self, image, geometry, options):
        return image

    def write(self, image, options, thumbnail):
        # Here we set url for our server
        thumbnail.url = '{}/{}'.format(settings.THUMBNAIL_SERVER_URL, thumbnail.name)
