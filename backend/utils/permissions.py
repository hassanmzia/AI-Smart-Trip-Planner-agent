"""
Custom DRF permission classes.
"""
from rest_framework import permissions
from django.utils import timezone


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if request user owns the object.
        """
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read-only access to anyone,
    but write access only to owner.
    """

    def has_object_permission(self, request, view, obj):
        """
        Allow read permissions to any request,
        write permissions only to owner.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read-only access to anyone,
    but write access only to admins.
    """

    def has_permission(self, request, view):
        """
        Allow read permissions to any request,
        write permissions only to admin users.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission to only allow verified users.
    """

    message = 'Email verification required'

    def has_permission(self, request, view):
        """
        Check if user has verified email.
        """
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'email_verified', True)
        )


class IsActiveUser(permissions.BasePermission):
    """
    Permission to only allow active users.
    """

    message = 'Account is not active'

    def has_permission(self, request, view):
        """
        Check if user account is active.
        """
        return request.user and request.user.is_active


class IsPremiumUser(permissions.BasePermission):
    """
    Permission to only allow premium/subscribed users.
    """

    message = 'Premium subscription required'

    def has_permission(self, request, view):
        """
        Check if user has premium subscription.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has active subscription
        if hasattr(request.user, 'subscription'):
            subscription = request.user.subscription
            return (
                subscription.is_active and
                subscription.end_date and
                subscription.end_date > timezone.now().date()
            )

        return False


class HasAPIKey(permissions.BasePermission):
    """
    Permission to require valid API key.
    """

    message = 'Valid API key required'

    def has_permission(self, request, view):
        """
        Check if request has valid API key.
        """
        from django.conf import settings

        api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')

        if not api_key:
            return False

        # TODO: Implement proper API key validation
        # This should check against stored API keys in database
        return api_key == settings.API_KEY


class ReadOnly(permissions.BasePermission):
    """
    Permission to only allow read-only (GET, HEAD, OPTIONS) requests.
    """

    def has_permission(self, request, view):
        """
        Allow only safe methods.
        """
        return request.method in permissions.SAFE_METHODS


class IsBookingOwner(permissions.BasePermission):
    """
    Permission to only allow booking owners to access booking details.
    """

    message = 'You do not have permission to access this booking'

    def has_object_permission(self, request, view, obj):
        """
        Check if request user owns the booking.
        """
        return obj.user == request.user or request.user.is_staff


class CanModifyBooking(permissions.BasePermission):
    """
    Permission to only allow booking modifications before departure.
    """

    message = 'Booking cannot be modified after departure'

    def has_object_permission(self, request, view, obj):
        """
        Check if booking can be modified.
        """
        # Allow staff to always modify
        if request.user.is_staff:
            return True

        # Check if user owns booking
        if obj.user != request.user:
            return False

        # Check if departure time has passed
        if hasattr(obj, 'departure_time') and obj.departure_time:
            return obj.departure_time > timezone.now()

        return True


class CanCancelBooking(permissions.BasePermission):
    """
    Permission to check if booking can be cancelled.
    """

    message = 'Booking cannot be cancelled'

    def has_object_permission(self, request, view, obj):
        """
        Check if booking can be cancelled based on cancellation policy.
        """
        # Allow staff to always cancel
        if request.user.is_staff:
            return True

        # Check if user owns booking
        if obj.user != request.user:
            return False

        # Check booking status
        if obj.status in ['cancelled', 'completed']:
            return False

        # Check cancellation deadline
        if hasattr(obj, 'departure_time') and obj.departure_time:
            hours_until_departure = (obj.departure_time - timezone.now()).total_seconds() / 3600

            # Example: Allow cancellation up to 24 hours before departure
            return hours_until_departure > 24

        return True


class IsPaymentOwner(permissions.BasePermission):
    """
    Permission to only allow payment owners to access payment details.
    """

    message = 'You do not have permission to access this payment'

    def has_object_permission(self, request, view, obj):
        """
        Check if request user owns the payment.
        """
        return obj.user == request.user or request.user.is_staff


class IsItineraryOwner(permissions.BasePermission):
    """
    Permission to only allow itinerary owners to access itinerary.
    """

    message = 'You do not have permission to access this itinerary'

    def has_object_permission(self, request, view, obj):
        """
        Check if request user owns the itinerary.
        """
        return obj.user == request.user


class CanShareItinerary(permissions.BasePermission):
    """
    Permission to check if user can share itinerary.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user can share the itinerary.
        """
        # Owner can always share
        if obj.user == request.user:
            return True

        # Check if itinerary is already shared with user
        if hasattr(obj, 'shared_with'):
            return request.user in obj.shared_with.all()

        return False


class IsReviewAuthor(permissions.BasePermission):
    """
    Permission to only allow review authors to modify their reviews.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if request user is the review author.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user or request.user.is_staff


class CanWriteReview(permissions.BasePermission):
    """
    Permission to check if user can write a review.
    """

    message = 'You must have a completed booking to write a review'

    def has_permission(self, request, view):
        """
        Check if user has completed bookings.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if this is a create action
        if request.method != 'POST':
            return True

        # Verify user has completed booking for the item
        # This should be checked in the view with the specific booking ID
        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if user can review this object.
        """
        # Allow reading any review
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only author can modify
        return obj.user == request.user


class RateLimitPermission(permissions.BasePermission):
    """
    Permission to enforce rate limiting.
    """

    message = 'Rate limit exceeded'

    def __init__(self, rate=10, period=60):
        """
        Initialize with rate limit parameters.

        Args:
            rate: Number of requests allowed
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period

    def has_permission(self, request, view):
        """
        Check if rate limit is exceeded.
        """
        from django.core.cache import cache
        from utils.helpers import get_client_ip

        # Get identifier (user ID or IP)
        if request.user.is_authenticated:
            identifier = f"user_{request.user.id}"
        else:
            identifier = f"ip_{get_client_ip(request)}"

        # Build cache key
        cache_key = f"rate_limit:{view.__class__.__name__}:{identifier}"

        # Get current count
        current_count = cache.get(cache_key, 0)

        if current_count >= self.rate:
            return False

        # Increment counter
        cache.set(cache_key, current_count + 1, self.period)

        return True


class IsInBusinessHours(permissions.BasePermission):
    """
    Permission to only allow access during business hours.
    """

    message = 'Service is only available during business hours (9 AM - 6 PM)'

    def has_permission(self, request, view):
        """
        Check if current time is within business hours.
        """
        # Allow staff to bypass this restriction
        if request.user and request.user.is_staff:
            return True

        now = timezone.now()
        current_hour = now.hour

        # Business hours: 9 AM to 6 PM
        return 9 <= current_hour < 18


class HasCompletedProfile(permissions.BasePermission):
    """
    Permission to require completed user profile.
    """

    message = 'Please complete your profile to access this resource'

    def has_permission(self, request, view):
        """
        Check if user has completed their profile.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Check required profile fields
        required_fields = ['first_name', 'last_name', 'phone', 'date_of_birth']

        for field in required_fields:
            if not getattr(request.user, field, None):
                return False

        return True


class IsNotBlocked(permissions.BasePermission):
    """
    Permission to check if user is not blocked.
    """

    message = 'Your account has been blocked'

    def has_permission(self, request, view):
        """
        Check if user is not blocked.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        return not getattr(request.user, 'is_blocked', False)


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    """
    Extended Django model permissions that also requires authentication for read access.
    """

    # Add GET, HEAD, OPTIONS to require permissions
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow access to owners or admin users.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user is owner or admin.
        """
        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj.user == request.user
