from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect


def home(request):
    return render(request, 'home.html', context={
        'COMPANY_NAME': settings.BRAND_DICT['COMPANY_NAME'],
    })
