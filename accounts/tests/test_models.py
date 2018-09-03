import os
from io import StringIO
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from accounts.models import (
    AreaCode,
    EmailAddress,
    NationalId,
    PhoneNumber,
    Profile,
    User,
)
from admin_console.models import Country

FIRST_NAMES = 'Alice'
LAST_NAMES = 'Van Der Laand'
USERNAME = 'alice-in-chains-112'
PHONE_NUMBER = '333-3333'
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

IMAGE_PATH = os.path.join(
    settings.BASE_DIR, 'assets/img/LinekodeIconB2.png')

TEST_MEDIA_ROOT = "/tmp/django_test_media_dump"


class EmailManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=USERNAME,
                                        password=PASSWORD,
                                        email=EMAIL)
        self.email1 = EmailAddress.objects.get(user=self.user)
        self.email2 = EmailAddress.objects.create(email='salted'+EMAIL,
                                                  user=self.user)
    
    def tearDown(self):
        self.user.delete()

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
                                        password=PASSWORD,
                                        email=EMAIL)
    # def tearDown(self):
    #     self.user.delete()

    def test_can_create(self):
        email = EmailAddress.objects.create(email='salted'+EMAIL,
                                            user=self.user)
        self.assertEqual(email, EmailAddress.objects.latest('created_at'))

    def test_first_email_is_primary(self):
        email = self.user.email_addresses.first()
        self.assertTrue(email.is_primary)

    def test_emails_after_first_are_not_primary(self):
        email2 = EmailAddress.objects.create(email='salted'+EMAIL,
                                             user=self.user)                                            
        self.assertFalse(email2.is_primary)


class AreaCodeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=USERNAME,
                                        password=PASSWORD,
                                        email=EMAIL)
    def tearDown(self):
        for obj in (self.user,):
            obj.delete()

    def test_reverse_relation(self):
        area_code = AreaCode.objects.create(code='809')
        phone = PhoneNumber.objects.create(phone_number=PHONE_NUMBER,
                                           area_code=area_code,
                                           user=self.user)
        area_code = AreaCode.objects.get(pk=area_code.pk)
        self.assertIn(phone, area_code.phone_numbers.all())


class PhoneNumberManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=USERNAME,
                                        password=PASSWORD,
                                        email=EMAIL)
        self.area_code = AreaCode.objects.create(code='809')
        self.phone1 = PhoneNumber.objects.create(phone_number=PHONE_NUMBER,
                                                 area_code=self.area_code,
                                                 user=self.user)
        self.phone2 = PhoneNumber.objects.create(phone_number=(
                                                     PHONE_NUMBER.replace(
                                                         '3',
                                                         '4',
                                                 )),
                                                 area_code=self.area_code,
                                                 user=self.user)
    
    def tearDown(self):
        for obj in (self.user, self.area_code, self.phone1, self.phone2):
            obj.delete()

    def test_can_set_primary_with_pk_no_user(self):
        PhoneNumber.objects.set_as_primary(self.phone2.pk)
        self.assertTrue(PhoneNumber.objects.get(pk=self.phone2.pk).is_primary)

    def test_can_set_primary_with_str_no_user(self):
        PhoneNumber.objects.set_as_primary(self.phone2.phone_number)
        self.assertTrue(PhoneNumber.objects.get(pk=self.phone2.pk).is_primary)

    def test_can_set_primary_with_obj_no_user(self):
        PhoneNumber.objects.set_as_primary(self.phone2)
        self.assertTrue(PhoneNumber.objects.get(pk=self.phone2.pk).is_primary)

    def test_can_set_primary_with_pk_with_user(self):
        PhoneNumber.objects.set_as_primary(self.phone2.pk)
        self.assertTrue(PhoneNumber.objects.get(pk=self.phone2.pk).is_primary)

    def test_can_set_primary_with_str_with_user(self):
        PhoneNumber.objects.set_as_primary(self.phone2.phone_number)
        self.assertTrue(PhoneNumber.objects.get(pk=self.phone2.pk).is_primary)

    def test_can_set_primary_with_obj_with_user(self):
        PhoneNumber.objects.set_as_primary(self.phone2)
        self.assertTrue(PhoneNumber.objects.get(pk=self.phone2.pk).is_primary)


class PhoneNumberTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username=USERNAME,
                                        password=PASSWORD,
                                        email=EMAIL)
    def tearDown(self):
        self.user.delete()

    def test_can_create(self):
        phone = PhoneNumber.objects.create(phone_number=PHONE_NUMBER,
                                            user=self.user)
        self.assertEqual(phone, PhoneNumber.objects.first())

    def test_first_phone_number_is_primary(self):
        phone = PhoneNumber.objects.create(phone_number=PHONE_NUMBER,
                                            user=self.user)
        self.assertTrue(phone.is_primary)

    def test_phone_numbers_after_first_are_not_primary(self):
        phone1 = PhoneNumber.objects.create(phone_number=PHONE_NUMBER,
                                             user=self.user)
        phone2 = PhoneNumber.objects.create(phone_number=(
                                                PHONE_NUMBER.replace(
                                                    '3',
                                                    '4',
                                            )),
                                            user=self.user)                                            
        self.assertFalse(phone2.is_primary)



