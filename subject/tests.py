from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Subject

class SubjectModelTests(TestCase):

    SUBJECT_NAME = 'Ukrainian Literature'
    VALID_IMAGE_URL = 'https://example.com/image.png'
    INVALID_IMAGE_URL = 'invalid-url'

    def setUp(self):
        '''Create a test user for Subject model.'''
        self.user = User.objects.create_user(username='testuser')


    def test_valid_subject_creation(self):
        '''Test creating a valid Subject instance.'''
        subject = Subject.objects.create(user=self.user, name=self.SUBJECT_NAME, image_url=self.VALID_IMAGE_URL)
        self.assertEqual(subject.user, self.user)
        self.assertEqual(subject.name, self.SUBJECT_NAME)
        self.assertEqual(subject.image_url, self.VALID_IMAGE_URL)


    def test_max_subject_limit(self):
        '''Test creating more subjects that allowed for user fails'''
        subjects = [Subject(user=self.user, name=f'Subject {i}') for i in range(Subject.MAX_SUBJECTS_PER_USER)]

        Subject.objects.bulk_create(subjects)

        try:
            subject = Subject(user=self.user, name='Extra subject')
            subject.full_clean()
            self.fail('ValidationError was not raised when creating more subjects per user than allowed')
        except ValidationError as e:
            error_codes = [err.code for err in e.error_dict.get('__all__', [])]
            self.assertIn('max_subjects_reached', error_codes)


    def test_name_cannot_be_blank(self):
        '''Test creating subject with blank name field fails'''
        try:
            subject = Subject.objects.create(user=self.user, name='')
            self.fail('ValidationError was not raised when creating subject with blank name field')
        except ValidationError:
            pass


    def test_name_max_length(self):
        '''Test creating subject with name exciding max allowed length fails'''
        long_name = 'A' * (Subject.MAX_SUBJECT_NAME_LENGTH + 1)
        try:
            subject = Subject.objects.create(user=self.user, name=long_name)
            self.fail('ValidationError was not raised when creating subject with name exciding max allowed length')
        except ValidationError:
            pass


    def test_invalid_image_url(self):
        '''Test creating a Subject instance with invalid image URL fails.'''
        try:
            subject = Subject.objects.create(user=self.user, name=self.SUBJECT_NAME, image_url=self.INVALID_IMAGE_URL)
            self.fail('ValidationError was not raised when creating subject with invalid image url')
        except ValidationError:
            pass