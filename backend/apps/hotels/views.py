from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q

from .models import Hotel, HotelAmenity, HotelSearch
from .serializers import (
    HotelSerializer,
    HotelListSerializer,
    HotelAmenitySerializer,
    HotelSearchSerializer,
    HotelSearchCreateSerializer
)


class HotelViewSet(viewsets.ModelViewSet):
    """ViewSet for Hotel model."""

    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'country', 'chain']
    filterset_fields = ['city', 'country', 'star_rating', 'property_type', 'is_featured']
    ordering_fields = ['guest_rating', 'star_rating', 'price_range_min', 'name']
    ordering = ['-guest_rating']

    def get_serializer_class(self):
        if self.action == 'list':
            return HotelListSerializer
        return HotelSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by guest rating
        min_rating = self.request.query_params.get('min_guest_rating')
        if min_rating:
            queryset = queryset.filter(guest_rating__gte=min_rating)

        # Filter by price range
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price_range_min__lte=max_price)

        # Filter by amenities
        amenities = self.request.query_params.getlist('amenities')
        if amenities:
            for amenity in amenities:
                queryset = queryset.filter(amenities__name__icontains=amenity)

        return queryset.distinct()

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced hotel search."""
        city = request.data.get('city')
        check_in = request.data.get('check_in_date')
        check_out = request.data.get('check_out_date')

        queryset = self.get_queryset().filter(city__iexact=city)

        # Apply additional filters
        min_star = request.data.get('min_star_rating')
        if min_star:
            queryset = queryset.filter(star_rating__gte=min_star)

        serializer = HotelListSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured hotels."""
        hotels = self.get_queryset().filter(is_featured=True)[:10]
        serializer = HotelListSerializer(hotels, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def amenities(self, request, pk=None):
        """Get hotel amenities grouped by category."""
        hotel = self.get_object()
        amenities = hotel.amenities.all()

        grouped = {}
        for amenity in amenities:
            category = amenity.get_category_display()
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(HotelAmenitySerializer(amenity).data)

        return Response(grouped)


class HotelSearchViewSet(viewsets.ModelViewSet):
    """ViewSet for HotelSearch model."""

    queryset = HotelSearch.objects.all()
    serializer_class = HotelSearchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['city', 'country']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return HotelSearchCreateSerializer
        return HotelSearchSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return HotelSearch.objects.all()
            return HotelSearch.objects.filter(user=self.request.user)
        return HotelSearch.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def popular_destinations(self, request):
        """Get popular hotel search destinations."""
        destinations = HotelSearch.objects.values('city', 'country').annotate(
            search_count=Count('id')
        ).order_by('-search_count')[:10]
        return Response(destinations)
