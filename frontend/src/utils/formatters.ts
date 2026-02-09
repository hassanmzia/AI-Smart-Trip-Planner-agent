import { format, parseISO, differenceInMinutes, differenceInDays } from 'date-fns';
import { CURRENCY_SYMBOLS, DATE_FORMATS } from './constants';

/**
 * Format currency with symbol
 */
export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  const symbol = CURRENCY_SYMBOLS[currency] || currency;
  return `${symbol}${amount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

/**
 * Format date to display format
 */
export const formatDate = (date: string | Date, formatStr: string = DATE_FORMATS.DISPLAY): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return format(dateObj, formatStr);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
};

/**
 * Format duration in minutes to readable format (e.g., "2h 30m")
 */
export const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) {
    return `${mins}m`;
  }

  if (mins === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${mins}m`;
};

/**
 * Format time range (e.g., "08:00 - 12:30")
 */
export const formatTimeRange = (start: string, end: string): string => {
  const startTime = formatDate(start, 'HH:mm');
  const endTime = formatDate(end, 'HH:mm');
  return `${startTime} - ${endTime}`;
};

/**
 * Calculate and format trip duration
 */
export const formatTripDuration = (checkIn: string, checkOut: string): string => {
  try {
    const days = differenceInDays(parseISO(checkOut), parseISO(checkIn));
    return days === 1 ? '1 night' : `${days} nights`;
  } catch (error) {
    return 'N/A';
  }
};

/**
 * Format flight number (e.g., "AA 123" from "AA123")
 */
export const formatFlightNumber = (flightNumber: string): string => {
  const match = flightNumber.match(/^([A-Z]{2})(\d+)$/);
  if (match) {
    return `${match[1]} ${match[2]}`;
  }
  return flightNumber;
};

/**
 * Format passenger count (e.g., "1 passenger", "3 passengers")
 */
export const formatPassengerCount = (count: number): string => {
  return count === 1 ? '1 passenger' : `${count} passengers`;
};

/**
 * Format guest count (e.g., "1 guest", "4 guests")
 */
export const formatGuestCount = (count: number): string => {
  return count === 1 ? '1 guest' : `${count} guests`;
};

/**
 * Format room count (e.g., "1 room", "2 rooms")
 */
export const formatRoomCount = (count: number): string => {
  return count === 1 ? '1 room' : `${count} rooms`;
};

/**
 * Format phone number
 */
export const formatPhoneNumber = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`;
  }
  return phone;
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number, decimals: number = 0): string => {
  return `${value.toFixed(decimals)}%`;
};

/**
 * Format rating (e.g., "4.5/5.0")
 */
export const formatRating = (rating: number, maxRating: number = 5): string => {
  return `${rating.toFixed(1)}/${maxRating.toFixed(1)}`;
};

/**
 * Format distance (e.g., "1.5 km" or "0.9 mi")
 */
export const formatDistance = (km: number, unit: 'km' | 'mi' = 'km'): string => {
  if (unit === 'mi') {
    const miles = km * 0.621371;
    return `${miles.toFixed(1)} mi`;
  }
  return `${km.toFixed(1)} km`;
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days")
 */
export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    const now = new Date();
    const diffMinutes = differenceInMinutes(now, dateObj);

    if (diffMinutes < 1) return 'just now';
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;

    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    const diffWeeks = Math.floor(diffDays / 7);
    if (diffWeeks < 4) return `${diffWeeks} week${diffWeeks > 1 ? 's' : ''} ago`;

    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
  } catch (error) {
    return 'Invalid date';
  }
};

/**
 * Format booking reference
 */
export const formatBookingReference = (id: string): string => {
  return id.slice(0, 8).toUpperCase();
};

/**
 * Capitalize first letter
 */
export const capitalize = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

/**
 * Format name (first letter of each word capitalized)
 */
export const formatName = (name: string): string => {
  return name
    .split(' ')
    .map(word => capitalize(word))
    .join(' ');
};
