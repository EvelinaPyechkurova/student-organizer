from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.constants import EVENT_TYPE_SPECIFIC_MESSAGES

def send_email():
    text_content = render_to_string(
        'notifications/email.txt',
        context={
            'first_name': 'Name',
            'event_type': 'Lesson',
            'title': 'Math',
            'start_time': 'Jul 23, 2025 at 21:48',
            'time_left': 'two days',
            'event_type_specific_message': EVENT_TYPE_SPECIFIC_MESSAGES['Lesson'],
        }
    )

    html_content = render_to_string(
        'notifications/email.html',
        context={
            'first_name': 'Name',
            'event_type': 'Lesson',
            'title': 'Math',
            'start_time': 'Jul 23, 2025 at 21:48',
            'time_left': 'two days',
            'event_type_specific_message': EVENT_TYPE_SPECIFIC_MESSAGES['Lesson'],
            }
        )
    
    msg = EmailMultiAlternatives(
        "Reminder",
        text_content,
        'address@gmail.com',
        ['address.com'],
    )
    
    msg.attach_alternative(html_content, "text/html")
    msg.send()