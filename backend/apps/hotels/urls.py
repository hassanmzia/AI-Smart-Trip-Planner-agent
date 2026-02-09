from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, HotelSearchViewSet, search_hotels

app_name = 'hotels'

router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'searches', HotelSearchViewSet, basename='search')

urlpatterns = [
    path('', include(router.urls)),
    path('search', search_hotels, name='hotel_search'),
]
