/**
 * Login screen with gradient header and social auth placeholders
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { useAuthStore } from '../../store/authStore';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import Toast from 'react-native-toast-message';

const { width } = Dimensions.get('window');

export const LoginScreen = ({ navigation }: any) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const { login, isLoading } = useAuthStore();

  const validate = () => {
    const newErrors: typeof errors = {};
    if (!email.trim()) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) newErrors.email = 'Invalid email format';
    if (!password) newErrors.password = 'Password is required';
    else if (password.length < 6) newErrors.password = 'Password must be 6+ characters';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async () => {
    if (!validate()) return;
    try {
      await login({ email: email.trim(), password });
    } catch (error: any) {
      Toast.show({
        type: 'error',
        text1: 'Login Failed',
        text2: error.message || 'Invalid credentials',
      });
    }
  };

  return (
    <ScreenWrapper
      scroll
      keyboardAvoiding
      edges={[]}
      noPadding
      backgroundColor={Colors.white}
    >
      {/* Hero Header */}
      <LinearGradient
        colors={Colors.gradient.hero}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View style={styles.logoContainer}>
            <Icon name="flight-takeoff" size={36} color={Colors.white} />
          </View>
          <Text style={styles.headerTitle}>Welcome Back</Text>
          <Text style={styles.headerSubtitle}>
            Sign in to plan your next adventure
          </Text>
        </View>
        {/* Decorative circle */}
        <View style={styles.circle1} />
        <View style={styles.circle2} />
      </LinearGradient>

      {/* Form */}
      <View style={styles.formContainer}>
        <Input
          label="Email"
          icon="email"
          placeholder="you@example.com"
          value={email}
          onChangeText={setEmail}
          error={errors.email}
          keyboardType="email-address"
          autoCapitalize="none"
          autoComplete="email"
        />

        <Input
          label="Password"
          icon="lock"
          placeholder="Enter your password"
          value={password}
          onChangeText={setPassword}
          error={errors.password}
          secureTextEntry={!showPassword}
          rightIcon={showPassword ? 'visibility' : 'visibility-off'}
          onRightIconPress={() => setShowPassword(!showPassword)}
        />

        <TouchableOpacity
          onPress={() => navigation.navigate('ForgotPassword')}
          style={styles.forgotButton}
        >
          <Text style={styles.forgotText}>Forgot Password?</Text>
        </TouchableOpacity>

        <Button
          title="Sign In"
          onPress={handleLogin}
          variant="gradient"
          size="lg"
          fullWidth
          loading={isLoading}
          icon="login"
        />

        {/* Divider */}
        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>or continue with</Text>
          <View style={styles.dividerLine} />
        </View>

        {/* Social Auth */}
        <View style={styles.socialRow}>
          <TouchableOpacity style={styles.socialButton}>
            <Icon name="language" size={24} color="#4285F4" />
            <Text style={styles.socialText}>Google</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.socialButton}>
            <Icon name="apple" size={24} color={Colors.black} />
            <Text style={styles.socialText}>Apple</Text>
          </TouchableOpacity>
        </View>

        {/* Register link */}
        <View style={styles.registerRow}>
          <Text style={styles.registerText}>Don't have an account? </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Register')}>
            <Text style={styles.registerLink}>Sign Up</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  header: {
    height: 280,
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  headerContent: {
    paddingHorizontal: Spacing.screenPadding,
    paddingBottom: Spacing['2xl'],
    zIndex: 1,
  },
  logoContainer: {
    width: 64,
    height: 64,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.base,
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
  circle1: {
    position: 'absolute',
    top: -40,
    right: -40,
    width: 160,
    height: 160,
    borderRadius: 80,
    backgroundColor: 'rgba(255,255,255,0.08)',
  },
  circle2: {
    position: 'absolute',
    top: 60,
    right: 40,
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.06)',
  },
  formContainer: {
    flex: 1,
    paddingHorizontal: Spacing.screenPadding,
    paddingTop: Spacing['2xl'],
    paddingBottom: Spacing['3xl'],
    backgroundColor: Colors.white,
    borderTopLeftRadius: BorderRadius['2xl'],
    borderTopRightRadius: BorderRadius['2xl'],
    marginTop: -20,
  },
  forgotButton: {
    alignSelf: 'flex-end',
    marginBottom: Spacing.lg,
    marginTop: -Spacing.sm,
  },
  forgotText: {
    ...Typography.bodySmall,
    color: Colors.primary[600],
    fontWeight: '600',
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: Spacing.xl,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: Colors.gray[200],
  },
  dividerText: {
    ...Typography.bodySmall,
    color: Colors.gray[400],
    marginHorizontal: Spacing.base,
  },
  socialRow: {
    flexDirection: 'row',
    gap: Spacing.md,
  },
  socialButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderWidth: 1.5,
    borderColor: Colors.gray[200],
    borderRadius: BorderRadius.lg,
    gap: Spacing.sm,
  },
  socialText: {
    ...Typography.body,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  registerRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: Spacing.xl,
  },
  registerText: {
    ...Typography.body,
    color: Colors.textSecondary,
  },
  registerLink: {
    ...Typography.body,
    color: Colors.primary[600],
    fontWeight: '700',
  },
});
