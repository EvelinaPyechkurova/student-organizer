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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homework = context['homework']

        context['source'] = homework.lesson_given or homework.lesson_due or homework
        context['start_time'] = homework.start_time or homework.lesson_given.start_time
        context['due_at'] = homework.due_at or homework.lesson_given.start_time

        return context
