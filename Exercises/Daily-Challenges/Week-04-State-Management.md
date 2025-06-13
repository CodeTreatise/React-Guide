# Week 04: State Management & Advanced Patterns - Daily Challenges

## Overview
This week focuses on advanced state management patterns, Context API mastery, Redux fundamentals, and building scalable application architectures. Each challenge builds toward creating production-ready state management solutions.

---

## Day 22: Context API Deep Dive

### 🎯 Challenge: Multi-Context Application Architecture
Build an application that uses multiple contexts efficiently to avoid prop drilling and unnecessary re-renders.

#### Requirements:
1. **User Context**: Authentication, profile, preferences
2. **Theme Context**: UI theming with custom themes
3. **Notification Context**: Toast notifications and alerts
4. **App State Context**: Global application state
5. **Optimization**: Prevent unnecessary re-renders

#### Architecture Pattern:
```jsx
// contexts/UserContext.js
const UserContext = createContext();
const UserProvider = ({ children }) => {
  // User state management
};

// contexts/ThemeContext.js  
const ThemeContext = createContext();
const ThemeProvider = ({ children }) => {
  // Theme state management
};

// App.js
function App() {
  return (
    <UserProvider>
      <ThemeProvider>
        <NotificationProvider>
          <AppStateProvider>
            <Router>
              {/* Your app routes */}
            </Router>
          </AppStateProvider>
        </NotificationProvider>
      </ThemeProvider>
    </UserProvider>
  );
}
```

#### Expected Features:
- Multiple contexts working together without conflicts
- Context selectors to prevent unnecessary re-renders
- Custom hooks for each context (`useUser`, `useTheme`, etc.)
- Context debugging tools and dev mode logging
- Performance monitoring for context updates

#### Bonus Points:
- Implement context persistence (localStorage/sessionStorage)
- Add context middleware for logging/debugging
- Create context composition helpers
- Build context-aware testing utilities

---

## Day 23: Redux Fundamentals & Toolkit

### 🎯 Challenge: E-commerce Store with Redux Toolkit
Build a complete e-commerce store management system using Redux Toolkit with modern patterns.

#### Requirements:
1. **Product Management**: CRUD operations for products
2. **Shopping Cart**: Add, remove, update quantities
3. **User Management**: Authentication, profile, order history
4. **Order Processing**: Checkout flow with status tracking
5. **Search & Filtering**: Product search with complex filters

#### Redux Store Structure:
```jsx
// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import productSlice from './slices/productSlice';
import cartSlice from './slices/cartSlice';
import orderSlice from './slices/orderSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    products: productSlice,
    cart: cartSlice,
    orders: orderSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [/* non-serializable actions */],
      },
    }),
});

// slices/productSlice.js
const productSlice = createSlice({
  name: 'products',
  initialState: {
    items: [],
    loading: false,
    error: null,
    filters: {},
    searchTerm: '',
  },
  reducers: {
    // Synchronous reducers
  },
  extraReducers: (builder) => {
    // Async thunk reducers
  },
});
```

#### Expected Features:
- Complete CRUD operations with async thunks
- Optimistic updates for better UX
- Normalized state structure for complex data
- RTK Query integration for API calls
- Redux DevTools integration with time-travel debugging

#### Bonus Points:
- Add RTK Query code generation
- Implement state persistence middleware
- Create custom Redux middleware
- Add state migration for version updates

---

## Day 24: State Normalization & Complex Data

### 🎯 Challenge: Social Media Feed with Complex Relationships
Build a social media application that handles complex, normalized data structures efficiently.

#### Requirements:
1. **Normalized Data**: Users, posts, comments, likes, follows
2. **Real-time Updates**: Live updates using WebSocket
3. **Infinite Scrolling**: Efficient pagination and caching
4. **Relationship Management**: Follow/unfollow, like/unlike
5. **Content Management**: Create, edit, delete posts and comments

