from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
    

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile/profile_detail.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.userprofile
        context['model_name'] = 'profile'  # logical entity is "profile" even though model is User
        print(context)
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = User
