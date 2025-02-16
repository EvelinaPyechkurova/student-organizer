from django.db import models

from subject.models import Subject
from lesson.models import Lesson

class Homework(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True)
    lesson_given = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True, related_name="given_homeworks")
    lesson_due = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True, related_name="due_homeworks")
    time_start = models.DateTimeField(blank=True, null=True)
    due_to = models.DateTimeField(blank=True, null=True)
    task = models.CharField(max_length=1000)
    completion_percent = models.IntegerField(default=0)
    has_subtasks = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)