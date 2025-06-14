# Real-time Data with WebSockets & Server-Sent Events

## Table of Contents
1. [Real-time Fundamentals](#real-time-fundamentals)
2. [WebSocket Integration](#websocket-integration)
3. [Server-Sent Events (SSE)](#server-sent-events-sse)
4. [React Implementation Patterns](#react-implementation-patterns)
5. [Connection Management](#connection-management)
6. [Message Broadcasting](#message-broadcasting)
7. [Authentication & Security](#authentication--security)
8. [Performance Optimization](#performance-optimization)
9. [Error Handling & Reconnection](#error-handling--reconnection)
10. [Testing Real-time Features](#testing-real-time-features)
11. [Production Considerations](#production-considerations)

## Real-time Fundamentals

### Understanding Real-time Communication

Real-time communication enables instant data exchange between client and server, essential for modern interactive applications.

```typescript
// Real-time communication patterns comparison
interface RealtimeTechnology {
  name: string;
  bidirectional: boolean;
  overhead: 'low' | 'medium' | 'high';
  browserSupport: 'excellent' | 'good' | 'limited';
  useCases: string[];
}

const technologies: RealtimeTechnology[] = [
  {
    name: 'WebSockets',
    bidirectional: true,
    overhead: 'low',
    browserSupport: 'excellent',
    useCases: ['Chat', 'Gaming', 'Collaborative editing', 'Live updates']
  },
  {
    name: 'Server-Sent Events',
    bidirectional: false,
    overhead: 'low',
    browserSupport: 'good',
    useCases: ['Live feeds', 'Notifications', 'Stock prices', 'Real-time dashboards']
  },
  {
    name: 'Polling',
    bidirectional: false,
    overhead: 'high',
    browserSupport: 'excellent',
    useCases: ['Simple updates', 'Legacy systems', 'Fallback option']
  },
  {
    name: 'Long Polling',
    bidirectional: false,
    overhead: 'medium',
    browserSupport: 'excellent',
    useCases: ['Chat systems', 'Real-time updates', 'SSE alternative']
  }
];

// Technology selection guide
export const selectRealtimeTechnology = (requirements: {
  bidirectional: boolean;
  frequency: 'low' | 'medium' | 'high';
  reliability: 'basic' | 'high';
  scalability: 'basic' | 'high';
}): string => {
  if (requirements.bidirectional && requirements.frequency === 'high') {
    return 'WebSockets';
  }
  
  if (!requirements.bidirectional && requirements.frequency === 'medium') {
    return 'Server-Sent Events';
  }
  
  if (requirements.frequency === 'low') {
    return 'Polling';
  }
  
  return 'WebSockets'; // Default for complex scenarios
};
```

### Real-time Architecture Patterns

```typescript
{% raw %}
{% raw %}
// Event-driven architecture for real-time systems
interface RealtimeEvent {
  id: string;
  type: string;
  payload: any;
  timestamp: number;
  source: string;
  target?: string;
}

interface RealtimeChannel {
  name: string;
  subscribers: Set<string>;
  eventHistory: RealtimeEvent[];
  maxHistory: number;
}

class RealtimeEventBus {
  private channels = new Map<string, RealtimeChannel>();
  private subscribers = new Map<string, Set<(event: RealtimeEvent) => void>>();

  createChannel(name: string, maxHistory = 100): void {
    this.channels.set(name, {
      name,
      subscribers: new Set(),
      eventHistory: [],
      maxHistory
    });
  }

  subscribe(channelName: string, callback: (event: RealtimeEvent) => void): () => void {
    const channel = this.channels.get(channelName);
    if (!channel) {
      throw new Error(`Channel ${channelName} does not exist`);
    }

    const subscriberId = crypto.randomUUID();
    channel.subscribers.add(subscriberId);

    if (!this.subscribers.has(subscriberId)) {
      this.subscribers.set(subscriberId, new Set());
    }
    this.subscribers.get(subscriberId)!.add(callback);

    // Send recent events to new subscriber
    channel.eventHistory.slice(-10).forEach(callback);

    return () => {
      channel.subscribers.delete(subscriberId);
      this.subscribers.delete(subscriberId);
    };
  }

  publish(channelName: string, event: Omit<RealtimeEvent, 'id' | 'timestamp'>): void {
    const channel = this.channels.get(channelName);
    if (!channel) return;

    const fullEvent: RealtimeEvent = {
      ...event,
      id: crypto.randomUUID(),
      timestamp: Date.now()
    };

    // Add to history
    channel.eventHistory.push(fullEvent);
    if (channel.eventHistory.length > channel.maxHistory) {
      channel.eventHistory.shift();
    }

    // Notify subscribers
    channel.subscribers.forEach(subscriberId => {
      const callbacks = this.subscribers.get(subscriberId);
      callbacks?.forEach(callback => callback(fullEvent));
    });
  }
}

export const eventBus = new RealtimeEventBus();
{% endraw %}
{% endraw %}
```

## WebSocket Integration

### Basic WebSocket Implementation

```typescript
// utils/websocket.ts
export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  messageQueueSize?: number;
}

export interface WebSocketMessage {
  type: string;
  payload: any;
  id?: string;
  timestamp?: number;
}

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private messageQueue: WebSocketMessage[] = [];
  private listeners = new Map<string, Set<(data: any) => void>>();
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  
  constructor(private config: WebSocketConfig) {
    this.config = {
      reconnectAttempts: 5,
      reconnectInterval: 1000,
      heartbeatInterval: 30000,
      messageQueueSize: 100,
      ...config
    };
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.url, this.config.protocols);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          this.stopHeartbeat();
          
          if (!event.wasClean && this.shouldReconnect()) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Normal closure');
      this.ws = null;
    }
    this.stopHeartbeat();
    this.stopReconnect();
  }

  send(message: WebSocketMessage): void {
    const fullMessage = {
      ...message,
      id: message.id || crypto.randomUUID(),
      timestamp: Date.now()
    };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(fullMessage));
    } else {
      this.queueMessage(fullMessage);
    }
  }

  subscribe(type: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(callback);

    return () => {
      this.listeners.get(type)?.delete(callback);
      if (this.listeners.get(type)?.size === 0) {
        this.listeners.delete(type);
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    const listeners = this.listeners.get(message.type);
    if (listeners) {
      listeners.forEach(callback => callback(message.payload));
    }
  }

  private queueMessage(message: WebSocketMessage): void {
    this.messageQueue.push(message);
    if (this.messageQueue.length > this.config.messageQueueSize!) {
      this.messageQueue.shift(); // Remove oldest message
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()!;
      this.send(message);
    }
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping', payload: {} });
    }, this.config.heartbeatInterval!);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.config.reconnectAttempts!;
  }

  private scheduleReconnect(): void {
    const delay = this.config.reconnectInterval! * Math.pow(2, this.reconnectAttempts);
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect().catch(() => {
        if (this.shouldReconnect()) {
          this.scheduleReconnect();
        }
      });
    }, delay);
  }

  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
```

### React WebSocket Hook

```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketManager, WebSocketConfig, WebSocketMessage } from '../utils/websocket';

interface UseWebSocketReturn {
  sendMessage: (message: WebSocketMessage) => void;
  subscribe: (type: string, callback: (data: any) => void) => () => void;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastMessage: WebSocketMessage | null;
  isConnected: boolean;
}

export const useWebSocket = (config: WebSocketConfig): UseWebSocketReturn => {
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsManagerRef = useRef<WebSocketManager | null>(null);

  useEffect(() => {
    const wsManager = new WebSocketManager(config);
    wsManagerRef.current = wsManager;

    const connect = async () => {
      setConnectionState('connecting');
      try {
        await wsManager.connect();
        setConnectionState('connected');
      } catch (error) {
        setConnectionState('error');
        console.error('WebSocket connection failed:', error);
      }
    };

    connect();

    return () => {
      wsManager.disconnect();
      setConnectionState('disconnected');
    };
  }, [config.url]);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    wsManagerRef.current?.send(message);
  }, []);

  const subscribe = useCallback((type: string, callback: (data: any) => void) => {
    return wsManagerRef.current?.subscribe(type, (data) => {
      setLastMessage({ type, payload: data, timestamp: Date.now() });
      callback(data);
    }) ?? (() => {});
  }, []);

  return {
    sendMessage,
    subscribe,
    connectionState,
    lastMessage,
    isConnected: connectionState === 'connected'
  };
};

// Specific hooks for common patterns
export const useWebSocketSubscription = <T>(
  config: WebSocketConfig,
  eventType: string,
  onMessage?: (data: T) => void
) => {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const { subscribe, connectionState } = useWebSocket(config);

  useEffect(() => {
    const unsubscribe = subscribe(eventType, (newData: T) => {
      setData(newData);
      setError(null);
      onMessage?.(newData);
    });

    return unsubscribe;
  }, [subscribe, eventType, onMessage]);

  return { data, error, connectionState };
};
```

### Real-time Chat Implementation

```typescript
{% raw %}
{% raw %}
// components/Chat/ChatRoom.tsx
interface ChatMessage {
  id: string;
  content: string;
  author: {
    id: string;
    name: string;
    avatar: string;
  };
  timestamp: number;
  type: 'text' | 'image' | 'file';
  edited?: boolean;
}

interface ChatRoom {
  id: string;
  name: string;
  participants: string[];
  lastActivity: number;
}

const ChatRoom: React.FC<{ roomId: string }> = ({ roomId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [typing, setTyping] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { sendMessage, subscribe, isConnected } = useWebSocket({
    url: `ws://localhost:8080/chat/${roomId}`,
    reconnectAttempts: 5,
    heartbeatInterval: 30000
  });

  // Subscribe to different message types
  useEffect(() => {
    const unsubscribers = [
      subscribe('message', (message: ChatMessage) => {
        setMessages(prev => [...prev, message]);
      }),
      
      subscribe('typing_start', ({ userId, userName }: { userId: string; userName: string }) => {
        setTyping(prev => prev.includes(userName) ? prev : [...prev, userName]);
      }),
      
      subscribe('typing_stop', ({ userName }: { userName: string }) => {
        setTyping(prev => prev.filter(name => name !== userName));
      }),
      
      subscribe('message_history', (history: ChatMessage[]) => {
        setMessages(history);
      }),
      
      subscribe('user_joined', ({ userName }: { userName: string }) => {
        // Handle user joined notification
      }),
      
      subscribe('user_left', ({ userName }: { userName: string }) => {
        // Handle user left notification
      })
    ];

    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [subscribe]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle typing indicators
  const typingTimeoutRef = useRef<NodeJS.Timeout>();
  const handleTyping = useCallback(() => {
    sendMessage({ type: 'typing_start', payload: {} });
    
    clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => {
      sendMessage({ type: 'typing_stop', payload: {} });
    }, 1000);
  }, [sendMessage]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (currentMessage.trim() && isConnected) {
      sendMessage({
        type: 'send_message',
        payload: {
          content: currentMessage.trim(),
          type: 'text'
        }
      });
      setCurrentMessage('');
      sendMessage({ type: 'typing_stop', payload: {} });
    }
  };

  return (
    <div className="chat-room">
      <div className="chat-header">
        <h2>Chat Room</h2>
        <div className="connection-status">
          {isConnected ? (
            <span className="status-connected">●</span>
          ) : (
            <span className="status-disconnected">●</span>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.map(message => (
          <ChatMessage key={message.id} message={message} />
        ))}
        
        {typing.length > 0 && (
          <div className="typing-indicator">
            {typing.join(', ')} {typing.length === 1 ? 'is' : 'are'} typing...
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chat-input">
        <input
          type="text"
          value={currentMessage}
          onChange={(e) => {
            setCurrentMessage(e.target.value);
            handleTyping();
          }}
          placeholder="Type a message..."
          disabled={!isConnected}
        />
        <button type="submit" disabled={!isConnected || !currentMessage.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

// components/Chat/ChatMessage.tsx
const ChatMessage: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const [showTimestamp, setShowTimestamp] = useState(false);
  
  return (
    <div 
      className={`chat-message ${message.type}`}
      onClick={() => setShowTimestamp(!showTimestamp)}
    >
      <div className="message-author">
        <img src={message.author.avatar} alt={message.author.name} />
        <span>{message.author.name}</span>
      </div>
      
      <div className="message-content">
        {message.type === 'text' && message.content}
        {message.type === 'image' && (
          <img src={message.content} alt="Shared image" />
        )}
        {message.edited && <span className="edited-indicator">(edited)</span>}
      </div>
      
      {showTimestamp && (
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleString()}
        </div>
      )}
    </div>
  );
};
{% endraw %}
{% endraw %}
```

## Server-Sent Events (SSE)

### SSE Implementation

```typescript
// utils/serverSentEvents.ts
interface SSEConfig {
  url: string;
  headers?: Record<string, string>;
  withCredentials?: boolean;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface SSEEvent {
  id?: string;
  event?: string;
  data: any;
  retry?: number;
}

export class ServerSentEventsManager {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private listeners = new Map<string, Set<(event: SSEEvent) => void>>();
  private reconnectTimer: NodeJS.Timeout | null = null;
  private lastEventId: string | null = null;

  constructor(private config: SSEConfig) {
    this.config = {
      reconnectAttempts: 5,
      reconnectInterval: 1000,
      ...config
    };
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const url = new URL(this.config.url);
        if (this.lastEventId) {
          url.searchParams.set('lastEventId', this.lastEventId);
        }

        this.eventSource = new EventSource(url.toString(), {
          withCredentials: this.config.withCredentials
        });

        this.eventSource.onopen = () => {
          console.log('SSE connection opened');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.eventSource.onmessage = (event) => {
          this.handleEvent({
            id: event.lastEventId,
            data: this.parseData(event.data)
          });
        };

        this.eventSource.onerror = (error) => {
          console.error('SSE error:', error);
          
          if (this.eventSource?.readyState === EventSource.CLOSED) {
            if (this.shouldReconnect()) {
              this.scheduleReconnect();
            } else {
              reject(new Error('SSE connection failed'));
            }
          }
        };

        // Handle custom events
        this.setupCustomEventListeners();

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.stopReconnect();
  }

  subscribe(eventType: string, callback: (event: SSEEvent) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    return () => {
      this.listeners.get(eventType)?.delete(callback);
      if (this.listeners.get(eventType)?.size === 0) {
        this.listeners.delete(eventType);
      }
    };
  }

  private setupCustomEventListeners(): void {
    if (!this.eventSource) return;

    // Listen for specific event types
    const eventTypes = ['update', 'notification', 'alert', 'heartbeat'];
    
    eventTypes.forEach(eventType => {
      this.eventSource!.addEventListener(eventType, (event) => {
        this.handleEvent({
          id: event.lastEventId,
          event: eventType,
          data: this.parseData((event as MessageEvent).data)
        });
      });
    });
  }

  private handleEvent(event: SSEEvent): void {
    if (event.id) {
      this.lastEventId = event.id;
    }

    const eventType = event.event || 'message';
    const listeners = this.listeners.get(eventType);
    
    if (listeners) {
      listeners.forEach(callback => callback(event));
    }
  }

  private parseData(data: string): any {
    try {
      return JSON.parse(data);
    } catch {
      return data;
    }
  }

  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.config.reconnectAttempts!;
  }

  private scheduleReconnect(): void {
    const delay = this.config.reconnectInterval! * Math.pow(2, this.reconnectAttempts);
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect().catch(() => {
        if (this.shouldReconnect()) {
          this.scheduleReconnect();
        }
      });
    }, delay);
  }

  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  get readyState(): number {
    return this.eventSource?.readyState ?? EventSource.CLOSED;
  }

  get isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}
```

### React SSE Hook

```typescript
// hooks/useServerSentEvents.ts
import { useEffect, useRef, useState, useCallback } from 'react';
import { ServerSentEventsManager, SSEConfig, SSEEvent } from '../utils/serverSentEvents';

interface UseSSEReturn {
  subscribe: (eventType: string, callback: (event: SSEEvent) => void) => () => void;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastEvent: SSEEvent | null;
  isConnected: boolean;
}

export const useServerSentEvents = (config: SSEConfig): UseSSEReturn => {
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const sseManagerRef = useRef<ServerSentEventsManager | null>(null);

  useEffect(() => {
    const sseManager = new ServerSentEventsManager(config);
    sseManagerRef.current = sseManager;

    const connect = async () => {
      setConnectionState('connecting');
      try {
        await sseManager.connect();
        setConnectionState('connected');
      } catch (error) {
        setConnectionState('error');
        console.error('SSE connection failed:', error);
      }
    };

    connect();

    return () => {
      sseManager.disconnect();
      setConnectionState('disconnected');
    };
  }, [config.url]);

  const subscribe = useCallback((eventType: string, callback: (event: SSEEvent) => void) => {
    return sseManagerRef.current?.subscribe(eventType, (event) => {
      setLastEvent(event);
      callback(event);
    }) ?? (() => {});
  }, []);

  return {
    subscribe,
    connectionState,
    lastEvent,
    isConnected: connectionState === 'connected'
  };
};

// Specific hook for live data feeds
export const useLiveDataFeed = <T>(
  config: SSEConfig,
  eventType: string = 'update',
  transformer?: (data: any) => T
) => {
  const [data, setData] = useState<T[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const { subscribe, connectionState } = useServerSentEvents(config);

  useEffect(() => {
    const unsubscribe = subscribe(eventType, (event) => {
      try {
        const newData = transformer ? transformer(event.data) : event.data;
        setData(prev => [newData, ...prev].slice(0, 100)); // Keep last 100 items
        setError(null);
      } catch (err) {
        setError(err as Error);
      }
    });

    return unsubscribe;
  }, [subscribe, eventType, transformer]);

  return { data, error, connectionState };
};
```

### Live Dashboard Implementation

```typescript
{% raw %}
{% raw %}
// components/Dashboard/LiveDashboard.tsx
interface DashboardMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  timestamp: number;
}

interface DashboardAlert {
  id: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  timestamp: number;
}

const LiveDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetric[]>([]);
  const [alerts, setAlerts] = useState<DashboardAlert[]>([]);
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);

  const { subscribe, isConnected } = useServerSentEvents({
    url: '/api/dashboard/stream',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });

  useEffect(() => {
    if (!isAutoRefresh) return;

    const unsubscribers = [
      subscribe('metrics', (event) => {
        const newMetrics: DashboardMetric[] = event.data;
        setMetrics(newMetrics);
      }),
      
      subscribe('alert', (event) => {
        const alert: DashboardAlert = event.data;
        setAlerts(prev => [alert, ...prev].slice(0, 50));
        
        // Show browser notification for critical alerts
        if (alert.level === 'error' && 'Notification' in window) {
          new Notification(`Critical Alert: ${alert.message}`);
        }
      }),
      
      subscribe('heartbeat', (event) => {
        console.log('Dashboard heartbeat:', event.data.timestamp);
      })
    ];

    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [subscribe, isAutoRefresh]);

  return (
    <div className="live-dashboard">
      <div className="dashboard-header">
        <h1>Live Dashboard</h1>
        <div className="dashboard-controls">
          <button
            onClick={() => setIsAutoRefresh(!isAutoRefresh)}
            className={isAutoRefresh ? 'active' : ''}
          >
            {isAutoRefresh ? 'Pause' : 'Resume'} Updates
          </button>
          <div className="connection-indicator">
            <span className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        {metrics.map(metric => (
          <MetricCard key={metric.id} metric={metric} />
        ))}
      </div>

      <div className="alerts-section">
        <h2>Recent Alerts</h2>
        <div className="alerts-list">
          {alerts.map(alert => (
            <AlertItem key={alert.id} alert={alert} />
          ))}
        </div>
      </div>
    </div>
  );
};

// components/Dashboard/MetricCard.tsx
const MetricCard: React.FC<{ metric: DashboardMetric }> = ({ metric }) => {
  const [previousValue, setPreviousValue] = useState(metric.value);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (metric.value !== previousValue) {
      setIsAnimating(true);
      setPreviousValue(metric.value);
      
      const timer = setTimeout(() => setIsAnimating(false), 500);
      return () => clearTimeout(timer);
    }
  }, [metric.value, previousValue]);

  const getTrendIcon = () => {
    switch (metric.trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      default: return '➡️';
    }
  };

  return (
    <div className={`metric-card ${metric.trend} ${isAnimating ? 'updating' : ''}`}>
      <div className="metric-header">
        <h3>{metric.name}</h3>
        <span className="trend-icon">{getTrendIcon()}</span>
      </div>
      <div className="metric-value">
        <span className="value">{metric.value.toLocaleString()}</span>
        <span className="unit">{metric.unit}</span>
      </div>
      <div className="metric-timestamp">
        Last updated: {new Date(metric.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
};
{% endraw %}
{% endraw %}
```

## Connection Management

### Connection State Management

```typescript
// contexts/RealtimeContext.tsx
interface RealtimeContextType {
  connections: Map<string, WebSocketManager | ServerSentEventsManager>;
  connectionStates: Map<string, 'connecting' | 'connected' | 'disconnected' | 'error'>;
  createConnection: (id: string, config: any, type: 'ws' | 'sse') => void;
  removeConnection: (id: string) => void;
  getConnection: (id: string) => WebSocketManager | ServerSentEventsManager | null;
}

export const RealtimeContext = createContext<RealtimeContextType | null>(null);

export const RealtimeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [connections] = useState(new Map());
  const [connectionStates] = useState(new Map());

  const createConnection = useCallback((id: string, config: any, type: 'ws' | 'sse') => {
    // Remove existing connection if any
    const existing = connections.get(id);
    if (existing) {
      existing.disconnect();
    }

    // Create new connection
    const connection = type === 'ws' 
      ? new WebSocketManager(config)
      : new ServerSentEventsManager(config);
    
    connections.set(id, connection);
    connectionStates.set(id, 'connecting');

    // Connect and update state
    connection.connect()
      .then(() => connectionStates.set(id, 'connected'))
      .catch(() => connectionStates.set(id, 'error'));
  }, [connections, connectionStates]);

  const removeConnection = useCallback((id: string) => {
    const connection = connections.get(id);
    if (connection) {
      connection.disconnect();
      connections.delete(id);
      connectionStates.delete(id);
    }
  }, [connections, connectionStates]);

  const getConnection = useCallback((id: string) => {
    return connections.get(id) || null;
  }, [connections]);

  useEffect(() => {
    // Cleanup all connections on unmount
    return () => {
      connections.forEach(connection => connection.disconnect());
      connections.clear();
      connectionStates.clear();
    };
  }, [connections, connectionStates]);

  return (
    <RealtimeContext.Provider value={{
      connections,
      connectionStates,
      createConnection,
      removeConnection,
      getConnection
    }}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtimeContext = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtimeContext must be used within RealtimeProvider');
  }
  return context;
};
```

### Connection Pool Management

```typescript
// utils/connectionPool.ts
interface ConnectionPoolConfig {
  maxConnections: number;
  idleTimeout: number;
  healthCheckInterval: number;
}

interface PooledConnection {
  id: string;
  connection: WebSocketManager | ServerSentEventsManager;
  lastUsed: number;
  isActive: boolean;
  subscribers: number;
}

export class RealtimeConnectionPool {
  private pool = new Map<string, PooledConnection>();
  private cleanupTimer: NodeJS.Timeout | null = null;

  constructor(private config: ConnectionPoolConfig) {
    this.startCleanupTimer();
  }

  async getConnection(
    id: string,
    connectionConfig: any,
    type: 'ws' | 'sse'
  ): Promise<WebSocketManager | ServerSentEventsManager> {
    let pooled = this.pool.get(id);

    if (pooled && pooled.isActive) {
      pooled.lastUsed = Date.now();
      pooled.subscribers++;
      return pooled.connection;
    }

    // Create new connection if pool limit not reached
    if (this.pool.size >= this.config.maxConnections) {
      this.evictOldestConnection();
    }

    const connection = type === 'ws'
      ? new WebSocketManager(connectionConfig)
      : new ServerSentEventsManager(connectionConfig);

    await connection.connect();

    pooled = {
      id,
      connection,
      lastUsed: Date.now(),
      isActive: true,
      subscribers: 1
    };

    this.pool.set(id, pooled);
    return connection;
  }

  releaseConnection(id: string): void {
    const pooled = this.pool.get(id);
    if (pooled) {
      pooled.subscribers = Math.max(0, pooled.subscribers - 1);
      pooled.lastUsed = Date.now();
    }
  }

  private evictOldestConnection(): void {
    let oldestId = '';
    let oldestTime = Date.now();

    this.pool.forEach((pooled, id) => {
      if (pooled.subscribers === 0 && pooled.lastUsed < oldestTime) {
        oldestTime = pooled.lastUsed;
        oldestId = id;
      }
    });

    if (oldestId) {
      this.removeConnection(oldestId);
    }
  }

  private removeConnection(id: string): void {
    const pooled = this.pool.get(id);
    if (pooled) {
      pooled.connection.disconnect();
      this.pool.delete(id);
    }
  }

  private startCleanupTimer(): void {
    this.cleanupTimer = setInterval(() => {
      const now = Date.now();
      const toRemove: string[] = [];

      this.pool.forEach((pooled, id) => {
        if (
          pooled.subscribers === 0 &&
          now - pooled.lastUsed > this.config.idleTimeout
        ) {
          toRemove.push(id);
        }
      });

      toRemove.forEach(id => this.removeConnection(id));
    }, this.config.healthCheckInterval);
  }

  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
    }
    this.pool.forEach(pooled => pooled.connection.disconnect());
    this.pool.clear();
  }
}

export const connectionPool = new RealtimeConnectionPool({
  maxConnections: 10,
  idleTimeout: 300000, // 5 minutes
  healthCheckInterval: 60000 // 1 minute
});
```

## Authentication & Security

### Secure Real-time Connections

```typescript
// utils/secureConnection.ts
interface AuthConfig {
  tokenProvider: () => Promise<string>;
  refreshThreshold: number; // Time before expiry to refresh
  maxRetries: number;
}

export class SecureWebSocketManager extends WebSocketManager {
  private authConfig: AuthConfig;
  private currentToken: string | null = null;
  private tokenExpiry: number | null = null;
  private refreshTimer: NodeJS.Timeout | null = null;

  constructor(config: WebSocketConfig & { auth: AuthConfig }) {
    super(config);
    this.authConfig = config.auth;
  }

  async connect(): Promise<void> {
    await this.ensureValidToken();
    
    // Add token to WebSocket URL
    const urlWithToken = new URL(this.config.url);
    urlWithToken.searchParams.set('token', this.currentToken!);
    
    const secureConfig = {
      ...this.config,
      url: urlWithToken.toString()
    };

    return super.connect.call(this, secureConfig);
  }

  private async ensureValidToken(): Promise<void> {
    const now = Date.now();
    
    if (!this.currentToken || !this.tokenExpiry || 
        now >= this.tokenExpiry - this.authConfig.refreshThreshold) {
      await this.refreshToken();
    }
  }

  private async refreshToken(): Promise<void> {
    try {
      const token = await this.authConfig.tokenProvider();
      
      // Decode JWT to get expiry (simplified)
      const payload = JSON.parse(atob(token.split('.')[1]));
      
      this.currentToken = token;
      this.tokenExpiry = payload.exp * 1000; // Convert to milliseconds
      
      this.scheduleTokenRefresh();
      
    } catch (error) {
      console.error('Failed to refresh token:', error);
      throw error;
    }
  }

  private scheduleTokenRefresh(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }

    if (this.tokenExpiry) {
      const refreshTime = this.tokenExpiry - Date.now() - this.authConfig.refreshThreshold;
      
      if (refreshTime > 0) {
        this.refreshTimer = setTimeout(() => {
          this.refreshToken().catch(console.error);
        }, refreshTime);
      }
    }
  }

  disconnect(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
    super.disconnect();
  }
}

// Message encryption/decryption
export class EncryptedMessageHandler {
  private key: CryptoKey | null = null;

  async initialize(keyMaterial: string): Promise<void> {
    const encoder = new TextEncoder();
    const keyData = encoder.encode(keyMaterial);
    
    this.key = await crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'AES-GCM' },
      false,
      ['encrypt', 'decrypt']
    );
  }

  async encryptMessage(message: any): Promise<string> {
    if (!this.key) throw new Error('Encryption key not initialized');

    const encoder = new TextEncoder();
    const data = encoder.encode(JSON.stringify(message));
    
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      this.key,
      data
    );

    const result = new Uint8Array(iv.length + encrypted.byteLength);
    result.set(iv);
    result.set(new Uint8Array(encrypted), iv.length);
    
    return btoa(String.fromCharCode(...result));
  }

  async decryptMessage(encryptedData: string): Promise<any> {
    if (!this.key) throw new Error('Encryption key not initialized');

    const data = new Uint8Array(
      atob(encryptedData).split('').map(char => char.charCodeAt(0))
    );
    
    const iv = data.slice(0, 12);
    const encrypted = data.slice(12);
    
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      this.key,
      encrypted
    );

    const decoder = new TextDecoder();
    return JSON.parse(decoder.decode(decrypted));
  }
}
```

## Performance Optimization

### Message Batching and Throttling

```typescript
// utils/messageOptimization.ts
interface BatchingConfig {
  batchSize: number;
  flushInterval: number;
  priority: 'size' | 'time' | 'adaptive';
}

export class MessageBatcher {
  private queue: any[] = [];
  private flushTimer: NodeJS.Timeout | null = null;
  private onFlush: (messages: any[]) => void;

  constructor(
    private config: BatchingConfig,
    onFlush: (messages: any[]) => void
  ) {
    this.onFlush = onFlush;
  }

  add(message: any): void {
    this.queue.push({
      ...message,
      timestamp: Date.now()
    });

    if (this.shouldFlush()) {
      this.flush();
    } else if (!this.flushTimer) {
      this.scheduleFlush();
    }
  }

  private shouldFlush(): boolean {
    switch (this.config.priority) {
      case 'size':
        return this.queue.length >= this.config.batchSize;
      case 'time':
        return false; // Always wait for timer
      case 'adaptive':
        const oldestMessage = this.queue[0];
        const age = Date.now() - oldestMessage?.timestamp;
        return this.queue.length >= this.config.batchSize || age > this.config.flushInterval;
      default:
        return this.queue.length >= this.config.batchSize;
    }
  }

  private scheduleFlush(): void {
    this.flushTimer = setTimeout(() => {
      this.flush();
    }, this.config.flushInterval);
  }

  private flush(): void {
    if (this.queue.length === 0) return;

    const messages = this.queue.splice(0);
    this.onFlush(messages);

    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
  }

  destroy(): void {
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
    }
    this.flush(); // Flush remaining messages
  }
}

// Throttling utility
export class MessageThrottler {
  private lastExecution = 0;
  private timeoutId: NodeJS.Timeout | null = null;

  constructor(private delay: number) {}

  throttle<T extends any[]>(func: (...args: T) => void): (...args: T) => void {
    return (...args: T) => {
      const now = Date.now();

      if (now - this.lastExecution >= this.delay) {
        this.lastExecution = now;
        func(...args);
      } else {
        if (this.timeoutId) {
          clearTimeout(this.timeoutId);
        }

        this.timeoutId = setTimeout(() => {
          this.lastExecution = Date.now();
          func(...args);
        }, this.delay - (now - this.lastExecution));
      }
    };
  }
}

// React hook for optimized real-time updates
export const useOptimizedRealtime = <T>(
  config: {
    wsConfig: WebSocketConfig;
    eventType: string;
    batchingConfig?: BatchingConfig;
    throttleDelay?: number;
  }
) => {
  const [data, setData] = useState<T[]>([]);
  const batcherRef = useRef<MessageBatcher | null>(null);
  const throttlerRef = useRef<MessageThrottler | null>(null);

  useEffect(() => {
    // Initialize batching if configured
    if (config.batchingConfig) {
      batcherRef.current = new MessageBatcher(
        config.batchingConfig,
        (messages) => {
          setData(prev => [...messages.map(m => m.payload), ...prev]);
        }
      );
    }

    // Initialize throttling if configured
    if (config.throttleDelay) {
      throttlerRef.current = new MessageThrottler(config.throttleDelay);
    }

    return () => {
      batcherRef.current?.destroy();
    };
  }, [config]);

  const { subscribe } = useWebSocket(config.wsConfig);

  useEffect(() => {
    const handleMessage = (payload: T) => {
      if (batcherRef.current) {
        batcherRef.current.add({ payload });
      } else if (throttlerRef.current) {
        const throttledUpdate = throttlerRef.current.throttle((data: T) => {
          setData(prev => [data, ...prev]);
        });
        throttledUpdate(payload);
      } else {
        setData(prev => [payload, ...prev]);
      }
    };

    return subscribe(config.eventType, handleMessage);
  }, [subscribe, config.eventType]);

  return data;
};
```

## Testing Real-time Features

### WebSocket Testing

```typescript
// __tests__/utils/websocket.test.ts
import { WebSocketManager } from '../utils/websocket';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(public url: string, public protocols?: string[]) {
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 10);
  }

  send(data: string): void {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
    // Echo the message back for testing
    setTimeout(() => {
      this.onmessage?.(new MessageEvent('message', { data }));
    }, 5);
  }

  close(code?: number, reason?: string): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close', { code, reason, wasClean: true }));
  }
}

