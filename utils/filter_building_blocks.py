from utils.constants import VALID_TIMEFRAME_OPTIONS, DEFAULT_SORTING_OPTIONS
from utils.query_filters import generate_select_options

'''
Returns context of common filters, that must be used as value in key-value pairs in <app>/filters.py
'''

def subject_filter(subject_model):
    return {
        'type': 'select',
        'label': 'Subject',
        'options': generate_select_options(subject_model, order_by='name'),
    }

def lesson_filter(lesson_model, label):
    return {
        'type': 'select',
        'label': label,
        'options': generate_select_options(lesson_model, order_by='start_time'),
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