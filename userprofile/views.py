from django.contrib.auth.models import User
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import UserRegisterForm

class ProfileDetailView(DetailView):
    pass

class ProfileUpdateView(UpdateView):
    pass

class ProfileDeleteView(DeleteView):
    pass

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_message = 'Congratulations! You can now costumize your Orginizer :)'
    from django.contrib.auth.models import User
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from .forms import UserRegisterForm

class ProfileDetailView(DetailView):
    pass

class ProfileUpdateView(UpdateView):
    pass

class ProfileDeleteView(DeleteView):
    pass

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_message = 'Congratulations! You can now costumize your Orginizer :)'
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('subject_list') # TEMP
