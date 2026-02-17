/**
 * Authentication store using Zustand
 */

import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS } from '../utils/constants';
import { authService } from '../services/authService';
import type { User, AuthTokens, LoginCredentials, RegisterData } from '../types';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  restoreSession: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true, // Start true to check stored session
  error: null,

  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.login(credentials);
      const { user, tokens } = response;

      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, tokens.accessToken);
      await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refreshToken);
      await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));

      set({ user, tokens, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.error || error.message || 'Login failed';
      set({ error: message, isLoading: false });
      throw new Error(message);
    }
  },

  register: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.register(data);
      const { user, tokens } = response;

      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, tokens.accessToken);
      await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refreshToken);
      await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));

      set({ user, tokens, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.error ||
        error.response?.data?.email?.[0] ||
        error.message || 'Registration failed';
      set({ error: message, isLoading: false });
      throw new Error(message);
    }
  },

  logout: async () => {
    try {
      await authService.logout();
    } catch {
      // Ignore server errors on logout
    }
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.AUTH_TOKEN,
      STORAGE_KEYS.REFRESH_TOKEN,
      STORAGE_KEYS.USER_DATA,
    ]);
    set({ user: null, tokens: null, isAuthenticated: false, error: null });
  },

  refreshUser: async () => {
    try {
      const user = await authService.getMe();
      await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
      set({ user });
    } catch {
      // Silently fail
    }
  },

  restoreSession: async () => {
    try {
      const [token, refreshToken, userData] = await AsyncStorage.multiGet([
        STORAGE_KEYS.AUTH_TOKEN,
        STORAGE_KEYS.REFRESH_TOKEN,
        STORAGE_KEYS.USER_DATA,
      ]);

      if (token[1] && refreshToken[1] && userData[1]) {
        const user = JSON.parse(userData[1]);
        set({
          user,
          tokens: { accessToken: token[1], refreshToken: refreshToken[1] },
          isAuthenticated: true,
          isLoading: false,
        });
        // Silently refresh user data in background
        get().refreshUser();
      } else {
        set({ isLoading: false });
      }
    } catch {
      set({ isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
