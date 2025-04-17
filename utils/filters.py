from django.utils.timezone import now, localtime
from datetime import timedelta


def apply_sorting(get_request, queryset, valid_filters):
    '''
    Sorts the provided queryset by parameters, provided in valid filters.
    Either recieves correct param from GET request, or uses default one.
    '''
    sort_param = get_request.get('sort_by')
    if sort_param:
        valid_sort_options = [option[0] for option in valid_filters['sort_by']['options']]
        if sort_param in valid_sort_options:
            queryset = queryset.order_by(sort_param)
        else:
            queryset = queryset.order_by(valid_filters['sort_by']['default'])
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


def apply_timeframe_filter_if_valid(get_request, queryset, param_name, valid_filters):
    '''
    Applies timeframe filtering to the queryset
    if the given param_name is in valid_filters.

    Assumes that the model field name matches the param_name.
    '''
    if filter_value := get_request.get(param_name):
        valid_timeframe_options = [option[0] for option in valid_filters[param_name]['options']]
        if filter_value in valid_timeframe_options:
            queryset = filter_by_timeframe(queryset, filter_value, param_name)
    return queryset


def generate_select_options(model, queryset=None, fields=('id', 'name'), order_by='-created_at'):
    '''
    Generate a list of (value, label) tuples for select dropdowns,
    based on the given model, fields, and optional queryset.
    '''
    if queryset == None:
        queryset = model.objects.all().order_by(order_by)
    return list(queryset.values_list(*fields))