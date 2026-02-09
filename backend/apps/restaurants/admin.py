from django.contrib import admin
from .models import Restaurant, Cuisine, RestaurantBooking


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    """Admin interface for Cuisine model."""
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """Admin interface for Restaurant model."""
    list_display = [
        'name', 'city', 'country', 'price_range', 'rating',
        'review_count', 'is_featured', 'is_active'
    ]
    list_filter = ['price_range', 'city', 'country', 'is_featured', 'is_active']
    search_fields = ['name', 'city', 'country', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['cuisines']
    readonly_fields = ['review_count', 'created_at', 'updated_at']


@admin.register(RestaurantBooking)
class RestaurantBookingAdmin(admin.ModelAdmin):
    """Admin interface for RestaurantBooking model."""
    list_display = [
        'booking_reference', 'restaurant', 'guest_name', 'reservation_date',
        'reservation_time', 'number_of_guests', 'status', 'created_at'
    ]
    list_filter = ['status', 'reservation_date']
    search_fields = ['booking_reference', 'guest_name', 'guest_email', 'restaurant__name']
    date_hierarchy = 'reservation_date'
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
