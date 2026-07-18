from django.contrib import admin

from .models import MediaItem


# Register your models here.
@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ['event', 'media_type', 'caption', 'order']
    list_editable = ['order']
    list_filter = ['event', 'media_type']
    list_display_links = ['media_type']