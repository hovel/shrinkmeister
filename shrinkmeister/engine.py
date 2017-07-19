# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shrinkmeister.helpers import toint
from shrinkmeister.parsers import parse_cropbox, parse_crop


class Engine(object):
    def create(self, image, geometry, options):
        image = self.scale(image, geometry, options)
        image = self.crop(image, geometry, options)
        return image

    def _calculate_scaling_factor(self, x_image, y_image, geometry, options):
        crop = options['crop']
        factors = (geometry[0] / x_image, geometry[1] / y_image)
        return max(factors) if crop else min(factors)

    def scale(self, image, geometry, options):
        """
        Wrapper for ``_scale``
        """
        upscale = options['upscale']
        x_image, y_image = map(float, self.get_image_size(image))
        factor = self._calculate_scaling_factor(x_image, y_image, geometry, options)

        if factor < 1 or upscale:
            width = toint(x_image * factor)
            height = toint(y_image * factor)
            image = self._scale(image, width, height)

        return image

    def crop(self, image, geometry, options):
        """
        Wrapper for ``_crop``
        """
        crop = options['crop']
        x_image, y_image = self.get_image_size(image)

        if not crop or crop == 'noop':
            return image
        elif crop == 'smart':
            raise NotImplementedError()

        # Handle any other crop option with the backend crop function.
        geometry = (min(x_image, geometry[0]), min(y_image, geometry[1]))
        x_offset, y_offset = parse_crop(crop, (x_image, y_image), geometry)
        return self._crop(image, geometry[0], geometry[1], x_offset, y_offset)

    def get_image_ratio(self, image, options):
        """
        Calculates the image ratio. If cropbox option is used, the ratio
        may have changed.
        """
        cropbox = options['cropbox']

        if cropbox:
            x, y, x2, y2 = parse_cropbox(cropbox)
            x = x2 - x
            y = y2 - y
        else:
            x, y = self.get_image_size(image)

        return float(x) / y

    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
        """
        return image.width, image.height

    def _scale(self, image, width, height):
        """
        Does the resizing of the image
        """
        image.resize(width, height)
        return image

    def _crop(self, image, width, height, x_offset, y_offset):
        """
        Crops the image
        """
        image.crop(x_offset, y_offset, width=width, height=height)
        return image
