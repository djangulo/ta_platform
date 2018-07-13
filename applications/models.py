import re
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from string import punctuation

from accounts.models import NationalId, Person, User

class SupportModel(models.Model):
    display_in_form = models.BooleanField(default=False, blank=False)
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Institution(SupportModel):
    short_name = models.CharField(max_length=15, unique=True, blank=False)


class Career(SupportModel):
    industry = models.CharField(max_length=50, unique=True)
    institution = models.ForeignKey(
        'applications.Institution',
        null=True,
        blank=True,
        related_name='careers',
        on_delete=models.SET_NULL,
    )


class Shift(SupportModel):
    class Meta(SupportModel.Meta):
        verbose_name = _('shift')
        verbose_name_plural = _('shifts')


class Language(SupportModel):
    class Meta(SupportModel.Meta):
        verbose_name = _('language')
        verbose_name_plural = _('languages')

class CityTown(SupportModel):
    class Meta(SupportModel.Meta):
        verbose_name = _('city or town')
        ordering = ('name',)

class CallCenter(SupportModel):
    class Meta(SupportModel.Meta):
        verbose_name = _('call center')
        verbose_name_plural = _('call centers')

class AreaOfExperience(SupportModel):
    class Meta(SupportModel.Meta):
        verbose_name = _('area of experience')
        verbose_name_plural = _('areas of experience')

class Application(models.Model):
    CEDULA = 0
    PASSPORT = 1
    SSN = 2
    ID_TYPE_CHOICES = (
        (CEDULA, _('Cedula')),
        (PASSPORT, _('Passport')),
        (SSN, _('Social Security Number'))
    )
    MALE = 0
    FEMALE = 1
    RATHERNOT = 2
    GENDER_CHOICES = (
        (MALE, _('Male')),
        (FEMALE, _('Female')),
        (RATHERNOT, _('Rather not say')),
    )
    first_names = models.CharField(max_length=100, blank=False)
    last_names = models.CharField(max_length=100, blank=False)
    primary_phone = models.CharField(max_length=15, blank=False)
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=False)
    lived_in_usa = models.BooleanField(default=False)
    birth_date = models.DateField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True, editable=False)
    national_id_type = models.IntegerField(choices=ID_TYPE_CHOICES,
                                           default=CEDULA)
    national_id_number = models.CharField(max_length=15, blank=False)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=MALE)
    address_line_one = models.CharField(max_length=150, blank=False)
    address_line_two = models.CharField(max_length=150, blank=True)
    active_studies = models.BooleanField(default=False)
    career = models.CharField(max_length=50, blank=True)
    institution = models.CharField(max_length=150, blank=True)

    currently_employed = models.BooleanField(default=False, blank=True)
    current_employer = models.CharField(max_length=50, blank=True)

    languages = models.ManyToManyField(
        'applications.Language',
        related_name='applicants',
        blank=True,
    )
    previous_call_center_xp = models.BooleanField(default=False, blank=True)
    previous_call_center = models.ManyToManyField(
        'applications.CallCenter',
        related_name='applications',
        blank=True,
    )
    city_or_town = models.ForeignKey(
        'applications.CityTown',
        related_name='applications',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    areas_of_expertise = models.ManyToManyField(
        'applications.AreaOfExperience',
        related_name='applicants',
        blank=True,
    )

    pre_screen = models.BooleanField(default=False, blank=True)
    hire_iq = models.IntegerField(blank=True, null=True)
    tss = models.BooleanField(default=False, blank=True)
    hm_interview = models.BooleanField(default=False, blank=True)

    person = models.ForeignKey(
        'accounts.Person',
        related_name='applications',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    national_id = models.ForeignKey(
        'accounts.NationalId',
        related_name='applications',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _('application')
        verbose_name_plural = _('applications')
        permissions = (
            ('change_status', _('can change status')),
            ('view_status', _('can view status')),
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Application, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.create_person_if_none()
        super(Application, self).clean(*args, **kwargs)

    def clean_stringf(self, value):
        return value.strip(punctuation)

    def create_person_if_none(self):
        by_natid = NationalId.objects.filter(
            id_number=self.clean_stringf(self.national_id_number)).first()
        by_phone = Person.objects.filter(
            primary_phone=self.clean_stringf(self.primary_phone)).first()
        by_email = User.objects.filter(
            email=self.email).first()
        # import pdb; pdb.set_trace()
        if by_natid is not None:
            self.person = by_natid.owner
            self.national_id = by_natid
        elif by_phone is not None:
            self.person = by_phone
            self.national_id = self.person.national_id
        elif by_email is not None:
            self.person = by_email.person
            self.national_id = self.person.national_id
        # else:
        #     User.objects.create_user(email=self.email, )



