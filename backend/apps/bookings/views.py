from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Booking, BookingItem, BookingStatus
from .serializers import (
    BookingSerializer,
    BookingListSerializer,
    BookingCreateSerializer,
    BookingItemSerializer,
    BookingStatusSerializer
)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model."""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['booking_number', 'primary_traveler_name', 'primary_traveler_email']
    filterset_fields = ['status', 'booking_date', 'currency']
    ordering_fields = ['booking_date', 'total_amount', 'updated_at']
    ordering = ['-booking_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        elif self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking."""
        booking = self.get_object()
        if booking.status != 'pending':
            return Response(
                {'error': 'Only pending bookings can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'confirmed'
        booking.confirmation_date = timezone.now()
        booking.save()

        BookingStatus.objects.create(
            booking=booking,
            old_status='pending',
            new_status='confirmed',
            changed_by=request.user,
            notes='Booking confirmed'
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        if booking.status in ['cancelled', 'completed', 'refunded']:
            return Response(
                {'error': f'Cannot cancel {booking.status} booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get('reason', '')
        old_status = booking.status
        booking.status = 'cancelled'
        booking.cancellation_date = timezone.now()
        booking.save()

        BookingStatus.objects.create(
            booking=booking,
            old_status=old_status,
            new_status='cancelled',
            changed_by=request.user,
            reason=reason
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings."""
        bookings = self.get_queryset().filter(
            status__in=['confirmed', 'pending'],
            items__start_date__gte=timezone.now()
        ).distinct()
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past bookings."""
        bookings = self.get_queryset().filter(
            status='completed'
        )
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for BookingItem model."""

    queryset = BookingItem.objects.all()
    serializer_class = BookingItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['booking', 'item_type']
    ordering = ['start_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return BookingItem.objects.all()
        return BookingItem.objects.filter(booking__user=self.request.user)
