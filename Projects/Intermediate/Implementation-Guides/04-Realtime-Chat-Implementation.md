# 🔄 Real-time Chat with WebSockets Implementation Guide

> **Project**: Real-time Chat Application with WebSocket Integration  
> **Level**: Intermediate  
> **Estimated Time**: 7-9 hours  
> **Focus**: WebSocket integration, real-time features, event handling

---

## 🚀 Quick Start (30 minutes)

### Step 1: Setup Project
```bash
npx create-react-app realtime-chat-app
cd realtime-chat-app
npm install socket.io-client uuid date-fns
npm start
```

### Step 2: Mock WebSocket Server Setup
For development, we'll create a mock WebSocket server simulation:

```jsx
// src/services/mockWebSocketServer.js
class MockWebSocketServer {
  constructor() {
    this.clients = new Map();
    this.rooms = new Map();
    this.messages = new Map();
    this.isRunning = false;
  }

  start() {
    this.isRunning = true;
    console.log('Mock WebSocket server started');
    
    // Simulate some initial data
    this.rooms.set('general', {
      id: 'general',
      name: 'General',
      description: 'General discussion',
      members: []
    });
    
    this.rooms.set('tech', {
      id: 'tech',
      name: 'Tech Talk',
      description: 'Technology discussions',
      members: []
    });

    this.messages.set('general', []);
    this.messages.set('tech', []);
  }

  addClient(clientId, socketMock) {
    this.clients.set(clientId, {
      id: clientId,
      socket: socketMock,
      rooms: ['general'],
      user: null
    });
  }

  removeClient(clientId) {
    const client = this.clients.get(clientId);
    if (client) {
      // Notify other clients that user left
      client.rooms.forEach(roomId => {
        this.broadcastToRoom(roomId, 'user:left', {
          userId: clientId,
          user: client.user
        }, clientId);
      });
    }
    this.clients.delete(clientId);
  }

  joinRoom(clientId, roomId) {
    const client = this.clients.get(clientId);
    if (client && this.rooms.has(roomId)) {
      if (!client.rooms.includes(roomId)) {
        client.rooms.push(roomId);
      }
      
      const room = this.rooms.get(roomId);
      if (!room.members.includes(clientId)) {
        room.members.push(clientId);
      }

      // Send room data to client
      client.socket.receive('room:joined', {
        room,
        messages: this.messages.get(roomId) || []
      });

      // Notify other clients
      this.broadcastToRoom(roomId, 'user:joined', {
        userId: clientId,
        user: client.user
      }, clientId);
    }
  }

  sendMessage(clientId, data) {
    const client = this.clients.get(clientId);
    if (!client) return;

    const message = {
      id: Date.now().toString(),
      content: data.content,
      user: client.user,
      timestamp: new Date().toISOString(),
      roomId: data.roomId,
      type: data.type || 'text'
    };

    // Store message
    if (!this.messages.has(data.roomId)) {
      this.messages.set(data.roomId, []);
    }
    this.messages.get(data.roomId).push(message);

    // Broadcast to all clients in room
    this.broadcastToRoom(data.roomId, 'message:received', message);
  }

  broadcastToRoom(roomId, event, data, excludeClientId = null) {
    this.clients.forEach((client, clientId) => {
      if (clientId !== excludeClientId && client.rooms.includes(roomId)) {
        client.socket.receive(event, data);
      }
    });
  }

  setUserInfo(clientId, user) {
    const client = this.clients.get(clientId);
    if (client) {
      client.user = user;
    }
  }

  simulateTyping(clientId, roomId, isTyping) {
    const client = this.clients.get(clientId);
    if (!client) return;

    this.broadcastToRoom(roomId, 'user:typing', {
      userId: clientId,
      user: client.user,
      isTyping,
      roomId
    }, clientId);
  }
}

export const mockServer = new MockWebSocketServer();
```

