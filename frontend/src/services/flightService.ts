import api, { handleApiResponse } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import { buildQueryString } from '@/utils/helpers';
import type {
  Flight,
  FlightSearchParams,
  FlightBooking,
  PaginatedResponse,
} from '@/types';

/**
 * Search flights with goal-based evaluation
 */
export const searchFlights = async (
  params: FlightSearchParams
): Promise<PaginatedResponse<Flight>> => {
  const queryString = buildQueryString(params);
  const response = await api.get(`${API_ENDPOINTS.FLIGHTS.SEARCH}?${queryString}`);
  return handleApiResponse(response);
};

/**
 * Get flight details by ID
 */
export const getFlightDetails = async (flightId: string): Promise<Flight> => {
  const response = await api.get(`${API_ENDPOINTS.FLIGHTS.DETAILS}/${flightId}`);
  return handleApiResponse(response);
};

/**
 * Book a flight
 */
export const bookFlight = async (bookingData: {
  flightId: string;
  passengers: FlightBooking['passengers'];
  seatSelections?: FlightBooking['seatSelections'];
  specialRequests?: string;
}): Promise<{ bookingId: string; paymentRequired: boolean }> => {
  const response = await api.post(API_ENDPOINTS.FLIGHTS.BOOK, bookingData);
  return handleApiResponse(response);
};

/**
 * Get available seats for a flight
 */
export const getAvailableSeats = async (
  flightId: string
): Promise<{ seatMap: any; available: string[] }> => {
  const response = await api.get(`${API_ENDPOINTS.FLIGHTS.DETAILS}/${flightId}/seats`);
  return handleApiResponse(response);
};

/**
 * Get flight price history
 */
export const getFlightPriceHistory = async (
  origin: string,
  destination: string,
  days: number = 30
): Promise<Array<{ date: string; price: number }>> => {
  const response = await api.get(
    `${API_ENDPOINTS.FLIGHTS.SEARCH}/price-history?origin=${origin}&destination=${destination}&days=${days}`
  );
  return handleApiResponse(response);
};

/**
 * Get popular routes
 */
export const getPopularRoutes = async (): Promise<
  Array<{
    origin: string;
    destination: string;
    count: number;
    averagePrice: number;
  }>
> => {
  const response = await api.get(`${API_ENDPOINTS.FLIGHTS.SEARCH}/popular-routes`);
  return handleApiResponse(response);
};

/**
 * Get airlines
 */
export const getAirlines = async (): Promise<
  Array<{ code: string; name: string; logo?: string }>
> => {
  const response = await api.get('/api/flights/airlines');
  return handleApiResponse(response);
};

/**
 * Search airports by query
 */
export const searchAirports = async (
  query: string
): Promise<
  Array<{
    code: string;
    name: string;
    city: string;
    country: string;
  }>
> => {
  const response = await api.get(`/api/flights/airports?q=${encodeURIComponent(query)}`);
  return handleApiResponse(response);
};

/**
 * Compare flights
 */
export const compareFlights = async (
  flightIds: string[]
): Promise<{ flights: Flight[]; comparison: any }> => {
  const response = await api.post(`${API_ENDPOINTS.FLIGHTS.SEARCH}/compare`, {
    flightIds,
  });
  return handleApiResponse(response);
};

/**
 * Get flight recommendations based on user preferences
 */
export const getFlightRecommendations = async (
  params: Partial<FlightSearchParams>
): Promise<Flight[]> => {
  const response = await api.post(`${API_ENDPOINTS.FLIGHTS.SEARCH}/recommendations`, params);
  return handleApiResponse(response);
};
