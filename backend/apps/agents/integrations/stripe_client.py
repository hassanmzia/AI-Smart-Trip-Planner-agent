"""
Stripe payment integration client.
"""
import logging
import stripe
from typing import Dict, Any, Optional
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)


class StripeClient:
    """
    Client for interacting with Stripe payment API.
    """

    def __init__(self):
        """
        Initialize Stripe client with API key.
        """
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        self.api_version = getattr(settings, 'STRIPE_API_VERSION', '2023-10-16')

    def create_customer(self, email: str, name: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a new Stripe customer.

        Args:
            email: Customer email address
            name: Customer name
            metadata: Optional metadata dictionary

        Returns:
            Customer object data
        """
        try:
            logger.info(f"Creating Stripe customer for email: {email}")

            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )

            logger.info(f"Stripe customer created: {customer.id}")

            return {
                'status': 'success',
                'customer_id': customer.id,
                'email': customer.email,
                'name': customer.name,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve customer information.

        Args:
            customer_id: Stripe customer ID

        Returns:
            Customer data or None
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)

            return {
                'id': customer.id,
                'email': customer.email,
                'name': customer.name,
                'created': customer.created,
                'metadata': customer.metadata,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving customer {customer_id}: {str(e)}")
            return None

    def create_payment_method(self, customer_id: str, card_token: str) -> Dict[str, Any]:
        """
        Create a payment method for a customer.

        Args:
            customer_id: Stripe customer ID
            card_token: Card token from Stripe.js

        Returns:
            Payment method data
        """
        try:
            payment_method = stripe.PaymentMethod.create(
                type='card',
                card={'token': card_token}
            )

            # Attach to customer
            stripe.PaymentMethod.attach(
                payment_method.id,
                customer=customer_id
            )

            logger.info(f"Payment method created and attached to customer {customer_id}")

            return {
                'status': 'success',
                'payment_method_id': payment_method.id,
                'card_last4': payment_method.card.last4,
                'card_brand': payment_method.card.brand,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating payment method: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def charge(self, amount: int, currency: str, customer_id: str = None,
               payment_method_id: str = None, description: str = None,
               metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a payment charge.

        Args:
            amount: Amount in cents (e.g., 1000 = $10.00)
            currency: Currency code (e.g., 'usd')
            customer_id: Stripe customer ID
            payment_method_id: Payment method ID
            description: Charge description
            metadata: Optional metadata

        Returns:
            Charge result data
        """
        try:
            logger.info(f"Creating charge for ${amount/100:.2f} {currency.upper()}")

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                payment_method=payment_method_id,
                description=description,
                metadata=metadata or {},
                confirm=True,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                }
            )

            if intent.status == 'succeeded':
                logger.info(f"Charge successful: {intent.id}")

                return {
                    'status': 'succeeded',
                    'transaction_id': intent.id,
                    'amount': intent.amount,
                    'currency': intent.currency,
                    'created': intent.created,
                }
            else:
                logger.warning(f"Charge not completed: {intent.status}")

                return {
                    'status': intent.status,
                    'transaction_id': intent.id,
                    'error_message': intent.last_payment_error.message if intent.last_payment_error else 'Payment not completed'
                }

        except stripe.error.CardError as e:
            # Card was declined
            logger.warning(f"Card declined: {str(e)}")
            return {
                'status': 'failed',
                'error_message': str(e.user_message),
                'error_code': e.code
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error during charge: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def refund(self, charge_id: str, amount: int = None, reason: str = None,
               metadata: Dict = None) -> Dict[str, Any]:
        """
        Refund a charge.

        Args:
            charge_id: Stripe charge/payment intent ID
            amount: Amount to refund in cents (None = full refund)
            reason: Refund reason
            metadata: Optional metadata

        Returns:
            Refund result data
        """
        try:
            logger.info(f"Creating refund for charge {charge_id}")

            refund_params = {
                'payment_intent': charge_id,
                'metadata': metadata or {}
            }

            if amount:
                refund_params['amount'] = amount

            if reason:
                refund_params['reason'] = reason

            refund = stripe.Refund.create(**refund_params)

            if refund.status == 'succeeded':
                logger.info(f"Refund successful: {refund.id}")

                return {
                    'status': 'succeeded',
                    'refund_id': refund.id,
                    'amount': refund.amount,
                    'currency': refund.currency,
                }
            else:
                return {
                    'status': refund.status,
                    'refund_id': refund.id,
                    'error_message': 'Refund not completed'
                }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating refund: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def get_charge(self, charge_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve charge information.

        Args:
            charge_id: Stripe charge/payment intent ID

        Returns:
            Charge data or None
        """
        try:
            intent = stripe.PaymentIntent.retrieve(charge_id)

            return {
                'id': intent.id,
                'amount': intent.amount,
                'currency': intent.currency,
                'status': intent.status,
                'created': intent.created,
                'description': intent.description,
                'metadata': intent.metadata,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving charge {charge_id}: {str(e)}")
            return None

    def create_subscription(self, customer_id: str, price_id: str,
                           trial_days: int = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a subscription for a customer.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Optional trial period in days
            metadata: Optional metadata

        Returns:
            Subscription data
        """
        try:
            logger.info(f"Creating subscription for customer {customer_id}")

            params = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'metadata': metadata or {}
            }

            if trial_days:
                params['trial_period_days'] = trial_days

            subscription = stripe.Subscription.create(**params)

            logger.info(f"Subscription created: {subscription.id}")

            return {
                'status': 'success',
                'subscription_id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def cancel_subscription(self, subscription_id: str, immediately: bool = False) -> Dict[str, Any]:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            immediately: If True, cancel immediately; otherwise at period end

        Returns:
            Cancellation result
        """
        try:
            logger.info(f"Cancelling subscription {subscription_id}")

            if immediately:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )

            logger.info(f"Subscription cancelled: {subscription_id}")

            return {
                'status': 'success',
                'subscription_id': subscription.id,
                'status': subscription.status,
                'cancelled_at': subscription.canceled_at if immediately else None,
                'cancel_at_period_end': subscription.cancel_at_period_end,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def create_webhook_endpoint(self, url: str, events: list) -> Dict[str, Any]:
        """
        Create a webhook endpoint.

        Args:
            url: Webhook URL
            events: List of event types to subscribe to

        Returns:
            Webhook endpoint data
        """
        try:
            endpoint = stripe.WebhookEndpoint.create(
                url=url,
                enabled_events=events
            )

            logger.info(f"Webhook endpoint created: {endpoint.id}")

            return {
                'status': 'success',
                'endpoint_id': endpoint.id,
                'secret': endpoint.secret,
                'url': endpoint.url,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating webhook endpoint: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }

    def verify_webhook_signature(self, payload: bytes, signature: str, webhook_secret: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Raw request body
            signature: Stripe signature header
            webhook_secret: Webhook secret from Stripe

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return True

        except ValueError:
            logger.error("Invalid payload")
            return False

        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            return False

    def list_payment_methods(self, customer_id: str) -> list:
        """
        List all payment methods for a customer.

        Args:
            customer_id: Stripe customer ID

        Returns:
            List of payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )

            return [
                {
                    'id': pm.id,
                    'brand': pm.card.brand,
                    'last4': pm.card.last4,
                    'exp_month': pm.card.exp_month,
                    'exp_year': pm.card.exp_year,
                }
                for pm in payment_methods.data
            ]

        except stripe.error.StripeError as e:
            logger.error(f"Error listing payment methods: {str(e)}")
            return []

    def detach_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """
        Detach a payment method from a customer.

        Args:
            payment_method_id: Payment method ID

        Returns:
            Result data
        """
        try:
            stripe.PaymentMethod.detach(payment_method_id)

            logger.info(f"Payment method detached: {payment_method_id}")

            return {
                'status': 'success',
                'payment_method_id': payment_method_id
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error detaching payment method: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
