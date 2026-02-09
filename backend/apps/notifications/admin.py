from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = [
        'title', 'user', 'notification_type', 'priority_badge',
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'read_at']

    def priority_badge(self, obj):
        """Display priority as colored badge."""
        colors = {
            'low': '#6c757d',
            'normal': '#0dcaf0',
            'high': '#ffc107',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model."""
    list_display = ['user', 'digest_frequency', 'quiet_hours_enabled', 'updated_at']
    list_filter = ['digest_frequency', 'quiet_hours_enabled']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
