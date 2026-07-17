from django.contrib import admin

from .models import SiteSettings

admin.site.site_header = "Администрирование Eseninbeg"
admin.site.site_title = "Администрирование Eseninbeg"

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False