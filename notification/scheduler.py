from django.utils.timezone import now, localtime

from lesson.models import Lesson
from assessment.models import Assessment
from homework.models import Homework
from userprofile.models import UserProfile

from subject.templatetags.custom_tags import get_human_duration
from utils.accessors import get_subject, get_user, get_userprofile
from notification.services.email_service import send_email

MODEL_CONFIGS = [
    {
        'model': Lesson,
        'select_related': ['subject__user__userprofile'],
        'use_with_derived_fields': False,
    },
    {
        'model': Assessment,
        'select_related': [
            'subject__user__userprofile',
            'lesson__subject__user__userprofile',
        ],
        'use_with_derived_fields': True,
    },
    {
        'model': Homework,
        'select_related': [
            'subject__user__userprofile',
            'lesson_given__subject__user__userprofile',
            'lesson_due__subject__user__userprofile',
        ],
        'use_with_derived_fields': True,
    },
]

def get_scheduled_time(event_type, event):
    '''
    Returns value responsible of event sheduled time
    based on its time.
    '''
    scheduled_time_path = {
        'lesson': lambda event: event.start_time,
        'assessment': lambda event: event.derived_start_time,
        'homework': lambda event: event.derived_due_at,
    }

    return scheduled_time_path[event_type](event)


def create_email_context(event, user):
    '''
    Builds context for the email notification.
    '''
    event_type = type(event).__name__.lower()
    event_subject = get_subject(event)
    scheduled_time = get_scheduled_time(event_type, event)
    time_left = scheduled_time - now()
    return {
        'first_name': user.first_name,
        'email': user.email,
        'event_id': event.id,
        'event_type': event_type,
        'event_subject': event_subject,
        'scheduled_time': localtime(scheduled_time).strftime('%d.%m.%Y %H:%M'),
        'time_left': get_human_duration(time_left)
    }


def update_event_reminder_status(event):
    event.reminder_sent = True
    event.save(update_fields=['reminder_sent'])


def send_notifications():
    '''
    Finds and sends all due scheduled notifications for Lesson, Assessment, and Homework.
    '''

    events = []
   
    for config in MODEL_CONFIGS:
        query_set = (
            config['model'].objects.with_derived_fields()
            if config['use_with_derived_fields']
            else config['model'].objects
        )

        query_set = query_set.filter(
            scheduled_reminder_time__lte=now(),
            reminder_sent=False,
        ).select_related(*config['select_related'])

        events.extend(query_set)


    for event in events:
        user = get_user(event)
        userprofile = get_userprofile(event)

        if userprofile.notification_method in (
            UserProfile.NotificationMethod.EMAIL,
            UserProfile.NotificationMethod.BOTH,
        ):
            context = create_email_context(event, user)
            send_email(context)
            update_event_reminder_status(event)

        if userprofile.notification_method in (
            UserProfile.NotificationMethod.PUSH,
            UserProfile.NotificationMethod.BOTH,
        ):
            pass


        