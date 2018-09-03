from math import floor
from django.contrib.auth.views import (
    INTERNAL_RESET_SESSION_TOKEN,
    INTERNAL_RESET_URL_TOKEN,
) 
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.test import TestCase
from unittest.mock import patch

from accounts.forms import (
    RegistrationForm,
    LoginForm,
    PasswordChangeForm,
    PasswordResetForm,
    PasswordSetForm,
)
from accounts.tokens import verify_token_generator, reset_token_generator
from accounts.models import User

from accounts.views import INTERNAL_VERIFICATION_URL_TOKEN, LOGOUT_MESSAGE

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

class RegistrationViewTest(TestCase):
    URL = reverse('accounts:register')
    @classmethod
    def setUpTestData(self):
        self.user = User(email=EMAIL,
                         username=USERNAME,
                         is_active=True,
                         is_verified=True,
                         accepted_tos=True)
        self.user.set_password(PASSWORD)
        self.user.save()

    def test_right_template_is_used(self):
        response = self.client.get(self.URL)
        self.assertTemplateUsed(response, 'accounts/registration_form.html')

    def test_logged_in_users_is_redirected(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(self.URL)
        expected_url = reverse('accounts:account', kwargs={
            'slug': self.user.slug
        })
        self.assertRedirects(response, expected_url)

    def test_correct_form_is_used(self):
        response = self.client.get(self.URL)
        self.assertIsInstance(response.context_data['form'], RegistrationForm)

    @patch('accounts.forms.RegistrationForm.send_mail')
    def test_form_valid_sends_email(self, mock_send_mail):
        OTHER_TEST_DATA = TEST_DATA.copy()
        OTHER_TEST_DATA['username'] = USERNAME + '2'
        OTHER_TEST_DATA['email'] = 'salt' + EMAIL 
        response = self.client.post(self.URL, data=OTHER_TEST_DATA)
        self.assertTrue(mock_send_mail.called)

    @patch('accounts.forms.RegistrationForm.send_mail')
    def test_form_invalid_does_not_sends_email(self, mock_send_mail):
        INVALID_DATA = TEST_DATA.copy()
        INVALID_DATA['accepted_tos'] = False
        response = self.client.post(self.URL, data=INVALID_DATA)
        self.assertFalse(mock_send_mail.called)

    @patch('accounts.forms.RegistrationForm.send_mail')
    def test_form_valid_redirects_to_register_done(self, mock_send_mail):
        OTHER_TEST_DATA = TEST_DATA.copy()
        OTHER_TEST_DATA['username'] = USERNAME+'2'
        OTHER_TEST_DATA['email'] = 'salt' + EMAIL
        response = self.client.post(self.URL, data=OTHER_TEST_DATA)
        expected_url = reverse('accounts:register_done')
        self.assertRedirects(response, expected_url)


class RegistrationDoneViewTest(TestCase):
    URL = reverse('accounts:register_done')
    def test_right_template_is_used(self):
        response = self.client.get(self.URL)
        self.assertTemplateUsed(response, 'accounts/registration_done.html')


class RegistrationVerifyViewTest(TestCase):
    """
    RegistrationVerifyView tests. Note that in order for tests to pass
    all client requests need to have kwarg follow=True set, as the im-
    plementation relies on a redirect for security.
    """
    token_generator = verify_token_generator

    def setUp(self):
        self.unregistered_user = User(email=EMAIL,
                                      username=USERNAME,
                                      accepted_tos=True)
        self.unregistered_user.set_password(PASSWORD)
        self.unregistered_user.save()
        self.token = self.token_generator.make_token(self.unregistered_user)
        self.uid = urlsafe_base64_encode(force_bytes(
            self.unregistered_user.pk)).decode()
        self.url = reverse('accounts:register_verify', kwargs={
            'uidb64': self.uid,
            'token': self.token,
        })

    def tearDown(self):
        self.unregistered_user.delete()

    def test_right_template_is_used(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'accounts/registration_verify.html')

    def test_token_is_replaced_on_url(self):
        response = self.client.get(self.url)
        self.assertNotIn(self.token, response.url)
        self.assertIn(INTERNAL_VERIFICATION_URL_TOKEN, response.url)

    def test_uid_is_kept_on_url(self):
        response = self.client.get(self.url)
        self.assertIn(self.uid, response.url)

    def test_proper_token_passed_verifies_user(self):
        response = self.client.get(self.url, follow=True)
        refreshed_user = User.objects.get(pk=self.unregistered_user.pk)
        self.assertTrue(refreshed_user.is_verified)

    def test_wrong_token_passed_does_not_verify_user(self):
        url = reverse('accounts:register_verify', kwargs={
            'uidb64': self.uid,
            'token': self.token+'a',
        })
        response = self.client.get(url, follow=True)
        refreshed_user = User.objects.get(pk=self.unregistered_user.pk)
        self.assertFalse(refreshed_user.is_verified)

    def test_proper_token_sets_validlink_true(self):
        url = reverse('accounts:register_verify', kwargs={
            'uidb64': self.uid,
            'token': self.token,    
        })
        response = self.client.get(self.url, follow=True)
        self.assertTrue(response.context_data['validlink'])

    def test_wrong_token_sets_validlink_false(self):
        url = reverse('accounts:register_verify', kwargs={
            'uidb64': self.uid,
            'token': self.token+'wrongotokeno',
        })
        response = self.client.get(url, follow=True)
        self.assertFalse(response.context_data['validlink'])

    def test_view_redirects_to_tokenless_view(self):
        expected_url = reverse('accounts:register_verify', kwargs={
            'uidb64': self.uid,
            'token': self.token,
        }).replace(self.token, INTERNAL_VERIFICATION_URL_TOKEN)
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_url)