### Step 3: WebSocket Client Service
```jsx
// src/services/webSocketService.js
import { mockServer } from './mockWebSocketServer';

class WebSocketClient {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.connected = false;
    this.clientId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect(user) {
    return new Promise((resolve, reject) => {
      try {
        // In a real app, you'd connect to actual WebSocket server
        // For demo, we'll use our mock server
        this.clientId = `client_${Date.now()}`;
        
        // Create mock socket interface
        this.socket = {
          receive: (event, data) => {
            this.handleMessage(event, data);
          },
          
          send: (event, data) => {
            this.handleOutgoingMessage(event, data);
          },
          
          close: () => {
            this.disconnect();
          }
        };

        // Start mock server if not running
        if (!mockServer.isRunning) {
          mockServer.start();
        }

        // Register client with mock server
        mockServer.addClient(this.clientId, this.socket);
        mockServer.setUserInfo(this.clientId, user);

        this.connected = true;
        this.reconnectAttempts = 0;

        // Simulate connection delay
        setTimeout(() => {
          this.emit('connected', { user });
          resolve();
        }, 500);

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect() {
    if (this.clientId) {
      mockServer.removeClient(this.clientId);
    }
    
    this.connected = false;
    this.socket = null;
    this.clientId = null;
    this.emit('disconnected');
  }

  handleMessage(event, data) {
    this.emit(event, data);
  }

  handleOutgoingMessage(event, data) {
    if (!this.connected) return;

    switch (event) {
      case 'message:send':
        mockServer.sendMessage(this.clientId, data);
        break;
      case 'room:join':
        mockServer.joinRoom(this.clientId, data.roomId);
        break;
      case 'user:typing':
        mockServer.simulateTyping(this.clientId, data.roomId, data.isTyping);
        break;
      default:
        console.log('Unhandled outgoing event:', event, data);
    }
  }

  // Event handling
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  off(event, callback) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('Error in event callback:', error);
      }
    });
  }

  // Public methods
  sendMessage(roomId, content, type = 'text') {
    this.socket?.send('message:send', { roomId, content, type });
  }

  joinRoom(roomId) {
    this.socket?.send('room:join', { roomId });
  }

  setTyping(roomId, isTyping) {
    this.socket?.send('user:typing', { roomId, isTyping });
  }

  // Connection status
  isConnected() {
    return this.connected;
  }

  // Simulate reconnection for demo
  attemptReconnect(user) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.emit('reconnect:failed');
      return;
    }

    this.reconnectAttempts++;
    this.emit('reconnecting', { attempt: this.reconnectAttempts });

    setTimeout(() => {
      this.connect(user)
        .then(() => {
          this.emit('reconnected');
        })
        .catch(() => {
          this.attemptReconnect(user);
        });
    }, this.reconnectDelay * this.reconnectAttempts);
  }
}

export const webSocketService = new WebSocketClient();
```

### Step 4: WebSocket Hook
```jsx
// src/hooks/useWebSocket.js
import { useEffect, useRef, useCallback, useState } from 'react';
import { webSocketService } from '../services/webSocketService';

export const useWebSocket = (user) => {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [reconnecting, setReconnecting] = useState(false);
  const listenersRef = useRef([]);

  // Connect to WebSocket
  const connect = useCallback(async () => {
    if (!user || connecting || connected) return;

    setConnecting(true);
    setError(null);

    try {
      await webSocketService.connect(user);
      setConnected(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setConnecting(false);
    }
  }, [user, connecting, connected]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    webSocketService.disconnect();
    setConnected(false);
    setReconnecting(false);
  }, []);

  // Subscribe to WebSocket events
  const subscribe = useCallback((event, callback) => {
    const unsubscribe = webSocketService.on(event, callback);
    listenersRef.current.push(unsubscribe);
    return unsubscribe;
  }, []);

  // Send message
  const sendMessage = useCallback((roomId, content, type = 'text') => {
    if (connected) {
      webSocketService.sendMessage(roomId, content, type);
    }
  }, [connected]);

  // Join room
  const joinRoom = useCallback((roomId) => {
    if (connected) {
      webSocketService.joinRoom(roomId);
    }
  }, [connected]);

  // Set typing status
  const setTyping = useCallback((roomId, isTyping) => {
    if (connected) {
      webSocketService.setTyping(roomId, isTyping);
    }
  }, [connected]);

  // Setup connection event listeners
  useEffect(() => {
    const unsubscribeConnected = webSocketService.on('connected', () => {
      setConnected(true);
      setConnecting(false);
      setError(null);
    });

    const unsubscribeDisconnected = webSocketService.on('disconnected', () => {
      setConnected(false);
      setReconnecting(false);
    });

    const unsubscribeReconnecting = webSocketService.on('reconnecting', ({ attempt }) => {
      setReconnecting(true);
      setConnected(false);
    });

    const unsubscribeReconnected = webSocketService.on('reconnected', () => {
      setReconnecting(false);
      setConnected(true);
      setError(null);
    });

    const unsubscribeReconnectFailed = webSocketService.on('reconnect:failed', () => {
      setReconnecting(false);
      setError('Failed to reconnect after multiple attempts');
    });

    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeReconnecting();
      unsubscribeReconnected();
      unsubscribeReconnectFailed();
    };
  }, []);

  // Auto-connect when user is available
  useEffect(() => {
    if (user && !connected && !connecting) {
      connect();
    }
  }, [user, connected, connecting, connect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Clean up all listeners
      listenersRef.current.forEach(unsubscribe => unsubscribe());
      listenersRef.current = [];
      
      // Disconnect
      disconnect();
    };
  }, [disconnect]);

  return {
    connected,
    connecting,
    reconnecting,
    error,
    connect,
    disconnect,
    subscribe,
    sendMessage,
    joinRoom,
    setTyping
  };
};
```

