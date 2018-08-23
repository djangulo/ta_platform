"""Accounts forms module."""
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import (
    ButtonHolder,
    Field,
    Fieldset,
    HTML,
    Layout,
    Submit,
    Div,
    MultiField,
)
from accounts.models import NationalId, Profile, User, reduce_to_alphanum
from accounts.tokens import verify_token_generator
from admin_console.models import CityTown, AreaCode, Address, PhoneNumber

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
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
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
                        wrapper_class='col-sm-12 col-md-6 mb-3'
                    ),

                    css_class='form-row'
                ),
                Div(
                    Field('password1', id='password1',
                          wrapper_class='col-sm-12 col-md-6 mb-3'),
                    Field('password2', id='password2',
                          wrapper_class='col-sm-12 col-md-6 mb-3'),
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
                        Submit('submit', 'Submit', css_class='button white')
                    ),
                    css_class='form-row'
                ),
            ),
        )
        # pylint: disable=E1101
        # if self._meta.model.USERNAME_FIELD in self.fields:
        #     self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})


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
        if natid:
            if NationalId.objects.filter(id_number=natid).exists():
                raise forms.ValidationError(_('This National ID already exists.'))
        return natid

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

    def get_inactive_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = User.objects.filter(**{
            '%s__iexact' % User.get_email_field_name(): email,
            'is_active': False,
        })
        return (u for u in active_users if u.has_usable_password())

    def clean(self, *args, **kwargs):
        cleaned_data = super(RegistrationForm, self).clean(*args, **kwargs)
        if settings.APP_SETTINGS['accounts']['ENFORCE_MIN_AGE']:
            if EIGHTEEN_YEARS_AGO < cleaned_data.get('birth_date'):
                raise forms.ValidationError('You must be 18 years old to enroll.')

    def save(self, domain_override=None,
             subject_template_name='accounts/registrationo_subject.txt',
             email_template_name='accounts/registration_email.html',
             use_https=False, token_generator=verify_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None, commit=True):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
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
        email = self.cleaned_data["email"]
        for user in self.get_inactive_users(email):
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



# class AdressForm(forms.ModelForm):
#     adress_line_one = forms.CharField(label=_('Address line one'),
#                                       max_length=150,
#                                       required=True,
#                                       widget=forms.TextInput(attrs={
#                                           'class': 'form-control',
#                                       }))
#     adress_line_two = forms.CharField(label=_('Address line two'),
#                                       max_length=150,
#                                       required=True,
#                                       widget=forms.TextInput(attrs={
#                                           'class': 'form-control',
#                                       }))
#     body = forms.CharField(label=_('Area code'),
#                                 max_length=3,
#                                 required=True,
#                                 widget=forms.TextInput(attrs={
#                                     'class': 'form-control',
#                                     'placeholder': '809',
#                                 }))
#     class Meta:
#         model = Address
#         fields = ('area_code', 'body',)


# class RegistrationForm(forms.ModelForm):
#     error_messages = {
#         'password_mismatch': _("The two password fields didn't match."),
#     }
#     first_names = forms.CharField(label=_('First names'), required=True,
#                                   widget=forms.TextInput(attrs={
#                                       'class': 'form-control'}))
#     last_names = forms.CharField(label=_('Last names'), required=True,
#                                  widget=forms.TextInput(attrs={
#                                      'class': 'form-control'}))
#     natid_type = forms.ChoiceField(choices=NationalId.ID_TYPE_CHOICES,
#                                          widget=forms.Select(attrs={
#                                              'class': 'form-control dropdown'}))
#     natid_number = forms.CharField(required=True,
#                                          widget=forms.TextInput(attrs={
#                                              'placeholder': _('Enter your national ID here'),
#                                              'class': 'form-control',
#                                          }))
#     email = forms.EmailField(required=True,
#                              widget=forms.EmailInput(attrs={
#                                  'class': 'form-control',
#                              }))
#     username = forms.CharField(required=True,
#                                widget=forms.TextInput(attrs={
#                                    'class': 'form-control',
#                                }))
#     accepted_eula = forms.BooleanField(required=True,
#                                        widget=forms.CheckboxInput(attrs={
#                                            'class': 'form-check-input',
#                                        }))
#     password1 = forms.CharField(
#         label=_("Password"),
#         strip=False,
#         widget=forms.PasswordInput,
#         help_text=password_validation.password_validators_help_text_html(),
#     )
#     password2 = forms.CharField(
#         label=_("Password confirmation"),
#         widget=forms.PasswordInput,
#         strip=False,
#         help_text=_("Enter the same password as before, for verification."),
#     )
#     class Meta:
#         model = User
#         fields = ('email', 'username', 'accepted_eula',)

#     def __init__(self, *args, **kwargs):
#         super(RegistrationForm, self).__init__(*args, **kwargs)
#         if self._meta.model.USERNAME_FIELD in self.fields:
#             self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})


#     def clean_password2(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError(
#                 self.error_messages['password_mismatch'],
#                 code='password_mismatch',
#             )
#         return password2

#     def _post_clean(self):
#         super()._post_clean()
#         # Validate the password after self.instance is updated with form data
#         # by super().
#         password = self.cleaned_data.get('password2')
#         if password:
#             try:
#                 password_validation.validate_password(password, self.instance)
#             except forms.ValidationError as error:
#                 self.add_error('password2', error)

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user

class LoginForm(auth_forms.AuthenticationForm):
    """This class merely modifies the widgets in the Django's
    AuthenticationForm"""
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.EmailInput(attrs={'class': 'form-control'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    """This class merely modifies the widgets in the Django's
    PasswordChangeForm"""
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'autofocus': True})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})


class PasswordResetForm(auth_forms.PasswordResetForm):
    """This class merely modifies the widgets in the Django's
    PasswordChangeForm"""
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={'class': 'form-control', 'autofocus': True})


class PasswordSetForm(auth_forms.SetPasswordForm):
    """This class merely modifies the widgets in the Django's
    SetPasswordForm"""
    def __init__(self, *args, **kwargs):
        super(PasswordSetForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'autofocus': True})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
