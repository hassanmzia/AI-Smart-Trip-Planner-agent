/**
 * Itinerary card with destination, dates, progress, and budget
 */

import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import type { Itinerary } from '../../types';

interface ItineraryCardProps {
  itinerary: Itinerary;
  onPress: () => void;
}

export const ItineraryCard: React.FC<ItineraryCardProps> = ({ itinerary, onPress }) => {
  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  const statusVariant = {
    draft: 'neutral' as const,
    planned: 'info' as const,
    approved: 'good' as const,
    booking: 'warning' as const,
    booked: 'success' as const,
    active: 'excellent' as const,
    completed: 'success' as const,
    cancelled: 'error' as const,
  }[itinerary.status] || 'neutral' as const;

  const dayCount = itinerary.days?.length || 0;
  const itemCount = itinerary.days?.reduce((sum, d) => sum + (d.items?.length || 0), 0) || 0;

  const placeholderImage = 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400';

  return (
    <Card variant="elevated" onPress={onPress} style={styles.card} padding={0}>
      {/* Cover Image with Overlay */}
      <View style={styles.imageContainer}>
        <Image
          source={{ uri: itinerary.cover_image || placeholderImage }}
          style={styles.image}
          resizeMode="cover"
        />
        <LinearGradient
          colors={['transparent', 'rgba(0,0,0,0.7)']}
          style={styles.gradient}
        >
          <Text style={styles.destination}>{itinerary.destination}</Text>
          <Text style={styles.dates}>
            {formatDate(itinerary.start_date)} - {formatDate(itinerary.end_date)}
          </Text>
        </LinearGradient>
        <View style={styles.statusBadge}>
          <Badge label={itinerary.status} variant={statusVariant} />
        </View>
      </View>

      {/* Content */}
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={1}>{itinerary.title}</Text>
        {itinerary.description ? (
          <Text style={styles.description} numberOfLines={2}>{itinerary.description}</Text>
        ) : null}

        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Icon name="calendar-today" size={16} color={Colors.primary[500]} />
            <Text style={styles.statText}>{dayCount} days</Text>
          </View>
          <View style={styles.stat}>
            <Icon name="place" size={16} color={Colors.secondary[500]} />
            <Text style={styles.statText}>{itemCount} activities</Text>
          </View>
          <View style={styles.stat}>
            <Icon name="people" size={16} color={Colors.success.main} />
            <Text style={styles.statText}>{itinerary.number_of_travelers}</Text>
          </View>
          <View style={styles.stat}>
            <Icon name="attach-money" size={16} color={Colors.warning.dark} />
            <Text style={styles.statText}>
              {itinerary.estimated_budget.toLocaleString()}
            </Text>
          </View>
        </View>
      </View>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginBottom: Spacing.base,
  },
  imageContainer: {
    height: 150,
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  gradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: Spacing.base,
    paddingBottom: Spacing.md,
    paddingTop: Spacing['3xl'],
  },
  destination: {
    ...Typography.heading3,
    color: Colors.white,
  },
  dates: {
    ...Typography.bodySmall,
    color: 'rgba(255,255,255,0.8)',
  },
  statusBadge: {
    position: 'absolute',
    top: Spacing.sm,
    right: Spacing.sm,
  },
  content: {
    padding: Spacing.base,
  },
  title: {
    ...Typography.heading4,
    color: Colors.textPrimary,
  },
  description: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: Spacing.md,
    paddingTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  statText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    fontWeight: '500',
  },
});
