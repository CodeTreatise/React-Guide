# 🚀 Intermediate React Projects

> **Level**: Intermediate (Weeks 5-8)  
> **Prerequisites**: Beginner projects completed, React fundamentals mastered  
> **Focus**: Advanced hooks, patterns, state management, and API integration

---

## 📋 Project Overview

These intermediate projects introduce more complex React concepts including custom hooks, advanced state management patterns, API integration, and real-world application architecture.

### Learning Progression
```
Project 1: Custom Hooks → useReducer, custom hook patterns
Project 2: Context API → Global state management
Project 3: API Integration → Data fetching, error handling
Project 4: Real-time Features → WebSocket integration
Project 5: Advanced Patterns → HOCs, Render Props, Compound Components
```

---

## 🎣 Project 1: Advanced Todo App with Custom Hooks

### Objective
Refactor a basic todo app using custom hooks and advanced state management patterns.

### Skills Practiced
- Custom hooks development
- useReducer for complex state
- Hook composition
- State management patterns

### Requirements
```jsx
// Custom hooks to implement
const useTodos = () => {
  // Todo CRUD operations
  // Local storage persistence
  // Filtering and sorting logic
};

const useLocalStorage = (key, initialValue) => {
  // Generic local storage hook
};

const useDebounce = (value, delay) => {
  // Debounced search functionality
};
```

### Features to Implement
- [x] Custom hook for todo management
- [x] Advanced filtering (by date, category, priority)
- [x] Bulk operations (select all, delete multiple)
- [x] Todo categories and tags
- [x] Search functionality with debouncing
- [x] Export/Import functionality
- [x] Keyboard shortcuts
- [x] Undo/Redo functionality

### Project Structure
```
advanced-todo-app/
├── src/
│   ├── components/
│   │   ├── TodoApp.jsx
│   │   ├── TodoList/
│   │   │   ├── TodoList.jsx
│   │   │   ├── TodoItem.jsx
│   │   │   └── BulkActions.jsx
│   │   ├── TodoForm/
│   │   │   ├── TodoForm.jsx
│   │   │   └── CategorySelector.jsx
│   │   └── TodoFilters/
│   │       ├── SearchBar.jsx
│   │       ├── FilterOptions.jsx
│   │       └── SortOptions.jsx
│   ├── hooks/
│   │   ├── useTodos.js
│   │   ├── useLocalStorage.js
│   │   ├── useDebounce.js
│   │   └── useKeyboardShortcuts.js
│   ├── reducers/
│   │   └── todoReducer.js
│   ├── utils/
│   │   ├── todoHelpers.js
│   │   └── exportHelpers.js
│   └── constants/
│       └── todoConstants.js
├── public/
└── package.json
```

### Custom Hook Implementation
```jsx
// src/hooks/useTodos.js
import { useReducer, useCallback } from 'react';
import { useLocalStorage } from './useLocalStorage';
import { todoReducer, initialState } from '../reducers/todoReducer';

export const useTodos = () => {
  // Load from localStorage
  const [savedTodos, setSavedTodos] = useLocalStorage('todos', []);
  
  const [state, dispatch] = useReducer(todoReducer, {
    ...initialState,
    todos: savedTodos
  });

  // Sync with localStorage
  useEffect(() => {
    setSavedTodos(state.todos);
  }, [state.todos, setSavedTodos]);

  const addTodo = useCallback((todoData) => {
    dispatch({
      type: 'ADD_TODO',
      payload: {
        id: Date.now().toString(),
        ...todoData,
        createdAt: new Date().toISOString(),
        completed: false
      }
    });
  }, []);

  const toggleTodo = useCallback((id) => {
    dispatch({ type: 'TOGGLE_TODO', payload: id });
  }, []);

  const deleteTodo = useCallback((id) => {
    dispatch({ type: 'DELETE_TODO', payload: id });
  }, []);

  const updateTodo = useCallback((id, updates) => {
    dispatch({ type: 'UPDATE_TODO', payload: { id, updates } });
  }, []);

  const bulkActions = {
    selectAll: useCallback(() => dispatch({ type: 'SELECT_ALL' }), []),
    deleteSelected: useCallback(() => dispatch({ type: 'DELETE_SELECTED' }), []),
    markSelectedComplete: useCallback(() => dispatch({ type: 'COMPLETE_SELECTED' }), [])
  };

  return {
    todos: state.todos,
    selectedTodos: state.selectedTodos,
    filter: state.filter,
    actions: {
      addTodo,
      toggleTodo,
      deleteTodo,
      updateTodo,
      ...bulkActions
    }
  };
};
```

