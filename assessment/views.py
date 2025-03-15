from django.views.generic import ListView, DetailView
from django.db.models import Q
from utils.filters import filter_by_timeframe
from .models import Assessment


VALID_FILTERS = {
    'start_time': ['today', 'tomorrow', 'next3', 'this_week', 'next_week', 'this_month', 'next_month'],
    'sort_by': {
        'start_time': 'derived_start_time', '-start_time': '-derived_start_time', 
        'created_at': 'created_at', '-created_at': '-created_at'
    },
}


class AssessmentListView(ListView):
    model = Assessment
    context_object_name = 'user_assessments'
    paginate_by = 20

    def get_queryset(self):
        '''
        Return assessments of the user sending requests
        '''
        # user = self.request.user
        # return Assessment.objects.filter(
        #     Q(subject__user=user) | Q(lesson__subject__user=user)
        # )

        queryset = Assessment.objects.with_derived_fields()

        if subject_filter := self.request.GET.get('subject'):
            queryset = queryset.filter(derived_subject=subject_filter)
        
        if lesson_filter := self.request.GET.get('lesson'):
            queryset = queryset.filter(lesson=lesson_filter)

        if type_filter := self.request.GET.get('type'):
            queryset = queryset.filter(type__iexact=type_filter)

        if min_duration_filter := self.request.GET.get('min_duration'):
            queryset = queryset.filter(duration__gte=min_duration_filter)

        if max_duration_filter := self.request.GET.get('max_duration'):
            queryset = queryset.filter(duration__lte=max_duration_filter)

        if start_time_filter := self.request.GET.get('start_time'):
            if start_time_filter in VALID_FILTERS['start_time']:
                queryset = filter_by_timeframe(
                    queryset,
                    filter_param=start_time_filter,
                    date_field='derived_start_time'
                )

        default_sort_param = 'derived_start_time'
        sort_param = self.request.GET.get('sort_by')
        queryset = queryset.order_by(VALID_FILTERS['sort_by'].get(sort_param, default_sort_param))

        return queryset

        
class AssessmentDetailView(DetailView):
    model = Assessment
