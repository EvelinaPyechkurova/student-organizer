from django.utils.timezone import localtime

def format_time(date_time):
    return localtime(date_time).strftime('%A, %b %d, %Y at %H:%M')