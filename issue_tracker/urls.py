from django.urls import path, re_path

from issue_tracker import views

app_name = 'issue_tracker'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
]
