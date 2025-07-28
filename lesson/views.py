from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from utils.constants import MAX_TIMEFRAME, RECENT_PAST_TIMEFRAME, VALID_TIMEFRAME_OPTIONS
from utils.filters import apply_sorting, apply_timeframe_filter_if_valid, generate_select_options
from utils.mixins import (
    CancelLinkMixin, ModelNameMixin,
    FilterConfigMixin, FilterStateMixin,
    OwnershipRequiredMixin, DerivedFieldsMixin
)

from subject.models import Subject
from .models import Lesson
from .forms import LessonCreateForm, LessonUpdateForm

from utils.userprofile import get_user
from notifications.scheduler import send_notifications


VALID_FILTERS = {
    'subject': {
        'type': 'select',
        'label': 'Subject',
        # 'options': generate_select_options(Subject, order_by='name'),
        'options': Lesson.Type.choices,
    },
    'type': {
        'type': 'select',
        'label': 'Lesson Type',
        'options': Lesson.Type.choices,
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
            ('start_time', 'Start Time ⭡'),
            ('-start_time', 'Start Time ⭣'),
            ('created_at', 'Created At ⭡'),
            ('-created_at', 'Created At ⭣')
        ]
    }
}

CANCEL_LINK = reverse_lazy('lesson_list')


class LessonListView(LoginRequiredMixin, FilterStateMixin, FilterConfigMixin, ListView):
    model = Lesson
    context_object_name = 'user_lessons'
    paginate_by = 8

    def get_queryset(self):
        '''
        Return lessons of the user sending request
        filtered and sorted if provided in the query params.
        '''
        queryset = Lesson.objects.filter(subject__user=self.request.user)
        get_request = self.request.GET

        if subject_filter := get_request.get('subject'):
            queryset = queryset.filter(subject=subject_filter)

        if type_filter := get_request.get('type'):
            queryset = queryset.filter(type__iexact=type_filter)

        queryset = apply_timeframe_filter_if_valid(get_request, queryset, 'start_time', VALID_FILTERS)

        queryset = apply_sorting(get_request, queryset, VALID_FILTERS)

        return queryset


class LessonDetailView(LoginRequiredMixin, DerivedFieldsMixin, OwnershipRequiredMixin,
                       ModelNameMixin, DetailView):
    model = Lesson
    owner_field = 'derived_user_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now_time = now()
        start_time = context['lesson'].start_time

        send_notifications()

        context['can_add_assessment'] = start_time > now_time
        context['can_add_lesson_given'] = start_time < now_time and start_time > now_time - MAX_TIMEFRAME
        context['can_add_lesson_due'] = start_time < now_time + MAX_TIMEFRAME and start_time > now_time - RECENT_PAST_TIMEFRAME
        
        return context


class LessonCreateView(LoginRequiredMixin, CancelLinkMixin, ModelNameMixin, CreateView):
    model = Lesson
    form_class = LessonCreateForm
    success_message = 'Lesson created successfully!'
    template_name_suffix = '_form_create'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['subject'].queryset = Subject.objects.filter(
            user=self.request.user.id
        )
        return form
    
    def get_initial(self):
        initial = super().get_initial()
        subject_id = self.request.GET.get('subject')
        if subject_id:
            initial['subject'] = subject_id
        return initial
    
    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs = {'pk': self.object.pk})
    

class LessonUpdateView(LoginRequiredMixin, DerivedFieldsMixin, OwnershipRequiredMixin,
                       CancelLinkMixin, ModelNameMixin, UpdateView):
    model = Lesson
    form_class = LessonUpdateForm
    success_message = 'Lesson updated successfully!'
    template_name_suffix = '_form_update'
    owner_field = 'derived_user_id'

    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs = {'pk': self.object.pk})
 

class LessonDeleteView(LoginRequiredMixin, DerivedFieldsMixin, OwnershipRequiredMixin,
                       CancelLinkMixin, ModelNameMixin, DeleteView):
    model = Lesson
    success_message = 'Lesson deleted successfully!'
    success_url = reverse_lazy('lesson_list')
    owner_field = 'derived_user_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object

        assessment_count = lesson.assessment_set.count()
        homework_count = lesson.given_homework.count() + lesson.due_homework.count()

        if related_objects := {
            key: value for (key, value) in [
                ('assessment', assessment_count),
                ('homework', homework_count),
            ]
            if value
        }:
            context['related_objects'] = related_objects

        return context