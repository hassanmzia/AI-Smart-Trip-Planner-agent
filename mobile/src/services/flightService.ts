/**
 * Flight search and booking service
 */

import api from './api';
import { ENDPOINTS } from '../utils/constants';
import type { Flight, FlightSearchParams, PaginatedResponse, Airport } from '../types';

export const flightService = {
  search: async (params: FlightSearchParams): Promise<PaginatedResponse<Flight>> => {
    const { data } = await api.get(ENDPOINTS.flights.search, { params });
    return data;
  },

  getDetail: async (id: string | number): Promise<Flight> => {
    const { data } = await api.get(ENDPOINTS.flights.detail(id));
    return data;
  },

  searchAirports: async (query: string): Promise<Airport[]> => {
    const { data } = await api.get(ENDPOINTS.flights.airports, { params: { query } });
    return data.results || data;
  },

  getRecommendations: async (params: FlightSearchParams): Promise<Flight[]> => {
    const { data } = await api.post(ENDPOINTS.flights.recommendations, params);
    return data.results || data;
  },

  book: async (bookingData: any): Promise<any> => {
    const { data } = await api.post(ENDPOINTS.flights.book, bookingData);
    return data;
  },
};
