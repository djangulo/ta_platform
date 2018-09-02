"""Brand context processor (for all brand variables)"""
from django.conf import settings
from django.utils.translation import get_language

def get_brand_dict(request):
    return settings.BRAND_DICT

def get_brand_bool(request):
    return {'BRANDING': settings.BRANDING}
