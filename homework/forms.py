from django.forms import ModelForm
from .models import Homework

from utils.mixins import DateTimeWidgetMixin

class HomeworkBaseForm(DateTimeWidgetMixin, ModelForm):
    class Meta:
        model = Homework
        fields = []


class HomeworkCreateForm(HomeworkBaseForm):
    class Meta(HomeworkBaseForm.Meta):
        model = Homework
        fields = ['subject', 'lesson_given', 'lesson_due', 'start_time',
                  'due_at', 'task', 'completion_percent', 'has_subtasks']


class HomeworkUpdateForm(HomeworkBaseForm):
    class Meta():
        model = Homework
        fields = ['lesson_due', 'due_at', 'task',
                  'completion_percent', 'has_subtasks']