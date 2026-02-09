import api, { handleApiResponse } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import type {
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  ApiResponse,
} from '@/types';

/**
 * Login user
 */
export const login = async (credentials: LoginCredentials): Promise<{
  user: User;
  tokens: AuthTokens;
}> => {
  const response = await api.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
  return handleApiResponse(response);
};

/**
 * Register new user
 */
export const register = async (data: RegisterData): Promise<{
  user: User;
  tokens: AuthTokens;
}> => {
  const response = await api.post(API_ENDPOINTS.AUTH.REGISTER, data);
  return handleApiResponse(response);
};

/**
 * Logout user
 */
export const logout = async (): Promise<void> => {
  const response = await api.post(API_ENDPOINTS.AUTH.LOGOUT);
  return handleApiResponse(response);
};

/**
 * Refresh access token
 */
export const refreshToken = async (refreshToken: string): Promise<AuthTokens> => {
  const response = await api.post(API_ENDPOINTS.AUTH.REFRESH, { refreshToken });
  return handleApiResponse(response);
};

/**
 * Get current user
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get(API_ENDPOINTS.AUTH.ME);
  return handleApiResponse(response);
};

/**
 * Update user profile
 */
export const updateProfile = async (data: Partial<User>): Promise<User> => {
  const response = await api.put(API_ENDPOINTS.AUTH.ME, data);
  return handleApiResponse(response);
};

/**
 * Change password
 */
export const changePassword = async (
  currentPassword: string,
  newPassword: string
): Promise<void> => {
  const response = await api.post(`${API_ENDPOINTS.AUTH.ME}/password`, {
    currentPassword,
    newPassword,
  });
  return handleApiResponse(response);
};

/**
 * Request password reset
 */
export const requestPasswordReset = async (email: string): Promise<void> => {
  const response = await api.post('/api/auth/forgot-password', { email });
  return handleApiResponse(response);
};

/**
 * Reset password with token
 */
export const resetPassword = async (
  token: string,
  newPassword: string
): Promise<void> => {
  const response = await api.post('/api/auth/reset-password', {
    token,
    newPassword,
  });
  return handleApiResponse(response);
};

/**
 * Verify email
 */
export const verifyEmail = async (token: string): Promise<void> => {
  const response = await api.post('/api/auth/verify-email', { token });
  return handleApiResponse(response);
};

/**
 * Resend verification email
 */
export const resendVerification = async (email: string): Promise<void> => {
  const response = await api.post('/api/auth/resend-verification', { email });
  return handleApiResponse(response);
};
