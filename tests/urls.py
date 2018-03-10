from django.conf.urls import url, include
from imagestorage.views import ImageUploader

urlpatterns = [
    url(r'^$', ImageUploader.as_view(), name='image_uploader'),
    url(r'^', include('shrinkmeister.urls')),
]
