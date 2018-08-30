from math import floor
from django import forms
from django.utils import timezone
from django.test import TestCase, override_settings
from unittest.mock import patch
from accounts.forms import RegistrationForm
from accounts.models import User, EmailAddress, PhoneNumber, NationalId

FIRST_NAMES = 'Alice'
LAST_NAMES = 'Van Der Laand'
USERNAME = 'alice-in-chains-112'
EMAIL = 'alice@wonderland.org'
BIRTH_DATE = '1916-11-12'
ID_TYPE = 0
ID_NUMBER = '000-000000-0'
PASSWORD = 'testpassword'
ACCEPT_TOS = True

TEST_DATA = {
    'first_names': FIRST_NAMES,
    'last_names': LAST_NAMES,
    'username': USERNAME,
    'email': EMAIL,
    'birth_date': BIRTH_DATE,
    'national_id_type': ID_TYPE,
    'national_id_number': ID_NUMBER,
    'accepted_tos': ACCEPT_TOS,
    'password1': PASSWORD,
    'password2': PASSWORD,
}

TEST_MIN_AGE = 18
MOCK_BIRTH_DATE_FAIL =  (timezone.now() - timezone.timedelta(days=(
    365 * (TEST_MIN_AGE - 2) + floor(TEST_MIN_AGE / 4)
))).date()
MOCK_BIRTH_DATE_PASS =  (timezone.now() - timezone.timedelta(days=(
    365 * (TEST_MIN_AGE + 2) + floor(TEST_MIN_AGE / 4)
))).date()


class RegistrationFormTest(TestCase):
    
    @patch('accounts.forms.RegistrationForm.send_mail')
    def test_save_on_empty_form_does_nothing(self, mock_send_mail):
        form = RegistrationForm()
        form.save()
        self.assertEqual(mock_send_mail.called, False)

    @patch('accounts.forms.RegistrationForm.send_mail')
    def test_valid_form_sends_email(self, mock_send_mail):
        form = RegistrationForm(data=TEST_DATA)
        form.save()
        self.assertEqual(mock_send_mail.called, True)

    def test_valid_form_creates_user(self):
        form = RegistrationForm(data=TEST_DATA)
        form.save()
        self.assertIsNotNone(User.objects.first())

    def test_invalid_form_does_not_create_user(self):
        INCOMPLETE_DATA = TEST_DATA.copy()
        INCOMPLETE_DATA.pop('accepted_tos')
        form = RegistrationForm(data=INCOMPLETE_DATA)
        form.save()
        self.assertIsNone(User.objects.first())

    def test_valid_form_creates_national_id(self):
        form = RegistrationForm(data=TEST_DATA)
        form.save()
        self.assertIsNotNone(NationalId.objects.first())

    @override_settings(ENFORCE_MIN_AGE=True,
                       MINIMUM_AGE_ALLOWED=TEST_MIN_AGE)
    def test_birth_date_validation_fails(self):
        INVALID_DATA = TEST_DATA.copy()
        INVALID_DATA['birth_date'] = MOCK_BIRTH_DATE_FAIL.strftime('%Y-%m-%d')
        form = RegistrationForm(data=INVALID_DATA)
        form.save()
        self.assertTrue(form.has_error('birth_date',
                                       'age_restricted'))

    @override_settings(ENFORCE_MIN_AGE=True,
                       MINIMUM_AGE_ALLOWED=TEST_MIN_AGE)
    def test_birth_date_validation_pass(self):
        VALID_DATA = TEST_DATA.copy()
        VALID_DATA['birth_date'] = MOCK_BIRTH_DATE_PASS.strftime('%Y-%m-%d')
        form = RegistrationForm(data=VALID_DATA)
        form.save()
        self.assertFalse(form.has_error('birth_date',
                                        'age_restricted'))

    def test_form_fails_on_national_id_duplicate(self):
        user = User.objects.create(username=USERNAME, password=PASSWORD)
        natid = NationalId.objects.create(id_number=ID_NUMBER, user=user)
        form = RegistrationForm(data=TEST_DATA)
        form.save()
        self.assertTrue(form.has_error('national_id_number',
                                       'national_id_exists'))

    def test_password_validation_fails_if_passwords_are_different(self):
        INVALID_DATA = TEST_DATA.copy()
        INVALID_DATA['password2'] = 'testpassword2'
        form = RegistrationForm(data=INVALID_DATA)
        form.save()
        self.assertTrue(form.has_error('password2', 'password_mismatch'))
