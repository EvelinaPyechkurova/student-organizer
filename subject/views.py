from django.views.generic import ListView, DetailView
from .models import Subject

class SubjectListView(ListView):
    model = Subject
    context_object_name = 'user_subjects'

    # def get_queryset(self):
    #     '''
    #     Return subjects of the user sending request
    #     '''
    #     return Subject.objects.filter(user=self.request.user)
    

class SubjectDetailView(DetailView):
    model = Subject