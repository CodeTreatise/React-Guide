# Context API vs Redux vs Zustand - Comparison Guide

## Overview

This guide compares three popular state management solutions in React: Context API, Redux, and Zustand. We'll build the same feature using each approach to understand their differences.

## Feature: User Authentication System

We'll implement a user authentication system with:
- Login/logout functionality
- User profile management
- Loading states
- Error handling
- Persistence

## 1. Context API Implementation

### Step 1: Create Auth Context

```jsx
// contexts/AuthContext.js
import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AuthContext = createContext();

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        loading: false,
        error: null
      };
    
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        loading: false,
        error: action.payload
      };
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        error: null
      };
    
    case 'UPDATE_PROFILE':
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
    
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    
    default:
      return state;
  }
}

// Provider Component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  
  // Check for existing session on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      dispatch({ type: 'LOGIN_SUCCESS', payload: JSON.parse(savedUser) });
    }
  }, []);
  
  // Actions
  const login = async (credentials) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const user = await response.json();
      localStorage.setItem('user', JSON.stringify(user));
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE', payload: error.message });
    }
  };
  
  const logout = () => {
    localStorage.removeItem('user');
    dispatch({ type: 'LOGOUT' });
  };
  
  const updateProfile = async (profileData) => {
    try {
      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
      });
      
      const updatedUser = await response.json();
      localStorage.setItem('user', JSON.stringify(updatedUser));
      dispatch({ type: 'UPDATE_PROFILE', payload: updatedUser });
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE', payload: error.message });
    }
  };
  
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };
  
  const value = {
    ...state,
    login,
    logout,
    updateProfile,
    clearError
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Step 2: Use Context in Components

```jsx
// components/LoginForm.js
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export function LoginForm() {
  const { login, loading, error, clearError } = useAuth();
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();
    await login(credentials);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      {error && <div className="error">{error}</div>}
      
      <input
        type="email"
        value={credentials.email}
        onChange={(e) => setCredentials({...credentials, email: e.target.value})}
        placeholder="Email"
        required
      />
      
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        placeholder="Password"
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

// components/Profile.js
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export function Profile() {
  const { user, updateProfile, logout } = useAuth();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || ''
  });
  
  const handleUpdate = async (e) => {
    e.preventDefault();
    await updateProfile(formData);
    setEditing(false);
  };
  
  return (
    <div>
      <h2>Profile</h2>
      {editing ? (
        <form onSubmit={handleUpdate}>
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
          <button type="submit">Save</button>
          <button type="button" onClick={() => setEditing(false)}>Cancel</button>
        </form>
      ) : (
        <div>
          <p>Name: {user?.name}</p>
          <p>Email: {user?.email}</p>
          <button onClick={() => setEditing(true)}>Edit Profile</button>
          <button onClick={logout}>Logout</button>
        </div>
      )}
    </div>
  );
}
```

## 2. Redux Toolkit Implementation

### Step 1: Configure Store

```jsx
// store/store.js
import { configureStore } from '@reduxjs/toolkit';
import authSlice from './authSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST']
      }
    })
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Step 2: Create Auth Slice

```jsx
// store/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const user = await response.json();
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateUserProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
      });
      
      const updatedUser = await response.json();
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return updatedUser;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Initial state
const initialState = {
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  isAuthenticated: !!localStorage.getItem('user'),
  loading: false,
  error: null
};

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      localStorage.removeItem('user');
      state.user = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update Profile
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.user = action.payload;
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.error = action.payload;
      });
  }
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
```

### Step 3: Use Redux in Components

```jsx
// hooks/redux.js
import { useDispatch, useSelector } from 'react-redux';

export const useAppDispatch = () => useDispatch();
export const useAppSelector = useSelector;

// components/LoginForm.js
import { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { loginUser, clearError } from '../store/authSlice';

export function LoginForm() {
  const dispatch = useAppDispatch();
  const { loading, error } = useAppSelector(state => state.auth);
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    dispatch(clearError());
    dispatch(loginUser(credentials));
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      {error && <div className="error">{error}</div>}
      
      <input
        type="email"
        value={credentials.email}
        onChange={(e) => setCredentials({...credentials, email: e.target.value})}
        placeholder="Email"
        required
      />
      
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        placeholder="Password"
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

// components/Profile.js
import { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { updateUserProfile, logout } from '../store/authSlice';

export function Profile() {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector(state => state.auth);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || ''
  });
  
  const handleUpdate = async (e) => {
    e.preventDefault();
    dispatch(updateUserProfile(formData));
    setEditing(false);
  };
  
  const handleLogout = () => {
    dispatch(logout());
  };
  
  return (
    <div>
      <h2>Profile</h2>
      {editing ? (
        <form onSubmit={handleUpdate}>
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
          <button type="submit">Save</button>
          <button type="button" onClick={() => setEditing(false)}>Cancel</button>
        </form>
      ) : (
        <div>
          <p>Name: {user?.name}</p>
          <p>Email: {user?.email}</p>
          <button onClick={() => setEditing(true)}>Edit Profile</button>
          <button onClick={handleLogout}>Logout</button>
        </div>
      )}
    </div>
  );
}
```

## 3. Zustand Implementation

### Step 1: Create Auth Store

