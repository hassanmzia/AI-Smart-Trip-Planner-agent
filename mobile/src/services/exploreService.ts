/**
 * Explore services - restaurants, attractions, weather, safety, events
 */

import api from './api';
import { ENDPOINTS } from '../utils/constants';
import type {
  Restaurant,
  TouristAttraction,
  WeatherData,
  SafetyInfo,
  PaginatedResponse,
} from '../types';

export const exploreService = {
  searchRestaurants: async (params: {
    destination: string;
    cuisine_type?: string;
  }): Promise<PaginatedResponse<Restaurant>> => {
    const { data } = await api.get(ENDPOINTS.restaurants.search, { params });
    return data;
  },

  searchAttractions: async (params: {
    destination: string;
    category?: string;
  }): Promise<PaginatedResponse<TouristAttraction>> => {
    const { data } = await api.get(ENDPOINTS.attractions.search, { params });
    return data;
  },

  getWeather: async (destination: string): Promise<WeatherData> => {
    const { data } = await api.get(ENDPOINTS.weather.forecast, { params: { destination } });
    return data;
  },

  getSafety: async (country: string): Promise<SafetyInfo> => {
    const { data } = await api.get(ENDPOINTS.safety.info, { params: { country } });
    return data;
  },

  searchEvents: async (params: {
    destination: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<any>> => {
    const { data } = await api.get(ENDPOINTS.events.search, { params });
    return data;
  },
};
