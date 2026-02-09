from django.contrib import admin
from .models import Itinerary, ItineraryDay, ItineraryItem, Weather


class ItineraryDayInline(admin.TabularInline):
    """Inline admin for ItineraryDay."""
    model = ItineraryDay
    extra = 0
    fields = ['day_number', 'date', 'title']


class ItineraryItemInline(admin.TabularInline):
    """Inline admin for ItineraryItem."""
    model = ItineraryItem
    extra = 0
    fields = ['item_type', 'title', 'start_time', 'location_name', 'is_booked']


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    """Admin interface for Itinerary model."""
    list_display = ['title', 'user', 'destination', 'start_date', 'end_date', 'status', 'duration_days']
    list_filter = ['status', 'start_date', 'is_public']
    search_fields = ['title', 'destination', 'user__email']
    date_hierarchy = 'start_date'
    inlines = [ItineraryDayInline]


@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    """Admin interface for ItineraryDay model."""
    list_display = ['itinerary', 'day_number', 'date', 'title']
    list_filter = ['date']
    search_fields = ['itinerary__title', 'title']
    inlines = [ItineraryItemInline]


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    """Admin interface for ItineraryItem model."""
    list_display = ['title', 'day', 'item_type', 'start_time', 'is_booked']
    list_filter = ['item_type', 'is_booked']
    search_fields = ['title', 'location_name']


@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    """Admin interface for Weather model."""
    list_display = ['location', 'date', 'condition', 'temp_high', 'temp_low', 'source']
    list_filter = ['condition', 'date', 'source']
    search_fields = ['location']
    date_hierarchy = 'date'
