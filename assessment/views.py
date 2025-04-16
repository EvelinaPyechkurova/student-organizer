from datetime import timedelta
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.timezone import now
from utils.filters import filter_by_timeframe
from utils.duration import parse_duration
from utils.mixins import ModelNameMixin, DerivedFieldsMixin, CancelLinkMixin
from .models import Assessment
from .forms import AssessmentCreateForm, AssessmentUpdateForm

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


class AssessmentListView(DerivedFieldsMixin, ListView):
    model = Assessment
    context_object_name = 'user_assessments'
    paginate_by = 20

    def get_queryset(self):
        '''
        Return assessments of the user sending requests
        '''
        queryset = super().get_queryset()

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


class AssessmentDetailView(DerivedFieldsMixin, ModelNameMixin, DetailView):
    model = Assessment


class AssessmentCreateView(CancelLinkMixin, DerivedFieldsMixin, ModelNameMixin, 
                           CreateView):
    model = Assessment
    form_class = AssessmentCreateForm
    template_name_suffix = '_form_create'
    success_message = 'Assessment created successfully!'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['lesson'].queryset = Lesson.objects.filter(
            start_time__gte=now()
        )
        return form

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

    def get_success_url(self):
        return reverse_lazy('assessment_detail', kwargs = {'pk': self.object.pk})


class AssessmentUpdateView(CancelLinkMixin, DerivedFieldsMixin, ModelNameMixin, 
                           UpdateView):
    model = Assessment
    form_class = AssessmentUpdateForm
    template_name_suffix = '_form_update'
    success_message = 'Assessment updated successfully!'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['lesson'].queryset = Lesson.objects.filter(
            Q(subject=self.object.derived_subject_id) & (
                Q(pk=self.object.lesson_id) | Q(start_time__gte=now())
            )
        )
    
        return form

    def get_success_url(self):
        return reverse_lazy('assessment_detail', kwargs = {'pk': self.object.pk})


class AssessmentDeleteView(CancelLinkMixin, ModelNameMixin,
                           DeleteView):
    model = Assessment
    success_message = 'Assessment deleted successfully!'
    success_url = reverse_lazy('assessment_list')