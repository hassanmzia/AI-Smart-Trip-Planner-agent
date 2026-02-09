import api, { handleApiResponse } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import type { Notification, PaginatedResponse } from '@/types';

/**
 * Get all notifications
 */
export const getNotifications = async (
  page: number = 1,
  pageSize: number = 20,
  unreadOnly: boolean = false
): Promise<PaginatedResponse<Notification>> => {
  const response = await api.get(
    `${API_ENDPOINTS.NOTIFICATIONS.LIST}?page=${page}&pageSize=${pageSize}&unreadOnly=${unreadOnly}`
  );
  return handleApiResponse(response);
};

/**
 * Get unread notification count
 */
export const getUnreadCount = async (): Promise<number> => {
  const response = await api.get(`${API_ENDPOINTS.NOTIFICATIONS.LIST}/unread-count`);
  return handleApiResponse(response);
};

/**
 * Mark notification as read
 */
export const markAsRead = async (notificationId: string): Promise<void> => {
  const response = await api.put(
    `${API_ENDPOINTS.NOTIFICATIONS.MARK_READ}/${notificationId}`
  );
  return handleApiResponse(response);
};

/**
 * Mark all notifications as read
 */
export const markAllAsRead = async (): Promise<void> => {
  const response = await api.put(`${API_ENDPOINTS.NOTIFICATIONS.MARK_READ}/all`);
  return handleApiResponse(response);
};

/**
 * Delete notification
 */
export const deleteNotification = async (notificationId: string): Promise<void> => {
  const response = await api.delete(
    `${API_ENDPOINTS.NOTIFICATIONS.LIST}/${notificationId}`
  );
  return handleApiResponse(response);
};

/**
 * Delete all notifications
 */
export const deleteAllNotifications = async (): Promise<void> => {
  const response = await api.delete(`${API_ENDPOINTS.NOTIFICATIONS.LIST}/all`);
  return handleApiResponse(response);
};

/**
 * Get notification preferences
 */
export const getNotificationPreferences = async (): Promise<{
  email: boolean;
  sms: boolean;
  push: boolean;
  types: Record<string, boolean>;
}> => {
  const response = await api.get('/api/notifications/preferences');
  return handleApiResponse(response);
};

/**
 * Update notification preferences
 */
export const updateNotificationPreferences = async (preferences: {
  email?: boolean;
  sms?: boolean;
  push?: boolean;
  types?: Record<string, boolean>;
}): Promise<void> => {
  const response = await api.put('/api/notifications/preferences', preferences);
  return handleApiResponse(response);
};
