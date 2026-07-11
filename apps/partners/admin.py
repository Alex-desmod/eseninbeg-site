from django.contrib import admin
from .models import Partner

# Register your models here.
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'website_url']
    list_editable = ['order']
    list_display_links = ['name']
