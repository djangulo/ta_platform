"""Accounts forms module."""
from math import floor
from django import forms
from django.db.models import Q
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape, html_safe, mark_safe, format_html
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Field,
    Fieldset,
    HTML,
    Button,
    Layout,
    Submit,
    Div,
)
from accounts.models import AreaCode, PhoneNumber, NationalId, Profile, User, reduce_to_alphanum
from accounts.tokens import verify_token_generator, reset_token_generator
from admin_console.models import CityTown, Address

EIGHTEEN_YEARS_AGO = (timezone.now() - timezone.timedelta(days=((365*18)+5))
                      ).date()
EIGHTEEN_YEARS_AGO_STR = EIGHTEEN_YEARS_AGO.strftime('%m/%d/%Y')

class NationalIdForm(forms.ModelForm):
    national_id_type = forms.ChoiceField(label=_('ID Type'), required=True,
                                         choices=NationalId.ID_TYPE_CHOICES)
    national_id_number = forms.CharField(label=_('ID Number'), required=True)



class RegistrationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    first_names = forms.CharField(label=_('First names'), required=True)
    last_names = forms.CharField(label=_('Last names'), required=True)
    email = forms.EmailField(label=_('Email'), required=True)
    username = forms.CharField(label=_('Username'), required=True)
    accepted_tos = forms.BooleanField(label=_('Accept Terms of Service'),
                                      required=True,)
    birth_date = forms.DateField(label=_('Birth date'),
                                      required=True,)
    national_id_type = forms.ChoiceField(label=_('ID Type'), required=True,
                                         choices=NationalId.ID_TYPE_CHOICES)
    national_id_number = forms.CharField(label=_('ID Number'), required=True)
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = (
            'first_names',
            'last_names',
            'email',
            'username',
            'birth_date',
            'national_id_type',
            'national_id_number',
            'accepted_tos',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-registration-form'
        self.helper.form_class = 'needs-validation'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('accounts:register')
        self.helper.html5_required = False
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                _('{{ COMPANY_NAME }}: Register'),
                Div(
                    Field('first_names', id='first-names',
                          wrapper_class='col-sm-12 col-md-6 mb-3'),
                    Field('last_names', id='last-names',
                          wrapper_class='col-sm-12 col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Div(
                    Field('email', id='email',
                          wrapper_class='col-sm-12 col-md-6 mb-3'),
                    Field('username', id='username',
                          wrapper_class='col-sm-12 col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Div(
                    Field(
                        'birth_date',
                        placeholder='mm/dd/yyyy',
                        css_class='datepicker',
                        wrapper_class='col-sm-12 col-md-3 mb-3'
                    ),
                    Field(
                        'national_id_type',
                        css_class='dropdown',
                        wrapper_class='col-sm-12 col-md-3 mb-3'
                    ),
                    Field(
                        'national_id_number',
                        placeholder='000-0000000-0',
                        wrapper_class='col-sm-12 col-md-6 mb-3'
                    ),

                    css_class='form-row'
                ),
                Div(
                    Field(
                        'password1',
                        id='password1',
                        data_toggle='tooltip',
                        data_placement='top',
                        data_html="true",
                        title=password_validation.password_validators_help_text_html(),
                        wrapper_class='col-sm-12 col-md-6 mb-3'
                    ),
                    Field(
                        'password2',
                        id='password2',
                        data_toggle='tooltip',
                        data_placement='top',
                        data_html="true",
                        title=_('Enter the same password as before, for verification.'),
                        wrapper_class='col-sm-12 col-md-6 mb-3'
                    ),
                    css_class='form-row'
                ),
                Div(
                    Field(
                        'accepted_tos',
                        template='prettycheckbox_fill.html',
                        label=_('I have read and accepted the Terms of Service.'),
                        wrapper_class='mb-2',
                    ),
                    css_class='form-row'
                ),
                Div(
                    ButtonHolder(
                        Submit('submit', _('Submit'), css_class='button white')
                    ),
                    css_class='form-row'
                ),
            ),
        )
        # pylint: disable=E1101
        # if self._meta.model.USERNAME_FIELD in self.fields:
        #     self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
        # for testing only

        email_message.send()

    def get_inactive_users(self, username):
        """Given an username, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        inactive_users = User.objects.filter(**{
            'username__iexact': username,
            'is_active': False,
        })
        return (u for u in inactive_users if u.has_usable_password())

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean_national_id_number(self):
        natid = reduce_to_alphanum(
            self.cleaned_data.get('national_id_number')
        )
        if NationalId.objects.filter(id_number=natid).exists():
            raise forms.ValidationError(
                _('This National ID already exists.'),
                code='national_id_exists',
            )
        return natid

    def clean_birth_date(self):
        # cleaned_data = super(RegistrationForm, self).clean()
        birth_date = self.cleaned_data.get('birth_date')
        # import pdb; pdb.set_trace()
        if settings.ENFORCE_MIN_AGE:
            min_age = (
                timezone.now() - timezone.timedelta(days=(
                    365*settings.MINIMUM_AGE_ALLOWED +
                    floor(settings.MINIMUM_AGE_ALLOWED / 4)
                ))
            ).date()
            if min_age < birth_date:
                raise forms.ValidationError(
                    _('You must be %(value)s years old to enroll.'),
                    code='age_restricted',
                    params={'value': settings.MINIMUM_AGE_ALLOWED},
                )
        return birth_date


    # def clean(self, *args, **kwargs):

    def save(self, domain_override=None,
             subject_template_name='accounts/registration_subject.txt',
             email_template_name='accounts/registration_email.html',
             use_https=False, token_generator=verify_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None, commit=True):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        self.full_clean()
        if self.is_valid():
            # import pdb; pdb.set_trace()
            user = super(RegistrationForm, self).save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
            NationalId.objects.create(
                id_type=self.cleaned_data['national_id_type'],
                id_number=self.cleaned_data['national_id_number'],
                user=user,
                is_verified=False
            )
            email = self.cleaned_data['email']
            username = self.cleaned_data['username']
            for user in self.get_inactive_users(username):
                if not domain_override:
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                else:
                    site_name = domain = domain_override
                context = {
                    'email': email,
                    'domain': domain,
                    'site_name': site_name,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'user': user,
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',
                    **(extra_email_context or {}),
                }
                self.send_mail(
                    subject_template_name, email_template_name, context, from_email,
                    email, html_email_template_name=html_email_template_name,
                )
        return None


class LoginForm(auth_forms.AuthenticationForm):
    """This class merely modifies the widgets in the Django's
    AuthenticationForm"""
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # pylint: disable=E1101
        self.fields['username'].widget.attrs.update({'autofocus': True})
        self.helper = FormHelper()
        self.helper.form_id = 'id-login-form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('accounts:login')
        self.helper.html5_required = False
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Field('username', id='username',
                          wrapper_class='col-sm-12 mb-3'),
                    Field('password', id='last-names',
                          wrapper_class='col-sm-12 mb-3'),
                    HTML(_("""<p><a href="{% url 'accounts:password_reset' %}">Forgot your password?</a></p>""")),
                    css_class='form-row'
                ),
                Div(
                    ButtonHolder(
                        Submit('submit', _('Login'), css_class='btn btn-primary col-sm-12'),
                        css_class='col-sm-12'
                    ),
                    css_class='form-row'
                ),
            ),
        )


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    """This class merely modifies the widgets in the Django's
    PasswordChangeForm"""
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-password-change-form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('accounts:password_change')
        self.helper.html5_required = False
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Field('old_password', id='old-password',
                          wrapper_class='col-sm-12 mb-3'),
                    Field(
                        'new_password1',
                        id='new-password',
                        data_toggle='tooltip',
                        data_placement='top',
                        data_html="true",
                        title=password_validation.password_validators_help_text_html(),
                        wrapper_class='col-sm-12 mb-3'
                    ),
                    Field('new_password2', id='new-password-confirm',
                          wrapper_class='col-sm-12 mb-3'),                          
                    css_class='form-row'
                ),
                Div(
                    ButtonHolder(
                        Submit('submit', _('Submit'), css_class='btn btn-primary col-sm-12'),
                        Button('cancel', _('Cancel'), css_class='btn btn-default col-sm-12 mt-1'),
                        css_class='col-sm-12'
                    ),
                    css_class='form-row'
                ),
            ),
        )



class PasswordResetForm(forms.Form):
    """Own implementation of django's PasswordResetForm."""
    email_or_username = forms.CharField(label=_('Email or username'),
                                         max_length=254)
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-password-reset-form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('accounts:password_reset')
        self.helper.html5_required = False
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Field('email_or_username', id='email',
                          wrapper_class='col-sm-12 mb-3'),
                    css_class='form-row'
                ),
                Div(
                    ButtonHolder(
                        Submit('submit', _('Submit'), css_class='btn btn-primary col-sm-12'),
                        css_class='col-sm-12'
                    ),
                    css_class='form-row'
                ),
            ),
        )
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_active_users(self, email_or_username):
        """Given an email or username, return matching user(s) who should
        receive a reset.
        """
        active_users = User.objects.filter(
            Q(username=email_or_username) |
            Q(email=email_or_username),
            Q(is_active=True)
        )
        return [u for u in active_users if u.has_usable_password()]

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=reset_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        self.full_clean()
        if self.is_valid():
            email_or_username = self.cleaned_data["email_or_username"]
            for user in self.get_active_users(email_or_username):
                if not domain_override:
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                else:
                    site_name = domain = domain_override
                context = {
                    'email': user.email,
                    'domain': domain,
                    'site_name': site_name,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'user': user,
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',
                    **(extra_email_context or {}),
                }
                self.send_mail(
                    subject_template_name, email_template_name, context, from_email,
                    user.email, html_email_template_name=html_email_template_name,
                )
        return None


