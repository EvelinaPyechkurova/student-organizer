from . import profile_views
from django.urls import path

urlpatterns = [
    path('', view=profile_views.ProfileDetailView.as_view(), name='profile_detail'),
    path('update', view=profile_views.ProfileUpdateView.as_view(), name='profile_update'),
    path('delete', view=profile_views.ProfileDeleteView.as_view(), name='profile_delete'),
]