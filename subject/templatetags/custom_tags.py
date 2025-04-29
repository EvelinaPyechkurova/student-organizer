from django import template

register = template.Library()

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
    Parses timedelta object more user-friendly format
    with hours and minutes separated
    '''
    total_minutes = int(timedelta.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    user_friendly = []

    if hours:
        user_friendly.append(f'{hours} hour{"s" if hours != 1 else ""}')
    if minutes:
        user_friendly.append(f'{minutes} minute{"s" if minutes != 1 else ""}')

    return ', '.join(user_friendly) 
