from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Review, Rating
from .serializers import ReviewSerializer, RatingSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model."""
    queryset = Review.objects.filter(status='approved')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['content_type', 'object_id', 'rating', 'is_verified_purchase']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        if self.request.user.is_authenticated and self.action in ['list', 'retrieve']:
            return Review.objects.filter(status='approved')
        return Review.objects.filter(status='approved')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        """Mark review as helpful."""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        return Response({'helpful_count': review.helpful_count})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_not_helpful(self, request, pk=None):
        """Mark review as not helpful."""
        review = self.get_object()
        review.not_helpful_count += 1
        review.save()
        return Response({'not_helpful_count': review.not_helpful_count})


class RatingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Rating model."""
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review', 'aspect']
