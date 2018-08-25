"""Admin console models."""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from accounts.models import reduce_to_alphanum

class BaseSupportModel(models.Model):
    """Base model for all helper models in admin_console."""
    display_in_form = models.BooleanField(default=False, blank=False)
    name = models.CharField(max_length=50, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    modified_by = (
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='%(app_label)s_%(class)s_modified_by',
                          on_delete=models.SET_NULL, null=True,
                          blank=True))
    history = HistoricalRecords()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(BaseSupportModel, self).save(*args, **kwargs)

    @property
    def _history_user(self):
        return self.modified_by

    @_history_user.setter
    def _history_user(self, value):
        self.modified_by = value



class Address(BaseSupportModel):
    """Address model."""
    associated_name = models.CharField(max_length=100, blank=False,
                                       help_text=_('Enter a name to remember'\
                                       'this address by.'))
    state_province_region = models.CharField(max_length=50, blank=True)
    address_line_one = models.CharField(max_length=150, blank=False)
    address_line_two = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=14, blank=False)
    is_primary = models.BooleanField(default=False)
    # latlng = JSONField(blank=True, editable=False, null=True) # psql version
    formatted_name = models.CharField(max_length=500, blank=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='addresses',
        on_delete=models.CASCADE
    )
    country = models.ForeignKey(
        'admin_console.Country',
        related_name='addresses',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    city = models.ForeignKey(
        'admin_console.CityTown',
        related_name='addresses',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    sector = models.ForeignKey(
        'admin_console.CitySector',
        related_name='addresses',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    phone_number = models.ForeignKey(
        'admin_console.PhoneNumber',
        related_name='addresses',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    state_province_region = models.ForeignKey(
        'admin_console.StateProvinceRegion',
        related_name='addresses',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
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
        return f'address of %s' % (self.user.username,)


class Institution(BaseSupportModel):
    """Curated institution (or college) model."""
    short_name = models.CharField(max_length=15, unique=True, blank=False)
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('institution')
        verbose_name_plural = _('institutions')

class Career(BaseSupportModel):
    """Curated career model."""
    industry = models.CharField(max_length=50, unique=True)
    institution = models.ForeignKey(
        'admin_console.Institution',
        null=True,
        blank=True,
        related_name='careers',
        on_delete=models.SET_NULL,
    )


class Shift(BaseSupportModel):
    """
    Represents a work-shift that should be available to applicatnts.
    """
    # look into making a time-based calendar-like field
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('shift')
        verbose_name_plural = _('shifts')


class Language(BaseSupportModel):
    """Curated language model to display in application form."""
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('language')
        verbose_name_plural = _('languages')


class AreaCode(BaseSupportModel):
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
    PREFIX_CHOICES = [(i, c) for i, c in zip(list(range(len(PREFIX_CHOICES))), PREFIX_CHOICES)]
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

    class Meta(BaseSupportModel.Meta):
        verbose_name = _('Area code')
        ordering = ('name',)


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
        user.email_addresses.all().update(is_primary=False)
        self.get_queryset().filter(pk=phone_number.pk).update(is_primary=True)
        return phone_number


class PhoneNumber(models.Model):
    """Model to unify all Phone related stuff."""
    phone_number = models.CharField(max_length=12, blank=False)
    is_primary = models.BooleanField(default=False)
    area_code = models.ForeignKey(
        'admin_console.AreaCode',
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

    def __str__(self):
        return '(%s)%s-%s' % (self.area_code, self.phone_number[:3], self.phone_number[3:])

    def save(self, *args, **kwargs):
        self.full_clean()
        super(PhoneNumber, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.area_code = reduce_to_alphanum(self.area_code)
        self.phone_number = reduce_to_alphanum(self.phone_number)
        super(PhoneNumber, self).clean(*args, **kwargs)


class CityTown(BaseSupportModel):
    """City or town model."""
    # conforming to a single standard (DR or US) narrows the scope too
    # much. It's left open, individual use-cases may have different
    # setups
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('city or town')
        ordering = ('name',)


class CitySector(BaseSupportModel):
    """City subdivision model."""
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('city sector')
        ordering = ('name',)


class StateProvinceRegion(BaseSupportModel):
    """Country subdivision model."""
    country = models.ForeignKey(
        'admin_console.Country',
        related_name='division_set',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('State, province or region')
        verbose_name_plural = _('States, provinces or regions')
        ordering = ('name',)


class Country(BaseSupportModel):
    """Curated country model."""
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ('name',)


class CallCenter(BaseSupportModel):
    """Curated call center model."""
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('call center')
        verbose_name_plural = _('call centers')


class AreaOfExpertise(BaseSupportModel):
    """Curated area of expertise model."""
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('area of experience')
        verbose_name_plural = _('areas of experience')


class ApplicationStatus(BaseSupportModel):
    """Curated application status model."""
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('application status')
        verbose_name_plural = _('application status')

class DeclinedReason(BaseSupportModel):
    """Curated declined reason."""
    class Meta(BaseSupportModel.Meta):
        verbose_name = _('declined reason')
        verbose_name_plural = _('declined reasons')
