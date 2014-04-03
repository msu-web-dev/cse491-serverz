from django import forms
from image.models import Image


class ImageUploadForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    image = forms.ImageField()