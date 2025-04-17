from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from utils.constants import MAX_TIMEFRAME, RECENT_PAST_TIMEFRAME
from utils.filters import generate_select_options, apply_timeframe_filter_if_valid, apply_sorting
from utils.mixins import ModelNameMixin, DerivedFieldsMixin, CancelLinkMixin
from .models import Homework
from .forms import HomeworkCreateForm, HomeworkUpdateForm

from django.utils.timezone import now

from lesson.models import Lesson


VALID_FILTERS = {
    'subject': {
        'type': 'select',
        'label': 'Subject',
   #     'options': generate_select_options(Subject, fields=('id', 'name'), order_by='name')
    },
    'valid_timeframe': ['today', 'tomorrow', 'next3', 'this_week', 'next_week', 'this_month', 'next_month'],
    'completion': ['0', '25', '50', '75', '100'],
    'sort_by': { 
        'start_time': 'derived_start_time', '-start_time': '-derived_start_time',
        'due_at': 'derived_due_at', '-due_at': '-derived_due_at',
        'completion': 'completion_percent', '-completion': '-completion_percent',
        'created_at': 'created_at', '-created_at': '-created_at'
    },
}

CANCEL_LINK = reverse_lazy('homework_list')


class HomeworkListView(DerivedFieldsMixin, ListView):
    model = Homework
    context_object_name = 'user_homework'

    def get_queryset(self):
        '''
        Return homework of the user sending requests
        '''
        # user = self.request.user
        # queryset = Homework.objects.filter(derived_subject__user=user)

        queryset = super().get_queryset()

        if subject_filter := self.request.GET.get('subject'): # name := expr, expr is calculated at then assigned
            queryset = queryset.filter(derived_subject_id=subject_filter)

        if lesson_given_filter := self.request.GET.get('lesson_given'):
            queryset = queryset.filter(lesson_given=lesson_given_filter)

        if lesson_due_filter := self.request.GET.get('lesson_due'):
            queryset = queryset.filter(lesson_due=lesson_due_filter)

        if lesson_filter := self.request.GET.get('lesson'):
            queryset = queryset.filter(
                Q(lesson_given=lesson_filter) | Q(lesson_due=lesson_filter)
            )

        if completion_filter := self.request.GET.get('completion'):
            if completion_filter in VALID_FILTERS['completion']:
                queryset = queryset.filter(completion_percent=completion_filter)
        else:
            if min_completion_filter := self.request.GET.get('min_completion'):
                queryset = queryset.filter(completion_percent__gte=min_completion_filter)
            if max_completion_filter := self.request.GET.get('max_completion'):
                queryset = queryset.filter(completion_percent__lte=max_completion_filter)

        if start_time_filter := self.request.GET.get('start_time'):
            if start_time_filter in VALID_FILTERS['valid_timeframe']:
                queryset = filter_by_timeframe(
                    queryset,
                    filter_param=start_time_filter,
                    date_field='derived_start_time'
                )
                

        if due_at_filter := self.request.GET.get('due_at'):
            if due_at_filter == 'overdue':
                queryset = queryset.filter(due_at__lt=now())
            elif due_at_filter in VALID_FILTERS['valid_timeframe']:
                queryset = filter_by_timeframe(
                    queryset,
                    filter_param=due_at_filter,
                    date_field='derived_due_at'
                )


        default_sort_param = 'derived_start_time'
        sort_param = self.request.GET.get('sort_by')
        queryset = queryset.order_by(VALID_FILTERS['sort_by'].get(sort_param, default_sort_param))

        return queryset
    

class HomeworkDetailView(DerivedFieldsMixin, ModelNameMixin, DetailView):
    model = Homework


class HomeworkCreateView(CancelLinkMixin, DerivedFieldsMixin, ModelNameMixin, 
                         CreateView):
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
    

class HomeworkUpdateView(CancelLinkMixin, DerivedFieldsMixin, ModelNameMixin, 
                         UpdateView):
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


class HomeworkDeleteView(CancelLinkMixin, ModelNameMixin, 
                         DeleteView):
    model = Homework
    success_message = 'Assessment deleted successfully!'
    success_url = reverse_lazy('homework_list')