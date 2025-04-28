from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['lesson_duration', 'assessment_duration', 'recieve_lesson_remainders',
                  'lesson_remainder_timing', 'recieve_assessment_remainders', 'assessment_remainder_timing',
                  'recieve_homework_remainders', 'homework_remainder_timing']