```jsx
// stores/authStore.js
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useAuthStore = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        user: null,
        isAuthenticated: false,
        loading: false,
        error: null,
        
        // Actions
        login: async (credentials) => {
          set({ loading: true, error: null });
          try {
            const response = await fetch('/api/auth/login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(credentials)
            });
            
            if (!response.ok) {
              throw new Error('Login failed');
            }
            
            const user = await response.json();
            set({ 
              user, 
              isAuthenticated: true, 
              loading: false, 
              error: null 
            });
          } catch (error) {
            set({ 
              user: null, 
              isAuthenticated: false, 
              loading: false, 
              error: error.message 
            });
          }
        },
        
        logout: () => {
          set({ 
            user: null, 
            isAuthenticated: false, 
            error: null 
          });
        },
        
        updateProfile: async (profileData) => {
          try {
            const response = await fetch('/api/user/profile', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(profileData)
            });
            
            const updatedUser = await response.json();
            set({ user: updatedUser });
          } catch (error) {
            set({ error: error.message });
          }
        },
        
        clearError: () => set({ error: null }),
        
        // Computed values
        isLoggedIn: () => get().isAuthenticated,
        getCurrentUser: () => get().user
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated
        })
      }
    ),
    { name: 'auth-store' }
  )
);

export default useAuthStore;
```

### Step 2: Use Zustand in Components

```jsx
// components/LoginForm.js
import { useState } from 'react';
import useAuthStore from '../stores/authStore';

export function LoginForm() {
  const { login, loading, error, clearError } = useAuthStore();
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();
    await login(credentials);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      {error && <div className="error">{error}</div>}
      
      <input
        type="email"
        value={credentials.email}
        onChange={(e) => setCredentials({...credentials, email: e.target.value})}
        placeholder="Email"
        required
      />
      
      <input
        type="password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
        placeholder="Password"
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

// components/Profile.js
import { useState } from 'react';
import useAuthStore from '../stores/authStore';

export function Profile() {
  const { user, updateProfile, logout } = useAuthStore();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || ''
  });
  
  const handleUpdate = async (e) => {
    e.preventDefault();
    await updateProfile(formData);
    setEditing(false);
  };
  
  return (
    <div>
      <h2>Profile</h2>
      {editing ? (
        <form onSubmit={handleUpdate}>
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
          <button type="submit">Save</button>
          <button type="button" onClick={() => setEditing(false)}>Cancel</button>
        </form>
      ) : (
        <div>
          <p>Name: {user?.name}</p>
          <p>Email: {user?.email}</p>
          <button onClick={() => setEditing(true)}>Edit Profile</button>
          <button onClick={logout}>Logout</button>
        </div>
      )}
    </div>
  );
}

// Selective subscriptions for performance
const UserName = () => {
  const userName = useAuthStore(state => state.user?.name);
  return <span>Welcome, {userName}!</span>;
};
```

## Comparison Summary

| Feature | Context API | Redux Toolkit | Zustand |
|---------|-------------|---------------|---------|
| **Bundle Size** | Built-in | ~13KB | ~3KB |
| **Learning Curve** | Medium | High | Low |
| **Boilerplate** | Medium | Low (with RTK) | Very Low |
| **DevTools** | Limited | Excellent | Good |
| **TypeScript** | Good | Excellent | Excellent |
| **Performance** | Can cause re-renders | Optimized | Optimized |
| **Async Handling** | Manual | Built-in | Manual |
| **Persistence** | Manual | Middleware | Built-in |
| **Middleware** | Manual | Rich ecosystem | Some available |

## When to Use Each

### Context API
✅ **Use when:**
- Small to medium applications
- State is mostly UI-related
- Limited number of components need the state
- You want to avoid external dependencies

❌ **Avoid when:**
- Complex state logic
- Many frequent updates
- Need advanced debugging tools

### Redux Toolkit
✅ **Use when:**
- Large, complex applications
- Need predictable state updates
- Complex async operations
- Team needs powerful debugging tools
- Need middleware ecosystem

❌ **Avoid when:**
- Simple applications
- Team is new to Redux concepts
- Quick prototyping

### Zustand
✅ **Use when:**
- Want simplicity with power
- Need good performance out of the box
- Small to medium applications
- Like the store-based approach
- Want minimal boilerplate

❌ **Avoid when:**
- Need extensive middleware ecosystem
- Require advanced debugging tools
- Team prefers flux-style architecture

## Performance Considerations

### Context API
```jsx
// Problem: All consumers re-render when any context value changes
const AppContext = createContext();

// Solution: Split contexts by concern
const UserContext = createContext();
const ThemeContext = createContext();
const SettingsContext = createContext();

// Or use useMemo for context values
function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  
  const userValue = useMemo(() => ({ user, setUser }), [user]);
  const themeValue = useMemo(() => ({ theme, setTheme }), [theme]);
  
  return (
    <UserContext.Provider value={userValue}>
      <ThemeContext.Provider value={themeValue}>
        {children}
      </ThemeContext.Provider>
    </UserContext.Provider>
  );
}
```

### Redux
```jsx
// Use selectors to prevent unnecessary re-renders
const selectUser = (state) => state.auth.user;
const selectUserName = createSelector(
  [selectUser],
  (user) => user?.name
);

// In component
const userName = useAppSelector(selectUserName);
```

### Zustand
```jsx
// Use selectors for specific slices of state
const userName = useAuthStore(state => state.user?.name);
const isLoading = useAuthStore(state => state.loading);

// Use shallow for objects
import { shallow } from 'zustand/shallow';
const { user, loading } = useAuthStore(
  state => ({ user: state.user, loading: state.loading }),
  shallow
);
```

## Conclusion

Each state management solution has its place:

- **Context API**: Great for simple global state and avoiding prop drilling
- **Redux Toolkit**: Best for complex applications with predictable state requirements
- **Zustand**: Perfect balance of simplicity and power for most applications

Choose based on your application's complexity, team expertise, and specific requirements.
