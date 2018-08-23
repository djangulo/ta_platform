from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'


def home(request):
    return render(request, 'home.html', context={
        'BRANDING': False,
        'COMPANY_NAME': 'MyCo DR',
    })
