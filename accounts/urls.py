from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('register/done/', views.RegistrationDoneView.as_view(),
         name='register_done'),
    path('register/verify/<uidb64>/<token>/',
         views.RegistrationVerifyView.as_view(), name='register_verify'),
    path('register/complete/', views.RegistrationCompleteView.as_view(),
         name='register_complete'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', views.PasswordChangeCompleteView.as_view(), name='password_change_complete'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile'),
]