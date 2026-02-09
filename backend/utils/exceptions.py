"""
Custom exception classes for the application.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class BaseAPIException(APIException):
    """
    Base exception class for API errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred'
    default_code = 'error'


class ValidationError(BaseAPIException):
    """
    Exception raised when data validation fails.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error'
    default_code = 'validation_error'


class AuthenticationError(BaseAPIException):
    """
    Exception raised for authentication failures.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed'
    default_code = 'authentication_error'


class PermissionDeniedError(BaseAPIException):
    """
    Exception raised when user lacks required permissions.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied'
    default_code = 'permission_denied'


class NotFoundError(BaseAPIException):
    """
    Exception raised when a resource is not found.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'not_found'


class ConflictError(BaseAPIException):
    """
    Exception raised when there's a conflict with existing data.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict'
    default_code = 'conflict'


class RateLimitExceededError(BaseAPIException):
    """
    Exception raised when rate limit is exceeded.
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded'
    default_code = 'rate_limit_exceeded'


class ServiceUnavailableError(BaseAPIException):
    """
    Exception raised when an external service is unavailable.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable'
    default_code = 'service_unavailable'


class PaymentError(BaseAPIException):
    """
    Exception raised for payment processing errors.
    """
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed'
    default_code = 'payment_error'


class InsufficientFundsError(PaymentError):
    """
    Exception raised when payment fails due to insufficient funds.
    """
    default_detail = 'Insufficient funds'
    default_code = 'insufficient_funds'


class PaymentMethodError(PaymentError):
    """
    Exception raised when payment method is invalid or declined.
    """
    default_detail = 'Invalid or declined payment method'
    default_code = 'payment_method_error'


class BookingError(BaseAPIException):
    """
    Base exception for booking-related errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Booking error'
    default_code = 'booking_error'


class BookingUnavailableError(BookingError):
    """
    Exception raised when booking is no longer available.
    """
    default_detail = 'Booking no longer available'
    default_code = 'booking_unavailable'


class BookingCancelledError(BookingError):
    """
    Exception raised when trying to operate on a cancelled booking.
    """
    default_detail = 'Booking has been cancelled'
    default_code = 'booking_cancelled'


class BookingExpiredError(BookingError):
    """
    Exception raised when booking has expired.
    """
    default_detail = 'Booking has expired'
    default_code = 'booking_expired'


class FlightError(BaseAPIException):
    """
    Base exception for flight-related errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Flight error'
    default_code = 'flight_error'


class FlightNotFoundError(NotFoundError):
    """
    Exception raised when flight is not found.
    """
    default_detail = 'Flight not found'
    default_code = 'flight_not_found'


class FlightFullyBookedError(FlightError):
    """
    Exception raised when flight is fully booked.
    """
    default_detail = 'Flight is fully booked'
    default_code = 'flight_fully_booked'


class FlightCancelledError(FlightError):
    """
    Exception raised when flight has been cancelled.
    """
    default_detail = 'Flight has been cancelled'
    default_code = 'flight_cancelled'


class InvalidDateRangeError(ValidationError):
    """
    Exception raised when date range is invalid.
    """
    default_detail = 'Invalid date range'
    default_code = 'invalid_date_range'


class InvalidSearchParametersError(ValidationError):
    """
    Exception raised when search parameters are invalid.
    """
    default_detail = 'Invalid search parameters'
    default_code = 'invalid_search_parameters'


class ExternalAPIError(ServiceUnavailableError):
    """
    Exception raised when external API call fails.
    """
    default_detail = 'External API error'
    default_code = 'external_api_error'


class WeatherAPIError(ExternalAPIError):
    """
    Exception raised when weather API fails.
    """
    default_detail = 'Weather service unavailable'
    default_code = 'weather_api_error'


class PaymentGatewayError(ExternalAPIError):
    """
    Exception raised when payment gateway fails.
    """
    default_detail = 'Payment gateway error'
    default_code = 'payment_gateway_error'


class AIAgentError(BaseAPIException):
    """
    Base exception for AI agent errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'AI agent error'
    default_code = 'ai_agent_error'


class AIModelError(AIAgentError):
    """
    Exception raised when AI model fails.
    """
    default_detail = 'AI model error'
    default_code = 'ai_model_error'