// Setup mock
global.WebSocket = MockWebSocket as any;

describe('WebSocketManager', () => {
  let wsManager: WebSocketManager;

  beforeEach(() => {
    wsManager = new WebSocketManager({
      url: 'ws://localhost:8080',
      reconnectAttempts: 3
    });
  });

  afterEach(async () => {
    wsManager.disconnect();
  });

  it('should connect successfully', async () => {
    await wsManager.connect();
    expect(wsManager.isConnected).toBe(true);
  });

  it('should send and receive messages', async () => {
    await wsManager.connect();

    const receivedMessages: any[] = [];
    const unsubscribe = wsManager.subscribe('test', (data) => {
      receivedMessages.push(data);
    });

    wsManager.send({ type: 'test', payload: { message: 'hello' } });

    // Wait for message to be processed
    await new Promise(resolve => setTimeout(resolve, 20));

    expect(receivedMessages).toHaveLength(1);
    expect(receivedMessages[0]).toEqual({ message: 'hello' });

    unsubscribe();
  });

  it('should handle connection errors', async () => {
    // Mock connection failure
    global.WebSocket = class extends MockWebSocket {
      constructor(url: string) {
        super(url);
        setTimeout(() => {
          this.onerror?.(new Event('error'));
        }, 5);
      }
    } as any;

    wsManager = new WebSocketManager({
      url: 'ws://localhost:8080',
      reconnectAttempts: 1
    });

    await expect(wsManager.connect()).rejects.toThrow();
  });
});
```

### SSE Testing

```typescript
// __tests__/utils/sse.test.ts
import { ServerSentEventsManager } from '../utils/serverSentEvents';

