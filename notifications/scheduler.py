from django.utils.timezone import now

from utils.userprofile import get_user

from subject.templatetags.custom_tags import get_human_duration

from lesson.models import Lesson
from assessment.models import Assessment
from homework.models import Homework

from .services.email_service import send_email

def get_scheduled_time(event_type, event):
    '''
    Returns value responsible of event sheduled time
    based on its time.
    '''
    scheduled_time_path = {
        'lesson': lambda event: event.start_time,
        'assessment': lambda event: event.derived_start_time_prop,
        'homework': lambda event: event.derived_due_at_prop,
    }

    return scheduled_time_path[event_type](event)


def create_email_context(event, user):
    '''
    Builds context for the email notification.
    '''
    event_type = type(event).__name__.lower()
    scheduled_time = get_scheduled_time(event_type, event)
    time_left = scheduled_time - now()
    return {
        'first_name': user.first_name,
        'event_type': event_type,
        'title': str(event),
        'scheduled_time': scheduled_time,
        'time_left': get_human_duration(time_left)
    }


def send_notifications():
    '''
    Finds and sends all due scheduled notifications for Lesson, Assessment, and Homework.
    '''
    events = []
    events.extend(
        Lesson.objects.filter(
            scheduled_reminder_time__lte=now(),
            reminder_sent=False
        ).select_related(
            'subject__user__userprofile',
        )
    )
    events.extend(
        Assessment.objects.filter(
            scheduled_reminder_time__lte=now(),
            reminder_sent=False
        ).select_related(
            'subject__user__userprofile',
            'lesson__subject__user__userprofile',
        )
    )
    events.extend(
        Homework.objects.filter(
            scheduled_reminder_time__lte=now(),
            reminder_sent=False
        ).select_related(
            'subject__user__userprofile',
            'lesson_given__subject__user__userprofile',
            'lesson_due__subject__user__userprofile',
        )
    )

    for event in events:
        user = get_user(event)
        context = create_email_context(event, user)

        send_email(context)
        event.reminder_sent = True
        event.save(update_fields=['reminder_sent'])