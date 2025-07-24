from django.db import models
from django.contrib.auth.models import User

from utils.constants import (
    DEFAULT_LESSON_DURATION,
    DEFAULT_RECIEVE_LESSON_REMINDERS,
    DEFAULT_LESSON_REMINDER_TIMING,
    DEFAULT_RECIEVE_ASSESSMENT_REMINDERS,
    DEFAULT_ASSESSMENT_REMINDER_TIMING,
    DEFAULT_RECIEVE_HOMEWORK_REMINDERS,
    DEFAULT_HOMEWORK_REMINDER_TIMING,
)

class UserProfile(models.Model):

    class Meta:
        db_table = 'userprofile'

    class NotificationMethod(models.TextChoices):
        PUSH = 'P', 'Push'
        EMAIL = 'E', 'Email'
        BOTH = 'B', 'Both'

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    lesson_duration = models.DurationField(default=DEFAULT_LESSON_DURATION)
    assessment_duration = models.DurationField(default=DEFAULT_LESSON_DURATION)

    notification_method = models.CharField(
        max_length=1,
        choices=NotificationMethod,
        default=NotificationMethod.PUSH
    )
    
    recieve_lesson_reminders = models.BooleanField(default=DEFAULT_RECIEVE_LESSON_REMINDERS)
    lesson_reminder_timing = models.DurationField(default=DEFAULT_LESSON_REMINDER_TIMING)

    recieve_assessment_reminders = models.BooleanField(default=DEFAULT_RECIEVE_ASSESSMENT_REMINDERS)
    assessment_reminder_timing = models.DurationField(default=DEFAULT_ASSESSMENT_REMINDER_TIMING)

    recieve_homework_reminders = models.BooleanField(default=DEFAULT_RECIEVE_HOMEWORK_REMINDERS)
    homework_reminder_timing = models.DurationField(default=DEFAULT_HOMEWORK_REMINDER_TIMING)

    def __str__(self):
        return f'{self.user.username} profile'

