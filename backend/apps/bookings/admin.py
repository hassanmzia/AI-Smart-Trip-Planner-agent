from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookingItem, BookingStatus


class BookingItemInline(admin.TabularInline):
    """Inline admin for BookingItem."""
    model = BookingItem
    extra = 0
    fields = ['item_type', 'item_name', 'unit_price', 'quantity', 'total_price', 'start_date']
    readonly_fields = ['total_price']


class BookingStatusInline(admin.TabularInline):
    """Inline admin for BookingStatus."""
    model = BookingStatus
    extra = 0
    fields = ['old_status', 'new_status', 'changed_by', 'reason', 'timestamp']
    readonly_fields = ['timestamp']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model."""

    list_display = [
        'booking_number', 'user', 'primary_traveler_name', 'status_badge',
        'final_amount_display', 'booking_date', 'item_count'
    ]
    list_filter = ['status', 'booking_date', 'currency']
    search_fields = [
        'booking_number', 'user__email', 'primary_traveler_name',
        'primary_traveler_email'
    ]
    date_hierarchy = 'booking_date'
    readonly_fields = [
        'booking_number', 'booking_date', 'confirmation_date',
        'cancellation_date', 'created_at', 'updated_at', 'final_amount'
    ]
    inlines = [BookingItemInline, BookingStatusInline]

    fieldsets = (
        ('Booking Info', {
            'fields': ('user', 'booking_number', 'status')
        }),
        ('Financial', {
            'fields': (
                'total_amount', 'tax_amount', 'discount_amount',
                'final_amount', 'currency'
            )
        }),
        ('Traveler Information', {
            'fields': (
                'primary_traveler_name', 'primary_traveler_email',
                'primary_traveler_phone'
            )
        }),
        ('Additional Info', {
            'fields': ('special_requests', 'notes')
        }),
        ('Timestamps', {
            'fields': (
                'booking_date', 'confirmation_date', 'cancellation_date',
                'created_at', 'updated_at'
            )
        }),
    )

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#ffc107',
            'confirmed': '#0dcaf0',
            'cancelled': '#dc3545',
            'completed': '#198754',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def final_amount_display(self, obj):
        """Display final amount."""
        return f"{obj.currency} {obj.final_amount}"
    final_amount_display.short_description = 'Final Amount'

    def item_count(self, obj):
        """Display count of booking items."""
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(BookingItem)
class BookingItemAdmin(admin.ModelAdmin):
    """Admin interface for BookingItem model."""

    list_display = [
        'booking', 'item_type', 'item_name', 'unit_price',
        'quantity', 'total_price', 'start_date'
    ]
    list_filter = ['item_type', 'start_date']
    search_fields = ['booking__booking_number', 'item_name']
    date_hierarchy = 'start_date'


@admin.register(BookingStatus)
class BookingStatusAdmin(admin.ModelAdmin):
    """Admin interface for BookingStatus model."""

    list_display = [
        'booking', 'old_status', 'new_status', 'changed_by', 'timestamp'
    ]
    list_filter = ['new_status', 'timestamp']
    search_fields = ['booking__booking_number', 'changed_by__email']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
