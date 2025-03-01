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
    START_TIME = now() + timedelta(days=2)
    DEFAULT_DURATION = timedelta(minutes=90)

    def setUp(self):
        '''Create a test subject and lesson for Assessment model.'''
        self.user = User.objects.create_user(username='testuser')
        self.subject = Subject.objects.create(user=self.user, name=self.SUBJECT_NAME)
        self.lesson = Lesson.objects.create(
            subject=self.subject,
            start_time=now() + timedelta(days=1),
        )


    def test_valid_assessment_creation(self):
        assessment = Assessment.objects.create(
            subject=self.subject,
            type=Assessment.Type.TEST,
            start_time=self.START_TIME,
        )
        self.assertEqual(assessment.subject, self.subject)
        self.assertEqual(assessment.type, Assessment.Type.TEST)
        self.assertEqual(assessment.start_time, self.START_TIME)
        self.assertEqual(assessment.duration, self.DEFAULT_DURATION)


    def test_start_time_must_be_in_future(self):
        '''Test creating assessment that starts in the past fails.'''
        try:
            assessment = Assessment.objects.create(
                subject=self.subject,
                type=Assessment.Type.EXAM,
                start_time=now() - timedelta(days=1),
                duration=timedelta(minutes=60)
            )
            self.fail('ValidationError was not raised for assessment starting in the past.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('start_time', [])]
            self.assertIn('assessment_starts_in_past', error_codes)


    def test_lesson_start_time_must_be_in_future(self):
        '''Test creating assessment attached to lesson that starts in the past fails.'''
        try:
            past_lesson = Lesson(
                subject=self.subject,
                start_time=now() - timedelta(days=1),
            )

            assessment = Assessment.objects.create(
                lesson=past_lesson,
                type=Assessment.Type.ESSAY
            )
            self.fail('ValidationError was not raised for assessment attached to lesson starting in the past.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('lesson', [])]
            self.assertIn('assessment_starts_in_past', error_codes)


    def test_assessment_requires_subject_or_lesson(self):
        '''Test creating assessment with neither subject nor lesson fails.'''
        try:
            assessment = Assessment.objects.create(
                start_time=self.START_TIME,
                type=Assessment.Type.LAB_WORK,
                duration=timedelta(minutes=60)
            )
            self.fail('ValidationError was not raised for assessment with neither subject nor lesson.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('__all__', [])]
            self.assertIn('required', error_codes)


    def test_start_time_required_if_no_lesson(self):
        '''Test creating assessment with neither start_time nor lesson fails.'''
        try:
            assessment = Assessment.objects.create(
                subject=self.subject,
                type=Assessment.Type.MIDTERM,
                duration=timedelta(minutes=60)
            )
            self.fail('ValidationError was not raised for assessment with neither start_time nor lesson.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('start_time', [])]
            self.assertIn('required', error_codes)

    
    def test_type_must_be_one_character(self):
        '''Test creating assessment with type field containing more than one character fails.'''
        try:
            assessment = Assessment.objects.create(
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
            assessment = Assessment.objects.create(
                subject=self.subject,
                type='X',
                start_time=self.START_TIME
            )
            self.fail('ValidationError was not raised for invalid type choice')
        except ValidationError as e:
            self.assertIn('type', e.error_dict)


    def test_minimum_assessment_duration(self):
        '''Test creating assessment shorter than 5 minutes fails.'''
        try:
            assessment = Assessment.objects.create(
                subject=self.subject,
                type=Assessment.Type.ORAL_EXAM,
                start_time=self.START_TIME,
                duration=Assessment.MIN_DURATION - timedelta(seconds=1)
            )
            self.fail('ValidationError was not raised for minimum duration not met')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('duration', [])]
            self.assertIn('min_duration_not_met', error_codes)


    def test_maximum_lesson_duration(self):
        '''Test creating assessment longer than 7 days fails.'''
        try:
            lesson = Lesson.objects.create(
                subject=self.subject,
                type=Assessment.Type.QUIZ,
                start_time=self.START_TIME,
                duration=Lesson.MAX_DURATION + timedelta(seconds=1)
            )
            self.fail('ValidationError was not raised for maximum duration exceeded')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('duration', [])]
            self.assertIn('max_duration_exceeded', error_codes)


    def test_lesson_and_subject_must_match(self):
        '''Test creating assessment with lesson and subject not matching fails.'''
        another_subject = Subject.objects.create(
            user=self.user,
            name='Frontend and Backend'
        )

        lesson = Lesson.objects.create(
            subject=another_subject,
            start_time=self.START_TIME,
            duration=timedelta(minutes=90)
        )

        try:
            assessment = Assessment.objects.create(
                subject=self.subject,
                lesson=lesson,
                type=Assessment.Type.EXAM
            )
            self.fail('ValidationError was not raised for subject and lesson mismatch.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('__all__', [])]
            self.assertIn('subject_mismatch', error_codes)


    def test_start_time_must_match(self):
        '''Test creating assessment with start_time not matching attached lesson start_time fails.'''
        try:
            assessment = Assessment.objects.create(
                subject=self.subject,
                lesson=self.lesson,
                start_time=self.START_TIME + timedelta(hours=1),
                type=Assessment.Type.QUIZ
            )
            self.fail('ValidationError was not raised for subject\'s and lesson\'s start_time mismatch.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('start_time', [])]
            self.assertIn('start_time_mismatch', error_codes)


    def test_assessment_duration_can_exceed_lesson_duration(self):
        '''Test creating assessment with duration exceeding lesson duration not fails.'''
        try:
            assessment = Assessment(
                lesson=self.lesson,
                type=Assessment.Type.EXAM,
                duration=timedelta(minutes=120)
            )
            assessment.full_clean()
        except ValidationError:
            self.fail('ValidationError raised incorrectly for assessment longer than lesson duration.')


    def test_lesson_str_method(self):
        '''Test the __str__ method of Assessment.'''
        assessment = Assessment.objects.create(
            subject=self.subject,
            type=Assessment.Type.TEST,
            start_time=self.START_TIME
        )
        self.assertIn(self.subject.name, str(assessment))
        self.assertIn('test', str(assessment).lower())