#### Data Normalization Pattern:
```jsx
// Data structure
const initialState = {
  entities: {
    users: {
      byId: {},
      allIds: []
    },
    posts: {
      byId: {},
      allIds: []
    },
    comments: {
      byId: {},
      allIds: []
    }
  },
  ui: {
    feed: {
      postIds: [],
      loading: false,
      hasMore: true
    },
    userProfile: {
      userId: null,
      postIds: [],
      loading: false
    }
  }
};

// Selectors
const selectUser = (state, userId) => state.entities.users.byId[userId];
const selectPost = createSelector(
  [state => state.entities.posts.byId, (state, postId) => postId],
  (posts, postId) => posts[postId]
);
const selectPostWithAuthor = createSelector(
  [selectPost, selectUser],
  (post, author) => ({ ...post, author })
);
```

#### Expected Features:
- Efficient data normalization and denormalization
- Complex relationship management
- Real-time updates without full re-renders
- Optimistic updates for user interactions
- Caching strategies for offline support

#### Bonus Points:
- Add content moderation features
- Implement advanced search with faceting
- Create data export/import functionality
- Add analytics and usage tracking

---

## Day 25: State Machines & Advanced Patterns

### 🎯 Challenge: Multi-Step Form Wizard with State Machine
Create a complex multi-step form using state machine principles for robust state management.

#### Requirements:
1. **Multi-Step Flow**: Personal info → Payment → Confirmation
2. **Validation**: Step-by-step validation with dependencies
3. **Navigation**: Forward/backward with state persistence
4. **Error Handling**: Robust error recovery and retry logic
5. **Progress Tracking**: Visual progress and completion status

#### State Machine Implementation:
```jsx
// Using XState or custom state machine
const formMachine = {
  initial: 'personalInfo',
  context: {
    formData: {},
    errors: {},
    completedSteps: []
  },
  states: {
    personalInfo: {
      on: {
        NEXT: {
          target: 'paymentInfo',
          guard: 'isPersonalInfoValid',
          actions: 'savePersonalInfo'
        }
      }
    },
    paymentInfo: {
      on: {
        NEXT: {
          target: 'confirmation',
          guard: 'isPaymentInfoValid',
          actions: 'savePaymentInfo'
        },
        BACK: 'personalInfo'
      }
    },
    confirmation: {
      on: {
        SUBMIT: {
          target: 'submitting',
          actions: 'submitForm'
        },
        BACK: 'paymentInfo'
      }
    },
    submitting: {
      on: {
        SUCCESS: 'success',
        ERROR: 'error'
      }
    },
    success: {
      type: 'final'
    },
    error: {
      on: {
        RETRY: 'submitting',
        BACK: 'confirmation'
      }
    }
  }
};

function FormWizard() {
  const [state, send] = useStateMachine(formMachine);
  
  return (
    <div className="form-wizard">
      <ProgressIndicator currentStep={state.value} />
      {renderCurrentStep(state.value, state.context, send)}
    </div>
  );
}
```

#### Expected Features:
- Robust state transitions with guards and actions
- Form validation with cross-step dependencies
- Data persistence across steps
- Error handling with recovery options
- Progress visualization and step navigation

#### Bonus Points:
- Add dynamic step generation based on user input
- Implement form autosave and recovery
- Create wizard testing utilities
- Add accessibility features for screen readers

---

## Day 26: Performance Optimization in State Management

### 🎯 Challenge: High-Performance Dashboard with Real-time Data
Build a real-time analytics dashboard that handles high-frequency updates efficiently.

#### Requirements:
1. **Real-time Data**: WebSocket updates every second
2. **Multiple Widgets**: 10+ different data visualizations
3. **User Customization**: Drag-and-drop dashboard layout
4. **Data Processing**: Complex calculations and aggregations
5. **Performance**: Handle 1000+ data points without lag

