# Module 4: State Management

## 📚 Learning Objectives

By the end of this module, you will:
- Master React Context API for global state management
- Understand when and how to use different state management solutions
- Learn Redux fundamentals and modern Redux Toolkit
- Implement Zustand for lightweight state management
- Apply state management patterns in real applications
- Choose the right state management solution for different scenarios
- Debug state-related issues effectively

## 🎯 Prerequisites

- Completed Module 1: JavaScript Prerequisites
- Completed Module 2: React Fundamentals  
- Completed Module 3: Component Lifecycle & Hooks
- Understanding of useReducer and useContext hooks
- Knowledge of JavaScript ES6+ features

## 📖 Module Content

### 1. State Management Overview

#### What is State Management?

State management is the process of managing the state (data) of your application in a predictable and organized way. As applications grow, managing state becomes more complex.

#### Types of State

```jsx
// 1. Local Component State
function Counter() {
  const [count, setCount] = useState(0); // Local state
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}

// 2. Shared State (between components)
function Parent() {
  const [user, setUser] = useState(null);
  return (
    <div>
      <Header user={user} />
      <Profile user={user} setUser={setUser} />
    </div>
  );
}

// 3. Global State (application-wide)
// Using Context, Redux, Zustand, etc.
```

#### When to Use Global State Management

✅ **Use Global State When:**
- State is needed by many components at different nesting levels
- Components need to share state that's not parent-child related
- State updates need to trigger updates in multiple parts of the app
- You need predictable state updates and debugging capabilities

❌ **Don't Use Global State When:**
- State is only used by one component or direct parent-child
- Simple form state or UI state (modals, dropdowns)
- Temporary or transient state

### 2. React Context API

Context provides a way to pass data through the component tree without having to pass props down manually at every level.

#### Basic Context Setup

```jsx
import React, { createContext, useContext, useReducer } from 'react';

// 1. Create Context
const AppContext = createContext();

// 2. Create Provider Component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  const value = {
    state,
    dispatch,
    // Action creators
    login: (user) => dispatch({ type: 'LOGIN', payload: user }),
    logout: () => dispatch({ type: 'LOGOUT' }),
    updateProfile: (profile) => dispatch({ type: 'UPDATE_PROFILE', payload: profile })
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

// 3. Custom Hook for Context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}

// 4. Reducer Function
const initialState = {
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null
};

function appReducer(state, action) {
  switch (action.type) {
    case 'LOGIN':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        error: null
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false
      };
    case 'UPDATE_PROFILE':
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}
```

#### Using Context in Components

```jsx
// App.js
function App() {
  return (
    <AppProvider>
      <Header />
      <MainContent />
      <Footer />
    </AppProvider>
  );
}

// Header.js
function Header() {
  const { state, logout } = useApp();
  
  return (
    <header>
      {state.isAuthenticated ? (
        <div>
          <span>Welcome, {state.user.name}!</span>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <LoginButton />
      )}
    </header>
  );
}

// Profile.js
function Profile() {
  const { state, updateProfile } = useApp();
  const [formData, setFormData] = useState({
    name: state.user?.name || '',
    email: state.user?.email || ''
  });
  
  const handleSubmit = (e) => {
    e.preventDefault();
    updateProfile(formData);
  };
  
  if (!state.isAuthenticated) {
    return <div>Please log in to view profile</div>;
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        placeholder="Name"
      />
      <input
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        placeholder="Email"
      />
      <button type="submit">Update Profile</button>
    </form>
  );
}
```

#### Multiple Contexts Pattern

```jsx
// Separate contexts for different concerns
const AuthContext = createContext();
const ThemeContext = createContext();
const CartContext = createContext();

// Compose providers
function AppProviders({ children }) {
  return (
    <AuthProvider>
      <ThemeProvider>
        <CartProvider>
          {children}
        </CartProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

// Or use a provider composer
function ComposeProviders({ providers, children }) {
  return providers.reduceRight(
    (acc, Provider) => <Provider>{acc}</Provider>,
    children
  );
}

function App() {
  return (
    <ComposeProviders providers={[AuthProvider, ThemeProvider, CartProvider]}>
      <MainApp />
    </ComposeProviders>
  );
}
```

