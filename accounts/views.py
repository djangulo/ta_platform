from django import forms
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.template import loader
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
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
from accounts.models import User, Profile, NationalId
from accounts.tokens import verify_token_generator

# if settings.BRANDING:
#     COMPANY_NAME = settings.BRAND_DICT.get('COMPANY_NAME')
# else:
#     COMPANY_NAME = 'MyCo DR'
LOGOUT_MESSAGE = _('You have successfully logged out.')


UserModel = get_user_model()

INTERNAL_VERIFICATION_URL_TOKEN = 'verify-user'
INTERNAL_VERIFICATION_SESSION_TOKEN = '_verification_token'

class ProfileDetailView(generic.DetailView):
    model = User
    template_name = 'accounts/profile_detail.html'


class RegistrationView(generic.CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:register_done')
    token_generator = verify_token_generator
    model = User

    template_name = 'accounts/registration_form.html'
    email_template_name = 'accounts/registration_email.html'
    subject_template_name = 'accounts/registration_subject.txt'
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    title = _('Register')

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
        return HttpResponseRedirect(reverse_lazy('accounts:register_done'))


class RegistrationDoneView(generic.TemplateView):
    template_name = 'accounts/registration_done.html'


class RegistrationVerifyView(generic.TemplateView):
    """Modified django.contrib.auth.views.PasswordResetView, it's
    purpose is to verify the user via the emailed token after
    registration.
    """
    template_name = 'accounts/registration_complete.html'
    title = _('Registration complete')
    token_generator = verify_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if self.token_generator.check_token(self.user, token):
                # Store the token in the session and redirect to the
                # "verification succesful" message at a URL without
                # the token. That avoids the possibility of leaking
                # the token in the HTTP Referer header.
                self.request.session[INTERNAL_VERIFICATION_SESSION_TOKEN] = token
                redirect_url = self.request.path.replace(
                    token,
                    INTERNAL_VERIFICATION_URL_TOKEN
                )
                User.objects.filter(id=self.user.id).update(is_verified=True,
                                                            is_active=True)
                return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Verification unsuccessful'),
                'validlink': False,
            })
        return context

class RegistrationCompleteView(views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'



class LoginView(views.LoginView):
    """This view only changes the available options in the Django's
    LoginView."""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')
    redirect_authenticated_user = True


class LogoutView(SuccessMessageMixin, views.LogoutView):
    """This view only changes the available options in the Django's
    LogoutView."""
    template_name = 'accounts/logout.html'
    next_page = reverse_lazy('home')
    success_message = LOGOUT_MESSAGE


class PasswordResetView(views.PasswordResetView):
    """User forgot password and needs a new one. Email workflow ensues."""
    # TODO: edit the email template
    # TODO: create email editor for users
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    form_class = PasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetDoneView(views.PasswordChangeDoneView):
    """This view only changes the available options in the Django's
    PasswordChangeDoneView."""
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordSetForm
    success_url = reverse_lazy('accounts:password_reset_complete')


class PasswordResetCompleteView(views.PasswordResetCompleteView):
    """This view only changes the available options in the Django's
    PasswordResetCompleteView."""
    template_name = 'accounts/password_reset_complete.html'


class PasswordChangeView(views.PasswordChangeView):
    """User voluntarily changes password."""
    template_name = 'accounts/password_change_form.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_complete')


class PasswordChangeCompleteView(views.PasswordResetCompleteView):
    """This view only changes the available options in the Django's
    PasswordResetCompleteView."""
    template_name = 'accounts/password_change_complete.html'

