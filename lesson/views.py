from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from utils.constants import MAX_TIMEFRAME, RECENT_PAST_TIMEFRAME
from utils.mixins import (
    CancelLinkMixin, ModelNameMixin,
    OwnershipRequiredMixin, DerivedFieldsMixin
)
from utils.query_filters import apply_sorting, apply_timeframe_filter_if_valid
from utils.sidebar_context import (
    SidebarSectionsMixin, SidebarStateMixin,
    section
)

from subject.models import Subject
from .models import Lesson
from .forms import LessonCreateForm, LessonUpdateForm

from .filter_config import build_lesson_filters
from .sort_config import build_lesson_sorting

CANCEL_LINK = reverse_lazy('lesson_list')


class LessonListView(LoginRequiredMixin, SidebarStateMixin, 
                     SidebarSectionsMixin, ListView):
    model = Lesson
    context_object_name = 'user_lessons'
    paginate_by = 8

    def build_sidebar_sections(self):
        return [
            section(heading='Filter By', configs=build_lesson_filters(user=self.request.GET.get('user'))),
            section(heading='Sort By', configs=build_lesson_sorting())
        ]

    def get_queryset(self):
        '''
        Return lessons of the user sending request
        filtered and sorted if provided in the query params.
        '''
        queryset = Lesson.objects.filter(subject__user=self.request.user)
        get_request = self.request.GET
        filter_config = build_lesson_filters(user=self.request.GET.get('user'))
        sort_config = build_lesson_sorting()

        if subject_filter := get_request.get('subject'):
            queryset = queryset.filter(subject=subject_filter)

        if type_filter := get_request.get('type'):
            queryset = queryset.filter(type__iexact=type_filter)

        queryset = apply_timeframe_filter_if_valid(get_request, queryset, 'start_time', filter_config)

        queryset = apply_sorting(get_request, queryset, sort_config)

        return queryset


class LessonDetailView(LoginRequiredMixin, DerivedFieldsMixin, OwnershipRequiredMixin,
                       ModelNameMixin, DetailView):
    model = Lesson
    owner_field = 'derived_user_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now_time = now()
        start_time = context['lesson'].start_time

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