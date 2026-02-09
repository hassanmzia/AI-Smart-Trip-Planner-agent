import { useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as notificationService from '@/services/notificationService';
import useNotificationStore from '@/store/notificationStore';
import { QUERY_KEYS } from '@/utils/constants';
import toast from 'react-hot-toast';

/**
 * Hook to manage notifications
 */
export const useNotifications = () => {
  const queryClient = useQueryClient();
  const { notifications, unreadCount, markAsRead, markAllAsRead, removeNotification } =
    useNotificationStore();

  // Fetch notifications
  const { isLoading } = useQuery({
    queryKey: QUERY_KEYS.NOTIFICATIONS,
    queryFn: () => notificationService.getNotifications(),
    onSuccess: (data) => {
      // Sync with store
      data.items.forEach((notification) => {
        useNotificationStore.getState().addNotification(notification);
      });
    },
  });

  // Fetch unread count
  useQuery({
    queryKey: [...QUERY_KEYS.NOTIFICATIONS, 'unread-count'],
    queryFn: notificationService.getUnreadCount,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: notificationService.markAsRead,
    onSuccess: (_, notificationId) => {
      markAsRead(notificationId);
      queryClient.invalidateQueries(QUERY_KEYS.NOTIFICATIONS);
    },
  });

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation({
    mutationFn: notificationService.markAllAsRead,
    onSuccess: () => {
      markAllAsRead();
      queryClient.invalidateQueries(QUERY_KEYS.NOTIFICATIONS);
    },
  });

  // Delete notification mutation
  const deleteNotificationMutation = useMutation({
    mutationFn: notificationService.deleteNotification,
    onSuccess: (_, notificationId) => {
      removeNotification(notificationId);
      queryClient.invalidateQueries(QUERY_KEYS.NOTIFICATIONS);
    },
  });

  const handleMarkAsRead = useCallback(
    async (notificationId: string) => {
      try {
        await markAsReadMutation.mutateAsync(notificationId);
      } catch (error) {
        toast.error('Failed to mark notification as read');
      }
    },
    [markAsReadMutation]
  );

  const handleMarkAllAsRead = useCallback(async () => {
    try {
      await markAllAsReadMutation.mutateAsync();
      toast.success('All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all notifications as read');
    }
  }, [markAllAsReadMutation]);

  const handleDeleteNotification = useCallback(
    async (notificationId: string) => {
      try {
        await deleteNotificationMutation.mutateAsync(notificationId);
        toast.success('Notification deleted');
      } catch (error) {
        toast.error('Failed to delete notification');
      }
    },
    [deleteNotificationMutation]
  );

  return {
    notifications,
    unreadCount,
    isLoading,
    markAsRead: handleMarkAsRead,
    markAllAsRead: handleMarkAllAsRead,
    deleteNotification: handleDeleteNotification,
  };
};

/**
 * Hook to show toast notifications
 */
export const useToast = () => {
  const showSuccess = useCallback((message: string) => {
    toast.success(message);
  }, []);

  const showError = useCallback((message: string) => {
    toast.error(message);
  }, []);

  const showInfo = useCallback((message: string) => {
    toast(message);
  }, []);

  const showLoading = useCallback((message: string) => {
    return toast.loading(message);
  }, []);

  const dismiss = useCallback((toastId?: string) => {
    toast.dismiss(toastId);
  }, []);

  return {
    showSuccess,
    showError,
    showInfo,
    showLoading,
    dismiss,
  };
};
