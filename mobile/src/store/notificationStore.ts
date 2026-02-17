/**
 * Notification state store
 */

import { create } from 'zustand';
import type { Notification } from '../types';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;

  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  markAsRead: (id: string | number) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string | number) => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,

  setNotifications: (notifications) =>
    set({
      notifications,
      unreadCount: notifications.filter((n) => !n.read).length,
    }),

  addNotification: (notification) => {
    const { notifications } = get();
    set({
      notifications: [notification, ...notifications],
      unreadCount: get().unreadCount + (notification.read ? 0 : 1),
    });
  },

  markAsRead: (id) => {
    const { notifications } = get();
    set({
      notifications: notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n,
      ),
      unreadCount: Math.max(0, get().unreadCount - 1),
    });
  },

  markAllAsRead: () => {
    const { notifications } = get();
    set({
      notifications: notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    });
  },

  removeNotification: (id) => {
    const { notifications } = get();
    const notification = notifications.find((n) => n.id === id);
    set({
      notifications: notifications.filter((n) => n.id !== id),
      unreadCount: notification && !notification.read
        ? Math.max(0, get().unreadCount - 1)
        : get().unreadCount,
    });
  },

  clearAll: () => set({ notifications: [], unreadCount: 0 }),
}));
