from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentMethod, Payment, Transaction, Refund


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin interface for PaymentMethod model."""
    list_display = ['user', 'method_type', 'display_info', 'is_default', 'is_active', 'created_at']
    list_filter = ['method_type', 'is_default', 'is_active', 'card_type']
    search_fields = ['user__email', 'last_four_digits', 'cardholder_name']
    readonly_fields = ['created_at', 'updated_at']

    def display_info(self, obj):
        return str(obj)
    display_info.short_description = 'Payment Info'


class TransactionInline(admin.TabularInline):
    """Inline admin for Transaction."""
    model = Transaction
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""
    list_display = [
        'transaction_id', 'user', 'amount_display', 'status_badge',
        'gateway_name', 'payment_date'
    ]
    list_filter = ['status', 'gateway_name', 'payment_date']
    search_fields = ['transaction_id', 'user__email', 'gateway_transaction_id']
    date_hierarchy = 'payment_date'
    readonly_fields = ['transaction_id', 'payment_date', 'completed_at', 'created_at', 'updated_at']
    inlines = [TransactionInline]

    def amount_display(self, obj):
        return f"{obj.currency} {obj.amount}"
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#0dcaf0',
            'completed': '#198754',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin interface for Refund model."""
    list_display = [
        'refund_id', 'user', 'amount_display', 'status_badge',
        'reason', 'requested_at'
    ]
    list_filter = ['status', 'reason', 'requested_at']
    search_fields = ['refund_id', 'user__email']
    date_hierarchy = 'requested_at'
    readonly_fields = ['refund_id', 'requested_at', 'processed_at', 'created_at', 'updated_at']

    def amount_display(self, obj):
        return f"{obj.currency} {obj.amount}"
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#0dcaf0',
            'completed': '#198754',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
