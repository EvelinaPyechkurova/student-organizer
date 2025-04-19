from django.db import models
from django.contrib.auth.models import User

from utils.constants import (
    DEFAULT_LESSON_LENGTH,
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