class UserManagerTest(TestCase):
    """User manager tests."""

    # def tearDown(self):
    #     for obj in User.objects.all():
    #         obj.delete()

    def test_can_create_user(self):
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        self.assertEqual(user, User.objects.first())

    def test_can_create_superuser(self):
        superuser = User.objects.create_superuser(email=EMAIL,
                                                  username=USERNAME,
                                                  password=PASSWORD)
        self.assertTrue(superuser.is_admin)

    def test_create_superuser_assigns_group_even_if_does_exist(self):
        superusers, created = Group.objects.get_or_create(name='superuser')
        superuser = User.objects.create_superuser(email=EMAIL,
                                                  username=USERNAME,
                                                  password=PASSWORD)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_assigns_group_even_if_does_not_exist(self):
        superusers, created = Group.objects.get_or_create(name='superuser')
        superusers.delete()
        superuser = User.objects.create_superuser(email=EMAIL,
                                                  username=USERNAME,
                                                  password=PASSWORD)
        self.assertTrue(superuser.is_superuser)


class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        out = StringIO()
        call_command('create_initial_groups', stdout=out)
        cls.content_type = ContentType.objects.get_for_model(User)
        cls.perms = Permission.objects.filter(
            content_type=cls.content_type)

    def test_can_create(self):
        user = User.objects.create(username=USERNAME, password=PASSWORD,
                                   email=EMAIL)
        self.assertEqual(User.objects.first(), user)

    def test_can_create_with_all_args(self):
        user = User.objects.create(
            username=USERNAME,
            password=PASSWORD,
            email=EMAIL,
            birth_date='1916-12-21',
            first_names='Alice',
            last_names='Van Der Laand',
        )
        self.assertEqual(User.objects.first(), user)

    def test_is_staff_returns_true_when_true(self):
        group1 = Group.objects.get(name='admin')
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        user.groups.add(group1)
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.is_staff)

    def test_is_staff_returns_false_when_false(self):
        group1 = Group.objects.get(name='recruiter')
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        user.groups.add(group1)
        user = User.objects.get(pk=user.pk)
        self.assertFalse(user.is_staff)

    def test_is_superuser_returns_true_when_true(self):
        group1 = Group.objects.get(name='superuser')
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        user.groups.add(group1)
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.is_superuser)

    def test_is_superuser_returns_false_when_false(self):
        group1 = Group.objects.get(name='recruiter')
        user = User.objects.create_user(email=EMAIL, password=PASSWORD,
                                   username=USERNAME)
        user.groups.add(group1)
        user = User.objects.get(pk=user.pk)
        self.assertFalse(user.is_superuser)

    def test_has_perm_returns_true_when_true(self):
        user = User.objects.create(username=USERNAME, password=PASSWORD, email=EMAIL)
        user.groups.add(Group.objects.get(name='superuser'))
        user.save()
        perms = user.get_group_permissions()
        self.assertIn('delete_site', perms['superuser'])


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class NationalIdTest(TestCase):
    def setUp(self):
        self.user = User(username=USERNAME,
                         email=EMAIL,
                         is_active=True,
                         is_verified=True)
        self.user.set_password(PASSWORD)
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_image_is_deleted_from_filesystem_on_delete(self):
        natid = NationalId.objects.create(
            id_type=ID_TYPE,
            id_number=ID_NUMBER,
            user=self.user,
            verification_image=SimpleUploadedFile(
                name='saved.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/png'
            )
        )
        path = natid.verification_image.file.name
        natid.delete()
        with self.assertRaises(FileNotFoundError):
            open(path, 'rb')

    def test_user_directory_path(self):
        natid = NationalId.objects.create(
            id_type=ID_TYPE,
            id_number=ID_NUMBER,
            user=self.user,
            verification_image=SimpleUploadedFile(
                name='saved.jpg',
                content=open(IMAGE_PATH, 'rb').read(),
                content_type='image/png'
            )
        )
        self.assertIn('cedula_saved.jpg', os.listdir(
            os.path.join(
                TEST_MEDIA_ROOT,
                'user_%s' %(self.user.id,),
                'docs'
            )))


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
            os.path.join(
                TEST_MEDIA_ROOT,
                'user_%s' %(self.user.id,),
                'profile'
            )))