### Step 5: Real-time Chat Component
```jsx
// src/components/RealTimeChat.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import ChatRoom from './Chat/ChatRoom';
import UserAuth from './Auth/UserAuth';
import ConnectionStatus from './Connection/ConnectionStatus';
import './RealTimeChat.css';

const RealTimeChat = () => {
  const [user, setUser] = useState(null);
  const [currentRoom, setCurrentRoom] = useState('general');
  const [messages, setMessages] = useState({});
  const [rooms, setRooms] = useState({});
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [typingUsers, setTypingUsers] = useState({});

  const {
    connected,
    connecting,
    reconnecting,
    error,
    subscribe,
    sendMessage,
    joinRoom,
    setTyping
  } = useWebSocket(user);

  // Handle incoming messages
  useEffect(() => {
    if (!connected) return;

    const unsubscribeMessage = subscribe('message:received', (message) => {
      setMessages(prev => ({
        ...prev,
        [message.roomId]: [...(prev[message.roomId] || []), message]
      }));
    });

    const unsubscribeRoomJoined = subscribe('room:joined', ({ room, messages: roomMessages }) => {
      setRooms(prev => ({ ...prev, [room.id]: room }));
      setMessages(prev => ({ ...prev, [room.id]: roomMessages }));
    });

    const unsubscribeUserJoined = subscribe('user:joined', ({ user: joinedUser }) => {
      setOnlineUsers(prev => {
        if (prev.find(u => u.id === joinedUser.id)) return prev;
        return [...prev, joinedUser];
      });
    });

    const unsubscribeUserLeft = subscribe('user:left', ({ user: leftUser }) => {
      setOnlineUsers(prev => prev.filter(u => u.id !== leftUser.id));
    });

    const unsubscribeTyping = subscribe('user:typing', ({ user: typingUser, isTyping, roomId }) => {
      setTypingUsers(prev => ({
        ...prev,
        [roomId]: {
          ...prev[roomId],
          [typingUser.id]: isTyping ? typingUser : undefined
        }
      }));

      // Clear typing after 3 seconds
      if (isTyping) {
        setTimeout(() => {
          setTypingUsers(prev => ({
            ...prev,
            [roomId]: {
              ...prev[roomId],
              [typingUser.id]: undefined
            }
          }));
        }, 3000);
      }
    });

    return () => {
      unsubscribeMessage();
      unsubscribeRoomJoined();
      unsubscribeUserJoined();
      unsubscribeUserLeft();
      unsubscribeTyping();
    };
  }, [connected, subscribe]);

  // Join initial room when connected
  useEffect(() => {
    if (connected && currentRoom) {
      joinRoom(currentRoom);
    }
  }, [connected, currentRoom, joinRoom]);

  const handleUserLogin = useCallback((userData) => {
    setUser(userData);
  }, []);

  const handleSendMessage = useCallback((content, type = 'text') => {
    if (content.trim() && currentRoom) {
      sendMessage(currentRoom, content, type);
    }
  }, [currentRoom, sendMessage]);

  const handleRoomChange = useCallback((roomId) => {
    setCurrentRoom(roomId);
    if (connected) {
      joinRoom(roomId);
    }
  }, [connected, joinRoom]);

  const handleTyping = useCallback((isTyping) => {
    if (currentRoom) {
      setTyping(currentRoom, isTyping);
    }
  }, [currentRoom, setTyping]);

  if (!user) {
    return <UserAuth onLogin={handleUserLogin} />;
  }

  return (
    <div className="realtime-chat">
      <ConnectionStatus 
        connected={connected}
        connecting={connecting}
        reconnecting={reconnecting}
        error={error}
      />
      
      <ChatRoom
        user={user}
        currentRoom={currentRoom}
        rooms={rooms}
        messages={messages[currentRoom] || []}
        onlineUsers={onlineUsers}
        typingUsers={Object.values(typingUsers[currentRoom] || {}).filter(Boolean)}
        onSendMessage={handleSendMessage}
        onRoomChange={handleRoomChange}
        onTyping={handleTyping}
        connected={connected}
      />
    </div>
  );
};

export default RealTimeChat;
```

---

## 📚 Complete Implementation

### 1. Advanced WebSocket Features

