from datetime import timedelta

from django.db import models
from django.db.models.functions import Coalesce
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject
from lesson.models import Lesson

from utils.constants import MIN_ASSESSMENT_DURATION as MIN_DURATION, MAX_ASSESSMENT_DURATION as MAX_DURATION

class AssessmentManager(models.Manager):
    
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
            derived_user_id=Coalesce('subject__user', 'lesson__subject__user'),
            derived_subject_id=Coalesce('subject', 'lesson__subject'),
            derived_start_time=Coalesce('start_time', 'lesson__start_time'),
            derived_duration=Coalesce('duration', 'lesson__duration')
        )


class Assessment(models.Model):

    class Meta:
        db_table = 'assessment'

    class Type(models.TextChoices):
        TEST = 'T', 'Test'
        QUIZ = 'Q', 'Quiz'
        EXAM = 'E', 'Exam'
        MIDTERM = 'M', 'Midterm'
        ORAL_EXAM = 'O', 'Oral Exam'
        LAB_WORK = 'L', 'Lab Work'
        ESSAY = 'S', 'Essay'
        PROJECT = 'P', 'Project'
        
        
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=1, choices=Type, default=Type.TEST)
    start_time = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = AssessmentManager()
    
    @property
    def derived_subject(self):
        if hasattr(self, 'derived_subject_id'):
            return Subject.objects.get(id=self.derived_subject_id)
        return self.subject or (self.lesson and self.lesson.subject)
    

    def clean(self):
        super().clean()

        errors = {}

        if self.lesson and self.subject and self.subject != self.lesson.subject:
            errors['__all__'] = ValidationError(
                message=(
                    f'The selected lesson belongs to "{self.lesson.subject}" '
                    f'but this assessment is for "{self.subject}". '
                    'To fix this, either '
                    'select a lesson from the same subject as the assessment, or '
                    'remove either the lesson or the subject so the remaining one is used.'
                ),              
                code='subject_mismatch'
            )

        
        if self.lesson and self.start_time and self.start_time != self.lesson.start_time:
            errors['start_time'] = ValidationError(
                message=(

                    f'This assessment is linked to a lesson that starts at {localtime(self.lesson.start_time).strftime("%a, %b %d %Y at %H:%M")}, '
                    f'you have chosen a different start time for the assessment ({localtime(self.start_time).strftime("%a, %b %d %Y at %H:%M")}). '
                    'Since an assessment connected to a lesson must always use the lesson’s scheduled time, you need to either: '
                    'remove the selected lesson if this assessment should have its own custom time, or '
                    'remove the custom start time so the assessment automatically follows the lesson’s schedule..'
                ),
                code='start_time_mismatch'
            )

        if not (self.lesson or self.subject):
            errors['__all__'] = ValidationError(
                message='Assessment must have either a subject or a lesson.',
                code='required'
            )
        
        if not (self.lesson or self.start_time):
            errors['start_time'] = ValidationError(
                message="Start time is required if the assessment isn't linked to any lesson.",
                code='required'
            )
        
        if self.duration and self.duration < MIN_DURATION:
            errors['duration'] = ValidationError(
                message=f'Assessment duration must be at least {MIN_DURATION.seconds // 60} minutes.',
                code='min_duration_not_met'
            )
        
        if self.duration and self.duration > MAX_DURATION:
            errors['duration'] = ValidationError(
                message=f'Assessment duration can\'t exceed {MAX_DURATION.days} days.',
                code='max_duration_exceeded'
            )
        
        if self.start_time and self.start_time < now():
            errors['start_time'] = ValidationError(
                message='Assessment must start in the future.',
                code='assessment_starts_in_past'
            )
        
        if self.lesson and self.lesson.start_time < now():
            errors['lesson'] = ValidationError(
                message='Assessment can\'t be attached to lesson starting in the past.',
                code='assessment_starts_in_past'
            )
        
        if errors:
            raise ValidationError(errors)
            

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.lesson:
            self.subject = None
            self.start_time = None

        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.get_type_display()} — {self.derived_subject} on {localtime(self.start_time).strftime('%A, %b %d, %Y at %H:%M')}'