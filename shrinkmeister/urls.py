from django.conf.urls import url
from views import ThumbnailFromURL, ThumbnailFromHash

urlpatterns = [
    url(r'^url/$', ThumbnailFromURL.as_view(), name='thumbnail_from_url'),
    url(r'^hash/(?P<hash>\S+)/$', ThumbnailFromHash.as_view(), name='thumbnail_from_hash')
]
