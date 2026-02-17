/**
 * AI Agent chat service
 */

import api from './api';
import { ENDPOINTS } from '../utils/constants';
import type { ChatMessage } from '../types';

export const chatService = {
  sendMessage: async (message: string, sessionId?: string): Promise<ChatMessage> => {
    const { data } = await api.post(ENDPOINTS.agents.chat, {
      message,
      session_id: sessionId,
    });
    return data;
  },

  getHistory: async (sessionId?: string): Promise<ChatMessage[]> => {
    const { data } = await api.get(ENDPOINTS.agents.chat, {
      params: { session_id: sessionId },
    });
    return data.messages || data;
  },

  getSuggestions: async (context?: string): Promise<string[]> => {
    const { data } = await api.post(ENDPOINTS.agents.suggestions, { context });
    return data.suggestions || [];
  },
};
