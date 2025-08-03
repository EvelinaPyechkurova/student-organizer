from django.utils.timezone import localtime

def format_time(dt, time_display_format):
    '''
    Formats a datetime object using either 12-hour or 24-hour clock format
    '''

    if time_display_format == '24':
        return localtime(dt).strftime('%A, %b %d, %Y at %H:%M')
    elif time_display_format == '12':
        return localtime(dt).strftime('%A, %b %d, %Y at %I:%M %p')
    else:
        raise ValueError(f'Unknown time display format: {time_display_format}')
    