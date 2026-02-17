/**
 * App-wide constants and configuration
 */

import { Platform } from 'react-native';

// ─── API Configuration ──────────────────────────────────────────────────────

// Production backend URL (your live Linux server).
// Set USE_LOCAL_BACKEND=true below to use localhost during development.
const USE_LOCAL_BACKEND = false;

const PRODUCTION_URL = 'https://demo.eminencetechsolutions.com:3090';
const PRODUCTION_WS  = 'wss://demo.eminencetechsolutions.com:3090/ws';
const PRODUCTION_MCP = 'https://demo.eminencetechsolutions.com:3090/mcp';

const LOCAL_API = Platform.select({
  android: 'http://10.0.2.2:8109', // Android emulator localhost alias
  ios: 'http://localhost:8109',
  default: 'http://localhost:8109',
})!;

const LOCAL_WS = Platform.select({
  android: 'ws://10.0.2.2:8109/ws',
  ios: 'ws://localhost:8109/ws',
  default: 'ws://localhost:8109/ws',
})!;

const LOCAL_MCP = Platform.select({
  android: 'http://10.0.2.2:8107',
  ios: 'http://localhost:8107',
  default: 'http://localhost:8107',
})!;

export const API_BASE_URL = (__DEV__ && USE_LOCAL_BACKEND) ? LOCAL_API : PRODUCTION_URL;
export const WS_BASE_URL  = (__DEV__ && USE_LOCAL_BACKEND) ? LOCAL_WS  : PRODUCTION_WS;
export const MCP_BASE_URL = (__DEV__ && USE_LOCAL_BACKEND) ? LOCAL_MCP : PRODUCTION_MCP;

// ─── API Endpoints ──────────────────────────────────────────────────────────

export const ENDPOINTS = {
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',
    refresh: '/api/auth/refresh',
    me: '/api/auth/me',
    forgotPassword: '/api/auth/forgot-password',
    resetPassword: '/api/auth/reset-password',
  },
  flights: {
    search: '/api/flights/search',
    detail: (id: string | number) => `/api/flights/${id}`,
    book: '/api/flights/book',
    airports: '/api/flights/airports',
    recommendations: '/api/flights/search/recommendations',
  },
  hotels: {
    search: '/api/hotels/search',
    detail: (id: string | number) => `/api/hotels/${id}`,
    book: '/api/hotels/book',
    reviews: (id: string | number) => `/api/hotels/${id}/reviews`,
    recommendations: '/api/hotels/search/recommendations',
  },
  bookings: {
    list: '/api/bookings/bookings/',
    detail: (id: string | number) => `/api/bookings/bookings/${id}`,
    cancel: (id: string | number) => `/api/bookings/bookings/${id}/cancel`,
  },
  itineraries: {
    list: '/api/itineraries/itineraries/',
    detail: (id: number) => `/api/itineraries/itineraries/${id}/`,
    create: '/api/itineraries/itineraries/',
    days: '/api/itineraries/days/',
    items: '/api/itineraries/items/',
  },
  agents: {
    chat: '/api/agents/chat',
    suggestions: '/api/agents/chat/suggestions',
  },
  restaurants: {
    search: '/api/restaurants/search/',
  },
  attractions: {
    search: '/api/tourist-attractions/search/',
  },
  weather: {
    forecast: '/api/weather/forecast/',
  },
  safety: {
    info: '/api/safety/info/',
  },
  events: {
    search: '/api/events/search/',
  },
  notifications: {
    list: '/api/notifications/notifications/',
    markRead: '/api/notifications/notifications/mark_read/',
  },
  profile: {
    me: '/api/profiles/me/',
    avatar: '/api/profiles/upload_avatar/',
  },
} as const;

// ─── Storage Keys ───────────────────────────────────────────────────────────

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  THEME: 'theme',
  ONBOARDING_COMPLETE: 'onboarding_complete',
  SEARCH_HISTORY: 'search_history',
} as const;

// ─── App Constants ──────────────────────────────────────────────────────────

export const APP_NAME = 'AI Trip Planner';
export const APP_VERSION = '1.0.0';

export const TRAVEL_CLASSES = [
  { label: 'Economy', value: 'economy' },
  { label: 'Premium Economy', value: 'premium_economy' },
  { label: 'Business', value: 'business' },
  { label: 'First Class', value: 'first' },
];

export const BOOKING_STATUSES = {
  pending: { label: 'Pending', color: '#EAB308' },
  confirmed: { label: 'Confirmed', color: '#22C55E' },
  cancelled: { label: 'Cancelled', color: '#EF4444' },
  completed: { label: 'Completed', color: '#3B82F6' },
} as const;

export const AMENITY_ICONS: Record<string, string> = {
  wifi: 'wifi',
  pool: 'pool',
  parking: 'local-parking',
  gym: 'fitness-center',
  spa: 'spa',
  restaurant: 'restaurant',
  bar: 'local-bar',
  'room-service': 'room-service',
  laundry: 'local-laundry-service',
  ac: 'ac-unit',
  breakfast: 'free-breakfast',
  pet: 'pets',
};

export const ITEM_TYPE_ICONS: Record<string, { name: string; color: string }> = {
  flight: { name: 'flight', color: '#3B82F6' },
  hotel: { name: 'hotel', color: '#8B5CF6' },
  restaurant: { name: 'restaurant', color: '#F97316' },
  attraction: { name: 'photo-camera', color: '#22C55E' },
  activity: { name: 'directions-run', color: '#EC4899' },
  transport: { name: 'directions-car', color: '#06B6D4' },
  note: { name: 'note', color: '#6B7280' },
};
