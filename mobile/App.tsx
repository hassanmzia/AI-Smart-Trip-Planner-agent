/**
 * AI Smart Trip Planner - React Native Mobile App
 *
 * Cross-platform (iOS + Android) companion app for the
 * AI-powered travel planning platform.
 */

import React from 'react';
import { StatusBar, LogBox } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import Toast from 'react-native-toast-message';
import { RootNavigator } from './src/navigation/RootNavigator';
import { Colors } from './src/utils/theme';

// Suppress known harmless warnings in development
LogBox.ignoreLogs([
  'ViewPropTypes will be removed',
  'ColorPropType will be removed',
]);

const App = () => {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <NavigationContainer
          theme={{
            dark: false,
            colors: {
              primary: Colors.primary[600],
              background: Colors.background,
              card: Colors.surface,
              text: Colors.textPrimary,
              border: Colors.border,
              notification: Colors.error.main,
            },
          }}
        >
          <StatusBar
            barStyle="dark-content"
            backgroundColor={Colors.background}
          />
          <RootNavigator />
        </NavigationContainer>
        <Toast />
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
};

export default App;
