from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Cuisine(models.Model):
    """Cuisine types."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'cuisines'
        ordering = ['name']
        verbose_name = 'Cuisine'
        verbose_name_plural = 'Cuisines'

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """Restaurant information model."""

    PRICE_RANGE_CHOICES = [
        ('$', 'Budget ($)'),
        ('$$', 'Moderate ($$)'),
        ('$$$', 'Upscale ($$$)'),
        ('$$$$', 'Fine Dining ($$$$)'),
    ]

    # Basic info
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    cuisines = models.ManyToManyField(Cuisine, related_name='restaurants')

    # Location
    address = models.TextField()
    city = models.CharField(max_length=200, db_index=True)
    state_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Operating hours
    opening_hours = models.JSONField(default=dict, blank=True)

    # Pricing
    price_range = models.CharField(max_length=5, choices=PRICE_RANGE_CHOICES, default='$$')
    average_cost_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Ratings
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(default=0)

    # Features
    seating_capacity = models.IntegerField(null=True, blank=True)
    has_outdoor_seating = models.BooleanField(default=False)
    has_delivery = models.BooleanField(default=False)
    has_takeout = models.BooleanField(default=False)
    has_reservation = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    is_wheelchair_accessible = models.BooleanField(default=False)

    dietary_options = models.JSONField(default=list, blank=True)  # vegetarian, vegan, gluten-free, etc.
    amenities = models.JSONField(default=list, blank=True)

    # Media
    primary_image = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)
    menu_url = models.URLField(blank=True)

    # Booking
    reservation_url = models.URLField(blank=True)
    delivery_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants'
        ordering = ['-rating', 'name']
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['price_range']),
            models.Index(fields=['-rating']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"


class RestaurantBooking(models.Model):
    """Restaurant reservation/booking."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurant_bookings'
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    booking_reference = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Reservation details
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.IntegerField(validators=[MinValueValidator(1)])

    # Guest information
    guest_name = models.CharField(max_length=255)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)

    # Preferences
    special_requests = models.TextField(blank=True)
    seating_preference = models.CharField(max_length=100, blank=True)

    # Notifications
    reminder_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurant_bookings'
        ordering = ['-reservation_date', '-reservation_time']
        verbose_name = 'Restaurant Booking'
        verbose_name_plural = 'Restaurant Bookings'
        indexes = [
            models.Index(fields=['user', '-reservation_date']),
            models.Index(fields=['restaurant', 'reservation_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.booking_reference} - {self.restaurant.name} ({self.reservation_date})"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import uuid
            self.booking_reference = f"RB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
