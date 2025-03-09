from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.LessonListView.as_view(), name='lesson_list'),
    path(route='<int:pk>', view=views.LessonDetailView.as_view(), name='lesson_details'),
]
