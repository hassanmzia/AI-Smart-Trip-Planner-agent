from django.contrib import admin
from .models import UserActivity, SearchAnalytics, BookingAnalytics


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin interface for UserActivity model."""
    list_display = ['user', 'action', 'country', 'city', 'timestamp']
    list_filter = ['action', 'timestamp', 'country']
    search_fields = ['user__email', 'session_id', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for SearchAnalytics model."""
    list_display = [
        'search_type', 'origin', 'destination', 'results_count',
        'converted_to_booking', 'timestamp'
    ]
    list_filter = ['search_type', 'converted_to_booking', 'timestamp']
    search_fields = ['origin', 'destination', 'user__email']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']


@admin.register(BookingAnalytics)
class BookingAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for BookingAnalytics model."""
    list_display = [
        'user', 'booking_type', 'total_amount', 'currency',
        'payment_success', 'created_at'
    ]
    list_filter = ['booking_type', 'payment_success', 'created_at']
    search_fields = ['user__email', 'booking__booking_number']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
