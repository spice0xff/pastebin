from django.contrib import admin
from .models import AccessPeriod, Paste, CodeLanguage


class AccessTimeAdmin(admin.ModelAdmin):
    pass


class PasteAdmin(admin.ModelAdmin):
    pass


class CodeLanguageAdmin(admin.ModelAdmin):
    pass


admin.site.register(AccessPeriod, AccessTimeAdmin)
admin.site.register(Paste, PasteAdmin)
admin.site.register(CodeLanguage, CodeLanguageAdmin)
