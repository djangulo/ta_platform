from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from urllib.parse import unquote

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, translate_url
from django.utils.http import is_safe_url
from django.utils.translation import (
    LANGUAGE_SESSION_KEY, check_for_language,
)

LANGUAGE_QUERY_PARAMETER = 'language'
class HomeView(TemplateView):
    template_name = 'home.html'

# def set_language(request):
#     """
#     Redirect to a given URL while setting the chosen language in the session
#     (if enabled) and in a cookie. The URL and the language code need to be
#     specified in the request parameters.

#     Since this view changes how the user will see the rest of the site, it must
#     only be accessed as a POST request. If called as a GET request, it will
#     redirect to the page in the request (the '_next' parameter) without changing
#     any state.
#     """
#     _next = request.POST.get('_next', request.GET.get('_next'))
#     if ((_next or not request.is_ajax()) and
#             not is_safe_url(url=_next, allowed_hosts={request.get_host()}, require_https=request.is_secure())):
#         _next = request.META.get('HTTP_REFERER')
#         _next = _next and unquote(_next)  # HTTP_REFERER may be encoded.
#         if not is_safe_url(url=_next, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
#             _next = '/'
#     response = HttpResponseRedirect(_next) if _next else HttpResponse(status=204)
#     if request.method == 'POST':
#         lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
#         if lang_code and check_for_language(lang_code):
#             if _next:
#                 next_trans = translate_url(_next, lang_code)
#                 if next_trans != _next:
#                     response = HttpResponseRedirect(next_trans)
#             if hasattr(request, 'session'):
#                 request.session[LANGUAGE_SESSION_KEY] = lang_code
#             response.set_cookie(
#                 settings.LANGUAGE_COOKIE_NAME, lang_code,
#                 max_age=settings.LANGUAGE_COOKIE_AGE,
#                 path=settings.LANGUAGE_COOKIE_PATH,
#                 domain=settings.LANGUAGE_COOKIE_DOMAIN,
#             )
#     if request.method == 'GET':
#         lang_code = request.GET.get(LANGUAGE_QUERY_PARAMETER)
#         import pdb; pdb.set_trace()
#         if lang_code and check_for_language(lang_code):
#             if _next:
#                 next_trans = translate_url(_next, lang_code)
#                 if next_trans != _next:
#                     response = HttpResponseRedirect(next_trans)
#             if hasattr(request, 'session'):
#                 request.session[LANGUAGE_SESSION_KEY] = lang_code
#             response.set_cookie(
#                 settings.LANGUAGE_COOKIE_NAME, lang_code,
#                 max_age=settings.LANGUAGE_COOKIE_AGE,
#                 path=settings.LANGUAGE_COOKIE_PATH,
#                 domain=settings.LANGUAGE_COOKIE_DOMAIN,
#             )
#     return response



# def set_language(request, language_code):
#     """
#     Redirect to a given URL while setting the chosen language in the session
#     (if enabled) and in a cookie. The URL and the language code need to be
#     specified in the request parameters.

#     Since this view changes how the user will see the rest of the site, it must
#     only be accessed as a POST request. If called as a GET request, it will
#     redirect to the page in the request (the '_next' parameter) without changing
#     any state.
#     """
#     _next = request.GET.get('_next')
#     if ((_next or not request.is_ajax()) and
#             not is_safe_url(url=_next, allowed_hosts={request.get_host()}, require_https=request.is_secure())):
#         _next = request.META.get('HTTP_REFERER')
#         _next = _next and unquote(_next)  # HTTP_REFERER may be encoded.
#         if not is_safe_url(url=_next, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
#             _next = '/'
#     response = HttpResponseRedirect(_next) if _next else HttpResponse(status=204)
#     if request.method == 'GET':
#         lang_code = language_code
#         import pdb; pdb.set_trace()
#         if lang_code and check_for_language(lang_code):
#             activate(lang_code)

#             if _next:
#                 next_trans = translate_url(_next, lang_code)
#                 if next_trans != _next:
#                     response = HttpResponseRedirect(next_trans)
#             if hasattr(request, 'session'):
#                 request.session[LANGUAGE_SESSION_KEY] = lang_code
#             response.set_cookie(
#                 settings.LANGUAGE_COOKIE_NAME, lang_code,
#                 max_age=settings.LANGUAGE_COOKIE_AGE,
#                 path=settings.LANGUAGE_COOKIE_PATH,
#                 domain=settings.LANGUAGE_COOKIE_DOMAIN,
#             )
#     return response