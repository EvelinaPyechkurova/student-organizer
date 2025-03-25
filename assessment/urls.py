from django.urls import include, path

from . import views

urlpatterns = [
    path(route='', view=views.AssessmentListView.as_view(), name='assessment_list'),
    path(route='<int:pk>', view=views.AssessmentDetailView.as_view(), name='assessment_detail'),
    path(route='create', view=views.AssessmentCreateView.as_view(), name='assessment_create'),
    path(route='<int:pk>/update', view=views.AssessmentUpdateView.as_view(), name='assessment_update'),
    path(route='<int:pk>/delete', view=views.AssessmentDeleteView.as_view(), name='assessment_delete'),
]
