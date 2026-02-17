/**
 * Screen wrapper with safe area, scroll, and loading states
 */

import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  StatusBar,
  ViewStyle,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Colors, Spacing } from '../../utils/theme';

interface ScreenWrapperProps {
  children: React.ReactNode;
  scroll?: boolean;
  loading?: boolean;
  refreshing?: boolean;
  onRefresh?: () => void;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  edges?: ('top' | 'bottom' | 'left' | 'right')[];
  statusBarStyle?: 'light-content' | 'dark-content';
  backgroundColor?: string;
  keyboardAvoiding?: boolean;
  noPadding?: boolean;
}

export const ScreenWrapper: React.FC<ScreenWrapperProps> = ({
  children,
  scroll = true,
  loading = false,
  refreshing = false,
  onRefresh,
  style,
  contentStyle,
  edges = ['top', 'bottom'],
  statusBarStyle = 'dark-content',
  backgroundColor = Colors.background,
  keyboardAvoiding = false,
  noPadding = false,
}) => {
  const content = loading ? (
    <View style={styles.loadingContainer}>
      <ActivityIndicator size="large" color={Colors.primary[600]} />
    </View>
  ) : scroll ? (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={[
        !noPadding && styles.scrollContent,
        contentStyle,
      ]}
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="handled"
      refreshControl={
        onRefresh ? (
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={Colors.primary[600]}
            colors={[Colors.primary[600]]}
          />
        ) : undefined
      }
    >
      {children}
    </ScrollView>
  ) : (
    <View style={[styles.staticContent, !noPadding && styles.scrollContent, contentStyle]}>
      {children}
    </View>
  );

  const wrapper = (
    <SafeAreaView
      edges={edges}
      style={[styles.container, { backgroundColor }, style]}
    >
      <StatusBar barStyle={statusBarStyle} backgroundColor={backgroundColor} />
      {content}
    </SafeAreaView>
  );

  if (keyboardAvoiding) {
    return (
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        {wrapper}
      </KeyboardAvoidingView>
    );
  }

  return wrapper;
};

const styles = StyleSheet.create({
  flex: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing['3xl'],
  },
  staticContent: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
