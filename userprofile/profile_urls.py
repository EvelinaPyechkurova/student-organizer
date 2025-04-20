from . import views
from django.urls import path

urlpatterns = [
    path('', view=views.ProfileDetailView.as_view(), name='user_profile_detail'),
    path('', view=views.ProfileUpdateView.as_view(), name='user_profile_update'),
    path('', view=views.ProfileDeleteView.as_view(), name='user_profile_delete'),
]