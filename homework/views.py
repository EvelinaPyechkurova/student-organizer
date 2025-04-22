from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.timezone import now

from utils.constants import MAX_TIMEFRAME, RECENT_PAST_TIMEFRAME, VALID_TIMEFRAME_OPTIONS
from utils.filters import generate_select_options, apply_timeframe_filter_if_valid, apply_sorting
from utils.mixins import ModelNameMixin, DerivedFieldsMixin, CancelLinkMixin, FilterConfigMixin, FilterStateMixin

from subject.models import Subject
from lesson.models import Lesson
from .forms import HomeworkCreateForm, HomeworkUpdateForm
from .models import Homework


VALID_FILTERS = {
    'subject': {
        'type': 'select',
        'label': 'Subject',
        'options': generate_select_options(Subject, order_by='name'),
    },
    'lesson_given': {
        'type': 'select',
        'label': 'Lesson When Given',
        'options': generate_select_options(Lesson, order_by='start_time'),
    },
    'lesson_due': {
        'type': 'select',
        'label': 'Lesson Due For',
        'options': generate_select_options(Lesson, order_by='start_time'),
    },
    'lesson': {
        'type': 'select',
        'label': 'Lesson (Given or Due)',
        'options': generate_select_options(Lesson, order_by='start_time'),
    },
    'completion': {
        'type': 'select',
        'label': 'Completion Percent',
        'options': [
            ('0', '0% (Not Started)'), 
            ('25', '25% (Started)'), 
            ('50', '50% (Halfway Done)'),
            ('75', '75% (Almost Finished)'), 
            ('100', '100% (Completed)'),
        ],
    },
    'min_completion': {
        'type': 'number',
        'label': 'Minimum Completion Percent',
        'attributes': [
            ('min', '0'),
            ('max', '100'),
            ('step', '1'),
            ('placeholder', 'Enter minimum %'),
        ],
    },
    'max_completion': {
        'type': 'number',
        'label': 'Maximum Completion Percent',
        'attributes': [
            ('min', '0'),
            ('max', '100'),
            ('step', '1'),
            ('placeholder', 'Enter maximum %'),
        ],
    },
    'start_time': {
        'type': 'select',
        'label': 'Start Time',
        'options': VALID_TIMEFRAME_OPTIONS,
    },
    'due_at': {
        'type': 'select',
        'label': 'Due At',
        'options': VALID_TIMEFRAME_OPTIONS
    },
    'sort_by': {
        'type': 'select',
        'label': 'Sort By',
        'default': 'start_time',
        'options': [
            ('start_time', 'Start Time ⭡', 'derived_start_time'),
            ('-start_time', 'Start Time ⭣', '-derived_start_time'),
            ('completion', 'Completion Percent ⭡', 'completion_percent'),
            ('-completion', 'Completion Percent ⭣', '-completion_percent'),
            ('created_at', 'Created At ⭡'),
            ('-created_at', 'Created At ⭣'),
        ]
    },
}

CANCEL_LINK = reverse_lazy('homework_list')


class HomeworkListView(LoginRequiredMixin, FilterStateMixin, FilterConfigMixin,
                       DerivedFieldsMixin, ListView):
    model = Homework
    context_object_name = 'user_homework'
    paginate_by = 10

    def get_queryset(self):
        '''
        Return homework of the user sending requests
        '''
        # queryset = super().get_queryset().filter(derived_subject__user=self.request.user)
        queryset = super().get_queryset()
        get_request = self.request.GET

        if subject_filter := get_request.get('subject'):
            queryset = queryset.filter(derived_subject_id=subject_filter)

        if lesson_given_filter := get_request.get('lesson_given'):
            queryset = queryset.filter(lesson_given=lesson_given_filter)

        if lesson_due_filter := get_request.get('lesson_due'):
            queryset = queryset.filter(lesson_due=lesson_due_filter)

        if lesson_filter := get_request.get('lesson'):
            queryset = queryset.filter(
                Q(lesson_given=lesson_filter) | Q(lesson_due=lesson_filter)
            )

        if completion_filter := get_request.get('completion'):
            valid_completion_percents = [option[0] for option in VALID_FILTERS['completion']['options']]
            if completion_filter in valid_completion_percents:
                queryset = queryset.filter(completion_percent=completion_filter)
        else:
            if min_completion_filter := get_request.get('min_completion'):
                queryset = queryset.filter(completion_percent__gte=min_completion_filter)
            if max_completion_filter := get_request.get('max_completion'):
                queryset = queryset.filter(completion_percent__lte=max_completion_filter)

        queryset = apply_timeframe_filter_if_valid(get_request, queryset, 'start_time', VALID_FILTERS, model_field_name='derived_start_time')

        queryset = apply_timeframe_filter_if_valid(get_request, queryset, 'due_at', VALID_FILTERS, model_field_name='derived_due_at')

        queryset = apply_sorting(get_request, queryset, VALID_FILTERS)

        return queryset
    

class HomeworkDetailView(LoginRequiredMixin, DerivedFieldsMixin, ModelNameMixin,
                         DetailView):
    model = Homework


class HomeworkCreateView(LoginRequiredMixin, CancelLinkMixin, DerivedFieldsMixin,
                         ModelNameMixin, CreateView):
    model = Homework
    form_class = HomeworkCreateForm
    template_name_suffix = '_form_create'
    success_message = 'Homework created successfully!'

    def get_initial(self):
        initial = super().get_initial()
        lesson_given_id = self.request.GET.get('lesson_given')
        lesson_due_id = self.request.GET.get('lesson_due')
        subject_id = self.request.GET.get('subject')

        if lesson_given_id:
            try:
                lesson_given = Lesson.objects.get(pk=lesson_given_id)
                initial.update({
                    'subject': lesson_given.subject,
                    'lesson_given': lesson_given_id,
                    'start_time': lesson_given.start_time,
                })
            except Lesson.DoesNotExist:
                pass
        elif lesson_due_id:
            try:
                lesson_due = Lesson.objects.get(pk=lesson_due_id)
                initial.update({
                    'subject': lesson_due.subject,
                    'lesson_due': lesson_due_id,
                    'due_at': lesson_due.start_time,
                })
            except Lesson.DoesNotExist:
                pass
        elif subject_id:
            initial['subject'] = subject_id

        return initial
        
    def get_success_url(self):
        return reverse_lazy('homework_detail', kwargs = {'pk': self.object.pk})
    

class HomeworkUpdateView(LoginRequiredMixin, CancelLinkMixin, DerivedFieldsMixin,
                         ModelNameMixin, UpdateView):
    model = Homework
    form_class = HomeworkUpdateForm
    template_name_suffix = '_form_update'
    success_message = 'Homework updated successfully!'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.derived_subject_id:
            now_time = now()
            form.fields['lesson_due'].queryset = Lesson.objects.filter(
                Q(subject=self.object.derived_subject_id) & (
                    Q(start_time__gte=max(
                        now_time - RECENT_PAST_TIMEFRAME,
                        self.object.derived_start_time
                    )) &
                    Q(start_time__lte=now_time + MAX_TIMEFRAME) |
                    Q(pk=self.object.lesson_due_id)
                )
            )
        return form


    def get_success_url(self):
        return reverse_lazy('homework_detail', kwargs = {'pk': self.object.pk})


class HomeworkDeleteView(LoginRequiredMixin, CancelLinkMixin, ModelNameMixin, 
                         DeleteView):
    model = Homework
    success_message = 'Assessment deleted successfully!'
    success_url = reverse_lazy('homework_list')