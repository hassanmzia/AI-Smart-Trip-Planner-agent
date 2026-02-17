/**
 * Flight result card with airline info, route, and AI scoring
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Colors, Typography, Spacing, Shadows } from '../../utils/theme';
import type { Flight } from '../../types';

interface FlightCardProps {
  flight: Flight;
  onPress: () => void;
}

export const FlightCard: React.FC<FlightCardProps> = ({ flight, onPress }) => {
  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
  };

  const stopsLabel = flight.stops === 0 ? 'Direct' : `${flight.stops} Stop${flight.stops > 1 ? 's' : ''}`;

  return (
    <Card variant="elevated" onPress={onPress} style={styles.card}>
      {/* Airline & Price Row */}
      <View style={styles.topRow}>
        <View style={styles.airlineInfo}>
          <View style={styles.airlineLogo}>
            <Icon name="flight" size={18} color={Colors.primary[600]} />
          </View>
          <View>
            <Text style={styles.airlineName}>{flight.airline}</Text>
            <Text style={styles.flightNumber}>{flight.flight_number}</Text>
          </View>
        </View>
        <View style={styles.priceContainer}>
          <Text style={styles.price}>
            ${flight.price.toLocaleString()}
          </Text>
          <Text style={styles.priceLabel}>per person</Text>
        </View>
      </View>

      {/* Route */}
      <View style={styles.routeContainer}>
        <View style={styles.routePoint}>
          <Text style={styles.time}>{formatTime(flight.departure_time)}</Text>
          <Text style={styles.airportCode}>{flight.origin.code}</Text>
          <Text style={styles.cityName} numberOfLines={1}>{flight.origin.city}</Text>
        </View>

        <View style={styles.routeLine}>
          <View style={styles.dot} />
          <View style={styles.line}>
            <Text style={styles.duration}>{flight.duration}</Text>
          </View>
          <View style={styles.dot} />
          <Text style={styles.stopsText}>{stopsLabel}</Text>
        </View>

        <View style={[styles.routePoint, styles.routePointEnd]}>
          <Text style={styles.time}>{formatTime(flight.arrival_time)}</Text>
          <Text style={styles.airportCode}>{flight.destination.code}</Text>
          <Text style={styles.cityName} numberOfLines={1}>{flight.destination.city}</Text>
        </View>
      </View>

      {/* Bottom row - class & AI recommendation */}
      <View style={styles.bottomRow}>
        <Badge label={flight.travel_class} variant="neutral" />
        {flight.goal_evaluation && (
          <Badge
            label={`AI Score: ${Math.round(flight.goal_evaluation.total_utility * 100)}%`}
            variant={flight.goal_evaluation.recommendation}
            icon="auto-awesome"
          />
        )}
        {flight.available_seats <= 5 && (
          <Badge
            label={`${flight.available_seats} left`}
            variant="warning"
            icon="event-seat"
          />
        )}
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
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.base,
  },
  airlineInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  airlineLogo: {
    width: 36,
    height: 36,
    borderRadius: 8,
    backgroundColor: Colors.primary[50],
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.sm,
  },
  airlineName: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  flightNumber: {
    ...Typography.caption,
    color: Colors.textTertiary,
  },
  priceContainer: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: 22,
    fontWeight: '700',
    color: Colors.primary[700],
  },
  priceLabel: {
    ...Typography.caption,
    color: Colors.textTertiary,
  },
  routeContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: Spacing.md,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: Colors.gray[100],
    marginBottom: Spacing.md,
  },
  routePoint: {
    width: 70,
  },
  routePointEnd: {
    alignItems: 'flex-end',
  },
  time: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  airportCode: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.primary[600],
    marginTop: 2,
  },
  cityName: {
    ...Typography.caption,
    color: Colors.textTertiary,
  },
  routeLine: {
    flex: 1,
    alignItems: 'center',
    paddingTop: 6,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: Colors.primary[400],
  },
  line: {
    height: 1,
    width: '80%',
    backgroundColor: Colors.gray[200],
    marginVertical: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
  duration: {
    ...Typography.caption,
    color: Colors.textSecondary,
    backgroundColor: Colors.white,
    paddingHorizontal: 6,
    position: 'absolute',
    top: -8,
  },
  stopsText: {
    ...Typography.caption,
    color: Colors.textTertiary,
    marginTop: 2,
  },
  bottomRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    flexWrap: 'wrap',
  },
});