#### Enhanced WebSocket Service
```jsx
// src/services/webSocketService.js (Enhanced version)
class EnhancedWebSocketClient {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.connected = false;
    this.clientId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.heartbeatInterval = null;
    this.lastHeartbeat = null;
    this.messageQueue = [];
    this.typingTimeout = null;
  }

  connect(user) {
    return new Promise((resolve, reject) => {
      try {
        this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Create enhanced mock socket
        this.socket = {
          receive: (event, data) => {
            this.handleMessage(event, data);
          },
          
          send: (event, data) => {
            this.handleOutgoingMessage(event, data);
          },
          
          close: () => {
            this.disconnect();
          }
        };

        // Enhanced mock server setup
        if (!mockServer.isRunning) {
          mockServer.start();
        }

        mockServer.addClient(this.clientId, this.socket);
        mockServer.setUserInfo(this.clientId, user);

        this.connected = true;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.processMessageQueue();

        setTimeout(() => {
          this.emit('connected', { user });
          resolve();
        }, 300);

      } catch (error) {
        reject(error);
      }
    });
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.connected) {
        this.lastHeartbeat = Date.now();
        this.socket?.send('heartbeat', { timestamp: this.lastHeartbeat });
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  processMessageQueue() {
    while (this.messageQueue.length > 0 && this.connected) {
      const { event, data } = this.messageQueue.shift();
      this.socket?.send(event, data);
    }
  }

  queueMessage(event, data) {
    this.messageQueue.push({ event, data });
    
    // Limit queue size
    if (this.messageQueue.length > 100) {
      this.messageQueue = this.messageQueue.slice(-50);
    }
  }

  handleOutgoingMessage(event, data) {
    if (!this.connected) {
      // Queue messages when disconnected
      this.queueMessage(event, data);
      return;
    }

    switch (event) {
      case 'message:send':
        mockServer.sendMessage(this.clientId, data);
        break;
      case 'room:join':
        mockServer.joinRoom(this.clientId, data.roomId);
        break;
      case 'user:typing':
        this.handleTyping(data);
        break;
      case 'message:edit':
        mockServer.editMessage(this.clientId, data);
        break;
      case 'message:delete':
        mockServer.deleteMessage(this.clientId, data);
        break;
      case 'heartbeat':
        // Handle heartbeat response
        break;
      default:
        console.log('Unhandled outgoing event:', event, data);
    }
  }

  handleTyping(data) {
    // Clear previous typing timeout
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
    }

    mockServer.simulateTyping(this.clientId, data.roomId, data.isTyping);

    // Auto-clear typing after 3 seconds
    if (data.isTyping) {
      this.typingTimeout = setTimeout(() => {
        mockServer.simulateTyping(this.clientId, data.roomId, false);
      }, 3000);
    }
  }

  // Enhanced methods
  sendMessage(roomId, content, type = 'text', metadata = {}) {
    this.socket?.send('message:send', { 
      roomId, 
      content, 
      type, 
      metadata,
      clientTimestamp: Date.now()
    });
  }

  editMessage(messageId, newContent, roomId) {
    this.socket?.send('message:edit', { messageId, newContent, roomId });
  }

  deleteMessage(messageId, roomId) {
    this.socket?.send('message:delete', { messageId, roomId });
  }

  sendFile(roomId, file) {
    // In a real implementation, you'd upload the file first
    // For demo, we'll simulate file sharing
    const fileMessage = {
      roomId,
      content: `[File: ${file.name}]`,
      type: 'file',
      metadata: {
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
        fileUrl: URL.createObjectURL(file) // Demo only
      }
    };
    
    this.socket?.send('message:send', fileMessage);
  }

  sendReaction(messageId, roomId, emoji) {
    this.socket?.send('message:reaction', { messageId, roomId, emoji });
  }

  disconnect() {
    this.stopHeartbeat();
    
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
    }

    if (this.clientId) {
      mockServer.removeClient(this.clientId);
    }
    
    this.connected = false;
    this.socket = null;
    this.clientId = null;
    this.emit('disconnected');
  }

  // Connection quality monitoring
  getConnectionQuality() {
    if (!this.connected) return 'disconnected';
    
    const now = Date.now();
    const timeSinceHeartbeat = now - (this.lastHeartbeat || now);
    
    if (timeSinceHeartbeat < 35000) return 'good';
    if (timeSinceHeartbeat < 60000) return 'poor';
    return 'unstable';
  }
}

export const webSocketService = new EnhancedWebSocketClient();
```

