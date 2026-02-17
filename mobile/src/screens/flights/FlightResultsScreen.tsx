/**
 * Flight search results screen
 */

import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { FlightCard } from '../../components/cards/FlightCard';
import { EmptyState } from '../../components/common/EmptyState';
import { Badge } from '../../components/common/Badge';
import { useSearchStore } from '../../store/searchStore';
import { flightService } from '../../services/flightService';
import { Colors, Typography, Spacing } from '../../utils/theme';
import type { Flight } from '../../types';

type SortOption = 'price' | 'duration' | 'score' | 'stops';

export const FlightResultsScreen = ({ navigation, route }: any) => {
  const { flightResults, isSearchingFlights } = useSearchStore();
  const [sortBy, setSortBy] = useState<SortOption>('score');
  const params = route?.params?.params;

  const sortedResults = [...flightResults].sort((a, b) => {
    switch (sortBy) {
      case 'price': return a.price - b.price;
      case 'duration': return (a.duration_minutes || 0) - (b.duration_minutes || 0);
      case 'stops': return a.stops - b.stops;
      case 'score':
        return (b.goal_evaluation?.total_utility || 0) - (a.goal_evaluation?.total_utility || 0);
      default: return 0;
    }
  });

  const sortOptions: { key: SortOption; label: string; icon: string }[] = [
    { key: 'score', label: 'AI Score', icon: 'auto-awesome' },
    { key: 'price', label: 'Price', icon: 'attach-money' },
    { key: 'duration', label: 'Duration', icon: 'schedule' },
    { key: 'stops', label: 'Stops', icon: 'flight' },
  ];

  return (
    <ScreenWrapper scroll={false} noPadding loading={isSearchingFlights}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>
            {params?.origin} → {params?.destination}
          </Text>
          <Text style={styles.subtitle}>
            {sortedResults.length} flights found
          </Text>
        </View>
      </View>

      {/* Sort bar */}
      <View style={styles.sortBar}>
        {sortOptions.map((opt) => (
          <TouchableOpacity
            key={opt.key}
            style={[styles.sortBtn, sortBy === opt.key && styles.sortBtnActive]}
            onPress={() => setSortBy(opt.key)}
          >
            <Icon
              name={opt.icon}
              size={14}
              color={sortBy === opt.key ? Colors.white : Colors.gray[500]}
            />
            <Text style={[styles.sortText, sortBy === opt.key && styles.sortTextActive]}>
              {opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Results */}
      <FlatList
        data={sortedResults}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <FlightCard
            flight={item}
            onPress={() => navigation.navigate('FlightDetail', { flight: item })}
          />
        )}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <EmptyState
            icon="flight"
            title="No Flights Found"
            subtitle="Try different dates or destinations"
            actionTitle="Modify Search"
            onAction={() => navigation.goBack()}
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
    ...Typography.heading3,
    color: Colors.textPrimary,
  },
  subtitle: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  sortBar: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing.md,
    gap: Spacing.sm,
  },
  sortBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
    backgroundColor: Colors.gray[100],
    gap: 4,
  },
  sortBtnActive: {
    backgroundColor: Colors.primary[600],
  },
  sortText: {
    ...Typography.caption,
    color: Colors.gray[500],
    fontWeight: '600',
  },
  sortTextActive: {
    color: Colors.white,
  },
  list: {
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing['3xl'],
  },
});
