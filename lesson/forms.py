from django.forms import ModelForm
from .models import Lesson

class LessonCreateForm(ModelForm):
    class Meta:
        model = Lesson
        fields = ['subject', 'type', 'start_time', 'duration']

class LessonUpdateForm(ModelForm):
    class Meta:
        model = Lesson
        fields = ['type', 'start_time', 'duration']