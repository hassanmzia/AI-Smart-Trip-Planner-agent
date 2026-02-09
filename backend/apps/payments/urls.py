from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentMethodViewSet, PaymentViewSet, RefundViewSet

app_name = 'payments'

router = DefaultRouter()
router.register(r'methods', PaymentMethodViewSet, basename='method')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'refunds', RefundViewSet, basename='refund')

urlpatterns = [
    path('', include(router.urls)),
]
