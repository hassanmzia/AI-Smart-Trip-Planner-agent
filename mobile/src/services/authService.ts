/**
 * Authentication service
 */

import api from './api';
import { ENDPOINTS } from '../utils/constants';
import type { LoginCredentials, RegisterData, User, AuthTokens } from '../types';

interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const { data } = await api.post(ENDPOINTS.auth.login, credentials);
    return data;
  },

  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const { data } = await api.post(ENDPOINTS.auth.register, userData);
    return data;
  },

  logout: async (): Promise<void> => {
    await api.post(ENDPOINTS.auth.logout);
  },

  getMe: async (): Promise<User> => {
    const { data } = await api.get(ENDPOINTS.auth.me);
    return data;
  },

  updateProfile: async (profileData: Partial<User>): Promise<User> => {
    const { data } = await api.put(ENDPOINTS.auth.me, profileData);
    return data;
  },

  forgotPassword: async (email: string): Promise<void> => {
    await api.post(ENDPOINTS.auth.forgotPassword, { email });
  },

  resetPassword: async (token: string, password: string): Promise<void> => {
    await api.post(ENDPOINTS.auth.resetPassword, { token, password });
  },
};
