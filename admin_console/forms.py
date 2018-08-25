from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget
from django.contrib.auth.models import Permission
from django.utils.translation import gettext as _

import admin_console.models as admin_models
import accounts.models as accounts_models


class AdminUserCreationForm(forms.ModelForm):
    first_names = forms.CharField(label=_('First names'), required=True,
                                  widget=forms.TextInput(attrs={
                                      'class': 'form-control'}))
    last_names = forms.CharField(label=_('Last names'), required=True,
                                 widget=forms.TextInput(attrs={
                                     'class': 'form-control'}))
    email = forms.EmailField(label=_('Email'), required=True,
                             widget=forms.EmailInput(attrs={
                                 'class': 'form-control',
                             }))
    username = forms.CharField(label=_('Username'), required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                               }))

    class Meta:
        model = accounts_models.User
        fields = (
            'first_names',
            'last_names',
            'email',
            'username',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # pylint: disable=E1101
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(user.make_random_password)
        if commit:
            user.save()
        return user


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        widget=FilteredSelectMultiple('Permissions', is_stacked=False),
        queryset=Permission.objects.all()
    )
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    class Meta:
        model = accounts_models.ModGroup
        fields = (
            'name',
            'permissions',
        )

    class Media:
        js = ('/admin-contrib/jsi18n/',)


class PhoneNumberForm(forms.ModelForm):
    area_code = forms.ModelChoiceField(
        label=_('Area code'),
        required=True,
        queryset=admin_models.AreaCode.objects.filter(
            display_in_form=True
        ),
        widget=forms.Select(attrs={
            'class': 'form-control dropdown',
        }),
    )
    phone_number = forms.CharField(label=_('Phone number'),
                                max_length=3,
                                required=True,
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': '000-0000',
                                }))
    class Meta:
        model = admin_models.PhoneNumber
        fields = ('area_code', 'phone_number',)


class PhoneNumberAdminForm(PhoneNumberForm):
    user = forms.ModelChoiceField(
        label=_('User'),
        required=True,
        queryset=accounts_models.User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control dropdown',
        })
    )
    class Meta(PhoneNumberForm.Meta):
        fields = ('area_code', 'phone_number', 'user')


class AreaCodeForm(forms.ModelForm):
    prefix = forms.ChoiceField(label=_('Prefix'),
                               required=True,
                               choices=admin_models.AreaCode.PREFIX_CHOICES,
                               widget=forms.Select(attrs={
                                   'class': 'form-control dropdown',
                               }))
    code = forms.CharField(label=_('Code'),
                           max_length=5,
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    country = forms.ModelChoiceField(
        label=_('Country'),
        required=True,
        queryset=admin_models.Country.objects.filter(
            display_in_form=True
        ),
        widget=forms.Select(attrs={
            'class': 'form-control dropdown',
        }),
    )
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.AreaCode
        fields = ('prefix', 'code', 'country', 'display_in_form')


class CityTownForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.CityTown
        fields = ('name', 'display_in_form', )


class CitySectorForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.CitySector
        fields = ('name', 'display_in_form', )


class StateProvinceRegionForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    country = forms.ModelChoiceField(
        label=_('Country'),
        required=True,
        queryset=admin_models.Country.objects.filter(
            display_in_form=True
        ),
        widget=forms.Select(attrs={
            'class': 'form-control dropdown',
        }),
    )
    class Meta:
        model = admin_models.StateProvinceRegion
        fields = ('name', 'display_in_form', 'country',)


class CallCenterForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.CallCenter
        fields = ('name', 'display_in_form', )


class AreaOfExpertiseForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.AreaOfExpertise
        fields = ('name', 'display_in_form', )


class ApplicationStatusForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.ApplicationStatus
        fields = ('name', 'display_in_form', )


class DeclinedReasonForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.DeclinedReason
        fields = ('name', 'display_in_form', )

class ShiftForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.Shift
        fields = ('name', 'display_in_form', )


class LanguageForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    class Meta:
        model = admin_models.Language
        fields = ('name', 'display_in_form', )


class CareerForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    industry = forms.CharField(label=_('Industry'),
                               required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                               }))
    institution = forms.ModelChoiceField(
        label=_('Institution'),
        required=True,
        queryset=admin_models.Institution.objects.filter(
            display_in_form=True
        ),
        widget=forms.Select(attrs={
            'class': 'form-control dropdown',
        }),
    )
    class Meta:
        model = admin_models.Career
        fields = ('name', 'display_in_form', )

class InstitutionForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),
                           required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                           }))
    display_in_form = forms.BooleanField(label=_('Display in form'),
                                         required=True,
                                         widget=forms.CheckboxInput(attrs={
                                             'class': 'form-check-input',
                                         }))
    short_name = forms.CharField(label=_('Industry'),
                               required=True,
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                               }))
    class Meta:
        model = admin_models.Institution
        fields = ('name', 'display_in_form', )
# PersonFormSet = forms.inlineformset_factory(parent_model=User,
#                                             model=Profile,
#                                             exclude=('email', 'password',),
#                                             extra=1,
#                                             widgets={
#     'first_names': forms.TextInput(attrs={'class': 'form-control'}),
#     'last_names': forms.TextInput(attrs={'class': 'form-control'}),
#     'natid_type': forms.Select(attrs={'class': 'form-control dropdown'}),
#     'natid': forms.TextInput(attrs={'class': 'form-control'}),
#     'email': forms.EmailInput(attrs={'class': 'form-control'}),
#     'display_name': forms.TextInput(attrs={'class': 'form-control'}),
#     'primary_phone': forms.TextInput(attrs={
#         'class': 'form-control',
#         'placeholder': '(809)555-5555',
#     }),
#     'secondary_phone': forms.TextInput(attrs={
#         'class': 'form-control',
#         'placeholder': '(809)555-5555',
#     }),
#     'gender': forms.Select(attrs={'class': 'form-control'}),
#     'employee_status': forms.Select(attrs={'class': 'form-control'}),
#     'last_names': forms.TextInput(attrs={'class': 'form-control'}),
# })

# class PersonForm(forms.ModelForm):
#     prefix = 'user'

#     first_names = forms.CharField(required=True,
#                                   widget=forms.TextInput(attrs={
#                                       'class': 'form-control',
#                                   }))
#     last_names = forms.CharField(required=True,
#                                  widget=forms.TextInput(attrs={
#                                      'class': 'form-control',
#                                  }))
#     email = forms.EmailField(required=True,
#                                     widget=forms.TextInput(attrs={
#                                         'class': 'form-control',
#                                     }))
#     display_name = forms.CharField(required=True,
#                                    widget=forms.TextInput(attrs={
#                                        'class': 'form-control',
#                                    }))
#     primary_phone = forms.CharField(required=True,
#                                     widget=forms.TextInput(attrs={
#                                         'class': 'form-control',
#                                     }))
#     secondary_phone = forms.CharField(required=False,
#                                       widget=forms.TextInput(attrs={
#                                           'class': 'form-control',
#                                       }))
#     birth_date = forms.DateField(required=False,
#                                  widget=forms.DateInput(attrs={
#                                      'placeholder': 'mm/dd/yyyy',
#                                      'class': 'form-control datepicker'}))
#     gender = forms.ChoiceField(required=False,
#                                choices=Profile.GENDER_CHOICES,
#                                widget=forms.Select(attrs={
#                                    'class': 'form-control dropdown'}))
#     bio = forms.CharField(required=False,
#                           widget=forms.Textarea(
#                           attrs={'class': 'form-control', 'cols': 80}))
#     natid_type = forms.ChoiceField(choices=NationalId.ID_TYPE_CHOICES,
#                                    widget=forms.Select(attrs={
#                                        'class': 'form-control dropdown'}))
#     natid = forms.CharField(required=True,
#                             widget=forms.TextInput(attrs={
#                                 'class': 'form-control',
#                             }))
#     picture = forms.ImageField(required=False, allow_empty_file=True)

#     employee_status = forms.ChoiceField(choices=User.EMPLOYEE_STATUS_CHOICES,
#                                    widget=forms.Select(attrs={
#                                        'class': 'form-control dropdown'}))

#     groups = forms.ModelMultipleChoiceField(
#         widget=FilteredSelectMultiple('Groups', is_stacked=False),
#         queryset=ModGroup.objects.all()
#     )

#     class Meta:
#         model = Profile
#         fields = (
#             'first_names',
#             'last_names',
#             'email',
#             'display_name',
#             'primary_phone',
#             'secondary_phone',
#             'birth_date',
#             'gender',
#             'bio',
#             'natid_type',
#             'natid',
#             'picture',
#             'employee_status',
#             'picture',
#             'groups',
#         )

#     class Media:
#         js = ('/admin-contrib/jsi18n/',)