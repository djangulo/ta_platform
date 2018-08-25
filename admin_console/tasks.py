# """Applications signals module"""
# from django.core.mail import EmailMessage
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.template import Context
# from django.template.loader import get_template

# from applications.models import Application
# from applications.tasks import send_user_email
# from accounts.models import Profile

# @receiver(post_save, sender=Profile)
# #pylint: disable=W0613
# def create_user_post_person_creation(sender, instance, **kwargs):
#     """Create and assign a Profile object after an pplication is
#     created."""
#     try:
#         profile = Profile.objects.get(natid=instance.national_id_number)
#     except Profile.DoesNotExist:
#         profile = Profile.objects.create(first_names=instance.first_names,
#                                        last_names=instance.last_names,
#                                        primary_phone=instance.primary_phone,
#                                        secondary_phone=instance.secondary_phone,
#                                        email=instance.email,
#                                        birth_date=instance.birth_date,
#                                        natid_type=instance.national_id_type,
#                                        natid=instance.national_id_number)
#     profile.applications.add(instance)

# @receiver(post_save, sender=Application)
# def send_user_creation_email(sender, instance, **kwargs):
#     send_user_email.delay(instance.email)