// Mock EventSource
class MockEventSource {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 2;

  readyState = MockEventSource.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  
  private listeners = new Map<string, ((event: MessageEvent) => void)[]>();

  constructor(public url: string, public config?: EventSourceInit) {
    setTimeout(() => {
      this.readyState = MockEventSource.OPEN;
      this.onopen?.(new Event('open'));
    }, 10);
  }

  addEventListener(type: string, listener: (event: MessageEvent) => void): void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(listener);
  }

  removeEventListener(type: string, listener: (event: MessageEvent) => void): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  close(): void {
    this.readyState = MockEventSource.CLOSED;
  }

  // Test helper to simulate events
  simulate(type: string, data: any, eventType = 'message'): void {
    const event = new MessageEvent(eventType, {
      data: typeof data === 'string' ? data : JSON.stringify(data),
      lastEventId: Date.now().toString()
    });

    if (type === 'message') {
      this.onmessage?.(event);
    } else {
      const listeners = this.listeners.get(type);
      listeners?.forEach(listener => listener(event));
    }
  }
}

global.EventSource = MockEventSource as any;

describe('ServerSentEventsManager', () => {
  let sseManager: ServerSentEventsManager;
  let mockEventSource: MockEventSource;

  beforeEach(() => {
    sseManager = new ServerSentEventsManager({
      url: 'http://localhost:3000/events'
    });
  });

  afterEach(() => {
    sseManager.disconnect();
  });

  it('should connect and receive events', async () => {
    await sseManager.connect();
    expect(sseManager.isConnected).toBe(true);

    const receivedEvents: any[] = [];
    const unsubscribe = sseManager.subscribe('update', (event) => {
      receivedEvents.push(event);
    });

    // Get the mock instance
    mockEventSource = (global.EventSource as any).prototype.constructor.instances?.[0];
    
    // Simulate an event
    mockEventSource.simulate('update', { value: 42 });

    expect(receivedEvents).toHaveLength(1);
    expect(receivedEvents[0].data).toEqual({ value: 42 });

    unsubscribe();
  });
});
```

### Component Testing

```typescript
// __tests__/components/LiveDashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { LiveDashboard } from '../components/Dashboard/LiveDashboard';

