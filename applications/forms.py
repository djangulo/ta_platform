from django import forms
from django.core import validators
from django.utils import timezone
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms import widgets, formset_factory, inlineformset_factory

from django.utils.translation import gettext_lazy as _

from applications.models import Application, CallCenter, CityTown, Language, AreaOfExpertise

REQUIRED_ERROR = 'This field cannot be blank.'
EIGHTEEN_YEARS_AGO = (timezone.now() - timezone.timedelta(days=((365*18)+5))
                      ).strftime('%m/%d/%Y')

class ApplicationForm(forms.ModelForm):
    prefix = 'application'
    email = forms.EmailField(validators=[validators.validate_email],
                widget=forms.EmailInput(attrs={
                    'placeholder': 'john.doe@company.com',
                    'class': 'form-control',
                },))
    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['previous_call_center'].queryset = CallCenter.objects.all().filter(display_in_form=True)
        self.fields['city_or_town'].queryset = CityTown.objects.all().filter(display_in_form=True)
        self.fields['languages'].queryset = Language.objects.all().filter(display_in_form=True)
        self.fields['areas_of_expertise'].queryset = AreaOfExpertise.objects.all().filter(display_in_form=True)

    # def clean(self):

    class Meta:
        model = Application
        fields = (
            'national_id_type',
            'national_id_number',
            'email',
            'first_names',
            'last_names',
            'primary_phone',
            'secondary_phone',
            'gender',
            'lived_in_usa',
            'birth_date',
            'city_or_town',
            'address_line_one',
            'address_line_two',
            'previous_call_center',
            'currently_employed',
            'current_employer',
            'areas_of_expertise',
            'languages',
        )
        widgets = {
            'national_id_type': forms.Select(attrs={
                'class': 'form-control dropdown',
            }),
            'national_id_number': forms.TextInput(attrs={
                    'placeholder': 'Enter your national ID here',
                    'class': 'form-control',
                    'required': True,
                },
            ),
            'email': forms.EmailInput(attrs={
                    'placeholder': 'john.doe@company.com',
                    'class': 'form-control',
                },
            ),
            'first_names': forms.TextInput(attrs={
                'placeholder': 'John',
                'class': 'form-control',
            }),
            'last_names': forms.TextInput(attrs={
                'placeholder': 'Doe',
                'class': 'form-control',
            }),
            'primary_phone': forms.TextInput(attrs={
                'placeholder': '809-555-5555',
                'class': 'form-control',
            }),
            'secondary_phone': forms.TextInput(attrs={
                'placeholder': '809-555-5555',
                'class': 'form-control',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control dropdown',
            }),
            'birth_date': forms.DateInput(attrs={
                'placeholder': EIGHTEEN_YEARS_AGO,
                'class': 'form-control datepicker',
            }),
            'city_or_town': forms.Select(attrs={
                'class': 'form-control dropdown',
            }),
            'address_line_one': forms.DateInput(attrs={
                'placeholder': '',
                'class': 'form-control datepicker',
            }),
            'address_line_two': forms.DateInput(attrs={
                'placeholder': '',
                'class': 'form-control datepicker',
            }),
            'previous_call_center': forms.CheckboxSelectMultiple(),
            # 'lived_in_usa': forms.CheckboxInput(attrs={
            #     'class': 'pretty p-switch p-fill p-primary',
            # }),
        }
#         error_messages = {
#             'start_date': {
#                 'required': REQUIRED_ERROR,
#                 'invalid': 'this is not a message',
#             },
#             'line_of_business': {
#                 'required': REQUIRED_ERROR,
#             },
#             'shift': {
#                 'required': REQUIRED_ERROR,
#             },
#             'hiring_bonus': {
#                 'required': REQUIRED_ERROR,
#             },
#             'referral_bonus': {
#                 'required': REQUIRED_ERROR,
#             },
#             NON_FIELD_ERRORS: {
#                 'unique_together': 'Class already exists for that date',
#             }
#         }

# class LineOfBusinessForm(forms.ModelForm):

#     prefix = 'line-of-business'

