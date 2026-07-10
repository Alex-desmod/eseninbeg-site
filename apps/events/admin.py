from django.contrib import admin
from .models import Event, Distance, DistanceRecord, ScheduleItem, BibPickupInfo, VenueInfo

# Register your models here.
class DistanceInline(admin.TabularInline):
    model = Distance
    extra = 1


class DistanceRecordInline(admin.TabularInline):
    model = DistanceRecord
    extra = 0
    max_num = 2


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
    list_display = ['title', 'date', 'location', 'status']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DistanceInline, ScheduleItemInline, BibPickupInfoInline, VenueInfoInline]


@admin.register(Distance)
class DistanceAdmin(admin.ModelAdmin):
    inlines = [DistanceRecordInline]