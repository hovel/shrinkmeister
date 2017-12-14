from django.views.generic import CreateView
from models import Image


class ImageUploader(CreateView):
    model = Image
    fields = ['image']
    success_url = '/'

    def get_context_data(self, *args, **kwargs):
        ctx = super(ImageUploader, self).get_context_data(*args, **kwargs)
        ctx['images'] = Image.objects.all()
        return ctx

