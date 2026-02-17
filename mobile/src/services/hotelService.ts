/**
 * Hotel search and booking service
 */

import api from './api';
import { ENDPOINTS } from '../utils/constants';
import type { Hotel, HotelSearchParams, PaginatedResponse } from '../types';

export const hotelService = {
  search: async (params: HotelSearchParams): Promise<PaginatedResponse<Hotel>> => {
    const { data } = await api.get(ENDPOINTS.hotels.search, { params });
    return data;
  },

  getDetail: async (id: string | number): Promise<Hotel> => {
    const { data } = await api.get(ENDPOINTS.hotels.detail(id));
    return data;
  },

  getReviews: async (id: string | number, page = 1) => {
    const { data } = await api.get(ENDPOINTS.hotels.reviews(id), { params: { page } });
    return data;
  },

  getRecommendations: async (params: HotelSearchParams): Promise<Hotel[]> => {
    const { data } = await api.post(ENDPOINTS.hotels.recommendations, params);
    return data.results || data;
  },

  book: async (bookingData: any): Promise<any> => {
    const { data } = await api.post(ENDPOINTS.hotels.book, bookingData);
    return data;
  },
};
