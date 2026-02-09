from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Hotel(models.Model):
    """Hotel information model."""

    STAR_RATING_CHOICES = [(i, f"{i} Star") for i in range(1, 6)]

    # Basic Information
    name = models.CharField(max_length=255, db_index=True)
    chain = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=200, blank=True)

    # Location
    address = models.TextField()
    city = models.CharField(max_length=200, db_index=True)
    state_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Ratings
    star_rating = models.IntegerField(choices=STAR_RATING_CHOICES, default=3)
    guest_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    review_count = models.IntegerField(default=0)

    # Property Details
    property_type = models.CharField(
        max_length=50,
        choices=[
            ('hotel', 'Hotel'),
            ('resort', 'Resort'),
            ('motel', 'Motel'),
            ('hostel', 'Hostel'),
            ('apartment', 'Apartment'),
            ('villa', 'Villa'),
            ('guesthouse', 'Guesthouse'),
        ],
        default='hotel'
    )

    total_rooms = models.IntegerField(default=0)
    check_in_time = models.TimeField(default='15:00:00')
    check_out_time = models.TimeField(default='11:00:00')

    # Description
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Images
    primary_image = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)

    # Price Range
    price_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    price_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hotels'
        ordering = ['-guest_rating', 'name']
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hotels'
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['star_rating', '-guest_rating']),
            models.Index(fields=['is_active', 'is_featured']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"


class HotelAmenity(models.Model):
    """Hotel amenities and features."""

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('room', 'Room'),
        ('bathroom', 'Bathroom'),
        ('food_drink', 'Food & Drink'),
        ('services', 'Services'),
        ('entertainment', 'Entertainment'),
        ('business', 'Business'),
        ('wellness', 'Wellness'),
        ('outdoor', 'Outdoor'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_free = models.BooleanField(default=True)
    additional_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'hotel_amenities'
        verbose_name = 'Hotel Amenity'
        verbose_name_plural = 'Hotel Amenities'
        indexes = [
            models.Index(fields=['hotel', 'category']),
        ]

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class HotelSearch(models.Model):
    """Track hotel searches for analytics."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hotel_searches',
        null=True,
        blank=True
    )

    # Search parameters
    city = models.CharField(max_length=200, db_index=True)
    country = models.CharField(max_length=100, blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    nights = models.IntegerField(default=1)

    # Guest details
    rooms = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    adults = models.IntegerField(default=2, validators=[MinValueValidator(1)])
    children = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Preferences
    min_star_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    min_guest_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True
    )
    property_types = models.JSONField(default=list, blank=True)
    amenities = models.JSONField(default=list, blank=True)

    # Budget
    max_price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Results
    results_count = models.IntegerField(default=0)
    search_duration_ms = models.IntegerField(default=0)

    # Session
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotel_searches'
        ordering = ['-created_at']
        verbose_name = 'Hotel Search'
        verbose_name_plural = 'Hotel Searches'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['city', '-created_at']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{user_str} - {self.city} ({self.check_in_date} to {self.check_out_date})"

    @property
    def total_guests(self):
        """Calculate total number of guests."""
        return self.adults + self.children
