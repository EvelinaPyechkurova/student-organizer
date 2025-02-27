from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Subject

class SubjectModelTests(TestCase):

    def setUp(self):
        '''Create a test user for Subject model.'''
        self.user = User.objects.create_user(username='testuser')

    def test_valid_subject_creation(self):
        SUBJECT_NAME = 'Ukrainian Literature'
        '''Test creating a valid Subject instance.'''
        subject = Subject.objects.create(user=self.user, name=SUBJECT_NAME)
        self.assertEqual(subject.user, self.user)
        self.assertEqual(subject.name, SUBJECT_NAME)

    def test_max_subject_limit(self):
        subjects = [Subject(user=self.user, name=f'Subject {i}') for i in range(Subject.MAX_SUBJECTS_PER_USER)]

        for subject in subjects:
            subject.full_clean()

        Subject.objects.bulk_create(subjects)

        try:
            subject = Subject(user=self.user, name='Extra subject')
            subject.save()
            self.fail('ValidationError was not raised when creating more subjects per user then allowed')
        except ValidationError:
            pass

    def test_name_cannot_be_blank(self):
        '''Test creating subject with blank name field fails'''
        try:
            subject = Subject.objects.create(user=self.user, name='')
            self.fail('ValidationError was not raised when creating subject with blank name field')
        except ValidationError:
            pass