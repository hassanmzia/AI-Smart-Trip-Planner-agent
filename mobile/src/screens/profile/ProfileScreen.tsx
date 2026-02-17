/**
 * Profile screen with user info, stats, and settings
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Alert } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { useAuthStore } from '../../store/authStore';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../utils/theme';

const MENU_ITEMS = [
  { icon: 'person', label: 'Edit Profile', route: 'EditProfile', color: Colors.primary[500] },
  { icon: 'credit-card', label: 'Payment Methods', route: null, color: Colors.secondary[500] },
  { icon: 'notifications', label: 'Notifications', route: 'NotificationsScreen', color: '#F97316' },
  { icon: 'favorite', label: 'Saved Places', route: null, color: '#EF4444' },
  { icon: 'history', label: 'Travel History', route: null, color: '#22C55E' },
  { icon: 'settings', label: 'Settings', route: 'Settings', color: Colors.gray[500] },
  { icon: 'help', label: 'Help & Support', route: null, color: '#06B6D4' },
];

export const ProfileScreen = ({ navigation }: any) => {
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: () => logout() },
    ]);
  };

  const initials = `${user?.first_name?.[0] || ''}${user?.last_name?.[0] || ''}`.toUpperCase();

  return (
    <ScreenWrapper scroll>
      {/* Profile Header */}
      <View style={styles.profileHeader}>
        <LinearGradient
          colors={Colors.gradient.primary}
          style={styles.avatarContainer}
        >
          {user?.profile?.avatar ? (
            <Image source={{ uri: user.profile.avatar }} style={styles.avatar} />
          ) : (
            <Text style={styles.initials}>{initials}</Text>
          )}
        </LinearGradient>
        <Text style={styles.name}>
          {user?.first_name} {user?.last_name}
        </Text>
        <Text style={styles.email}>{user?.email}</Text>
        {user?.profile && (
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{user.profile.total_trips || 0}</Text>
              <Text style={styles.statLabel}>Trips</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.stat}>
              <Text style={styles.statValue}>{user.profile.total_bookings || 0}</Text>
              <Text style={styles.statLabel}>Bookings</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.stat}>
              <Text style={styles.statValue}>
                ${(user.profile.total_spent || 0).toLocaleString()}
              </Text>
              <Text style={styles.statLabel}>Spent</Text>
            </View>
          </View>
        )}
      </View>

      {/* Menu Items */}
      <Card variant="elevated" style={styles.menuCard} padding={0}>
        {MENU_ITEMS.map((item, index) => (
          <TouchableOpacity
            key={item.label}
            style={[
              styles.menuItem,
              index < MENU_ITEMS.length - 1 && styles.menuItemBorder,
            ]}
            onPress={() => item.route && navigation.navigate(item.route)}
            activeOpacity={0.6}
          >
            <View style={[styles.menuIcon, { backgroundColor: item.color + '15' }]}>
              <Icon name={item.icon} size={20} color={item.color} />
            </View>
            <Text style={styles.menuLabel}>{item.label}</Text>
            <Icon name="chevron-right" size={22} color={Colors.gray[300]} />
          </TouchableOpacity>
        ))}
      </Card>

      {/* Sign Out */}
      <Button
        title="Sign Out"
        onPress={handleLogout}
        variant="outline"
        fullWidth
        icon="logout"
        style={{ marginTop: Spacing.xl, borderColor: Colors.error.main }}
        textStyle={{ color: Colors.error.main }}
      />

      {/* App version */}
      <Text style={styles.version}>AI Trip Planner v1.0.0</Text>
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  profileHeader: {
    alignItems: 'center',
    paddingVertical: Spacing.xl,
  },
  avatarContainer: {
    width: 88,
    height: 88,
    borderRadius: 44,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.md,
    ...Shadows.lg,
  },
  avatar: {
    width: 84,
    height: 84,
    borderRadius: 42,
    borderWidth: 3,
    borderColor: Colors.white,
  },
  initials: {
    fontSize: 32,
    fontWeight: '700',
    color: Colors.white,
  },
  name: {
    ...Typography.heading3,
    color: Colors.textPrimary,
  },
  email: {
    ...Typography.body,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.lg,
    backgroundColor: Colors.gray[50],
    borderRadius: BorderRadius.xl,
    paddingVertical: Spacing.base,
    paddingHorizontal: Spacing.xl,
  },
  stat: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    ...Typography.heading4,
    color: Colors.primary[700],
  },
  statLabel: {
    ...Typography.caption,
    color: Colors.textTertiary,
    marginTop: 2,
  },
  statDivider: {
    width: 1,
    height: 30,
    backgroundColor: Colors.gray[200],
    marginHorizontal: Spacing.base,
  },
  menuCard: {
    marginTop: Spacing.md,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: Spacing.base,
  },
  menuItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  menuIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  menuLabel: {
    ...Typography.body,
    fontWeight: '500',
    color: Colors.textPrimary,
    flex: 1,
  },
  version: {
    ...Typography.caption,
    color: Colors.textTertiary,
    textAlign: 'center',
    marginTop: Spacing.xl,
    marginBottom: Spacing.lg,
  },
});
