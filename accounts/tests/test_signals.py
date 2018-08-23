from django.test import TestCase

from accounts.models import Profile, User

from .test_models import USERNAME, PASSWORD, EMAIL

class AccountSignalTest(TestCase):

    def test_create_user_triggers_profile_creation(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                        username=USERNAME)
        self.assertEqual(user.profile, Profile.objects.first())