### 3. Advanced Context Patterns

#### Context with Custom Hooks

```jsx
{% raw %}
// Theme Context Example
const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  const [fontSize, setFontSize] = useState('medium');
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };
  
  const updateFontSize = (size) => {
    setFontSize(size);
  };
  
  const themeStyles = {
    light: {
      backgroundColor: '#ffffff',
      color: '#000000',
      borderColor: '#cccccc'
    },
    dark: {
      backgroundColor: '#333333',
      color: '#ffffff',
      borderColor: '#666666'
    }
  };
  
  const fontSizes = {
    small: '14px',
    medium: '16px',
    large: '18px'
  };
  
  const value = {
    theme,
    fontSize,
    toggleTheme,
    updateFontSize,
    styles: themeStyles[theme],
    currentFontSize: fontSizes[fontSize]
  };
  
  return (
    <ThemeContext.Provider value={value}>
      <div style={{ ...themeStyles[theme], minHeight: '100vh' }}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// Usage
function ThemedButton({ children, ...props }) {
  const { styles, currentFontSize } = useTheme();
  
  return (
    <button
      style={{
        ...styles,
        fontSize: currentFontSize,
        padding: '8px 16px',
        border: `1px solid ${styles.borderColor}`,
        borderRadius: '4px'
      }}
      {...props}
    >
      {children}
    </button>
  );
}
{% endraw %}
```

#### Context with Async Operations

```jsx
const DataContext = createContext();

export function DataProvider({ children }) {
  const [state, dispatch] = useReducer(dataReducer, {
    users: [],
    posts: [],
    loading: {},
    errors: {}
  });
  
  const fetchUsers = async () => {
    dispatch({ type: 'SET_LOADING', payload: { users: true } });
    try {
      const response = await fetch('/api/users');
      const users = await response.json();
      dispatch({ type: 'SET_USERS', payload: users });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: { users: error.message } });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { users: false } });
    }
  };
  
  const createUser = async (userData) => {
    dispatch({ type: 'SET_LOADING', payload: { createUser: true } });
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      const newUser = await response.json();
      dispatch({ type: 'ADD_USER', payload: newUser });
      return newUser;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: { createUser: error.message } });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: { createUser: false } });
    }
  };
  
  const value = {
    state,
    actions: {
      fetchUsers,
      createUser
    }
  };
  
  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
}

function dataReducer(state, action) {
  switch (action.type) {
    case 'SET_USERS':
      return { ...state, users: action.payload };
    case 'ADD_USER':
      return { ...state, users: [...state.users, action.payload] };
    case 'SET_LOADING':
      return { 
        ...state, 
        loading: { ...state.loading, ...action.payload } 
      };
    case 'SET_ERROR':
      return { 
        ...state, 
        errors: { ...state.errors, ...action.payload } 
      };
    default:
      return state;
  }
}
```

### 4. Redux Fundamentals

Redux is a predictable state container for JavaScript applications.

#### Core Concepts

1. **Store**: Holds the complete state tree
2. **Actions**: Plain objects describing what happened
3. **Reducers**: Pure functions that specify how state changes
4. **Dispatch**: Method to send actions to the store

#### Basic Redux Setup

```jsx
// store.js
import { createStore, combineReducers } from 'redux';

// Action Types
const INCREMENT = 'INCREMENT';
const DECREMENT = 'DECREMENT';
const SET_USER = 'SET_USER';

// Action Creators
export const increment = () => ({ type: INCREMENT });
export const decrement = () => ({ type: DECREMENT });
export const setUser = (user) => ({ type: SET_USER, payload: user });

// Reducers
function counterReducer(state = { count: 0 }, action) {
  switch (action.type) {
    case INCREMENT:
      return { ...state, count: state.count + 1 };
    case DECREMENT:
      return { ...state, count: state.count - 1 };
    default:
      return state;
  }
}

function userReducer(state = { user: null }, action) {
  switch (action.type) {
    case SET_USER:
      return { ...state, user: action.payload };
    default:
      return state;
  }
}

// Combine Reducers
const rootReducer = combineReducers({
  counter: counterReducer,
  user: userReducer
});

// Create Store
export const store = createStore(rootReducer);
```

