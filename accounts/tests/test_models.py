import os
from io import StringIO
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from accounts.models import User, Profile, ModGroup, EmailAddress

EMAIL = 'alice@wonderland.com'
PASSWORD = 'TESTPASSWORD'
USERNAME = 'alice-warrior-117'

IMAGE_PATH = os.path.join(
    settings.BASE_DIR, 'assets/img/LinekodeIconB2.png')

TEST_MEDIA_ROOT = "/tmp/django_test_media_dump"


class EmailManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=USERNAME,
                                        password=PASSWORD)
        self.email1 = EmailAddress.objects.create(email=EMAIL,
                                                  user=self.user)
        self.email2 = EmailAddress.objects.create(email='salted'+EMAIL,
                                                  user=self.user)
    
    def tearDown(self):
        for obj in (self.user, self.email1, self.email2):
            obj.delete()

    def test_can_set_primary_with_pk_no_user(self):
        EmailAddress.objects.set_as_primary(self.email2.pk)
        self.assertTrue(EmailAddress.objects.get(pk=self.email2.pk).is_primary)

    def test_can_set_primary_with_str_no_user(self):
        EmailAddress.objects.set_as_primary(self.email2.email)
        self.assertTrue(EmailAddress.objects.get(pk=self.email2.pk).is_primary)

    def test_can_set_primary_with_obj_no_user(self):
        EmailAddress.objects.set_as_primary(self.email2)
        self.assertTrue(EmailAddress.objects.get(pk=self.email2.pk).is_primary)

    def test_can_set_primary_with_pk_with_user(self):
        EmailAddress.objects.set_as_primary(self.email2.pk)
        self.assertTrue(EmailAddress.objects.get(pk=self.email2.pk).is_primary)

    def test_can_set_primary_with_str_with_user(self):
        EmailAddress.objects.set_as_primary(self.email2.email)
        self.assertTrue(EmailAddress.objects.get(pk=self.email2.pk).is_primary)

    def test_can_set_primary_with_obj_with_user(self):
        EmailAddress.objects.set_as_primary(self.email2)
        self.assertTrue(EmailAddress.objects.get(pk=self.email2.pk).is_primary)


class EmailAddressTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=USERNAME,
                                        password=PASSWORD)
    def tearDown(self):
        self.user.delete()

    def test_can_create(self):
        email = EmailAddress.objects.create(email=EMAIL,
                                            user=self.user)
        self.assertEqual(email, EmailAddress.objects.first())

    def test_first_email_is_primary(self):
        email = EmailAddress.objects.create(email=EMAIL,
                                            user=self.user)
        self.assertTrue(email.is_primary)

    def test_emails_after_first_are_not_primary(self):
        email1 = EmailAddress.objects.create(email=EMAIL,
                                             user=self.user)
        email2 = EmailAddress.objects.create(email='salted'+EMAIL,
                                             user=self.user)                                            
        self.assertFalse(email2.is_primary)


class UserManagerTest(TestCase):
    """User manager tests."""
    def test_can_create_user(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        self.assertEqual(user, User.objects.first())

    def test_can_create_superuser(self):
        superuser = User.objects.create_superuser(email=EMAIL,
                                                  username=USERNAME,
                                                  password=PASSWORD)
        self.assertTrue(superuser.is_admin)


class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        out = StringIO()
        call_command('create_initial_groups', stdout=out)
        cls.content_type = ContentType.objects.get_for_model(User)
        cls.perms = Permission.objects.filter(
            content_type=cls.content_type)

    def test_can_create(self):
        user = User.objects.create(username=USERNAME, password=PASSWORD)
        self.assertEqual(User.objects.first(), user)

    def test_can_create_with_all_args(self):
        user = User.objects.create(
            username=USERNAME,
            password=PASSWORD,
            birth_date='1916-12-21',
            first_names='Alice',
            last_names='Van Der Laand',
        )
        self.assertEqual(User.objects.first(), user)

#     def test_str_call_returns_email(self):
#         user = User.objects.create(email=EMAIL, password=PASSWORD,
#                                    username=USERNAME)
#         self.assertEqual(str(user), EMAIL)


# class ModGroupTest(TestCase):
#     """Tests for ModGroup model."""
#     def test_inheritance_works(self):
#         group = ModGroup.objects.create(name='test_group')
#         self.assertEqual(Group.objects.first().name, group.name)

#     def test_get_all_perms_method(self):
#         group = ModGroup.objects.create(name='test_group')
#         perm1 = Permission.objects.get(pk=1)
#         perm2 = Permission.objects.get(pk=2)
#         group.permissions.add(perm1, perm2)
#         self.assertIn(
#             perm1.codename,
#             group.permissions.all().values_list('codename', flat=True))



# class NationalIdTest(TestCase):
#     pass


# @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
# class ProfileTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username=USERNAME,
#                                         password=PASSWORD,
#                                         email=EMAIL)
#         self.profile = self.user.profile

#     def test_image_is_deleted_from_filesystem_on_delete(self):
#         self.profile.picture = SimpleUploadedFile(
#             name='destroyed.jpg',
#             content=open(IMAGE_PATH, 'rb').read(),
#             content_type='image/png'
#         )
#         self.profile.save()
#         path = self.profile.picture.file.name
#         self.profile.picture.delete()
#         with self.assertRaises(FileNotFoundError):
#             open(path, 'rb')

#     def test_user_directory_path(self):
#         self.profile.picture = SimpleUploadedFile(
#             name='saved.jpg',
#             content=open(IMAGE_PATH, 'rb').read(),
#             content_type='image/png'
#         )
#         self.profile.save()
#         self.assertIn('saved.jpg', os.listdir(
#             os.path.join(TEST_MEDIA_ROOT,'user_%s' %(self.user.id,), 'profile')))