// Mock the SSE hook
jest.mock('../hooks/useServerSentEvents', () => ({
  useServerSentEvents: jest.fn(() => ({
    subscribe: jest.fn(() => () => {}),
    isConnected: true,
    connectionState: 'connected',
    lastEvent: null
  }))
}));

describe('LiveDashboard', () => {
  it('should render dashboard with connection status', () => {
    render(<LiveDashboard />);
    
    expect(screen.getByText('Live Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Live')).toBeInTheDocument();
  });

  it('should handle metric updates', async () => {
    const mockSubscribe = jest.fn();
    const { useServerSentEvents } = require('../hooks/useServerSentEvents');
    
    useServerSentEvents.mockReturnValue({
      subscribe: mockSubscribe,
      isConnected: true,
      connectionState: 'connected',
      lastEvent: null
    });

    render(<LiveDashboard />);

    // Simulate metrics subscription call
    expect(mockSubscribe).toHaveBeenCalledWith('metrics', expect.any(Function));
    
    // Get the callback and simulate data
    const metricsCallback = mockSubscribe.mock.calls.find(
      call => call[0] === 'metrics'
    )[1];

    const mockMetrics = [
      {
        id: '1',
        name: 'CPU Usage',
        value: 75,
        unit: '%',
        trend: 'up',
        timestamp: Date.now()
      }
    ];

    // Simulate receiving metrics
    metricsCallback({ data: mockMetrics });

    await waitFor(() => {
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
      expect(screen.getByText('75')).toBeInTheDocument();
    });
  });
});
```

This comprehensive guide covers real-time data handling with WebSockets and Server-Sent Events in React applications, from basic implementation through advanced patterns, security, performance optimization, and testing strategies.
