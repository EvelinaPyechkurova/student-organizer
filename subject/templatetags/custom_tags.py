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