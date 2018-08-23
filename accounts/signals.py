"""Applications signals module"""
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User, Profile

@receiver(post_save, sender=User)
#pylint: disable=W0613
def create_profile_for_user(sender, instance, **kwargs):
    """Create and assign a Profile object after a User object is
    created."""
    Profile.objects.get_or_create(user=instance)
