"""Accounts models module."""
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    GroupManager,
    Permission
)
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from simple_history import register
from simple_history.models import HistoricalRecords

def user_directory_path(instance, filename):
    """Saves user picture under settings.MEDIA_ROOT"""
    return f'user_{instance.id}/profile/{filename}'

def reduce_to_alphanum(string):
    """Removes all non alphanumeric characters from string."""
    return ''.join(c if c.isalnum() else '' for c in string)

# if not hasattr(Group, 'parent'):
#     #pylint: disable=C0103
#     field = models.ForeignKey(Group, blank=True, null=True,
#                               related_name='children',
#                               on_delete=models.SET_NULL)
#     field.contribute_to_class(Group, 'parent')


NON_EDITABLE_GROUPS = [
    'superuser',
    'admin',
    'supervisor',
    'human_resources',
    'recruiter',
    'sourcer',
    'hiring_manager',
    'lab_manager',
    'reporting',
    'payroll',
    'employee',
    'candidate',
    'ANON',
    'BOT',
]

def get_group_user(instance, **kwargs):
    return instance.modified_by

# register(Poll, get_user=get_poll_user)

# monkey-patch original Group model
# Group.add_to_class('modified_by', models.ForeignKey(
#     'accounts.User',
#     on_delete=models.CASCADE,
#     blank=True,
#     null=True,
#     related_name='%(app_label)s_%(class)s_modified_by',
# ))
Group.add_to_class('is_supervisor', models.BooleanField(default=False))
Group.add_to_class('is_admin', models.BooleanField(default=False))
# Group.add_to_class('history', HistoricalRecords())
# simple_history register Groups and Permissions
register(Group)
register(Permission)

class EmailAddressManager(models.Manager):
    """Custom manager for email addresses."""
    def set_as_primary(self, email, user=None):
        """
        Sets an email as primary for a particular user.
        """
        if isinstance(email, int):
            email = self.get_queryset().get(pk=email)
        if isinstance(email, str):
            email = self.get_queryset().get(email=email)
        if user is None:
            user = email.user
        user.email_addresses.all().update(is_primary=False)
        self.get_queryset().filter(pk=email.pk).update(is_primary=True)
        User.objects.filter(pk=user.pk).update(email=email.email)
        return email


class EmailAddress(models.Model):
    """Email address model."""
    email = models.EmailField(unique=True, blank=False, null=False)
    is_primary = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='email_addresses',
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_modified_by',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))
    history = HistoricalRecords()

    objects = EmailAddressManager()

    def __str__(self):
        return '%s: %s' % (self.user.username, self.email,)

    def save(self, *args, **kwargs):
        if self.user.email_addresses.count() == 0:
            self.is_primary = True
        self.full_clean()
        super(EmailAddress, self).save(*args, **kwargs)


class ModGroupManager(models.Manager):
    """Custom manager for ModGroup."""
    def get_supervisor_groups(self):
        return super(ModGroupManager, self
                    ).get_queryset().filter(is_supervisor=True)

    def get_admin_groups(self):
        return super(ModGroupManager, self
                    ).get_queryset().filter(is_admin=True)                    


class ModGroup(Group):
    """Extended django.contrib.auth.models.Group with history and
    created_at fields."""

    mod_manager = ModGroupManager()

    class Meta:
        proxy = True

    def get_all_perms(self):
        """Convenience method to return a concatenated string with all
        permissions."""
        return ', '.join([p.codename for p in self.permissions.all()])

    @property
    def _editable(self):
        if not self.name in NON_EDITABLE_GROUPS:
            return True
        return False


