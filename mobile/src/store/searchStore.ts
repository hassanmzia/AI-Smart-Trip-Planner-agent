/**
 * Search state store
 */

import { create } from 'zustand';
import type { FlightSearchParams, HotelSearchParams, Flight, Hotel } from '../types';

interface SearchState {
  // Flight search
  flightSearchParams: FlightSearchParams | null;
  flightResults: Flight[];
  isSearchingFlights: boolean;
  flightError: string | null;

  // Hotel search
  hotelSearchParams: HotelSearchParams | null;
  hotelResults: Hotel[];
  isSearchingHotels: boolean;
  hotelError: string | null;

  // Actions
  setFlightSearchParams: (params: FlightSearchParams) => void;
  setFlightResults: (results: Flight[]) => void;
  setFlightSearching: (loading: boolean) => void;
  setFlightError: (error: string | null) => void;

  setHotelSearchParams: (params: HotelSearchParams) => void;
  setHotelResults: (results: Hotel[]) => void;
  setHotelSearching: (loading: boolean) => void;
  setHotelError: (error: string | null) => void;

  clearSearch: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  flightSearchParams: null,
  flightResults: [],
  isSearchingFlights: false,
  flightError: null,

  hotelSearchParams: null,
  hotelResults: [],
  isSearchingHotels: false,
  hotelError: null,

  setFlightSearchParams: (params) => set({ flightSearchParams: params }),
  setFlightResults: (results) => set({ flightResults: results }),
  setFlightSearching: (loading) => set({ isSearchingFlights: loading }),
  setFlightError: (error) => set({ flightError: error }),

  setHotelSearchParams: (params) => set({ hotelSearchParams: params }),
  setHotelResults: (results) => set({ hotelResults: results }),
  setHotelSearching: (loading) => set({ isSearchingHotels: loading }),
  setHotelError: (error) => set({ hotelError: error }),

  clearSearch: () =>
    set({
      flightSearchParams: null,
      flightResults: [],
      flightError: null,
      hotelSearchParams: null,
      hotelResults: [],
      hotelError: null,
    }),
}));
