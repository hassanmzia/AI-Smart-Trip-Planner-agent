/**
 * Registration screen
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { useAuthStore } from '../../store/authStore';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import Toast from 'react-native-toast-message';

export const RegisterScreen = ({ navigation }: any) => {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { register, isLoading } = useAuthStore();

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.first_name.trim()) e.first_name = 'First name required';
    if (!form.last_name.trim()) e.last_name = 'Last name required';
    if (!form.email.trim()) e.email = 'Email required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Invalid email';
    if (!form.password) e.password = 'Password required';
    else if (form.password.length < 8) e.password = 'Min 8 characters';
    if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleRegister = async () => {
    if (!validate()) return;
    try {
      await register({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        password: form.password,
      });
      Toast.show({ type: 'success', text1: 'Welcome!', text2: 'Account created successfully' });
    } catch (error: any) {
      Toast.show({ type: 'error', text1: 'Registration Failed', text2: error.message });
    }
  };

  return (
    <ScreenWrapper scroll keyboardAvoiding edges={[]} noPadding backgroundColor={Colors.white}>
      {/* Header */}
      <LinearGradient
        colors={[Colors.secondary[700], Colors.primary[600]]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.header}
      >
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
        >
          <Icon name="arrow-back" size={24} color={Colors.white} />
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <View style={styles.logoContainer}>
            <Icon name="person-add" size={32} color={Colors.white} />
          </View>
          <Text style={styles.headerTitle}>Create Account</Text>
          <Text style={styles.headerSubtitle}>
            Start planning your dream trips
          </Text>
        </View>
      </LinearGradient>

      {/* Form */}
      <View style={styles.formContainer}>
        <View style={styles.nameRow}>
          <Input
            label="First Name"
            icon="person"
            placeholder="John"
            value={form.first_name}
            onChangeText={(v) => setForm({ ...form, first_name: v })}
            error={errors.first_name}
            containerStyle={{ flex: 1, marginRight: Spacing.sm }}
          />
          <Input
            label="Last Name"
            placeholder="Doe"
            value={form.last_name}
            onChangeText={(v) => setForm({ ...form, last_name: v })}
            error={errors.last_name}
            containerStyle={{ flex: 1 }}
          />
        </View>

        <Input
          label="Email"
          icon="email"
          placeholder="you@example.com"
          value={form.email}
          onChangeText={(v) => setForm({ ...form, email: v })}
          error={errors.email}
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <Input
          label="Password"
          icon="lock"
          placeholder="Min 8 characters"
          value={form.password}
          onChangeText={(v) => setForm({ ...form, password: v })}
          error={errors.password}
          secureTextEntry={!showPassword}
          rightIcon={showPassword ? 'visibility' : 'visibility-off'}
          onRightIconPress={() => setShowPassword(!showPassword)}
        />

        <Input
          label="Confirm Password"
          icon="lock-outline"
          placeholder="Re-enter password"
          value={form.confirmPassword}
          onChangeText={(v) => setForm({ ...form, confirmPassword: v })}
          error={errors.confirmPassword}
          secureTextEntry={!showPassword}
        />

        <Button
          title="Create Account"
          onPress={handleRegister}
          variant="gradient"
          size="lg"
          fullWidth
          loading={isLoading}
          icon="how-to-reg"
        />

        <View style={styles.termsRow}>
          <Text style={styles.termsText}>
            By signing up, you agree to our{' '}
            <Text style={styles.termsLink}>Terms of Service</Text> and{' '}
            <Text style={styles.termsLink}>Privacy Policy</Text>
          </Text>
        </View>

        <View style={styles.loginRow}>
          <Text style={styles.loginText}>Already have an account? </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Login')}>
            <Text style={styles.loginLink}>Sign In</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  header: {
    height: 240,
    justifyContent: 'flex-end',
  },
  backButton: {
    position: 'absolute',
    top: 56,
    left: Spacing.screenPadding,
    zIndex: 10,
  },
  headerContent: {
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing['2xl'],
  },
  logoContainer: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  headerTitle: {
    ...Typography.heading1,
    color: Colors.white,
  },
  headerSubtitle: {
    ...Typography.body,
    color: 'rgba(255,255,255,0.8)',
    marginTop: Spacing.xs,
  },
  formContainer: {
    paddingHorizontal: Spacing.screenPadding,
    paddingTop: Spacing['2xl'],
    paddingBottom: Spacing['3xl'],
    backgroundColor: Colors.white,
    borderTopLeftRadius: BorderRadius['2xl'],
    borderTopRightRadius: BorderRadius['2xl'],
    marginTop: -20,
  },
  nameRow: {
    flexDirection: 'row',
  },
  termsRow: {
    marginTop: Spacing.lg,
    paddingHorizontal: Spacing.lg,
  },
  termsText: {
    ...Typography.bodySmall,
    color: Colors.textTertiary,
    textAlign: 'center',
    lineHeight: 20,
  },
  termsLink: {
    color: Colors.primary[600],
    fontWeight: '600',
  },
  loginRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: Spacing.lg,
  },
  loginText: {
    ...Typography.body,
    color: Colors.textSecondary,
  },
  loginLink: {
    ...Typography.body,
    color: Colors.primary[600],
    fontWeight: '700',
  },
});
