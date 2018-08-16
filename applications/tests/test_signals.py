from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Person
from applications.models import Application

# TEST_IMAGE_PATH = os.path.join(
#     settings.BASE_DIR, 'applications/static/img/awesomeface.jpg')


class AssignPersonToApplicationSignalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = Person.objects.create(first_names='Alexander',
                                        last_names='The Great',
                                        display_name='thegratestA',
                                        primary_phone='MXXIV',
                                        natid_type=0,
                                        natid='112-2334455-6',
                                        email='alexander@alexandria.com',
                                        )

    def test_create_application_triggers_person_creation(self):
        application = Application.objects.create(
            first_names='John Test',
            last_names='Exampleson',
            primary_phone='555555555',
            national_id_number='000-0000000-0',
            address_line_one='ma-haus',
            email='mrtest@acompany.com')
        self.assertIsNotNone(application.person)

    def test_application_matches_person_by_natid(self):
        application = Application.objects.create(
            first_names='Waldo',
            last_names='The Unfindable',
            primary_phone='555555555',
            national_id_number=self.person.natid,
            address_line_one='ma-haus',
            email='otherwaldo@findme.com')
        self.assertEqual(application.person, self.person)


class SubsequentApplicationsSignalTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.person = Person.objects.create(first_names='Alexander',
                                        last_names='The Great',
                                        display_name='thegratestA',
                                        primary_phone='MXXIV',
                                        natid_type=0,
                                        natid='112-2334455-6',
                                        email='alexander@alexandria.com',
                                        )

    # def test_subsequent_applications_fail(self):
    #     application = Application.objects.create(
    #         first_names=self.person.first_names,
    #         last_names=self.person.last_names,
    #         primary_phone=self.person.primary_phone,
    #         national_id_number=self.person.natid,
    #         address_line_one='ma-haus',
    #         email=self.person.email,
    #     )

    #     app2 = Application(
    #         first_names=self.person.first_names,
    #         last_names=self.person.last_names,
    #         primary_phone=self.person.primary_phone,
    #         national_id_number=self.person.natid,
    #         address_line_one='ma-haus',
    #         email=self.person.email,
    #     )

    #     self.assertRaises(ValidationError, app2.save)