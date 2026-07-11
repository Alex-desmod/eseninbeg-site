from django.contrib import admin
from .models import Event, Distance, DistanceRecord, ScheduleItem, BibPickupInfo, VenueInfo

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


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['home_order', 'title', 'date', 'location', 'status']
    list_display_links = ['title']
    list_editable = ['home_order']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['partners']
    inlines = [DistanceInline, ScheduleItemInline, BibPickupInfoInline, VenueInfoInline]


@admin.register(DistanceRecord)
class DistanceRecordAdmin(admin.ModelAdmin):
    list_display = ['distance', 'gender', 'athlete', 'result_time', 'date']
    list_filter = ['distance__event', 'gender']