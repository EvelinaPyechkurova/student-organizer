from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject

class Lesson(models.Model):

    class Meta:
        db_table = 'lesson'

    MIN_DURATION = timedelta(minutes=15)
    MAX_DURATION = timedelta(hours=8)

    class Type(models.TextChoices):
        LECTURE = 'L', 'Lecture'
        PRACTICE = 'P', 'Practice'
        SEMINAR = 'S', 'Seminar'
        SELF_STUDY = 'Y', 'Self-Study'
        

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=Type, default=Type.LECTURE)
    start_time = models.DateTimeField()
    duration = models.DurationField(default=timedelta(minutes=90))
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    
    def clean(self):
        super().clean()

        if self.duration < self.MIN_DURATION:
            raise ValidationError(
                message=f'Lesson duration must be at least {Lesson.MIN_DURATION.seconds // 60} minutes.',
                code='min_duration_not_met'
            )
        
        if self.duration > self.MAX_DURATION:
            raise ValidationError(
                message=f'Lesson duration can\'t exceed {Lesson.MAX_DURATION.seconds // 3600} hourse.',
                code='max_duration_exceeded'
            )
        
        if self.start_time < now():
            raise ValidationError(
                message='Lesson must start in the future.',
                code='lesson_starts_in_past'
            )

        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.subject} {self.get_type_display().lower()} on {localtime(self.start_time).strftime("%a, %b %d %Y at %H:%M")}'