from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Homework

class HomeworkListView(ListView):
    model = Homework
    context_object_name = 'user_homework'

    def get_queryset(self):
        '''
        Return homework of the user sending requests
        '''
        # user = self.request.user
        # queryset = Homework.objects.filter(derived_subject__user=user)

        queryset = Homework.objects.with_derived_fields()

        return queryset
    

class HomeworkDetailView(DetailView):
    model = Homework