### Assessment Criteria
- Custom hooks are well-designed and reusable ✅
- State management is efficient and predictable ✅
- Performance optimizations are implemented ✅
- Code is modular and maintainable ✅

---

## 🌐 Project 2: Global State Management with Context

### Objective
Build a multi-user chat application using React Context for global state management.

### Skills Practiced
- Context API patterns
- Provider composition
- Context optimization
- State normalization

### Requirements
```jsx
// Context structure
<AppProvider>
  <AuthProvider>
    <ChatProvider>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </ChatProvider>
  </AuthProvider>
</AppProvider>
```

### Features to Implement
- [x] User authentication state
- [x] Chat rooms and messages
- [x] Real-time message updates (simulated)
- [x] User presence indicators
- [x] Theme customization
- [x] Notification system
- [x] Message search and filtering
- [x] User preferences

### Project Structure
```
chat-app-context/
├── src/
│   ├── components/
│   │   ├── App.jsx
│   │   ├── Layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Footer.jsx
│   │   ├── Chat/
│   │   │   ├── ChatRoom.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   └── UserList.jsx
│   │   └── Auth/
│   │       ├── LoginForm.jsx
│   │       └── UserProfile.jsx
│   ├── contexts/
│   │   ├── AppContext.jsx
│   │   ├── AuthContext.jsx
│   │   ├── ChatContext.jsx
│   │   ├── ThemeContext.jsx
│   │   └── NotificationContext.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useChat.js
│   │   ├── useTheme.js
│   │   └── useNotifications.js
│   ├── services/
│   │   ├── authService.js
│   │   ├── chatService.js
│   │   └── mockApi.js
│   └── utils/
│       ├── contextHelpers.js
│       └── messageHelpers.js
├── public/
└── package.json
```

### Context Implementation
```jsx
// src/contexts/ChatContext.jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { chatReducer, initialChatState } from '../reducers/chatReducer';
import { chatService } from '../services/chatService';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate incoming messages
      const randomMessage = chatService.generateRandomMessage();
      if (randomMessage) {
        dispatch({ type: 'ADD_MESSAGE', payload: randomMessage });
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const sendMessage = async (roomId, content) => {
    const message = await chatService.sendMessage(roomId, content);
    dispatch({ type: 'ADD_MESSAGE', payload: message });
  };

  const joinRoom = async (roomId) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const roomData = await chatService.joinRoom(roomId);
      dispatch({ type: 'JOIN_ROOM', payload: roomData });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const value = {
    ...state,
    actions: {
      sendMessage,
      joinRoom,
      // ...other actions
    }
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};
```

### Assessment Criteria
- Context providers are properly structured ✅
- State is normalized and efficient ✅
- Performance is optimized (minimal re-renders) ✅
- Context composition is clean ✅

---

## 🌍 Project 3: Weather App with API Integration

### Objective
Build a comprehensive weather application with real API integration and advanced data fetching patterns.

### Skills Practiced
- API integration patterns
- Error handling strategies
- Loading states management
- Data caching
- Retry logic

### Requirements
```jsx
// API integration features
<WeatherApp>
  <LocationSearch onLocationSelect={handleLocationSelect} />
  <CurrentWeather location={selectedLocation} />
  <WeatherForecast location={selectedLocation} />
  <WeatherMap location={selectedLocation} />
  <WeatherAlerts location={selectedLocation} />
</WeatherApp>
```

### Features to Implement
- [x] Real weather API integration (OpenWeatherMap)
- [x] Geolocation support
- [x] Search with autocomplete
- [x] Current weather display
- [x] 7-day forecast
- [x] Weather alerts and warnings
- [x] Interactive weather map
- [x] Offline support with caching
- [x] Background sync

