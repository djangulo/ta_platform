from django.conf import settings
from django.views.generic import FormView
from django.shortcuts import render, get_object_or_404, redirect

from applications.forms import ApplicationForm


def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.save()
    else:
        form = ApplicationForm()
    return render(request, 'applications/application_form.html', context={
            'form': form,
            'COMPANY_NAME': settings.BRAND_DICT['COMPANY_NAME'],
        })


def edit_application(request, id=None):
    application = get_object_or_404(Application, id=id)    
    form = ApplicationForm(request.Post or None, instance=application)
    if form.is_valid():
        form.save()
    return render(request, 'applications/application_form.htlm', {'form': form})