#### Using Redux with React

```jsx
// App.js
import { Provider } from 'react-redux';
import { store } from './store';

function App() {
  return (
    <Provider store={store}>
      <Counter />
      <UserProfile />
    </Provider>
  );
}

// Counter.js
import { useSelector, useDispatch } from 'react-redux';
import { increment, decrement } from './store';

function Counter() {
  const count = useSelector(state => state.counter.count);
  const dispatch = useDispatch();
  
  return (
    <div>
      <h2>Count: {count}</h2>
      <button onClick={() => dispatch(increment())}>+</button>
      <button onClick={() => dispatch(decrement())}>-</button>
    </div>
  );
}
```

### 5. Modern Redux with Redux Toolkit (RTK)

Redux Toolkit is the official, recommended way to write Redux logic.

#### RTK Setup

```bash
npm install @reduxjs/toolkit react-redux
```

```jsx
// store/store.js
import { configureStore } from '@reduxjs/toolkit';
import counterSlice from './counterSlice';
import userSlice from './userSlice';

export const store = configureStore({
  reducer: {
    counter: counterSlice,
    user: userSlice
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

#### Creating Slices

```jsx
// store/counterSlice.js
import { createSlice } from '@reduxjs/toolkit';

const counterSlice = createSlice({
  name: 'counter',
  initialState: {
    value: 0,
    step: 1
  },
  reducers: {
    increment: (state) => {
      state.value += state.step;
    },
    decrement: (state) => {
      state.value -= state.step;
    },
    incrementByAmount: (state, action) => {
      state.value += action.payload;
    },
    setStep: (state, action) => {
      state.step = action.payload;
    },
    reset: (state) => {
      state.value = 0;
    }
  }
});

export const { increment, decrement, incrementByAmount, setStep, reset } = counterSlice.actions;
export default counterSlice.reducer;
```

#### Async Actions with createAsyncThunk

```jsx
{% raw %}
// store/userSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk
export const fetchUser = createAsyncThunk(
  'user/fetchUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateUser = createAsyncThunk(
  'user/updateUser',
  async ({ userId, userData }, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState: {
    data: null,
    loading: false,
    error: null
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    logout: (state) => {
      state.data = null;
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch User
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update User
      .addCase(updateUser.fulfilled, (state, action) => {
        state.data = action.payload;
      });
  }
});

export const { clearError, logout } = userSlice.actions;
export default userSlice.reducer;
{% endraw %}
```

#### Using RTK in Components

```jsx
// hooks/redux.js
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from '../store/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// Counter.js
import { useAppSelector, useAppDispatch } from '../hooks/redux';
import { increment, decrement, incrementByAmount } from '../store/counterSlice';

function Counter() {
  const { value, step } = useAppSelector(state => state.counter);
  const dispatch = useAppDispatch();
  
  return (
    <div>
      <h2>Count: {value}</h2>
      <button onClick={() => dispatch(increment())}>+ {step}</button>
      <button onClick={() => dispatch(decrement())}>- {step}</button>
      <button onClick={() => dispatch(incrementByAmount(5))}>+ 5</button>
    </div>
  );
}

// UserProfile.js
function UserProfile({ userId }) {
  const { data: user, loading, error } = useAppSelector(state => state.user);
  const dispatch = useAppDispatch();
  
  useEffect(() => {
    dispatch(fetchUser(userId));
  }, [userId, dispatch]);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return <div>No user found</div>;
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <button onClick={() => dispatch(updateUser({ userId, userData: { status: 'active' } }))}>
        Activate User
      </button>
    </div>
  );
}
```

### 6. Zustand - Lightweight State Management

Zustand is a small, fast, and scalable state management solution.

#### Basic Zustand Store

```jsx
{% raw %}
// store/useStore.js
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useStore = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        count: 0,
        user: null,
        theme: 'light',
        
        // Actions
        increment: () => set((state) => ({ count: state.count + 1 })),
        decrement: () => set((state) => ({ count: state.count - 1 })),
        reset: () => set({ count: 0 }),
        
        setUser: (user) => set({ user }),
        logout: () => set({ user: null }),
        
        toggleTheme: () => set((state) => ({
          theme: state.theme === 'light' ? 'dark' : 'light'
        })),
        
        // Async actions
        fetchUser: async (id) => {
          try {
            const response = await fetch(`/api/users/${id}`);
            const user = await response.json();
            set({ user });
          } catch (error) {
            console.error('Failed to fetch user:', error);
          }
        }
      }),
      {
        name: 'app-storage', // localStorage key
        partialize: (state) => ({ 
          theme: state.theme,
          user: state.user 
        }) // only persist theme and user
      }
    )
  )
);

