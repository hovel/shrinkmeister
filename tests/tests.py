# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import boto3
import requests
from wand.image import Image
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.cache import caches
from django.test import SimpleTestCase  # No Database iteraction

from shrinkmeister.helpers import ImageLikeObject, merge_with_defaults
from shrinkmeister.utils import generate_cache_key

from sorl.thumbnail.images import ImageFile
from sorl.thumbnail import get_thumbnail

from storages.backends.s3boto3 import S3Boto3Storage, S3Boto3StorageFile

class ImageFromHashTest(SimpleTestCase):
    def setUp(self):
        self.bucket = getattr(settings, 'THUMBNAIL_BUCKET')
        self.cache = caches[getattr(settings, 'THUMBNAIL_CACHE_NAME')]
        self.test_image_path = getattr(settings, 'THUMBNAIL_TEST_IMAGE',
                                       'shrinkmeister/test_image.jpg')
        self.s3_endpiont = getattr(settings, 'AWS_S3_HOST', None)
        self.s3_image_key = 'shrinkmeister_test_image.jpg'
        self.geometry_string = '50x50'

        self.cache.delete_pattern('*')

        try:
            img_file = open(self.test_image_path, 'rb')
        except IOError:
            self.fail("Can't open test image {}, don't your forget to setup THUMBNAIL_TEST_IMAGE?"
                      "".format(self.test_image_path))

        # Store image on S3
        client = boto3.client('s3', endpoint_url=self.s3_endpiont)
        try:
            client.upload_fileobj(
                Fileobj=img_file,
                Bucket=self.bucket, Key=self.s3_image_key,
                ExtraArgs={'StorageClass': 'REDUCED_REDUNDANCY'})
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchBucket":
                client.create_bucket(Bucket=self.bucket)
                client.upload_fileobj(
                    Fileobj=img_file,
                    Bucket=self.bucket, Key=self.s3_image_key,
                    ExtraArgs={'StorageClass': 'REDUCED_REDUNDANCY'})
            raise e

    def test_image_from_hash(self):
        storage = S3Boto3Storage(bucket=self.bucket)
        s3_file = S3Boto3StorageFile(name=self.s3_image_key, mode='r', storage=storage)
        
        # Mock model Image field
        # S3Boto3StorageFile store storage information in ._storage wich is not checked by 
        # ImageFile during storage identification
        s3_file.storage = storage
        
        image_s3 = ImageFile(s3_file)

        # Test local part
        options = {}
        thumbnail = get_thumbnail(s3_file, self.geometry_string, **options)
        print('Generated thumbnail url: {}'.format(thumbnail.url))
        print('Thumbnail cache key: {}'.format(thumbnail.name))

        # Now, test shrinkmeister server (should be up and running)
        resp = requests.get(thumbnail.url)
        image = Image(blob=resp.content)
        self.assertEqual(image.width, 50)
        self.assertEqual(image.height, 38)

        thumbnail_from_cache = self.cache.get(thumbnail.name)
        self.assertNotEqual(thumbnail_from_cache, None,
                            msg="No image in cache detected :(")
        image = Image(blob=resp.content)
        self.assertEqual(image.width, 50)
        self.assertEqual(image.height, 38)

        resp = requests.get(thumbnail_from_cache.url)

        url, ext = thumbnail_from_cache.url.rsplit('.', 1)
        x2_url = '{}@2x.{}'.format(url, ext)
        print('x2 url {}' .format(x2_url))
        resp = requests.get(x2_url)
        image = Image(blob=resp.content)
        self.assertEqual(image.width, 100)
        self.assertEqual(image.height, 75)
