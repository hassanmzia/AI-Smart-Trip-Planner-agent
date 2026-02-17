/**
 * Professional button component with multiple variants
 */

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
  View,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Colors, Typography, BorderRadius, Spacing, Shadows } from '../../utils/theme';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'gradient';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: string;
  iconRight?: string;
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'md',
  icon,
  iconRight,
  loading = false,
  disabled = false,
  fullWidth = false,
  style,
  textStyle,
}) => {
  const isDisabled = disabled || loading;

  const sizeStyles = {
    sm: { paddingVertical: 8, paddingHorizontal: 16, fontSize: 13, iconSize: 16 },
    md: { paddingVertical: 14, paddingHorizontal: 24, fontSize: 16, iconSize: 20 },
    lg: { paddingVertical: 18, paddingHorizontal: 32, fontSize: 18, iconSize: 22 },
  }[size];

  const getVariantStyles = (): { container: ViewStyle; text: TextStyle } => {
    switch (variant) {
      case 'primary':
        return {
          container: {
            backgroundColor: Colors.primary[600],
            ...Shadows.md,
            ...(Shadows.colored(Colors.primary[600]) as any),
          },
          text: { color: Colors.white },
        };
      case 'secondary':
        return {
          container: {
            backgroundColor: Colors.secondary[600],
            ...Shadows.md,
          },
          text: { color: Colors.white },
        };
      case 'outline':
        return {
          container: {
            backgroundColor: 'transparent',
            borderWidth: 1.5,
            borderColor: Colors.primary[600],
          },
          text: { color: Colors.primary[600] },
        };
      case 'ghost':
        return {
          container: { backgroundColor: 'transparent' },
          text: { color: Colors.primary[600] },
        };
      case 'danger':
        return {
          container: { backgroundColor: Colors.error.main, ...Shadows.md },
          text: { color: Colors.white },
        };
      case 'gradient':
        return {
          container: { ...Shadows.lg },
          text: { color: Colors.white },
        };
      default:
        return {
          container: { backgroundColor: Colors.primary[600] },
          text: { color: Colors.white },
        };
    }
  };

  const variantStyles = getVariantStyles();

  const buttonContent = (
    <View style={styles.content}>
      {loading ? (
        <ActivityIndicator
          color={variantStyles.text.color}
          size="small"
          style={{ marginRight: Spacing.sm }}
        />
      ) : icon ? (
        <Icon
          name={icon}
          size={sizeStyles.iconSize}
          color={variantStyles.text.color as string}
          style={{ marginRight: Spacing.sm }}
        />
      ) : null}
      <Text
        style={[
          styles.text,
          { fontSize: sizeStyles.fontSize },
          variantStyles.text,
          textStyle,
        ]}
      >
        {title}
      </Text>
      {iconRight && !loading ? (
        <Icon
          name={iconRight}
          size={sizeStyles.iconSize}
          color={variantStyles.text.color as string}
          style={{ marginLeft: Spacing.sm }}
        />
      ) : null}
    </View>
  );

  if (variant === 'gradient') {
    return (
      <TouchableOpacity
        onPress={onPress}
        disabled={isDisabled}
        activeOpacity={0.8}
        style={[fullWidth && styles.fullWidth, style]}
      >
        <LinearGradient
          colors={[Colors.primary[500], Colors.primary[700]]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={[
            styles.button,
            {
              paddingVertical: sizeStyles.paddingVertical,
              paddingHorizontal: sizeStyles.paddingHorizontal,
            },
            variantStyles.container,
            isDisabled && styles.disabled,
          ]}
        >
          {buttonContent}
        </LinearGradient>
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
      style={[
        styles.button,
        {
          paddingVertical: sizeStyles.paddingVertical,
          paddingHorizontal: sizeStyles.paddingHorizontal,
        },
        variantStyles.container,
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        style,
      ]}
    >
      {buttonContent}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    ...Typography.button,
  },
  fullWidth: {
    width: '100%',
  },
  disabled: {
    opacity: 0.5,
  },
});
