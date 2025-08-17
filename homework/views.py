from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.timezone import now

from utils.constants import MAX_TIMEFRAME, RECENT_PAST_TIMEFRAME
from utils.mixins import (
    CancelLinkMixin, ModelNameMixin,
    OwnershipRequiredMixin, DerivedFieldsMixin
)
from utils.query_filters import apply_timeframe_filter_if_valid, apply_sorting
from utils.sidebar_context import (
    SidebarSectionsMixin, SidebarStateMixin,
    section
)

from subject.models import Subject
from lesson.models import Lesson

from .forms import HomeworkCreateForm, HomeworkUpdateForm
from .models import Homework

from .filter_config import build_homework_filters
from .sort_config import build_homework_sorting

CANCEL_LINK = reverse_lazy('homework_list')


class HomeworkListView(LoginRequiredMixin, SidebarStateMixin,
                       SidebarSectionsMixin, DerivedFieldsMixin,
                       ListView):
    model = Homework
    context_object_name = 'user_homework'
    paginate_by = 10

    def build_sidebar_sections(self):
        return [
            section(heading='Filter By', configs=build_homework_filters(user=self.request.GET.get('user'))),
            section(heading='Sort By', configs=build_homework_sorting())
        ]

    def get_queryset(self):
        '''
        Return homework of the user sending requests
        '''
        queryset = super().get_queryset().filter(derived_user_id=self.request.user.id)
        get_request = self.request.GET
        filter_config = build_homework_filters(user=self.request.GET.get('user'))
        sort_config = build_homework_sorting()

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
            valid_completion_percents = [option[0] for option in filter_config['completion']['options']]
            if completion_filter in valid_completion_percents:
                queryset = queryset.filter(completion_percent=completion_filter)
        else:
            if min_completion_filter := get_request.get('min_completion'):
                queryset = queryset.filter(completion_percent__gte=min_completion_filter)
            if max_completion_filter := get_request.get('max_completion'):
                queryset = queryset.filter(completion_percent__lte=max_completion_filter)

        for param_name, model_field_name in [('start_time', 'derived_start_time'), ('due_at', 'derived_due_at')]:
            queryset = apply_timeframe_filter_if_valid(get_request, queryset, param_name, filter_config, model_field_name)

        queryset = apply_sorting(get_request, queryset, sort_config)

        return queryset
    

class HomeworkDetailView(LoginRequiredMixin, DerivedFieldsMixin, OwnershipRequiredMixin, 
                         ModelNameMixin, DetailView):
    model = Homework
    owner_field = 'derived_user_id'


class HomeworkCreateView(LoginRequiredMixin, CancelLinkMixin, DerivedFieldsMixin,
                         ModelNameMixin, CreateView):
    model = Homework
    form_class = HomeworkCreateForm
    owner_field = 'derived_user_id'
    template_name_suffix = '_form_create'
    success_message = 'Homework created successfully!'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
       
        now_time = now()
        form.fields['subject'].queryset = Subject.objects.filter(
            user=self.request.user.id
        )

        form.fields['lesson_given'].queryset = Lesson.objects.filter(
            Q(subject__user=self.request.user) &
            Q(start_time__gte=now_time - RECENT_PAST_TIMEFRAME) &
            Q(start_time__lte=now_time)
        )

        form.fields['lesson_due'].queryset = Lesson.objects.filter(
            Q(subject__user=self.request.user) &
            Q(start_time__gte=now_time - RECENT_PAST_TIMEFRAME) &
            Q(start_time__lte=now_time + MAX_TIMEFRAME)
        )

        return form

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
    

class HomeworkUpdateView(LoginRequiredMixin, OwnershipRequiredMixin, CancelLinkMixin,
                         DerivedFieldsMixin, ModelNameMixin, UpdateView):
    model = Homework
    form_class = HomeworkUpdateForm
    owner_field = 'derived_user_id'
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


class HomeworkDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, CancelLinkMixin,
                         DerivedFieldsMixin, ModelNameMixin, DeleteView):
    model = Homework
    owner_field = 'derived_user_id'
    success_message = 'Assessment deleted successfully!'
    success_url = reverse_lazy('homework_list')