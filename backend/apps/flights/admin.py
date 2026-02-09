from django.contrib import admin
from django.utils.html import format_html
from .models import Flight, FlightSearch, PriceAlert


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """Admin interface for Flight model."""

    list_display = [
        'flight_number', 'airline_name', 'route', 'departure_time',
        'duration', 'travel_class', 'status_badge', 'price', 'seats_available'
    ]
    list_filter = ['status', 'travel_class', 'airline_code', 'is_direct', 'departure_time']
    search_fields = [
        'flight_number', 'airline_name', 'origin_airport', 'destination_airport',
        'origin_city', 'destination_city'
    ]
    date_hierarchy = 'departure_time'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Flight Identification', {
            'fields': ('flight_number', 'airline_code', 'airline_name')
        }),
        ('Route', {
            'fields': (
                ('origin_airport', 'origin_city', 'origin_country'),
                ('destination_airport', 'destination_city', 'destination_country')
            )
        }),
        ('Schedule', {
            'fields': ('departure_time', 'arrival_time', 'duration_minutes')
        }),
        ('Aircraft', {
            'fields': ('aircraft_type', 'aircraft_model')
        }),
        ('Details', {
            'fields': ('travel_class', 'status', 'total_seats', 'available_seats')
        }),
        ('Pricing', {
            'fields': ('base_price', 'currency')
        }),
        ('Amenities', {
            'fields': (
                'has_wifi', 'has_meals', 'has_entertainment',
                'baggage_allowance_kg', 'carry_on_allowance_kg'
            ),
            'classes': ('collapse',)
        }),
        ('Stops', {
            'fields': ('is_direct', 'stops_count', 'layover_airports')
        }),
        ('Metadata', {
            'fields': ('booking_url', 'terms_and_conditions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def route(self, obj):
        """Display route."""
        return f"{obj.origin_airport} → {obj.destination_airport}"
    route.short_description = 'Route'

    def duration(self, obj):
        """Display duration in hours and minutes."""
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        return f"{hours}h {minutes}m"
    duration.short_description = 'Duration'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'scheduled': '#198754',
            'delayed': '#ffc107',
            'cancelled': '#dc3545',
            'completed': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def price(self, obj):
        """Display formatted price."""
        return f"{obj.currency} {obj.base_price}"
    price.short_description = 'Price'

    def seats_available(self, obj):
        """Display available seats with color coding."""
        if obj.available_seats == 0:
            color = '#dc3545'
        elif obj.available_seats < 10:
            color = '#ffc107'
        else:
            color = '#198754'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} / {}</span>',
            color,
            obj.available_seats,
            obj.total_seats
        )
    seats_available.short_description = 'Seats'


@admin.register(FlightSearch)
class FlightSearchAdmin(admin.ModelAdmin):
    """Admin interface for FlightSearch model."""

    list_display = [
        'user_info', 'route', 'departure_date', 'return_date',
        'trip_type', 'passengers', 'preferred_class', 'results_count', 'created_at'
    ]
    list_filter = ['trip_type', 'preferred_class', 'direct_flights_only', 'created_at']
    search_fields = [
        'user__email', 'origin_airport', 'destination_airport',
        'origin_city', 'destination_city', 'session_id'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'search_duration_ms']

    fieldsets = (
        ('User', {
            'fields': ('user', 'session_id', 'ip_address')
        }),
        ('Route', {
            'fields': (
                ('origin_airport', 'origin_city'),
                ('destination_airport', 'destination_city')
            )
        }),
        ('Dates', {
            'fields': ('departure_date', 'return_date', 'trip_type')
        }),
        ('Passengers', {
            'fields': ('adults', 'children', 'infants')
        }),
        ('Preferences', {
            'fields': (
                'preferred_class', 'direct_flights_only',
                'preferred_airlines', 'max_price'
            )
        }),
        ('Results', {
            'fields': ('results_count', 'search_duration_ms')
        }),
        ('Technical', {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def user_info(self, obj):
        """Display user email or Anonymous."""
        return obj.user.email if obj.user else 'Anonymous'
    user_info.short_description = 'User'

    def route(self, obj):
        """Display route."""
        return f"{obj.origin_airport} → {obj.destination_airport}"
    route.short_description = 'Route'

    def passengers(self, obj):
        """Display total passengers."""
        return f"{obj.total_passengers} ({obj.adults}A, {obj.children}C, {obj.infants}I)"
    passengers.short_description = 'Passengers'


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    """Admin interface for PriceAlert model."""

    list_display = [
        'user', 'route', 'departure_date', 'target_price_display',
        'current_price_display', 'status_badge', 'expiry_date', 'created_at'
    ]
    list_filter = ['status', 'travel_class', 'created_at', 'expiry_date']
    search_fields = [
        'user__email', 'origin_airport', 'destination_airport'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = [
        'current_price', 'lowest_price_seen', 'last_checked_at',
        'triggered_at', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Route', {
            'fields': ('origin_airport', 'destination_airport')
        }),
        ('Dates', {
            'fields': ('departure_date', 'return_date', 'expiry_date')
        }),
        ('Alert Settings', {
            'fields': ('target_price', 'currency', 'travel_class', 'preferred_airlines')
        }),
        ('Status', {
            'fields': (
                'status', 'current_price', 'lowest_price_seen',
                'last_checked_at', 'triggered_at'
            )
        }),
        ('Notifications', {
            'fields': ('email_notification', 'push_notification')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def route(self, obj):
        """Display route."""
        return f"{obj.origin_airport} → {obj.destination_airport}"
    route.short_description = 'Route'

    def target_price_display(self, obj):
        """Display target price."""
        return f"{obj.currency} {obj.target_price}"
    target_price_display.short_description = 'Target Price'

    def current_price_display(self, obj):
        """Display current price with color coding."""
        if not obj.current_price:
            return '-'

        if obj.current_price <= obj.target_price:
            color = '#198754'  # Green
        else:
            color = '#dc3545'  # Red

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            obj.currency,
            obj.current_price
        )
    current_price_display.short_description = 'Current Price'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'active': '#0dcaf0',
            'triggered': '#198754',
            'expired': '#6c757d',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
