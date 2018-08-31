"""Applications signals module"""
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User, Profile, EmailAddress

@receiver(post_save, sender=User)
#pylint: disable=W0613
def create_profile_for_user(sender, instance, created, **kwargs):
    """Create and assign a Profile object after a User object is
    created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_email_for_user(sender, instance, created, **kwargs):
    """Create and assign an object after a User object is
    created."""
    if created:
        EmailAddress.objects.create(email=instance.email,
                                    is_primary=True,
                                    user=instance)