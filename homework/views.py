from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Homework

class HomeworkListView(ListView):
    model = Homework
    context_object_name = 'user_homework'

    # def get_queryset(self):
    #     '''
    #     Return homework of the user sending requests
    #     '''
    #     user = self.request.user
    #     return Homework.objects.filter(
    #         Q(subject__user=user) | 
    #         (Q(lesson_given__subject__user=user) | Q(lesson_due__subject__user=user))
    #     )
    

class HomeworkDetailView(DetailView):
    model = Homework
