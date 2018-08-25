from django.http import HttpResponseRedirect
from django.views.generic import (
    DetailView,
    UpdateView,
    ListView,
    TemplateView,
    CreateView
)
from django.urls import reverse_lazy
from django.utils import timezone

from accounts.models import ModGroup, User, Profile
from admin_console.forms import AdminUserCreationForm, GroupForm

EIGHTEEN_YEARS_AGO = (timezone.now() - timezone.timedelta(days=((365*18)+5))
                      ).strftime('%m/%d/%Y')



class AdminHomeView(TemplateView):
    template_name = 'admin_console/home.html'


class AdminAccountsView(TemplateView):
    template_name = 'admin_console/accounts.html'

class GroupListView(ListView):
    model = ModGroup
    template_name = 'admin_console/modgroup_list.html'


class GroupCreateView(CreateView):
    model = ModGroup
    template_name = 'admin_console/modgroup_form.html'
    from_class = GroupForm
    fields = ('name', 'permissions', )


class GroupDetailView(DetailView):
    model = ModGroup
    template_name = 'admin_console/modgroup_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(GroupDetailView, self
            ).get_context_data(*args, **kwargs)
        context['permissions'] = self.get_object().permissions.all()
        return context


class GroupUpdateView(UpdateView):
    model = ModGroup
    form_class = GroupForm
    template_name = 'admin_console/modgroup_form.html'



class UserListView(ListView):
    model = Profile
    template_name = 'admin_console/user_list.html'


class UserCreateView(CreateView):
    model = Profile
    form_class = AdminUserCreationForm
    template_name = 'admin_console/user_form.html'
    # success_url = reverse_lazy('admin_console:user-detail')
    initial = {
        'birth_date': EIGHTEEN_YEARS_AGO
    }
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        instance = form.save()
        clean_data = form.cleaned_data
        if clean_data['display_name'] is not None:
            username = clean_data['display_name']
        user = User.objects.create_user(clean_data['email'],
                                        username=username)
        user.groups.set([g for g in clean_data['groups']])
        instance.user = user
        user.save()
        instance.save()
        return super(UserCreateView, self).form_valid(form)

    # def get_success_url(self):
    #     obj = self.get_object()
    #     return HttpResponseRedirect(reverse_lazy('admin_console:user-detail'),
    #                                 obj.user.pk)



class UserDetailView(DetailView):
    model = Profile
    template_name = 'admin_console/user_detail.html'

    def get_context_data(self, *args, **kwargs):
        profile = self.get_object()
        context = super(UserDetailView, self
            ).get_context_data(*args, **kwargs)
        context['permissions'] = profile.user.user_permissions.all()
        context['groups'] = profile.user.groups.all()

        return context




class UserUpdateView(UpdateView):
    model = Profile
    form_class = AdminUserCreationForm
    template_name = 'admin_console/user_form.html'
    success_url = reverse_lazy('admin_console:user-detail')

    def get_success_url(self, *args, **kwargs):
        obj = self.get_object()
        print('\n\n\n -=-=-=-=-=-=-=-=--==-\n pk {}\n\n\n\n\n -=-=-=-=='.format(obj.pk))
        return HttpResponseRedirect(
            reverse_lazy('admin_console:user-detail', kwargs={'pk': obj.pk}))

