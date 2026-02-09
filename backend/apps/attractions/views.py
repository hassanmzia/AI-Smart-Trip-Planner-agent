from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Attraction, AttractionCategory
from .serializers import (
    AttractionSerializer, AttractionListSerializer,
    AttractionCategorySerializer
)


class AttractionViewSet(viewsets.ModelViewSet):
    """ViewSet for Attraction model."""
    queryset = Attraction.objects.filter(is_active=True)
    serializer_class = AttractionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'country', 'description']
    filterset_fields = ['city', 'country', 'attraction_type', 'is_free', 'is_featured']
    ordering_fields = ['rating', 'name', 'admission_price']
    ordering = ['-rating']

    def get_serializer_class(self):
        if self.action == 'list':
            return AttractionListSerializer
        return AttractionSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured attractions."""
        attractions = self.get_queryset().filter(is_featured=True)[:10]
        serializer = AttractionListSerializer(attractions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """Get attractions by city."""
        city = request.query_params.get('city')
        if not city:
            return Response({'error': 'city parameter is required'}, status=400)

        attractions = self.get_queryset().filter(city__iexact=city)
        serializer = AttractionListSerializer(attractions, many=True)
        return Response(serializer.data)


class AttractionCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AttractionCategory model."""
    queryset = AttractionCategory.objects.all()
    serializer_class = AttractionCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']
