from django.forms import ModelForm
from .models import Assessment

from utils.mixins import DateTimeWidgetMixin

class AssessmentBaseForm(DateTimeWidgetMixin, ModelForm):
    class Meta:
        model = Assessment
        fields = []


class AssessmentCreateForm(AssessmentBaseForm):
    class Meta(AssessmentBaseForm.Meta):
        model = Assessment
        fields = ['subject', 'lesson', 'type', 'start_time', 'duration', 'description']


class AssessmentUpdateForm(AssessmentBaseForm):
    class Meta(AssessmentBaseForm.Meta):
        model = Assessment
        fields = ['lesson', 'type', 'start_time', 'duration', 'description', 'reminder_sent']