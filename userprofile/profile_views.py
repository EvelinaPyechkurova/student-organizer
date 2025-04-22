from django.contrib.auth.models import User
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
    

class ProfileUpdateView(UpdateView):
    model = User

class ProfileDetailView(DetailView):
    model = User

class ProfileDeleteView(DeleteView):
    model = User
