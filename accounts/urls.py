from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path(_('login/'), views.LoginView.as_view(), name='login'),
    path(_('logout/'), views.LogoutView.as_view(), name='logout'),
    path(_('register/'), views.RegistrationView.as_view(), name='register'),
    path(_('register/done/'), views.RegistrationDoneView.as_view(),
         name='register_done'),
    path(_('register/verify/<uidb64>/<token>/'),
         views.RegistrationVerifyView.as_view(),
         name='register_verify'),
    path(_('register/complete/'),
         views.RegistrationCompleteView.as_view(),
         name='register_complete'),
    path(_('password/change/'),
         views.PasswordChangeView.as_view(),
         name='password_change'),
    path(_('password/change/done/'),
         views.PasswordChangeCompleteView.as_view(),
         name='password_change_complete'),
    path(_('password/reset/'),
         views.PasswordResetView.as_view(),
         name='password_reset'),
    path(_('password/reset/done/'),
         views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path(_('password/reset/confirm/<uidb64>/<token>/'),
         views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path(_('password/reset/complete/'),
         views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path(_('<slug:slug>/'),
         views.ProfileDetailView.as_view(),
         name='profile'),
    path(_('<slug:slug>/my-account'),
         views.AccountDetailView.as_view(),
         name='account'),
]