#### Real-time Message Component
```jsx
// src/components/Chat/RealtimeMessage.jsx
import React, { useState, useEffect } from 'react';
import { format, formatDistanceToNow } from 'date-fns';
import MessageReactions from './MessageReactions';
import MessageActions from './MessageActions';
import './RealtimeMessage.css';

const RealtimeMessage = ({ 
  message, 
  isOwnMessage, 
  onEdit, 
  onDelete, 
  onReaction,
  showActions = true 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [showReactions, setShowReactions] = useState(false);
  const [isNew, setIsNew] = useState(true);

  // Highlight new messages briefly
  useEffect(() => {
    const timer = setTimeout(() => setIsNew(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  const handleEdit = () => {
    if (editContent.trim() && editContent !== message.content) {
      onEdit(message.id, editContent.trim(), message.roomId);
    }
    setIsEditing(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleEdit();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setEditContent(message.content);
    }
  };

  const renderContent = () => {
    switch (message.type) {
      case 'file':
        return (
          <div className="message-file">
            <div className="file-icon">📎</div>
            <div className="file-info">
              <div className="file-name">{message.metadata?.fileName}</div>
              <div className="file-size">
                {formatFileSize(message.metadata?.fileSize)}
              </div>
            </div>
            {message.metadata?.fileUrl && (
              <a 
                href={message.metadata.fileUrl} 
                download={message.metadata.fileName}
                className="file-download"
              >
                Download
              </a>
            )}
          </div>
        );
      
      case 'image':
        return (
          <div className="message-image">
            <img 
              src={message.metadata?.imageUrl} 
              alt={message.content}
              className="chat-image"
              loading="lazy"
            />
            {message.content && (
              <div className="image-caption">{message.content}</div>
            )}
          </div>
        );
      
      case 'system':
        return (
          <div className="message-system">
            {message.content}
          </div>
        );
      
      default:
        return isEditing ? (
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            onKeyDown={handleKeyPress}
            onBlur={handleEdit}
            className="message-edit-input"
            autoFocus
          />
        ) : (
          <div className="message-text">
            {message.content}
            {message.edited && (
              <span className="message-edited">(edited)</span>
            )}
          </div>
        );
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  return (
    <div className={`realtime-message ${isOwnMessage ? 'own' : 'other'} ${isNew ? 'new' : ''} ${message.type}`}>
      <div className="message-header">
        <div className="message-user">
          <img 
            src={message.user.avatar} 
            alt={message.user.name}
            className="user-avatar"
          />
          <span className="user-name">{message.user.name}</span>
        </div>
        
        <div className="message-timestamp">
          <span title={format(new Date(message.timestamp), 'PPpp')}>
            {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
          </span>
        </div>
      </div>

      <div className="message-content">
        {renderContent()}
      </div>

      {message.reactions && Object.keys(message.reactions).length > 0 && (
        <MessageReactions 
          reactions={message.reactions}
          onReactionClick={(emoji) => onReaction(message.id, message.roomId, emoji)}
        />
      )}

      {showActions && isOwnMessage && message.type === 'text' && (
        <MessageActions
          onEdit={() => setIsEditing(true)}
          onDelete={() => onDelete(message.id, message.roomId)}
          onReaction={() => setShowReactions(!showReactions)}
        />
      )}

      {showReactions && (
        <div className="reaction-picker">
          {['👍', '❤️', '😂', '😮', '😢', '😡'].map(emoji => (
            <button
              key={emoji}
              onClick={() => {
                onReaction(message.id, message.roomId, emoji);
                setShowReactions(false);
              }}
              className="reaction-button"
            >
              {emoji}
            </button>
          ))}
        </div>
      )}

      {message.deliveryStatus && (
        <div className={`delivery-status ${message.deliveryStatus}`}>
          {message.deliveryStatus === 'sending' && '⏳'}
          {message.deliveryStatus === 'sent' && '✓'}
          {message.deliveryStatus === 'delivered' && '✓✓'}
          {message.deliveryStatus === 'failed' && '❌'}
        </div>
      )}
    </div>
  );
};

export default RealtimeMessage;
```

#### Connection Quality Indicator
```jsx
// src/components/Connection/ConnectionQuality.jsx
import React, { useState, useEffect } from 'react';
import { webSocketService } from '../../services/webSocketService';
import './ConnectionQuality.css';

const ConnectionQuality = () => {
  const [quality, setQuality] = useState('disconnected');
  const [ping, setPing] = useState(null);

  useEffect(() => {
    const checkQuality = () => {
      const currentQuality = webSocketService.getConnectionQuality();
      setQuality(currentQuality);
    };

    // Check quality every 5 seconds
    const interval = setInterval(checkQuality, 5000);
    checkQuality(); // Initial check

    return () => clearInterval(interval);
  }, []);

  const getQualityColor = () => {
    switch (quality) {
      case 'good': return '#4CAF50';
      case 'poor': return '#FF9800';
      case 'unstable': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getQualityIcon = () => {
    switch (quality) {
      case 'good': return '🟢';
      case 'poor': return '🟡';
      case 'unstable': return '🔴';
      default: return '⚫';
    }
  };

  const getQualityText = () => {
    switch (quality) {
      case 'good': return 'Good Connection';
      case 'poor': return 'Poor Connection';
      case 'unstable': return 'Unstable Connection';
      default: return 'Disconnected';
    }
  };

  return (
    <div className="connection-quality" style={{ color: getQualityColor() }}>
      <span className="quality-icon">{getQualityIcon()}</span>
      <span className="quality-text">{getQualityText()}</span>
      {ping && <span className="ping">({ping}ms)</span>}
    </div>
  );
};

export default ConnectionQuality;
```

### 2. Advanced Chat Features

