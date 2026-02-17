/**
 * Explore screen - discover restaurants, attractions, events, and more
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Card } from '../../components/common/Card';
import { Input } from '../../components/common/Input';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../utils/theme';

const { width } = Dimensions.get('window');

const CATEGORIES = [
  { icon: 'restaurant', label: 'Restaurants', color: '#F97316', desc: 'Local dining' },
  { icon: 'photo-camera', label: 'Attractions', color: '#22C55E', desc: 'Must-see places' },
  { icon: 'event', label: 'Events', color: '#8B5CF6', desc: 'Happening now' },
  { icon: 'directions-car', label: 'Car Rental', color: '#EC4899', desc: 'Get around' },
  { icon: 'shopping-bag', label: 'Shopping', color: '#06B6D4', desc: 'Retail therapy' },
  { icon: 'cloud', label: 'Weather', color: '#3B82F6', desc: 'Forecast' },
  { icon: 'security', label: 'Safety', color: '#EF4444', desc: 'Travel advisory' },
  { icon: 'directions-bus', label: 'Commute', color: '#14B8A6', desc: 'Transport info' },
];

export const ExploreScreen = ({ navigation }: any) => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <ScreenWrapper scroll>
      <Text style={styles.title}>Explore</Text>
      <Text style={styles.subtitle}>Discover amazing places & activities</Text>

      <Input
        icon="search"
        placeholder="Search destination..."
        value={searchQuery}
        onChangeText={setSearchQuery}
      />

      {/* Category Grid */}
      <View style={styles.grid}>
        {CATEGORIES.map((cat) => (
          <TouchableOpacity
            key={cat.label}
            style={styles.categoryCard}
            onPress={() => {
              if (cat.label === 'Weather') navigation.navigate('Weather', {});
              else if (cat.label === 'Safety') navigation.navigate('Safety', {});
            }}
            activeOpacity={0.7}
          >
            <LinearGradient
              colors={[cat.color + '15', cat.color + '08']}
              style={styles.categoryGradient}
            >
              <View style={[styles.categoryIcon, { backgroundColor: cat.color + '20' }]}>
                <Icon name={cat.icon} size={28} color={cat.color} />
              </View>
              <Text style={styles.categoryLabel}>{cat.label}</Text>
              <Text style={styles.categoryDesc}>{cat.desc}</Text>
            </LinearGradient>
          </TouchableOpacity>
        ))}
      </View>

      {/* Quick Tips */}
      <Card variant="flat" style={styles.tipCard}>
        <View style={styles.tipHeader}>
          <Icon name="lightbulb" size={22} color={Colors.warning.main} />
          <Text style={styles.tipTitle}>Travel Tip</Text>
        </View>
        <Text style={styles.tipText}>
          Use our AI Trip Planner to automatically discover restaurants and attractions at
          your destination. It creates a day-by-day plan with activities, dining, and more!
        </Text>
        <TouchableOpacity
          style={styles.tipButton}
          onPress={() => navigation.navigate('AIPlanner')}
        >
          <Text style={styles.tipButtonText}>Try AI Planner</Text>
          <Icon name="arrow-forward" size={16} color={Colors.primary[600]} />
        </TouchableOpacity>
      </Card>
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  title: {
    ...Typography.heading2,
    color: Colors.textPrimary,
    marginTop: Spacing.md,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.textSecondary,
    marginBottom: Spacing.lg,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
    marginTop: Spacing.sm,
  },
  categoryCard: {
    width: (width - Spacing.screenPadding * 2 - Spacing.md) / 2,
    borderRadius: BorderRadius.xl,
    overflow: 'hidden',
    ...Shadows.sm,
  },
  categoryGradient: {
    padding: Spacing.base,
    minHeight: 120,
    justifyContent: 'center',
  },
  categoryIcon: {
    width: 48,
    height: 48,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  categoryLabel: {
    ...Typography.heading4,
    color: Colors.textPrimary,
    fontSize: 16,
  },
  categoryDesc: {
    ...Typography.caption,
    color: Colors.textTertiary,
    marginTop: 2,
  },
  tipCard: {
    marginTop: Spacing.xl,
    padding: Spacing.base,
  },
  tipHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  tipTitle: {
    ...Typography.heading4,
    color: Colors.textPrimary,
  },
  tipText: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    lineHeight: 20,
  },
  tipButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: Spacing.md,
  },
  tipButtonText: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.primary[600],
  },
});
