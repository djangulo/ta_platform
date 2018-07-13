from django.contrib import admin

from applications.models import (
    CallCenter, Language, Career, Institution, AreaOfExperience,
    CityTown)


admin.site.register(CallCenter)
admin.site.register(Language)
admin.site.register(Career)

admin.site.register(Institution)
admin.site.register(AreaOfExperience)
admin.site.register(CityTown)
# Register your models here.

