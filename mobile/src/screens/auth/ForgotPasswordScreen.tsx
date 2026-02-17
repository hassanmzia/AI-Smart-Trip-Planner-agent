/**
 * Forgot password screen
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { authService } from '../../services/authService';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import Toast from 'react-native-toast-message';

export const ForgotPasswordScreen = ({ navigation }: any) => {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) {
      Toast.show({ type: 'error', text1: 'Invalid Email', text2: 'Enter a valid email' });
      return;
    }
    setLoading(true);
    try {
      await authService.forgotPassword(email.trim());
      setSent(true);
    } catch {
      // Show success anyway (don't reveal if email exists)
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenWrapper scroll keyboardAvoiding backgroundColor={Colors.white}>
      <TouchableOpacity
        onPress={() => navigation.goBack()}
        style={styles.backButton}
      >
        <Icon name="arrow-back" size={24} color={Colors.textPrimary} />
      </TouchableOpacity>

      {sent ? (
        <View style={styles.successContainer}>
          <View style={styles.successIcon}>
            <Icon name="mark-email-read" size={48} color={Colors.primary[600]} />
          </View>
          <Text style={styles.title}>Check Your Email</Text>
          <Text style={styles.subtitle}>
            We've sent a password reset link to{'\n'}
            <Text style={{ fontWeight: '600' }}>{email}</Text>
          </Text>
          <Button
            title="Back to Login"
            onPress={() => navigation.navigate('Login')}
            variant="primary"
            style={{ marginTop: Spacing['2xl'] }}
          />
        </View>
      ) : (
        <View style={styles.container}>
          <View style={styles.iconContainer}>
            <Icon name="lock-reset" size={48} color={Colors.primary[600]} />
          </View>
          <Text style={styles.title}>Forgot Password?</Text>
          <Text style={styles.subtitle}>
            Enter your email and we'll send you a link to reset your password.
          </Text>

          <Input
            label="Email Address"
            icon="email"
            placeholder="you@example.com"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            containerStyle={{ marginTop: Spacing['2xl'] }}
          />

          <Button
            title="Send Reset Link"
            onPress={handleSubmit}
            variant="gradient"
            size="lg"
            fullWidth
            loading={loading}
            icon="send"
          />
        </View>
      )}
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  backButton: {
    marginBottom: Spacing.lg,
  },
  container: {
    paddingTop: Spacing['3xl'],
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 24,
    backgroundColor: Colors.primary[50],
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  title: {
    ...Typography.heading2,
    color: Colors.textPrimary,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.textSecondary,
    marginTop: Spacing.sm,
    lineHeight: 22,
  },
  successContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: Spacing['5xl'],
  },
  successIcon: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: Colors.primary[50],
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
});
