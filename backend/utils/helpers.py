"""
Common utility functions and helpers.
"""
import re
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
import pytz
from django.conf import settings
from django.utils import timezone


def generate_random_string(length: int = 32, include_punctuation: bool = False) -> str:
    """
    Generate a cryptographically secure random string.

    Args:
        length: Length of the string to generate
        include_punctuation: Whether to include punctuation characters

    Returns:
        Random string
    """
    if include_punctuation:
        alphabet = string.ascii_letters + string.digits + string.punctuation
    else:
        alphabet = string.ascii_letters + string.digits

    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_confirmation_code(prefix: str = '', length: int = 8) -> str:
    """
    Generate a confirmation code for bookings, etc.

    Args:
        prefix: Optional prefix for the code
        length: Length of the random part

    Returns:
        Confirmation code (e.g., BK-ABC123XY)
    """
    random_part = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )

    if prefix:
        return f"{prefix}-{random_part}"

    return random_part


def hash_string(value: str, algorithm: str = 'sha256') -> str:
    """
    Hash a string using the specified algorithm.

    Args:
        value: String to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)

    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(value.encode('utf-8'))
    return hasher.hexdigest()


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (basic validation).

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Check if it contains only digits and optional + prefix
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, cleaned))


def format_currency(amount: Union[Decimal, float, int], currency: str = 'USD') -> str:
    """
    Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, etc.)

    Returns:
        Formatted currency string
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
    }

    symbol = symbols.get(currency, currency)

    if currency == 'JPY':
        # Japanese Yen has no decimal places
        return f"{symbol}{int(amount):,}"

    return f"{symbol}{float(amount):,.2f}"


def parse_currency(value: str) -> Optional[Decimal]:
    """
    Parse currency string to Decimal.

    Args:
        value: Currency string (e.g., "$1,234.56")

    Returns:
        Decimal value or None if parsing fails
    """
    try:
        # Remove currency symbols and separators
        cleaned = re.sub(r'[^\d.]', '', value)
        return Decimal(cleaned)
    except (ValueError, TypeError):
        return None


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two geographic coordinates using Haversine formula.

    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point

    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2

    # Earth's radius in kilometers
    R = 6371.0

    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """
    Convert datetime from one timezone to another.

    Args:
        dt: Datetime to convert
        from_tz: Source timezone name
        to_tz: Target timezone name

    Returns:
        Converted datetime
    """
    from_zone = pytz.timezone(from_tz)
    to_zone = pytz.timezone(to_tz)

    # Localize to source timezone if naive
    if dt.tzinfo is None:
        dt = from_zone.localize(dt)

    # Convert to target timezone
    return dt.astimezone(to_zone)


def get_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Generate list of dates between start and end dates.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        List of dates
    """
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate string to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing unsafe characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove unsafe characters
    safe_name = re.sub(r'[^\w\s\-\.]', '', filename)

    # Replace spaces with underscores
    safe_name = re.sub(r'\s+', '_', safe_name)

    # Remove duplicate underscores
    safe_name = re.sub(r'_+', '_', safe_name)

    return safe_name.strip('_')


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def get_client_ip(request) -> str:
    """
    Get client IP address from request, considering proxies.

    Args:
        request: Django request object

    Returns:
        IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 30m")
    """
    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"

    return f"{hours}h {remaining_minutes}m"


def calculate_percentage_change(old_value: Union[Decimal, float], new_value: Union[Decimal, float]) -> float:
    """
    Calculate percentage change between two values.

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        Percentage change (positive for increase, negative for decrease)
    """
    if old_value == 0:
        return 0.0 if new_value == 0 else 100.0

    return ((float(new_value) - float(old_value)) / float(old_value)) * 100


def parse_query_params(query_string: str) -> Dict[str, Any]:
    """
    Parse query string into dictionary.

    Args:
        query_string: URL query string

    Returns:
        Dictionary of query parameters
    """
    from urllib.parse import parse_qs

    params = parse_qs(query_string)

    # Convert single-item lists to single values
    result = {}
    for key, value in params.items():
        result[key] = value[0] if len(value) == 1 else value

    return result


def is_business_day(date: datetime) -> bool:
    """
    Check if date is a business day (Monday-Friday).

    Args:
        date: Date to check

    Returns:
        True if business day, False otherwise
    """
    return date.weekday() < 5


def get_next_business_day(date: datetime) -> datetime:
    """
    Get the next business day after the given date.

    Args:
        date: Starting date

    Returns:
        Next business day
    """
    next_day = date + timedelta(days=1)

    while not is_business_day(next_day):
        next_day += timedelta(days=1)

    return next_day


def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = '*') -> str:
    """
    Mask sensitive data, showing only last few characters.

    Args:
        data: Data to mask
        visible_chars: Number of characters to keep visible
        mask_char: Character to use for masking

    Returns:
        Masked string
    """
    if len(data) <= visible_chars:
        return mask_char * len(data)

    mask_length = len(data) - visible_chars
    return mask_char * mask_length + data[-visible_chars:]


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate URL-friendly slug from text.

    Args:
        text: Text to convert to slug
        max_length: Maximum length of slug

    Returns:
        Slug string
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    # Truncate if necessary
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')

    return slug


def retry_on_exception(func, max_retries: int = 3, delay: int = 1, exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on exception.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    import time
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0

        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                retries += 1

                if retries >= max_retries:
                    raise

                time.sleep(delay * retries)

        return None

    return wrapper
