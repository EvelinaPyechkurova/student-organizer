from utils.constants import VALID_TIMEFRAME_OPTIONS, DEFAULT_SORTING_OPTIONS
from utils.filters import generate_select_options

'''
Returns context of common filters, that must be used as value in key-value pairs in <app>/filters.py
'''

def subject_filter(SubjectModel):
    return {
        'type': 'select',
        'label': 'Subject',
        'options': generate_select_options(SubjectModel, order_by='name'),
    }

def timeframe_filter(label):
    return {
        'type': 'select',
        'label': label,
        'options': VALID_TIMEFRAME_OPTIONS
    }

def sort_by(default, options):
    return {
        'type': 'select',
        'label': 'Sort By',
        'default': default,
        'options': [
            *DEFAULT_SORTING_OPTIONS,
            *options
        ]
    }