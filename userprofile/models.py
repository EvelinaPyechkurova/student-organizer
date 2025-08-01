from django.db import models
from django.contrib.auth.models import User

from utils.constants import (
    DEFAULT_LESSON_DURATION,
    DEFAULT_RECEIVE_LESSON_REMINDERS,
    DEFAULT_LESSON_REMINDER_TIMING,
    DEFAULT_RECEIVE_ASSESSMENT_REMINDERS,
    DEFAULT_ASSESSMENT_REMINDER_TIMING,
    DEFAULT_RECEIVE_HOMEWORK_REMINDERS,
    DEFAULT_HOMEWORK_REMINDER_TIMING,
)

class UserProfile(models.Model):

    class Meta:
        db_table = 'userprofile'

    class NotificationMethod(models.TextChoices):
        PUSH = 'P', 'Push'
        EMAIL = 'E', 'Email'
        BOTH = 'B', 'Both'

    class TimeDisplayFormat(models.TextChoices):
        H24 = '24', '24-hour (13:00)'
        H12 = '12', '12-hour (1:00 PM)'

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    lesson_duration = models.DurationField(default=DEFAULT_LESSON_DURATION)
    assessment_duration = models.DurationField(default=DEFAULT_LESSON_DURATION)

    notification_method = models.CharField(
        max_length=1,
        choices=NotificationMethod,
        default=NotificationMethod.PUSH
    )
    
    receive_lesson_reminders = models.BooleanField(default=DEFAULT_RECEIVE_LESSON_REMINDERS)
    lesson_reminder_timing = models.DurationField(default=DEFAULT_LESSON_REMINDER_TIMING)

    receive_assessment_reminders = models.BooleanField(default=DEFAULT_RECEIVE_ASSESSMENT_REMINDERS)
    assessment_reminder_timing = models.DurationField(default=DEFAULT_ASSESSMENT_REMINDER_TIMING)
    
    receive_homework_reminders = models.BooleanField(default=DEFAULT_RECEIVE_HOMEWORK_REMINDERS)
    homework_reminder_timing = models.DurationField(default=DEFAULT_HOMEWORK_REMINDER_TIMING)

    time_display_format = models.CharField(
        max_length=2,
        choices=TimeDisplayFormat,
        default=TimeDisplayFormat.H24
    )

    def __str__(self):
        return f'{self.user.username} profile'

