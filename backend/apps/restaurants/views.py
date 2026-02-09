from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Restaurant, Cuisine, RestaurantBooking
from .serializers import (
    RestaurantSerializer, RestaurantListSerializer,
    CuisineSerializer, RestaurantBookingSerializer
)


class RestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet for Restaurant model."""
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'country', 'description']
    filterset_fields = ['city', 'country', 'price_range', 'has_delivery', 'is_featured']
    ordering_fields = ['rating', 'name', 'average_cost_per_person']
    ordering = ['-rating']

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantListSerializer
        return RestaurantSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured restaurants."""
        restaurants = self.get_queryset().filter(is_featured=True)[:10]
        serializer = RestaurantListSerializer(restaurants, many=True)
        return Response(serializer.data)


class CuisineViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Cuisine model."""
    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RestaurantBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for RestaurantBooking model."""
    queryset = RestaurantBooking.objects.all()
    serializer_class = RestaurantBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'restaurant', 'reservation_date']
    ordering = ['-reservation_date', '-reservation_time']

    def get_queryset(self):
        if self.request.user.is_staff:
            return RestaurantBooking.objects.all()
        return RestaurantBooking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a restaurant booking."""
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        return Response(self.get_serializer(booking).data)
