/**
 * Professional text input with icons, validation, and animations
 */

import React, { useState, useRef } from 'react';
import {
  View,
  TextInput,
  Text,
  StyleSheet,
  Animated,
  TouchableOpacity,
  TextInputProps,
  ViewStyle,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { Colors, Typography, BorderRadius, Spacing } from '../../utils/theme';

interface InputProps extends TextInputProps {
  label?: string;
  icon?: string;
  rightIcon?: string;
  onRightIconPress?: () => void;
  error?: string;
  hint?: string;
  containerStyle?: ViewStyle;
}

export const Input: React.FC<InputProps> = ({
  label,
  icon,
  rightIcon,
  onRightIconPress,
  error,
  hint,
  containerStyle,
  ...textInputProps
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const borderAnim = useRef(new Animated.Value(0)).current;

  const handleFocus = (e: any) => {
    setIsFocused(true);
    Animated.timing(borderAnim, {
      toValue: 1,
      duration: 200,
      useNativeDriver: false,
    }).start();
    textInputProps.onFocus?.(e);
  };

  const handleBlur = (e: any) => {
    setIsFocused(false);
    Animated.timing(borderAnim, {
      toValue: 0,
      duration: 200,
      useNativeDriver: false,
    }).start();
    textInputProps.onBlur?.(e);
  };

  const borderColor = borderAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [
      error ? Colors.error.main : Colors.gray[200],
      error ? Colors.error.main : Colors.primary[500],
    ],
  });

  return (
    <View style={[styles.container, containerStyle]}>
      {label && (
        <Text style={[styles.label, error && styles.labelError]}>{label}</Text>
      )}
      <Animated.View
        style={[
          styles.inputContainer,
          { borderColor },
          isFocused && styles.inputFocused,
          error && styles.inputError,
        ]}
      >
        {icon && (
          <Icon
            name={icon}
            size={20}
            color={isFocused ? Colors.primary[500] : Colors.gray[400]}
            style={styles.leftIcon}
          />
        )}
        <TextInput
          {...textInputProps}
          style={[
            styles.input,
            icon && styles.inputWithLeftIcon,
            rightIcon && styles.inputWithRightIcon,
            textInputProps.style,
          ]}
          placeholderTextColor={Colors.gray[400]}
          onFocus={handleFocus}
          onBlur={handleBlur}
        />
        {rightIcon && (
          <TouchableOpacity
            onPress={onRightIconPress}
            style={styles.rightIcon}
            hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
          >
            <Icon
              name={rightIcon}
              size={20}
              color={Colors.gray[400]}
            />
          </TouchableOpacity>
        )}
      </Animated.View>
      {error && (
        <View style={styles.errorRow}>
          <Icon name="error-outline" size={14} color={Colors.error.main} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
      {hint && !error && <Text style={styles.hintText}>{hint}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: Spacing.base,
  },
  label: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.gray[700],
    marginBottom: Spacing.xs,
  },
  labelError: {
    color: Colors.error.main,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.gray[50],
    borderWidth: 1.5,
    borderColor: Colors.gray[200],
    borderRadius: BorderRadius.md,
    overflow: 'hidden',
  },
  inputFocused: {
    backgroundColor: Colors.white,
  },
  inputError: {
    borderColor: Colors.error.main,
    backgroundColor: Colors.error.light + '20',
  },
  input: {
    flex: 1,
    ...Typography.body,
    color: Colors.textPrimary,
    paddingVertical: 14,
    paddingHorizontal: Spacing.base,
  },
  inputWithLeftIcon: {
    paddingLeft: 0,
  },
  inputWithRightIcon: {
    paddingRight: 0,
  },
  leftIcon: {
    marginLeft: Spacing.base,
    marginRight: Spacing.sm,
  },
  rightIcon: {
    padding: Spacing.base,
  },
  errorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  errorText: {
    ...Typography.caption,
    color: Colors.error.main,
    marginLeft: 4,
  },
  hintText: {
    ...Typography.caption,
    color: Colors.gray[400],
    marginTop: 4,
  },
});
