/**
 * Hotel search results screen
 */

import React, { useState } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { HotelCard } from '../../components/cards/HotelCard';
import { EmptyState } from '../../components/common/EmptyState';
import { useSearchStore } from '../../store/searchStore';
import { Colors, Typography, Spacing } from '../../utils/theme';

type SortOption = 'score' | 'price' | 'rating' | 'stars';

export const HotelResultsScreen = ({ navigation, route }: any) => {
  const { hotelResults, isSearchingHotels } = useSearchStore();
  const [sortBy, setSortBy] = useState<SortOption>('score');
  const params = route?.params?.params;

  const sortedResults = [...hotelResults].sort((a, b) => {
    switch (sortBy) {
      case 'price': return a.price_per_night - b.price_per_night;
      case 'rating': return b.rating - a.rating;
      case 'stars': return b.stars - a.stars;
      case 'score':
        return (b.utility_score?.total_score || 0) - (a.utility_score?.total_score || 0);
      default: return 0;
    }
  });

  const sortOptions: { key: SortOption; label: string; icon: string }[] = [
    { key: 'score', label: 'AI Score', icon: 'auto-awesome' },
    { key: 'price', label: 'Price', icon: 'attach-money' },
    { key: 'rating', label: 'Rating', icon: 'star' },
    { key: 'stars', label: 'Stars', icon: 'hotel' },
  ];

  return (
    <ScreenWrapper scroll={false} noPadding loading={isSearchingHotels}>
      <View style={styles.header}>
        <Text style={styles.title}>Hotels in {params?.destination}</Text>
        <Text style={styles.subtitle}>{sortedResults.length} properties found</Text>
      </View>

      <View style={styles.sortBar}>
        {sortOptions.map((opt) => (
          <TouchableOpacity
            key={opt.key}
            style={[styles.sortBtn, sortBy === opt.key && styles.sortBtnActive]}
            onPress={() => setSortBy(opt.key)}
          >
            <Icon name={opt.icon} size={14} color={sortBy === opt.key ? Colors.white : Colors.gray[500]} />
            <Text style={[styles.sortText, sortBy === opt.key && styles.sortTextActive]}>
              {opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={sortedResults}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <HotelCard
            hotel={item}
            onPress={() => navigation.navigate('HotelDetail', { hotel: item })}
          />
        )}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <EmptyState
            icon="hotel"
            title="No Hotels Found"
            subtitle="Try different dates or destination"
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
