import api, { handleApiResponse } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import { buildQueryString } from '@/utils/helpers';
import type {
  Hotel,
  HotelSearchParams,
  HotelBooking,
  HotelReview,
  PaginatedResponse,
} from '@/types';

/**
 * Search hotels with utility scoring
 */
export const searchHotels = async (
  params: HotelSearchParams
): Promise<PaginatedResponse<Hotel>> => {
  const queryString = buildQueryString(params);
  const response = await api.get(`${API_ENDPOINTS.HOTELS.SEARCH}?${queryString}`);
  return handleApiResponse(response);
};

/**
 * Get hotel details by ID
 */
export const getHotelDetails = async (hotelId: string): Promise<Hotel> => {
  const response = await api.get(`${API_ENDPOINTS.HOTELS.DETAILS}/${hotelId}`);
  return handleApiResponse(response);
};

/**
 * Book a hotel
 */
export const bookHotel = async (bookingData: {
  hotelId: string;
  roomTypeId: string;
  checkInDate: string;
  checkOutDate: string;
  guests: number;
  specialRequests?: string;
}): Promise<{ bookingId: string; paymentRequired: boolean }> => {
  const response = await api.post(API_ENDPOINTS.HOTELS.BOOK, bookingData);
  return handleApiResponse(response);
};

/**
 * Get hotel reviews
 */
export const getHotelReviews = async (
  hotelId: string,
  page: number = 1,
  pageSize: number = 10
): Promise<PaginatedResponse<HotelReview>> => {
  const response = await api.get(
    `${API_ENDPOINTS.HOTELS.DETAILS}/${hotelId}/reviews?page=${page}&pageSize=${pageSize}`
  );
  return handleApiResponse(response);
};

/**
 * Add hotel review
 */
export const addHotelReview = async (
  hotelId: string,
  review: { rating: number; comment: string }
): Promise<HotelReview> => {
  const response = await api.post(
    `${API_ENDPOINTS.HOTELS.DETAILS}/${hotelId}/reviews`,
    review
  );
  return handleApiResponse(response);
};

/**
 * Get room availability
 */
export const getRoomAvailability = async (
  hotelId: string,
  checkInDate: string,
  checkOutDate: string
): Promise<{
  available: boolean;
  rooms: Hotel['roomTypes'];
}> => {
  const response = await api.get(
    `${API_ENDPOINTS.HOTELS.DETAILS}/${hotelId}/availability?checkIn=${checkInDate}&checkOut=${checkOutDate}`
  );
  return handleApiResponse(response);
};

/**
 * Get popular destinations
 */
export const getPopularDestinations = async (): Promise<
  Array<{
    city: string;
    country: string;
    count: number;
    averagePrice: number;
    image?: string;
  }>
> => {
  const response = await api.get(`${API_ENDPOINTS.HOTELS.SEARCH}/popular-destinations`);
  return handleApiResponse(response);
};

/**
 * Get hotel recommendations based on user preferences
 */
export const getHotelRecommendations = async (
  params: Partial<HotelSearchParams>
): Promise<Hotel[]> => {
  const response = await api.post(
    `${API_ENDPOINTS.HOTELS.SEARCH}/recommendations`,
    params
  );
  return handleApiResponse(response);
};

/**
 * Compare hotels
 */
export const compareHotels = async (
  hotelIds: string[]
): Promise<{ hotels: Hotel[]; comparison: any }> => {
  const response = await api.post(`${API_ENDPOINTS.HOTELS.SEARCH}/compare`, {
    hotelIds,
  });
  return handleApiResponse(response);
};

/**
 * Get nearby attractions
 */
export const getNearbyAttractions = async (
  hotelId: string
): Promise<
  Array<{
    name: string;
    type: string;
    distance: number;
    rating?: number;
  }>
> => {
  const response = await api.get(
    `${API_ENDPOINTS.HOTELS.DETAILS}/${hotelId}/nearby-attractions`
  );
  return handleApiResponse(response);
};

/**
 * Get hotel amenities list
 */
export const getHotelAmenities = async (): Promise<string[]> => {
  const response = await api.get('/api/hotels/amenities');
  return handleApiResponse(response);
};
