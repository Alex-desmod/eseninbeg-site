from import_export import resources
from import_export.admin import ExportMixin
from django.contrib import admin
from .models import Event, Distance, DistanceRecord, ScheduleItem, BibPickupInfo, VenueInfo, WaitlistEntry
from ..gallery.models import MediaItem


# Register your models here.
class DistanceInline(admin.TabularInline):
    model = Distance
    extra = 1


class ScheduleItemInline(admin.TabularInline):
    model = ScheduleItem
    extra = 1


class BibPickupInfoInline(admin.StackedInline):
    model = BibPickupInfo
    extra = 0
    max_num = 1


class VenueInfoInline(admin.StackedInline):
    model = VenueInfo
    extra = 0
    max_num = 1


class MediaItemInline(admin.TabularInline):
    model = MediaItem
    extra = 1
    fields = ['media_type', 'image', 'video_embed_url', 'caption', 'order']



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['home_order', 'title', 'date', 'location', 'status', 'waitlist_enabled']
    list_display_links = ['title']
    list_editable = ['home_order', 'waitlist_enabled']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['partners']
    inlines = [DistanceInline, ScheduleItemInline, BibPickupInfoInline, VenueInfoInline, MediaItemInline]


@admin.register(DistanceRecord)
class DistanceRecordAdmin(admin.ModelAdmin):
    list_display = ['distance', 'gender', 'athlete', 'result_time', 'date']
    list_filter = ['distance__event', 'gender']


class WaitlistEntryResource(resources.ModelResource):
    class Meta:
        model = WaitlistEntry


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = WaitlistEntryResource
    list_display = ['full_name', 'phone', 'email', 'event', 'created_at']
    list_filter = ['event']
    readonly_fields = ['created_at']