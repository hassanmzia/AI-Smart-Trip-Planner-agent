from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    """User notifications."""

    TYPE_CHOICES = [
        ('booking', 'Booking Update'),
        ('payment', 'Payment'),
        ('price_alert', 'Price Alert'),
        ('itinerary', 'Itinerary'),
        ('review', 'Review'),
        ('system', 'System'),
        ('promotional', 'Promotional'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    title = models.CharField(max_length=255)
    message = models.TextField()

    # Related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Actions
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Delivery channels
    sent_email = models.BooleanField(default=False)
    sent_push = models.BooleanField(default=False)
    sent_sms = models.BooleanField(default=False)

    # Additional data
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class NotificationPreference(models.Model):
    """User notification preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Email preferences
    email_booking_updates = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_price_alerts = models.BooleanField(default=True)
    email_itinerary_updates = models.BooleanField(default=True)
    email_promotional = models.BooleanField(default=False)
    email_newsletter = models.BooleanField(default=False)

    # Push notification preferences
    push_booking_updates = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)
    push_price_alerts = models.BooleanField(default=True)
    push_itinerary_updates = models.BooleanField(default=False)
    push_promotional = models.BooleanField(default=False)

    # SMS preferences
    sms_booking_updates = models.BooleanField(default=False)
    sms_payment_updates = models.BooleanField(default=False)
    sms_price_alerts = models.BooleanField(default=False)

    # Frequency
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('realtime', 'Real-time'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('never', 'Never'),
        ],
        default='realtime'
    )

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"
