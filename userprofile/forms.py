from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, RadioSelect

from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'lesson_duration', 'assessment_duration', 'notification_method',
            'receive_lesson_reminders', 'lesson_reminder_timing',
            'receive_lesson_reminders', 'assessment_reminder_timing',
            'receive_homework_reminders', 'homework_reminder_timing',
            'time_display_format'
        ]
        widgets = {
            'notification_method': RadioSelect,
            'time_display_format': RadioSelect
        }
        