#### Typing Indicator Component
```jsx
// src/components/Chat/TypingIndicator.jsx
import React from 'react';
import './TypingIndicator.css';

const TypingIndicator = ({ typingUsers, currentUser }) => {
  const filteredUsers = typingUsers.filter(user => user.id !== currentUser.id);
  
  if (filteredUsers.length === 0) return null;

  const renderTypingText = () => {
    const names = filteredUsers.map(user => user.name);
    
    if (names.length === 1) {
      return `${names[0]} is typing...`;
    } else if (names.length === 2) {
      return `${names[0]} and ${names[1]} are typing...`;
    } else if (names.length === 3) {
      return `${names[0]}, ${names[1]} and ${names[2]} are typing...`;
    } else {
      return `${names[0]}, ${names[1]} and ${names.length - 2} others are typing...`;
    }
  };

  return (
    <div className="typing-indicator">
      <div className="typing-avatars">
        {filteredUsers.slice(0, 3).map(user => (
          <img
            key={user.id}
            src={user.avatar}
            alt={user.name}
            className="typing-avatar"
          />
        ))}
      </div>
      
      <div className="typing-text">
        {renderTypingText()}
      </div>
      
      <div className="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
};

export default TypingIndicator;
```

#### Enhanced Message Input
```jsx
// src/components/Chat/EnhancedMessageInput.jsx
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useDebounce } from '../../hooks/useDebounce';
import EmojiPicker from './EmojiPicker';
import FileUpload from './FileUpload';
import './EnhancedMessageInput.css';

const EnhancedMessageInput = ({ 
  onSendMessage, 
  onTyping, 
  disabled = false,
  placeholder = "Type a message..." 
}) => {
  const [message, setMessage] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  
  const textareaRef = useRef(null);
  const debouncedMessage = useDebounce(message, 300);

  // Handle typing indicators
  useEffect(() => {
    const wasTyping = isTyping;
    const nowTyping = message.length > 0;
    
    if (wasTyping !== nowTyping) {
      setIsTyping(nowTyping);
      onTyping(nowTyping);
    }
  }, [debouncedMessage, message.length, isTyping, onTyping]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      setIsTyping(false);
      onTyping(false);
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  }, [message, disabled, onSendMessage, onTyping]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  const handleEmojiSelect = useCallback((emoji) => {
    const cursorPosition = textareaRef.current?.selectionStart || message.length;
    const newMessage = message.slice(0, cursorPosition) + emoji + message.slice(cursorPosition);
    setMessage(newMessage);
    
    // Focus back to textarea
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        const newPosition = cursorPosition + emoji.length;
        textareaRef.current.setSelectionRange(newPosition, newPosition);
      }
    }, 0);
  }, [message]);

  const handleFileSelect = useCallback((file) => {
    onSendMessage(`[File: ${file.name}]`, 'file', { file });
    setShowFileUpload(false);
  }, [onSendMessage]);

  const handlePaste = useCallback((e) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let item of items) {
      if (item.type.indexOf('image') !== -1) {
        e.preventDefault();
        const file = item.getAsFile();
        if (file) {
          handleFileSelect(file);
        }
      }
    }
  }, [handleFileSelect]);

  return (
    <div className="enhanced-message-input">
      <form onSubmit={handleSubmit} className="message-form">
        <div className="input-container">
          <button
            type="button"
            onClick={() => setShowFileUpload(!showFileUpload)}
            className="attach-button"
            disabled={disabled}
            title="Attach file"
          >
            📎
          </button>

          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder={disabled ? "Connecting..." : placeholder}
            disabled={disabled}
            className="message-textarea"
            rows={1}
          />

          <button
            type="button"
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
            className="emoji-button"
            disabled={disabled}
            title="Add emoji"
          >
            😊
          </button>

          <button
            type="submit"
            disabled={!message.trim() || disabled}
            className="send-button"
            title="Send message (Enter)"
          >
            📤
          </button>
        </div>

        {showEmojiPicker && (
          <EmojiPicker
            onEmojiSelect={handleEmojiSelect}
            onClose={() => setShowEmojiPicker(false)}
          />
        )}

        {showFileUpload && (
          <FileUpload
            onFileSelect={handleFileSelect}
            onClose={() => setShowFileUpload(false)}
          />
        )}
      </form>
    </div>
  );
};

export default EnhancedMessageInput;
```

### 3. Styling

#### Real-time Chat Styles
```css
/* src/components/RealTimeChat.css */
.realtime-chat {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.chat-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.connection-status {
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4CAF50;
  animation: pulse 2s infinite;
}

.status-dot.connecting {
  background: #FF9800;
}

.status-dot.reconnecting {
  background: #F44336;
  animation: pulse 0.5s infinite;
}

.status-dot.disconnected {
  background: #9E9E9E;
  animation: none;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.error-banner {
  background: #F44336;
  color: white;
  padding: 10px 20px;
  text-align: center;
  font-size: 14px;
}

@media (max-width: 768px) {
  .connection-status {
    padding: 8px 15px;
    flex-direction: column;
    gap: 5px;
  }
}
```

