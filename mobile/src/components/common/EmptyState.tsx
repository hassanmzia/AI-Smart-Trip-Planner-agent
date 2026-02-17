/**
 * Empty state placeholder component
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Colors, Typography, Spacing } from '../../utils/theme';
import { Button } from './Button';

interface EmptyStateProps {
  icon: string;
  title: string;
  subtitle?: string;
  actionTitle?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  subtitle,
  actionTitle,
  onAction,
}) => (
  <View style={styles.container}>
    <View style={styles.iconContainer}>
      <Icon name={icon} size={48} color={Colors.gray[300]} />
    </View>
    <Text style={styles.title}>{title}</Text>
    {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
    {actionTitle && onAction && (
      <Button
        title={actionTitle}
        onPress={onAction}
        variant="outline"
        size="sm"
        style={{ marginTop: Spacing.lg }}
      />
    )}
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing['3xl'],
    paddingVertical: Spacing['5xl'],
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: Colors.gray[100],
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  title: {
    ...Typography.heading4,
    color: Colors.gray[700],
    textAlign: 'center',
  },
  subtitle: {
    ...Typography.body,
    color: Colors.gray[400],
    textAlign: 'center',
    marginTop: Spacing.sm,
  },
});
