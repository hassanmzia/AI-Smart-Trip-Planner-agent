from django.contrib import admin
from .models import Attraction, AttractionCategory


@admin.register(AttractionCategory)
class AttractionCategoryAdmin(admin.ModelAdmin):
    """Admin interface for AttractionCategory model."""
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    """Admin interface for Attraction model."""
    list_display = [
        'name', 'city', 'country', 'attraction_type', 'rating',
        'review_count', 'is_free', 'is_featured', 'is_active'
    ]
    list_filter = ['attraction_type', 'city', 'country', 'is_free', 'is_featured', 'is_active']
    search_fields = ['name', 'city', 'country', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['categories']
    readonly_fields = ['review_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description', 'attraction_type')
        }),
        ('Categories', {
            'fields': ('categories',)
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'state_province', 'country',
                'postal_code', 'latitude', 'longitude'
            )
        }),
        ('Operating Hours', {
            'fields': ('opening_hours', 'is_open_24_7')
        }),
        ('Pricing', {
            'fields': ('admission_price', 'currency', 'is_free', 'typical_duration_minutes')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Ratings', {
            'fields': ('rating', 'review_count')
        }),
        ('Media', {
            'fields': ('primary_image', 'images', 'video_urls')
        }),
        ('Features', {
            'fields': ('accessibility_features', 'amenities', 'languages_available')
        }),
        ('Booking', {
            'fields': ('booking_required', 'booking_url')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
