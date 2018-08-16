from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from applications.models import Application
from accounts.models import Person

@receiver(post_save, sender=Application)
def assign_person_to_application(sender, instance, **kwargs):
    try:
        person = Person.objects.get(natid=instance.national_id_number)
    except Person.DoesNotExist:
        person = Person.objects.create(first_names=instance.first_names,
                                       last_names=instance.last_names,
                                       primary_phone=instance.primary_phone,
                                       secondary_phone=instance.secondary_phone,
                                       email=instance.email,
                                       birth_date=instance.birth_date,
                                       natid_type=instance.national_id_type,
                                       natid=instance.national_id_number)
    person.applications.add(instance)
