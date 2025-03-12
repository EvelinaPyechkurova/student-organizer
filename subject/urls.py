from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.SubjectListView.as_view(), name='subject_list'),
    path(route='<int:pk>', view=views.SubjectDetailView.as_view(), name='subject_detail'),
]
