from django.contrib import admin
from .models import AccessPeriod, Paste


class AccessTimeAdmin(admin.ModelAdmin):
    pass


class PasteAdmin(admin.ModelAdmin):
    pass


admin.site.register(AccessPeriod, AccessTimeAdmin)
admin.site.register(Paste, PasteAdmin)