class LoginViewTest(TestCase):
    url = reverse('accounts:login')
    def setUp(self):
        self.user = User(email=EMAIL,
                                      username=USERNAME,
                                      accepted_tos=True,
                                      is_active=True,
                                      is_verified=True)
        self.user.set_password(PASSWORD)
        self.user.save()

    def tearDown(self):
        self.user.delete()

    @patch('django.contrib.auth.login')
    def test_login_fails_with_wrong_credentials(self, mock_login):
        self.client.post(self.url, data={
            'username': USERNAME+'b',
            'password': PASSWORD
        })
        self.assertFalse(mock_login.called)

    def test_login_runs_with_right_credentials(self):
        self.client.post(self.url, data={
            'username': USERNAME,
            'password': PASSWORD
        })
        self.assertTrue(self.user.is_authenticated)

    def test_correct_template_is_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_correct_form_is_used(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context_data['form'], LoginForm)

    def test_success_message_has_username_in_it(self):
        response = self.client.post(self.url, follow=True, data={
            'username': USERNAME,
            'password': PASSWORD,
        })
        self.assertContains(response, 'Welcome %s!' % (USERNAME,))


class LogoutViewTest(TestCase):
    url = reverse('accounts:logout')
    def setUp(self):
        self.user = User(email=EMAIL,
                         username=USERNAME,
                         accepted_tos=True,
                         is_active=True,
                         is_verified=True)
        self.user.set_password(PASSWORD)
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_can_logout_with_GET(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(self.url, follow=True)
        self.assertNotEqual(response.context.get('user'), self.user)
        self.assertTrue(response.context.get('user').is_anonymous)

    def test_can_logout_with_POST(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(self.url, follow=True)
        self.assertNotEqual(response.context.get('user'), self.user)
        self.assertTrue(response.context.get('user').is_anonymous)

    def test_success_message_is_added_on_logout(self):
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, LOGOUT_MESSAGE)

    def test_logout_redirects_to_home(self):
        expected_url = reverse('home')
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_url)


