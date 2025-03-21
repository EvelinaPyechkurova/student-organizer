from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.SubjectListView.as_view(), name='subject_list'),
    path(route='<int:pk>', view=views.SubjectDetailView.as_view(), name='subject_detail'),
    path(route='create', view=views.SubjectCreateView.as_view(), name='subject_create'),
    path(route='<int:pk>/update', view=views.SubjectUpdateView.as_view(), name='subject_update'),
    path(route='<int:pk>/delete', view=views.SubjectDeleteView.as_view(), name='subject_delete'),
]
