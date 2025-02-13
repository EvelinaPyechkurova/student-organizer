from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime

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
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.lesson:
            return f'{self.lesson.subject.name} {self.type} on {localtime(self.lesson.start_time).strftime("%a, %b %d %Y at %H:%M")}'
        elif self.subject:
            return f'{self.name} {self.type} on {localtime(self.start_time).strftime("%a, %b %d %Y at %H:%M")}'
        else:
            return 'Invalid assessment (missing subject and lesson)'