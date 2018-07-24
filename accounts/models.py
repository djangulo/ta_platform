import re
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from string import punctuation

def person_directory_path(instance, filename):
    return f'user_{instance.id}/profile/{filename}'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have a valid email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=False, unique=True)
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return True
    
    @property
    def is_superuser(self):
        return True


class Address(models.Model):
    associated_name = models.CharField(max_length=100, blank=False)
    state_province_region = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    sector = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=200, default='Dominican Republic')
    address_line_one = models.CharField(max_length=150, blank=False)
    address_line_two = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=14, blank=False)
    is_primary = models.BooleanField(default=False, editable=False)
    # latlng = JSONField(blank=True, editable=False, null=True) # psql version
    formatted_name = models.CharField(max_length=500, blank=True, editable=False)
    owner = models.ForeignKey(
        'accounts.Person',
        related_name='addresses',
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Address, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.formatted_name = ', '.join((
            f'{self.address_line_one}',
            f'{self.sector}',
            f'{self.city}',
            f'{self.state_province_region}',
            f'{self.country}'
        ))
        super(Address, self).clean(*args, **kwargs)

    def __str__(self):
        return f'{self.owner.display_name}: address_{self.id}'

# Retiring this (for now)
# class NationalId(models.Model):
#     CEDULA = 0
#     PASSPORT = 1
#     SSN = 2
#     ID_TYPE_CHOICES = (
#         (CEDULA, _('Cedula')),
#         (PASSPORT, _('Passport')),
#         (SSN, _('Social Security Number'))
#     )
#     id_type = models.IntegerField(
#         choices=ID_TYPE_CHOICES,
#         default=CEDULA,
#         help_text='ID Type: Cedula, SSN, Passport'
#     )
#     id_number = models.CharField(max_length=15, blank=False)
#     owner = models.OneToOneField(
#         'accounts.Person',
#         related_name='national_id',
#         on_delete=models.CASCADE,
#     )

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super(NationalId, self).save(*args, **kwargs)

#     def clean(self, *args, **kwargs):
#         self.id_number = self.id_number.strip(punctuation)
#         super(NationalId, self).clean(*args, **kwargs)

#     def __str__(self):
#         if self.id_type == 0:
#             return f'{self.id_number[:3]}-{self.id_number[3:10]}-{self.id_number[-1:]}'
#         elif self.id_type == 1:
#             return f'{self.id_number}'
#         elif self.id_type == 2:
#             return f'{self.id_number[:3]}-{self.id_number[3:5]}-{self.id_number[-4:]}'


class Person(models.Model):
    CEDULA = 0
    PASSPORT = 1
    SSN = 2
    ID_TYPE_CHOICES = (
        (CEDULA, _('Cedula')),
        (PASSPORT, _('Passport')),
        (SSN, _('Social Security Number'))
    )
    first_names = models.CharField(max_length=100, blank=False)
    last_names = models.CharField(max_length=100, blank=False)
    email = models.EmailField(blank=False)
    display_name = models.CharField(max_length=125, blank=True, null=True)
    primary_phone = models.CharField(max_length=15, blank=False)
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(default='', blank=True)
    natid_type = models.IntegerField(
        choices=ID_TYPE_CHOICES,
        default=CEDULA,
        help_text='ID Type: Cedula, SSN, Passport'
    )
    natid = models.CharField(max_length=15, blank=False, unique=True)
    picture = models.ImageField(
        upload_to=person_directory_path,
        blank=True,
        null=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='person',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'person'
        verbose_name_plural = 'persons'
        indexes = [
            models.Index(fields=['natid']),
            models.Index(fields=['primary_phone']),
        ]


    def save(self, *args, **kwargs):
        self.full_clean()
        super(Person, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.display_name is None:
            self.display_name = f'{self.first_names} {self.last_names}'
        self.primary_phone = self.primary_phone.strip(punctuation)
        if self.secondary_phone:
            self.secondary_phone = self.secondary_phone.strip(punctuation)
        super(Person, self).clean(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.picture.delete(save=False)
        super(Person, self).delete(*args, **kwargs)

    def __str__(self):
        return '%s %s (%s: %s)' % (self.first_names, self.last_names,
                                self.get_natid_type_display(),
                                self.natid)

