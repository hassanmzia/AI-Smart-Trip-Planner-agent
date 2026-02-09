from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum
from datetime import timedelta
from django.utils import timezone

from .models import UserActivity, SearchAnalytics, BookingAnalytics
from .serializers import (
    UserActivitySerializer, SearchAnalyticsSerializer,
    BookingAnalyticsSerializer
)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for UserActivity model."""
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'user']
    ordering = ['-timestamp']

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=self.request.user)


class SearchAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SearchAnalytics model."""
    queryset = SearchAnalytics.objects.all()
    serializer_class = SearchAnalyticsSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['search_type', 'destination']
    ordering = ['-timestamp']

    @action(detail=False, methods=['get'])
    def popular_destinations(self, request):
        """Get popular search destinations."""
        destinations = SearchAnalytics.objects.values('destination').annotate(
            search_count=Count('id')
        ).order_by('-search_count')[:10]
        return Response(destinations)


class BookingAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for BookingAnalytics model."""
    queryset = BookingAnalytics.objects.all()
    serializer_class = BookingAnalyticsSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['booking_type', 'payment_success']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def revenue_summary(self, request):
        """Get revenue summary."""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        bookings = BookingAnalytics.objects.filter(
            created_at__gte=thirty_days_ago,
            payment_success=True
        )

        summary = {
            'total_bookings': bookings.count(),
            'total_revenue': bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'average_booking_value': bookings.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
        }
        return Response(summary)
