"""Accounts models module."""
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
)
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

def user_directory_path(instance, filename):
    """Saves user picture under settings.MEDIA_ROOT"""
    return f'user_{instance.id}/profile/{filename}'

def reduce_to_alphanum(string):
    """Removes all non alphanumeric characters from string."""
    return ''.join(c if c.isalnum() else '' for c in string)

if not hasattr(Group, 'parent'):
    #pylint: disable=C0103
    field = models.ForeignKey(Group, blank=True, null=True,
                              related_name='children',
                              on_delete=models.SET_NULL)
    field.contribute_to_class(Group, 'parent')

class CustomUserManager(BaseUserManager):
    """Base manager for user model."""
    def create_user(self, email, password=None, username=None, **extra_fields):
        """Creates basic user with basic permissions (via ModGroup
        assignment)."""
        if not email:
            raise ValueError('Users must have a valid email address')
        email = self.normalize_email(email)
        if password is None:
            password = self.make_random_password()
        if username is None:
            username = email.split('@')[0]
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates super user with all permissions."""
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.is_active = True
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
    email = models.EmailField(blank=False, unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def clean(self, *args, **kwargs):
        if self.username is None:
            self.username = self.email.split('@')[0]
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

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        """Returns true if the user is the supervisor, admin or superuser groups."""
        groups = self.groups.all().values_list('name', flat=True)
        return any(['superuser' in groups,
                    'admin' in groups,
                    'supervisor' in groups])

    @property
    def is_superuser(self):
        """Returns true if the user is the superuser."""
        return 'superuser' in self.groups.all().values_list('name', flat=True)


class ModGroup(Group):
    """Extended django.contrib.auth.models.Group with history and
    created_at fields."""
    slug = models.SlugField(editable=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_modified',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))

    def save(self, *args, **kwargs):
        """Extended save but to implement the full_clean."""
        self.full_clean()
        super(ModGroup, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """Extended clean but to implement the auto-slug."""
        if self.slug is None:
            self.slug = slugify(self.name)
        super(ModGroup, self).clean(*args, **kwargs)

    def get_all_perms(self):
        """Convenience method to return a concatenated string with all
        permissions."""
        return ', '.join([p.name for p in self.permissions.all()])

    @property
    def _history_user(self):
        return self.modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value


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
