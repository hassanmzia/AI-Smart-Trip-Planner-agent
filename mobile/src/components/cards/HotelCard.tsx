/**
 * Hotel result card with image, rating, amenities, and AI utility score
 */

import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import type { Hotel } from '../../types';

interface HotelCardProps {
  hotel: Hotel;
  onPress: () => void;
  nights?: number;
}

export const HotelCard: React.FC<HotelCardProps> = ({ hotel, onPress, nights = 1 }) => {
  const renderStars = () => {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        <Icon
          key={i}
          name={i < hotel.stars ? 'star' : 'star-border'}
          size={14}
          color={i < hotel.stars ? '#F59E0B' : Colors.gray[300]}
        />,
      );
    }
    return stars;
  };

  const placeholderImage = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400';

  return (
    <Card variant="elevated" onPress={onPress} style={styles.card} padding={0}>
      {/* Image */}
      <View style={styles.imageContainer}>
        <Image
          source={{ uri: hotel.images?.[0] || placeholderImage }}
          style={styles.image}
          resizeMode="cover"
        />
        {hotel.utility_score && (
          <View style={styles.scoreBadge}>
            <Icon name="auto-awesome" size={12} color={Colors.white} />
            <Text style={styles.scoreText}>
              {Math.round(hotel.utility_score.total_score * 100)}%
            </Text>
          </View>
        )}
      </View>

      {/* Content */}
      <View style={styles.content}>
        <View style={styles.headerRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.name} numberOfLines={1}>{hotel.name}</Text>
            <View style={styles.starsRow}>{renderStars()}</View>
          </View>
          <View style={styles.ratingBadge}>
            <Text style={styles.ratingText}>{hotel.rating.toFixed(1)}</Text>
          </View>
        </View>

        <View style={styles.locationRow}>
          <Icon name="location-on" size={14} color={Colors.gray[400]} />
          <Text style={styles.location} numberOfLines={1}>
            {hotel.city}, {hotel.country}
          </Text>
          {hotel.distance_from_center && (
            <Text style={styles.distance}>
              {hotel.distance_from_center.toFixed(1)} km from center
            </Text>
          )}
        </View>

        {/* Amenities */}
        <View style={styles.amenitiesRow}>
          {hotel.amenities?.slice(0, 4).map((amenity, i) => (
            <Badge key={i} label={amenity} variant="neutral" size="sm" />
          ))}
          {hotel.amenities?.length > 4 && (
            <Badge label={`+${hotel.amenities.length - 4}`} variant="info" size="sm" />
          )}
        </View>

        {/* Price */}
        <View style={styles.priceRow}>
          <View>
            <Text style={styles.price}>
              ${hotel.price_per_night.toLocaleString()}
            </Text>
            <Text style={styles.priceLabel}>per night</Text>
          </View>
          {nights > 1 && (
            <Text style={styles.totalPrice}>
              ${(hotel.price_per_night * nights).toLocaleString()} total
            </Text>
          )}
          {hotel.utility_score && (
            <Badge
              label={hotel.utility_score.recommendation}
              variant={hotel.utility_score.recommendation}
            />
          )}
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
    height: 160,
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  scoreBadge: {
    position: 'absolute',
    top: Spacing.sm,
    right: Spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.primary[600],
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: BorderRadius.full,
    gap: 4,
  },
  scoreText: {
    color: Colors.white,
    fontWeight: '700',
    fontSize: 12,
  },
  content: {
    padding: Spacing.base,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  name: {
    ...Typography.heading4,
    color: Colors.textPrimary,
  },
  starsRow: {
    flexDirection: 'row',
    marginTop: 2,
  },
  ratingBadge: {
    backgroundColor: Colors.primary[600],
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
    marginLeft: Spacing.sm,
  },
  ratingText: {
    color: Colors.white,
    fontWeight: '700',
    fontSize: 14,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.sm,
    gap: 4,
  },
  location: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    flex: 1,
  },
  distance: {
    ...Typography.caption,
    color: Colors.textTertiary,
  },
  amenitiesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: Spacing.md,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginTop: Spacing.md,
    paddingTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
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
  totalPrice: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
});
