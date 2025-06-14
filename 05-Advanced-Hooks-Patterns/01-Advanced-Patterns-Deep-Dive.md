# Advanced Hooks Patterns Deep Dive

## Table of Contents
1. [Hook Libraries and Utilities](#hook-libraries-and-utilities)
2. [Performance-Optimized Hooks](#performance-optimized-hooks)
3. [Complex State Management Patterns](#complex-state-management-patterns)
4. [Advanced Component Patterns](#advanced-component-patterns)
5. [Testing Advanced Hooks](#testing-advanced-hooks)
6. [Real-World Applications](#real-world-applications)

## Hook Libraries and Utilities

### 1. Building a Custom Hook Library

#### Core Utility Hooks
```jsx
{% raw %}
{% raw %}
// hooks/useToggle.js - Simple boolean state management
export function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => setValue(prev => !prev), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);
  
  return [value, { toggle, setTrue, setFalse }];
}

// hooks/useCounter.js - Counter with bounds and step
export function useCounter(initialValue = 0, { min, max, step = 1 } = {}) {
  const [count, setCount] = useState(initialValue);
  
  const increment = useCallback(() => {
    setCount(prev => {
      const newValue = prev + step;
      return max !== undefined ? Math.min(newValue, max) : newValue;
    });
  }, [step, max]);
  
  const decrement = useCallback(() => {
    setCount(prev => {
      const newValue = prev - step;
      return min !== undefined ? Math.max(newValue, min) : newValue;
    });
  }, [step, min]);
  
  const reset = useCallback(() => setCount(initialValue), [initialValue]);
  
  const set = useCallback((value) => {
    setCount(prev => {
      if (min !== undefined && value < min) return min;
      if (max !== undefined && value > max) return max;
      return value;
    });
  }, [min, max]);
  
  return {
    count,
    increment,
    decrement,
    reset,
    set,
    isAtMin: min !== undefined && count <= min,
    isAtMax: max !== undefined && count >= max
  };
}

// hooks/useLocalStorage.js - Persistent state
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });
  
  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);
  
  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);
  
  return [storedValue, setValue, removeValue];
}
{% endraw %}
{% endraw %}
```

#### Advanced Data Fetching Hooks
```jsx
{% raw %}
{% raw %}
// hooks/useAsync.js - Generic async operation handler
export function useAsync(asyncFunction, dependencies = []) {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  });
  
  const execute = useCallback(async (...args) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await asyncFunction(...args);
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      setState({ data: null, loading: false, error });
      throw error;
    }
  }, dependencies);
  
  return { ...state, execute };
}

// hooks/useApi.js - RESTful API operations
export function useApi(url, options = {}) {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  });
  
  const { method = 'GET', headers = {}, ...restOptions } = options;
  
  const request = useCallback(async (overrides = {}) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers,
          ...overrides.headers
        },
        ...restOptions,
        ...overrides
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      setState({ data: null, loading: false, error });
      throw error;
    }
  }, [url, method, headers, restOptions]);
  
  // Auto-fetch on mount for GET requests
  useEffect(() => {
    if (method === 'GET' && options.autoFetch !== false) {
      request();
    }
  }, [request, method, options.autoFetch]);
  
  return { ...state, request, refetch: request };
}
{% endraw %}
{% endraw %}
```

## Performance-Optimized Hooks

### 1. Memoization Patterns
```jsx
// hooks/useDeepMemo.js - Deep comparison memoization
import { isEqual } from 'lodash';

export function useDeepMemo(factory, deps) {
  const ref = useRef();
  
  if (!ref.current || !isEqual(ref.current.deps, deps)) {
    ref.current = {
      deps,
      value: factory()
    };
  }
  
  return ref.current.value;
}

// hooks/useStableMemo.js - Stable reference with deep comparison
export function useStableMemo(value) {
  const ref = useRef(value);
  
  if (!isEqual(ref.current, value)) {
    ref.current = value;
  }
  
  return ref.current;
}
```

### 2. Optimized Event Handlers
```jsx
// hooks/useEventCallback.js - Stable event handlers
export function useEventCallback(callback) {
  const ref = useRef();
  
  useLayoutEffect(() => {
    ref.current = callback;
  });
  
  return useCallback((...args) => ref.current?.(...args), []);
}

// hooks/useThrottledCallback.js - Throttled callbacks
export function useThrottledCallback(callback, delay) {
  const lastCall = useRef(0);
  const timeoutRef = useRef();
  
  return useCallback((...args) => {
    const now = Date.now();
    
    if (now - lastCall.current >= delay) {
      lastCall.current = now;
      return callback(...args);
    } else {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        lastCall.current = Date.now();
        callback(...args);
      }, delay - (now - lastCall.current));
    }
  }, [callback, delay]);
}
```

## Complex State Management Patterns

### 1. Reducer-Based Patterns
```jsx
// hooks/useAsyncReducer.js - Async actions with reducer
export function useAsyncReducer(reducer, initialState) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [asyncActions, setAsyncActions] = useState(new Set());
  
  const asyncDispatch = useCallback(async (action) => {
    if (typeof action === 'function') {
      const actionId = Symbol('asyncAction');
      setAsyncActions(prev => new Set(prev).add(actionId));
      
      try {
        const result = await action(dispatch, state);
        return result;
      } finally {
        setAsyncActions(prev => {
          const newSet = new Set(prev);
          newSet.delete(actionId);
          return newSet;
        });
      }
    } else {
      return dispatch(action);
    }
  }, [dispatch, state]);
  
  return [
    { ...state, isLoading: asyncActions.size > 0 },
    asyncDispatch
  ];
}

// hooks/useUndoRedo.js - Undo/Redo functionality
export function useUndoRedo(initialState) {
  const [history, setHistory] = useState([initialState]);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const currentState = history[currentIndex];
  const canUndo = currentIndex > 0;
  const canRedo = currentIndex < history.length - 1;
  
  const setState = useCallback((newState) => {
    setHistory(prev => {
      const newHistory = prev.slice(0, currentIndex + 1);
      return [...newHistory, newState];
    });
    setCurrentIndex(prev => prev + 1);
  }, [currentIndex]);
  
  const undo = useCallback(() => {
    if (canUndo) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [canUndo]);
  
  const redo = useCallback(() => {
    if (canRedo) {
      setCurrentIndex(prev => prev + 1);
    }
  }, [canRedo]);
  
  const reset = useCallback(() => {
    setHistory([initialState]);
    setCurrentIndex(0);
  }, [initialState]);
  
  return {
    state: currentState,
    setState,
    undo,
    redo,
    reset,
    canUndo,
    canRedo,
    history: history.length
  };
}
```

### 2. Form Management Patterns
```jsx
// hooks/useForm.js - Comprehensive form management
export function useForm(initialValues = {}, validationSchema = {}) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const validateField = useCallback((name, value) => {
    const validator = validationSchema[name];
    if (!validator) return null;
    
    try {
      validator(value);
      return null;
    } catch (error) {
      return error.message;
    }
  }, [validationSchema]);
  
  const setFieldValue = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Validate if field has been touched
    if (touched[name]) {
      const error = validateField(name, value);
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  }, [touched, validateField]);
  
  const setFieldTouched = useCallback((name, isTouched = true) => {
    setTouched(prev => ({ ...prev, [name]: isTouched }));
    
    if (isTouched) {
      const error = validateField(name, values[name]);
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  }, [validateField, values]);
  
  const validateForm = useCallback(() => {
    const newErrors = {};
    let isValid = true;
    
    Object.keys(validationSchema).forEach(name => {
      const error = validateField(name, values[name]);
      if (error) {
        newErrors[name] = error;
        isValid = false;
      }
    });
    
    setErrors(newErrors);
    setTouched(
      Object.keys(validationSchema).reduce(
        (acc, name) => ({ ...acc, [name]: true }),
        {}
      )
    );
    
    return isValid;
  }, [validationSchema, validateField, values]);
  
  const handleSubmit = useCallback((onSubmit) => async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    
    try {
      const isValid = validateForm();
      if (isValid) {
        await onSubmit(values);
      }
    } finally {
      setIsSubmitting(false);
    }
  }, [validateForm, values]);
  
  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);
  
  return {
    values,
    errors,
    touched,
    isSubmitting,
    setFieldValue,
    setFieldTouched,
    handleSubmit,
    reset,
    isValid: Object.keys(errors).length === 0
  };
}
```

## Advanced Component Patterns

### 1. Render Props with Hooks
```jsx
// hooks/useRenderProps.js - Render props pattern with hooks
export function useRenderProps(children, props) {
  return useMemo(() => {
    if (typeof children === 'function') {
      return children(props);
    }
    return children;
  }, [children, props]);
}

// Example: Mouse tracker component
function MouseTracker({ children }) {
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  
  useEffect(() => {
    function handleMouseMove(event) {
      setMouse({ x: event.clientX, y: event.clientY });
    }
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);
  
  return useRenderProps(children, mouse);
}
```

### 2. Higher-Order Component Hooks
```jsx
// hooks/useHOC.js - HOC pattern with hooks
export function withLoading(Component) {
  return function WrappedComponent(props) {
    const [loading, setLoading] = useState(false);
    
    const withLoadingProps = {
      ...props,
      setLoading,
      loading
    };
    
    if (loading) {
      return <div>Loading...</div>;
    }
    
    return <Component {...withLoadingProps} />;
  };
}

// Better approach: Custom hook instead of HOC
export function useLoading(initialState = false) {
  const [loading, setLoading] = useState(initialState);
  
  const withLoading = useCallback(async (asyncFn) => {
    setLoading(true);
    try {
      const result = await asyncFn();
      return result;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return { loading, setLoading, withLoading };
}
```

## Testing Advanced Hooks

### 1. Testing Custom Hooks
```jsx
// __tests__/useCounter.test.js
import { renderHook, act } from '@testing-library/react';
import { useCounter } from '../hooks/useCounter';

describe('useCounter', () => {
  it('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });
  
  it('should initialize with custom value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });
  
  it('should increment count', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
  
  it('should respect max boundary', () => {
    const { result } = renderHook(() => useCounter(5, { max: 5 }));
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(5);
    expect(result.current.isAtMax).toBe(true);
  });
});
```

### 2. Testing Hooks with Context
```jsx
// __tests__/useAuth.test.js
import React from 'react';
import { renderHook } from '@testing-library/react';
import { AuthProvider, useAuth } from '../hooks/useAuth';

const wrapper = ({ children }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('useAuth', () => {
  it('should provide auth context', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(typeof result.current.login).toBe('function');
    expect(typeof result.current.logout).toBe('function');
  });
});
```

## Real-World Applications

### 1. E-commerce Cart Hook
```jsx
// hooks/useShoppingCart.js
export function useShoppingCart() {
  const [items, setItems] = useLocalStorage('cart-items', []);
  
  const addItem = useCallback((product, quantity = 1) => {
    setItems(prev => {
      const existingItem = prev.find(item => item.id === product.id);
      
      if (existingItem) {
        return prev.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }
      
      return [...prev, { ...product, quantity }];
    });
  }, [setItems]);
  
  const removeItem = useCallback((productId) => {
    setItems(prev => prev.filter(item => item.id !== productId));
  }, [setItems]);
  
  const updateQuantity = useCallback((productId, quantity) => {
    if (quantity <= 0) {
      removeItem(productId);
      return;
    }
    
    setItems(prev =>
      prev.map(item =>
        item.id === productId ? { ...item, quantity } : item
      )
    );
  }, [setItems, removeItem]);
  
  const clearCart = useCallback(() => {
    setItems([]);
  }, [setItems]);
  
  const totals = useMemo(() => {
    const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const tax = subtotal * 0.1; // 10% tax
    const total = subtotal + tax;
    
    return { subtotal, tax, total, itemCount: items.length };
  }, [items]);
  
  return {
    items,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    ...totals
  };
}
```

### 2. Real-time Chat Hook
```jsx
{% raw %}
{% raw %}
// hooks/useChatRoom.js
export function useChatRoom(roomId) {
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState([]);
  const [connectionState, setConnectionState] = useState('disconnected');
  const ws = useRef(null);
  
  useEffect(() => {
    if (!roomId) return;
    
    ws.current = new WebSocket(`ws://localhost:8080/chat/${roomId}`);
    
    ws.current.onopen = () => {
      setConnectionState('connected');
    };
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'message':
          setMessages(prev => [...prev, data.payload]);
          break;
        case 'typing':
          setTyping(prev => {
            if (data.payload.isTyping) {
              return [...prev.filter(u => u !== data.payload.user), data.payload.user];
            } else {
              return prev.filter(u => u !== data.payload.user);
            }
          });
          break;
      }
    };
    
    ws.current.onclose = () => {
      setConnectionState('disconnected');
    };
    
    return () => {
      ws.current?.close();
    };
  }, [roomId]);
  
  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'message',
        payload: { message, timestamp: Date.now() }
      }));
    }
  }, []);
  
  const sendTyping = useCallback((isTyping) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'typing',
        payload: { isTyping }
      }));
    }
  }, []);
  
  return {
    messages,
    typing,
    connectionState,
    sendMessage,
    sendTyping,
    isConnected: connectionState === 'connected'
  };
}
{% endraw %}
{% endraw %}
```

## Best Practices and Performance Tips

### 1. Hook Optimization Checklist
- ✅ Use `useCallback` for functions passed as dependencies
- ✅ Use `useMemo` for expensive calculations
- ✅ Avoid creating objects/arrays in render
- ✅ Use refs for mutable values that don't cause re-renders
- ✅ Split complex state into multiple pieces
- ✅ Consider using reducers for complex state logic

### 2. Common Pitfalls to Avoid
- ❌ Creating functions inside render without `useCallback`
- ❌ Not memoizing expensive computations
- ❌ Using hooks inside loops or conditions
- ❌ Forgetting to cleanup side effects
- ❌ Over-optimizing with unnecessary memoization

### 3. Testing Strategy
- Unit test individual hooks in isolation
- Integration test hooks with components
- Test error scenarios and edge cases
- Mock external dependencies (APIs, localStorage, etc.)
- Use React Testing Library for realistic testing

---

This deep dive covers advanced patterns that are essential for building scalable React applications. Practice these patterns and gradually introduce them into your projects to become proficient with advanced React development.
