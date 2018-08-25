"""ta_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

from ta_platform.views import HomeView

admin.site.site_header = "{} administration".format(settings.BRAND_DICT['COMPANY_NAME'])

urlpatterns = [
    path('admin-contrib/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    # path('apply/', include('applications.urls', namespace='applications')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # path('admin-console/', include('admin_console.urls', namespace='admin_console')),
    # path('its/', include('issue_tracker.urls', namespace='its')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += i18n_patterns(
#     path('jsi18n/', JavaScriptCatalog.as_view(domain='djangojs', packages=[
#         'applications',
#         'admin',
#         'accounts',
#         ]), name='javascript-catalog'),
# )


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns