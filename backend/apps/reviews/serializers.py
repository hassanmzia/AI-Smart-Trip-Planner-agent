from rest_framework import serializers
from .models import Review, Rating


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for Rating model."""
    aspect_display = serializers.CharField(source='get_aspect_display', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'aspect', 'aspect_display', 'score']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    ratings = RatingSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user_email', 'title', 'content', 'rating', 'status',
            'status_display', 'is_verified_purchase', 'helpful_count',
            'not_helpful_count', 'images', 'videos', 'ratings',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'is_verified_purchase', 'helpful_count',
            'not_helpful_count', 'created_at', 'updated_at'
        ]
