from datetime import timedelta

from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from utils.constants import VALID_TIMEFRAME_OPTIONS
from utils.duration import parse_duration
from utils.filters import apply_sorting, apply_timeframe_filter_if_valid, generate_select_options
from utils.mixins import CancelLinkMixin, DerivedFieldsMixin, ModelNameMixin, FilterConfigMixin, FilterStateMixin

from subject.models import Subject
from lesson.models import Lesson
from .forms import AssessmentCreateForm, AssessmentUpdateForm
from .models import Assessment


VALID_FILTERS = {
    'subject': {
        'type': 'select',
        'label': 'Subject',
        'options': generate_select_options(Subject, order_by='name'),
    },
    'lesson': {
        'type': 'select',
        'label': 'Assessment Lesson',
        'options': generate_select_options(Lesson, order_by='start_time'),
    },
    'type': {
        'type': 'select',
        'label': 'Assessment Type',
        'options': Assessment.Type.choices
    },
    'duration': {
        'type': 'select',
        'label': 'Duration',
        'options': [
            timedelta(minutes=15), timedelta(minutes=30), timedelta(minutes=45),
            timedelta(minutes=60), timedelta(minutes=90), timedelta(minutes=120)
        ]
    },
    'min_duration': {
        'type': 'text',
        'label': 'Minimum Duration',
    },
    'max_duration': {
        'type': 'text',
        'label': 'Maximum Duration',
    },
    'start_time': {
        'type': 'select',
        'label': 'Start Time',
        'options': VALID_TIMEFRAME_OPTIONS,
    },
    'sort_by': {
        'type': 'select',
        'label': 'Sort By',
        'default': 'start_time',
        'options': [
            ('start_time', 'Start Time ⭡', 'derived_start_time'),
            ('-start_time', 'Start Time ⭣', '-derived_start_time'),
            ('created_at', 'Created At ⭡'),
            ('-created_at', 'Created At ⭣')
        ]
    }
}

CANCEL_LINK = reverse_lazy('assessment_list')


class AssessmentListView(FilterStateMixin, FilterConfigMixin, DerivedFieldsMixin, ListView):
    model = Assessment
    context_object_name = 'user_assessments'
    paginate_by = 20

    def get_queryset(self):
        '''
        Return assessments of the user sending requests
        '''
        queryset = super().get_queryset()
        get_request = self.request.GET

        if subject_filter := get_request.get('subject'):
            queryset = queryset.filter(derived_subject_id=subject_filter)
        
        if lesson_filter := get_request.get('lesson'):
            queryset = queryset.filter(lesson=lesson_filter)

        if type_filter := get_request.get('type'):
            queryset = queryset.filter(type__iexact=type_filter)

        if duration_filter := parse_duration(get_request.get('duration')):
            if duration_filter in VALID_FILTERS['duration']['options']:
                queryset = queryset.filter(duration=duration_filter)
        else:
            if min_duration_filter := parse_duration(get_request.get('min_duration')):
                queryset = queryset.filter(duration__gte=min_duration_filter)

            if max_duration_filter := parse_duration(get_request.get('max_duration')):
                queryset = queryset.filter(duration__lte=max_duration_filter)


        queryset = apply_timeframe_filter_if_valid(get_request, queryset, 'start_time', VALID_FILTERS)

        queryset = apply_sorting(get_request, queryset, VALID_FILTERS)

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