export default useStore;
{% endraw %}
```

#### Using Zustand in Components

```jsx
// Counter.js
import useStore from '../store/useStore';

function Counter() {
  const { count, increment, decrement, reset } = useStore();
  
  return (
    <div>
      <h2>Count: {count}</h2>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}

// Profile.js
function Profile() {
  const { user, fetchUser, logout } = useStore();
  
  useEffect(() => {
    if (!user) {
      fetchUser(1);
    }
  }, [user, fetchUser]);
  
  return (
    <div>
      {user ? (
        <>
          <h1>{user.name}</h1>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
}
```

#### Advanced Zustand Patterns

```jsx
// Slices pattern for large stores
const createCounterSlice = (set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 }))
});

const createUserSlice = (set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null })
});

const useStore = create((...a) => ({
  ...createCounterSlice(...a),
  ...createUserSlice(...a)
}));

// Selectors for performance
const useCount = () => useStore((state) => state.count);
const useUser = () => useStore((state) => state.user);
```

## 🎯 Practical Exercises

### Exercise 1: Shopping Cart with Context
Build a shopping cart using React Context API with add, remove, and update quantity functionality.

### Exercise 2: Todo App with Redux Toolkit
Create a comprehensive todo application using RTK with categories, filters, and persistence.

### Exercise 3: User Dashboard with Zustand
Build a user dashboard with authentication, profile management, and settings using Zustand.

### Exercise 4: State Management Comparison
Implement the same feature using Context, Redux, and Zustand to understand the differences.

## 📊 Assessment Criteria

### Knowledge Check
- [ ] Explain when to use local vs global state
- [ ] Demonstrate proper Context API usage with custom hooks
- [ ] Implement Redux with proper action/reducer patterns
- [ ] Use Redux Toolkit for modern Redux development
- [ ] Apply Zustand for lightweight state management
- [ ] Choose appropriate state management solution for different scenarios

### Practical Assessment
- [ ] Build a multi-feature app with global state management
- [ ] Implement proper error handling in state management
- [ ] Create reusable state management patterns
- [ ] Optimize performance with proper selectors
- [ ] Handle async operations in state management

### Code Quality
- [ ] Organize state management code properly
- [ ] Use TypeScript with state management libraries
- [ ] Implement proper testing for state management
- [ ] Follow best practices for each state management solution

## 🚀 Project: E-commerce Application

Build a complete e-commerce application with multiple state management solutions:

**Requirements:**
- User authentication and profile management
- Product catalog with categories and filters
- Shopping cart with add/remove/update functionality
- Order history and tracking
- Theme and user preferences
- Admin panel for product management

**State Management Requirements:**
- Use Context API for theme and user preferences
- Use Redux Toolkit for product catalog and orders
- Use Zustand for shopping cart
- Implement proper error handling and loading states
- Add data persistence where appropriate

## 📚 Additional Resources

### Documentation
- [React Context API](https://reactjs.org/docs/context.html)
- [Redux Official Documentation](https://redux.js.org/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)

### Best Practices
- State management decision tree
- Performance considerations
- Testing state management
- TypeScript integration

## ⏭️ Next Steps

After mastering this module, you'll be ready for:
- **Module 5**: Advanced Hooks & Patterns
- **Module 6**: Performance Optimization
- Building complex applications with proper state architecture

---

**Estimated Time:** 2-3 weeks  
**Difficulty:** Intermediate to Advanced  
**Prerequisites:** Modules 1-3 completed