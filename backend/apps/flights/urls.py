from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightViewSet, FlightSearchViewSet, PriceAlertViewSet

app_name = 'flights'

router = DefaultRouter()
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'searches', FlightSearchViewSet, basename='search')
router.register(r'price-alerts', PriceAlertViewSet, basename='price-alert')

urlpatterns = [
    path('', include(router.urls)),
]
