from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.SubjectListView.as_view(), name='list_subjects'),
]
