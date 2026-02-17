/**
 * Bookings list screen
 */

import React, { useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { BookingCard } from '../../components/cards/BookingCard';
import { EmptyState } from '../../components/common/EmptyState';
import { Badge } from '../../components/common/Badge';
import { bookingService } from '../../services/bookingService';
import { Colors, Typography, Spacing } from '../../utils/theme';
import type { Booking } from '../../types';

const STATUS_FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'confirmed', label: 'Confirmed' },
  { key: 'pending', label: 'Pending' },
  { key: 'completed', label: 'Completed' },
  { key: 'cancelled', label: 'Cancelled' },
];

export const BookingsScreen = ({ navigation }: any) => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all');

  const fetchBookings = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await bookingService.list(params);
      setBookings(data.results || []);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchBookings();
    }, [filter]),
  );

  return (
    <ScreenWrapper scroll={false} noPadding loading={loading}>
      <View style={styles.header}>
        <Text style={styles.title}>Bookings</Text>
        <Text style={styles.subtitle}>{bookings.length} reservations</Text>
      </View>

      {/* Filter chips */}
      <View style={styles.filterRow}>
        {STATUS_FILTERS.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[styles.filterChip, filter === f.key && styles.filterChipActive]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterText, filter === f.key && styles.filterTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={bookings}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <BookingCard
            booking={item}
            onPress={() => navigation.navigate('BookingDetail', { booking: item })}
          />
        )}
        contentContainerStyle={styles.list}
        refreshing={refreshing}
        onRefresh={() => fetchBookings(true)}
        ListEmptyComponent={
          <EmptyState
            icon="confirmation-number"
            title="No Bookings"
            subtitle="Your flight and hotel bookings will appear here"
            actionTitle="Search Flights"
            onAction={() => navigation.navigate('FlightSearch')}
          />
        }
      />
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  header: {
    paddingHorizontal: Spacing.screenPadding,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.sm,
  },
  title: {
    ...Typography.heading2,
    color: Colors.textPrimary,
  },
  subtitle: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  filterRow: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing.md,
    gap: Spacing.sm,
  },
  filterChip: {
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 20,
    backgroundColor: Colors.gray[100],
  },
  filterChipActive: {
    backgroundColor: Colors.primary[600],
  },
  filterText: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.gray[500],
  },
  filterTextActive: {
    color: Colors.white,
  },
  list: {
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing['3xl'],
  },
});
