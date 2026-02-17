/**
 * Versatile card component with variants
 */

import React from 'react';
import {
  View,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
} from 'react-native';
import { Colors, BorderRadius, Spacing, Shadows } from '../../utils/theme';

interface CardProps {
  children: React.ReactNode;
  onPress?: () => void;
  variant?: 'default' | 'elevated' | 'outlined' | 'flat';
  style?: ViewStyle;
  padding?: number;
}

export const Card: React.FC<CardProps> = ({
  children,
  onPress,
  variant = 'default',
  style,
  padding = Spacing.base,
}) => {
  const variantStyles: Record<string, ViewStyle> = {
    default: {
      backgroundColor: Colors.surface,
      ...Shadows.sm,
    },
    elevated: {
      backgroundColor: Colors.surface,
      ...Shadows.lg,
    },
    outlined: {
      backgroundColor: Colors.surface,
      borderWidth: 1,
      borderColor: Colors.border,
    },
    flat: {
      backgroundColor: Colors.gray[50],
    },
  };

  const cardStyle = [
    styles.card,
    variantStyles[variant],
    { padding },
    style,
  ];

  if (onPress) {
    return (
      <TouchableOpacity
        onPress={onPress}
        activeOpacity={0.7}
        style={cardStyle}
      >
        {children}
      </TouchableOpacity>
    );
  }

  return <View style={cardStyle}>{children}</View>;
};

const styles = StyleSheet.create({
  card: {
    borderRadius: BorderRadius.lg,
    overflow: 'hidden',
  },
});
