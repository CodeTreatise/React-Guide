# 🌐 Context API State Management Implementation Guide

> **Project**: Multi-User Chat Application with Context API  
> **Level**: Intermediate  
> **Estimated Time**: 5-7 hours  
> **Focus**: Context API, global state management, provider patterns

---

## 🚀 Quick Start (30 minutes)

### Step 1: Setup Project
```bash
npx create-react-app chat-context-app
cd chat-context-app
npm install uuid date-fns react-router-dom
npm start
```

### Step 2: Basic Context Structure
```jsx
{% raw %}
// src/contexts/AuthContext.js
import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AuthContext = createContext();

const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null
};

function authReducer(state, action) {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return { 
        ...state, 
        isLoading: false, 
        user: action.payload, 
        isAuthenticated: true 
      };
    case 'LOGIN_ERROR':
      return { 
        ...state, 
        isLoading: false, 
        error: action.payload 
      };
    case 'LOGOUT':
      return { ...initialState };
    default:
      return state;
  }
}

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const login = async (credentials) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      const user = { 
        id: Date.now(), 
        name: credentials.name, 
        email: credentials.email,
        avatar: `https://ui-avatars.com/api/?name=${credentials.name}&background=random`
      };
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
    } catch (error) {
      dispatch({ type: 'LOGIN_ERROR', payload: error.message });
    }
  };

  const logout = () => {
    dispatch({ type: 'LOGOUT' });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
{% endraw %}
```

### Step 3: Chat Context
```jsx
// src/contexts/ChatContext.js
import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

const ChatContext = createContext();

const initialState = {
  rooms: [
    { id: 'general', name: 'General', description: 'General discussion' },
    { id: 'random', name: 'Random', description: 'Random topics' }
  ],
  messages: {},
  activeRoom: 'general',
  onlineUsers: [],
  typing: {}
};

function chatReducer(state, action) {
  switch (action.type) {
    case 'SET_ACTIVE_ROOM':
      return { ...state, activeRoom: action.payload };
    
    case 'ADD_MESSAGE':
      const roomId = action.payload.roomId;
      return {
        ...state,
        messages: {
          ...state.messages,
          [roomId]: [...(state.messages[roomId] || []), action.payload.message]
        }
      };
    
    case 'SET_TYPING':
      return {
        ...state,
        typing: {
          ...state.typing,
          [action.payload.roomId]: {
            ...state.typing[action.payload.roomId],
            [action.payload.userId]: action.payload.isTyping
          }
        }
      };
    
    case 'SET_ONLINE_USERS':
      return { ...state, onlineUsers: action.payload };
    
    case 'USER_JOINED':
      return {
        ...state,
        onlineUsers: [...state.onlineUsers, action.payload]
      };
    
    case 'USER_LEFT':
      return {
        ...state,
        onlineUsers: state.onlineUsers.filter(user => user.id !== action.payload.id)
      };
    
    default:
      return state;
  }
}

export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const setActiveRoom = useCallback((roomId) => {
    dispatch({ type: 'SET_ACTIVE_ROOM', payload: roomId });
  }, []);

  const sendMessage = useCallback((content, user) => {
    const message = {
      id: uuidv4(),
      content,
      user,
      timestamp: new Date().toISOString(),
      roomId: state.activeRoom
    };
    dispatch({ 
      type: 'ADD_MESSAGE', 
      payload: { message, roomId: state.activeRoom }
    });
  }, [state.activeRoom]);

  const setTyping = useCallback((userId, isTyping) => {
    dispatch({
      type: 'SET_TYPING',
      payload: { userId, isTyping, roomId: state.activeRoom }
    });
  }, [state.activeRoom]);

  return (
    <ChatContext.Provider value={{
      ...state,
      setActiveRoom,
      sendMessage,
      setTyping
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
```

---

## 📚 Complete Implementation

### 1. Enhanced Context Providers

#### Theme Context
```jsx
{% raw %}
// src/contexts/ThemeContext.js
import React, { createContext, useContext, useReducer, useEffect } from 'react';

const ThemeContext = createContext();

const themes = {
  light: {
    name: 'light',
    colors: {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      danger: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8',
      background: '#ffffff',
      surface: '#f8f9fa',
      text: '#212529',
      textSecondary: '#6c757d',
      border: '#dee2e6'
    }
  },
  dark: {
    name: 'dark',
    colors: {
      primary: '#0d6efd',
      secondary: '#6c757d',
      success: '#198754',
      danger: '#dc3545',
      warning: '#ffc107',
      info: '#0dcaf0',
      background: '#212529',
      surface: '#343a40',
      text: '#ffffff',
      textSecondary: '#adb5bd',
      border: '#495057'
    }
  },
  purple: {
    name: 'purple',
    colors: {
      primary: '#6f42c1',
      secondary: '#6c757d',
      success: '#20c997',
      danger: '#e74c3c',
      warning: '#f39c12',
      info: '#3498db',
      background: '#2c1810',
      surface: '#3d2515',
      text: '#ffffff',
      textSecondary: '#cccccc',
      border: '#4a3728'
    }
  }
};

const initialState = {
  currentTheme: 'light',
  availableThemes: Object.keys(themes),
  theme: themes.light
};

function themeReducer(state, action) {
  switch (action.type) {
    case 'SET_THEME':
      return {
        ...state,
        currentTheme: action.payload,
        theme: themes[action.payload]
      };
    case 'LOAD_THEME':
      const savedTheme = localStorage.getItem('chatApp_theme') || 'light';
      return {
        ...state,
        currentTheme: savedTheme,
        theme: themes[savedTheme]
      };
    default:
      return state;
  }
}

export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, initialState);

  useEffect(() => {
    dispatch({ type: 'LOAD_THEME' });
  }, []);

  useEffect(() => {
    localStorage.setItem('chatApp_theme', state.currentTheme);
    // Apply CSS custom properties
    const root = document.documentElement;
    Object.entries(state.theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
  }, [state.currentTheme, state.theme]);

  const setTheme = (themeName) => {
    if (themes[themeName]) {
      dispatch({ type: 'SET_THEME', payload: themeName });
    }
  };

  return (
    <ThemeContext.Provider value={{ ...state, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
{% endraw %}
```

#### Notification Context
```jsx
// src/contexts/NotificationContext.js
import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

const NotificationContext = createContext();

const initialState = {
  notifications: []
};

function notificationReducer(state, action) {
  switch (action.type) {
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [...state.notifications, action.payload]
      };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    case 'CLEAR_ALL':
      return { ...state, notifications: [] };
    default:
      return state;
  }
}

export const NotificationProvider = ({ children }) => {
  const [state, dispatch] = useReducer(notificationReducer, initialState);

  const addNotification = useCallback((notification) => {
    const id = uuidv4();
    const newNotification = {
      id,
      type: 'info',
      autoClose: true,
      duration: 5000,
      ...notification,
      timestamp: Date.now()
    };

    dispatch({ type: 'ADD_NOTIFICATION', payload: newNotification });

    if (newNotification.autoClose) {
      setTimeout(() => {
        dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
      }, newNotification.duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
  }, []);

  const clearAll = useCallback(() => {
    dispatch({ type: 'CLEAR_ALL' });
  }, []);

  // Notification helpers
  const showSuccess = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'success', message });
  }, [addNotification]);

  const showError = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'error', message, duration: 8000 });
  }, [addNotification]);

  const showWarning = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'warning', message });
  }, [addNotification]);

  const showInfo = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'info', message });
  }, [addNotification]);

  return (
    <NotificationContext.Provider value={{
      ...state,
      addNotification,
      removeNotification,
      clearAll,
      showSuccess,
      showError,
      showWarning,
      showInfo
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};
```

### 2. Provider Composition
```jsx
// src/providers/AppProviders.js
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import { ChatProvider } from '../contexts/ChatContext';
import { ThemeProvider } from '../contexts/ThemeContext';
import { NotificationProvider } from '../contexts/NotificationContext';

const AppProviders = ({ children }) => {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <NotificationProvider>
          <AuthProvider>
            <ChatProvider>
              {children}
            </ChatProvider>
          </AuthProvider>
        </NotificationProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

export default AppProviders;
```

### 3. Enhanced Chat Context with Advanced Features
```jsx
{% raw %}
// src/contexts/ChatContext.js (Enhanced version)
import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useAuth } from './AuthContext';
import { useNotification } from './NotificationContext';

const ChatContext = createContext();

const initialState = {
  rooms: [
    { 
      id: 'general', 
      name: 'General', 
      description: 'General discussion',
      private: false,
      members: [],
      createdAt: new Date().toISOString()
    },
    { 
      id: 'random', 
      name: 'Random', 
      description: 'Random topics',
      private: false,
      members: [],
      createdAt: new Date().toISOString()
    }
  ],
  messages: {
    general: [
      {
        id: '1',
        content: 'Welcome to the General chat room!',
        user: { id: 'system', name: 'System', avatar: null },
        timestamp: new Date().toISOString(),
        roomId: 'general',
        type: 'system'
      }
    ],
    random: [
      {
        id: '2',
        content: 'This is the Random chat room for off-topic discussions.',
        user: { id: 'system', name: 'System', avatar: null },
        timestamp: new Date().toISOString(),
        roomId: 'random',
        type: 'system'
      }
    ]
  },
  activeRoom: 'general',
  onlineUsers: [],
  typing: {},
  unreadCounts: {},
  searchTerm: '',
  searchResults: []
};

function chatReducer(state, action) {
  switch (action.type) {
    case 'SET_ACTIVE_ROOM':
      const newActiveRoom = action.payload;
      return { 
        ...state, 
        activeRoom: newActiveRoom,
        unreadCounts: {
          ...state.unreadCounts,
          [newActiveRoom]: 0
        }
      };
    
    case 'ADD_MESSAGE':
      const { message, roomId } = action.payload;
      const isActiveRoom = state.activeRoom === roomId;
      
      return {
        ...state,
        messages: {
          ...state.messages,
          [roomId]: [...(state.messages[roomId] || []), message]
        },
        unreadCounts: {
          ...state.unreadCounts,
          [roomId]: isActiveRoom ? 0 : (state.unreadCounts[roomId] || 0) + 1
        }
      };
    
    case 'EDIT_MESSAGE':
      return {
        ...state,
        messages: {
          ...state.messages,
          [action.payload.roomId]: state.messages[action.payload.roomId].map(msg =>
            msg.id === action.payload.messageId
              ? { ...msg, content: action.payload.newContent, edited: true, editedAt: new Date().toISOString() }
              : msg
          )
        }
      };
    
    case 'DELETE_MESSAGE':
      return {
        ...state,
        messages: {
          ...state.messages,
          [action.payload.roomId]: state.messages[action.payload.roomId].filter(
            msg => msg.id !== action.payload.messageId
          )
        }
      };
    
    case 'ADD_REACTION':
      return {
        ...state,
        messages: {
          ...state.messages,
          [action.payload.roomId]: state.messages[action.payload.roomId].map(msg =>
            msg.id === action.payload.messageId
              ? {
                  ...msg,
                  reactions: {
                    ...msg.reactions,
                    [action.payload.emoji]: [
                      ...(msg.reactions?.[action.payload.emoji] || []),
                      action.payload.userId
                    ]
                  }
                }
              : msg
          )
        }
      };
    
    case 'REMOVE_REACTION':
      return {
        ...state,
        messages: {
          ...state.messages,
          [action.payload.roomId]: state.messages[action.payload.roomId].map(msg =>
            msg.id === action.payload.messageId
              ? {
                  ...msg,
                  reactions: {
                    ...msg.reactions,
                    [action.payload.emoji]: (msg.reactions?.[action.payload.emoji] || [])
                      .filter(userId => userId !== action.payload.userId)
                  }
                }
              : msg
          )
        }
      };
    
    case 'SET_TYPING':
      return {
        ...state,
        typing: {
          ...state.typing,
          [action.payload.roomId]: {
            ...state.typing[action.payload.roomId],
            [action.payload.userId]: action.payload.isTyping ? Date.now() : undefined
          }
        }
      };
    
    case 'CLEAR_OLD_TYPING':
      const now = Date.now();
      const fiveSecondsAgo = now - 5000;
      
      return {
        ...state,
        typing: Object.fromEntries(
          Object.entries(state.typing).map(([roomId, users]) => [
            roomId,
            Object.fromEntries(
              Object.entries(users).filter(([userId, timestamp]) => 
                timestamp && timestamp > fiveSecondsAgo
              )
            )
          ])
        )
      };
    
    case 'CREATE_ROOM':
      const newRoom = {
        id: uuidv4(),
        ...action.payload,
        createdAt: new Date().toISOString(),
        members: [action.payload.createdBy]
      };
      return {
        ...state,
        rooms: [...state.rooms, newRoom],
        messages: { ...state.messages, [newRoom.id]: [] }
      };
    
    case 'JOIN_ROOM':
      return {
        ...state,
        rooms: state.rooms.map(room =>
          room.id === action.payload.roomId
            ? { ...room, members: [...room.members, action.payload.userId] }
            : room
        )
      };
    
    case 'LEAVE_ROOM':
      return {
        ...state,
        rooms: state.rooms.map(room =>
          room.id === action.payload.roomId
            ? { ...room, members: room.members.filter(id => id !== action.payload.userId) }
            : room
        )
      };
    
    case 'SET_ONLINE_USERS':
      return { ...state, onlineUsers: action.payload };
    
    case 'USER_JOINED':
      return {
        ...state,
        onlineUsers: state.onlineUsers.find(u => u.id === action.payload.id)
          ? state.onlineUsers
          : [...state.onlineUsers, action.payload]
      };
    
    case 'USER_LEFT':
      return {
        ...state,
        onlineUsers: state.onlineUsers.filter(user => user.id !== action.payload.id)
      };
    
    case 'SEARCH_MESSAGES':
      const searchTerm = action.payload.toLowerCase();
      const searchResults = [];
      
      Object.entries(state.messages).forEach(([roomId, messages]) => {
        messages.forEach(message => {
          if (message.content.toLowerCase().includes(searchTerm)) {
            searchResults.push({ ...message, roomId });
          }
        });
      });
      
      return {
        ...state,
        searchTerm: action.payload,
        searchResults
      };
    
    case 'CLEAR_SEARCH':
      return {
        ...state,
        searchTerm: '',
        searchResults: []
      };
    
    default:
      return state;
  }
}

export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const { user } = useAuth();
  const { showSuccess, showInfo } = useNotification();

  // Auto-clear old typing indicators
  useEffect(() => {
    const interval = setInterval(() => {
      dispatch({ type: 'CLEAR_OLD_TYPING' });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Simulate user joining/leaving
  useEffect(() => {
    if (user) {
      dispatch({ type: 'USER_JOINED', payload: user });
      showInfo(`${user.name} joined the chat`);

      return () => {
        dispatch({ type: 'USER_LEFT', payload: user });
      };
    }
  }, [user, showInfo]);

  const setActiveRoom = useCallback((roomId) => {
    dispatch({ type: 'SET_ACTIVE_ROOM', payload: roomId });
  }, []);

  const sendMessage = useCallback((content, messageType = 'text') => {
    if (!user || !content.trim()) return;

    const message = {
      id: uuidv4(),
      content: content.trim(),
      user,
      timestamp: new Date().toISOString(),
      roomId: state.activeRoom,
      type: messageType,
      reactions: {}
    };

    dispatch({ 
      type: 'ADD_MESSAGE', 
      payload: { message, roomId: state.activeRoom }
    });

    // Clear typing indicator
    setTyping(user.id, false);
  }, [user, state.activeRoom]);

  const editMessage = useCallback((messageId, newContent, roomId) => {
    dispatch({
      type: 'EDIT_MESSAGE',
      payload: { messageId, newContent, roomId }
    });
  }, []);

  const deleteMessage = useCallback((messageId, roomId) => {
    dispatch({
      type: 'DELETE_MESSAGE',
      payload: { messageId, roomId }
    });
  }, []);

  const addReaction = useCallback((messageId, emoji, roomId) => {
    if (!user) return;
    
    dispatch({
      type: 'ADD_REACTION',
      payload: { messageId, emoji, userId: user.id, roomId }
    });
  }, [user]);

  const removeReaction = useCallback((messageId, emoji, roomId) => {
    if (!user) return;
    
    dispatch({
      type: 'REMOVE_REACTION',
      payload: { messageId, emoji, userId: user.id, roomId }
    });
  }, [user]);

  const setTyping = useCallback((userId, isTyping) => {
    dispatch({
      type: 'SET_TYPING',
      payload: { userId, isTyping, roomId: state.activeRoom }
    });
  }, [state.activeRoom]);

  const createRoom = useCallback((roomData) => {
    if (!user) return;

    dispatch({
      type: 'CREATE_ROOM',
      payload: { ...roomData, createdBy: user.id }
    });

    showSuccess(`Room "${roomData.name}" created successfully!`);
  }, [user, showSuccess]);

  const joinRoom = useCallback((roomId) => {
    if (!user) return;

    dispatch({
      type: 'JOIN_ROOM',
      payload: { roomId, userId: user.id }
    });
  }, [user]);

  const leaveRoom = useCallback((roomId) => {
    if (!user) return;

    dispatch({
      type: 'LEAVE_ROOM',
      payload: { roomId, userId: user.id }
    });
  }, [user]);

  const searchMessages = useCallback((term) => {
    dispatch({ type: 'SEARCH_MESSAGES', payload: term });
  }, []);

  const clearSearch = useCallback(() => {
    dispatch({ type: 'CLEAR_SEARCH' });
  }, []);

  // Get current room messages
  const currentRoomMessages = state.messages[state.activeRoom] || [];
  
  // Get current room info
  const currentRoom = state.rooms.find(room => room.id === state.activeRoom);
  
  // Get typing users for current room
  const typingUsers = Object.entries(state.typing[state.activeRoom] || {})
    .filter(([userId, timestamp]) => timestamp && userId !== user?.id)
    .map(([userId]) => state.onlineUsers.find(u => u.id === userId))
    .filter(Boolean);

  return (
    <ChatContext.Provider value={{
      ...state,
      currentRoomMessages,
      currentRoom,
      typingUsers,
      setActiveRoom,
      sendMessage,
      editMessage,
      deleteMessage,
      addReaction,
      removeReaction,
      setTyping,
      createRoom,
      joinRoom,
      leaveRoom,
      searchMessages,
      clearSearch
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
{% endraw %}
```

### 4. Main Application Components

#### Chat Application Component
```jsx
// src/components/ChatApp.jsx
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from './Auth/LoginForm';
import ChatInterface from './Chat/ChatInterface';
import NotificationContainer from './Notifications/NotificationContainer';
import './ChatApp.css';

const ChatApp = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="chat-app loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-app">
      {isAuthenticated ? <ChatInterface /> : <LoginForm />}
      <NotificationContainer />
    </div>
  );
};

export default ChatApp;
```

#### Login Form Component
```jsx
// src/components/Auth/LoginForm.jsx
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import './LoginForm.css';

const LoginForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: ''
  });
  const { login, isLoading, error } = useAuth();
  const { setTheme, availableThemes, currentTheme } = useTheme();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.name.trim() && formData.email.trim()) {
      await login(formData);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>💬 Chat App</h1>
          <p>Enter your details to join the conversation</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="name">Display Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter your name"
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading || !formData.name.trim() || !formData.email.trim()}
          >
            {isLoading ? 'Joining...' : 'Join Chat'}
          </button>
        </form>

        <div className="theme-selector">
          <label>Theme:</label>
          <select 
            value={currentTheme} 
            onChange={(e) => setTheme(e.target.value)}
            className="theme-select"
          >
            {availableThemes.map(theme => (
              <option key={theme} value={theme}>
                {theme.charAt(0).toUpperCase() + theme.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
```

#### Chat Interface Component
```jsx
{% raw %}
// src/components/Chat/ChatInterface.jsx
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../contexts/ChatContext';
import { useTheme } from '../../contexts/ThemeContext';
import Sidebar from './Sidebar';
import MessageArea from './MessageArea';
import MessageInput from './MessageInput';
import UserList from './UserList';
import SearchPanel from './SearchPanel';
import './ChatInterface.css';

const ChatInterface = () => {
  const { user, logout } = useAuth();
  const { currentRoom, onlineUsers } = useChat();
  const { setTheme, availableThemes, currentTheme } = useTheme();
  const [showSearch, setShowSearch] = useState(false);
  const [showUserList, setShowUserList] = useState(false);

  return (
    <div className="chat-interface">
      <header className="chat-header">
        <div className="header-left">
          <h2>💬 {currentRoom?.name || 'Chat Room'}</h2>
          <span className="room-description">{currentRoom?.description}</span>
        </div>
        
        <div className="header-center">
          <button 
            onClick={() => setShowSearch(!showSearch)}
            className={`icon-button ${showSearch ? 'active' : ''}`}
            title="Search messages"
          >
            🔍
          </button>
          <button 
            onClick={() => setShowUserList(!showUserList)}
            className={`icon-button ${showUserList ? 'active' : ''}`}
            title="Show users"
          >
            👥 {onlineUsers.length}
          </button>
        </div>

        <div className="header-right">
          <div className="user-info">
            <img 
              src={user.avatar} 
              alt={user.name}
              className="user-avatar"
            />
            <span className="user-name">{user.name}</span>
          </div>
          
          <select 
            value={currentTheme} 
            onChange={(e) => setTheme(e.target.value)}
            className="theme-select"
          >
            {availableThemes.map(theme => (
              <option key={theme} value={theme}>
                {theme.charAt(0).toUpperCase() + theme.slice(1)}
              </option>
            ))}
          </select>
          
          <button onClick={logout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <div className="chat-body">
        <Sidebar />
        
        <main className="chat-main">
          {showSearch && <SearchPanel />}
          <MessageArea />
          <MessageInput />
        </main>
        
        {showUserList && <UserList />}
      </div>
    </div>
  );
};

export default ChatInterface;
{% endraw %}
```

### 5. Styling

#### Main App Styles
```css
/* src/components/ChatApp.css */
.chat-app {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  transition: all 0.3s ease;
}

.chat-app.loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-left: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* CSS Custom Properties for theming */
:root {
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-danger: #dc3545;
  --color-warning: #ffc107;
  --color-info: #17a2b8;
  --color-background: #ffffff;
  --color-surface: #f8f9fa;
  --color-text: #212529;
  --color-text-secondary: #6c757d;
  --color-border: #dee2e6;
}
```

#### Login Form Styles
```css
/* src/components/Auth/LoginForm.css */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-info));
  padding: 20px;
}

.login-card {
  background: var(--color-background);
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: var(--color-text);
}

.login-header p {
  color: var(--color-text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: 600;
  color: var(--color-text);
}

.form-group input {
  padding: 12px;
  border: 2px solid var(--color-border);
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.2s ease;
  background: var(--color-background);
  color: var(--color-text);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: var(--color-danger);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
}

.login-button {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-button:hover:not(:disabled) {
  background: var(--color-primary);
  transform: translateY(-1px);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.theme-selector {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.theme-select {
  padding: 6px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
}
```

#### Chat Interface Styles
```css
/* src/components/Chat/ChatInterface.css */
.chat-interface {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 70px;
}

.header-left h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-text);
}

.room-description {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-left: 10px;
}

.header-center {
  display: flex;
  gap: 10px;
}

.icon-button {
  background: none;
  border: 1px solid var(--color-border);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-text);
}

.icon-button:hover {
  background: var(--color-border);
}

.icon-button.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 600;
  color: var(--color-text);
}

.logout-button {
  background: var(--color-danger);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.logout-button:hover {
  background: #c82333;
}

.chat-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
}

/* Responsive design */
@media (max-width: 768px) {
  .chat-header {
    padding: 10px 15px;
    flex-direction: column;
    gap: 10px;
    min-height: auto;
  }

  .header-left,
  .header-center,
  .header-right {
    width: 100%;
    justify-content: center;
  }

  .header-right {
    flex-direction: column;
    gap: 10px;
  }

  .room-description {
    margin-left: 0;
    margin-top: 5px;
    display: block;
  }
}
```

---

## 🧪 Testing the Implementation

### Test Checklist
- [ ] **Authentication**: Login/logout functionality works
- [ ] **Room Navigation**: Switch between different chat rooms
- [ ] **Message Sending**: Send messages in different rooms
- [ ] **Real-time Updates**: Messages appear immediately (simulated)
- [ ] **Typing Indicators**: Show when users are typing
- [ ] **User Presence**: Display online users correctly
- [ ] **Theme Switching**: All themes apply correctly
- [ ] **Notifications**: Success/error messages appear
- [ ] **Message Reactions**: Add/remove emoji reactions
- [ ] **Message Search**: Search functionality works
- [ ] **Room Creation**: Create new chat rooms
- [ ] **Responsive Design**: Works on mobile devices
- [ ] **Data Persistence**: Theme preference persists

### Context Performance Testing
```jsx
{% raw %}
// Test context re-render optimization
const ContextProfiler = ({ children, name }) => {
  return (
    <React.Profiler
      id={name}
      onRender={(id, phase, actualDuration) => {
        console.log(`${id} rendered in ${actualDuration}ms during ${phase} phase`);
      }}
    >
      {children}
    </React.Profiler>
  );
};

// Usage in providers
<ContextProfiler name="ChatProvider">
  <ChatProvider>
    {children}
  </ChatProvider>
</ContextProfiler>
{% endraw %}
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Context value changing on every render**
```jsx
// ❌ Wrong - creates new object every render
const value = {
  user,
  login,
  logout
};

// ✅ Correct - memoize the value
const value = useMemo(() => ({
  user,
  login,
  logout
}), [user, login, logout]);
```

**2. Provider composition causing performance issues**
```jsx
// ❌ Wrong - nested providers create deep tree
<AuthProvider>
  <ThemeProvider>
    <ChatProvider>
      <NotificationProvider>
        <App />
      </NotificationProvider>
    </ChatProvider>
  </ThemeProvider>
</AuthProvider>

// ✅ Better - use composition component
const AllProviders = ({ children }) => (
  <AuthProvider>
    <ThemeProvider>
      <ChatProvider>
        <NotificationProvider>
          {children}
        </NotificationProvider>
      </ChatProvider>
    </ThemeProvider>
  </AuthProvider>
);
```

**3. Contexts causing unnecessary re-renders**
```jsx
// Split contexts by concern and update frequency
const FastChangingContext = createContext(); // For frequently changing data
const SlowChangingContext = createContext(); // For rarely changing data

// Use React.memo for expensive components
export default React.memo(ExpensiveComponent);
```

**4. Reducer state becoming too complex**
```jsx
// Break down large reducers into smaller ones
const chatReducer = (state, action) => {
  return {
    ...state,
    messages: messagesReducer(state.messages, action),
    rooms: roomsReducer(state.rooms, action),
    users: usersReducer(state.users, action)
  };
};
```

---

## 🎓 Learning Objectives

### Context API Mastery
- ✅ **Context Creation**: Creating and structuring contexts effectively
- ✅ **Provider Patterns**: Implementing provider composition and optimization
- ✅ **Context Consumption**: Using contexts efficiently without performance issues
- ✅ **State Management**: Managing complex state with useReducer and Context

### Advanced State Patterns
- ✅ **State Normalization**: Organizing state for performance and maintainability
- ✅ **Action Design**: Creating clear and predictable action patterns
- ✅ **Side Effects**: Handling side effects in context providers
- ✅ **State Persistence**: Persisting and hydrating state from localStorage

### Performance Optimization
- ✅ **Render Optimization**: Preventing unnecessary re-renders with memoization
- ✅ **Context Splitting**: Organizing contexts by update frequency
- ✅ **Value Memoization**: Optimizing context values with useMemo
- ✅ **Component Memoization**: Using React.memo effectively

### Real-world Patterns
- ✅ **Provider Composition**: Structuring multiple providers cleanly
- ✅ **Custom Hooks**: Creating context-based custom hooks
- ✅ **Error Boundaries**: Handling context errors gracefully
- ✅ **TypeScript Integration**: Adding type safety to contexts

---

## 🚀 Next Steps

1. **Add WebSocket Integration**: Replace simulated real-time with actual WebSockets
2. **Implement Persistence**: Add backend integration for message persistence
3. **Add File Sharing**: Allow users to share images and files
4. **Voice/Video Chat**: Integrate WebRTC for voice/video calls
5. **Push Notifications**: Add browser push notifications
6. **Advanced Search**: Implement full-text search with highlighting
7. **Message Threading**: Add reply threads to messages
8. **Admin Features**: Room moderation and user management

This implementation demonstrates advanced Context API patterns and provides a solid foundation for building complex, real-time applications with global state management.
