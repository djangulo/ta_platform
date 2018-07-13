from django.urls import path

from .views import ApplicationView

app_name = 'applications'
urlpatterns = [
    path('', ApplicationView.as_view(), name='apply'),
]
