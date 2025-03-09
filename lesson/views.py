from django.views.generic import ListView, DetailView
from .models import Lesson

class LessonListView(ListView):
    model = Lesson
    context_object_name = 'user_lessons'

    # def get_queryset(self):
    #     '''
    #     Return lessons of the user sending request.
    #     '''
    #     return Lesson.objects.filter(subject__user=self.request.user)
    

class LessonDetailView(DetailView):
    model = Lesson