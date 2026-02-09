import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import * as bookingService from '@/services/bookingService';
import type { BookingState, Booking } from '@/types';

const useBookingStore = create<BookingState>()(
  devtools(
    (set, get) => ({
      currentBooking: null,
      bookings: [],
      isLoading: false,
      error: null,

      createBooking: async (booking: Partial<Booking>) => {
        set({ isLoading: true, error: null });
        try {
          set({
            currentBooking: booking,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to create booking',
            isLoading: false,
          });
          throw error;
        }
      },

      updateBooking: async (id: string, data: Partial<Booking>) => {
        set({ isLoading: true, error: null });
        try {
          const updatedBooking = await bookingService.updateBooking(id, data);

          set((state) => ({
            bookings: state.bookings.map((b) => (b.id === id ? updatedBooking : b)),
            currentBooking:
              state.currentBooking?.id === id ? updatedBooking : state.currentBooking,
            isLoading: false,
          }));
        } catch (error: any) {
          set({
            error: error.message || 'Failed to update booking',
            isLoading: false,
          });
          throw error;
        }
      },

      cancelBooking: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await bookingService.cancelBooking(id);

          set((state) => ({
            bookings: state.bookings.map((b) =>
              b.id === id ? { ...b, status: 'cancelled' as const } : b
            ),
            isLoading: false,
          }));
        } catch (error: any) {
          set({
            error: error.message || 'Failed to cancel booking',
            isLoading: false,
          });
          throw error;
        }
      },

      fetchBookings: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await bookingService.getBookings();

          set({
            bookings: response.items,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to fetch bookings',
            isLoading: false,
          });
          throw error;
        }
      },
    }),
    { name: 'BookingStore' }
  )
);

export default useBookingStore;
