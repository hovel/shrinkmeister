from django import forms

class ImageURLForm(forms.Form):
    url = forms.URLField()