#     class Meta:
#         model = LineOfBusiness
#         fields = ('name', 'slug', 'description',)
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'maxlenght': 25,
#                 'minlength': 3,
#                 'class': 'form-control col-sm-5',
#                 'placeholder': 'Enter Line Of Business name'
#             }),
#             'slug': forms.HiddenInput(),
#             # 'slug': forms.TextInput(attrs={
#             #     'class': 'form-control col-sm-5',
#             #     'placeholder': 'Enter Line Of Business name',
#             #     'disabled': True
#             # }),
#             'description': forms.Textarea(attrs={
#                 'maxlenght': 200,
#                 'minlength': 5,
#                 'class': 'form-control col-sm-5',
#                 'placeholder': 'Enter Line Of Business description'
#             }),

#         }


# class TenureAndValueWidget(widgets.MultiWidget):
#     def __init__(self, *args, **kwargs):
#         _widgets = (
#             widgets.TextInput(attrs={'class': 'form-control', 'required': True}),
#             widgets.TextInput(attrs={'class': 'form-control', 'required': True}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#             widgets.TextInput(attrs={'class': 'form-control'}),
#         )
#         super(TenureAndValueWidget, self).__init__(_widgets, *args, **kwargs)

#     def decompress(self, value):
#         if value:
#             return [val for val in value]
#         return [None for i in range(10)]


# class TenureAndValueField(forms.MultiValueField):

#     def __init__(self, *args, **kwargs):
#         error_messages = {
#             'incomplete': 'Enter at least one tenure and value pair',
#         }
#         fields = (
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#             forms.CharField(max_length=4),
#         )
#         super(TenureAndValueField, self).__init__(*args, **kwargs)
    
#     def compress(self, data_list):
#         ldict = []
#         for i in range(0, len(data_list), 2):
#             if len(data_list[i]) > 0 and len(data_list[i + 1]) > 0:
#                 ldict.append({data_list[i]: data_list[i + 1]})
#         return ldict

#     def decompress(self, value):
#         if value:
#             return [val for val in value]
#         return [None for i in range(10)]


# class BonusForm(forms.ModelForm):
#     class Meta:
#         fields = (
#             'name',
#             'amount',
#             'slug',
#             't_1', 'v_1',
#             't_2', 'v_2',
#             't_3', 'v_3',
#             't_4', 'v_4',
#             't_5', 'v_5',
#         )

#     def clean(self):
#         cleaned_data = super(BonusForm, self).clean()
#         amount = cleaned_data.get('amount')
#         values = sum([i for i in (
#             cleaned_data.get('v_1'),
#             cleaned_data.get('v_2'),
#             cleaned_data.get('v_3'),
#             cleaned_data.get('v_4'),
#             cleaned_data.get('v_5'),
#         ) if i is not None])
#         if amount != values:
#             msg = "The amount and the sum of payouts don't match"
#             self.add_error('amount', msg)


# class HiringBonusForm(BonusForm):
#     prefix = 'hiring-bonus'
#     class Meta(BonusForm.Meta):
#         model = HiringBonus
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'maxlenght': 25,
#                 'minlength': 3,
#                 'class': 'form-control col-sm-5',
#                 'placeholder': 'Enter hiring bonus name'
#             }),
#             'amount': forms.TextInput(attrs={
#                 'class': 'form-control col-sm-5',
#                 'placeholder': 'Enter hiring bonus amount'
#             }),
#             'slug': forms.HiddenInput(),
#         }


# class ReferralBonusForm(BonusForm):
#     prefix = 'referral-bonus'
#     class Meta(BonusForm.Meta):
#         model = ReferralBonus
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'maxlenght': 25,
#                 'minlength': 3,
#                 'class': 'form-control col-sm-5',
#                 'placeholder': 'Enter referral bonus name'
#             }),
#             'amount': forms.TextInput(attrs={
#                 'class': 'form-control col-sm-5',
#                 'placeholder': 'Enter referral bonus amount'
#             }),
#             'slug': forms.HiddenInput(),
#         }
