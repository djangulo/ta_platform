from django.contrib import admin

# Register your models here.

from admin_console import models

admin.site.register(models.AreaCode)
admin.site.register(models.Country)
