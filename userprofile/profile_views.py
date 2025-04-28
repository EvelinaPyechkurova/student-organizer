from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy

from utils.mixins import UserObjectMixin
    

class ProfileDetailView(LoginRequiredMixin, UserObjectMixin, DetailView):
    model = User
    template_name = 'profile/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.userprofile
        context['profile'] = profile
        context['model_name'] = 'profile'  # logical entity is "profile" even though model is User
        context['reminders'] = [
            {
                'label': 'Lesson reminders',
                'enabled': profile.recieve_lesson_remainders,
                'timing': profile.lesson_remainder_timing,
            },
            {
                'label': 'Assessment reminders',
                'enabled': profile.recieve_assessment_remainders,
                'timing': profile.assessment_remainder_timing,
            },
            {
                'label': 'Homework reminders',
                'enabled': profile.recieve_homework_remainders,
                'timing': profile.homework_remainder_timing,
            },
        ]
        return context


class ProfileUpdateView(LoginRequiredMixin, UserObjectMixin, UpdateView):
    model = User


class ProfileDeleteView(LoginRequiredMixin, UserObjectMixin, DeleteView):
    model = User
    template_name = 'profile/profile_confirm_delete.html'
    success_url = reverse_lazy('user_login')
