from rest_framework import serializers
from .models import Attraction, AttractionCategory


class AttractionCategorySerializer(serializers.ModelSerializer):
    """Serializer for AttractionCategory model."""

    class Meta:
        model = AttractionCategory
        fields = ['id', 'name', 'slug', 'description', 'icon']
        read_only_fields = ['id']


class AttractionSerializer(serializers.ModelSerializer):
    """Serializer for Attraction model."""
    attraction_type_display = serializers.CharField(source='get_attraction_type_display', read_only=True)
    categories = AttractionCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Attraction
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'review_count', 'created_at', 'updated_at']


class AttractionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Attraction list views."""
    attraction_type_display = serializers.CharField(source='get_attraction_type_display', read_only=True)

    class Meta:
        model = Attraction
        fields = [
            'id', 'name', 'slug', 'short_description', 'attraction_type',
            'attraction_type_display', 'city', 'country', 'rating',
            'review_count', 'admission_price', 'currency', 'is_free',
            'primary_image'
        ]
