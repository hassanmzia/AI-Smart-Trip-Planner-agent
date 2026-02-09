from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Itinerary, ItineraryDay, ItineraryItem, Weather
from .serializers import (
    ItinerarySerializer, ItineraryDaySerializer,
    ItineraryItemSerializer, WeatherSerializer
)


class ItineraryViewSet(viewsets.ModelViewSet):
    """ViewSet for Itinerary model."""
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'destination']
    filterset_fields = ['status', 'destination']
    ordering = ['-start_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Itinerary.objects.all()
        return Itinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ItineraryDayViewSet(viewsets.ModelViewSet):
    """ViewSet for ItineraryDay model."""
    queryset = ItineraryDay.objects.all()
    serializer_class = ItineraryDaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['itinerary']
    ordering = ['day_number']

    def get_queryset(self):
        if self.request.user.is_staff:
            return ItineraryDay.objects.all()
        return ItineraryDay.objects.filter(itinerary__user=self.request.user)


class ItineraryItemViewSet(viewsets.ModelViewSet):
    """ViewSet for ItineraryItem model."""
    queryset = ItineraryItem.objects.all()
    serializer_class = ItineraryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['day', 'item_type', 'is_booked']
    ordering = ['order', 'start_time']

    def get_queryset(self):
        if self.request.user.is_staff:
            return ItineraryItem.objects.all()
        return ItineraryItem.objects.filter(day__itinerary__user=self.request.user)


class WeatherViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Weather model."""
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['location', 'date']
    ordering = ['date']
