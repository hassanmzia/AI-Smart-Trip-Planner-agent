from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserActivityViewSet, SearchAnalyticsViewSet, BookingAnalyticsViewSet

app_name = 'analytics'

router = DefaultRouter()
router.register(r'activities', UserActivityViewSet, basename='activity')
router.register(r'searches', SearchAnalyticsViewSet, basename='search')
router.register(r'bookings', BookingAnalyticsViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]
