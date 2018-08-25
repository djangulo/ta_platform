from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounts.models import Profile
from applications.forms import ApplicationForm
from applications.models import Application

# form = ApplicationForm(data={
#             'first_names': profile.first_names,
#             'last_names': profile.last_names,
#             'primary_phone': profile.primary_phone,
#             'national_id_number': profile.natid,
#             'address_line_one': 'ma-haus',
#             'email': profile.email,
#         })


class ApplicationFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # cls.user = User.objects.create_user(
        #                     email='waldo@findme.com',
        #                     username='waldo1',
        #                     password='testpassword'
        #                 )
        # cls.user.save()
        cls.profile = Profile.objects.create(first_names='Waldo',
                                        last_names='The Unfindable',
                                        display_name='@waldini',
                                        primary_phone='809-000-0023',
                                        natid_type=0,
                                        natid='123-456789-0',
                                        email='waldo@findme.com',
                                        birth_date='1998-11-10',
                                        )

    def test_form_save_creates_object(self):
        data = {
            'first_names': 'Alice',
            'last_names': 'In Chains',
            'primary_phone': '809-000-0023',
            'national_id_number': '123-456789-0',
            'national_id_type': 0,
            'address_line_one': 'Wonderland, mad hatter\'s house',
            'email': 'alice@wonderland.com',
            'birth_date': '1998-11-10',
            'gender': 1,
        }
        form = ApplicationForm(data=data)
        print(form.errors.as_data())
        instance = form.save()
        self.assertEqual(Application.objects.first(), instance)

    def test_subsequent_applications_fail(self):
        form = ApplicationForm(data={
            'first_names': self.profile.first_names,
            'last_names': self.profile.last_names,
            'primary_phone': self.profile.primary_phone,
            'national_id_number': self.profile.natid,
            'address_line_one': 'ma-haus',
            'email': self.profile.email,
        })
        form.save()

        form2 = ApplicationForm(data={
            'first_names': self.profile.first_names,
            'last_names': self.profile.last_names,
            'primary_phone': self.profile.primary_phone,
            'national_id_number': self.profile.natid,
            'address_line_one': 'ma-haus',
            'email': self.profile.email,
        })

        self.assertRaises(ValidationError, form2.save)