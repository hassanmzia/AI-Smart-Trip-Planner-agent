from django.contrib import admin
from django.utils.html import format_html
from .models import Hotel, HotelAmenity, HotelSearch


class HotelAmenityInline(admin.TabularInline):
    """Inline admin for HotelAmenity."""
    model = HotelAmenity
    extra = 1
    fields = ['name', 'category', 'is_free', 'additional_cost']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    """Admin interface for Hotel model."""

    list_display = [
        'name', 'city', 'country', 'star_rating_badge',
        'guest_rating_badge', 'review_count', 'property_type',
        'is_active', 'is_featured'
    ]
    list_filter = ['star_rating', 'property_type', 'is_active', 'is_featured', 'country']
    search_fields = ['name', 'city', 'country', 'chain', 'address']
    readonly_fields = ['review_count', 'created_at', 'updated_at']
    inlines = [HotelAmenityInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'chain', 'brand', 'property_type')
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'state_province', 'country',
                'postal_code', 'latitude', 'longitude'
            )
        }),
        ('Ratings', {
            'fields': ('star_rating', 'guest_rating', 'review_count')
        }),
        ('Property Details', {
            'fields': ('total_rooms', 'check_in_time', 'check_out_time')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Media', {
            'fields': ('primary_image', 'images')
        }),
        ('Pricing', {
            'fields': ('price_range_min', 'price_range_max', 'currency')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def star_rating_badge(self, obj):
        """Display star rating with stars."""
        stars = '⭐' * obj.star_rating
        return format_html('<span>{}</span>', stars)
    star_rating_badge.short_description = 'Stars'

    def guest_rating_badge(self, obj):
        """Display guest rating with color."""
        if not obj.guest_rating:
            return '-'

        if obj.guest_rating >= 8:
            color = '#198754'
        elif obj.guest_rating >= 6:
            color = '#ffc107'
        else:
            color = '#dc3545'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/10</span>',
            color,
            obj.guest_rating
        )
    guest_rating_badge.short_description = 'Guest Rating'


@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    """Admin interface for HotelAmenity model."""

    list_display = ['name', 'hotel', 'category', 'is_free', 'additional_cost']
    list_filter = ['category', 'is_free']
    search_fields = ['name', 'hotel__name']


@admin.register(HotelSearch)
class HotelSearchAdmin(admin.ModelAdmin):
    """Admin interface for HotelSearch model."""

    list_display = [
        'user_info', 'city', 'country', 'check_in_date',
        'check_out_date', 'nights', 'guests_info', 'results_count', 'created_at'
    ]
    list_filter = ['city', 'country', 'created_at']
    search_fields = ['user__email', 'city', 'country']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'nights']

    def user_info(self, obj):
        return obj.user.email if obj.user else 'Anonymous'
    user_info.short_description = 'User'

    def guests_info(self, obj):
        return f"{obj.rooms}R, {obj.adults}A, {obj.children}C"
    guests_info.short_description = 'Guests'
