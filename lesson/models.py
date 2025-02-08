from datetime import timedelta

from django.db import models

from subject.models import Subject

class Lesson(models.Model):
    LESSON_TYPES = [
        ('L', 'Lecture'),
        ('P', 'Practice'),
        ('S', 'Seminar'),
        ('Y', 'Self-Study')
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=LESSON_TYPES)
    start_time = models.DateTimeField()
    duration_minutes = models.DurationField(default=timedelta(minutes=90))
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)