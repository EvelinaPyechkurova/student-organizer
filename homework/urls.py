from django.urls import include, path

from . import views

urlpatterns = [
    path(route='', view=views.HomeworkListView.as_view(), name='homework_list'),
    path(route='<int:pk>', view=views.HomeworkDetailView.as_view(), name='homework_details'),
]
