from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Assessment

class AssessmentListView(ListView):
    model = Assessment
    context_object_name = 'user_assessments'

    # def get_queryset(self):
    #     '''
    #     Return assessments of the user sending requests
    #     '''
    #     user = self.request.user
    #     return Assessment.objects.filter(
    #         Q(subject__user=user) | Q(lesson__subject__user=user)
    #     )

        
class AssessmentDetailView(DetailView):
    model = Assessment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment = self.get_object()
        context['source'] = assessment.lesson or assessment
        return context