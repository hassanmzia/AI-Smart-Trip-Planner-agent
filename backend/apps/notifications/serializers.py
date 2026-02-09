from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display', 'priority',
            'priority_display', 'title', 'message', 'action_url', 'action_text',
            'is_read', 'read_at', 'sent_email', 'sent_push', 'sent_sms',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""

    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
