from django.views.generic import ListView, DetailView
from .models import Lesson

def filter_by_time_window(queryset, window):
    today = today = localtime(now()).date()
    pass

class LessonListView(ListView):
    model = Lesson
    context_object_name = 'user_lessons'




    def get_queryset(self):
        '''
        Return lessons of the user sending request
        filtered and sorted if provided in the query params.
        '''
        # queryset = Lesson.objects.filter(subject__user=self.request.user)
        queryset = Lesson.objects.all()

        subject_filter = self.request.GET.get('subject')
        if subject_filter:
            queryset = queryset.filter(subject=subject_filter)

        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type__iexact=type_filter)

        start_time_filter = self.request.GET.get('start_time')
        if start_time_filter in ['today', 'tomorrow', 'next3', 'this_week', 'next_week', 'this_month']:
            queryset = filter_by_time_window(queryset, window=start_time_filter)

        default_sort_param = 'start_time'
        sort_param = self.request.GET.get('sort_by')
        if sort_param and sort_param in ['start_time', '-start_time', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_param)
        else:
            queryset = queryset.order_by(default_sort_param)

        return queryset


class LessonDetailView(DetailView):
    model = Lesson