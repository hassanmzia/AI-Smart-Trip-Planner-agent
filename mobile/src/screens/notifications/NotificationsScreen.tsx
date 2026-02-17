/**
 * Notifications screen
 */

import React, { useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Card } from '../../components/common/Card';
import { EmptyState } from '../../components/common/EmptyState';
import { useNotificationStore } from '../../store/notificationStore';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import api from '../../services/api';
import { ENDPOINTS } from '../../utils/constants';
import type { Notification } from '../../types';

const TYPE_CONFIG: Record<string, { icon: string; color: string }> = {
  price_alert: { icon: 'trending-down', color: '#22C55E' },
  booking_confirmation: { icon: 'check-circle', color: '#3B82F6' },
  payment_status: { icon: 'payment', color: '#8B5CF6' },
  trip_reminder: { icon: 'notifications-active', color: '#F97316' },
  system: { icon: 'info', color: Colors.gray[500] },
};

export const NotificationsScreen = ({ navigation }: any) => {
  const { notifications, setNotifications, markAsRead, markAllAsRead } =
    useNotificationStore();
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(ENDPOINTS.notifications.list);
      setNotifications(data.results || data || []);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchNotifications();
    }, []),
  );

  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const renderNotification = ({ item }: { item: Notification }) => {
    const config = TYPE_CONFIG[item.type] || TYPE_CONFIG.system;

    return (
      <TouchableOpacity
        style={[styles.notifItem, !item.read && styles.notifItemUnread]}
        onPress={() => markAsRead(item.id)}
        activeOpacity={0.7}
      >
        <View style={[styles.notifIcon, { backgroundColor: config.color + '15' }]}>
          <Icon name={config.icon} size={22} color={config.color} />
        </View>
        <View style={styles.notifContent}>
          <Text style={[styles.notifTitle, !item.read && styles.notifTitleUnread]}>
            {item.title}
          </Text>
          <Text style={styles.notifMessage} numberOfLines={2}>
            {item.message}
          </Text>
          <Text style={styles.notifTime}>{formatTime(item.created_at)}</Text>
        </View>
        {!item.read && <View style={styles.unreadDot} />}
      </TouchableOpacity>
    );
  };

  return (
    <ScreenWrapper scroll={false} noPadding loading={loading}>
      <View style={styles.header}>
        <Text style={styles.title}>Notifications</Text>
        {notifications.some((n) => !n.read) && (
          <TouchableOpacity onPress={markAllAsRead}>
            <Text style={styles.markAll}>Mark all read</Text>
          </TouchableOpacity>
        )}
      </View>

      <FlatList
        data={notifications}
        keyExtractor={(item) => String(item.id)}
        renderItem={renderNotification}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <EmptyState
            icon="notifications-none"
            title="No Notifications"
            subtitle="You're all caught up!"
          />
        }
      />
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.screenPadding,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.md,
  },
  title: {
    ...Typography.heading2,
    color: Colors.textPrimary,
  },
  markAll: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.primary[600],
  },
  list: {
    paddingBottom: Spacing['3xl'],
  },
  notifItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.screenPadding,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  notifItemUnread: {
    backgroundColor: Colors.primary[50] + '40',
  },
  notifIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  notifContent: {
    flex: 1,
  },
  notifTitle: {
    ...Typography.body,
    fontWeight: '500',
    color: Colors.textPrimary,
  },
  notifTitleUnread: {
    fontWeight: '700',
  },
  notifMessage: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  notifTime: {
    ...Typography.caption,
    color: Colors.textTertiary,
    marginTop: 4,
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.primary[600],
    marginTop: 6,
    marginLeft: Spacing.sm,
  },
});
