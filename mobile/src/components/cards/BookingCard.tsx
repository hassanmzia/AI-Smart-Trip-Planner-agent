/**
 * Booking card with status, details, and quick actions
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import { BOOKING_STATUSES } from '../../utils/constants';
import type { Booking } from '../../types';

interface BookingCardProps {
  booking: Booking;
  onPress: () => void;
}

export const BookingCard: React.FC<BookingCardProps> = ({ booking, onPress }) => {
  const status = BOOKING_STATUSES[booking.status];
  const icon = booking.type === 'flight' ? 'flight' : booking.type === 'hotel' ? 'hotel' : 'card-travel';
  const title =
    booking.type === 'flight'
      ? `${booking.flight_details?.origin.city} → ${booking.flight_details?.destination.city}`
      : booking.type === 'hotel'
        ? booking.hotel_details?.name || 'Hotel Booking'
        : 'Package Booking';
  const subtitle =
    booking.type === 'flight'
      ? `${booking.flight_details?.airline} ${booking.flight_details?.flight_number}`
      : booking.hotel_details?.city || '';

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <Card variant="elevated" onPress={onPress} style={styles.card}>
      <View style={styles.topRow}>
        <View style={[styles.typeIcon, { backgroundColor: Colors.primary[50] }]}>
          <Icon name={icon} size={22} color={Colors.primary[600]} />
        </View>
        <View style={styles.info}>
          <Text style={styles.title} numberOfLines={1}>{title}</Text>
          <Text style={styles.subtitle}>{subtitle}</Text>
        </View>
        <Badge
          label={status.label}
          variant={
            booking.status === 'confirmed' ? 'success' :
            booking.status === 'cancelled' ? 'error' :
            booking.status === 'completed' ? 'info' : 'warning'
          }
        />
      </View>

      <View style={styles.detailsRow}>
        <View style={styles.detail}>
          <Icon name="calendar-today" size={14} color={Colors.gray[400]} />
          <Text style={styles.detailText}>{formatDate(booking.created_at)}</Text>
        </View>
        <View style={styles.detail}>
          <Icon name="attach-money" size={14} color={Colors.gray[400]} />
          <Text style={styles.detailText}>
            {booking.currency} {booking.total_amount.toLocaleString()}
          </Text>
        </View>
        <View style={styles.detail}>
          <Icon name="payment" size={14} color={Colors.gray[400]} />
          <Text style={styles.detailText}>
            {booking.payment_status === 'paid' ? 'Paid' : 'Pending'}
          </Text>
        </View>
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: Spacing.md,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typeIcon: {
    width: 44,
    height: 44,
    borderRadius: BorderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  info: {
    flex: 1,
  },
  title: {
    ...Typography.heading4,
    fontSize: 16,
    color: Colors.textPrimary,
  },
  subtitle: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: Spacing.md,
    paddingTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
  },
  detail: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
});
