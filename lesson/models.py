from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject

class Lesson(models.Model):

    MIN_LESSON_DURATION = timedelta(minutes=15)
    MAX_LESSON_DURATION = timedelta(hours=8)


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

        if self.start_time + self.duration_minutes < now():
            raise ValidationError(
                message='The lesson must end in the future.',
                code='lesson_ends_in_past'
            )

        if self.duration_minutes < self.MIN_LESSON_DURATION:
            raise ValidationError(
                message=f'Lesson duration must be at least {Lesson.MIN_LESSON_DURATION // 60} minutes.',
                code='min_duration_not_met'
            )
        
        if self.duration_minutes > self.MAX_LESSON_DURATION:
            raise ValidationError(
                message=f'Lessons can\'t exceed {Lesson.MAX_LESSON_DURATION // 3600} hourse.',
                code='max_duration_exceeded'
            )

        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.subject} {self.get_type_display().lower()} on {localtime(self.start_time).strftime("%a, %b %d %Y at %H:%M")}'