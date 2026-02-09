from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Flight(models.Model):
    """Flight information model."""

    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('premium_economy', 'Premium Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Flight identification
    flight_number = models.CharField(max_length=20, db_index=True)
    airline_code = models.CharField(max_length=3)
    airline_name = models.CharField(max_length=200)

    # Route information
    origin_airport = models.CharField(max_length=3, db_index=True)  # IATA code
    origin_city = models.CharField(max_length=200)
    origin_country = models.CharField(max_length=100)

    destination_airport = models.CharField(max_length=3, db_index=True)  # IATA code
    destination_city = models.CharField(max_length=200)
    destination_country = models.CharField(max_length=100)

    # Schedule
    departure_time = models.DateTimeField(db_index=True)
    arrival_time = models.DateTimeField()
    duration_minutes = models.IntegerField()

    # Aircraft
    aircraft_type = models.CharField(max_length=50, blank=True)
    aircraft_model = models.CharField(max_length=100, blank=True)

    # Flight details
    travel_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Capacity
    total_seats = models.IntegerField(default=0)
    available_seats = models.IntegerField(default=0)

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='USD')

    # Amenities
    has_wifi = models.BooleanField(default=False)
    has_meals = models.BooleanField(default=False)
    has_entertainment = models.BooleanField(default=False)
    baggage_allowance_kg = models.IntegerField(default=23)
    carry_on_allowance_kg = models.IntegerField(default=7)

    # Stops
    is_direct = models.BooleanField(default=True, db_index=True)
    stops_count = models.IntegerField(default=0)
    layover_airports = models.JSONField(default=list, blank=True)

    # Metadata
    booking_url = models.URLField(blank=True)
    terms_and_conditions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'flights'
        ordering = ['departure_time']
        verbose_name = 'Flight'
        verbose_name_plural = 'Flights'
        indexes = [
            models.Index(fields=['origin_airport', 'destination_airport', 'departure_time']),
            models.Index(fields=['airline_code', 'flight_number']),
            models.Index(fields=['status', 'departure_time']),
        ]

    def __str__(self):
        return f"{self.airline_code}{self.flight_number} - {self.origin_airport} to {self.destination_airport}"

    @property
    def is_available(self):
        """Check if flight has available seats."""
        return self.available_seats > 0 and self.status == 'scheduled'


class FlightSearch(models.Model):
    """Track user flight searches for analytics and recommendations."""

    TRIP_TYPE_CHOICES = [
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
        ('multi_city', 'Multi City'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flight_searches',
        null=True,
        blank=True  # Allow anonymous searches
    )

    # Search parameters
    origin_airport = models.CharField(max_length=3)
    origin_city = models.CharField(max_length=200, blank=True)

    destination_airport = models.CharField(max_length=3)
    destination_city = models.CharField(max_length=200, blank=True)

    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES, default='round_trip')

    # Passenger details
    adults = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    children = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    infants = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Preferences
    preferred_class = models.CharField(max_length=20, default='economy')
    direct_flights_only = models.BooleanField(default=False)
    preferred_airlines = models.JSONField(default=list, blank=True)

    # Budget
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Search results metadata
    results_count = models.IntegerField(default=0)
    search_duration_ms = models.IntegerField(default=0)

    # User session
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'flight_searches'
        ordering = ['-created_at']
        verbose_name = 'Flight Search'
        verbose_name_plural = 'Flight Searches'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['origin_airport', 'destination_airport']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{user_str} - {self.origin_airport} to {self.destination_airport} ({self.departure_date})"

    @property
    def total_passengers(self):
        """Calculate total number of passengers."""
        return self.adults + self.children + self.infants


class PriceAlert(models.Model):
    """Price alerts for flight routes."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('triggered', 'Triggered'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='price_alerts'
    )

    # Route
    origin_airport = models.CharField(max_length=3)
    destination_airport = models.CharField(max_length=3)

    # Travel dates
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    # Alert settings
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='USD')

    # Preferences
    travel_class = models.CharField(max_length=20, default='economy')
    preferred_airlines = models.JSONField(default=list, blank=True)

    # Alert status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    lowest_price_seen = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Notification settings
    email_notification = models.BooleanField(default=True)
    push_notification = models.BooleanField(default=True)

    # Tracking
    last_checked_at = models.DateTimeField(null=True, blank=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'price_alerts'
        ordering = ['-created_at']
        verbose_name = 'Price Alert'
        verbose_name_plural = 'Price Alerts'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['origin_airport', 'destination_airport']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.origin_airport} to {self.destination_airport} (Target: {self.target_price} {self.currency})"

    @property
    def is_active(self):
        """Check if alert is still active."""
        return self.status == 'active' and self.expiry_date >= timezone.now().date()

    def check_price(self, current_price):
        """Check if current price meets target and trigger alert if needed."""
        self.current_price = current_price
        self.last_checked_at = timezone.now()

        # Update lowest price seen
        if self.lowest_price_seen is None or current_price < self.lowest_price_seen:
            self.lowest_price_seen = current_price

        # Trigger alert if price is at or below target
        if current_price <= self.target_price and self.status == 'active':
            self.status = 'triggered'
            self.triggered_at = timezone.now()

        self.save()
