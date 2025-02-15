from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime
from django.core.exceptions import ValidationError

from subject.models import Subject
from lesson.models import Lesson

class Assessment(models.Model):

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
    duration_minutes = models.DurationField(default=timedelta(minutes=90))
    description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


    def clean(self):
        if not (self.lesson or self.subject):
            raise ValidationError(
                message='Assessment must have either a subject or a lesson.',
                code='required'
            )
        if not (self.lesson or self.start_time):
            raise ValidationError(
                message='Start time is required if the assessment is not linked to a lesson.',
                code='required'
            )
        if self.duration_minutes and self.duration_minutes <= 0:
            raise ValidationError(
                message='Lesson duration must be a positive value.',
                code='non_positive'
            )
            

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.lesson:
            self.subject = None
            self.start_time = None
            if not self.duration_minutes:
                self.duration_minutes = self.lesson.duration_minutes
        else:
            if not self.duration_minutes:
                self.duration_minutes = 90 # replace with standard for user

        super().save(*args, **kwargs)


    def __str__(self):
        if self.lesson:
            return f'{self.lesson.subject.name} {self.type} on {localtime(self.lesson.start_time).strftime("%a, %b %d %Y at %H:%M")}'
        elif self.subject:
            return f'{self.subject.name} {self.type} on {localtime(self.start_time).strftime("%a, %b %d %Y at %H:%M")}'
        else:
            return 'Invalid assessment (missing subject and lesson)'
        