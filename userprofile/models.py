from django.db import models
from django.contrib.auth.models import User

from utils.constants import (
    DEFAULT_LESSON_DURATION,
    DEFAULT_RECIEVE_LESSON_REMAINDERS,
    DEFAULT_LESSON_REMAINDER_TIMING,
    DEFAULT_RECIEVE_ASSESSMENT_REMAINDERS,
    DEFAULT_ASSESSMENT_REMAINDER_TIMING,
    DEFAULT_RECIEVE_HOMEWORK_REMAINDERS,
    DEFAULT_HOMEWORK_REMAINDER_TIMING,
)

class UserProfile(models.Model):
    # "These are our recommended reminder settings — you can change them anytime."
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    lesson_duration = models.DurationField(default=DEFAULT_LESSON_DURATION)
    assessment_duration = models.DurationField(default=DEFAULT_LESSON_DURATION)
    
    recieve_lesson_remainders = models.BooleanField(default=DEFAULT_RECIEVE_LESSON_REMAINDERS)
    lesson_remainder_timing = models.DurationField(default=DEFAULT_LESSON_REMAINDER_TIMING)

    recieve_assessment_remainders = models.BooleanField(default=DEFAULT_RECIEVE_ASSESSMENT_REMAINDERS)
    assessment_remainder_timing = models.DurationField(default=DEFAULT_ASSESSMENT_REMAINDER_TIMING)

    recieve_homework_remainders = models.BooleanField(default=DEFAULT_RECIEVE_HOMEWORK_REMAINDERS)
    homework_remainder_timing = models.DurationField(default=DEFAULT_HOMEWORK_REMAINDER_TIMING)

    def __str__(self):
        return f'{self.user.username} profile'

