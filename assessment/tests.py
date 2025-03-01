from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from subject.models import Subject
from lesson.models import Lesson

from .models import Assessment

class AssessmentModelTests(TestCase):

    SUBJECT_NAME = 'Python for Big Data and Data Science'

    def setUp(self):
        '''Create a test subject and lesson for Assessment model.'''
        self.user = User.objects.create_user(username='testuser')
        self.subject = Subject.objects.create(user=self.user, name=self.SUBJECT_NAME)
        self.lesson = Lesson.objects.create(subject=self.subject)