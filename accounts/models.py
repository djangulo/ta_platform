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

from admin_console.models import AreaCode


def user_directory_path(instance, filename):
    return f'user_{instance.id}/profile/{filename}'

def reduce_to_alphanum(string):
    return ''.join(c if c.isalnum() else '' for c in string)

if not hasattr(Group, 'parent'):
    field = models.ForeignKey(Group, blank=True, null=True,
                              related_name='children',
                              on_delete=models.SET_NULL)
    field.contribute_to_class(Group, 'parent')


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
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


    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user





class User(AbstractBaseUser, PermissionsMixin):
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
        if self.username:
            return self.username
        else:
            return self.email

    def clean(self, *args, **kwargs):
        if self.username is None:
            self.username = self.email.split('@')[0]
        super(User, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
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


class ModGroup(Group):
    slug = models.SlugField(editable=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    history = HistoricalRecords()
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_last_modified',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))

    # class Meta:
    #     proxy = True

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ModGroup, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name)
        super(ModGroup, self).clean(*args, **kwargs)

    def get_all_perms(self):
        return ', '.join([p.name for p in self.permissions.all()])

    @property
    def _history_user(self):
        return self.modified_by
    
    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value


class NationalId(models.Model):
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
        t = self.id_type
        if t == 0:
            return '%s-%s-%s' % (nat[:3], nat[3:10], nat[-1:])
        if t == 1:
            return nat
        if t == 2:
            return '%s-%s-%s' % (nat[:3], nat[3:5], nat[-4:])

    @property
    def _history_user(self):
        return self.modified_by
    
    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value


class Profile(models.Model):
    MALE = 0
    FEMALE = 1
    GENDER_CHOICES = (
        (MALE, _('Male')),
        (FEMALE, _('Female')),
    )
    birth_date = models.DateField(blank=True, null=True)
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
