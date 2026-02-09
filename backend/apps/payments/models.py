from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class PaymentMethod(models.Model):
    """Stored payment methods for users."""

    METHOD_TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
        ('wallet', 'Digital Wallet'),
    ]

    CARD_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )

    method_type = models.CharField(max_length=20, choices=METHOD_TYPE_CHOICES)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Card details (encrypted in production)
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, blank=True)
    last_four_digits = models.CharField(max_length=4, blank=True)
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    cardholder_name = models.CharField(max_length=255, blank=True)

    # Billing address
    billing_address = models.TextField(blank=True)
    billing_city = models.CharField(max_length=200, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)

    # External payment gateway reference
    gateway_payment_method_id = models.CharField(max_length=255, blank=True)
    gateway_name = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_methods'
        ordering = ['-is_default', '-created_at']
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'

    def __str__(self):
        if self.method_type == 'card':
            return f"{self.get_card_type_display()} ending in {self.last_four_digits}"
        return f"{self.get_method_type_display()}"


class Payment(models.Model):
    """Payment transactions."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )

    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Amounts
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='USD')
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Gateway information
    gateway_name = models.CharField(max_length=50)
    gateway_transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    # Timestamps
    payment_date = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['user', '-payment_date']),
            models.Index(fields=['booking']),
            models.Index(fields=['status', '-payment_date']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Detailed transaction log."""

    TRANSACTION_TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('chargeback', 'Chargeback'),
        ('adjustment', 'Adjustment'),
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)

    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_transactions'
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-timestamp']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} {self.currency}"


class Refund(models.Model):
    """Refund requests and processing."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    REASON_CHOICES = [
        ('cancellation', 'Booking Cancellation'),
        ('overcharge', 'Overcharge'),
        ('duplicate', 'Duplicate Payment'),
        ('service_issue', 'Service Issue'),
        ('other', 'Other'),
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refunds'
    )

    refund_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3)

    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_description = models.TextField(blank=True)

    # Processing
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds'
    )
    processing_notes = models.TextField(blank=True)

    # Gateway
    gateway_refund_id = models.CharField(max_length=255, blank=True)

    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'refunds'
        ordering = ['-requested_at']
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        indexes = [
            models.Index(fields=['user', '-requested_at']),
            models.Index(fields=['status', '-requested_at']),
        ]

    def __str__(self):
        return f"{self.refund_id} - {self.amount} {self.currency} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.refund_id:
            self.refund_id = f"REF{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