#### Message Styles
```css
/* src/components/Chat/RealtimeMessage.css */
.realtime-message {
  margin-bottom: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.realtime-message.new {
  animation: messageAppear 0.3s ease-out;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

.realtime-message.own {
  background: rgba(116, 185, 255, 0.2);
  margin-left: 20%;
  border-color: rgba(116, 185, 255, 0.3);
}

.realtime-message.other {
  margin-right: 20%;
}

.realtime-message.system {
  background: rgba(255, 255, 255, 0.05);
  text-align: center;
  font-style: italic;
  margin: 8px 10%;
}

@keyframes messageAppear {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
}

.message-timestamp {
  font-size: 12px;
  opacity: 0.7;
}

.message-content {
  line-height: 1.4;
  word-wrap: break-word;
}

.message-text {
  font-size: 15px;
}

.message-edited {
  font-size: 12px;
  opacity: 0.6;
  font-style: italic;
  margin-left: 8px;
}

.message-edit-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  padding: 8px;
  color: white;
  font-size: 15px;
  resize: vertical;
  min-height: 60px;
}

.message-edit-input:focus {
  outline: none;
  border-color: rgba(116, 185, 255, 0.6);
  background: rgba(255, 255, 255, 0.15);
}

.message-file {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px dashed rgba(255, 255, 255, 0.3);
}

.file-icon {
  font-size: 24px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.file-size {
  font-size: 12px;
  opacity: 0.7;
}

.file-download {
  background: rgba(116, 185, 255, 0.3);
  color: white;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  transition: background-color 0.2s ease;
}

.file-download:hover {
  background: rgba(116, 185, 255, 0.5);
}

.message-image {
  text-align: center;
}

.chat-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.image-caption {
  margin-top: 8px;
  font-size: 14px;
  opacity: 0.8;
}

.delivery-status {
  position: absolute;
  bottom: 4px;
  right: 8px;
  font-size: 12px;
  opacity: 0.6;
}

.delivery-status.sending {
  color: #FF9800;
}

.delivery-status.sent {
  color: #4CAF50;
}

.delivery-status.delivered {
  color: #2196F3;
}

.delivery-status.failed {
  color: #F44336;
}

@media (max-width: 768px) {
  .realtime-message {
    margin-bottom: 12px;
    padding: 10px 12px;
  }

  .realtime-message.own {
    margin-left: 10%;
  }

  .realtime-message.other {
    margin-right: 10%;
  }

  .message-file {
    padding: 8px;
    gap: 8px;
  }

  .chat-image {
    max-height: 200px;
  }
}
```

#### Typing Indicator Styles
```css
/* src/components/Chat/TypingIndicator.css */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  margin: 8px 0;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  font-size: 14px;
  opacity: 0.8;
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 0.8;
    transform: translateY(0);
  }
}

.typing-avatars {
  display: flex;
  gap: 4px;
}

.typing-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.typing-text {
  font-style: italic;
}

.typing-dots {
  display: flex;
  gap: 2px;
  margin-left: 4px;
}

.typing-dots span {
  width: 4px;
  height: 4px;
  background: currentColor;
  border-radius: 50%;
  animation: typingDots 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: 0s;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingDots {
  0%, 60%, 100% {
    transform: scale(1);
    opacity: 0.4;
  }
  30% {
    transform: scale(1.3);
    opacity: 1;
  }
}
```

#### Enhanced Message Input Styles
```css
/* src/components/Chat/EnhancedMessageInput.css */
.enhanced-message-input {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
}

.message-form {
  position: relative;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.message-textarea {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: white;
  font-size: 15px;
  padding: 8px 12px;
  resize: none;
  min-height: 20px;
  max-height: 120px;
  overflow-y: auto;
  line-height: 1.4;
}

.message-textarea::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.message-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.attach-button,
.emoji-button,
.send-button {
  background: none;
  border: none;
  font-size: 18px;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.attach-button:hover,
.emoji-button:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.send-button {
  background: rgba(116, 185, 255, 0.3);
  border: 1px solid rgba(116, 185, 255, 0.5);
}

.send-button:hover:not(:disabled) {
  background: rgba(116, 185, 255, 0.5);
  transform: scale(1.05);
}

.send-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.emoji-picker,
.file-upload {
  position: absolute;
  bottom: 100%;
  right: 0;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  max-width: 300px;
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.emoji-button-picker {
  background: none;
  border: none;
  font-size: 20px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.emoji-button-picker:hover {
  background: rgba(116, 185, 255, 0.2);
}

@media (max-width: 768px) {
  .enhanced-message-input {
    padding: 12px;
  }

  .input-container {
    padding: 6px;
  }

  .message-textarea {
    font-size: 16px; /* Prevent zoom on iOS */
  }

  .emoji-picker,
  .file-upload {
    left: 0;
    right: 0;
    max-width: none;
  }
}
```

