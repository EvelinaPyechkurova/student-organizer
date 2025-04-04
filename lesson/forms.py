from django.forms import ModelForm
from .models import Lesson

class LessonForm(ModelForm):
    class Meta:
        model = Lesson
        fields = ['subject', 'type', 'start_time', 'duration']