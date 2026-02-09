from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttractionViewSet, AttractionCategoryViewSet

app_name = 'attractions'

router = DefaultRouter()
router.register(r'attractions', AttractionViewSet, basename='attraction')
router.register(r'categories', AttractionCategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
