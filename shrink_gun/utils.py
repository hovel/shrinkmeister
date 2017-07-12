from django.core.files.base import ContentFile
import boto3
from urllib2 import urlopen
from wand.image import Image
from hashlib import md5
from django.core.cache import cache
from django.core import signing
from django.conf import settings
import re

THUMBNAIL_SERVER_URL = getattr(settings, 'THUMBNAIL_SERVER_URL')

class ImageLikeObject(Object):
    '''
    Image object imitator for templates
    provides easy replacement for easy_thumbnail
    '''
    def _init__(self, url, width, height):
        super(ImageLikeObject, self).__init__()
        self.url = url
        self.width = width
        self.height = height

def calculate_size(self, height, width, target_geometry):
    '''
    Calculate target image size based on proportion
    target_w/target_h = source_w/source_h and preserve aspect ratio

    If aspect ratio (target_w/target_h) < (source_w/source_h) ignore target_h, and ignore target_w otherwise
    '''
    geometry_splitted = geometry.strip().split('x')
    target_w = int(geometry_splitted[0] or 0)
    try:
        ystr = re.sub("\D", "", geometry_splitted[1]) # Remove possible ImageMagick options from end of the string
        target_h = int(ystr or 0)
    except IndexError:
        target_h = 0

    if not target_h and not target_w:
        raise Exception('wrong geometry')

    if (target_h and ((target_w/target_h) < (width/heigt))) or not target_h:
        target_h = int(target_w * height / float(width))
    else:
        target_w = int(target_h * width / float(height))
        
    return (target_w, target_h)

def image_from_url(url):
    '''
    Return Wand Image from target url
    '''
    stream = urlopen(url)
    img = Image(file=stream)
    return img

def image_from_s3(bucket, key):
    '''
    Return Wand Image from S3 bucket/key pair
    '''
    client = boto3.client('s3')
    stream = client.get_object(Bucket=bucket, Key=key)
    img = Image(file=stream['Body'])
    return img

def generate_cache_key(url='', bucket='', key='', size='', extra=''):
    '''
    Generate hash key for cache for specific image.
    Pass any addional params (such as database primary key)
    to 'extra' for better detection.
    '''
    md = md5(url+bucket+key+size+extra)
    return md.hexdigest()

def generate_protected_request(bucket, key, size):
    '''
    Create encrypted string containing address of source image and target image size
    '''
    struct = {
        'bucket': bucket,
        'key': key,
        'size': size
    }
    return signing.dumps(struct)

def shrink_and_store(img, size, target_bucket, target_key, cache_key):
    '''
    Sample image to target size,
    Store it on S3

    
    For 'size' provide imagemagick options
    http://www.imagemagick.org/script/command-line-processing.php#geometry

    Return image data stored in Cache
    '''
    img.transform(resize=size)
    out_img = ContentFile(img.make_blob('jpeg'))
    client = boto3.client('s3')
    #TODO Extra Args should be passed via arguments?
    client.upload_fileobj(out_img, Bucket=target_bucket, Key=target_key, ExtraArgs={'StorageClass': 'REDUCED_REDUNDANCY'})
    url = client.generate_presigned_url(ClientMethod='get_object', Params={ 'Bucket': target_bucket, 'Key': target_key })
    image_info = {
        'url': url,
        'height': img.height,
        'width': img.width
    }
    cache.set(cache_key, image_info)
    return image_info

def get_thumbnail(img, target_geometry):
    width, height = calculate_size(img.width, img.height, target_geometry)
    #TODO Find how to get bucket/key from image object
    bucket = img.storage.bucket_name
    key = img.url
    url = THUMBNAIL_SERVER_URL + generate_protected_request(bucket, key, target_geometry)
    return ImageLikeObject(url, width, height)


