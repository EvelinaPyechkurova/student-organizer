from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from subject.models import Subject

from .models import Lesson

class LessontModelTests(TestCase):

    DEFAULT_DURATION = timedelta(minutes=90) # replace with standard for user
    START_TIME = now() + timedelta(minutes=1)
    SUBJECT_NAME = 'The History of Ukrainian Cybernetics'

    def setUp(self):
        '''Create a test Subject for Lesson model.'''
        self.user = User.objects.create_user(username='testuser')
        self.subject = Subject.objects.create(user=self.user, name=self.SUBJECT_NAME)


    def test_valid_lesson_creation(self):
        '''Test creating a valid Lesson instance.'''
        lesson = Lesson.objects.create(
            subject=self.subject,
            start_time=self.START_TIME,
        )
        self.assertEqual(lesson.subject, self.subject)
        self.assertEqual(lesson.type, Lesson.Type.LECTURE)
        self.assertEqual(lesson.start_time, self.START_TIME)
        self.assertEqual(lesson.duration, self.DEFAULT_DURATION)


    def test_lesson_start_time_in_past(self):
        '''Test creating lesson that starts in the past fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type=Lesson.Type.PRACTICE,
                start_time = now() - timedelta(seconds=1)
            )
            self.fail('ValidationError was not raised for lesson starting in the past')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('start_time', [])]
            self.assertIn('lesson_starts_in_past', error_codes)


    def test_minimum_lesson_duration(self):
        '''Test that creating lesson shorter than 15 minutes fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type=Lesson.Type.SEMINAR,
                start_time=now() + timedelta(days=1),
                duration=Lesson.MIN_DURATION - timedelta(seconds=1)
            )
            self.fail("ValidationError was not raised for minimum duration not met")
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('duration', [])]
            self.assertIn('min_duration_not_met', error_codes)


    def test_maximum_lesson_duration(self):
        '''Test that creating lesson longer than 8 hours fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type=Lesson.Type.SEMINAR,
                start_time=now() + timedelta(days=1),
                duration=Lesson.MAX_DURATION + timedelta(seconds=1)
            )
            self.fail("ValidationError was not raised for maximum duration exceeded")
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('duration', [])]
            self.assertIn('max_duration_exceeded', error_codes)


    def test_lesson_str_method(self):
        '''Test the __str__ method of Subject.'''
        lesson = Lesson.objects.create(
            subject=self.subject,
            type=Lesson.Type.SELF_STUDY,
            start_time=now() + timedelta(days=1, hours=2)
        )
        self.assertIn(self.subject.name, str(lesson))
        self.assertIn("self-study", str(lesson).lower())