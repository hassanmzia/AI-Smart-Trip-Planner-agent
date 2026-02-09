from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import CarType, CarRental, RentalBooking
from .serializers import (
    CarTypeSerializer, CarRentalSerializer,
    CarRentalListSerializer, RentalBookingSerializer
)


class CarTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CarType model."""
    queryset = CarType.objects.all()
    serializer_class = CarTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    filterset_fields = ['category', 'transmission', 'fuel_type']
    ordering = ['category', 'name']


class CarRentalViewSet(viewsets.ModelViewSet):
    """ViewSet for CarRental model."""
    queryset = CarRental.objects.filter(is_active=True, status='available')
    serializer_class = CarRentalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['make', 'model', 'pickup_city', 'rental_company']
    filterset_fields = ['pickup_city', 'car_type', 'status']
    ordering_fields = ['price_per_day', 'rating', 'year']
    ordering = ['price_per_day']

    def get_serializer_class(self):
        if self.action == 'list':
            return CarRentalListSerializer
        return CarRentalSerializer

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search for available cars."""
        pickup_city = request.data.get('pickup_city')
        pickup_date = request.data.get('pickup_date')
        return_date = request.data.get('return_date')

        queryset = self.get_queryset()

        if pickup_city:
            queryset = queryset.filter(pickup_city__iexact=pickup_city)

        # Additional filters
        car_type = request.data.get('car_type')
        if car_type:
            queryset = queryset.filter(car_type_id=car_type)

        max_price = request.data.get('max_price_per_day')
        if max_price:
            queryset = queryset.filter(price_per_day__lte=max_price)

        serializer = CarRentalListSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})


class RentalBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for RentalBooking model."""
    queryset = RentalBooking.objects.all()
    serializer_class = RentalBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'pickup_date']
    ordering = ['-pickup_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return RentalBooking.objects.all()
        return RentalBooking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a rental booking."""
        booking = self.get_object()
        if booking.status in ['completed', 'cancelled']:
            return Response(
                {'error': f'Cannot cancel {booking.status} booking'},
                status=400
            )

        booking.status = 'cancelled'
        booking.save()
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def start_rental(self, request, pk=None):
        """Mark rental as active (picked up)."""
        booking = self.get_object()
        if booking.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed bookings can be started'},
                status=400
            )

        booking.status = 'active'
        booking.save()
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def complete_rental(self, request, pk=None):
        """Mark rental as completed (returned)."""
        booking = self.get_object()
        if booking.status != 'active':
            return Response(
                {'error': 'Only active rentals can be completed'},
                status=400
            )

        booking.status = 'completed'
        booking.save()
        return Response(self.get_serializer(booking).data)
