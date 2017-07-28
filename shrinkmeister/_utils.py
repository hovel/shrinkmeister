# This utils require Wand to work
import boto3
from wand.image import Image

def image_from_url(url):
    """
    Return Wand Image from target url
    """
    stream = urlopen(url)
    img = Image(file=stream)
    return img


def image_from_s3(bucket, key, endpoint_url=None):
    """
    Return Wand Image from S3 bucket/key pair
    """
    client = boto3.client('s3', endpoint_url=endpoint_url)
    stream = client.get_object(Bucket=bucket, Key=key)
    img = Image(file=stream['Body'])
    return img
