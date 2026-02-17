/**
 * Booking management service
 */

import api from './api';
import { ENDPOINTS } from '../utils/constants';
import type { Booking, PaginatedResponse } from '../types';

export const bookingService = {
  list: async (params?: { status?: string; page?: number }): Promise<PaginatedResponse<Booking>> => {
    const { data } = await api.get(ENDPOINTS.bookings.list, { params });
    return data;
  },

  getDetail: async (id: string | number): Promise<Booking> => {
    const { data } = await api.get(ENDPOINTS.bookings.detail(id));
    return data;
  },

  cancel: async (id: string | number): Promise<Booking> => {
    const { data } = await api.post(ENDPOINTS.bookings.cancel(id));
    return data;
  },
};
