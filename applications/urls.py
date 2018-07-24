from django.urls import path

from applications.views import create_application

app_name = 'applications'
urlpatterns = [
    path('', create_application, name='apply'),
]
