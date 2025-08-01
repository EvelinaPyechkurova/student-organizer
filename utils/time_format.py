from django.utils.timezone import localtime

from utils.accessors import get_time_display_format

def format_time(dt, time_display_format):
    '''
    
    '''

    if time_display_format == '24':
        return localtime(dt).strftime('%A, %b %d, %Y at %H:%M')
    elif time_display_format == '12':
        return localtime(dt).strftime('%A, %b %d, %Y at %I:%M %p')
    else:
        raise ValueError(f'Unknown time display format: {time_display_format}')
    