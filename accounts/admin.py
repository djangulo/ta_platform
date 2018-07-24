from django.contrib import admin

# Register your models here.

from accounts.models import User, Person, Address

admin.site.register(User)
admin.site.register(Person)
admin.site.register(Address)
