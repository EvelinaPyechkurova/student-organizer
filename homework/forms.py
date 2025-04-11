from django.forms import ModelForm
from .models import Homework

class HomeworkForm(ModelForm):
    class Meta:
        model = Homework
        fields = ['subject', 'lesson_given', 'lesson_due', 'start_time',
                  'due_at', 'task', 'completion_percent', 'has_subtasks']