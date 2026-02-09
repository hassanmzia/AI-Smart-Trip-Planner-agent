from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class AttractionCategory(models.Model):
    """Categories for attractions."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    class Meta:
        db_table = 'attraction_categories'
        ordering = ['name']
        verbose_name = 'Attraction Category'
        verbose_name_plural = 'Attraction Categories'

    def __str__(self):
        return self.name


class Attraction(models.Model):
    """Tourist attractions and activities."""

    TYPE_CHOICES = [
        ('museum', 'Museum'),
        ('monument', 'Monument'),
        ('park', 'Park'),
        ('theme_park', 'Theme Park'),
        ('zoo', 'Zoo'),
        ('aquarium', 'Aquarium'),
        ('theater', 'Theater'),
        ('gallery', 'Art Gallery'),
        ('landmark', 'Landmark'),
        ('tour', 'Tour'),
        ('activity', 'Activity'),
        ('entertainment', 'Entertainment'),
    ]

    # Basic info
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    attraction_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    categories = models.ManyToManyField(AttractionCategory, related_name='attractions')

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
    is_open_24_7 = models.BooleanField(default=False)

    # Pricing
    admission_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')
    is_free = models.BooleanField(default=False)

    # Duration
    typical_duration_minutes = models.IntegerField(null=True, blank=True)

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

    # Media
    primary_image = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)
    video_urls = models.JSONField(default=list, blank=True)

    # Features
    accessibility_features = models.JSONField(default=list, blank=True)
    amenities = models.JSONField(default=list, blank=True)
    languages_available = models.JSONField(default=list, blank=True)

    # Booking
    booking_required = models.BooleanField(default=False)
    booking_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attractions'
        ordering = ['-rating', 'name']
        verbose_name = 'Attraction'
        verbose_name_plural = 'Attractions'
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['attraction_type']),
            models.Index(fields=['-rating']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"
