from django.contrib import admin

from applications.models import (
    CallCenter, Language, Career, Institution, AreaOfExpertise, Application,
    CityTown)


admin.site.register(CallCenter)
admin.site.register(Language)
admin.site.register(Career)

admin.site.register(Institution)
admin.site.register(AreaOfExpertise)
admin.site.register(CityTown)
admin.site.register(Application)
# Register your models here.

