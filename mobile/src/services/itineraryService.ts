/**
 * Itinerary management service
 */

import api from './api';
import { ENDPOINTS } from '../utils/constants';
import type { Itinerary, ItineraryDay, ItineraryItem, PaginatedResponse } from '../types';

export const itineraryService = {
  list: async (): Promise<PaginatedResponse<Itinerary>> => {
    const { data } = await api.get(ENDPOINTS.itineraries.list);
    return data;
  },

  getDetail: async (id: number): Promise<Itinerary> => {
    const { data } = await api.get(ENDPOINTS.itineraries.detail(id));
    return data;
  },

  create: async (itineraryData: Partial<Itinerary>): Promise<Itinerary> => {
    const { data } = await api.post(ENDPOINTS.itineraries.create, itineraryData);
    return data;
  },

  update: async (id: number, itineraryData: Partial<Itinerary>): Promise<Itinerary> => {
    const { data } = await api.put(ENDPOINTS.itineraries.detail(id), itineraryData);
    return data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(ENDPOINTS.itineraries.detail(id));
  },

  createDay: async (dayData: Partial<ItineraryDay>): Promise<ItineraryDay> => {
    const { data } = await api.post(ENDPOINTS.itineraries.days, dayData);
    return data;
  },

  createItem: async (itemData: Partial<ItineraryItem>): Promise<ItineraryItem> => {
    const { data } = await api.post(ENDPOINTS.itineraries.items, itemData);
    return data;
  },
};