#### Optimization Strategies:
```jsx
// Selector optimization
const selectDashboardData = createSelector(
  [state => state.analytics.rawData, state => state.dashboard.config],
  (rawData, config) => {
    // Expensive computation only when dependencies change
    return processAnalyticsData(rawData, config);
  }
);

// Component optimization
const Widget = React.memo(function Widget({ type, data, config }) {
  const processedData = useMemo(() => {
    return processWidgetData(data, config);
  }, [data, config]);
  
  return <WidgetRenderer type={type} data={processedData} />;
});

// State update optimization
const analyticsSlice = createSlice({
  name: 'analytics',
  initialState: {
    data: {},
    lastUpdate: null
  },
  reducers: {
    updateData: (state, action) => {
      // Use Immer for efficient immutable updates
      const { timestamp, updates } = action.payload;
      
      // Only update changed data points
      Object.keys(updates).forEach(key => {
        if (state.data[key] !== updates[key]) {
          state.data[key] = updates[key];
        }
      });
      
      state.lastUpdate = timestamp;
    }
  }
});
```

#### Expected Features:
- Optimized selectors with memoization
- Efficient WebSocket data handling
- Batch updates for better performance
- Virtual scrolling for large datasets
- Memory leak prevention

#### Bonus Points:
- Add data streaming with backpressure handling
- Implement data compression for WebSocket
- Create performance monitoring dashboard
- Add automated performance testing

---

## Day 27: State Persistence & Offline Support

### 🎯 Challenge: Offline-First Task Management App
Create a task management application that works seamlessly offline with sync capabilities.

#### Requirements:
1. **Offline Storage**: IndexedDB for complex data
2. **Sync Logic**: Conflict resolution when coming online
3. **Optimistic Updates**: Immediate UI feedback
4. **Background Sync**: Sync when connection restored
5. **Data Migration**: Handle schema changes

#### Offline-First Architecture:
```jsx
// Sync middleware
const createSyncMiddleware = () => store => next => action => {
  const result = next(action);
  
  // Queue actions for sync when offline
  if (!navigator.onLine && action.meta?.sync) {
    queueActionForSync(action);
  }
  
  // Attempt sync when online
  if (navigator.onLine && hasQueuedActions()) {
    syncQueuedActions();
  }
  
  return result;
};

// Offline slice
const offlineSlice = createSlice({
  name: 'offline',
  initialState: {
    isOnline: navigator.onLine,
    syncQueue: [],
    lastSync: null,
    conflicts: []
  },
  reducers: {
    setOnlineStatus: (state, action) => {
      state.isOnline = action.payload;
    },
    addToSyncQueue: (state, action) => {
      state.syncQueue.push({
        ...action.payload,
        timestamp: Date.now(),
        id: generateId()
      });
    },
    processSyncQueue: (state) => {
      state.syncQueue = [];
      state.lastSync = Date.now();
    },
    addConflict: (state, action) => {
      state.conflicts.push(action.payload);
    }
  }
});

// Custom hook for offline handling
function useOfflineSync() {
  const dispatch = useDispatch();
  const { isOnline, syncQueue, conflicts } = useSelector(state => state.offline);
  
  useEffect(() => {
    const handleOnline = () => {
      dispatch(setOnlineStatus(true));
      if (syncQueue.length > 0) {
        dispatch(processSyncQueue());
      }
    };
    
    const handleOffline = () => {
      dispatch(setOnlineStatus(false));
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [dispatch, syncQueue.length]);
  
  return { isOnline, syncQueue, conflicts };
}
```

#### Expected Features:
- Complete offline functionality
- Intelligent conflict resolution
- Background synchronization
- Data versioning and migration
- Connection status indicators

#### Bonus Points:
- Add P2P sync capabilities
- Implement differential sync
- Create data export/backup features
- Add sync analytics and monitoring

---

## Day 28: Integration Project - Project Management Platform

### 🎯 Challenge: Complete Project Management Platform
Build a full-featured project management platform combining all state management concepts.

