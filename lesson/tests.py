from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from subject.models import Subject

from .models import Lesson

class LessontModelTests(TestCase):

    SUBJECT_NAME = 'The History of Ukrainian Cybernetics'
    DEFAULT_DURATION = timedelta(minutes=90) # replace with standard for user
    START_TIME = now() + timedelta(minutes=1)

    def setUp(self):
        '''Create a test subject for Lesson model.'''
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

    
    def test_type_must_be_one_character(self):
        '''Test creating lesson with type field containing more than one character fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type='INVALID',
                start_time=self.START_TIME
            )
            self.fail('ValidationError was not raised for type field length constraint violation.')
        except ValidationError as e:
            self.assertIn('type', e.error_dict)


    def test_invalid_type_choice(self):
        '''Test creating lesson with type field containing invalid type choice fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type='X',
                start_time=self.START_TIME
            )
            self.fail('ValidationError was not raised for invalid type choice')
        except ValidationError as e:
            self.assertIn('type', e.error_dict)


    def test_start_time_cannot_be_blank(self):
        '''Test creating lesson without start_time fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
            )
            self.fail('TypeError was not raised for missing start_time')
        except TypeError:
            pass
        except ValidationError as e:
            self.assertIn('start_time', e.error_dict)


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
        '''Test creating lesson shorter than 15 minutes fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type=Lesson.Type.SEMINAR,
                start_time=self.START_TIME,
                duration=Lesson.MIN_DURATION - timedelta(seconds=1)
            )
            self.fail('ValidationError was not raised for minimum duration not met')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('duration', [])]
            self.assertIn('min_duration_not_met', error_codes)


    def test_maximum_lesson_duration(self):
        '''Test creating lesson longer than 8 hours fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type=Lesson.Type.SEMINAR,
                start_time=self.START_TIME,
                duration=Lesson.MAX_DURATION + timedelta(seconds=1)
            )
            self.fail('ValidationError was not raised for maximum duration exceeded')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('duration', [])]
            self.assertIn('max_duration_exceeded', error_codes)


    def test_lesson_str_method(self):
        '''Test the __str__ method of Lesson.'''
        lesson = Lesson.objects.create(
            subject=self.subject,
            type=Lesson.Type.SELF_STUDY,
            start_time=self.START_TIME
        )
        self.assertIn(self.subject.name, str(lesson))
        self.assertIn('self-study', str(lesson).lower())