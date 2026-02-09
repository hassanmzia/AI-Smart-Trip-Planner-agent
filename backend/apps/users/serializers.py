from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, TravelHistory


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""

    class Meta:
        model = UserProfile
        fields = [
            'id', 'date_of_birth', 'nationality', 'passport_number', 'passport_expiry',
            'preferred_currency', 'preferred_language', 'preferred_travel_class',
            'preferred_airlines', 'preferred_hotel_chains', 'frequent_flyer_programs',
            'hotel_loyalty_programs', 'dietary_restrictions', 'accessibility_needs',
            'seat_preference', 'total_trips', 'total_flights', 'total_hotel_nights',
            'countries_visited', 'cities_visited', 'email_notifications',
            'sms_notifications', 'push_notifications', 'avatar', 'bio',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_trips', 'total_flights', 'total_hotel_nights', 'created_at', 'updated_at']


class TravelHistorySerializer(serializers.ModelSerializer):
    """Serializer for TravelHistory model."""

    class Meta:
        model = TravelHistory
        fields = [
            'id', 'destination_city', 'destination_country', 'origin_city',
            'origin_country', 'departure_date', 'return_date', 'trip_type',
            'number_of_travelers', 'booking_reference', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with nested profile."""

    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'is_verified', 'date_joined',
            'last_login', 'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at', 'is_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number']

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """Create user and associated profile."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Create associated profile
        UserProfile.objects.create(user=user)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for User model with nested relationships."""

    profile = UserProfileSerializer(read_only=True)
    travel_history = TravelHistorySerializer(many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'is_verified', 'date_joined',
            'last_login', 'profile', 'travel_history', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at', 'is_verified']
