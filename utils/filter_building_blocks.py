from subject.models import Subject
from lesson.models import Lesson

from utils.constants import VALID_TIMEFRAME_OPTIONS, DEFAULT_SORTING_OPTIONS
from utils.query_filters import generate_select_options

'''
Returns context of common filters, that must be used as value in key-value pairs in <app>/filters.py
'''

def subject_filter(user):
    return {
        'type': 'select',
        'label': 'Subject',
        'options': generate_select_options(
            model=Subject,
            filters={'user__id': user.id},
            label_accessor='name',
            order_by='name'
        ),
    }

def lesson_filter(user, label):
    return {
        'type': 'select',
        'label': label,
        'options': generate_select_options(
            queryset=Lesson.objects.with_derived_fields(),
            filters={'derived_user_id': user.id},
            order_by='start_time',
        ),
    }

def timeframe_filter(label):
    return {
        'type': 'select',
        'label': label,
        'options': VALID_TIMEFRAME_OPTIONS
    }

def sort_by(default, options):
    return {
        'sort_by': {
            'type': 'select',
            'label': 'Sort By',
            'default': default,
            'options': [
                *options,
                *DEFAULT_SORTING_OPTIONS,
            ]
        }
    }