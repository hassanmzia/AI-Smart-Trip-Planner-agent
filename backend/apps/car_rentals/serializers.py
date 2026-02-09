from rest_framework import serializers
from .models import CarType, CarRental, RentalBooking


class CarTypeSerializer(serializers.ModelSerializer):
    """Serializer for CarType model."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    transmission_display = serializers.CharField(source='get_transmission_display', read_only=True)
    fuel_type_display = serializers.CharField(source='get_fuel_type_display', read_only=True)

    class Meta:
        model = CarType
        fields = '__all__'
        read_only_fields = ['id']


class CarRentalSerializer(serializers.ModelSerializer):
    """Serializer for CarRental model."""
    car_type = CarTypeSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CarRental
        fields = '__all__'
        read_only_fields = ['id', 'review_count', 'created_at', 'updated_at']


class CarRentalListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for CarRental list views."""
    car_type_name = serializers.CharField(source='car_type.name', read_only=True)
    car_type_category = serializers.CharField(source='car_type.get_category_display', read_only=True)

    class Meta:
        model = CarRental
        fields = [
            'id', 'make', 'model', 'year', 'car_type_name', 'car_type_category',
            'pickup_city', 'price_per_day', 'currency', 'rating',
            'primary_image', 'status'
        ]


class RentalBookingSerializer(serializers.ModelSerializer):
    """Serializer for RentalBooking model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    car_info = serializers.SerializerMethodField()

    class Meta:
        model = RentalBooking
        fields = [
            'id', 'booking_reference', 'status', 'status_display', 'car_rental',
            'car_info', 'pickup_date', 'return_date', 'total_days',
            'pickup_location', 'return_location', 'different_return_location',
            'driver_name', 'driver_email', 'driver_phone', 'driver_license_number',
            'driver_age', 'additional_drivers', 'includes_insurance',
            'special_requests', 'rental_cost', 'insurance_cost',
            'additional_fees', 'total_cost', 'currency', 'deposit_paid',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'booking_reference', 'total_days', 'created_at', 'updated_at'
        ]

    def get_car_info(self, obj):
        """Get basic car information."""
        car = obj.car_rental
        return f"{car.year} {car.make} {car.model}"
