from django.utils.timezone import now, localtime
from datetime import timedelta


def apply_sorting(request, queryset, valid_filters):
    sort_param = request.get('sort-by')
    if sort_param:
        valid_sort_options = [option[0] for option in valid_filters['sort-by']['options']]
        if sort_param in valid_sort_options:
            queryset = queryset.order_by(sort_param)
        else:
            queryset = queryset.order_by(valid_filters['sort-by']['default'])
    return queryset


def filter_by_timeframe(queryset, filter_param, date_field='start_time'):
    '''
    Filters the provided queryset by timeframe conditions like 'today', 'this_week', etc.
    Assumes queryset uses 'start_time' or specified 'date_field' for filtering.
    '''

    DAYS_IN_WEEK = 7
    DAYS_IN_MONTH = 32

    today = localtime(now()).date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    next_month = (start_of_month + timedelta(days=DAYS_IN_MONTH)).replace(day=1)

    time_filters = {
        'today': lambda: (today, today),
        'tomorrow': lambda: (today + timedelta(days=1), today + timedelta(days=1)),
        'next3' : lambda: (today, today + timedelta(days=3)),
        'this_week' : lambda: (
            start_of_week, 
            start_of_week + timedelta(days=6)
        ),
        'next_week' : lambda: (
            start_of_week + timedelta(days=DAYS_IN_WEEK), 
            start_of_week + timedelta(days=DAYS_IN_WEEK * 2 - 1)
        ),
        'this_month' : lambda: (
            start_of_month, 
            (start_of_month + timedelta(days=DAYS_IN_MONTH)).replace(day=1) - timedelta(days=1)
        ),
        'next_month' : lambda: (
            next_month,
            (next_month + timedelta(days=DAYS_IN_MONTH)).replace(day=1) - timedelta(days=1)
        ),
    }

    start_date, end_date = time_filters[filter_param]()
    return queryset.filter(**{f'{date_field}__date__range': [start_date, end_date]})

