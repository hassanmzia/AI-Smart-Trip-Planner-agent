import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  SearchState,
  FlightSearchParams,
  HotelSearchParams,
  Flight,
  Hotel,
} from '@/types';

const useSearchStore = create<SearchState>()(
  devtools(
    (set) => ({
      flightSearchParams: null,
      hotelSearchParams: null,
      flightResults: [],
      hotelResults: [],
      isSearching: false,
      searchError: null,

      setFlightSearchParams: (params: FlightSearchParams) => {
        set({
          flightSearchParams: params,
          flightResults: [],
          searchError: null,
        });
      },

      setHotelSearchParams: (params: HotelSearchParams) => {
        set({
          hotelSearchParams: params,
          hotelResults: [],
          searchError: null,
        });
      },

      clearSearch: () => {
        set({
          flightSearchParams: null,
          hotelSearchParams: null,
          flightResults: [],
          hotelResults: [],
          isSearching: false,
          searchError: null,
        });
      },
    }),
    { name: 'SearchStore' }
  )
);

export default useSearchStore;
