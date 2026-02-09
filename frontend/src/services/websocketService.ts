import { io, Socket } from 'socket.io-client';
import { WS_BASE_URL, WS_EVENTS } from '@/utils/constants';
import { getAuthToken } from '@/utils/helpers';
import type { WebSocketMessage, Notification } from '@/types';

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.socket?.connected) {
      console.log('WebSocket already connected');
      return;
    }

    const token = getAuthToken();

    if (!token) {
      console.warn('No auth token found, skipping WebSocket connection');
      return;
    }

    this.socket = io(WS_BASE_URL, {
      auth: {
        token,
      },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: this.reconnectDelay,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    this.setupEventHandlers();
  }

  /**
   * Setup WebSocket event handlers
   */
  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.on(WS_EVENTS.CONNECT, () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.emit('connected', null);
    });

    this.socket.on(WS_EVENTS.DISCONNECT, (reason: string) => {
      console.log('WebSocket disconnected:', reason);
      this.emit('disconnected', { reason });
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        this.emit('error', { message: 'Failed to connect to server' });
      }
    });

    // Handle incoming messages
    this.socket.on(WS_EVENTS.NOTIFICATION, (data: Notification) => {
      this.emit(WS_EVENTS.NOTIFICATION, data);
    });

    this.socket.on(WS_EVENTS.PRICE_UPDATE, (data: any) => {
      this.emit(WS_EVENTS.PRICE_UPDATE, data);
    });

    this.socket.on(WS_EVENTS.BOOKING_UPDATE, (data: any) => {
      this.emit(WS_EVENTS.BOOKING_UPDATE, data);
    });

    this.socket.on(WS_EVENTS.CHAT_MESSAGE, (data: any) => {
      this.emit(WS_EVENTS.CHAT_MESSAGE, data);
    });

    // Handle any custom events
    this.socket.onAny((eventName: string, data: any) => {
      this.emit(eventName, data);
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.listeners.clear();
      console.log('WebSocket disconnected');
    }
  }

  /**
   * Send message through WebSocket
   */
  send(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected, message not sent');
    }
  }

  /**
   * Subscribe to price alerts
   */
  subscribeToPriceAlerts(alertIds: string[]): void {
    this.send('subscribe_price_alerts', { alertIds });
  }

  /**
   * Unsubscribe from price alerts
   */
  unsubscribeFromPriceAlerts(alertIds: string[]): void {
    this.send('unsubscribe_price_alerts', { alertIds });
  }

  /**
   * Subscribe to booking updates
   */
  subscribeToBookingUpdates(bookingIds: string[]): void {
    this.send('subscribe_booking_updates', { bookingIds });
  }

  /**
   * Join chat room
   */
  joinChatRoom(roomId: string): void {
    this.send('join_room', { roomId });
  }

  /**
   * Leave chat room
   */
  leaveChatRoom(roomId: string): void {
    this.send('leave_room', { roomId });
  }

  /**
   * Add event listener
   */
  on(event: string, callback: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  /**
   * Remove event listener
   */
  off(event: string, callback: (data: any) => void): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.delete(callback);
      if (listeners.size === 0) {
        this.listeners.delete(event);
      }
    }
  }

  /**
   * Emit event to all listeners
   */
  private emit(event: string, data: any): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Get socket instance
   */
  getSocket(): Socket | null {
    return this.socket;
  }
}

// Export singleton instance
const websocketService = new WebSocketService();
export default websocketService;
