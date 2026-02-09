import api, { handleApiResponse } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import type { PaymentIntent, PaymentMethod } from '@/types';

/**
 * Create payment intent
 */
export const createPaymentIntent = async (
  bookingId: string,
  amount: number,
  currency: string = 'USD'
): Promise<PaymentIntent> => {
  const response = await api.post(API_ENDPOINTS.PAYMENTS.CREATE_INTENT, {
    bookingId,
    amount,
    currency,
  });
  return handleApiResponse(response);
};

/**
 * Confirm payment
 */
export const confirmPayment = async (
  paymentIntentId: string,
  paymentMethodId: string
): Promise<{ success: boolean; bookingId: string }> => {
  const response = await api.post(API_ENDPOINTS.PAYMENTS.CONFIRM, {
    paymentIntentId,
    paymentMethodId,
  });
  return handleApiResponse(response);
};

/**
 * Get payment methods
 */
export const getPaymentMethods = async (): Promise<PaymentMethod[]> => {
  const response = await api.get(API_ENDPOINTS.PAYMENTS.METHODS);
  return handleApiResponse(response);
};

/**
 * Add payment method
 */
export const addPaymentMethod = async (
  paymentMethodData: Partial<PaymentMethod>
): Promise<PaymentMethod> => {
  const response = await api.post(API_ENDPOINTS.PAYMENTS.METHODS, paymentMethodData);
  return handleApiResponse(response);
};

/**
 * Delete payment method
 */
export const deletePaymentMethod = async (paymentMethodId: string): Promise<void> => {
  const response = await api.delete(`${API_ENDPOINTS.PAYMENTS.METHODS}/${paymentMethodId}`);
  return handleApiResponse(response);
};

/**
 * Set default payment method
 */
export const setDefaultPaymentMethod = async (
  paymentMethodId: string
): Promise<void> => {
  const response = await api.put(
    `${API_ENDPOINTS.PAYMENTS.METHODS}/${paymentMethodId}/default`
  );
  return handleApiResponse(response);
};

/**
 * Get payment history
 */
export const getPaymentHistory = async (
  page: number = 1,
  pageSize: number = 10
): Promise<{
  items: Array<{
    id: string;
    amount: number;
    currency: string;
    status: string;
    bookingId: string;
    createdAt: string;
  }>;
  total: number;
}> => {
  const response = await api.get(
    `/api/payments/history?page=${page}&pageSize=${pageSize}`
  );
  return handleApiResponse(response);
};

/**
 * Request refund
 */
export const requestRefund = async (
  paymentId: string,
  reason: string
): Promise<{ refundId: string; status: string }> => {
  const response = await api.post(`/api/payments/${paymentId}/refund`, { reason });
  return handleApiResponse(response);
};