### Project Structure
```
weather-app-api/
├── src/
│   ├── components/
│   │   ├── WeatherApp.jsx
│   │   ├── LocationSearch/
│   │   │   ├── LocationSearch.jsx
│   │   │   └── LocationSuggestions.jsx
│   │   ├── Weather/
│   │   │   ├── CurrentWeather.jsx
│   │   │   ├── WeatherForecast.jsx
│   │   │   ├── WeatherMap.jsx
│   │   │   └── WeatherAlerts.jsx
│   │   └── UI/
│   │       ├── LoadingSpinner.jsx
│   │       ├── ErrorBoundary.jsx
│   │       └── OfflineNotice.jsx
│   ├── hooks/
│   │   ├── useWeatherAPI.js
│   │   ├── useGeolocation.js
│   │   ├── useLocalStorage.js
│   │   └── useNetworkStatus.js
│   ├── services/
│   │   ├── weatherAPI.js
│   │   ├── geocodingAPI.js
│   │   └── cacheService.js
│   ├── utils/
│   │   ├── weatherHelpers.js
│   │   ├── locationHelpers.js
│   │   └── dateHelpers.js
│   └── constants/
│       └── weatherConstants.js
├── public/
└── package.json
```

### API Integration Hook
```jsx
{% raw %}
// src/hooks/useWeatherAPI.js
import { useState, useEffect, useCallback } from 'react';
import { weatherAPI } from '../services/weatherAPI';
import { cacheService } from '../services/cacheService';

export const useWeatherAPI = () => {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWeather = useCallback(async (location, options = {}) => {
    const { useCache = true, retryCount = 3 } = options;
    
    setLoading(true);
    setError(null);

    try {
      // Check cache first
      if (useCache) {
        const cachedData = cacheService.get(`weather_${location}`);
        if (cachedData && !cacheService.isExpired(cachedData)) {
          setWeather(cachedData.data);
          setLoading(false);
          return;
        }
      }

      // Fetch from API with retry logic
      const data = await weatherAPI.getCurrentWeather(location, { retryCount });
      
      // Cache the result
      cacheService.set(`weather_${location}`, data, 10 * 60 * 1000); // 10 minutes
      
      setWeather(data);
    } catch (err) {
      setError(err.message);
      
      // Try to use stale cache data as fallback
      const staleData = cacheService.get(`weather_${location}`);
      if (staleData) {
        setWeather(staleData.data);
        setError(`Using cached data: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchForecast = useCallback(async (location) => {
    try {
      const data = await weatherAPI.getForecast(location);
      setForecast(data);
    } catch (err) {
      console.error('Forecast fetch failed:', err);
    }
  }, []);

  return {
    weather,
    forecast,
    loading,
    error,
    fetchWeather,
    fetchForecast,
    refetch: () => fetchWeather(weather?.location, { useCache: false })
  };
};
{% endraw %}
```

### Assessment Criteria
- API integration is robust and handles errors ✅
- Loading and error states are managed properly ✅
- Caching and offline support work correctly ✅
- User experience is smooth and responsive ✅

---

## 💬 Project 4: Real-time Chat Application

### Objective
Build a real-time chat application using WebSocket simulation and advanced React patterns.

### Skills Practiced
- Real-time data handling
- WebSocket patterns (simulated)
- Message state management
- Optimistic updates
- Connection handling

### Requirements
```jsx
// Real-time features
<ChatApplication>
  <ChatRoomList rooms={availableRooms} />
  <ActiveChat 
    room={selectedRoom}
    messages={messages}
    onSendMessage={handleSendMessage}
  />
  <UserPresence users={onlineUsers} />
  <TypingIndicator typingUsers={typingUsers} />
</ChatApplication>
```

### Features to Implement
- [x] Real-time messaging (simulated WebSocket)
- [x] Multiple chat rooms
- [x] User presence indicators
- [x] Typing indicators
- [x] Message status (sent, delivered, read)
- [x] File sharing simulation
- [x] Message search and history
- [x] Push notifications
- [x] Emoji reactions

### Project Structure
```
realtime-chat-app/
├── src/
│   ├── components/
│   │   ├── ChatApplication.jsx
│   │   ├── ChatRoom/
│   │   │   ├── ChatRoomList.jsx
│   │   │   ├── ActiveChat.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   └── MessageItem.jsx
│   │   ├── UserInterface/
│   │   │   ├── UserPresence.jsx
│   │   │   ├── TypingIndicator.jsx
│   │   │   └── UserProfile.jsx
│   │   └── Notifications/
│   │       ├── NotificationCenter.jsx
│   │       └── PushNotification.jsx
│   ├── hooks/
│   │   ├── useWebSocket.js (simulated)
│   │   ├── useChat.js
│   │   ├── usePresence.js
│   │   └── useNotifications.js
│   ├── services/
│   │   ├── chatService.js
│   │   ├── websocketService.js (simulated)
│   │   └── notificationService.js
│   ├── utils/
│   │   ├── messageHelpers.js
│   │   └── timeHelpers.js
│   └── constants/
│       └── chatConstants.js
├── public/
└── package.json
```

### WebSocket Simulation Hook
```jsx
{% raw %}
// src/hooks/useWebSocket.js
import { useState, useEffect, useCallback, useRef } from 'react';

