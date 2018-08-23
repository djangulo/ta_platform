from django.urls import reverse
from django.test import TestCase

from accounts.forms import RegistrationForm
from accounts.models import User

from .test_models import EMAIL, USERNAME

class RegistrationViewTest(TestCase):
    URL = reverse('accounts:register')
    def test_can_access(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)

    # def test_right_template_is_used(self):
    #     response = self.client.get(self.URL)
    #     self.assertTemplateUsed(response, 'accounts/user_form.html')

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
#                                              passwo    # path('register/complete/', auth_views.password_reset_complete, {
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
        
    