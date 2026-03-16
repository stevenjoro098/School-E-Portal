# forms.py
from django import forms
from .models import VideosResource

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideosResource
        fields = ['title', 'description', 'video']