from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, RatingViewSet

app_name = 'reviews'

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'ratings', RatingViewSet, basename='rating')

urlpatterns = [
    path('', include(router.urls)),
]
