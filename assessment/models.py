from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject
from lesson.models import Lesson

class Assessment(models.Model):

    class Meta:
        db_table = 'assessment'

    MIN_DURATION = timedelta(minutes=5)
    MAX_DURATION = timedelta(days=7)

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
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=1, choices=Type, default=Type.TEST)
    start_time = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(default=timedelta(minutes=90))
    description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


    def clean(self):
        super().clean()

        if self.lesson and self.subject and self.subject != self.lesson.subject:
            raise ValidationError(
                message=(
                    f'The selected lesson belongs to "{self.lesson.subject}" '
                    f'but this assessment is for "{self.subject}". '
                    'To fix this, either '
                    'select a lesson from the same subject as the assessment, or '
                    'remove either the lesson or the subject so the remaining one is used.'
                ),              
                code='subject_mismatch'
            )

        if not (self.lesson or self.subject):
            raise ValidationError(
                message='Assessment must have either a subject or a lesson.',
                code='required'
            )
        
        if not (self.lesson or self.start_time):
            raise ValidationError(
                message="Start time is required if the assessment isn't linked to any lesson.",
                code='required'
            )
        
        if self.duration and self.duration < Assessment.MIN_DURATION:
            raise ValidationError(
                message=f'Assessment duration must be at least {Assessment.MIN_DURATION.seconds // 60} minutes.',
                code='min_duration_not_met'
            )
        
        if self.duration and self.duration > Assessment.MAX_DURATION:
            raise ValidationError(
                message=f'Assessment duration can\'t exceed {Assessment.MAX_DURATION.days} days.',
                code='max_duration_exceeded'
            )
        
        if self.start_time or self.lesson.start_time > now():
            raise ValidationError(
                message='Lesson must start in the future.',
                code='lesson_starts_in_past'
            )
            

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.lesson:
            self.subject = None
            self.start_time = None
            if not self.duration:
                self.duration = None
        else:
            if not self.duration:
                self.duration = timedelta(minutes=90) # replace with standard for user

        super().save(*args, **kwargs)


    def __str__(self):
        if self.lesson:
            return f'{self.lesson.subject} {self.get_type_display().lower()} on {localtime(self.lesson.start_time).strftime("%a, %b %d %Y at %H:%M")}'
        elif self.subject:
            return f'{self.subject} {self.get_type_display().lower()} on {localtime(self.start_time).strftime("%a, %b %d %Y at %H:%M")}'
        else:
            return 'Invalid assessment (missing subject and lesson)'
        