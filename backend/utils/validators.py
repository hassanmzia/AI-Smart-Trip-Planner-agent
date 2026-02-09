"""
Custom validators for model fields and API inputs.
"""
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Any, List, Optional, Union
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator as DjangoEmailValidator
from django.utils import timezone


class EmailValidator(DjangoEmailValidator):
    """
    Enhanced email validator with additional checks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Enter a valid email address'

    def __call__(self, value):
        super().__call__(value)

        # Additional checks
        if value:
            # Check for disposable email domains
            disposable_domains = [
                'tempmail.com', 'throwaway.email', '10minutemail.com',
                'guerrillamail.com', 'mailinator.com'
            ]

            domain = value.split('@')[1].lower()

            if domain in disposable_domains:
                raise ValidationError('Disposable email addresses are not allowed')


def validate_phone_number(value: str) -> None:
    """
    Validate phone number format.

    Args:
        value: Phone number string

    Raises:
        ValidationError: If phone number is invalid
    """
    if not value:
        return

    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', value)

    # Check format
    pattern = r'^\+?[1-9]\d{9,14}$'

    if not re.match(pattern, cleaned):
        raise ValidationError(
            'Enter a valid phone number with country code (e.g., +1234567890)'
        )


def validate_postal_code(value: str, country: str = 'US') -> None:
    """
    Validate postal code format based on country.

    Args:
        value: Postal code string
        country: Country code (ISO 3166-1 alpha-2)

    Raises:
        ValidationError: If postal code is invalid
    """
    if not value:
        return

    patterns = {
        'US': r'^\d{5}(-\d{4})?$',
        'CA': r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$',
        'UK': r'^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$',
        'DE': r'^\d{5}$',
        'FR': r'^\d{5}$',
        'JP': r'^\d{3}-?\d{4}$',
    }

    pattern = patterns.get(country.upper())

    if not pattern:
        # Generic validation for unknown countries
        if not re.match(r'^[A-Z0-9\s\-]{3,10}$', value.upper()):
            raise ValidationError('Enter a valid postal code')
        return

    if not re.match(pattern, value.upper()):
        raise ValidationError(f'Enter a valid {country} postal code')


def validate_passport_number(value: str) -> None:
    """
    Validate passport number format.

    Args:
        value: Passport number string

    Raises:
        ValidationError: If passport number is invalid
    """
    if not value:
        return

    # Remove spaces
    cleaned = value.replace(' ', '')

    # Basic validation: 6-12 alphanumeric characters
    if not re.match(r'^[A-Z0-9]{6,12}$', cleaned.upper()):
        raise ValidationError('Enter a valid passport number (6-12 alphanumeric characters)')


def validate_credit_card_number(value: str) -> None:
    """
    Validate credit card number using Luhn algorithm.

    Args:
        value: Credit card number string

    Raises:
        ValidationError: If credit card number is invalid
    """
    if not value:
        return

    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', value)

    # Check if all digits
    if not cleaned.isdigit():
        raise ValidationError('Credit card number must contain only digits')

    # Check length (13-19 digits)
    if not 13 <= len(cleaned) <= 19:
        raise ValidationError('Credit card number must be 13-19 digits')

    # Luhn algorithm
    def luhn_check(card_number):
        digits = [int(d) for d in card_number]
        checksum = 0

        # Double every second digit from right to left
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9

        return sum(digits) % 10 == 0

    if not luhn_check(cleaned):
        raise ValidationError('Invalid credit card number')


def validate_cvv(value: str, card_type: str = None) -> None:
    """
    Validate CVV/CVC code.

    Args:
        value: CVV code string
        card_type: Optional card type (amex requires 4 digits)

    Raises:
        ValidationError: If CVV is invalid
    """
    if not value:
        return

    # American Express uses 4 digits, others use 3
    expected_length = 4 if card_type == 'amex' else 3

    if not value.isdigit() or len(value) != expected_length:
        raise ValidationError(f'CVV must be {expected_length} digits')


def validate_date_range(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> None:
    """
    Validate that end date is after start date.

    Args:
        start_date: Start date
        end_date: End date

    Raises:
        ValidationError: If date range is invalid
    """
    if not start_date or not end_date:
        return

    if end_date < start_date:
        raise ValidationError('End date must be after start date')


def validate_future_date(value: Union[date, datetime]) -> None:
    """
    Validate that date is in the future.

    Args:
        value: Date to validate

    Raises:
        ValidationError: If date is not in the future
    """
    if not value:
        return

    now = timezone.now()

    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, datetime.min.time())
        value = timezone.make_aware(value)

    if value <= now:
        raise ValidationError('Date must be in the future')


def validate_past_date(value: Union[date, datetime]) -> None:
    """
    Validate that date is in the past.

    Args:
        value: Date to validate

    Raises:
        ValidationError: If date is not in the past
    """
    if not value:
        return

    now = timezone.now()

    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, datetime.min.time())
        value = timezone.make_aware(value)

    if value >= now:
        raise ValidationError('Date must be in the past')


def validate_age_range(birth_date: date, min_age: int = 0, max_age: int = 150) -> None:
    """
    Validate age based on birth date.

    Args:
        birth_date: Birth date
        min_age: Minimum required age
        max_age: Maximum allowed age

    Raises:
        ValidationError: If age is outside allowed range
    """
    if not birth_date:
        return

    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    if age < min_age:
        raise ValidationError(f'Must be at least {min_age} years old')

    if age > max_age:
        raise ValidationError(f'Age cannot exceed {max_age} years')


def validate_price(value: Union[Decimal, float, int]) -> None:
    """
    Validate price value.

    Args:
        value: Price value

    Raises:
        ValidationError: If price is invalid
    """
    if value is None:
        return

    try:
        price = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError('Invalid price format')

    if price < 0:
        raise ValidationError('Price cannot be negative')

    if price > Decimal('999999.99'):
        raise ValidationError('Price exceeds maximum allowed value')

    # Check decimal places
    if price.as_tuple().exponent < -2:
        raise ValidationError('Price can have at most 2 decimal places')


def validate_coordinates(latitude: float, longitude: float) -> None:
    """
    Validate geographic coordinates.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Raises:
        ValidationError: If coordinates are invalid
    """
    if latitude is None or longitude is None:
        return

    if not -90 <= latitude <= 90:
        raise ValidationError('Latitude must be between -90 and 90')

    if not -180 <= longitude <= 180:
        raise ValidationError('Longitude must be between -180 and 180')


def validate_url(value: str, allowed_schemes: List[str] = None) -> None:
    """
    Validate URL format.

    Args:
        value: URL string
        allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])

    Raises:
        ValidationError: If URL is invalid
    """
    if not value:
        return

    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']

    pattern = r'^(https?):\/\/([\w\d\-_]+\.)+[\w\d\-_]+(\/[\w\d\-_\.\/\?=&]*)?$'

    if not re.match(pattern, value, re.IGNORECASE):
        raise ValidationError('Enter a valid URL')

    scheme = value.split('://')[0].lower()

    if scheme not in allowed_schemes:
        raise ValidationError(f'URL scheme must be one of: {", ".join(allowed_schemes)}')


def validate_file_size(file, max_size_mb: int = 10) -> None:
    """
    Validate uploaded file size.

    Args:
        file: Uploaded file object
        max_size_mb: Maximum file size in megabytes

    Raises:
        ValidationError: If file is too large
    """
    if not file:
        return

    max_size_bytes = max_size_mb * 1024 * 1024

    if file.size > max_size_bytes:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB')


def validate_file_extension(file, allowed_extensions: List[str]) -> None:
    """
    Validate uploaded file extension.

    Args:
        file: Uploaded file object
        allowed_extensions: List of allowed extensions (e.g., ['pdf', 'jpg'])

    Raises:
        ValidationError: If file extension is not allowed
    """
    if not file:
        return

    extension = file.name.split('.')[-1].lower()

    if extension not in [ext.lower() for ext in allowed_extensions]:
        raise ValidationError(
            f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
        )


def validate_image_dimensions(file, min_width: int = None, min_height: int = None,
                              max_width: int = None, max_height: int = None) -> None:
    """
    Validate image dimensions.

    Args:
        file: Uploaded image file
        min_width: Minimum width in pixels
        min_height: Minimum height in pixels
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels

    Raises:
        ValidationError: If image dimensions are invalid
    """
    if not file:
        return

    try:
        from PIL import Image

        image = Image.open(file)
        width, height = image.size

        if min_width and width < min_width:
            raise ValidationError(f'Image width must be at least {min_width}px')

        if min_height and height < min_height:
            raise ValidationError(f'Image height must be at least {min_height}px')

        if max_width and width > max_width:
            raise ValidationError(f'Image width cannot exceed {max_width}px')

        if max_height and height > max_height:
            raise ValidationError(f'Image height cannot exceed {max_height}px')

    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')


def validate_json_structure(value: Any, required_fields: List[str] = None) -> None:
    """
    Validate JSON data structure.

    Args:
        value: JSON data (dict)
        required_fields: List of required field names

    Raises:
        ValidationError: If JSON structure is invalid
    """
    if not isinstance(value, dict):
        raise ValidationError('Value must be a JSON object')

    if required_fields:
        missing_fields = [field for field in required_fields if field not in value]

        if missing_fields:
            raise ValidationError(f'Missing required fields: {", ".join(missing_fields)}')


def validate_password_strength(password: str) -> None:
    """
    Validate password strength.

    Args:
        password: Password string

    Raises:
        ValidationError: If password is not strong enough
    """
    if not password:
        return

    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')

    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')

    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')

    # Check for common passwords
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234567890'
    ]

    if password.lower() in common_passwords:
        raise ValidationError('Password is too common')


def validate_username(username: str) -> None:
    """
    Validate username format.

    Args:
        username: Username string

    Raises:
        ValidationError: If username is invalid
    """
    if not username:
        return

    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long')

    if len(username) > 30:
        raise ValidationError('Username cannot exceed 30 characters')

    if not re.match(r'^[a-zA-Z0-9_\-]+$', username):
        raise ValidationError('Username can only contain letters, numbers, underscores, and hyphens')

    if username[0] in '_-' or username[-1] in '_-':
        raise ValidationError('Username cannot start or end with underscore or hyphen')


def validate_booking_dates(departure_date: datetime, return_date: datetime = None,
                           min_advance_days: int = 0, max_advance_days: int = 365) -> None:
    """
    Validate booking dates.

    Args:
        departure_date: Departure date
        return_date: Optional return date
        min_advance_days: Minimum days in advance for booking
        max_advance_days: Maximum days in advance for booking

    Raises:
        ValidationError: If booking dates are invalid
    """
    now = timezone.now()

    # Check departure date is in future
    if departure_date <= now:
        raise ValidationError('Departure date must be in the future')

    # Check minimum advance booking
    min_date = now + timezone.timedelta(days=min_advance_days)
    if departure_date < min_date:
        raise ValidationError(f'Booking must be made at least {min_advance_days} days in advance')

    # Check maximum advance booking
    max_date = now + timezone.timedelta(days=max_advance_days)
    if departure_date > max_date:
        raise ValidationError(f'Booking cannot be made more than {max_advance_days} days in advance')

    # Validate return date if provided
    if return_date:
        if return_date <= departure_date:
            raise ValidationError('Return date must be after departure date')

        # Check maximum trip duration
        trip_duration = (return_date - departure_date).days
        if trip_duration > 365:
            raise ValidationError('Trip duration cannot exceed 365 days')
