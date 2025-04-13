from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.timezone import now
from utils.filters import filter_by_timeframe
from utils.mixins import ModelNameMixin
from .models import Lesson
from .forms import LessonForm

from utils.constants import MAX_TIMEFRAME


VALID_FILTERS = {
    'start_time': ['today', 'tomorrow', 'next3', 'this_week', 'next_week', 'this_month', 'next_month'],
    'sort_by': ['start_time', '-start_time', 'created_at', '-created_at'],
}

CANCEL_LINK = reverse_lazy('lesson_list')


class LessonListView(ListView):
    model = Lesson
    context_object_name = 'user_lessons'
    paginate_by = 20

    def get_queryset(self):
        '''
        Return lessons of the user sending request
        filtered and sorted if provided in the query params.
        '''
        # queryset = Lesson.objects.filter(subject__user=self.request.user)
        queryset = Lesson.objects.all()

        if subject_filter := self.request.GET.get('subject'):
            queryset = queryset.filter(subject=subject_filter)

        if type_filter := self.request.GET.get('type'):
            queryset = queryset.filter(type__iexact=type_filter)

        start_time_filter = self.request.GET.get('start_time')
        if start_time_filter := self.request.GET.get('start_time'):
            if start_time_filter in VALID_FILTERS['start_time']:
                queryset = filter_by_timeframe(queryset, filter_param=start_time_filter)

        default_sort_param = 'start_time'
        sort_param = self.request.GET.get('sort_by')
        queryset = queryset.order_by(sort_param if sort_param in VALID_FILTERS['sort_by'] else default_sort_param)

        return queryset


class LessonDetailView(ModelNameMixin, DetailView):
    model = Lesson
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now_time = now()
        start_time = context['lesson'].start_time

        context['can_add_assessment'] = start_time > now_time
        context['can_add_lesson_given'] = start_time < now_time and start_time > now_time - MAX_TIMEFRAME
        context['can_add_lesson_due'] = start_time < now_time and start_time > now_time - MAX_TIMEFRAME
        print(context)
        return context


class LessonCreateView(CreateView):
    model = Lesson
    form_class = LessonForm

    def get_initial(self):
        initial = super().get_initial()
        subject_id = self.request.GET.get('subject')
        if subject_id:
            initial['subject'] = subject_id
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_link'] = CANCEL_LINK
        return context
    
    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs = {'pk': self.object.pk})
    

class LessonUpdateView(UpdateView):
    model = Lesson
 

class LessonDeleteView(ModelNameMixin, DeleteView):
    model = Lesson
    success_message = 'Lesson deleted successfully!'
    success_url = reverse_lazy('lesson_list')

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