from django.views.generic import ListView, DetailView
from utils.filters import filter_by_timeframe
from .models import Lesson


VALID_FILTERS = {
    'start_time': ['today', 'tomorrow', 'next3', 'this_week', 'next_week', 'this_month', 'next_month'],
    'sort_by': ['start_time', '-start_time', 'created_at', '-created_at'],
}


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


class LessonDetailView(DetailView):
    model = Lesson