class AIResponseError(AIAgentError):
    """
    Exception raised when AI response is invalid or cannot be parsed.
    """
    default_detail = 'Invalid AI response'
    default_code = 'ai_response_error'


class ItineraryError(BaseAPIException):
    """
    Base exception for itinerary errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Itinerary error'
    default_code = 'itinerary_error'


class ItineraryGenerationError(ItineraryError):
    """
    Exception raised when itinerary generation fails.
    """
    default_detail = 'Failed to generate itinerary'
    default_code = 'itinerary_generation_error'


class InvalidItineraryError(ItineraryError):
    """
    Exception raised when itinerary data is invalid.
    """
    default_detail = 'Invalid itinerary data'
    default_code = 'invalid_itinerary'


class EmailVerificationError(BaseAPIException):
    """
    Exception raised for email verification errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Email verification error'
    default_code = 'email_verification_error'


class EmailAlreadyVerifiedError(EmailVerificationError):
    """
    Exception raised when trying to verify already verified email.
    """
    default_detail = 'Email already verified'
    default_code = 'email_already_verified'


class InvalidVerificationTokenError(EmailVerificationError):
    """
    Exception raised when verification token is invalid.
    """
    default_detail = 'Invalid or expired verification token'
    default_code = 'invalid_verification_token'


class AccountLockedError(AuthenticationError):
    """
    Exception raised when account is locked.
    """
    default_detail = 'Account is locked'
    default_code = 'account_locked'


class AccountDisabledError(AuthenticationError):
    """
    Exception raised when account is disabled.
    """
    default_detail = 'Account is disabled'
    default_code = 'account_disabled'


class InvalidCredentialsError(AuthenticationError):
    """
    Exception raised when credentials are invalid.
    """
    default_detail = 'Invalid credentials'
    default_code = 'invalid_credentials'


class TokenExpiredError(AuthenticationError):
    """
    Exception raised when authentication token has expired.
    """
    default_detail = 'Token has expired'
    default_code = 'token_expired'


class InvalidTokenError(AuthenticationError):
    """
    Exception raised when authentication token is invalid.
    """
    default_detail = 'Invalid token'
    default_code = 'invalid_token'


class DuplicateError(ConflictError):
    """
    Exception raised when trying to create a duplicate resource.
    """
    default_detail = 'Resource already exists'
    default_code = 'duplicate'


class DataIntegrityError(BaseAPIException):
    """
    Exception raised for data integrity violations.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Data integrity error'
    default_code = 'data_integrity_error'


class FileUploadError(BaseAPIException):
    """
    Exception raised for file upload errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'File upload error'
    default_code = 'file_upload_error'


class FileTooLargeError(FileUploadError):
    """
    Exception raised when uploaded file is too large.
    """
    default_detail = 'File size exceeds maximum allowed'
    default_code = 'file_too_large'


class InvalidFileTypeError(FileUploadError):
    """
    Exception raised when file type is not allowed.
    """
    default_detail = 'File type not allowed'
    default_code = 'invalid_file_type'


class QuotaExceededError(BaseAPIException):
    """
    Exception raised when user quota is exceeded.
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Quota exceeded'
    default_code = 'quota_exceeded'


class MaintenanceModeError(ServiceUnavailableError):
    """
    Exception raised when system is in maintenance mode.
    """
    default_detail = 'System is currently under maintenance'
    default_code = 'maintenance_mode'


def handle_exception(exc):
    """
    Global exception handler for consistent error responses.

    Args:
        exc: Exception instance

    Returns:
        Dictionary with error details
    """
    if isinstance(exc, BaseAPIException):
        return {
            'error': exc.default_code,
            'detail': str(exc.detail),
            'status_code': exc.status_code
        }

    # Handle Django validation errors
    from django.core.exceptions import ValidationError as DjangoValidationError

    if isinstance(exc, DjangoValidationError):
        return {
            'error': 'validation_error',
            'detail': str(exc),
            'status_code': status.HTTP_400_BAD_REQUEST
        }

    # Handle generic exceptions
    import logging
    logger = logging.getLogger(__name__)
    logger.exception("Unhandled exception")

    return {
        'error': 'internal_error',
        'detail': 'An internal error occurred',
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
    }
