"""
Custom decorators for views and functions.
"""
import time
import logging
from functools import wraps
from typing import Callable, Any
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status

logger = logging.getLogger(__name__)


def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure and log function execution time.

    Usage:
        @timing_decorator
        def my_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed_time = time.time() - start_time
            logger.info(
                f"{func.__module__}.{func.__name__} executed in {elapsed_time:.4f}s"
            )

    return wrapper


def cache_result(timeout: int = 300, key_prefix: str = None):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Optional prefix for cache key

    Usage:
        @cache_result(timeout=600, key_prefix='my_func')
        def my_function(param1, param2):
            return expensive_operation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [
                key_prefix or func.__name__,
                str(args),
                str(sorted(kwargs.items()))
            ]
            cache_key = ':'.join(cache_key_parts)

            # Try to get from cache
            cached_result = cache.get(cache_key)

            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)

            logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result

        return wrapper

    return decorator


def rate_limit(key: str, rate: int = 10, period: int = 60):
    """
    Rate limiting decorator.

    Args:
        key: Cache key for rate limiting (can include request parameters)
        rate: Number of allowed requests
        period: Time period in seconds

    Usage:
        @rate_limit(key='api_endpoint', rate=10, period=60)
        def my_view(request):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Generate rate limit key
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
            else:
                from utils.helpers import get_client_ip
                user_id = get_client_ip(request)

            cache_key = f"rate_limit:{key}:{user_id}"

            # Get current count
            current_count = cache.get(cache_key, 0)

            if current_count >= rate:
                logger.warning(f"Rate limit exceeded for {user_id} on {key}")
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'detail': f'Maximum {rate} requests per {period} seconds'
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Increment counter
            cache.set(cache_key, current_count + 1, period)

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_api_key(func: Callable) -> Callable:
    """
    Decorator to require API key authentication.

    Usage:
        @require_api_key
        def my_view(request):
            pass
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')

        if not api_key:
            return JsonResponse(
                {'error': 'API key required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Validate API key
        # TODO: Implement actual API key validation
        if api_key != settings.API_KEY:
            return JsonResponse(
                {'error': 'Invalid API key'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return func(request, *args, **kwargs)

    return wrapper


def log_exceptions(func: Callable) -> Callable:
    """
    Decorator to log exceptions with full traceback.

    Usage:
        @log_exceptions
        def my_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(
                f"Exception in {func.__module__}.{func.__name__}: {str(e)}"
            )
            raise

    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier
        exceptions: Tuple of exceptions to catch

    Usage:
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        def unreliable_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {str(e)}. "
                        f"Retrying in {current_delay}s..."
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper

    return decorator


def require_verified_email(func: Callable) -> Callable:
    """
    Decorator to require verified email for view access.

    Usage:
        @require_verified_email
        def my_view(request):
            pass
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.email_verified:
            return JsonResponse(
                {
                    'error': 'Email verification required',
                    'detail': 'Please verify your email address to access this resource'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return func(request, *args, **kwargs)

    return wrapper


def transaction_atomic(func: Callable) -> Callable:
    """
    Decorator to wrap function in database transaction.

    Usage:
        @transaction_atomic
        def my_function():
            pass
    """
    from django.db import transaction

    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            return func(*args, **kwargs)

    return wrapper


def validate_request_data(*required_fields):
    """
    Decorator to validate required fields in request data.

    Args:
        *required_fields: Names of required fields

    Usage:
        @validate_request_data('name', 'email')
        def my_view(request):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get request data
            if request.method in ['POST', 'PUT', 'PATCH']:
                data = request.POST if request.POST else request.data
            else:
                data = request.GET

            # Check for required fields
            missing_fields = []

            for field in required_fields:
                if field not in data or not data.get(field):
                    missing_fields.append(field)

            if missing_fields:
                return JsonResponse(
                    {
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def admin_only(func: Callable) -> Callable:
    """
    Decorator to restrict access to admin users only.

    Usage:
        @admin_only
        def admin_view(request):
            pass
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.is_staff and not request.user.is_superuser:
            return JsonResponse(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        return func(request, *args, **kwargs)

    return wrapper


def cors_allow_all(func: Callable) -> Callable:
    """
    Decorator to add CORS headers allowing all origins.
    Use with caution - only for public endpoints.

    Usage:
        @cors_allow_all
        def public_api_view(request):
            pass
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        return response

    return wrapper


def deprecated(replacement: str = None):
    """
    Decorator to mark function as deprecated.

    Args:
        replacement: Name of replacement function

    Usage:
        @deprecated(replacement='new_function')
        def old_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = f"{func.__name__} is deprecated"

            if replacement:
                message += f". Use {replacement} instead"

            logger.warning(message)

            return func(*args, **kwargs)

        return wrapper

    return decorator
