"""Brand context processor (for all brand variables)"""

from django.conf import settings

def get_brand_dict(request):
    return settings.BRAND_DICT

def get_brand_bool(request):
    return {'BRANDING': settings.BRANDING}
