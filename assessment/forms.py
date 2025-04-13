from django.forms import ModelForm
from .models import Assessment

class AssessmentBaseForm(ModelForm):
    class Meta:
        model = Assessment


class AssessmentCreateForm(AssessmentBaseForm):
    class Meta(AssessmentBaseForm.Meta):
        model = Assessment
        fields = ['subject', 'lesson', 'type', 'start_time', 'duration', 'description']


class AssessmentUpdateForm(AssessmentBaseForm):
    class Meta(AssessmentBaseForm.Meta):
        model = Assessment
        fields = ['lesson', 'type', 'start_time', 'duration', 'description']