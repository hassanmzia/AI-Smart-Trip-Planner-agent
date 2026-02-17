/**
 * Itineraries list screen (Trips tab)
 */

import React, { useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { ItineraryCard } from '../../components/cards/ItineraryCard';
import { EmptyState } from '../../components/common/EmptyState';
import { Button } from '../../components/common/Button';
import { itineraryService } from '../../services/itineraryService';
import { Colors, Typography, Spacing } from '../../utils/theme';
import type { Itinerary } from '../../types';

export const ItinerariesScreen = ({ navigation }: any) => {
  const [itineraries, setItineraries] = useState<Itinerary[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchItineraries = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    try {
      const data = await itineraryService.list();
      setItineraries(data.results || []);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchItineraries();
    }, []),
  );

  return (
    <ScreenWrapper scroll={false} noPadding loading={loading}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>My Trips</Text>
          <Text style={styles.subtitle}>{itineraries.length} itineraries</Text>
        </View>
        <Button
          title="New Trip"
          onPress={() => navigation.navigate('CreateItinerary')}
          variant="primary"
          size="sm"
          icon="add"
        />
      </View>

      <FlatList
        data={itineraries}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <ItineraryCard
            itinerary={item}
            onPress={() => navigation.navigate('ItineraryDetail', { itineraryId: item.id })}
          />
        )}
        contentContainerStyle={styles.list}
        refreshing={refreshing}
        onRefresh={() => fetchItineraries(true)}
        ListEmptyComponent={
          <EmptyState
            icon="map"
            title="No Trips Yet"
            subtitle="Create your first trip itinerary"
            actionTitle="Plan a Trip"
            onAction={() => navigation.navigate('AIPlanner')}
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
  subtitle: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
  },
  list: {
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing['3xl'],
  },
});
