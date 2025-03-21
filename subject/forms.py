from django.forms import ModelForm
from .models import Subject

class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'image_url']