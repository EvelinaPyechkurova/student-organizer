from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from subject.models import Subject
from lesson.models import Lesson

from .models import Homework

class HomeworkModelTests(TestCase):
    
    SUBJECT_NAME = 'Functional Programming'
    START_TIME = now() - timedelta(hours=2)
    DUE_TIME = now() + timedelta(days=5)


    def setUp(self):
        '''Create test user, subject, and lessons for Homework model.'''
        self.user = User.objects.create_user(username='testuser')
        self.subject = Subject.objects.create(user=self.user, name=self.SUBJECT_NAME)
        self.lesson_given = Lesson(
            subject=self.subject,
            start_time=now() - timedelta(days=1)
        )
        self.lesson_due = Lesson.objects.create(
            subject=self.subject,
            start_time=now() + timedelta(days=7)
        )

    
    def test_valid_homework_creation(self):
        '''Test creating a valid Homework instance.'''
        homework = Homework.objects.create(
            subject=self.subject,
            task='Complete the Python set-up',
            start_time=self.START_TIME,
            due_at=self.DUE_TIME,
        )
        self.assertEqual(homework.subject, self.subject)
        self.assertEqual(homework.task, 'Complete the Python set-up')
        self.assertEqual(homework.start_time, self.START_TIME)
        self.assertEqual(homework.due_at, self.DUE_TIME)
        self.assertEqual(homework.completion_percent, 0)


    def test_homework_must_have_subject_or_lesson(self):
        '''Test creating homework without neither subject nor lesson_given nor lesson_due fails.'''
        try:
            homework = Homework.objects.create(
                task='Some task',
                start_time=self.START_TIME
            )
            self.fail('ValidationError was not raised for homework with neither subject nor lessons.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('__all__', [])]
            self.assertIn('required', error_codes)


    def test_homework_must_have_due_date_or_lesson_due(self):
        '''Test homework without neither due_at nor lesson_due fails.'''
        try:
            homework = Homework.objects.create(
                subject=self.subject,
                task='Some task',
                start_time=self.START_TIME
            )
            self.fail('ValidationError was not raised for homework with neither due date nor lesson_due.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('due_at', [])]
            self.assertIn('required', error_codes)


    def test_lesson_given_and_lesson_due_must_have_same_subject(self):
        '''Test creating homework with lesson_given and lesson_due belonging to different subjects fails.'''
        another_subject = Subject.objects.create(
            user=self.user,
            name='Functional Programming'
        )
        lesson_given = Lesson.objects.create(
            subject=another_subject,
            start_time=now() + timedelta(days=2)
        )

        try:
            homework = Homework.objects.create(
                lesson_given=lesson_given,
                lesson_due=self.lesson_due,
                task='Some task'
            )
            self.fail('ValidationError was not raised for homework with mismatched lesson\'s subjects.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('__all__', [])]
            self.assertIn('subject_mismatch', error_codes)


    def test_homework_start_time_cannot_be_older_than_1_year(self):
        '''Test creating homework with start_time more than 1 year in the past fails.'''
        try:
            homework = Homework.objects.create(
                subject=self.subject,
                start_time=now() - (Homework.MAX_TIMEFRAME + timedelta(days=1)),
                task='Some task'
            )
            self.fail(f'ValidationError was not raised for homework with start_time more than {Homework.MAX_TIMEFRAME.days} days in the past.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('start_time', [])]
            self.assertIn('past_limit_exceeded', error_codes)


    def test_homework_start_time_cannot_be_more_than_1_year_ahead(self):
        '''Test creating homework with start_time more than 1 year in the future fails.'''
        try:
            homework = Homework.objects.create(
                subject=self.subject,
                start_time=now() + Homework.MAX_TIMEFRAME + timedelta(days=1),
                task='Some task'
            )
            self.fail(f'ValidationError was not raised for homework with start_time more than {Homework.MAX_TIMEFRAME.days} days in the future.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('start_time', [])]
            self.assertIn('future_limit_exceeded', error_codes)


    def test_lesson_given_start_time_cannot_be_older_than_1_year(self):
        '''Test creating homework given at lesson starting more than 1 year in the past fails.'''
        lesson = Lesson(
            subject=self.subject,
            start_time=now() - (Homework.MAX_TIMEFRAME + timedelta(days=1)),
        )

        try:
            homework = Homework.objects.create(
                lesson_given=lesson,
                task='Some task'
            )
            self.fail(f'ValidationError was not raised for lesson_given start_time more than {Homework.MAX_TIMEFRAME.days} days in the past.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('lesson_given', [])]
            self.assertIn('past_limit_exceeded', error_codes)


    def test_lesson_given_start_time_cannot_be_in_future(self):
        '''Test creating homework with lesson_given in the future fails.'''
        lesson = Lesson.objects.create(
            subject=self.subject,
            start_time=now() + timedelta(days=5)
        )

        try:
            homework = Homework.objects.create(
                lesson_given=lesson,
                task='Some task'
            )
            self.fail('ValidationError was not raised for homework with lesson_given start_time in the future.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('lesson_given', [])]
            self.assertIn('invalid_given_time', error_codes)


    def test_due_at_cannot_be_more_than_1_year_ahead(self):
        '''Test creating homework with due_at more than 1 year in the future fails.'''
        try:
            homework = Homework.objects.create(
                subject=self.subject,
                due_at=now() + (Homework.MAX_TIMEFRAME + timedelta(days=1)),
                task='Some task'
            )
            self.fail('ValidationError was not raised for homework with due_at more than {Homework.MAX_TIMEFRAME.days} days in the future.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('due_at', [])]
            self.assertIn('future_limit_exceeded', error_codes)


    def test_due_at_cannot_be_more_than_1_month_in_the_past(self):
        '''Test creating homework with due_at more than 1 month in the past fails.'''
        try:
            homework = Homework.objects.create(
                subject=self.subject,
                due_at=now() - timedelta(days=31),
                task='Some task'
            )
            self.fail('ValidationError was not raised for homework with due_at more than 1 month in the past.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('due_at', [])]
            self.assertIn('past_due_date', error_codes)


    def test_lesson_due_cannot_be_more_than_1_year_ahead(self):
        try:
            future_lesson = Lesson(
                subject=self.subject,
                start_time=now() + (Homework.MAX_TIMEFRAME + timedelta(days=1))
            )
            homework = Homework.objects.create(
                lesson_due=future_lesson,
                task='Some task',
            )
            self.fail('ValidationError was not raised for homework with lesson_due more than {Homework.MAX_TIMEFRAME.days} days in the future.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('lesson_due', [])]
            self.assertIn('future_limit_exceeded', error_codes)


    def test_lesson_due_cannot_be_more_than_1_month_in_the_past(self):
        try:
            old_lesson = Lesson(
                subject=self.subject,
                start_time=now() - timedelta(days=31)
            )
            homework = Homework.objects.create(
                lesson_due=old_lesson,
                task='Some task',
            )
            self.fail('ValidationError was not raised for homework with lesson_due more than one month in the past.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('lesson_due', [])]
            self.assertIn('past_due_date', error_codes)



    def test_start_time_must_be_before_due_at(self):
        '''Test creating homework with start_time not earlier than due_at fails.'''
        try:
            Homework.objects.create(
                subject=self.subject,
                start_time=now() + timedelta(days=5),
                due_at=now() + timedelta(days=3),
                task='Some task'
            )
            self.fail('ValidationError was not raised for homework with start_time after due_at.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('due_at', [])]
            self.assertIn('invalid_start_order', error_codes)


    def test_start_time_must_be_before_lesson_due(self):
        '''Test creating homework with start_time not earlier than lesson_due start fails.'''
        try:
            Homework.objects.create(
                subject=self.subject,
                start_time=now() + timedelta(days=5),
                lesson_due=Lesson(
                    subject=self.subject,
                    start_time=now() + timedelta(days=3),
                ),
                task='Some task'
            )
            self.fail('ValidationError was not raised for homework with start_time after due_at.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('lesson_due', [])]
            self.assertIn('invalid_start_order', error_codes)


    def test_lesson_given_start_time_must_be_before_due_at(self):
        '''Test creating homework with lesson_given start_time not earlier than due_at fails.'''
        try:
            Homework.objects.create(
                lesson_given=self.lesson_due,
                due_at=now() - timedelta(days=2),
                task='Some task'
            )
            self.fail('ValidationError was not raised for homework with lesson_given start_time after due_at.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('due_at', [])]
            self.assertIn('invalid_start_order', error_codes)


    def test_lesson_given_start_time_must_be_before_lesson_due(self):
        '''Test creating homework with lesson_given start_time not earlier than lesson_due fails.'''
        try:
            Homework.objects.create(
                lesson_given=self.lesson_due,
                lesson_due=Lesson(
                    subject=self.subject,
                    start_time=now() - timedelta(days=2)
                ),
                task='Some task'
            )
            self.fail('ValidationError was not raised for lesson_given start_time after due_at.')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('lesson_due', [])]
            self.assertIn('invalid_start_order', error_codes)


    def test_completion_percentage_validation(self):
        '''Test creating homework completion percentage not in [0, 100] fails.'''
        for invalid_value in [-10, 110]:
            try:
                Homework.objects.create(
                    subject=self.subject,
                    task='Some task',
                    completion_percent=invalid_value
                )
                self.fail(f'ValidationError was not raised for homework with invalid completion percentage: {invalid_value}')
            except ValidationError as e:
                error_codes = [err.code for err in e.error_dict.get('completion_percent', [])]
                self.assertIn('invalid_completion_percent', error_codes)

    
    def test_task_max_length(self):
        '''Test creating homework with task exciding max allowed length fails'''
        long_task = 'A' * (Homework.MAX_TASK_LENGTH + 1)
        try:
            homework = Homework.objects.create(
                subject=self.subject,
                lesson_due=self.lesson_due,
                task=long_task
            )
            self.fail('ValidationError was not raised when creating homework with task exciding max allowed length')
        except ValidationError as e:
            self.assertIn('task', e.error_dict)