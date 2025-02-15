from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime
from django.core.exceptions import ValidationError

from subject.models import Subject

class Lesson(models.Model):

    class Type(models.TextChoices):
        LECTURE = 'L', 'Lecture'
        PRACTICE = 'P', 'Practice'
        SEMINAR = 'S', 'Seminar'
        SELF_STUDY = 'Y', 'Self-Study'


    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=Type, default=Type.LECTURE)
    start_time = models.DateTimeField()
    duration_minutes = models.DurationField(default=timedelta(minutes=90))
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    
    def clean(self):
        super().clean()

        if self.duration_minutes.total_seconds() <= 0:
            raise ValidationError(
                message='Lesson duration must be a positive value.',
                code='non_positive'
            )


    def __str__(self):
        return f'{self.subject.name} {self.get_type_display().lower()} on {localtime(self.start_time).strftime("%a, %b %d %Y at %H:%M")}'