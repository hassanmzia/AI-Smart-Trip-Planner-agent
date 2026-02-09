from rest_framework import serializers
from .models import Restaurant, Cuisine, RestaurantBooking


class CuisineSerializer(serializers.ModelSerializer):
    """Serializer for Cuisine model."""

    class Meta:
        model = Cuisine
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id']


class RestaurantSerializer(serializers.ModelSerializer):
    """Serializer for Restaurant model."""
    cuisines = CuisineSerializer(many=True, read_only=True)
    price_range_display = serializers.CharField(source='get_price_range_display', read_only=True)

    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'review_count', 'created_at', 'updated_at']


class RestaurantListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Restaurant list views."""
    price_range_display = serializers.CharField(source='get_price_range_display', read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'short_description', 'city', 'country',
            'price_range', 'price_range_display', 'rating', 'review_count',
            'primary_image', 'has_delivery', 'has_reservation'
        ]


class RestaurantBookingSerializer(serializers.ModelSerializer):
    """Serializer for RestaurantBooking model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = RestaurantBooking
        fields = [
            'id', 'booking_reference', 'restaurant', 'restaurant_name',
            'status', 'status_display', 'reservation_date', 'reservation_time',
            'number_of_guests', 'guest_name', 'guest_email', 'guest_phone',
            'special_requests', 'seating_preference', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'booking_reference', 'created_at', 'updated_at']
