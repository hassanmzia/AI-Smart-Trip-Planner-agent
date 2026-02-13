from rest_framework import serializers
from .models import Booking, BookingItem, BookingStatus


class BookingItemSerializer(serializers.ModelSerializer):
    """Serializer for BookingItem model."""

    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)

    class Meta:
        model = BookingItem
        fields = [
            'id', 'item_type', 'item_type_display', 'item_name',
            'item_description', 'unit_price', 'quantity', 'total_price',
            'start_date', 'end_date', 'item_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingStatusSerializer(serializers.ModelSerializer):
    """Serializer for BookingStatus model."""

    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)

    class Meta:
        model = BookingStatus
        fields = [
            'id', 'old_status', 'new_status', 'changed_by_email',
            'reason', 'notes', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""

    items = BookingItemSerializer(many=True, read_only=True)
    status_history = BookingStatusSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'status', 'status_display', 'total_amount',
            'currency', 'tax_amount', 'discount_amount', 'final_amount',
            'primary_traveler_name', 'primary_traveler_email', 'primary_traveler_phone',
            'special_requests', 'notes', 'booking_date', 'confirmation_date',
            'cancellation_date', 'items', 'status_history', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'booking_number', 'booking_date', 'confirmation_date',
            'cancellation_date', 'created_at', 'updated_at'
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Booking list views."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'status', 'status_display', 'total_amount',
            'currency', 'primary_traveler_name', 'booking_date', 'notes', 'item_count'
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings."""

    items = BookingItemSerializer(many=True, required=False)

    class Meta:
        model = Booking
        fields = [
            'total_amount', 'currency', 'tax_amount', 'discount_amount',
            'primary_traveler_name', 'primary_traveler_email',
            'primary_traveler_phone', 'special_requests', 'notes', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        booking = Booking.objects.create(**validated_data)

        for item_data in items_data:
            BookingItem.objects.create(booking=booking, **item_data)

        return booking
