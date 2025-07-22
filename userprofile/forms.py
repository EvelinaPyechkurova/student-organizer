from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, RadioSelect

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
        fields = [
            'lesson_duration', 'assessment_duration', 'notification_method',
            'recieve_lesson_reminders', 'lesson_reminder_timing',
            'recieve_assessment_reminders', 'assessment_reminder_timing',
            'recieve_homework_reminders', 'homework_reminder_timing'
        ]
        widgets = {
            'notification_method': RadioSelect
        }
        