# Advanced Context API Patterns

## Table of Contents
1. [Context API Deep Dive](#context-api-deep-dive)
2. [Advanced Context Patterns](#advanced-context-patterns)
3. [Performance Optimization](#performance-optimization)
4. [Context Composition](#context-composition)
5. [Type Safety with TypeScript](#type-safety-with-typescript)
6. [Testing Context Providers](#testing-context-providers)
7. [Real-World Examples](#real-world-examples)
8. [Common Pitfalls](#common-pitfalls)
9. [Best Practices](#best-practices)

## Context API Deep Dive

### Understanding Context Fundamentals

The Context API provides a way to pass data through the component tree without having to pass props down manually at every level.

```jsx
{% raw %}
{% raw %}
// Basic Context Setup
import React, { createContext, useContext, useState } from 'react';

// 1. Create Context
const ThemeContext = createContext();

// 2. Create Provider Component
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  const value = {
    theme,
    setTheme,
    toggleTheme: () => setTheme(prev => prev === 'light' ? 'dark' : 'light')
  };
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. Custom Hook for Consuming Context
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// 4. Usage in Components
function App() {
  return (
    <ThemeProvider>
      <Header />
      <Main />
      <Footer />
    </ThemeProvider>
  );
}

function Header() {
  const { theme, toggleTheme } = useTheme();
  return (
    <header className={`header header--${theme}`}>
      <button onClick={toggleTheme}>
        Switch to {theme === 'light' ? 'dark' : 'light'} mode
      </button>
    </header>
  );
}
{% endraw %}
{% endraw %}
```

### Context with useReducer

For complex state logic, combine Context with useReducer:

```jsx
// State and Actions
const initialState = {
  user: null,
  loading: false,
  error: null,
  notifications: []
};

const actionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_USER: 'SET_USER',
  SET_ERROR: 'SET_ERROR',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Reducer Function
function authReducer(state, action) {
  switch (action.type) {
    case actionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
        error: null
      };
      
    case actionTypes.SET_USER:
      return {
        ...state,
        user: action.payload,
        loading: false,
        error: null
      };
      
    case actionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };
      
    case actionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, action.payload]
      };
      
    case actionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(
          notification => notification.id !== action.payload
        )
      };
      
    case actionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
      
    default:
      return state;
  }
}

// Context Provider with useReducer
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  
  // Action Creators
  const actions = {
    setLoading: (loading) => dispatch({
      type: actionTypes.SET_LOADING,
      payload: loading
    }),
    
    setUser: (user) => dispatch({
      type: actionTypes.SET_USER,
      payload: user
    }),
    
    setError: (error) => dispatch({
      type: actionTypes.SET_ERROR,
      payload: error
    }),
    
    addNotification: (notification) => dispatch({
      type: actionTypes.ADD_NOTIFICATION,
      payload: {
        id: Date.now(),
        timestamp: new Date(),
        ...notification
      }
    }),
    
    removeNotification: (id) => dispatch({
      type: actionTypes.REMOVE_NOTIFICATION,
      payload: id
    }),
    
    clearError: () => dispatch({
      type: actionTypes.CLEAR_ERROR
    })
  };
  
  // Async Actions
  const login = async (credentials) => {
    try {
      actions.setLoading(true);
      const response = await authService.login(credentials);
      actions.setUser(response.user);
      actions.addNotification({
        type: 'success',
        message: 'Successfully logged in!'
      });
    } catch (error) {
      actions.setError(error.message);
      actions.addNotification({
        type: 'error',
        message: 'Login failed. Please try again.'
      });
    }
  };
  
  const logout = async () => {
    try {
      actions.setLoading(true);
      await authService.logout();
      actions.setUser(null);
      actions.addNotification({
        type: 'info',
        message: 'Successfully logged out'
      });
    } catch (error) {
      actions.setError(error.message);
    }
  };
  
  const value = {
    ...state,
    ...actions,
    login,
    logout
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
```

## Advanced Context Patterns

### 1. Multiple Contexts Pattern

Split contexts by domain to avoid unnecessary re-renders:

```jsx
// User Context
const UserContext = createContext();
export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  
  return (
    <UserContext.Provider value={{ user, setUser, profile, setProfile }}>
      {children}
    </UserContext.Provider>
  );
}

// Settings Context
const SettingsContext = createContext();
export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState({
    theme: 'light',
    language: 'en',
    notifications: true
  });
  
  return (
    <SettingsContext.Provider value={{ settings, setSettings }}>
      {children}
    </SettingsContext.Provider>
  );
}

// App Context Composition
function App() {
  return (
    <UserProvider>
      <SettingsProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </Router>
      </SettingsProvider>
    </UserProvider>
  );
}
```

### 2. Context Factory Pattern

Create reusable context factories:

```jsx
{% raw %}
{% raw %}
// Generic Context Factory
function createContext(name, defaultValue = null) {
  const Context = React.createContext(defaultValue);
  
  function useContext() {
    const context = React.useContext(Context);
    if (!context) {
      throw new Error(`use${name} must be used within a ${name}Provider`);
    }
    return context;
  }
  
  function Provider({ children, ...props }) {
    return <Context.Provider {...props}>{children}</Context.Provider>;
  }
  
  return [Provider, useContext, Context];
}

// Usage
const [CounterProvider, useCounter] = createContext('Counter');

function CounterApp() {
  const [count, setCount] = useState(0);
  
  return (
    <CounterProvider value={{ count, setCount }}>
      <Counter />
      <ResetButton />
    </CounterProvider>
  );
}
{% endraw %}
{% endraw %}
```

### 3. Compound Context Pattern

Combine multiple related contexts:

```jsx
// Shopping Cart Context System
const CartStateContext = createContext();
const CartDispatchContext = createContext();

function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD_ITEM':
      const existingItem = state.items.find(item => item.id === action.payload.id);
      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + action.payload.quantity }
              : item
          )
        };
      }
      return {
        ...state,
        items: [...state.items, action.payload]
      };
      
    case 'REMOVE_ITEM':
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload)
      };
      
    case 'UPDATE_QUANTITY':
      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        )
      };
      
    case 'CLEAR_CART':
      return {
        ...state,
        items: []
      };
      
    default:
      return state;
  }
}

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, {
    items: [],
    total: 0,
    tax: 0
  });
  
  // Calculate derived values
  const cartState = useMemo(() => ({
    ...state,
    total: state.items.reduce((total, item) => total + (item.price * item.quantity), 0),
    itemCount: state.items.reduce((count, item) => count + item.quantity, 0)
  }), [state]);
  
  return (
    <CartStateContext.Provider value={cartState}>
      <CartDispatchContext.Provider value={dispatch}>
        {children}
      </CartDispatchContext.Provider>
    </CartStateContext.Provider>
  );
}

// Custom hooks for accessing cart
export function useCartState() {
  const context = useContext(CartStateContext);
  if (!context) {
    throw new Error('useCartState must be used within CartProvider');
  }
  return context;
}

export function useCartDispatch() {
  const context = useContext(CartDispatchContext);
  if (!context) {
    throw new Error('useCartDispatch must be used within CartProvider');
  }
  return context;
}

// High-level hook for cart actions
export function useCart() {
  const state = useCartState();
  const dispatch = useCartDispatch();
  
  const actions = useMemo(() => ({
    addItem: (item) => dispatch({ type: 'ADD_ITEM', payload: item }),
    removeItem: (id) => dispatch({ type: 'REMOVE_ITEM', payload: id }),
    updateQuantity: (id, quantity) => dispatch({ 
      type: 'UPDATE_QUANTITY', 
      payload: { id, quantity } 
    }),
    clearCart: () => dispatch({ type: 'CLEAR_CART' })
  }), [dispatch]);
  
  return { ...state, ...actions };
}
```

## Performance Optimization

### 1. Context Value Memoization

Prevent unnecessary re-renders by memoizing context values:

```jsx
// Problem: Creates new object on every render
function BadProvider({ children }) {
  const [user, setUser] = useState(null);
  const [settings, setSettings] = useState({});
  
  // This creates a new object every render!
  return (
    <UserContext.Provider value={{ user, setUser, settings, setSettings }}>
      {children}
    </UserContext.Provider>
  );
}

// Solution: Memoize the context value
function GoodProvider({ children }) {
  const [user, setUser] = useState(null);
  const [settings, setSettings] = useState({});
  
  const value = useMemo(() => ({
    user,
    setUser,
    settings,
    setSettings
  }), [user, settings]);
  
  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}

// Better: Separate frequently changing values
function OptimizedProvider({ children }) {
  const [user, setUser] = useState(null);
  const [settings, setSettings] = useState({});
  
  // Separate stable and changing values
  const stableValue = useMemo(() => ({
    setUser,
    setSettings
  }), []);
  
  const dynamicValue = useMemo(() => ({
    user,
    settings
  }), [user, settings]);
  
  return (
    <StableContext.Provider value={stableValue}>
      <DynamicContext.Provider value={dynamicValue}>
        {children}
      </DynamicContext.Provider>
    </StableContext.Provider>
  );
}
```

### 2. Split Contexts for Performance

Split contexts based on update frequency:

```jsx
// Fast-changing context (user interactions)
const UIStateContext = createContext();
export function UIStateProvider({ children }) {
  const [loading, setLoading] = useState(false);
  const [modal, setModal] = useState(null);
  const [toast, setToast] = useState(null);
  
  const value = useMemo(() => ({
    loading,
    setLoading,
    modal,
    setModal,
    toast,
    setToast
  }), [loading, modal, toast]);
  
  return (
    <UIStateContext.Provider value={value}>
      {children}
    </UIStateContext.Provider>
  );
}

// Slow-changing context (app configuration)
const AppConfigContext = createContext();
export function AppConfigProvider({ children }) {
  const [config, setConfig] = useState({
    apiUrl: process.env.REACT_APP_API_URL,
    theme: 'light',
    language: 'en'
  });
  
  const value = useMemo(() => ({
    config,
    updateConfig: (updates) => setConfig(prev => ({ ...prev, ...updates }))
  }), [config]);
  
  return (
    <AppConfigContext.Provider value={value}>
      {children}
    </AppConfigContext.Provider>
  );
}
```

### 3. Selector Pattern for Context

Implement selectors to prevent unnecessary re-renders:

```jsx
{% raw %}
{% raw %}
// Context with selector support
function createContextWithSelector(name) {
  const Context = createContext();
  
  function Provider({ value, children }) {
    const contextValue = useMemo(() => value, [value]);
    return <Context.Provider value={contextValue}>{children}</Context.Provider>;
  }
  
  function useContextSelector(selector) {
    const context = useContext(Context);
    if (!context) {
      throw new Error(`use${name}Selector must be used within ${name}Provider`);
    }
    
    return useMemo(() => selector(context), [context, selector]);
  }
  
  return [Provider, useContextSelector];
}

// Usage
const [UserProvider, useUserSelector] = createContextWithSelector('User');

function UserApp() {
  const [user, setUser] = useState({
    name: 'John',
    email: 'john@example.com',
    preferences: { theme: 'dark' }
  });
  
  return (
    <UserProvider value={{ user, setUser }}>
      <UserName />
      <UserEmail />
      <UserTheme />
    </UserProvider>
  );
}

// Components only re-render when their selected data changes
function UserName() {
  const name = useUserSelector(state => state.user.name);
  return <div>Name: {name}</div>;
}

function UserEmail() {
  const email = useUserSelector(state => state.user.email);
  return <div>Email: {email}</div>;
}

function UserTheme() {
  const theme = useUserSelector(state => state.user.preferences.theme);
  return <div>Theme: {theme}</div>;
}
{% endraw %}
{% endraw %}
```

## Context Composition

### Combining Multiple Providers

```jsx
// Provider Composition Component
function AppProviders({ children }) {
  return (
    <ErrorBoundary>
      <QueryClient>
        <BrowserRouter>
          <AuthProvider>
            <ThemeProvider>
              <NotificationProvider>
                <CartProvider>
                  {children}
                </CartProvider>
              </NotificationProvider>
            </ThemeProvider>
          </AuthProvider>
        </BrowserRouter>
      </QueryClient>
    </ErrorBoundary>
  );
}

// Compose function for cleaner syntax
function compose(...providers) {
  return ({ children }) => {
    return providers.reduceRight(
      (acc, Provider) => <Provider>{acc}</Provider>,
      children
    );
  };
}

// Usage
const AppProviders = compose(
  ErrorBoundary,
  QueryClient,
  BrowserRouter,
  AuthProvider,
  ThemeProvider,
  NotificationProvider,
  CartProvider
);

function App() {
  return (
    <AppProviders>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </AppProviders>
  );
}
```

### Provider Factory Pattern

```jsx
{% raw %}
{% raw %}
// Generic Provider Factory
function createProvider(name, useHook) {
  const Context = createContext();
  
  function Provider({ children, ...props }) {
    const value = useHook(props);
    return <Context.Provider value={value}>{children}</Context.Provider>;
  }
  
  function useContext() {
    const context = React.useContext(Context);
    if (!context) {
      throw new Error(`use${name} must be used within ${name}Provider`);
    }
    return context;
  }
  
  return [Provider, useContext];
}

// Custom hooks for state logic
function useAuthState({ initialUser = null } = {}) {
  const [user, setUser] = useState(initialUser);
  const [loading, setLoading] = useState(false);
  
  const login = useCallback(async (credentials) => {
    setLoading(true);
    try {
      const user = await authService.login(credentials);
      setUser(user);
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);
  
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authService.logout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);
  
  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  };
}

// Create providers using factory
const [AuthProvider, useAuth] = createProvider('Auth', useAuthState);
const [ThemeProvider, useTheme] = createProvider('Theme', useThemeState);
{% endraw %}
{% endraw %}
```

## Type Safety with TypeScript

### Strongly Typed Context

```tsx
// Define context types
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'moderator';
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
}

interface LoginCredentials {
  email: string;
  password: string;
}

// Create typed context
const AuthContext = createContext<AuthContextType | null>(null);

// Typed provider
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const login = useCallback(async (credentials: LoginCredentials) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authAPI.login(credentials);
      setUser(response.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);
  
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authAPI.logout();
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
    } finally {
      setLoading(false);
    }
  }, []);
  
  const updateProfile = useCallback(async (updates: Partial<User>) => {
    if (!user) throw new Error('No user logged in');
    
    setLoading(true);
    try {
      const updatedUser = await authAPI.updateProfile(user.id, updates);
      setUser(updatedUser);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [user]);
  
  const value: AuthContextType = {
    user,
    loading,
    error,
    login,
    logout,
    updateProfile
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Typed hook
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// Type-safe selectors
export function useAuthUser(): User | null {
  return useAuth().user;
}

export function useAuthActions() {
  const { login, logout, updateProfile } = useAuth();
  return { login, logout, updateProfile };
}
```

### Generic Context Factory with TypeScript

```tsx
{% raw %}
{% raw %}
// Generic context factory with full type safety
function createTypedContext<T>(name: string) {
  const Context = createContext<T | null>(null);
  
  function useContext(): T {
    const context = React.useContext(Context);
    if (!context) {
      throw new Error(`use${name} must be used within ${name}Provider`);
    }
    return context;
  }
  
  function Provider({ 
    children, 
    value 
  }: { 
    children: React.ReactNode; 
    value: T;
  }) {
    return <Context.Provider value={value}>{children}</Context.Provider>;
  }
  
  return [Provider, useContext, Context] as const;
}

// Usage with full type inference
interface CounterContextType {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

const [CounterProvider, useCounter] = createTypedContext<CounterContextType>('Counter');

function CounterApp() {
  const [count, setCount] = useState(0);
  
  const value: CounterContextType = {
    count,
    increment: () => setCount(c => c + 1),
    decrement: () => setCount(c => c - 1),
    reset: () => setCount(0)
  };
  
  return (
    <CounterProvider value={value}>
      <Counter />
    </CounterProvider>
  );
}
{% endraw %}
{% endraw %}
```

## Testing Context Providers

### Basic Context Testing

```jsx
// Testing utilities
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';

// Test component
function TestComponent() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button data-testid="toggle" onClick={toggleTheme}>
        Toggle
      </button>
    </div>
  );
}

// Helper function to render with provider
function renderWithTheme(ui, { initialTheme = 'light' } = {}) {
  function Wrapper({ children }) {
    return <ThemeProvider initialTheme={initialTheme}>{children}</ThemeProvider>;
  }
  return render(ui, { wrapper: Wrapper });
}

describe('ThemeContext', () => {
  test('provides theme value', () => {
    renderWithTheme(<TestComponent />);
    expect(screen.getByTestId('theme')).toHaveTextContent('light');
  });
  
  test('toggles theme', () => {
    renderWithTheme(<TestComponent />);
    
    const toggleButton = screen.getByTestId('toggle');
    const themeDisplay = screen.getByTestId('theme');
    
    expect(themeDisplay).toHaveTextContent('light');
    
    fireEvent.click(toggleButton);
    expect(themeDisplay).toHaveTextContent('dark');
    
    fireEvent.click(toggleButton);
    expect(themeDisplay).toHaveTextContent('light');
  });
  
  test('starts with custom initial theme', () => {
    renderWithTheme(<TestComponent />, { initialTheme: 'dark' });
    expect(screen.getByTestId('theme')).toHaveTextContent('dark');
  });
});
```

### Testing Context with Mock Providers

```jsx
// Mock provider for testing
function createMockAuthProvider(mockValue) {
  return function MockAuthProvider({ children }) {
    return (
      <AuthContext.Provider value={mockValue}>
        {children}
      </AuthContext.Provider>
    );
  };
}

// Test with mocked context
describe('LoginForm', () => {
  test('calls login function on submit', async () => {
    const mockLogin = jest.fn().mockResolvedValue(undefined);
    const MockProvider = createMockAuthProvider({
      user: null,
      loading: false,
      error: null,
      login: mockLogin,
      logout: jest.fn()
    });
    
    render(
      <MockProvider>
        <LoginForm />
      </MockProvider>
    );
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });
});
```

### Integration Testing with Multiple Contexts

```jsx
// Test helper for multiple providers
function renderWithProviders(
  ui,
  {
    preloadedState = {},
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <QueryClient client={queryClient}>
          <AuthProvider>
            <ThemeProvider>
              <NotificationProvider>
                {children}
              </NotificationProvider>
            </ThemeProvider>
          </AuthProvider>
        </QueryClient>
      </BrowserRouter>
    );
  }
  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

// Integration test
describe('App Integration', () => {
  test('user can login and see dashboard', async () => {
    // Mock API
    server.use(
      rest.post('/api/auth/login', (req, res, ctx) => {
        return res(
          ctx.json({
            user: { id: '1', name: 'John Doe', email: 'john@example.com' }
          })
        );
      })
    );
    
    renderWithProviders(<App />);
    
    // Navigate to login
    fireEvent.click(screen.getByText('Login'));
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'john@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password' }
    });
    
    // Submit
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // Verify user is logged in
    await waitFor(() => {
      expect(screen.getByText('Welcome, John Doe')).toBeInTheDocument();
    });
  });
});
```

## Real-World Examples

### E-commerce Shopping Cart

```jsx
{% raw %}
{% raw %}
// Complete shopping cart implementation
const CartContext = createContext();

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, {
    items: [],
    shipping: null,
    discount: null,
    tax: 0.08
  });
  
  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('shopping-cart');
    if (savedCart) {
      dispatch({ type: 'LOAD_CART', payload: JSON.parse(savedCart) });
    }
  }, []);
  
  // Save cart to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('shopping-cart', JSON.stringify(state));
  }, [state]);
  
  // Calculated values
  const cartData = useMemo(() => {
    const subtotal = state.items.reduce(
      (sum, item) => sum + (item.price * item.quantity), 
      0
    );
    
    const discountAmount = state.discount 
      ? (subtotal * state.discount.percentage / 100)
      : 0;
      
    const taxAmount = (subtotal - discountAmount) * state.tax;
    const shippingCost = state.shipping?.cost || 0;
    const total = subtotal - discountAmount + taxAmount + shippingCost;
    
    return {
      ...state,
      subtotal,
      discountAmount,
      taxAmount,
      shippingCost,
      total,
      itemCount: state.items.reduce((sum, item) => sum + item.quantity, 0)
    };
  }, [state]);
  
  const actions = {
    addItem: (product, quantity = 1) => {
      dispatch({
        type: 'ADD_ITEM',
        payload: { ...product, quantity }
      });
    },
    
    removeItem: (productId) => {
      dispatch({ type: 'REMOVE_ITEM', payload: productId });
    },
    
    updateQuantity: (productId, quantity) => {
      if (quantity <= 0) {
        dispatch({ type: 'REMOVE_ITEM', payload: productId });
      } else {
        dispatch({
          type: 'UPDATE_QUANTITY',
          payload: { productId, quantity }
        });
      }
    },
    
    applyDiscount: (discount) => {
      dispatch({ type: 'APPLY_DISCOUNT', payload: discount });
    },
    
    setShipping: (shipping) => {
      dispatch({ type: 'SET_SHIPPING', payload: shipping });
    },
    
    clearCart: () => {
      dispatch({ type: 'CLEAR_CART' });
    }
  };
  
  return (
    <CartContext.Provider value={{ ...cartData, ...actions }}>
      {children}
    </CartContext.Provider>
  );
}

// Hook for using cart
export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
}

// Cart components
function CartSummary() {
  const { items, subtotal, total, itemCount } = useCart();
  
  if (itemCount === 0) {
    return <div>Your cart is empty</div>;
  }
  
  return (
    <div className="cart-summary">
      <h3>Cart Summary</h3>
      <div>{itemCount} items</div>
      <div>Subtotal: ${subtotal.toFixed(2)}</div>
      <div>Total: ${total.toFixed(2)}</div>
    </div>
  );
}

function CartItem({ item }) {
  const { updateQuantity, removeItem } = useCart();
  
  return (
    <div className="cart-item">
      <img src={item.image} alt={item.name} />
      <div>
        <h4>{item.name}</h4>
        <p>${item.price}</p>
      </div>
      <div>
        <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>
          -
        </button>
        <span>{item.quantity}</span>
        <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>
          +
        </button>
      </div>
      <button onClick={() => removeItem(item.id)}>
        Remove
      </button>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

### Multi-Step Form Context

```jsx
// Multi-step form with context
const FormContext = createContext();

export function MultiStepFormProvider({ children }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    personal: {},
    contact: {},
    preferences: {},
    review: {}
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  const steps = [
    { key: 'personal', title: 'Personal Information', component: PersonalStep },
    { key: 'contact', title: 'Contact Details', component: ContactStep },
    { key: 'preferences', title: 'Preferences', component: PreferencesStep },
    { key: 'review', title: 'Review & Submit', component: ReviewStep }
  ];
  
  const currentStepKey = steps[currentStep]?.key;
  
  const updateStepData = useCallback((stepKey, data) => {
    setFormData(prev => ({
      ...prev,
      [stepKey]: { ...prev[stepKey], ...data }
    }));
  }, []);
  
  const validateStep = useCallback((stepKey) => {
    const stepData = formData[stepKey];
    const stepErrors = {};
    
    switch (stepKey) {
      case 'personal':
        if (!stepData.firstName) stepErrors.firstName = 'First name is required';
        if (!stepData.lastName) stepErrors.lastName = 'Last name is required';
        if (!stepData.birthDate) stepErrors.birthDate = 'Birth date is required';
        break;
        
      case 'contact':
        if (!stepData.email) stepErrors.email = 'Email is required';
        if (!stepData.phone) stepErrors.phone = 'Phone is required';
        if (stepData.email && !/\S+@\S+\.\S+/.test(stepData.email)) {
          stepErrors.email = 'Email is invalid';
        }
        break;
        
      case 'preferences':
        if (!stepData.communication) {
          stepErrors.communication = 'Please select communication preference';
        }
        break;
    }
    
    setErrors(prev => ({ ...prev, [stepKey]: stepErrors }));
    return Object.keys(stepErrors).length === 0;
  }, [formData]);
  
  const nextStep = useCallback(() => {
    if (validateStep(currentStepKey)) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
    }
  }, [currentStepKey, validateStep, steps.length]);
  
  const prevStep = useCallback(() => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }, []);
  
  const goToStep = useCallback((stepIndex) => {
    setCurrentStep(stepIndex);
  }, []);
  
  const submitForm = useCallback(async () => {
    // Validate all steps
    const allValid = steps.every(step => validateStep(step.key));
    
    if (!allValid) {
      // Go to first invalid step
      const firstInvalidStep = steps.findIndex(step => 
        Object.keys(errors[step.key] || {}).length > 0
      );
      setCurrentStep(firstInvalidStep);
      return false;
    }
    
    try {
      const response = await fetch('/api/submit-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        // Reset form
        setFormData({
          personal: {},
          contact: {},
          preferences: {},
          review: {}
        });
        setCurrentStep(0);
        setErrors({});
        return true;
      }
    } catch (error) {
      console.error('Form submission error:', error);
    }
    
    return false;
  }, [formData, errors, steps, validateStep]);
  
  const value = {
    currentStep,
    currentStepKey,
    steps,
    formData,
    errors,
    touched,
    updateStepData,
    validateStep,
    nextStep,
    prevStep,
    goToStep,
    submitForm,
    setTouched,
    isFirstStep: currentStep === 0,
    isLastStep: currentStep === steps.length - 1,
    completedSteps: currentStep,
    totalSteps: steps.length
  };
  
  return (
    <FormContext.Provider value={value}>
      {children}
    </FormContext.Provider>
  );
}

export function useMultiStepForm() {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useMultiStepForm must be used within MultiStepFormProvider');
  }
  return context;
}
```

## Common Pitfalls

### 1. Creating New Objects in Render

```jsx
// ❌ Wrong: Creates new object every render
function BadProvider({ children }) {
  const [user, setUser] = useState(null);
  
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

// ✅ Correct: Memoize the value
function GoodProvider({ children }) {
  const [user, setUser] = useState(null);
  
  const value = useMemo(() => ({ user, setUser }), [user]);
  
  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}
```

### 2. Not Handling Context Errors

```jsx
// ❌ Wrong: No error handling
function useAuth() {
  return useContext(AuthContext);
}

// ✅ Correct: Proper error handling
function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

### 3. Overusing Context

```jsx
// ❌ Wrong: Everything in one context
const AppContext = createContext();

function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [cart, setCart] = useState([]);
  const [notifications, setNotifications] = useState([]);
  // ... many more states
  
  // This will cause unnecessary re-renders
  return (
    <AppContext.Provider value={{ 
      user, setUser, 
      theme, setTheme, 
      cart, setCart,
      notifications, setNotifications
    }}>
      {children}
    </AppContext.Provider>
  );
}

// ✅ Correct: Separate contexts by concern
function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <CartProvider>
          <NotificationProvider>
            <AppContent />
          </NotificationProvider>
        </CartProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}
```

## Best Practices

### 1. Context Organization

- **Separate by domain**: Create separate contexts for different app concerns
- **Limit context size**: Keep contexts focused and small
- **Use composition**: Combine multiple small contexts rather than one large one

### 2. Performance Guidelines

- **Memoize context values**: Always memoize objects passed to providers
- **Split frequent updates**: Separate frequently changing data from stable data
- **Use selectors**: Implement selector pattern for complex state

### 3. Error Handling

- **Validate context usage**: Always check if context is used within provider
- **Provide meaningful errors**: Give clear error messages
- **Use error boundaries**: Wrap providers with error boundaries

### 4. Testing Strategy

- **Test in isolation**: Test context logic separately from components
- **Mock providers**: Create mock providers for testing
- **Integration tests**: Test full provider chains

### 5. TypeScript Integration

- **Strong typing**: Use TypeScript for better developer experience
- **Generic factories**: Create reusable typed context factories
- **Discriminated unions**: Use for complex state types

### 6. Development Tools

```jsx
{% raw %}
{% raw %}
// Development-only context debugging
function ContextDevTools({ children, name, value }) {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`${name} Context Updated:`, value);
    }
  }, [name, value]);
  
  return children;
}

// Usage
function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  
  return (
    <AuthContext.Provider value={state}>
      <ContextDevTools name="Auth" value={state}>
        {children}
      </ContextDevTools>
    </AuthContext.Provider>
  );
}
{% endraw %}
{% endraw %}
```

The Context API is a powerful tool for state management in React applications. When used correctly with proper optimization techniques and patterns, it can handle complex state requirements while maintaining good performance. Remember to balance between simplicity and performance, and always consider whether Context is the right solution for your specific use case.