class AreaCode(models.Model):
    """Area code model to display in application form."""
    PREFIX_CHOICES = [
        '+1',
        '+502',
        '+504',
        '+507',
        '+509',
        '+51',
        '+52',
        '+55',
        '+58',
        '+63',
    ]
    display_in_form = models.BooleanField(default=False, blank=False)
    name = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_modified_by',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))
    history = HistoricalRecords()
    PREFIX_CHOICES = [
        (i, c) for i, c in zip(
            list(range(len(PREFIX_CHOICES))), PREFIX_CHOICES)]
    country = models.ForeignKey('admin_console.Country',
                                related_name='area_codes',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    prefix = models.IntegerField(choices=PREFIX_CHOICES,
                                 blank=False, default=0)
    code = models.CharField(max_length=5, blank=False)

    def __str__(self):
        if self.country:
            return '%s: %s %s' % (self.country.name, self.get_prefix_display(), self.code,)
        return self.code

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(AreaCode, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if not self.name:
            if self.country:
                self.name = self.country.name
            self.name = self.code
        return super(AreaCode, self).clean(*args, **kwargs)

    class Meta:
        verbose_name = _('Area code')
        ordering = ('name',)

    @property
    def _history_user(self):
        return self.modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value


class PhoneNumberManager(models.Manager):
    def set_as_primary(self, phone_number, user=None):
        """
        Sets an phone number as primary for a particular user.
        """
        if isinstance(phone_number, int):
            phone_number = self.get_queryset().get(pk=phone_number)
        if isinstance(phone_number, str):
            phone_number = self.get_queryset().get(phone_number=phone_number)
        if user is None:
            user = phone_number.user
        user.phone_numbers.all().update(is_primary=False)
        self.get_queryset().filter(pk=phone_number.pk).update(is_primary=True)
        return phone_number


class PhoneNumber(models.Model):
    """Model to unify all Phone related stuff."""
    phone_number = models.CharField(max_length=12, blank=False)
    is_primary = models.BooleanField(default=False)
    area_code = models.ForeignKey(
        'accounts.AreaCode',
        related_name='phone_numbers',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='phone_numbers',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    history = HistoricalRecords()
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_modified_by',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))
    objects = PhoneNumberManager()

    def __str__(self):
        return '(%s)%s-%s' % (self.area_code, self.phone_number[:3], self.phone_number[3:])

    def save(self, *args, **kwargs):
        if self.user.phone_numbers.count() == 0:
            self.is_primary = True
        self.full_clean()
        super(PhoneNumber, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.phone_number = reduce_to_alphanum(self.phone_number)
        super(PhoneNumber, self).clean(*args, **kwargs)

    @property
    def _history_user(self):
        return self.modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value


class CustomUserManager(BaseUserManager):
    """Base manager for user model."""
    def create_user(self, username, email, password=None, **extra_fields):
        """Creates basic user with basic permissions (via Group
        assignment)."""
        if not email:
            raise ValueError('Users must have a valid email address')
        email = self.normalize_email(email)
        if password is None:
            password = self.make_random_password()
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email=None):
        """Creates super user with all permissions."""
        user = self.create_user(username=username,
                                email=email,
                                password=password)
        user.is_active = True
        #pylint: disable=W0612
        try:
            superusers = Group.objects.get(name='superuser')
        except Group.DoesNotExist:
            superusers = Group.objects.create(name='superuser',
                                              is_supervisor=True,
                                              is_admin=True)
        user.groups.add(superusers)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Base user model."""
    ACTIVE = 0
    TERMED = 1
    NEVER_EMPLOYED = 2
    NON_REHIRABLE = 3
    EMPLOYEE_STATUS_CHOICES = (
        (ACTIVE, _('Active')),
        (TERMED, _('Termed')),
        (NEVER_EMPLOYED, _('Never worked for us')),
        (NON_REHIRABLE, _('Non-rehirable')),
    )
    username = models.CharField(max_length=30, unique=True, blank=True, null=True)
    username_slug = models.SlugField(unique=True, editable=False, blank=True, null=True)
    email = models.EmailField(blank=False)
    first_names = models.CharField(max_length=100, blank=True, default='')
    last_names = models.CharField(max_length=100, blank=True, default='')
    birth_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    accepted_tos = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    employee_status = models.IntegerField(choices=EMPLOYEE_STATUS_CHOICES,
                                          default=NEVER_EMPLOYED)
    history = HistoricalRecords()

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def clean(self, *args, **kwargs):
        self.username_slug = slugify(self.username)
        super(User, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        """Returns full name of the user in the format
        "first_name + last_name + username" (no email)."""
        if self.first_names and self.last_names:
            return "%s %s - %s" % (self.first_names, self.last_names, self.username)
        return self.username

    def get_short_name(self):
        """Return user's username."""
        return self.username

    # def has_perm(self, perm, obj=None):
    #     if not self.is_admin:

    #     return True

    # def has_module_perms(self, app_label):
    #     return True

    @property
    def is_staff(self):
        """Returns true if the user is the supervisor, admin or superuser groups."""
        groups = self.groups.all().values_list('name', flat=True)
        supervisor_groups = (
            ModGroup
            .mod_manager
            .get_supervisor_groups()
            .values_list('name', flat=True))
        return bool(set(groups).intersection(set(supervisor_groups)))

    @property
    def is_admin(self):
        """Returns true if the user is the admin or superuser groups."""
        groups = self.groups.all().values_list('name', flat=True)
        supervisor_groups = (
            ModGroup
            .mod_manager
            .get_admin_groups()
            .values_list('name', flat=True))
        return bool(set(groups).intersection(set(supervisor_groups)))

    @property
    def is_superuser(self):
        """Returns true if the user is the superuser."""
        return 'superuser' in self.groups.all().values_list('name', flat=True)

    def get_group_permissions(self, obj=None):
        """
        Returns a dict with all group permissions, as a flat list under
        each group's name.
        e.g. {'admin': ['can_add_user, 'can_delete_user']}
        """
        return {group.name: list(group.permissions.all().values_list('codename', flat=True))
                 for group in self.groups.all()}


class NationalId(models.Model):
    """
    Simple national ID model with type & number fields, extended with a
    history and user FKs.
    """
    CEDULA = 0
    PASSPORT = 1
    SSN = 2
    ID_TYPE_CHOICES = (
        (CEDULA, _('Cedula')),
        (PASSPORT, _('Passport')),
        (SSN, _('Social Security Number'))
    )
    id_type = models.IntegerField(
        choices=ID_TYPE_CHOICES,
        default=CEDULA,
        help_text=_('ID Type: Cedula, SSN, Passport'),
    )
    id_number = models.CharField(max_length=15, blank=False)
    is_verified = models.BooleanField(default=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='national_id',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    history = HistoricalRecords()
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_last_modified',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))

    def save(self, *args, **kwargs):
        self.full_clean()
        super(NationalId, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.id_number = reduce_to_alphanum(self.id_number)
        super(NationalId, self).clean(*args, **kwargs)

    def __str__(self):
        nat = self.id_number
        _type = self.id_type
        if _type == 0:
            _id = '%s-%s-%s' % (nat[:3], nat[3:10], nat[-1:])
        elif _type == 1:
            _id = nat
        elif _type == 2:
            _id = '%s-%s-%s' % (nat[:3], nat[3:5], nat[-4:])
        return _id

    @property
    def _history_user(self):
        return self.modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value


class Profile(models.Model):
    """Model to contain additional, non-essential info from a user."""
    MALE = 0
    FEMALE = 1
    GENDER_CHOICES = (
        (MALE, _('Male')),
        (FEMALE, _('Female')),
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=MALE)
    bio = models.TextField(default='', blank=True)
    picture = models.ImageField(blank=True, null=True,
                                upload_to=user_directory_path)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='profile',
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)
    history = HistoricalRecords()
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_last_modified',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def delete(self, *args, **kwargs):
        self.picture.delete(save=False)
        super(Profile, self).delete(*args, **kwargs)

    def __str__(self):
        return 'Profile of %s' % (self.user.username,)

    @property
    def _history_user(self):
        return self.modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value
