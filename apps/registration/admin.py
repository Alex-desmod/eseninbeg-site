from import_export import resources
from import_export.admin import ExportMixin
from django.contrib import admin
from .models import Registration


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration


@admin.register(Registration)
class RegistrationAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = RegistrationResource
    list_display = [
        'full_name', 'event', 'distance', 'status', 'gender',
        'birth_date', 'email', 'phone', 'amount', 'bib_number', 'created_at'
    ]
    list_filter = ['event', 'distance', 'status', 'gender']
    list_editable = ['status', 'bib_number']
    search_fields = ['full_name', 'email', 'phone', 'city', 'club']
    readonly_fields = ['created_at']

    def has_delete_permission(self, request, obj=None):
        return False
