from django.utils.timezone import now, localtime
from datetime import timedelta


def apply_sorting(get_request, queryset, sort_options):
    '''
    Sorts the provided queryset by parameters, provided in sort_config.
    Either recieves valid param from GET request, or uses a default one.
    Excepts that sort_options has the following structure:
    {type: ..., label: ..., default: some_value, options: [(value, value, <value>), ...]}
    '''
    sort_param = get_request.get('sort_by')
    if sort_param:
        valid_sort_options = [option[0] for option in sort_options['sort_by']['options']]
        if sort_param in valid_sort_options:
            for option in sort_options['sort_by']['options']:
                if option[0] == sort_param:
                    sort_field = option[2] if len(option) > 2 else option[0]
                    queryset = queryset.order_by(sort_field)
                    break
        else:
            queryset = queryset.order_by(sort_options['sort_by']['default'])
    return queryset


def filter_by_day(queryset, date, date_field='start_time'):
    return queryset.filter(**{f"{date_field}__date": date})


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


def apply_timeframe_filter_if_valid(get_request, queryset, param_name, valid_filters, model_field_name=None):
    '''
    Applies timeframe filtering to the queryset
    if the given param_name is in valid_filters.

    Assumes that the model field name matches the param_name.
    '''
    if filter_value := get_request.get(param_name):
        if model_field_name is None:
            model_field_name = param_name
        valid_timeframe_options = [option[0] for option in valid_filters[param_name]['options']]
        if filter_value in valid_timeframe_options:
            queryset = filter_by_timeframe(queryset, filter_value, model_field_name)
    return queryset


def generate_select_options(model, queryset=None, value_field='id', label_func=str, order_by='-created_at'):
    '''
    Generates a list of (value, label) tuples for select fields.
    label_func can be a field name (str) or a callable (function).
    '''
    if queryset == None:
        queryset = model.objects.all().order_by(order_by)

    options = []
    for obj in queryset:
        value = getattr(obj, value_field)
        label = label_func(obj) if callable(label_func) else getattr(obj, label_func)
        options.append((value, label))

    return options