class PasswordResetViewTest(TestCase):
    url = reverse('accounts:password_reset')
    def setUp(self):
        self.user = User(email=EMAIL,
                         username=USERNAME,
                         is_active=True,
                         is_verified=True,
                         accepted_tos=True)
        self.user.set_password(PASSWORD)
        self.user.save()
        self.client.login(username=USERNAME, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_right_template_is_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'accounts/password_reset_form.html')

    def test_correct_form_is_used(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context_data['form'], PasswordResetForm)

    @patch('accounts.forms.PasswordResetForm.send_mail')
    def test_form_valid_sends_email(self, mock_send_mail):
        data = {'email_or_username': EMAIL}
        response = self.client.post(self.url, data=data)
        self.assertTrue(mock_send_mail.called)

    @patch('accounts.forms.PasswordResetForm.send_mail')
    def test_form_invalid_does_not_sends_email(self, mock_send_mail):
        invalid_data = {'email_or_username': 'wrong@email.com'}
        response = self.client.post(self.url, data=invalid_data)
        self.assertFalse(mock_send_mail.called)

    @patch('accounts.forms.PasswordResetForm.send_mail')
    def test_form_valid_redirects_to_password_reset_done(self, mock_send_mail):
        data = {'email_or_username': EMAIL}
        response = self.client.post(self.url, data=data)
        expected_url = reverse('accounts:password_reset_done')
        self.assertRedirects(response, expected_url)

    @patch('accounts.forms.PasswordResetForm.send_mail')
    def test_can_reset_password_with_email(self, mock_send_mail):
        data = {'email_or_username': EMAIL}
        response = self.client.post(self.url, data=data)
        self.assertTrue(mock_send_mail.called)

    @patch('accounts.forms.PasswordResetForm.send_mail')
    def test_can_reset_password_with_username(self, mock_send_mail):
        data = {'email_or_username': USERNAME}
        response = self.client.post(self.url, data=data)
        self.assertTrue(mock_send_mail.called)

    @patch('accounts.forms.PasswordResetForm.send_mail')
    def test_invalid_email_still_redirects_to_success_view(self, mock_send_mail):
        data = {'email_or_username': 'invalido@emailo.com'}
        expected_url = reverse('accounts:password_reset_done')
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(response, expected_url)


class PasswordResetDoneView(TestCase):
    url = reverse('accounts:password_reset_done')
    @classmethod
    def setUpTestData(self):
        self.user = User(email=EMAIL,
                         username=USERNAME,
                         is_active=True,
                         is_verified=True,
                         accepted_tos=True)
        self.user.set_password(PASSWORD)
        self.user.save()

    def test_right_template_is_used(self):
        url = reverse('accounts:password_reset')
        data = {'email_or_username': EMAIL}
        response = self.client.post(url, data=data, follow=True)
        self.assertTemplateUsed(response, 'accounts/password_reset_done.html')

    def test_direct_access_redirects_to_password_reset(self):
        reset_url = reverse('accounts:password_reset')
        done_url = reverse('accounts:password_reset_done')
        response = self.client.get(done_url)
        self.assertRedirects(response, reset_url)


