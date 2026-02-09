from rest_framework import serializers
from .models import UserActivity, SearchAnalytics, BookingAnalytics


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model."""
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            'id', 'action', 'action_display', 'session_id', 'ip_address',
            'country', 'city', 'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class SearchAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for SearchAnalytics model."""

    class Meta:
        model = SearchAnalytics
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class BookingAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for BookingAnalytics model."""

    class Meta:
        model = BookingAnalytics
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
