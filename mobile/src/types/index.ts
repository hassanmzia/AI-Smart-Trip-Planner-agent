/**
 * AI Trip Planner Mobile - Type Definitions
 * Mirrors the web app types for full API compatibility.
 */

// ─── Auth ────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  role: 'user' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  profile?: UserProfile;
  preferences?: UserPreferences;
  date_joined?: string;
}

export interface UserProfile {
  date_of_birth?: string;
  nationality?: string;
  passport_number?: string;
  preferred_currency: string;
  preferred_language: string;
  preferred_travel_class: string;
  preferred_airlines: string[];
  preferred_hotel_chains: string[];
  loyalty_programs: LoyaltyProgram[];
  dietary_restrictions: string[];
  seat_preference: string;
  total_trips: number;
  total_bookings: number;
  total_spent: number;
  avatar?: string;
}

export interface UserPreferences {
  notifications_email: boolean;
  notifications_push: boolean;
  notifications_sms: boolean;
  price_alerts: boolean;
  newsletter: boolean;
  dark_mode: boolean;
}

export interface LoyaltyProgram {
  name: string;
  number: string;
  tier: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
}

// ─── Flights ────────────────────────────────────────────────────────────────

export interface Flight {
  id: string | number;
  airline: string;
  airline_logo?: string;
  flight_number: string;
  origin: Airport;
  destination: Airport;
  departure_time: string;
  arrival_time: string;
  duration: string;
  duration_minutes?: number;
  price: number;
  currency: string;
  travel_class: string;
  stops: number;
  layovers?: Layover[];
  available_seats: number;
  aircraft?: string;
  amenities?: string[];
  carbon_emissions?: number;
  booking_token?: string;
  goal_evaluation?: GoalEvaluation;
}

export interface Airport {
  code: string;
  name: string;
  city: string;
  country: string;
  timezone?: string;
}

export interface Layover {
  airport: Airport;
  duration: string;
}

export interface GoalEvaluation {
  total_utility: number;
  budget_constraint_met: boolean;
  price_score: number;
  duration_score: number;
  stops_score: number;
  recommendation: 'excellent' | 'good' | 'fair' | 'poor';
}

export interface FlightSearchParams {
  origin: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  passengers: number;
  travel_class: string;
  max_budget?: number;
  goals?: string[];
}

// ─── Hotels ─────────────────────────────────────────────────────────────────

export interface Hotel {
  id: string | number;
  name: string;
  address: string;
  city: string;
  country: string;
  rating: number;
  stars: number;
  price_per_night: number;
  currency: string;
  images: string[];
  amenities: string[];
  check_in_time: string;
  check_out_time: string;
  distance_from_center?: number;
  utility_score?: UtilityScore;
  review_count?: number;
  description?: string;
}

export interface UtilityScore {
  total_score: number;
  price_value: number;
  location_score: number;
  rating_score: number;
  amenities_score: number;
  recommendation: 'excellent' | 'good' | 'fair' | 'poor';
}

export interface HotelSearchParams {
  destination: string;
  check_in_date: string;
  check_out_date: string;
  guests: number;
  rooms: number;
  max_budget?: number;
  min_rating?: number;
  amenities?: string[];
}

// ─── Bookings ───────────────────────────────────────────────────────────────

export interface Booking {
  id: string | number;
  user_id: number;
  type: 'flight' | 'hotel' | 'package';
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  flight_details?: Flight;
  hotel_details?: Hotel;
  total_amount: number;
  currency: string;
  payment_status: 'pending' | 'paid' | 'refunded' | 'failed';
  payment_method?: string;
  created_at: string;
  updated_at: string;
  passengers?: Passenger[];
  special_requests?: string;
}

export interface Passenger {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  passport_number: string;
  nationality: string;
  email?: string;
  phone?: string;
}

// ─── Itineraries ────────────────────────────────────────────────────────────

export interface Itinerary {
  id: number;
  user?: number;
  title: string;
  description: string;
  destination: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'planned' | 'approved' | 'booking' | 'booked' | 'active' | 'completed' | 'cancelled';
  number_of_travelers: number;
  estimated_budget: number;
  actual_spent: number;
  currency: string;
  is_public: boolean;
  cover_image?: string;
  days: ItineraryDay[];
  created_at: string;
  updated_at: string;
}

export interface ItineraryDay {
  id: number;
  itinerary: number;
  day_number: number;
  date: string;
  title: string;
  description?: string;
  notes?: string;
  items: ItineraryItem[];
}

export interface ItineraryItem {
  id: number;
  day: number;
  item_type: 'flight' | 'hotel' | 'restaurant' | 'attraction' | 'activity' | 'transport' | 'note';
  order: number;
  title: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  duration_minutes?: number;
  location_name?: string;
  location_address?: string;
  estimated_cost?: number;
  notes?: string;
  url?: string;
}

// ─── Notifications ──────────────────────────────────────────────────────────

export interface Notification {
  id: string | number;
  user_id?: number;
  type: 'price_alert' | 'booking_confirmation' | 'payment_status' | 'trip_reminder' | 'system';
  title: string;
  message: string;
  read: boolean;
  data?: Record<string, any>;
  created_at: string;
}

// ─── Chat / AI Agent ────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

// ─── Explore ────────────────────────────────────────────────────────────────

export interface Restaurant {
  id: string | number;
  name: string;
  cuisine_type: string;
  rating: number;
  price_level: string;
  address: string;
  city: string;
  image?: string;
  distance?: number;
  is_open?: boolean;
}

export interface TouristAttraction {
  id: string | number;
  name: string;
  category: string;
  rating: number;
  price: number;
  address: string;
  city: string;
  image?: string;
  description?: string;
  opening_hours?: string;
}

export interface WeatherData {
  location: string;
  temperature: number;
  condition: string;
  humidity: number;
  wind_speed: number;
  icon?: string;
  forecast: WeatherForecast[];
}

export interface WeatherForecast {
  date: string;
  high: number;
  low: number;
  condition: string;
  icon?: string;
}

export interface SafetyInfo {
  country: string;
  overall_risk: 'low' | 'medium' | 'high' | 'extreme';
  advisory: string;
  health_info?: string;
  emergency_numbers?: Record<string, string>;
}

// ─── API Response Wrappers ──────────────────────────────────────────────────

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

// ─── Navigation ─────────────────────────────────────────────────────────────

export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  FlightSearch: undefined;
  FlightResults: { params: FlightSearchParams };
  FlightDetail: { flight: Flight };
  HotelSearch: undefined;
  HotelResults: { params: HotelSearchParams };
  HotelDetail: { hotel: Hotel };
  BookingDetail: { booking: Booking };
  BookingConfirmation: { bookingId: string | number };
  ItineraryDetail: { itineraryId: number };
  CreateItinerary: undefined;
  AIPlanner: undefined;
  RestaurantDetail: { restaurant: Restaurant };
  AttractionDetail: { attraction: TouristAttraction };
  Weather: { destination?: string };
  Safety: { country?: string };
  EditProfile: undefined;
  Settings: undefined;
  Chat: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

export type MainTabParamList = {
  HomeTab: undefined;
  ExploreTab: undefined;
  TripsTab: undefined;
  BookingsTab: undefined;
  ProfileTab: undefined;
};