#### Requirements:
1. **Multi-Team Support**: Teams, projects, tasks, users
2. **Real-time Collaboration**: Live updates, comments, notifications
3. **Complex Permissions**: Role-based access control
4. **Analytics Dashboard**: Project metrics and reporting
5. **Offline Support**: Work offline with sync

#### Application Architecture:
```jsx
// Store configuration
const store = configureStore({
  reducer: {
    // Feature slices
    auth: authSlice,
    teams: teamsSlice,
    projects: projectsSlice,
    tasks: tasksSlice,
    users: usersSlice,
    comments: commentsSlice,
    notifications: notificationsSlice,
    
    // UI slices
    dashboard: dashboardSlice,
    filters: filtersSlice,
    
    // System slices
    offline: offlineSlice,
    sync: syncSlice
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(syncMiddleware)
      .concat(analyticsMiddleware)
      .concat(persistenceMiddleware),
});

// Main application component
function ProjectManagementApp() {
  const { user, isAuthenticated } = useAuth();
  const { isOnline } = useOfflineSync();
  const { notifications } = useNotifications();
  
  if (!isAuthenticated) {
    return <AuthenticationFlow />;
  }
  
  return (
    <AppProvider>
      <div className="app">
        <Sidebar />
        <MainContent>
          <Router>
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/projects" element={<ProjectsView />} />
              <Route path="/tasks" element={<TasksView />} />
              <Route path="/team" element={<TeamView />} />
              <Route path="/analytics" element={<AnalyticsView />} />
            </Routes>
          </Router>
        </MainContent>
        <NotificationCenter notifications={notifications} />
        <OfflineIndicator isOnline={isOnline} />
      </div>
    </AppProvider>
  );
}
```

#### Expected Features:
- Complete project lifecycle management
- Real-time collaborative editing
- Advanced filtering and search
- Comprehensive analytics and reporting
- Mobile-responsive design
- Offline-first architecture

#### Technical Requirements:
- Use all state management patterns learned
- Implement proper error boundaries
- Add comprehensive testing
- Optimize for performance
- Include accessibility features

#### Bonus Points:
- Add time tracking functionality
- Implement Gantt chart visualization
- Create mobile app using React Native
- Add AI-powered project insights
- Build API integration for third-party tools

---

## 📋 Week 4 Assessment Checklist

### State Management Mastery:
- [ ] Effectively used Context API without performance issues
- [ ] Built complex Redux applications with RTK
- [ ] Implemented state normalization for complex data
- [ ] Created state machines for robust flow control
- [ ] Optimized state updates for performance
- [ ] Built offline-first applications with sync

### Architecture Skills:
- [ ] Designed scalable state management architecture
- [ ] Implemented proper separation of concerns
- [ ] Created reusable state management patterns
- [ ] Built middleware for cross-cutting concerns
- [ ] Designed error handling strategies

### Advanced Patterns:
- [ ] Used selectors for derived state
- [ ] Implemented optimistic updates
- [ ] Created conflict resolution strategies
- [ ] Built real-time collaborative features
- [ ] Designed data migration strategies

---

## 🚀 Bonus Challenges

### Expert Level Extensions:
1. **State Management Library**: Create your own state management library
2. **Advanced Testing**: Comprehensive testing strategies for state
3. **Performance Profiling**: Advanced performance optimization
4. **Micro-frontends**: State management across micro-frontends
5. **GraphQL Integration**: Complex state with GraphQL and Apollo

### Real-World Applications:
- **Trading Platform**: Real-time financial data management
- **Collaborative Editor**: Google Docs-like collaborative editing
- **Gaming Platform**: Complex game state management
- **IoT Dashboard**: Real-time device monitoring and control
- **Healthcare Platform**: HIPAA-compliant data management

Each challenge should take 4-6 hours to complete properly. Focus on understanding the architectural decisions and trade-offs. Document your patterns and create reusable solutions that can be applied to future projects.
