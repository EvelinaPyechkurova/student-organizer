from django.db import models
from django.db.models.functions import Coalesce
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject
from lesson.models import Lesson

from utils.accessors import get_subject, get_userprofile, get_time_display_format
from utils.constants import MIN_ASSESSMENT_DURATION as MIN_DURATION, MAX_ASSESSMENT_DURATION as MAX_DURATION
from utils.reminder_time import should_schedule_reminder, calculate_scheduled_reminder_time
from utils.time_format import format_time

REMINDER_TRIGGER_FIELD = 'derived_start_time_prop'

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
    scheduled_reminder_time = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = AssessmentManager()
    
    @property
    def derived_subject(self):
        if hasattr(self, 'derived_subject_id'):
            return Subject.objects.get(id=self.derived_subject_id)
        return self.subject or (self.lesson.subject if self.lesson else None)
    
    @property
    def derived_start_time_prop(self):
        return self.start_time or (self.lesson.start_time if self.lesson else None)
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_reminder_trigger_time = getattr(self, REMINDER_TRIGGER_FIELD)


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

        userprofile = get_userprofile(self)

        if should_schedule_reminder(self, userprofile, 'assessment', REMINDER_TRIGGER_FIELD):
            self.scheduled_reminder_time = calculate_scheduled_reminder_time(
                instance=self,
                userprofile=userprofile,
                event_type='assessment'
            )

        super().save(*args, **kwargs)
        self._original_reminder_trigger_time = getattr(self, REMINDER_TRIGGER_FIELD)


    def __str__(self):
        subject = get_subject(self)

        if hasattr(self, 'derived_start_time'):
            start_time = self.derived_start_time
        else:
            start_time = self.derived_start_time_prop

        return f'{self.get_type_display()} — {subject} on {format_time(start_time, get_time_display_format(self))}'