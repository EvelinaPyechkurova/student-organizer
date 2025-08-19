from django.utils.timezone import now, localtime
from datetime import timedelta


def apply_sorting(GET, queryset, sort_options):
    '''
    Sorts the provided queryset by parameters, provided in sort_config.
    Either recieves valid param from GET request, or uses a default one.
    Excepts that sort_options has the following structure:
    {type: ..., label: ..., default: some_value, options: [(value, value, <value>), ...]}
    '''
    sort_param = GET.get('sort_by')
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


def filter_by_date_range(queryset, filter_param, date=None, date_field='start_time'):
    '''
    Filters a queryset by a date range (like 'day', 'month')
    relative to a reference date. The reference date defaults to today.
    Assumes queryset uses 'start_time' or specified 'date_field' for filtering.
    '''

    DAYS_IN_WEEK = 7
    DAYS_IN_MONTH = 32

    if date is None:
        date = localtime(now()).date()

    start_of_week = date - timedelta(days=date.weekday())
    start_of_month = date.replace(day=1)
    next_month = (start_of_month + timedelta(days=DAYS_IN_MONTH)).replace(day=1)

    time_filters = {
        'day': lambda: (date, date),
        'next_day': lambda: (date + timedelta(days=1), date + timedelta(days=1)),
        'next_3_days' : lambda: (date, date + timedelta(days=3)),
        'week': lambda: (
            start_of_week, 
            start_of_week + timedelta(days=6)
        ),
        'next_week' : lambda: (
            start_of_week + timedelta(days=DAYS_IN_WEEK), 
            start_of_week + timedelta(days=DAYS_IN_WEEK * 2 - 1)
        ),
        'month' : lambda: (
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


def apply_date_range_filter_if_valid(GET, queryset, param_name, valid_filters, model_field_name=None):
    '''
    Applies timeframe filtering to the queryset
    if the given param_name is in valid_filters.

    Assumes that the model field name matches the param_name.
    '''
    if filter_value := GET.get(param_name):
        if model_field_name is None:
            model_field_name = param_name
        valid_timeframe_options = [option[0] for option in valid_filters[param_name]['options']]
        if filter_value in valid_timeframe_options:
            queryset = filter_by_date_range(
                queryset,
                filter_param=filter_value,
                date_field=model_field_name
            )
    return queryset


def generate_select_options(
        model=None,
        queryset=None,
        filters={},
        q_objects=[],
        value_field='id',
        label_accessor=str,
        order_by='-created_at',
        limit=None,
        distinct=False):
    '''
    Generates a list of (value, label) tuples for select fields.
    label_accessor can be a field name (str) or a callable (function).
    '''

    if queryset is None:
        if model is None:
            raise ValueError('Provide either "queryset" or "model".')
        queryset = model.objects.all()

    if filters:
        queryset = queryset.filter(**filters)
    if q_objects:
        queryset = queryset.filter(*q_objects)

    label_is_field = isinstance(label_accessor, str)
    if label_is_field:
        fields = {value_field, label_accessor}
        queryset = queryset.only(*fields)

    if order_by:
        queryset = queryset.order_by(*(order_by if isinstance(order_by, (list, tuple)) else [order_by]))

    if distinct:
        queryset = queryset.distinct()

    if limit is not None:
        queryset = queryset[:limit]


    options = []
    for obj in queryset:
        value = getattr(obj, value_field)
        label = label_accessor(obj) if callable(label_accessor) else getattr(obj, label_accessor)
        options.append((value, label))

    return options