from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItineraryViewSet, ItineraryDayViewSet, ItineraryItemViewSet, WeatherViewSet

app_name = 'itineraries'

router = DefaultRouter()
router.register(r'itineraries', ItineraryViewSet, basename='itinerary')
router.register(r'days', ItineraryDayViewSet, basename='day')
router.register(r'items', ItineraryItemViewSet, basename='item')
router.register(r'weather', WeatherViewSet, basename='weather')

urlpatterns = [
    path('', include(router.urls)),
]
