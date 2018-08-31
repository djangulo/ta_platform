from django.test import TestCase

from accounts.models import Profile, User, EmailAddress

from .test_models import USERNAME, PASSWORD, EMAIL

class AccountSignalTest(TestCase):

    def test_create_user_triggers_profile_creation(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                        username=USERNAME)
        self.assertEqual(user.profile, Profile.objects.first())

    def test_profile_reverse_relation(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                        username=USERNAME)
        profile = Profile.objects.first()
        self.assertEqual(profile.user, user)

    def test_create_user_triggers_email_creation(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                        username=USERNAME)
        self.assertEqual(user.email, EmailAddress.objects.first().email)

    def test_email_reverse_relation(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                        username=USERNAME)
        email = EmailAddress.objects.first()
        self.assertEqual(email.user, user)

    def test_email_reverse_relation_accessor(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                        username=USERNAME)
        email = EmailAddress.objects.first()
        self.assertIn(email, user.email_addresses.all())
