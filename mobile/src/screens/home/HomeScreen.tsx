/**
 * Home screen - hero banner, quick actions, AI planner, and recent trips
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  Image,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { useAuthStore } from '../../store/authStore';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../utils/theme';

const { width } = Dimensions.get('window');

const QUICK_ACTIONS = [
  { icon: 'flight', label: 'Flights', color: Colors.primary[500], route: 'FlightSearch' },
  { icon: 'hotel', label: 'Hotels', color: Colors.secondary[500], route: 'HotelSearch' },
  { icon: 'auto-awesome', label: 'AI Planner', color: '#F97316', route: 'AIPlanner' },
  { icon: 'map', label: 'Explore', color: Colors.success.main, route: 'ExploreTab' },
];

const POPULAR_DESTINATIONS = [
  { name: 'Paris', country: 'France', image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300', price: 450 },
  { name: 'Tokyo', country: 'Japan', image: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300', price: 680 },
  { name: 'Bali', country: 'Indonesia', image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=300', price: 520 },
  { name: 'New York', country: 'USA', image: 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=300', price: 320 },
];

export const HomeScreen = ({ navigation }: any) => {
  const { user } = useAuthStore();
  const firstName = user?.first_name || 'Traveler';

  return (
    <ScreenWrapper scroll noPadding edges={['bottom']}>
      {/* Hero */}
      <LinearGradient
        colors={Colors.gradient.hero}
        start={{ x: 0, y: 0 }}
        end={{ x: 0.5, y: 1 }}
        style={styles.hero}
      >
        {/* Top bar */}
        <View style={styles.topBar}>
          <View>
            <Text style={styles.greeting}>Hello, {firstName}</Text>
            <Text style={styles.tagline}>Where to next?</Text>
          </View>
          <TouchableOpacity
            onPress={() => navigation.navigate('NotificationsScreen')}
            style={styles.notifButton}
          >
            <Icon name="notifications-none" size={26} color={Colors.white} />
          </TouchableOpacity>
        </View>

        {/* Search box */}
        <TouchableOpacity
          style={styles.searchBox}
          activeOpacity={0.9}
          onPress={() => navigation.navigate('FlightSearch')}
        >
          <Icon name="search" size={22} color={Colors.gray[400]} />
          <Text style={styles.searchPlaceholder}>Search flights, hotels, destinations...</Text>
        </TouchableOpacity>

        {/* Decorative */}
        <View style={styles.heroCircle1} />
        <View style={styles.heroCircle2} />
      </LinearGradient>

      <View style={styles.content}>
        {/* Quick Actions */}
        <View style={styles.quickActions}>
          {QUICK_ACTIONS.map((action) => (
            <TouchableOpacity
              key={action.label}
              style={styles.quickAction}
              onPress={() => navigation.navigate(action.route)}
              activeOpacity={0.7}
            >
              <View style={[styles.quickActionIcon, { backgroundColor: action.color + '15' }]}>
                <Icon name={action.icon} size={26} color={action.color} />
              </View>
              <Text style={styles.quickActionLabel}>{action.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* AI Trip Planner Banner */}
        <TouchableOpacity
          activeOpacity={0.85}
          onPress={() => navigation.navigate('AIPlanner')}
        >
          <LinearGradient
            colors={Colors.gradient.sunset}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.aiBanner}
          >
            <View style={styles.aiBannerContent}>
              <Icon name="auto-awesome" size={28} color={Colors.white} />
              <View style={{ flex: 1, marginLeft: Spacing.md }}>
                <Text style={styles.aiBannerTitle}>AI Trip Planner</Text>
                <Text style={styles.aiBannerSubtitle}>
                  Tell our AI where you want to go and get a personalized itinerary
                </Text>
              </View>
              <Icon name="arrow-forward-ios" size={18} color="rgba(255,255,255,0.7)" />
            </View>
          </LinearGradient>
        </TouchableOpacity>

        {/* Popular Destinations */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Popular Destinations</Text>
            <TouchableOpacity onPress={() => navigation.navigate('ExploreTab')}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>

          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.destinationScroll}>
            {POPULAR_DESTINATIONS.map((dest) => (
              <TouchableOpacity
                key={dest.name}
                style={styles.destinationCard}
                activeOpacity={0.8}
                onPress={() => navigation.navigate('HotelSearch')}
              >
                <Image source={{ uri: dest.image }} style={styles.destImage} />
                <LinearGradient
                  colors={['transparent', 'rgba(0,0,0,0.7)']}
                  style={styles.destGradient}
                >
                  <Text style={styles.destName}>{dest.name}</Text>
                  <Text style={styles.destCountry}>{dest.country}</Text>
                  <Text style={styles.destPrice}>From ${dest.price}</Text>
                </LinearGradient>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Features grid */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Discover More</Text>
          <View style={styles.featuresGrid}>
            {[
              { icon: 'restaurant', label: 'Restaurants', color: '#F97316', route: 'ExploreTab' },
              { icon: 'photo-camera', label: 'Attractions', color: '#22C55E', route: 'ExploreTab' },
              { icon: 'cloud', label: 'Weather', color: '#06B6D4', route: 'Weather' },
              { icon: 'security', label: 'Safety', color: '#EF4444', route: 'Safety' },
              { icon: 'event', label: 'Events', color: '#8B5CF6', route: 'ExploreTab' },
              { icon: 'directions-car', label: 'Car Rental', color: '#EC4899', route: 'ExploreTab' },
            ].map((item) => (
              <TouchableOpacity
                key={item.label}
                style={styles.featureItem}
                onPress={() => navigation.navigate(item.route)}
                activeOpacity={0.7}
              >
                <View style={[styles.featureIcon, { backgroundColor: item.color + '12' }]}>
                  <Icon name={item.icon} size={24} color={item.color} />
                </View>
                <Text style={styles.featureLabel}>{item.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  hero: {
    paddingTop: 60,
    paddingBottom: Spacing['3xl'],
    paddingHorizontal: Spacing.screenPadding,
    overflow: 'hidden',
  },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.xl,
  },
  greeting: {
    ...Typography.body,
    color: 'rgba(255,255,255,0.8)',
  },
  tagline: {
    ...Typography.heading1,
    color: Colors.white,
    marginTop: 2,
  },
  notifButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.white,
    borderRadius: BorderRadius.lg,
    paddingHorizontal: Spacing.base,
    paddingVertical: 14,
    ...Shadows.lg,
    gap: Spacing.sm,
  },
  searchPlaceholder: {
    ...Typography.body,
    color: Colors.gray[400],
    flex: 1,
  },
  heroCircle1: {
    position: 'absolute',
    top: -30,
    right: -50,
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: 'rgba(255,255,255,0.06)',
  },
  heroCircle2: {
    position: 'absolute',
    bottom: 20,
    left: -30,
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: 'rgba(255,255,255,0.04)',
  },
  content: {
    paddingHorizontal: Spacing.screenPadding,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing['3xl'],
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: Spacing.xl,
  },
  quickAction: {
    alignItems: 'center',
    width: (width - Spacing.screenPadding * 2 - Spacing.md * 3) / 4,
  },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  quickActionLabel: {
    ...Typography.caption,
    color: Colors.textSecondary,
    fontWeight: '600',
  },
  aiBanner: {
    borderRadius: BorderRadius.xl,
    marginBottom: Spacing.xl,
    ...Shadows.lg,
  },
  aiBannerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.lg,
  },
  aiBannerTitle: {
    ...Typography.heading4,
    color: Colors.white,
  },
  aiBannerSubtitle: {
    ...Typography.bodySmall,
    color: 'rgba(255,255,255,0.85)',
    marginTop: 2,
  },
  section: {
    marginBottom: Spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  sectionTitle: {
    ...Typography.heading3,
    color: Colors.textPrimary,
  },
  seeAll: {
    ...Typography.bodySmall,
    color: Colors.primary[600],
    fontWeight: '600',
  },
  destinationScroll: {
    marginHorizontal: -Spacing.screenPadding,
    paddingHorizontal: Spacing.screenPadding,
  },
  destinationCard: {
    width: 180,
    height: 220,
    borderRadius: BorderRadius.xl,
    overflow: 'hidden',
    marginRight: Spacing.md,
    ...Shadows.md,
  },
  destImage: {
    width: '100%',
    height: '100%',
  },
  destGradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: Spacing.md,
    paddingTop: Spacing['3xl'],
  },
  destName: {
    ...Typography.heading4,
    color: Colors.white,
  },
  destCountry: {
    ...Typography.bodySmall,
    color: 'rgba(255,255,255,0.8)',
  },
  destPrice: {
    ...Typography.bodySmall,
    color: Colors.white,
    fontWeight: '700',
    marginTop: 4,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
    marginTop: Spacing.md,
  },
  featureItem: {
    width: (width - Spacing.screenPadding * 2 - Spacing.md * 2) / 3,
    alignItems: 'center',
    paddingVertical: Spacing.base,
  },
  featureIcon: {
    width: 52,
    height: 52,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  featureLabel: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    fontWeight: '500',
    textAlign: 'center',
  },
});