export const useWebSocket = (url) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const listenersRef = useRef(new Set());

  // Simulate WebSocket connection
  useEffect(() => {
    const connectTimer = setTimeout(() => {
      setIsConnected(true);
      setError(null);
    }, 1000);

    // Simulate incoming messages
    const messageInterval = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance of receiving a message
        const simulatedMessage = {
          id: Date.now(),
          type: 'message',
          data: {
            user: `User${Math.floor(Math.random() * 5) + 1}`,
            text: `Random message ${Date.now()}`,
            timestamp: new Date().toISOString()
          }
        };
        
        setLastMessage(simulatedMessage);
        
        // Notify all listeners
        listenersRef.current.forEach(listener => {
          listener(simulatedMessage);
        });
      }
    }, 3000);

    return () => {
      clearTimeout(connectTimer);
      clearInterval(messageInterval);
      setIsConnected(false);
    };
  }, [url]);

  const sendMessage = useCallback((message) => {
    if (!isConnected) {
      setError('Not connected to server');
      return;
    }

    // Simulate sending message with optimistic update
    const messageWithId = {
      ...message,
      id: Date.now(),
      timestamp: new Date().toISOString(),
      status: 'sending'
    };

    // Simulate network delay
    setTimeout(() => {
      messageWithId.status = 'sent';
      setLastMessage(messageWithId);
      
      listenersRef.current.forEach(listener => {
        listener(messageWithId);
      });
    }, 500);

    return messageWithId;
  }, [isConnected]);

  const addMessageListener = useCallback((listener) => {
    listenersRef.current.add(listener);
    
    return () => {
      listenersRef.current.delete(listener);
    };
  }, []);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    addMessageListener
  };
};
{% endraw %}
```

### Assessment Criteria
- Real-time features work smoothly ✅
- Message state management is efficient ✅
- Connection handling is robust ✅
- User experience feels responsive ✅

---

## 🎨 Project 5: Component Library with Advanced Patterns

### Objective
Create a reusable component library showcasing advanced React patterns and design principles.

### Skills Practiced
- Higher-Order Components (HOCs)
- Render Props pattern
- Compound Components
- Controlled/Uncontrolled patterns
- Component composition

### Requirements
```jsx
// Component library structure
<ComponentShowcase>
  <Modal>
    <Modal.Header>
      <Modal.Title>Advanced Modal</Modal.Title>
      <Modal.CloseButton />
    </Modal.Header>
    <Modal.Body>
      <DataTable 
        data={tableData}
        renderRow={(item) => <CustomRow item={item} />}
        withPagination
        withSorting
      />
    </Modal.Body>
  </Modal>
</ComponentShowcase>
```

### Components to Build
- [x] Modal (Compound Component pattern)
- [x] DataTable (Render Props pattern)
- [x] Form (Controlled/Uncontrolled pattern)
- [x] Dropdown (HOC pattern)
- [x] Tabs (Compound Component pattern)
- [x] Accordion (State management pattern)
- [x] Carousel (Advanced hooks pattern)
- [x] InfiniteScroll (Performance pattern)

### Project Structure
```
component-library/
├── src/
│   ├── components/
│   │   ├── Modal/
│   │   │   ├── Modal.jsx
│   │   │   ├── ModalHeader.jsx
│   │   │   ├── ModalBody.jsx
│   │   │   └── ModalFooter.jsx
│   │   ├── DataTable/
│   │   │   ├── DataTable.jsx
│   │   │   ├── TableHeader.jsx
│   │   │   ├── TableBody.jsx
│   │   │   └── Pagination.jsx
│   │   ├── Form/
│   │   │   ├── Form.jsx
│   │   │   ├── FormField.jsx
│   │   │   └── FormValidation.jsx
│   │   └── common/
│   │       ├── Button.jsx
│   │       ├── Input.jsx
│   │       └── Loading.jsx
│   ├── hocs/
│   │   ├── withModal.jsx
│   │   ├── withLoading.jsx
│   │   └── withValidation.jsx
│   ├── hooks/
│   │   ├── useModal.js
│   │   ├── useTable.js
│   │   └── useForm.js
│   ├── patterns/
│   │   ├── renderProps.jsx
│   │   └── compoundComponents.jsx
│   └── utils/
│       ├── componentHelpers.js
│       └── patternHelpers.js
├── stories/ (Storybook)
└── package.json
```

### Compound Component Pattern Example
```jsx
// src/components/Modal/Modal.jsx
import React, { createContext, useContext, useState } from 'react';

