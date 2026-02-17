/**
 * Badge/chip component for status labels, tags, and scores
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Colors, Typography, BorderRadius, Spacing } from '../../utils/theme';

type BadgeVariant = 'excellent' | 'good' | 'fair' | 'poor' | 'info' | 'warning' | 'success' | 'error' | 'neutral';

interface BadgeProps {
  label: string;
  variant?: BadgeVariant;
  icon?: string;
  size?: 'sm' | 'md';
  style?: ViewStyle;
}

const variantColors: Record<BadgeVariant, { bg: string; text: string }> = {
  excellent: { bg: '#DCFCE7', text: '#15803D' },
  good: { bg: '#DBEAFE', text: '#1D4ED8' },
  fair: { bg: '#FEF9C3', text: '#A16207' },
  poor: { bg: '#FEE2E2', text: '#B91C1C' },
  info: { bg: Colors.primary[100], text: Colors.primary[700] },
  warning: { bg: Colors.warning.light, text: Colors.warning.dark },
  success: { bg: Colors.success.light, text: Colors.success.dark },
  error: { bg: Colors.error.light, text: Colors.error.dark },
  neutral: { bg: Colors.gray[100], text: Colors.gray[700] },
};

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'neutral',
  icon,
  size = 'sm',
  style,
}) => {
  const colors = variantColors[variant];
  const isSmall = size === 'sm';

  return (
    <View
      style={[
        styles.badge,
        {
          backgroundColor: colors.bg,
          paddingVertical: isSmall ? 3 : 6,
          paddingHorizontal: isSmall ? 8 : 12,
        },
        style,
      ]}
    >
      {icon && (
        <Icon
          name={icon}
          size={isSmall ? 12 : 14}
          color={colors.text}
          style={{ marginRight: 4 }}
        />
      )}
      <Text
        style={[
          styles.text,
          {
            color: colors.text,
            fontSize: isSmall ? 11 : 13,
          },
        ]}
      >
        {label}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: BorderRadius.full,
    alignSelf: 'flex-start',
  },
  text: {
    fontWeight: '600',
    letterSpacing: 0.3,
  },
});
