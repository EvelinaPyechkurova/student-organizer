from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from utils.filters import filter_by_timeframe
from .models import Homework
from .forms import HomeworkForm

from django.utils.timezone import now

from homework.models import Homework


VALID_FILTERS = {
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


class HomeworkListView(ListView):
    model = Homework
    context_object_name = 'user_homework'

    def get_queryset(self):
        '''
        Return homework of the user sending requests
        '''
        # user = self.request.user
        # queryset = Homework.objects.filter(derived_subject__user=user)

        queryset = Homework.objects.with_derived_fields()

        if subject_filter := self.request.GET.get('subject'):
            queryset = queryset.filter(derived_subject_id=subject_filter)

        if lesson_given_filter := self.request.GET.get('lesson_given'):
            queryset = queryset.filter(lesson_given=lesson_given_filter)

        if lesson_due_filter := self.request.GET.get('lesson_due'):
            queryset = queryset.filter(lesson_due=lesson_due_filter)

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
    

class HomeworkDetailView(DetailView):
    model = Homework

    def get_queryset(self):
        return Homework.objects.with_derived_fields()


class HomeworkCreateView(CreateView):
    model = Homework
    form_class = HomeworkForm

    # def get_initial(self):
    #     initial = super().get_initial()
    #     lesson_given_id = self.request.GET.get('lesson_given')
    #     lesson_due_id = self.request.GET.get('lesson_due')
    #     subject_id = self.request.GET.get('subject')

    #     if lesson_given_id:
    #         try:
    #             pass
    #         except 
    #     elif lesson_due_id:
    #         pass
    #     elif subject_id:
    #         initial['subject'] = subject_id

        # return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_link'] = CANCEL_LINK
        return context
        
    def get_success_url(self):
        return reverse_lazy('homework_detail', kwargs = {'pk': self.object.pk})
    


class HomeworkUpdateView(UpdateView):
    model = Homework


class HomeworkDeleteView(DeleteView):
    model = Homework