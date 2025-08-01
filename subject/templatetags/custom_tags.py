import math
from django import template

register = template.Library()

SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
MINUTES_IN_DAY = 1440

def pluralize(value, singular):
    '''
    Returns the singular/plural form of the time unit.
    '''
    return f'{value} {singular}{"s" if value != 1 else ""}'

@register.filter
def get_item(dictionary, key):
    '''
    Custom filter for extracting keys from dicts templates based on dynamic values.
    Created for enabling use of one generic template for all apps.
    Currently located in subject app, but can be loaded from anywhere in project.
    '''
    return dictionary.get(key, '')

@register.filter
def get_human_duration(timedelta):
    '''
    Converts a timedelta into a user-friendly format (e.g. "2 days, 3 hours, 5 minutes").
    Handles pluralization and ignores zero values.
    Rounds minutes UP, but leaves days/hours logic untouched.
    '''

    total_minutes = math.ceil(timedelta.total_seconds() / SECONDS_IN_MINUTE)

    days, minutes = divmod(total_minutes, MINUTES_IN_DAY)
    hours, minutes = divmod(minutes, MINUTES_IN_HOUR)

    parts = []
    if days:
        parts.append(f'{days} day{"s" if days != 1 else ""}')
    if hours:
        parts.append(f'{hours} hour{"s" if hours != 1 else ""}')
    if minutes:
        parts.append(f'{minutes} minute{"s" if minutes != 1 else ""}')

    return ', '.join(parts) 
