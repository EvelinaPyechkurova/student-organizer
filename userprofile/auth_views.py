from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import UserRegisterForm
from .models import UserProfile

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_message = 'Congratulations! You can now costumize your Organizer :)'
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        responce = super().form_valid(form)
        UserProfile.objects.create(user=self.object)
        return responce