const ModalContext = createContext();

const Modal = ({ children, isOpen: controlledIsOpen, onClose, ...props }) => {
  const [internalIsOpen, setInternalIsOpen] = useState(false);
  
  // Support both controlled and uncontrolled usage
  const isOpen = controlledIsOpen !== undefined ? controlledIsOpen : internalIsOpen;
  const setIsOpen = onClose || setInternalIsOpen;

  const contextValue = {
    isOpen,
    onClose: () => setIsOpen(false),
    onOpen: () => setIsOpen(true)
  };

  if (!isOpen) return null;

  return (
    <ModalContext.Provider value={contextValue}>
      <div className="modal-overlay" onClick={contextValue.onClose}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          {children}
        </div>
      </div>
    </ModalContext.Provider>
  );
};

// Compound components
Modal.Header = ({ children }) => {
  const { onClose } = useContext(ModalContext);
  return (
    <div className="modal-header">
      {children}
    </div>
  );
};

Modal.Title = ({ children }) => (
  <h2 className="modal-title">{children}</h2>
);

Modal.CloseButton = () => {
  const { onClose } = useContext(ModalContext);
  return (
    <button className="modal-close" onClick={onClose}>
      ×
    </button>
  );
};

Modal.Body = ({ children }) => (
  <div className="modal-body">{children}</div>
);

Modal.Footer = ({ children }) => (
  <div className="modal-footer">{children}</div>
);

export default Modal;
```

### Assessment Criteria
- Advanced patterns are implemented correctly ✅
- Components are reusable and flexible ✅
- API design is intuitive and consistent ✅
- Documentation and examples are comprehensive ✅

---

## 🏆 Capstone Project: Task Management Dashboard

### Objective
Combine all intermediate concepts into a comprehensive task management application.

### Skills Practiced
- All intermediate React concepts
- Advanced state management
- API integration
- Real-time features
- Component patterns

### Features to Implement
- [x] User authentication and authorization
- [x] Project and task management
- [x] Real-time collaboration
- [x] File attachments and comments
- [x] Advanced filtering and search
- [x] Data visualization (charts, reports)
- [x] Notification system
- [x] Offline support
- [x] Mobile-responsive design

### Assessment Criteria
- Complex state management is handled well ✅
- Real-time features work seamlessly ✅
- Component architecture is scalable ✅
- Performance is optimized ✅
- User experience is professional ✅

---

## 📚 Resources for Intermediate Projects

### State Management
- [React Context Patterns](https://kentcdodds.com/blog/how-to-use-react-context-effectively)
- [Custom Hooks Guide](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [useReducer vs useState](https://react.dev/reference/react/useReducer)

### API Integration
- [Data Fetching Patterns](https://react.dev/reference/react/useEffect#fetching-data-with-effects)
- [Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [Axios Documentation](https://axios-http.com/docs/intro)

### Advanced Patterns
- [Higher-Order Components](https://react.dev/reference/react/Component#avoiding-legacy-lifecycles)
- [Render Props](https://react.dev/reference/react/cloneElement#passing-data-with-a-render-prop)
- [Compound Components](https://kentcdodds.com/blog/compound-components-with-react-hooks)

---

## 🚀 Next Steps

After completing these intermediate projects, you'll be ready for:
- **Advanced Projects**: Performance optimization, testing, and architecture
- **Expert Projects**: Full-stack applications and complex systems
- **Real-world Applications**: Production-ready applications with advanced features

**Continue to**: [Advanced Projects](../Advanced/README.md)