class PasswordSetForm(auth_forms.SetPasswordForm):
    """
    This class merely modifies the widgets in the Django's
    SetPasswordForm. Used after the user follows the link sent after
    the password reset process is initiated.
    """
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        }),
        strip=False,
    )
    def __init__(self, *args, **kwargs):
        super(PasswordSetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-password-set-form'
        self.helper.form_method = 'post'
        self.helper.html5_required = False
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(

                    Field(
                        'new_password1',
                        id='new-password',
                        data_toggle='tooltip',
                        data_placement='bottom',
                        data_html="true",
                        title=password_validation.password_validators_help_text_html(),
                        wrapper_class='col-sm-12 mb-3'
                    ),
                    Field('new_password2', id='new-password-confirm',
                          wrapper_class='col-sm-12 mb-3'),                          
                    css_class='form-row'
                ),
                Div(
                    ButtonHolder(
                        Submit('submit', _('Change my password'), css_class='btn btn-primary col-sm-6'),
                        css_class='col-sm-12'
                    ),
                    css_class='form-row'
                ),
            ),
        )

# class ConfirmPasswordForm(forms.Form):
#     password = forms.CharField(
#         label=_("Password"),
#         strip=False,
#         widget=forms.PasswordInput(attrs={'class': 'form-control'}),
#     )
#     def __init__(self, *args, **kwargs):
#         super(ConfirmPasswordForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_id = 'id-password-confirm-form'
#         self.helper.form_method = 'post'
#         self.helper.html5_required = False
#         self.helper.form_tag = True
#         self.helper.layout = Layout(
#             Fieldset(
#                 HTML("user: {{user.username}}"),
#                 Div(
#                     Field('username', id='username',
#                           wrapper_class='col-sm-12 mb-3'),
#                     Field('password', id='password',
#                           wrapper_class='col-sm-12 mb-3'),
#                     css_class='form-row'
#                 ),
#                 Div(
#                     ButtonHolder(
#                         Submit('submit', _('Go'), css_class='btn btn-primary col-sm-12'),
#                         css_class='col-sm-12'
#                     ),
#                     css_class='form-row'
#                 ),
#             ),
#         )
