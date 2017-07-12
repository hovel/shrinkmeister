from django.core.files.base import ContentFile
import boto3
from urllib2 import urlopen
from wand.image import Image
from hashlib import md5
from django.core.cache import cache

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
    img = Image(file=stream)
    return img

def generate_cache_key(url='', bucket='', key='', size='', extra=''):
    '''
    Generate hash key for cache for specific image.
    Pass any addional params (such as database primary key)
    to 'extra' for better detection.
    '''
    md = md5(url+bucket+key+size+extra)
    return md.hexdigest()

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


