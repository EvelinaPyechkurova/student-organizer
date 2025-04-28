from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.HomeworkListView.as_view(), name='homework_list'),
    path(route='<int:pk>/', view=views.HomeworkDetailView.as_view(), name='homework_detail'),
    path(route='create/', view=views.HomeworkCreateView.as_view(), name='homework_create'),
    path(route='<int:pk>/update/', view=views.HomeworkUpdateView.as_view(), name='homework_update'),
    path(route='<int:pk>/delete/', view=views.HomeworkDeleteView.as_view(), name='homework_delete'),
]
