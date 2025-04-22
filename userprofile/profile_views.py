from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
    

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = User
