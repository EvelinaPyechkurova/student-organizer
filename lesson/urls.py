from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.LessonListView.as_view(), name='lesson_list'),
    path(route='<int:pk>/', view=views.LessonDetailView.as_view(), name='lesson_detail'),
    path(route='create/', view=views.LessonCreateView.as_view(), name='lesson_create'),
    path(route='<int:pk>/update/', view=views.LessonUpdateView.as_view(), name='lesson_update'),
    path(route='<int:pk>/delete/', view=views.LessonDeleteView.as_view(), name='lesson_delete'),
]
