from django.db import models
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject

from utils.constants import MAX_LESSON_DURATION as MAX_DURATION, MIN_LESSON_DURATION as MIN_DURATION
from utils.default import set_dafault_if_none
from utils.reminder_time import should_schedule_reminder, calculate_scheduled_reminder_time
from utils.userprofile import get_userprofile

class LessonManager(models.Manager):

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj
    
    def bulk_create(self, objs, **kwargs):
        for obj in objs:
            obj.full_clean()
        return super().bulk_create(objs, **kwargs)
    
    def with_derived_fields(self):
        return self.annotate(
            derived_user_id = models.F('subject__user')
        )
    

class Lesson(models.Model):

    class Meta:
        db_table = 'lesson'

    class Type(models.TextChoices):
        LECTURE = 'L', 'Lecture'
        PRACTICE = 'P', 'Practice'
        SEMINAR = 'S', 'Seminar'
        SELF_STUDY = 'Y', 'Self-Study'
        

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=Type, default=Type.LECTURE)
    start_time = models.DateTimeField()
    duration = models.DurationField(blank=True, null=True)
    scheduled_reminder_time = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = LessonManager()

    def clean(self):
        super().clean()

        errors = {}

        if self.duration < MIN_DURATION:
            errors['duration'] =  ValidationError(
                message=f'Lesson duration must be at least {MIN_DURATION.seconds // 60} minutes.',
                code='min_duration_not_met'
            )
        
        if self.duration > MAX_DURATION:
            errors['duration'] =  ValidationError(
                message=f'Lesson duration can\'t exceed {MAX_DURATION.seconds // 3600} hours.',
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
        set_dafault_if_none(self, 'duration', self.subject.user.userprofile.lesson_duration)
        
        
        userprofile=get_userprofile(self)
        if should_schedule_reminder(self, userprofile, 'lesson'):
            self.scheduled_reminder_time = calculate_scheduled_reminder_time(
                instance=self,
                userprofile=userprofile,
                event_type='lesson'
            )

        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.get_type_display()} — {self.subject} on {localtime(self.start_time).strftime('%A, %b %d, %Y at %H:%M')}'