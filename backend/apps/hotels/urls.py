from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, HotelSearchViewSet

app_name = 'hotels'

router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'searches', HotelSearchViewSet, basename='search')

urlpatterns = [
    path('', include(router.urls)),
]
