from rest_framework import serializers
from .models import PaymentMethod, Payment, Transaction, Refund


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model."""
    method_type_display = serializers.CharField(source='get_method_type_display', read_only=True)
    card_type_display = serializers.CharField(source='get_card_type_display', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'method_type', 'method_type_display', 'is_default', 'is_active',
            'card_type', 'card_type_display', 'last_four_digits', 'expiry_month',
            'expiry_year', 'cardholder_name', 'billing_address', 'billing_city',
            'billing_country', 'billing_postal_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 'amount',
            'currency', 'description', 'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)
    payment_method_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'status', 'status_display', 'amount',
            'currency', 'refunded_amount', 'gateway_name', 'gateway_transaction_id',
            'payment_date', 'completed_at', 'payment_method_display',
            'transactions', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'payment_date', 'completed_at',
            'created_at', 'updated_at'
        ]

    def get_payment_method_display(self, obj):
        if obj.payment_method:
            return str(obj.payment_method)
        return None


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for Refund model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'refund_id', 'status', 'status_display', 'amount',
            'currency', 'reason', 'reason_display', 'reason_description',
            'processing_notes', 'requested_at', 'processed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'refund_id', 'status', 'requested_at', 'processed_at',
            'created_at', 'updated_at'
        ]
