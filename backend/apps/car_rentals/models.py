from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class CarType(models.Model):
    """Car type/category."""

    CATEGORY_CHOICES = [
        ('economy', 'Economy'),
        ('compact', 'Compact'),
        ('midsize', 'Midsize'),
        ('fullsize', 'Full-size'),
        ('suv', 'SUV'),
        ('luxury', 'Luxury'),
        ('van', 'Van/Minivan'),
        ('convertible', 'Convertible'),
        ('sports', 'Sports Car'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Capacity
    passenger_capacity = models.IntegerField(default=5)
    luggage_capacity = models.IntegerField(default=2)

    # Features
    transmission = models.CharField(
        max_length=20,
        choices=[('automatic', 'Automatic'), ('manual', 'Manual')],
        default='automatic'
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=[
            ('petrol', 'Petrol'),
            ('diesel', 'Diesel'),
            ('electric', 'Electric'),
            ('hybrid', 'Hybrid'),
        ],
        default='petrol'
    )

    # Media
    image = models.URLField(blank=True)

    class Meta:
        db_table = 'car_types'
        ordering = ['category', 'name']
        verbose_name = 'Car Type'
        verbose_name_plural = 'Car Types'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class CarRental(models.Model):
    """Car rental vehicle information."""

    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
        ('unavailable', 'Unavailable'),
    ]

    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE, related_name='rentals')

    # Vehicle details
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=50, blank=True)
    license_plate = models.CharField(max_length=20, blank=True)

    # Location
    rental_company = models.CharField(max_length=200)
    pickup_location = models.CharField(max_length=200, db_index=True)
    pickup_address = models.TextField()
    pickup_city = models.CharField(max_length=200, db_index=True)
    pickup_country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Pricing (per day)
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='USD')

    # Additional costs
    insurance_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_driver_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    young_driver_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Features & Amenities
    features = models.JSONField(default=list, blank=True)  # GPS, child seat, etc.
    has_gps = models.BooleanField(default=False)
    has_bluetooth = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=True)

    # Policies
    minimum_age = models.IntegerField(default=21)
    mileage_limit_per_day = models.IntegerField(null=True, blank=True)  # null = unlimited
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Images
    primary_image = models.URLField(blank=True)
    images = models.JSONField(default=list, blank=True)

    # Availability
    status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='available')
    is_active = models.BooleanField(default=True)

    # Rating
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    review_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'car_rentals'
        ordering = ['price_per_day']
        verbose_name = 'Car Rental'
        verbose_name_plural = 'Car Rentals'
        indexes = [
            models.Index(fields=['pickup_city', 'status']),
            models.Index(fields=['car_type', 'status']),
        ]

    def __str__(self):
        return f"{self.year} {self.make} {self.model} - {self.pickup_city}"


class RentalBooking(models.Model):
    """Car rental booking."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='car_rental_bookings'
    )

    car_rental = models.ForeignKey(
        CarRental,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    booking_reference = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Rental period
    pickup_date = models.DateTimeField()
    return_date = models.DateTimeField()
    total_days = models.IntegerField()

    # Locations
    pickup_location = models.CharField(max_length=200)
    return_location = models.CharField(max_length=200)
    different_return_location = models.BooleanField(default=False)

    # Driver information
    driver_name = models.CharField(max_length=255)
    driver_email = models.EmailField()
    driver_phone = models.CharField(max_length=20)
    driver_license_number = models.CharField(max_length=50)
    driver_age = models.IntegerField()

    # Additional options
    additional_drivers = models.IntegerField(default=0)
    includes_insurance = models.BooleanField(default=False)
    special_requests = models.TextField(blank=True)

    # Costs
    rental_cost = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Deposit
    deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_refunded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rental_bookings'
        ordering = ['-pickup_date']
        verbose_name = 'Rental Booking'
        verbose_name_plural = 'Rental Bookings'
        indexes = [
            models.Index(fields=['user', '-pickup_date']),
            models.Index(fields=['booking_reference']),
            models.Index(fields=['status', '-pickup_date']),
        ]

    def __str__(self):
        return f"{self.booking_reference} - {self.driver_name}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import uuid
            self.booking_reference = f"CR{uuid.uuid4().hex[:8].upper()}"

        # Calculate total days
        if self.pickup_date and self.return_date:
            duration = self.return_date - self.pickup_date
            self.total_days = max(1, duration.days)

        super().save(*args, **kwargs)
