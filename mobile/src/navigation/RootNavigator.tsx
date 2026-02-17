/**
 * Root navigator - handles auth state and main app navigation
 */

import React, { useEffect } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { useAuthStore } from '../store/authStore';
import { AuthNavigator } from './AuthNavigator';
import { MainTabNavigator } from './MainTabNavigator';
import { FlightSearchScreen } from '../screens/flights/FlightSearchScreen';
import { FlightResultsScreen } from '../screens/flights/FlightResultsScreen';
import { HotelSearchScreen } from '../screens/hotels/HotelSearchScreen';
import { HotelResultsScreen } from '../screens/hotels/HotelResultsScreen';
import { AIPlannerScreen } from '../screens/home/AIPlannerScreen';
import { NotificationsScreen } from '../screens/notifications/NotificationsScreen';
import { Colors, Typography } from '../utils/theme';
import type { RootStackParamList } from '../types';

const Stack = createNativeStackNavigator<RootStackParamList>();

export const RootNavigator = () => {
  const { isAuthenticated, isLoading, restoreSession } = useAuthStore();

  useEffect(() => {
    restoreSession();
  }, []);

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={Colors.primary[600]} />
      </View>
    );
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerBackTitleVisible: false,
        headerTintColor: Colors.primary[600],
        headerTitleStyle: {
          ...Typography.heading4,
          color: Colors.textPrimary,
        },
        headerShadowVisible: false,
        headerStyle: {
          backgroundColor: Colors.background,
        },
      }}
    >
      {!isAuthenticated ? (
        <Stack.Screen
          name="Auth"
          component={AuthNavigator}
          options={{ headerShown: false }}
        />
      ) : (
        <>
          <Stack.Screen
            name="Main"
            component={MainTabNavigator}
            options={{ headerShown: false }}
          />
          <Stack.Screen
            name="FlightSearch"
            component={FlightSearchScreen}
            options={{ title: 'Search Flights' }}
          />
          <Stack.Screen
            name="FlightResults"
            component={FlightResultsScreen}
            options={{ title: 'Flight Results' }}
          />
          <Stack.Screen
            name="HotelSearch"
            component={HotelSearchScreen}
            options={{ title: 'Search Hotels' }}
          />
          <Stack.Screen
            name="HotelResults"
            component={HotelResultsScreen}
            options={{ title: 'Hotel Results' }}
          />
          <Stack.Screen
            name="AIPlanner"
            component={AIPlannerScreen}
            options={{ title: 'AI Trip Planner' }}
          />
          <Stack.Screen
            name="Weather"
            component={require('../screens/explore/ExploreScreen').ExploreScreen}
            options={{ title: 'Weather' }}
          />
          <Stack.Screen
            name="Safety"
            component={require('../screens/explore/ExploreScreen').ExploreScreen}
            options={{ title: 'Safety Info' }}
          />
          <Stack.Screen
            name="NotificationsScreen"
            component={NotificationsScreen}
            options={{ title: 'Notifications' }}
          />
        </>
      )}
    </Stack.Navigator>
  );
};

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
  },
});
