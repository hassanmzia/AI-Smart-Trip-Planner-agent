import api, { handleApiResponse } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import type { PriceAlert, FlightSearchParams, HotelSearchParams } from '@/types';

/**
 * Create price alert
 */
export const createPriceAlert = async (alert: {
  type: 'flight' | 'hotel';
  searchParams: FlightSearchParams | HotelSearchParams;
  targetPrice: number;
  expiresAt?: string;
}): Promise<PriceAlert> => {
  const response = await api.post(API_ENDPOINTS.PRICE_ALERTS.CREATE, alert);
  return handleApiResponse(response);
};

/**
 * Get all price alerts
 */
export const getPriceAlerts = async (status?: string): Promise<PriceAlert[]> => {
  let url = API_ENDPOINTS.PRICE_ALERTS.LIST;
  if (status) {
    url += `?status=${status}`;
  }
  const response = await api.get(url);
  return handleApiResponse(response);
};

/**
 * Get price alert by ID
 */
export const getPriceAlert = async (alertId: string): Promise<PriceAlert> => {
  const response = await api.get(`${API_ENDPOINTS.PRICE_ALERTS.LIST}/${alertId}`);
  return handleApiResponse(response);
};

/**
 * Update price alert
 */
export const updatePriceAlert = async (
  alertId: string,
  data: Partial<PriceAlert>
): Promise<PriceAlert> => {
  const response = await api.put(`${API_ENDPOINTS.PRICE_ALERTS.LIST}/${alertId}`, data);
  return handleApiResponse(response);
};

/**
 * Delete price alert
 */
export const deletePriceAlert = async (alertId: string): Promise<void> => {
  const response = await api.delete(`${API_ENDPOINTS.PRICE_ALERTS.DELETE}/${alertId}`);
  return handleApiResponse(response);
};

/**
 * Pause price alert
 */
export const pausePriceAlert = async (alertId: string): Promise<PriceAlert> => {
  const response = await api.post(
    `${API_ENDPOINTS.PRICE_ALERTS.LIST}/${alertId}/pause`
  );
  return handleApiResponse(response);
};

/**
 * Resume price alert
 */
export const resumePriceAlert = async (alertId: string): Promise<PriceAlert> => {
  const response = await api.post(
    `${API_ENDPOINTS.PRICE_ALERTS.LIST}/${alertId}/resume`
  );
  return handleApiResponse(response);
};
