from django.urls import include, path

from . import views

urlpatterns = [
    path(route='', view=views.AssessmentListView.as_view(), name='assessment_list'),
    path(route='<int:pk>', view=views.AssessmentDetailView.as_view(), name='assessment_detail'),
]
