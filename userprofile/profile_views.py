from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView, DeleteView
from django.urls import reverse_lazy

from utils.mixins import UserObjectMixin

from .forms import UserUpdateForm, ProfileUpdateForm
    

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


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'profile/profile_update.html'
    success_url = reverse_lazy('profile_detail')
    cancel_link = reverse_lazy('profile_detail')

    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)

        return render(
            request, 
            self.template_name,
            {
                'user_form': user_form,
                'profile_form': profile_form,
                'cancel_link': self.cancel_link
            }
        )
    
    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(self.success_url)
        
        return render(
            request, 
            self.template_name,
            {
                'user_form': user_form,
                'profile_form': profile_form,
                'cancel_link': self.cancel_link
            }
        )


class ProfileDeleteView(LoginRequiredMixin, UserObjectMixin, DeleteView):
    model = User
    template_name = 'profile/profile_confirm_delete.html'
    success_url = reverse_lazy('user_login')
    cancel_link = reverse_lazy('profile_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_link'] = self.cancel_link
        return context
