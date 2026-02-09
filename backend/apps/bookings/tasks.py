"""
Celery tasks for booking operations.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_booking_reminders(self):
    """
    Send reminders to users about upcoming bookings.
    Sends reminders 24 hours before departure.
    """
    try:
        from .models import Booking
        from apps.notifications.models import Notification

        logger.info("Starting booking reminder check")

        # Get bookings departing in 24 hours
        reminder_time = timezone.now() + timedelta(hours=24)
        time_window_start = reminder_time - timedelta(minutes=30)
        time_window_end = reminder_time + timedelta(minutes=30)

        bookings = Booking.objects.filter(
            status='confirmed',
            departure_time__gte=time_window_start,
            departure_time__lte=time_window_end,
            reminder_sent=False
        ).select_related('user', 'flight')

        reminders_sent = 0

        for booking in bookings:
            try:
                # Create notification
                Notification.objects.create(
                    user=booking.user,
                    notification_type='booking_reminder',
                    title='Upcoming Flight Reminder',
                    message=f'Your flight {booking.flight.flight_number} departs in 24 hours!',
                    data={
                        'booking_id': booking.id,
                        'flight_number': booking.flight.flight_number,
                        'departure_time': booking.departure_time.isoformat(),
                        'destination': booking.destination
                    }
                )

                # Send email reminder
                if booking.user.email:
                    context = {
                        'user': booking.user,
                        'booking': booking,
                        'flight': booking.flight,
                    }

                    html_message = render_to_string('emails/booking_reminder.html', context)

                    send_mail(
                        subject=f'Reminder: Your flight to {booking.destination} departs tomorrow',
                        message=f'Your flight {booking.flight.flight_number} departs in 24 hours. Please check in online.',
                        html_message=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[booking.user.email],
                        fail_silently=True
                    )

                # Mark reminder as sent
                booking.reminder_sent = True
                booking.save(update_fields=['reminder_sent'])

                reminders_sent += 1
                logger.info(f"Reminder sent for booking {booking.id}")

            except Exception as e:
                logger.error(f"Error sending reminder for booking {booking.id}: {str(e)}")
                continue

        logger.info(f"Booking reminder task completed. {reminders_sent} reminders sent.")

        return {
            'status': 'success',
            'reminders_sent': reminders_sent
        }

    except Exception as exc:
        logger.error(f"Error in send_booking_reminders task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_booking_confirmation(self, booking_id):
    """
    Process booking confirmation and send confirmation email.

    Args:
        booking_id: ID of the booking to confirm
    """
    try:
        from .models import Booking
        from apps.notifications.models import Notification
        from apps.payments.models import Payment

        logger.info(f"Processing confirmation for booking {booking_id}")

        try:
            booking = Booking.objects.select_related('user', 'flight').get(id=booking_id)
        except Booking.DoesNotExist:
            logger.error(f"Booking {booking_id} not found")
            return {'status': 'error', 'message': 'Booking not found'}

        # Verify payment is completed
        payment = Payment.objects.filter(
            booking=booking,
            status='completed'
        ).first()

        if not payment:
            logger.warning(f"No completed payment found for booking {booking_id}")
            # Retry later in case payment is processing
            raise self.retry(countdown=60)

        # Update booking status
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.confirmation_code = booking.generate_confirmation_code()
        booking.save()

        # Create notification
        Notification.objects.create(
            user=booking.user,
            notification_type='booking_confirmed',
            title='Booking Confirmed!',
            message=f'Your booking for {booking.flight.flight_number} is confirmed.',
            data={
                'booking_id': booking.id,
                'confirmation_code': booking.confirmation_code,
                'flight_number': booking.flight.flight_number
            }
        )

        # Send confirmation email
        if booking.user.email:
            context = {
                'user': booking.user,
                'booking': booking,
                'flight': booking.flight,
                'payment': payment,
            }

            html_message = render_to_string('emails/booking_confirmation.html', context)

            send_mail(
                subject=f'Booking Confirmed - {booking.confirmation_code}',
                message=f'Your booking is confirmed! Confirmation code: {booking.confirmation_code}',
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                fail_silently=False
            )

        logger.info(f"Booking {booking_id} confirmed successfully")

        return {
            'status': 'success',
            'booking_id': booking_id,
            'confirmation_code': booking.confirmation_code
        }

    except Exception as exc:
        logger.error(f"Error in process_booking_confirmation task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def cancel_expired_bookings(self):
    """
    Cancel bookings that were not paid within the time limit.
    """
    try:
        from .models import Booking

        logger.info("Checking for expired bookings")

        # Find pending bookings older than 30 minutes
        expiry_time = timezone.now() - timedelta(minutes=30)
        expired_bookings = Booking.objects.filter(
            status='pending',
            created_at__lt=expiry_time
        )

        cancelled_count = 0

        for booking in expired_bookings:
            try:
                booking.status = 'cancelled'
                booking.cancellation_reason = 'Payment timeout'
                booking.cancelled_at = timezone.now()
                booking.save()

                # Release reserved seats/inventory
                if hasattr(booking, 'release_inventory'):
                    booking.release_inventory()

                cancelled_count += 1
                logger.info(f"Cancelled expired booking {booking.id}")

            except Exception as e:
                logger.error(f"Error cancelling booking {booking.id}: {str(e)}")
                continue

        logger.info(f"Expired bookings check completed. {cancelled_count} bookings cancelled.")

        return {
            'status': 'success',
            'cancelled_count': cancelled_count
        }

    except Exception as exc:
        logger.error(f"Error in cancel_expired_bookings task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def generate_booking_report(self, start_date, end_date, user_id=None):
    """
    Generate booking report for specified date range.

    Args:
        start_date: Start date for report (ISO format string)
        end_date: End date for report (ISO format string)
        user_id: Optional user ID to filter bookings
    """
    try:
        from .models import Booking
        from django.db.models import Count, Sum, Avg
        from datetime import datetime

        logger.info(f"Generating booking report from {start_date} to {end_date}")

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        queryset = Booking.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        )

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        report = queryset.aggregate(
            total_bookings=Count('id'),
            confirmed_bookings=Count('id', filter=models.Q(status='confirmed')),
            cancelled_bookings=Count('id', filter=models.Q(status='cancelled')),
            total_revenue=Sum('total_price'),
            average_booking_value=Avg('total_price')
        )

        logger.info(f"Booking report generated successfully")

        return {
            'status': 'success',
            'report': report,
            'start_date': start_date,
            'end_date': end_date
        }

    except Exception as exc:
        logger.error(f"Error in generate_booking_report task: {str(exc)}")
        raise self.retry(exc=exc)
