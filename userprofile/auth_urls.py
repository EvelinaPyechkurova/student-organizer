from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path(route='login/', view=LoginView.as_view(), name='user_login'),
    path(route='logout/', view=LogoutView.as_view(), name='user_logout'),
    # path(route='register/', view=views.RegistrationView.as_view(), name='user_register'),
]
