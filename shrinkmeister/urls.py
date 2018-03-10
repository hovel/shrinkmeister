from django.conf.urls import url
from views import ThumbnailFromHash

urlpatterns = [
    url(r'^hash/(?P<hash>\S+)/$', ThumbnailFromHash.as_view(), name='thumbnail_from_hash')
]
