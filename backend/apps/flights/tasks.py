"""
Celery tasks for flight operations.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def check_price_alerts(self):
    """
    Check for flight price changes and send alerts to users.
    Runs periodically to monitor price drops for tracked routes.
    """
    try:
        from .models import PriceAlert, Flight

        logger.info("Starting price alert check")

        # Get all active price alerts (status='active' and not expired)
        active_alerts = PriceAlert.objects.filter(
            status='active',
            expiry_date__gte=timezone.now().date(),
            user__is_active=True
        ).select_related('user')

        alerts_checked = 0
        alerts_triggered = 0

        for alert in active_alerts:
            try:
                alerts_checked += 1

                # Find the cheapest matching flight for this alert's route
                flight_qs = Flight.objects.filter(
                    origin_airport=alert.origin_airport,
                    destination_airport=alert.destination_airport,
                    departure_time__date=alert.departure_date,
                    travel_class=alert.travel_class,
                    status='scheduled',
                )
                if alert.preferred_airlines:
                    flight_qs = flight_qs.filter(
                        airline_code__in=alert.preferred_airlines
                    )
                cheapest_flight = flight_qs.order_by('base_price').first()

                if not cheapest_flight:
                    continue

                current_price = cheapest_flight.base_price

                # Update the alert's price tracking via the model method
                alert.check_price(current_price)

                # Check if the alert was triggered (status changed to 'triggered')
                if alert.status == 'triggered':
                    # Send in-app notification
                    from apps.notifications.models import Notification

                    Notification.objects.create(
                        user=alert.user,
                        notification_type='price_alert',
                        title=f'Price Alert: {alert.origin_airport} to {alert.destination_airport}',
                        message=f'Price dropped to ${current_price}! Your target was ${alert.target_price}.',
                        metadata={
                            'alert_id': alert.id,
                            'current_price': float(current_price),
                            'target_price': float(alert.target_price),
                            'origin': alert.origin_airport,
                            'destination': alert.destination_airport,
                        }
                    )

                    # Send email notification if enabled on the alert
                    if alert.email_notification:
                        send_mail(
                            subject=f'Price Alert: Flight from {alert.origin_airport} to {alert.destination_airport}',
                            message=f'Great news! The price for your tracked route has dropped to ${current_price}.',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[alert.user.email],
                            fail_silently=True
                        )

                    alerts_triggered += 1
                    logger.info(f"Price alert triggered for user {alert.user.id}, alert {alert.id}")

            except Exception as e:
                logger.error(f"Error processing price alert {alert.id}: {str(e)}")
                continue

        logger.info(f"Price alert check completed. {alerts_triggered} alerts triggered out of {alerts_checked} checked.")

        return {
            'status': 'success',
            'alerts_checked': alerts_checked,
            'alerts_triggered': alerts_triggered
        }

    except Exception as exc:
        logger.error(f"Error in check_price_alerts task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=5, default_retry_delay=180)
def update_flight_status(self, flight_id=None):
    """
    Update flight status from external API.
    Can update a specific flight or all active flights.

    Args:
        flight_id: Optional flight ID to update. If None, updates all active flights.
    """
    try:
        from .models import Flight
        from apps.notifications.models import Notification

        logger.info(f"Starting flight status update for flight_id: {flight_id or 'all'}")

        # Determine which flights to update
        if flight_id:
            flights = Flight.objects.filter(id=flight_id)
        else:
            # Update flights departing within next 48 hours
            cutoff_time = timezone.now() + timedelta(hours=48)
            flights = Flight.objects.filter(
                departure_time__lte=cutoff_time,
                departure_time__gte=timezone.now(),
                status__in=['scheduled', 'boarding', 'departed']
            )

        updated_count = 0
        status_changes = 0

        for flight in flights:
            try:
                old_status = flight.status

                # TODO: Integrate with real flight status API
                # For now, we'll use a placeholder
                # new_status = fetch_flight_status_from_api(flight.flight_number)

                # Simulate status update logic
                if flight.departure_time < timezone.now():
                    if old_status == 'scheduled':
                        flight.status = 'departed'
                    elif old_status == 'departed' and timezone.now() > flight.arrival_time:
                        flight.status = 'arrived'

                if old_status != flight.status:
                    flight.save()
                    status_changes += 1

                    # Notify users with bookings for this flight
                    from apps.bookings.models import Booking

                    bookings = Booking.objects.filter(
                        flight=flight,
                        status='confirmed'
                    ).select_related('user')

                    for booking in bookings:
                        Notification.objects.create(
                            user=booking.user,
                            notification_type='flight_status',
                            title=f'Flight Status Update: {flight.flight_number}',
                            message=f'Status changed from {old_status} to {flight.status}',
                            metadata={
                                'flight_id': flight.id,
                                'booking_id': booking.id,
                                'old_status': old_status,
                                'new_status': flight.status
                            }
                        )

                    logger.info(f"Flight {flight.id} status updated: {old_status} -> {flight.status}")

                updated_count += 1

            except Exception as e:
                logger.error(f"Error updating flight {flight.id}: {str(e)}")
                continue

        logger.info(f"Flight status update completed. {updated_count} flights checked, {status_changes} status changes.")

        return {
            'status': 'success',
            'flights_checked': updated_count,
            'status_changes': status_changes
        }

    except Exception as exc:
        logger.error(f"Error in update_flight_status task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def sync_flight_data(self, source='amadeus'):
    """
    Synchronize flight data from external providers.

    Args:
        source: Data source provider name (e.g., 'amadeus', 'skyscanner')
    """
    try:
        logger.info(f"Starting flight data sync from {source}")

        # TODO: Implement actual API integration
        # This would fetch and update flight schedules, prices, availability

        logger.info(f"Flight data sync from {source} completed successfully")

        return {
            'status': 'success',
            'source': source,
            'synced_at': timezone.now().isoformat()
        }

    except Exception as exc:
        logger.error(f"Error in sync_flight_data task: {str(exc)}")
        raise self.retry(exc=exc)
