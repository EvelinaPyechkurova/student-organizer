from django.forms import ModelForm
from .models import Assessment

class AssessmentForm(ModelForm):
    class Meta:
        model = Assessment
        fields = ['subject', 'lesson', 'type', 'start_time', 'duration', 'description']
