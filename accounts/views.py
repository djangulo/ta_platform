# pylint: disable=W0201
"""
Accounts views module. Pertinent to each user and user account.
Included views:
 - Profile detail view
 - Account settings view
 - Registration workflow views: form, done and verify
 - Login & logout views
 - Password reset workflow views: form, done, confirm, complete
 - Password change workflow views: form, complete
"""
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.utils.translation import ugettext_lazy as _
from accounts.forms import (
    LoginForm,
    PasswordChangeForm,
    PasswordResetForm,
    PasswordSetForm,
    RegistrationForm,
)
from accounts.models import User, EmailAddress
from accounts.tokens import verify_token_generator, reset_token_generator

LOGOUT_MESSAGE = _('You have successfully logged out.')
INTERNAL_VERIFICATION_URL_TOKEN = 'verify-user'
INTERNAL_VERIFICATION_SESSION_TOKEN = '_verification_token'


class ProfileDetailView(LoginRequiredMixin, generic.DetailView):
    """
    Profile detail view. Accessible to all registered users. Higher
    level of detail granted to owner and staff.
    """
    model = User
    template_name = 'accounts/profile_detail.html'


class AccountSettingsView(LoginRequiredMixin, generic.DetailView):
    """
    Account settings view. Accessible only to owner. Staff will
    have access to modify settings here, but through the admin console
    app.
    """
    model = User
    template_name = 'accounts/account_settings.html'


class RegistrationView(generic.CreateView):
    """Registration form view. Initiates registration workflow."""
    form_class = RegistrationForm
    token_generator = verify_token_generator
    model = User

    template_name = 'accounts/registration_form.html'
    email_template_name = 'accounts/registration_email.html'
    subject_template_name = 'accounts/registration_subject.txt'
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    title = _('Register')

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:account', kwargs={
                'slug': request.user.slug,
            }))
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }

        form.save(**opts)
        return HttpResponseRedirect(reverse('accounts:register_done'))


class RegistrationDoneView(generic.TemplateView):
    """
    Simple template view to display completion of first step of
    registration process.
    """
    template_name = 'accounts/registration_done.html'


class RegistrationVerifyView(generic.TemplateView):
    """Modified django.contrib.auth.views.PasswordResetView, it's
    purpose is to verify the user via the emailed token after
    registration.
    """
    template_name = 'accounts/registration_verify.html'
    title = _('Registration complete')
    token_generator = verify_token_generator
    user = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == INTERNAL_VERIFICATION_URL_TOKEN:
                session_token = self.request.session.get(
                    INTERNAL_VERIFICATION_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    self.activate_user_and_email()
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # "verification succesful" message at a URL without
                    # the token. That avoids the possibility of leaking
                    # the token in the HTTP Referer header.
                    self.request.session[
                        INTERNAL_VERIFICATION_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token,
                        INTERNAL_VERIFICATION_URL_TOKEN
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        """
        Finds the user by the base64 encoded primary key.
        """
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'title': _('Verification unsuccessful'),
                'validlink': False,
            })
        return context

    def activate_user_and_email(self):
        """Activates user and verifies the user and the email address."""
        User.objects.filter(id=self.user.id).update(is_verified=True,
                                                    is_active=True)
        EmailAddress.objects.filter(
            email=self.user.email
        ).update(is_verified=True)


class LoginView(SuccessMessageMixin, views.LoginView):
    """This view only changes the available options in the Django's
    LoginView."""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    # success_url = reverse_lazy('home')
    success_message = _("Welcome %(username)s!")
    # redirect_authenticated_user = True


class LogoutView(views.LogoutView):
    """This view only changes the available options in the Django's
    LogoutView."""
    # template_name = 'accounts/logout.html'
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, LOGOUT_MESSAGE)
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

class PasswordResetView(views.PasswordResetView):
    """User forgot password and needs a new one. Email workflow ensues."""
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    form_class = PasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')
    token_generator = reset_token_generator

    def form_valid(self, form):
        """Allows the password_reset_done_view access once."""
        self.request.session['can_view_password_reset_done'] = True
        return super(PasswordResetView, self).form_valid(form)

    def form_invalid(self, form):
        """
        Allows the password_reset_done_view access once. Enabled on
        invalid forms so as not to leak information about which email
        addresses or usernames do exist.
        """
        self.request.session['can_view_password_reset_done'] = True
        return super(PasswordResetView, self).form_invalid(form)

class PasswordResetDoneView(views.PasswordChangeDoneView):
    """This view only changes the available options in the Django's
    PasswordChangeDoneView."""
    template_name = 'accounts/password_reset_done.html'

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if not request.session.get('can_view_password_reset_done'):
            return HttpResponseRedirect(reverse('accounts:password_reset'))
        request.session.pop('can_view_password_reset_done')
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

class PasswordResetConfirmView(views.PasswordResetConfirmView):
    """Password reset confirm view. Extended for convenience."""
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordSetForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    token_generator = reset_token_generator

    def form_valid(self, form):
        """Allows the password_reset_done_view access once."""
        self.request.session['can_view_password_reset_complete'] = True
        return super(PasswordResetConfirmView, self).form_valid(form)


class PasswordResetCompleteView(views.PasswordResetCompleteView):
    """This view only changes the available options in the Django's
    PasswordResetCompleteView."""
    template_name = 'accounts/password_reset_complete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('can_view_password_reset_complete'):
            return HttpResponseRedirect(reverse('accounts:password_reset'))
        request.session.pop('can_view_password_reset_complete')
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

class PasswordChangeView(LoginRequiredMixin, views.PasswordChangeView):
    """User voluntarily changes password."""
    template_name = 'accounts/password_change_form.html'
    form_class = PasswordChangeForm
    max_last_login_seconds = 5
    success_url = reverse_lazy('accounts:password_change_complete')


class PasswordChangeCompleteView(LoginRequiredMixin, views.PasswordResetCompleteView):
    """This view only changes the available options in the Django's
    PasswordResetCompleteView."""
    template_name = 'accounts/password_change_complete.html'
