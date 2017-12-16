from django.conf.urls import url
from imagestorage.views import ImageUploader

urlpatterns = [
    url(r'^$', ImageUploader.as_view(), name='image_uploader'),
]
