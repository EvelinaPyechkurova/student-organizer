from datetime import timedelta
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from utils.filters import filter_by_timeframe
from utils.duration import parse_duration
from utils.mixins import ModelNameMixin
from .models import Assessment
from .forms import AssessmentForm

from lesson.models import Lesson


VALID_FILTERS = {
    'start_time': ['today', 'tomorrow', 'next3', 'this_week', 'next_week', 'this_month', 'next_month'],
    'duration': [timedelta(minutes=15), timedelta(minutes=30), timedelta(minutes=45),
                 timedelta(minutes=60), timedelta(minutes=90), timedelta(minutes=120)],
    'sort_by': {
        'start_time': 'derived_start_time', '-start_time': '-derived_start_time', 
        'created_at': 'created_at', '-created_at': '-created_at'
    },
}

CANCEL_LINK = reverse_lazy('assessment_list')


class AssessmentListView(ListView):
    model = Assessment
    context_object_name = 'user_assessments'
    paginate_by = 20

    def get_queryset(self):
        '''
        Return assessments of the user sending requests
        '''
        # user = self.request.user
        # return Assessment.objects.filter(derived_subject__user=user)

        queryset = Assessment.objects.with_derived_fields()

        if subject_filter := self.request.GET.get('subject'):
            queryset = queryset.filter(derived_subject_id=subject_filter)
        
        if lesson_filter := self.request.GET.get('lesson'):
            queryset = queryset.filter(lesson=lesson_filter)

        if type_filter := self.request.GET.get('type'):
            queryset = queryset.filter(type__iexact=type_filter)

        if duration_filter := parse_duration(self.request.GET.get('duration')):
            if duration_filter in VALID_FILTERS['duration']:
                queryset = queryset.filter(duration=duration_filter)
        else:
            if min_duration_filter := parse_duration(self.request.GET.get('min_duration')):
                queryset = queryset.filter(duration__gte=min_duration_filter)

            if max_duration_filter := parse_duration(self.request.GET.get('max_duration')):
                queryset = queryset.filter(duration__lte=max_duration_filter)

        if start_time_filter := self.request.GET.get('start_time'):
            if start_time_filter in VALID_FILTERS['start_time']:
                queryset = filter_by_timeframe(
                    queryset,
                    filter_param=start_time_filter,
                    date_field='derived_start_time'
                )

        default_sort_param = 'derived_start_time'
        sort_param = self.request.GET.get('sort_by')
        queryset = queryset.order_by(VALID_FILTERS['sort_by'].get(sort_param, default_sort_param))

        return queryset


class AssessmentDetailView(ModelNameMixin, DetailView):
    model = Assessment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        return context

    def get_queryset(self):
        return Assessment.objects.with_derived_fields()
    

class AssessmentCreateView(CreateView):
    model = Assessment
    form_class = AssessmentForm

    def get_initial(self):
        initial = super().get_initial()
        lesson_id = self.request.GET.get('lesson')
        subject_id = self.request.GET.get('subject')

        if lesson_id:
            try:
                lesson = Lesson.objects.get(pk=lesson_id)
                initial.update({
                    'subject': lesson.subject,
                    'lesson': lesson_id,
                    'start_time': lesson.start_time,
                    'duration': lesson.duration,
                })
            except Lesson.DoesNotExist:
                pass
            
        elif subject_id:
            initial['subject'] = subject_id

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_link'] = CANCEL_LINK
        return context
    
    def get_success_url(self):
        return reverse_lazy('assessment_detail', kwargs = {'pk': self.object.pk})


class AssessmentUpdateView(UpdateView):
    model = Assessment


class AssessmentDeleteView(DeleteView):
    model = Assessment