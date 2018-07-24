
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounts.models import User, Person, Address
from applications.models import (
    Career,
    Institution,
    Application,
    Language,
    CallCenter,
)

# TEST_IMAGE_PATH = os.path.join(
#     settings.BASE_DIR, 'applications/static/img/awesomeface.jpg')


class ApplicationModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # cls.user = User.objects.create_user(
        #                     email='waldo@findme.com',
        #                     username='waldo1',
        #                     password='testpassword'
        #                 )
        # cls.user.save()
        cls.person = Person.objects.create(first_names='Waldo',
                                        last_names='The Unfindable',
                                        display_name='@waldini',
                                        primary_phone='809-000-0023',
                                        natid_type=0,
                                        natid='123-456789-0',
                                        email='waldo@findme.com',
                                        )

    def test_anon_can_apply(self):
        application = Application.objects.create(
            first_names='Waldo',
            last_names='The Unfindable',
            primary_phone='555555555',
            national_id_number='000-0000000-0',
            address_line_one='ma-haus',
            email='otherwaldo@findme.com',
        )
        self.assertEquals(Application.objects.first(), application)

    def test_anon_becomes_person_after_applying(self):
        application = Application.objects.create(
            first_names='Waldo',
            last_names='The Unfindable',
            primary_phone='555555555',
            national_id_number='000-0000000-0',
            address_line_one='ma-haus',
            email='otherwaldo@findme.com',
        )
        self.assertEquals(Person.objects.last(),
                          application.person)

    def test_application_matching_natid_behavior(self):
        NATID = self.person.natid
        application = Application.objects.create(
            first_names='The New',
            last_names='Guy',
            primary_phone='5522345670',
            national_id_number=NATID,
            address_line_one='ma-haus',
            email='thenewguy@theoldcompany.com',
        )

    def test_subsequent_applications_fail(self):
        application = Application.objects.create(
            first_names=self.person.first_names,
            last_names=self.person.last_names,
            primary_phone=self.person.primary_phone,
            national_id_number=self.person.natid,
            address_line_one='ma-haus',
            email=self.person.email,
        )

        app2 = Application(
            first_names=self.person.first_names,
            last_names=self.person.last_names,
            primary_phone=self.person.primary_phone,
            national_id_number=self.person.natid,
            address_line_one='ma-haus',
            email=self.person.email,
        )

        self.assertRaises(ValidationError, app2.save)
#     def test_can_create_customer_with_user(self):
#         customer = Customer.objects.create(
#             first_name='Waldo',
#             last_name='The Unfindable',
#             display_name='waldo',
#             primary_phone='5555555555',
#             secondary_phone='1234567893',
#             user=self.user['object']
#         )
#         self.assertEqual(Customer.objects.first().user.email, 'waldo@findme.com')

#     def test_picture_uploads_successfully(self):
#         customer = Customer.objects.create(
#             first_name='Waldo',
#             last_name='The Unfindable',
#             display_name='waldo',
#             primary_phone='5555555555',
#             secondary_phone='1234567893',
#             picture=SimpleUploadedFile(
#                 name='my_awesome_face.jpg',
#                 content=open(TEST_IMAGE_PATH, 'rb').read(),
#                 content_type='image/jpeg'
#             ),
#             user=self.user['object']
#         )
#         self.assertIn(
#             'my_awesome_face.jpg',
#             os.listdir(
#                 os.path.join(
#                     settings.MEDIA_ROOT,
#                     'users',
#                     f'user_{self.user["object"].id}'
#                 )
#             )            
#         )

#     def test_reverse_relation_to_user_model(self):
#         customer = Customer.objects.create(
#             first_name='Waldo',
#             last_name='The Unfindable',
#             display_name='waldo',
#             primary_phone='5555555555',
#             secondary_phone='1234567893',
#             picture=SimpleUploadedFile(
#                 name='my_awesome_face.jpg',
#                 content=open(TEST_IMAGE_PATH, 'rb').read(),
#                 content_type='image/jpeg'
#             ),
#             user=self.user['object']
#         )
#         self.assertEqual(customer.user, self.user['object'])
    

# class AddressModelTests(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         user = User.objects.create_user(
#                             email='waldo@findme.com',
#                             password='testpassword'
#                         )
#         user.save()
#         customer = Customer.objects.create(
#             first_name='Waldo',
#             last_name='The Unfindable',
#             display_name='waldo',
#             primary_phone='5555555555',
#             secondary_phone='1234567893',
#             picture=SimpleUploadedFile(
#                 name='my_awesome_face.jpg',
#                 content=open(TEST_IMAGE_PATH, 'rb').read(),
#                 content_type='image/jpeg'
#             ),
#             user=user
#         )
#         cls.customer = customer

#     def test_cannot_create_address_without_customer(self):
#         address = Address(
#             full_name='My first address',
#             state_province_region='Santo Domingo',
#             city='DN',
#             sector='Los Cacicazgos',
#             address_line_one='c/ Hatuey',
#             phone_number='5555555555',
#             is_primary=False
#         )
#         self.assertRaises(ValidationError, address.save)

    # def test_can_create_address_with_customer(self):
    #     address = Address.objects.create(
    #         full_name='My first address',
    #         state_province_region='Santo Domingo',
    #         city='DN',
    #         sector='Los Cacicazgos',
    #         address_line_one='c/ Hatuey',
    #         phone_number='5555555555',
    #         is_primary=False,
    #         owner=self.customer
    #     )
    #     self.assertEqual(
    #         Address.objects.first().full_name,
    #         address.full_name
    #     )

    # @patch('googlemaps.Client.geocode')
    # def test_geocode_is_called_properly(self, mock_geocode):
    #     address = Address.objects.create(
    #         full_name='My first address',
    #         state_province_region='Santo Domingo',
    #         city='DN',
    #         sector='Los Cacicazgos',
    #         address_line_one='c/ Hatuey, no. 102',
    #         phone_number='5555555555',
    #         is_primary=False,
    #         owner=self.customer
    #     )
    #     print(address.address_line_two)

    #     gmaps = googlemaps.Client(key=settings.GOOGLEMAPS_SECRET_KEY)
    #     gmaps.geocode('c/ Hatuey, no. 102, Los Cacicazgos, Santo Domingo, Dominican Republic')

    #     self.assertTrue(mock_geocode.called)


    # @patch('googlemaps.Client.geocode')
    # def test_address_is_geocoded_properly(self, mock_geocode):
    #     address = Address.objects.create(
    #         full_name='My first address',
    #         state_province_region='Santo Domingo',
    #         city='DN',
    #         sector='Los Cacicazgos',
    #         address_line_one='c/ Hatuey, no. 102',
    #         phone_number='5555555555',
    #         is_primary=False,
    #         owner=self.customer
    #     )
    #     print(address.address_line_two)

    #     gmaps = googlemaps.Client(key=settings.GOOGLEMAPS_SECRET_KEY)
    #     gmaps.geocode('c/ Hatuey, no. 102, Los Cacicazgos, Santo Domingo, Dominican Republic')

    #     self.assertTrue(mock_geocode.called)
    #     self.assertEqual(
    #         'c/ Hatuey, no. 102, Los Cacicazgos, DN, Santo Domingo, Dominican Republic',
    #         address.formatted_name
    #     )