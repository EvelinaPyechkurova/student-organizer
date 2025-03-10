from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject

class LessonManager(models.Manager):

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj
    
    def bulk_create(self, objs, **kwargs):
        for obj in objs:
            obj.full_clean()
        return super().bulk_create(objs, **kwargs)
    

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
    duration = models.DurationField(default=timedelta(minutes=90)) # replace with standard for user
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = LessonManager()

    def clean(self):
        super().clean()

        errors = {}

        if self.duration < self.MIN_DURATION:
            errors['duration'] =  ValidationError(
                message=f'Lesson duration must be at least {Lesson.MIN_DURATION.seconds // 60} minutes.',
                code='min_duration_not_met'
            )
        
        if self.duration > self.MAX_DURATION:
            errors['duration'] =  ValidationError(
                message=f'Lesson duration can\'t exceed {Lesson.MAX_DURATION.seconds // 3600} hours.',
                code='max_duration_exceeded'
            )
        
        if self.start_time and self.start_time < now():
            errors['start_time'] =  ValidationError(
                message='Lesson must start in the future.',
                code='lesson_starts_in_past'
            )
        
        if errors:
            raise ValidationError(errors)

        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.subject} {self.get_type_display().lower()} on {localtime(self.start_time).strftime('%a, %b %d %Y at %H:%M')}'