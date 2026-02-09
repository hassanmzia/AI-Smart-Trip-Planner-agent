from django.db import models
from django.conf import settings


class UserActivity(models.Model):
    """Track user activity for analytics."""

    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('search_flight', 'Search Flight'),
        ('search_hotel', 'Search Hotel'),
        ('view_flight', 'View Flight'),
        ('view_hotel', 'View Hotel'),
        ('create_booking', 'Create Booking'),
        ('payment', 'Payment'),
        ('create_review', 'Create Review'),
        ('create_itinerary', 'Create Itinerary'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)

    # Session info
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Location
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=200, blank=True)

    # Additional data
    metadata = models.JSONField(default=dict, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'user_activities'
        ordering = ['-timestamp']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{user_str} - {self.get_action_display()} ({self.timestamp})"


class SearchAnalytics(models.Model):
    """Analytics for search behavior."""

    search_type = models.CharField(
        max_length=20,
        choices=[
            ('flight', 'Flight'),
            ('hotel', 'Hotel'),
            ('car', 'Car Rental'),
            ('restaurant', 'Restaurant'),
            ('attraction', 'Attraction'),
        ]
    )

    # Search parameters
    origin = models.CharField(max_length=200, blank=True, db_index=True)
    destination = models.CharField(max_length=200, blank=True, db_index=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Results
    results_count = models.IntegerField(default=0)
    search_duration_ms = models.IntegerField(default=0)

    # User interaction
    clicked_results = models.JSONField(default=list, blank=True)
    converted_to_booking = models.BooleanField(default=False)

    # Session
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_analytics',
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'search_analytics'
        ordering = ['-timestamp']
        verbose_name = 'Search Analytics'
        verbose_name_plural = 'Search Analytics'
        indexes = [
            models.Index(fields=['search_type', '-timestamp']),
            models.Index(fields=['destination', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.search_type} search: {self.origin} to {self.destination}"


class BookingAnalytics(models.Model):
    """Analytics for booking behavior."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_analytics',
        null=True,
        blank=True
    )

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='analytics',
        null=True,
        blank=True
    )

    # Booking details
    booking_type = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)

    # User journey
    search_to_booking_minutes = models.IntegerField(null=True, blank=True)
    page_views_before_booking = models.IntegerField(default=0)
    searches_before_booking = models.IntegerField(default=0)

    # Device & source
    device_type = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=100, blank=True)
    referrer = models.URLField(blank=True)

    # Payment
    payment_method = models.CharField(max_length=50, blank=True)
    payment_success = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'booking_analytics'
        ordering = ['-created_at']
        verbose_name = 'Booking Analytics'
        verbose_name_plural = 'Booking Analytics'

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{user_str} - {self.booking_type} booking"