class PasswordResetConfirmViewTest(TestCase):
    """
    PasswordResetConfirmViewTest tests. Note that in order for tests to pass
    all client requests need to have kwarg follow=True set, as the im-
    plementation relies on a redirect for security.
    """
    token_generator = reset_token_generator

    def setUp(self):
        self.user = User(email=EMAIL,
                         username=USERNAME,
                         accepted_tos=True,
                         is_verified=True,
                         is_active=True)
        self.user.set_password(PASSWORD)
        self.user.save()
        self.token = self.token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(
            self.user.pk)).decode()
        self.url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': self.uid,
            'token': self.token,
        })

    def tearDown(self):
        self.user.delete()

    def test_right_template_is_used(self):
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'accounts/password_reset_confirm.html')

    def test_token_is_replaced_on_url(self):
        response = self.client.get(self.url, follow=True)
        self.assertNotIn(self.token, response.request.get('PATH_INFO'))
        self.assertIn(INTERNAL_RESET_URL_TOKEN,
                      response.request.get('PATH_INFO'))

    def test_uid_is_kept_on_url(self):
        response = self.client.get(self.url)
        self.assertIn(self.uid, response.url)

    def test_proper_token_passed_displays_form(self):
        response = self.client.get(self.url, follow=True)
        self.assertIsNotNone(response.context_data['form'])

    def test_wrong_token_passed_does_display_form_user(self):
        url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': self.uid,
            'token': self.token+'a',
        })
        response = self.client.get(url, follow=True)
        self.assertIsNone(response.context_data['form'])

    def test_proper_token_sets_validlink_true(self):
        url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': self.uid,
            'token': self.token,    
        })
        response = self.client.get(self.url, follow=True)
        self.assertTrue(response.context_data['validlink'])

    def test_wrong_token_sets_validlink_false(self):
        url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': self.uid,
            'token': self.token+'wrongotokeno',
        })
        response = self.client.get(url, follow=True)
        self.assertFalse(response.context_data['validlink'])

    def test_view_redirects_to_tokenless_view(self):
        expected_url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': self.uid,
            'token': self.token,
        }).replace(self.token, INTERNAL_RESET_URL_TOKEN)
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_url)

    # def test_response_has_success_message(self):

        

    # def test_view_has_correct_form(self):
    #     response = self.client.get(self.URL)
    #     self.assertIsInstance(resp`onse.context['form'], RegistrationForm)

    # def test_invalid_form_renders_same_view(self):
    #     response = self.client.post(self.URL, data={
    #         'email': '',
    #         'username': '',
    #         'accepted_eula': False
    #     })
    #     self.assertTemplateUsed(response, 'accounts/user_form.html')

    # def test_invalid_form_does_not_create_user(self):
    #     response = self.client.post(self.URL, data={
    #         'email': '',
    #         'username': '',
    #         'accepted_eula': False
    #     })
    #     self.assertEqual(User.objects.count(), 0)

    # def test_valid_input_creates_user(self):
    #     response = self.client.post(self.URL, data={
    #         'email': EMAIL,
    #         'username': USERNAME,
    #         'accepted_eula': True
    #     })
    #     self.assertEqual(User.objects.first().username, USERNAME)

#     def test_home_page_returns_correct_markup(self):
#         request = HttpRequest()
#         res = home(request)
#         html = res.content.decode('utf8')
#         self.assertIn(f"<title>{COMPANY_NAME} | Home</title>", html)


# class ApplicationViewTests(TestCase):

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.user = User.objects.create_user(email='alice@wonderland.com',
#                                              passwo    
# # path('register/complete/', auth_views.password_reset_complete, {
    #     'template_name': 'registration/initial_complete.html',
    # }, name='register-complete'),elf.user,
#                                             first_names='Alice',
#                                             last_names='InChains',
#                                             email=self.user.email,
#                                             primary_phone='999-999-9999',
#                                             natid='999-9999999-9')

#     def test_can_get_application_form_view(self):
#         request = self.factory.get(reverse('applications:apply'))
#         response = ApplicationFormView.as_view()(request)
#         self.assertEqual(response.status_code, 200)


#     def test_application_form_view_has_correct_form(self):
#         request = self.factory.get(reverse('applications:apply'))
#         response = ApplicationFormView.as_view()(request)
#         form = response.context_data['form']
#         self.assertTrue(isinstance(form, ApplicationForm))

#     def test_can_save_a_POST_request(self):
#         response = self.client.post(reverse('applications:apply'), data={
#             'first_names': 'Alice',
#             'last_names': 'InChains',
#             'email': self.user.email,
#             'national_id_number': '123-4567890-1',
#             'primary_phone': self.profile.primary_phone,
#         })
#         application = Application.objects.first()
#         self.assertEqual(application.national_id_number, '12345678901')
        
    