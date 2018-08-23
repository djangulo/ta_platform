import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.contrib.auth.models import Group, Permission

from accounts.models import User, Profile, ModGroup

EMAIL = 'alice@wonderland.com'
PASSWORD = 'TESTPASSWORD'
USERNAME = 'alice-warrior-117'

IMAGE_PATH = os.path.join(
    settings.BASE_DIR, 'assets/img/LinekodeIconB2.png')

TEST_MEDIA_ROOT = "/tmp/django_test_media_dump"


class UserModelTest(TestCase):
    """User model tests."""
    def test_can_create_user(self):
        user = User.objects.create(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        self.assertEqual(user, User.objects.first())

    def test_can_create_superuser(self):
        superuser = User.objects.create_superuser(email=EMAIL,
                                                  password=PASSWORD)
        self.assertTrue(superuser.is_admin)

    def test_str_call_returns_email(self):
        user = User.objects.create(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        self.assertEqual(str(user), EMAIL)


class ModGroupTest(TestCase):
    """Tests for ModGroup model."""
    def test_inheritance_works(self):
        group = ModGroup.objects.create(name='test_group')
        self.assertEqual(Group.objects.first().name, group.name)

    def test_get_all_perms_method(self):
        group = ModGroup.objects.create(name='test_group')
        perm1 = Permission.objects.get(pk=1)
        perm2 = Permission.objects.get(pk=2)
        group.permissions.add(perm1, perm2)
        self.assertIn(
            perm1.codename,
            group.permissions.all().values_list('codename', flat=True))



class NationalIdTest(TestCase):
    pass


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProfileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username=USERNAME,
                                        password=PASSWORD,
                                        email=EMAIL)
        self.profile = self.user.profile

    def test_image_is_deleted_from_filesystem_on_delete(self):
        self.profile.picture = SimpleUploadedFile(
            name='destroyed.jpg',
            content=open(IMAGE_PATH, 'rb').read(),
            content_type='image/png'
        )
        self.profile.save()
        path = self.profile.picture.file.name
        self.profile.picture.delete()
        with self.assertRaises(FileNotFoundError):
            open(path, 'rb')

    def test_user_directory_path(self):
        self.profile.picture = SimpleUploadedFile(
            name='saved.jpg',
            content=open(IMAGE_PATH, 'rb').read(),
            content_type='image/png'
        )
        self.profile.save()
        self.assertIn('saved.jpg', os.listdir(
            os.path.join(TEST_MEDIA_ROOT,'user_%s' %(self.user.id,), 'profile')))
