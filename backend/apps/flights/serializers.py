from rest_framework import serializers
from .models import Flight, FlightSearch, PriceAlert


class FlightSerializer(serializers.ModelSerializer):
    """Serializer for Flight model."""

    travel_class_display = serializers.CharField(source='get_travel_class_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'airline_code', 'airline_name',
            'origin_airport', 'origin_city', 'origin_country',
            'destination_airport', 'destination_city', 'destination_country',
            'departure_time', 'arrival_time', 'duration_minutes', 'duration_hours',
            'aircraft_type', 'aircraft_model', 'travel_class', 'travel_class_display',
            'status', 'status_display', 'total_seats', 'available_seats',
            'base_price', 'currency', 'has_wifi', 'has_meals', 'has_entertainment',
            'baggage_allowance_kg', 'carry_on_allowance_kg', 'is_direct',
            'stops_count', 'layover_airports', 'booking_url',
            'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_available']

    def get_duration_hours(self, obj):
        """Convert duration from minutes to hours."""
        return round(obj.duration_minutes / 60, 2)


class FlightListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Flight list views."""

    travel_class_display = serializers.CharField(source='get_travel_class_display', read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'airline_name',
            'origin_airport', 'origin_city',
            'destination_airport', 'destination_city',
            'departure_time', 'arrival_time', 'duration_minutes',
            'travel_class', 'travel_class_display', 'base_price', 'currency',
            'is_direct', 'stops_count', 'available_seats', 'is_available'
        ]


class FlightSearchSerializer(serializers.ModelSerializer):
    """Serializer for FlightSearch model."""

    trip_type_display = serializers.CharField(source='get_trip_type_display', read_only=True)
    total_passengers = serializers.IntegerField(read_only=True)

    class Meta:
        model = FlightSearch
        fields = [
            'id', 'origin_airport', 'origin_city', 'destination_airport',
            'destination_city', 'departure_date', 'return_date', 'trip_type',
            'trip_type_display', 'adults', 'children', 'infants',
            'total_passengers', 'preferred_class', 'direct_flights_only',
            'preferred_airlines', 'max_price', 'results_count',
            'search_duration_ms', 'created_at'
        ]
        read_only_fields = ['id', 'results_count', 'search_duration_ms', 'created_at']


class FlightSearchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating flight searches."""

    class Meta:
        model = FlightSearch
        fields = [
            'origin_airport', 'origin_city', 'destination_airport',
            'destination_city', 'departure_date', 'return_date', 'trip_type',
            'adults', 'children', 'infants', 'preferred_class',
            'direct_flights_only', 'preferred_airlines', 'max_price'
        ]

    def validate(self, data):
        """Validate search parameters."""
        # Validate return date for round trips
        if data.get('trip_type') == 'round_trip' and not data.get('return_date'):
            raise serializers.ValidationError({
                'return_date': 'Return date is required for round trip flights.'
            })

        # Validate return date is after departure date
        if data.get('return_date') and data.get('return_date') < data.get('departure_date'):
            raise serializers.ValidationError({
                'return_date': 'Return date must be after departure date.'
            })

        # Validate at least one passenger
        total_passengers = data.get('adults', 0) + data.get('children', 0) + data.get('infants', 0)
        if total_passengers == 0:
            raise serializers.ValidationError('At least one passenger is required.')

        return data


class PriceAlertSerializer(serializers.ModelSerializer):
    """Serializer for PriceAlert model."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    price_difference = serializers.SerializerMethodField()

    class Meta:
        model = PriceAlert
        fields = [
            'id', 'origin_airport', 'destination_airport', 'departure_date',
            'return_date', 'target_price', 'currency', 'travel_class',
            'preferred_airlines', 'status', 'status_display', 'current_price',
            'lowest_price_seen', 'email_notification', 'push_notification',
            'last_checked_at', 'triggered_at', 'expiry_date', 'is_active',
            'price_difference', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'current_price', 'lowest_price_seen',
            'last_checked_at', 'triggered_at', 'created_at', 'updated_at'
        ]

    def get_price_difference(self, obj):
        """Calculate difference between current and target price."""
        if obj.current_price and obj.target_price:
            return float(obj.current_price - obj.target_price)
        return None


class PriceAlertCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating price alerts."""

    class Meta:
        model = PriceAlert
        fields = [
            'origin_airport', 'destination_airport', 'departure_date',
            'return_date', 'target_price', 'currency', 'travel_class',
            'preferred_airlines', 'email_notification', 'push_notification',
            'expiry_date'
        ]

    def validate(self, data):
        """Validate price alert parameters."""
        from django.utils import timezone
        from datetime import timedelta

        # Validate departure date is in the future
        if data.get('departure_date') < timezone.now().date():
            raise serializers.ValidationError({
                'departure_date': 'Departure date must be in the future.'
            })

        # Validate return date if provided
        if data.get('return_date') and data.get('return_date') < data.get('departure_date'):
            raise serializers.ValidationError({
                'return_date': 'Return date must be after departure date.'
            })

        # Validate expiry date
        if data.get('expiry_date') < timezone.now().date():
            raise serializers.ValidationError({
                'expiry_date': 'Expiry date must be in the future.'
            })

        # Expiry should be reasonable (not more than 1 year)
        max_expiry = timezone.now().date() + timedelta(days=365)
        if data.get('expiry_date') > max_expiry:
            raise serializers.ValidationError({
                'expiry_date': 'Expiry date cannot be more than 1 year in the future.'
            })

        return data


class FlightDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Flight with additional information."""

    travel_class_display = serializers.CharField(source='get_travel_class_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    duration_hours = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = '__all__'

    def get_duration_hours(self, obj):
        """Convert duration from minutes to hours."""
        return round(obj.duration_minutes / 60, 2)

    def get_occupancy_rate(self, obj):
        """Calculate occupancy rate percentage."""
        if obj.total_seats > 0:
            occupied = obj.total_seats - obj.available_seats
            return round((occupied / obj.total_seats) * 100, 2)
        return 0
