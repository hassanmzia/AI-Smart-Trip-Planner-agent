import api, { handleApiResponse } from './api';
import { API_ENDPOINTS } from '@/utils/constants';
import type { ChatMessage, AgentContext } from '@/types';

/**
 * Send message to AI agent
 */
export const sendChatMessage = async (
  message: string,
  context?: Partial<AgentContext>
): Promise<{
  response: ChatMessage;
  suggestions?: string[];
  actions?: Array<{ type: string; data: any }>;
}> => {
  const response = await api.post(API_ENDPOINTS.AGENT.CHAT, {
    message,
    context,
  });
  return handleApiResponse(response);
};

/**
 * Get chat history
 */
export const getChatHistory = async (
  sessionId?: string
): Promise<ChatMessage[]> => {
  let url = API_ENDPOINTS.AGENT.CHAT;
  if (sessionId) {
    url += `?sessionId=${sessionId}`;
  }
  const response = await api.get(url);
  return handleApiResponse(response);
};

/**
 * Create new chat session
 */
export const createChatSession = async (): Promise<{ sessionId: string }> => {
  const response = await api.post(`${API_ENDPOINTS.AGENT.CHAT}/session`);
  return handleApiResponse(response);
};

/**
 * Clear chat history
 */
export const clearChatHistory = async (sessionId: string): Promise<void> => {
  const response = await api.delete(`${API_ENDPOINTS.AGENT.CHAT}/session/${sessionId}`);
  return handleApiResponse(response);
};

/**
 * Get agent context (user preferences, goals, etc.)
 */
export const getAgentContext = async (): Promise<AgentContext> => {
  const response = await api.get(API_ENDPOINTS.AGENT.CONTEXT);
  return handleApiResponse(response);
};

/**
 * Update agent context
 */
export const updateAgentContext = async (
  context: Partial<AgentContext>
): Promise<AgentContext> => {
  const response = await api.put(API_ENDPOINTS.AGENT.CONTEXT, context);
  return handleApiResponse(response);
};

/**
 * Get agent suggestions based on user goals
 */
export const getAgentSuggestions = async (
  goals: string[],
  budget?: number
): Promise<{
  flights?: any[];
  hotels?: any[];
  tips?: string[];
}> => {
  const response = await api.post(`${API_ENDPOINTS.AGENT.CHAT}/suggestions`, {
    goals,
    budget,
  });
  return handleApiResponse(response);
};

/**
 * Analyze user query and extract intent
 */
export const analyzeQuery = async (
  query: string
): Promise<{
  intent: string;
  entities: Record<string, any>;
  confidence: number;
}> => {
  const response = await api.post(`${API_ENDPOINTS.AGENT.CHAT}/analyze`, {
    query,
  });
  return handleApiResponse(response);
};

/**
 * Get quick actions/prompts for the agent
 */
export const getQuickActions = async (): Promise<
  Array<{
    id: string;
    label: string;
    prompt: string;
    icon?: string;
  }>
> => {
  const response = await api.get(`${API_ENDPOINTS.AGENT.CHAT}/quick-actions`);
  return handleApiResponse(response);
};
