from django.urls import path

from admin_console import views

app_name = 'admin_console'
urlpatterns = [
    path('', views.AdminHomeView.as_view(), name='home'),
    path('accounts/', views.AdminAccountsView.as_view(), name='accounts'),
    path('accounts/groups/', views.GroupListView.as_view(), name='group-list'),
    path('accounts/groups/add/', views.GroupCreateView.as_view(), name='group-add'),
    path('accounts/groups/<slug:slug>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('accounts/groups/<slug:slug>/edit/', views.GroupUpdateView.as_view(), name='group-edit'),
    path('accounts/users/', views.UserListView.as_view(), name='user-list'),
    path('accounts/users/add/', views.UserCreateView.as_view(), name='user-add'),
    path('accounts/users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('accounts/users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user-edit'),
    path('accounts/permissions/', views.GroupListView.as_view(), name='permission-list'),
    path('accounts/permissions/add/', views.GroupListView.as_view(), name='permission-list'),
    path('accounts/permissions/<int:pk>/', views.GroupDetailView.as_view(), name='permission-detail'),
    path('accounts/permissions/<int:pk>/edit/', views.GroupUpdateView.as_view(), name='permission-edit'),
    # path('success', ApplicationSuccessView.as_view(), name='success'),
]
