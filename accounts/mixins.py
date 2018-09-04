import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.utils.timezone import now

# from accounts.views import ConfirmPasswordView


# class ConfirmPasswordMixin(AccessMixin):
#     """
#     Mixin that intercept the request to re-authenticate then redirect
#     the user to the requested (original) view. Used for
#     security locations like paywalls and account management.

#     confirm_success_url needs to be set in order for the mixin to know to which
#     view redirect to.
#     """
#     max_last_login_seconds = 300  # Defaults to 30 minutes

#     def dispatch(self, request, *args, **kwargs):
#         resp = super(ConfirmPasswordMixin, self).dispatch(
#             request, *args, **kwargs)

#         if resp.status_code == 200:
#             delta = datetime.timedelta(seconds=self.max_last_login_seconds)
#             if now() > (request.user.last_login + delta):
#                 return ConfirmPasswordView.as_view(next_page=request.path)
#             else:
#                 return resp
#         return resp
