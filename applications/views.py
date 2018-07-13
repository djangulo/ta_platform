from django.views.generic import FormView


from applications.forms import ApplicationForm

class ApplicationView(FormView):
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'
