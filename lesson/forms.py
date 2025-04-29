from django.forms import ModelForm
from .models import Lesson

from utils.mixins import DateTimeWidgetMixin

class LessonCreateForm(DateTimeWidgetMixin, ModelForm):
    class Meta:
        model = Lesson
        fields = ['subject', 'type', 'start_time', 'duration']


class LessonUpdateForm(DateTimeWidgetMixin, ModelForm):
    class Meta:
        model = Lesson
        fields = ['type', 'start_time', 'duration']
