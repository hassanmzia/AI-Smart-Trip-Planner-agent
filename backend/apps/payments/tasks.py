"""
Celery tasks for payment operations.
"""
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_payment(self, payment_id):
    """
    Process a payment transaction with payment gateway.

    Args:
        payment_id: ID of the payment to process
    """
    try:
        from .models import Payment, PaymentTransaction
        from apps.bookings.tasks import process_booking_confirmation

        logger.info(f"Processing payment {payment_id}")

        try:
            payment = Payment.objects.select_related('booking', 'user').get(id=payment_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return {'status': 'error', 'message': 'Payment not found'}

        # Check if already processed
        if payment.status in ['completed', 'failed']:
            logger.warning(f"Payment {payment_id} already processed with status: {payment.status}")
            return {
                'status': 'already_processed',
                'payment_status': payment.status
            }

        # Update status to processing
        payment.status = 'processing'
        payment.save(update_fields=['status'])

        # Create transaction record
        transaction = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='charge',
            amount=payment.amount,
            currency=payment.currency,
            status='pending'
        )

        try:
            # Process payment with payment gateway (e.g., Stripe)
            from apps.agents.integrations.stripe_client import StripeClient

            stripe_client = StripeClient()

            result = stripe_client.charge(
                amount=int(payment.amount * 100),  # Convert to cents
                currency=payment.currency.lower(),
                customer_id=payment.stripe_customer_id,
                payment_method_id=payment.payment_method_id,
                description=f'Booking {payment.booking.id}',
                metadata={
                    'payment_id': str(payment.id),
                    'booking_id': str(payment.booking.id),
                    'user_id': str(payment.user.id)
                }
            )

            if result['status'] == 'succeeded':
                # Payment successful
                payment.status = 'completed'
                payment.transaction_id = result['transaction_id']
                payment.completed_at = timezone.now()
                payment.save()

                transaction.status = 'completed'
                transaction.transaction_id = result['transaction_id']
                transaction.gateway_response = result
                transaction.completed_at = timezone.now()
                transaction.save()

                logger.info(f"Payment {payment_id} completed successfully")

                # Trigger booking confirmation
                process_booking_confirmation.delay(payment.booking.id)

                return {
                    'status': 'success',
                    'payment_id': payment_id,
                    'transaction_id': result['transaction_id']
                }

            else:
                # Payment failed
                payment.status = 'failed'
                payment.failure_reason = result.get('error_message', 'Payment declined')
                payment.save()

                transaction.status = 'failed'
                transaction.error_message = result.get('error_message')
                transaction.gateway_response = result
                transaction.save()

                logger.warning(f"Payment {payment_id} failed: {result.get('error_message')}")

                return {
                    'status': 'failed',
                    'payment_id': payment_id,
                    'error': result.get('error_message')
                }

        except Exception as e:
            # Payment processing error
            payment.status = 'failed'
            payment.failure_reason = str(e)
            payment.save()

            transaction.status = 'failed'
            transaction.error_message = str(e)
            transaction.save()

            logger.error(f"Error processing payment {payment_id}: {str(e)}")
            raise

    except Exception as exc:
        logger.error(f"Error in process_payment task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=5, default_retry_delay=120)
def process_refund(self, payment_id, amount=None, reason=None):
    """
    Process a refund for a payment.

    Args:
        payment_id: ID of the payment to refund
        amount: Optional partial refund amount. If None, full refund.
        reason: Reason for refund
    """
    try:
        from .models import Payment, PaymentTransaction
        from apps.notifications.models import Notification

        logger.info(f"Processing refund for payment {payment_id}, amount: {amount}")

        try:
            payment = Payment.objects.select_related('booking', 'user').get(id=payment_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment {payment_id} not found")
            return {'status': 'error', 'message': 'Payment not found'}

        # Verify payment is completed
        if payment.status != 'completed':
            logger.error(f"Cannot refund payment {payment_id} with status: {payment.status}")
            return {
                'status': 'error',
                'message': f'Cannot refund payment with status: {payment.status}'
            }

        # Calculate refund amount
        refund_amount = Decimal(str(amount)) if amount else payment.amount

        if refund_amount > payment.amount:
            logger.error(f"Refund amount {refund_amount} exceeds payment amount {payment.amount}")
            return {
                'status': 'error',
                'message': 'Refund amount exceeds payment amount'
            }

        # Create refund transaction
        transaction = PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='refund',
            amount=refund_amount,
            currency=payment.currency,
            status='pending',
            notes=reason
        )

        try:
            # Process refund with payment gateway
            from apps.agents.integrations.stripe_client import StripeClient

            stripe_client = StripeClient()

            result = stripe_client.refund(
                charge_id=payment.transaction_id,
                amount=int(refund_amount * 100),  # Convert to cents
                reason=reason or 'requested_by_customer',
                metadata={
                    'payment_id': str(payment.id),
                    'booking_id': str(payment.booking.id)
                }
            )

            if result['status'] == 'succeeded':
                # Refund successful
                payment.refunded_amount = (payment.refunded_amount or Decimal('0')) + refund_amount

                if payment.refunded_amount >= payment.amount:
                    payment.status = 'refunded'
                else:
                    payment.status = 'partially_refunded'

                payment.save()

                transaction.status = 'completed'
                transaction.transaction_id = result['refund_id']
                transaction.gateway_response = result
                transaction.completed_at = timezone.now()
                transaction.save()

                # Notify user
                Notification.objects.create(
                    user=payment.user,
                    notification_type='refund_processed',
                    title='Refund Processed',
                    message=f'Your refund of ${refund_amount} has been processed.',
                    data={
                        'payment_id': payment.id,
                        'refund_amount': float(refund_amount),
                        'refund_id': result['refund_id']
                    }
                )

                logger.info(f"Refund processed successfully for payment {payment_id}")

                return {
                    'status': 'success',
                    'payment_id': payment_id,
                    'refund_amount': float(refund_amount),
                    'refund_id': result['refund_id']
                }

            else:
                # Refund failed
                transaction.status = 'failed'
                transaction.error_message = result.get('error_message')
                transaction.gateway_response = result
                transaction.save()

                logger.error(f"Refund failed for payment {payment_id}: {result.get('error_message')}")

                return {
                    'status': 'failed',
                    'payment_id': payment_id,
                    'error': result.get('error_message')
                }

        except Exception as e:
            transaction.status = 'failed'
            transaction.error_message = str(e)
            transaction.save()

            logger.error(f"Error processing refund for payment {payment_id}: {str(e)}")
            raise

    except Exception as exc:
        logger.error(f"Error in process_refund task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def reconcile_payments(self, date=None):
    """
    Reconcile payment records with payment gateway.

    Args:
        date: Date to reconcile (ISO format). Defaults to yesterday.
    """
    try:
        from .models import Payment
        from datetime import datetime, timedelta

        if date:
            reconcile_date = datetime.fromisoformat(date)
        else:
            reconcile_date = (timezone.now() - timedelta(days=1)).date()

        logger.info(f"Reconciling payments for date: {reconcile_date}")

        # Get all payments for the date
        payments = Payment.objects.filter(
            completed_at__date=reconcile_date,
            status='completed'
        )

        discrepancies = []
        reconciled_count = 0

        for payment in payments:
            try:
                # Verify with payment gateway
                from apps.agents.integrations.stripe_client import StripeClient

                stripe_client = StripeClient()
                gateway_transaction = stripe_client.get_charge(payment.transaction_id)

                # Compare amounts
                gateway_amount = Decimal(str(gateway_transaction['amount'])) / 100

                if gateway_amount != payment.amount:
                    discrepancies.append({
                        'payment_id': payment.id,
                        'local_amount': float(payment.amount),
                        'gateway_amount': float(gateway_amount)
                    })
                    logger.warning(f"Amount discrepancy for payment {payment.id}")

                reconciled_count += 1

            except Exception as e:
                logger.error(f"Error reconciling payment {payment.id}: {str(e)}")
                continue

        logger.info(f"Reconciliation completed. {reconciled_count} payments reconciled, {len(discrepancies)} discrepancies found.")

        return {
            'status': 'success',
            'date': str(reconcile_date),
            'reconciled_count': reconciled_count,
            'discrepancies': discrepancies
        }

    except Exception as exc:
        logger.error(f"Error in reconcile_payments task: {str(exc)}")
        raise self.retry(exc=exc)
