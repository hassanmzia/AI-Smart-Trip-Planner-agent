from django.contrib import admin
from django.utils.html import format_html
from .models import CarType, CarRental, RentalBooking


@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    """Admin interface for CarType model."""
    list_display = ['name', 'category', 'transmission', 'fuel_type', 'passenger_capacity', 'luggage_capacity']
    list_filter = ['category', 'transmission', 'fuel_type']
    search_fields = ['name']


@admin.register(CarRental)
class CarRentalAdmin(admin.ModelAdmin):
    """Admin interface for CarRental model."""
    list_display = [
        'vehicle_name', 'car_type', 'rental_company', 'pickup_city',
        'price_per_day_display', 'status_badge', 'rating', 'is_active'
    ]
    list_filter = ['status', 'car_type', 'pickup_city', 'is_active']
    search_fields = ['make', 'model', 'license_plate', 'rental_company', 'pickup_city']
    readonly_fields = ['review_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Vehicle Details', {
            'fields': ('car_type', 'make', 'model', 'year', 'color', 'license_plate')
        }),
        ('Location', {
            'fields': (
                'rental_company', 'pickup_location', 'pickup_address',
                'pickup_city', 'pickup_country', 'latitude', 'longitude'
            )
        }),
        ('Pricing', {
            'fields': (
                'price_per_day', 'currency', 'insurance_per_day',
                'additional_driver_fee', 'young_driver_fee'
            )
        }),
        ('Features', {
            'fields': ('features', 'has_gps', 'has_bluetooth', 'has_air_conditioning')
        }),
        ('Policies', {
            'fields': ('minimum_age', 'mileage_limit_per_day', 'deposit_amount')
        }),
        ('Media', {
            'fields': ('primary_image', 'images')
        }),
        ('Status & Rating', {
            'fields': ('status', 'is_active', 'rating', 'review_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def vehicle_name(self, obj):
        """Display vehicle name."""
        return f"{obj.year} {obj.make} {obj.model}"
    vehicle_name.short_description = 'Vehicle'

    def price_per_day_display(self, obj):
        """Display price per day."""
        return f"{obj.currency} {obj.price_per_day}"
    price_per_day_display.short_description = 'Price/Day'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'available': '#198754',
            'rented': '#0dcaf0',
            'maintenance': '#ffc107',
            'unavailable': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(RentalBooking)
class RentalBookingAdmin(admin.ModelAdmin):
    """Admin interface for RentalBooking model."""
    list_display = [
        'booking_reference', 'user', 'car_display', 'driver_name',
        'pickup_date', 'return_date', 'total_days', 'status_badge',
        'total_cost_display'
    ]
    list_filter = ['status', 'pickup_date', 'includes_insurance']
    search_fields = [
        'booking_reference', 'user__email', 'driver_name',
        'driver_email', 'driver_license_number'
    ]
    date_hierarchy = 'pickup_date'
    readonly_fields = ['booking_reference', 'total_days', 'created_at', 'updated_at']

    fieldsets = (
        ('Booking Info', {
            'fields': ('user', 'booking_reference', 'status', 'car_rental')
        }),
        ('Rental Period', {
            'fields': (
                'pickup_date', 'return_date', 'total_days',
                'pickup_location', 'return_location', 'different_return_location'
            )
        }),
        ('Driver Information', {
            'fields': (
                'driver_name', 'driver_email', 'driver_phone',
                'driver_license_number', 'driver_age'
            )
        }),
        ('Additional Options', {
            'fields': ('additional_drivers', 'includes_insurance', 'special_requests')
        }),
        ('Costs', {
            'fields': (
                'rental_cost', 'insurance_cost', 'additional_fees',
                'total_cost', 'currency', 'deposit_paid', 'deposit_refunded'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def car_display(self, obj):
        """Display car information."""
        car = obj.car_rental
        return f"{car.year} {car.make} {car.model}"
    car_display.short_description = 'Car'

    def total_cost_display(self, obj):
        """Display total cost."""
        return f"{obj.currency} {obj.total_cost}"
    total_cost_display.short_description = 'Total Cost'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#ffc107',
            'confirmed': '#0dcaf0',
            'active': '#198754',
            'completed': '#6c757d',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
