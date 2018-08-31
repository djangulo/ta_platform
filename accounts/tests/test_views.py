from math import floor
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase

from accounts.forms import RegistrationForm
from accounts.models import User

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
        self.user = User.objects.create(email=EMAIL,
                                   username=USERNAME,
                                   password=PASSWORD,
                                   is_active=True,
                                   is_verified=True)

    def test_right_template_is_used(self):
        response = self.client.get(self.URL)
        self.assertTemplateUsed(response, 'accounts/registration_form.html')

    def test_redirect_for_logged_in_users(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 302)


    # def test_view_has_correct_form(self):
    #     response = self.client.get(self.URL)
    #     self.assertIsInstance(response.context['form'], RegistrationForm)

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
        
    