---

## 🧪 Testing the Implementation

### Test Checklist
- [ ] **WebSocket Connection**: Connection establishes and maintains properly
- [ ] **Real-time Messaging**: Messages appear instantly for all users
- [ ] **Typing Indicators**: Shows when users are typing and clears appropriately
- [ ] **Connection Recovery**: Handles disconnections and reconnections gracefully
- [ ] **Message Queue**: Queues messages when offline and sends when reconnected
- [ ] **File Sharing**: File upload and sharing works correctly
- [ ] **Message Reactions**: Emoji reactions work in real-time
- [ ] **Message Editing**: Edit and delete messages with real-time updates
- [ ] **Responsive Design**: Works well on mobile devices
- [ ] **Performance**: Handles multiple users and messages efficiently
- [ ] **Error Handling**: Network errors and connection issues are handled gracefully
- [ ] **Accessibility**: Screen reader support and keyboard navigation

### WebSocket Testing
```jsx
// Test WebSocket functionality
const testWebSocketFeatures = () => {
  // Test connection
  console.log('Connected:', webSocketService.isConnected());
  
  // Test message sending
  webSocketService.sendMessage('general', 'Test message');
  
  // Test typing
  webSocketService.setTyping('general', true);
  setTimeout(() => webSocketService.setTyping('general', false), 2000);
  
  // Test connection quality
  console.log('Connection quality:', webSocketService.getConnectionQuality());
};
```

---

## 🔧 Troubleshooting

### Common Issues

**1. WebSocket connection fails**
```jsx
// Add connection retry logic
const connectWithRetry = async (user, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await webSocketService.connect(user);
      return;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

**2. Messages not appearing in real-time**
```jsx
// Check event listeners are properly set up
useEffect(() => {
  const unsubscribe = webSocketService.on('message:received', (message) => {
    console.log('Message received:', message);
    // Update state
  });

  return unsubscribe;
}, []);
```

**3. Memory leaks from event listeners**
```jsx
// Always clean up event listeners
useEffect(() => {
  const unsubscribes = [];
  
  unsubscribes.push(webSocketService.on('message:received', handleMessage));
  unsubscribes.push(webSocketService.on('user:joined', handleUserJoined));
  
  return () => {
    unsubscribes.forEach(unsubscribe => unsubscribe());
  };
}, []);
```

**4. Performance issues with many messages**
```jsx
// Implement message pagination
const [messages, setMessages] = useState([]);
const [messageCount, setMessageCount] = useState(0);

// Only show last 50 messages
const visibleMessages = useMemo(() => {
  return messages.slice(-50);
}, [messages]);
```

**5. Connection drops frequently**
```jsx
// Implement heartbeat monitoring
useEffect(() => {
  const heartbeatInterval = setInterval(() => {
    if (webSocketService.isConnected()) {
      webSocketService.sendHeartbeat();
    }
  }, 30000);

  return () => clearInterval(heartbeatInterval);
}, []);
```

---

## 🎓 Learning Objectives

### WebSocket Integration Mastery
- ✅ **Real-time Communication**: Implementing bidirectional communication
- ✅ **Event Handling**: Managing WebSocket events and message types
- ✅ **Connection Management**: Handling connections, disconnections, and reconnections
- ✅ **Message Queue**: Queuing messages during offline periods

### Advanced Real-time Features
- ✅ **Typing Indicators**: Real-time typing status with auto-clear
- ✅ **Presence Indicators**: User online/offline status
- ✅ **Message Delivery**: Delivery status and read receipts
- ✅ **File Sharing**: Real-time file upload and sharing

### Performance and Reliability
- ✅ **Connection Quality**: Monitoring and displaying connection health
- ✅ **Error Recovery**: Graceful handling of network issues
- ✅ **Memory Management**: Proper cleanup of listeners and resources
- ✅ **Optimization**: Efficient handling of high-frequency events

### User Experience
- ✅ **Offline Support**: Graceful degradation when connection is lost
- ✅ **Real-time Feedback**: Immediate visual feedback for user actions
- ✅ **Progressive Enhancement**: Core functionality works without real-time features
- ✅ **Accessibility**: Support for screen readers and keyboard navigation

---

## 🚀 Next Steps

1. **Production WebSocket Server**: Replace mock server with Socket.IO or native WebSocket server
2. **Advanced Features**: Voice messages, video calls, screen sharing
3. **Message Encryption**: End-to-end encryption for secure messaging
4. **Message Threading**: Reply threads and message organization
5. **Advanced Notifications**: Push notifications and sound alerts
6. **Message Search**: Full-text search across message history
7. **Room Management**: Private rooms, invitations, and permissions
8. **Bot Integration**: Chatbots and automated responses

This implementation demonstrates advanced WebSocket patterns and provides a solid foundation for building real-time, collaborative applications.
