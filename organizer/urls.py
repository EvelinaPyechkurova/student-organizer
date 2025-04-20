from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('subjects/', include('subject.urls')),
    path('lessons/', include('lesson.urls')),
    path('assessments/', include('assessment.urls')),
    path('homework/', include('homework.urls')),
    path('auth/', include('userprofile.auth_urls')),
    path('profile/', include('userprofile.profile_urls')),
]
