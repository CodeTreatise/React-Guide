# Custom Hooks Patterns

## Table of Contents
1. [Introduction to Custom Hooks](#introduction-to-custom-hooks)
2. [Creating Your First Custom Hook](#creating-your-first-custom-hook)
3. [Common Custom Hook Patterns](#common-custom-hook-patterns)
4. [State Management Hooks](#state-management-hooks)
5. [Side Effect Hooks](#side-effect-hooks)
6. [Data Fetching Hooks](#data-fetching-hooks)
7. [Performance Optimization Hooks](#performance-optimization-hooks)
8. [Form Handling Hooks](#form-handling-hooks)
9. [Event Handling Hooks](#event-handling-hooks)
10. [Storage Hooks](#storage-hooks)
11. [Animation and Timing Hooks](#animation-and-timing-hooks)
12. [Testing Custom Hooks](#testing-custom-hooks)
13. [Best Practices and Guidelines](#best-practices-and-guidelines)

---

## Introduction to Custom Hooks

Custom hooks are JavaScript functions that start with "use" and can call other hooks. They allow you to extract component logic into reusable functions, promoting code reuse and separation of concerns.

### Why Custom Hooks?

```javascript
// Before: Logic scattered across components
function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/user');
      const userData = await response.json();
      setUser(userData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return <div>Welcome, {user?.name}</div>;
}

function UserSettings() {
  // Same logic repeated...
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUser();
  }, []);

  // ... duplicate code
}

// After: Logic extracted to custom hook
function useUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/user');
      const userData = await response.json();
      setUser(userData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { user, loading, error, refetch: fetchUser };
}

// Clean components
function UserProfile() {
  const { user, loading, error } = useUser();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return <div>Welcome, {user?.name}</div>;
}

function UserSettings() {
  const { user, loading, error } = useUser();
  // Clean, reusable logic
}
```

### Benefits of Custom Hooks

1. **Code Reusability**: Share stateful logic between components
2. **Separation of Concerns**: Keep UI logic separate from business logic
3. **Testability**: Test logic independently from components
4. **Readability**: Make component code cleaner and more focused
5. **Maintainability**: Change logic in one place

---

## Creating Your First Custom Hook

### Basic Structure

```javascript
// Custom hook naming convention: start with "use"
function useCustomHook(initialValue) {
  // Can use other hooks
  const [state, setState] = useState(initialValue);
  
  // Can contain logic
  const handleSomething = useCallback(() => {
    setState(prevState => !prevState);
  }, []);

  // Must return something (usually an object or array)
  return {
    state,
    handleSomething
  };
}

// Usage in component
function MyComponent() {
  const { state, handleSomething } = useCustomHook(false);
  
  return (
    <button onClick={handleSomething}>
      {state ? 'ON' : 'OFF'}
    </button>
  );
}
```

### Rules of Custom Hooks

```javascript
// ✅ CORRECT: Follows all hook rules
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  
  const increment = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);
  
  const decrement = useCallback(() => {
    setCount(prev => prev - 1);
  }, []);
  
  const reset = useCallback(() => {
    setCount(initialValue);
  }, [initialValue]);
  
  return {
    count,
    increment,
    decrement,
    reset
  };
}

// ❌ WRONG: Conditional hook usage
function useBadHook(condition) {
  if (condition) {
    const [state, setState] = useState(0); // ❌ Conditional hook
  }
  
  return state;
}

// ❌ WRONG: Hook in regular function
function regularFunction() {
  const [state, setState] = useState(0); // ❌ Hook outside component/custom hook
  return state;
}

// ❌ WRONG: Hook in callback
function useAnotherBadHook() {
  const handleClick = () => {
    const [state, setState] = useState(0); // ❌ Hook in callback
  };
  
  return handleClick;
}
```

---

## Common Custom Hook Patterns

### 1. Toggle Hook

```javascript
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);
  
  const setTrue = useCallback(() => {
    setValue(true);
  }, []);
  
  const setFalse = useCallback(() => {
    setValue(false);
  }, []);
  
  return {
    value,
    toggle,
    setTrue,
    setFalse,
    setValue
  };
}

// Usage
function Modal() {
  const { value: isOpen, toggle, setFalse } = useToggle();
  
  return (
    <div>
      <button onClick={toggle}>Toggle Modal</button>
      {isOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Modal Content</h2>
            <button onClick={setFalse}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 2. Counter Hook

```javascript
function useCounter(initialValue = 0, step = 1) {
  const [count, setCount] = useState(initialValue);
  
  const increment = useCallback(() => {
    setCount(prev => prev + step);
  }, [step]);
  
  const decrement = useCallback(() => {
    setCount(prev => prev - step);
  }, [step]);
  
  const reset = useCallback(() => {
    setCount(initialValue);
  }, [initialValue]);
  
  const setValue = useCallback((value) => {
    setCount(typeof value === 'function' ? value : value);
  }, []);
  
  return {
    count,
    increment,
    decrement,
    reset,
    setValue
  };
}

// Advanced counter with constraints
function useBoundedCounter(initialValue = 0, min = 0, max = 100) {
  const [count, setCount] = useState(
    Math.max(min, Math.min(max, initialValue))
  );
  
  const increment = useCallback(() => {
    setCount(prev => Math.min(max, prev + 1));
  }, [max]);
  
  const decrement = useCallback(() => {
    setCount(prev => Math.max(min, prev - 1));
  }, [min]);
  
  const setValue = useCallback((value) => {
    const newValue = typeof value === 'function' ? value(count) : value;
    setCount(Math.max(min, Math.min(max, newValue)));
  }, [min, max, count]);
  
  const isAtMin = count === min;
  const isAtMax = count === max;
  
  return {
    count,
    increment,
    decrement,
    setValue,
    isAtMin,
    isAtMax,
    min,
    max
  };
}
```

### 3. Array Hook

```javascript
function useArray(initialArray = []) {
  const [array, setArray] = useState(initialArray);
  
  const push = useCallback((element) => {
    setArray(prev => [...prev, element]);
  }, []);
  
  const remove = useCallback((index) => {
    setArray(prev => prev.filter((_, i) => i !== index));
  }, []);
  
  const removeById = useCallback((id) => {
    setArray(prev => prev.filter(item => item.id !== id));
  }, []);
  
  const update = useCallback((index, newElement) => {
    setArray(prev => prev.map((item, i) => i === index ? newElement : item));
  }, []);
  
  const clear = useCallback(() => {
    setArray([]);
  }, []);
  
  const insert = useCallback((index, element) => {
    setArray(prev => [
      ...prev.slice(0, index),
      element,
      ...prev.slice(index)
    ]);
  }, []);
  
  const move = useCallback((fromIndex, toIndex) => {
    setArray(prev => {
      const newArray = [...prev];
      const element = newArray.splice(fromIndex, 1)[0];
      newArray.splice(toIndex, 0, element);
      return newArray;
    });
  }, []);
  
  return {
    array,
    set: setArray,
    push,
    remove,
    removeById,
    update,
    clear,
    insert,
    move,
    isEmpty: array.length === 0,
    length: array.length
  };
}

// Usage example
function TodoList() {
  const { 
    array: todos, 
    push: addTodo, 
    removeById, 
    update 
  } = useArray([]);
  
  const [newTodo, setNewTodo] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (newTodo.trim()) {
      addTodo({
        id: Date.now(),
        text: newTodo,
        completed: false
      });
      setNewTodo('');
    }
  };
  
  const toggleTodo = (index, todo) => {
    update(index, { ...todo, completed: !todo.completed });
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          placeholder="Add todo..."
        />
        <button type="submit">Add</button>
      </form>
      
      <ul>
        {todos.map((todo, index) => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(index, todo)}
            />
            <span 
              style={{ 
                textDecoration: todo.completed ? 'line-through' : 'none' 
              }}
            >
              {todo.text}
            </span>
            <button onClick={() => removeById(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## State Management Hooks

### Previous State Hook

```javascript
function usePrevious(value) {
  const ref = useRef();
  
  useEffect(() => {
    ref.current = value;
  });
  
  return ref.current;
}

// Usage
function Counter() {
  const [count, setCount] = useState(0);
  const prevCount = usePrevious(count);
  
  return (
    <div>
      <p>Current: {count}</p>
      <p>Previous: {prevCount}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

### State History Hook

```javascript
function useStateHistory(initialState, capacity = 10) {
  const [state, setState] = useState(initialState);
  const [history, setHistory] = useState([initialState]);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const set = useCallback((newState) => {
    const newValue = typeof newState === 'function' 
      ? newState(state) 
      : newState;
    
    // Remove future history if we're not at the end
    const newHistory = history.slice(0, currentIndex + 1);
    
    // Add new state
    newHistory.push(newValue);
    
    // Limit capacity
    if (newHistory.length > capacity) {
      newHistory.shift();
    } else {
      setCurrentIndex(prev => prev + 1);
    }
    
    setHistory(newHistory);
    setState(newValue);
  }, [state, history, currentIndex, capacity]);
  
  const undo = useCallback(() => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      setCurrentIndex(newIndex);
      setState(history[newIndex]);
    }
  }, [currentIndex, history]);
  
  const redo = useCallback(() => {
    if (currentIndex < history.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      setState(history[newIndex]);
    }
  }, [currentIndex, history]);
  
  const reset = useCallback(() => {
    setState(initialState);
    setHistory([initialState]);
    setCurrentIndex(0);
  }, [initialState]);
  
  return {
    state,
    set,
    undo,
    redo,
    reset,
    canUndo: currentIndex > 0,
    canRedo: currentIndex < history.length - 1,
    history: history.slice(),
    currentIndex
  };
}

// Usage
function TextEditor() {
  const {
    state: text,
    set: setText,
    undo,
    redo,
    canUndo,
    canRedo,
    reset
  } = useStateHistory('');
  
  return (
    <div>
      <div>
        <button onClick={undo} disabled={!canUndo}>
          Undo
        </button>
        <button onClick={redo} disabled={!canRedo}>
          Redo
        </button>
        <button onClick={reset}>Reset</button>
      </div>
      
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Start typing..."
        rows={10}
        cols={50}
      />
    </div>
  );
}
```

### Reducer Hook with Actions

```javascript
function useActions(reducer, initialState) {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  const actions = useMemo(() => {
    return {
      dispatch,
      // Helper to create action creators
      createAction: (type) => (payload) => dispatch({ type, payload })
    };
  }, []);
  
  return [state, actions];
}

// Counter with actions
const counterReducer = (state, action) => {
  switch (action.type) {
    case 'INCREMENT':
      return { ...state, count: state.count + (action.payload || 1) };
    case 'DECREMENT':
      return { ...state, count: state.count - (action.payload || 1) };
    case 'RESET':
      return { ...state, count: 0 };
    case 'SET_STEP':
      return { ...state, step: action.payload };
    default:
      return state;
  }
};

function useCounter(initialCount = 0) {
  const [state, { dispatch, createAction }] = useActions(
    counterReducer,
    { count: initialCount, step: 1 }
  );
  
  const actions = useMemo(() => ({
    increment: createAction('INCREMENT'),
    decrement: createAction('DECREMENT'),
    reset: createAction('RESET'),
    setStep: createAction('SET_STEP'),
    incrementBy: (amount) => dispatch({ type: 'INCREMENT', payload: amount }),
    decrementBy: (amount) => dispatch({ type: 'DECREMENT', payload: amount })
  }), [createAction, dispatch]);
  
  return [state, actions];
}
```

---

## Side Effect Hooks

### Debounce Hook

```javascript
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return debouncedValue;
}

// Advanced debounce with callback
function useDebounceCallback(callback, delay, deps = []) {
  const timeoutRef = useRef(null);
  
  const debouncedCallback = useCallback((...args) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]);
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return debouncedCallback;
}

// Usage
function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const debouncedQuery = useDebounce(query, 300);
  
  useEffect(() => {
    if (debouncedQuery) {
      setLoading(true);
      searchAPI(debouncedQuery)
        .then(setResults)
        .finally(() => setLoading(false));
    } else {
      setResults([]);
    }
  }, [debouncedQuery]);
  
  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      {loading && <div>Searching...</div>}
      <ul>
        {results.map(result => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Throttle Hook

```javascript
function useThrottle(value, delay) {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastExecuted = useRef(Date.now());
  
  useEffect(() => {
    const handler = setTimeout(() => {
      const now = Date.now();
      if (now >= lastExecuted.current + delay) {
        setThrottledValue(value);
        lastExecuted.current = now;
      }
    }, delay - (Date.now() - lastExecuted.current));
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return throttledValue;
}

function useThrottleCallback(callback, delay, deps = []) {
  const lastRan = useRef(Date.now());
  
  const throttledCallback = useCallback((...args) => {
    const now = Date.now();
    
    if (now - lastRan.current >= delay) {
      callback(...args);
      lastRan.current = now;
    }
  }, [callback, delay, ...deps]);
  
  return throttledCallback;
}

// Usage
function ScrollTracker() {
  const [scrollY, setScrollY] = useState(0);
  
  const throttledHandleScroll = useThrottleCallback(() => {
    setScrollY(window.scrollY);
  }, 100);
  
  useEffect(() => {
    window.addEventListener('scroll', throttledHandleScroll);
    return () => {
      window.removeEventListener('scroll', throttledHandleScroll);
    };
  }, [throttledHandleScroll]);
  
  return (
    <div style={{ position: 'fixed', top: 10, right: 10 }}>
      Scroll Y: {scrollY}px
    </div>
  );
}
```

### Interval Hook

```javascript
function useInterval(callback, delay, immediate = false) {
  const savedCallback = useRef(callback);
  
  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  // Set up the interval
  useEffect(() => {
    if (delay === null) return;
    
    if (immediate) {
      savedCallback.current();
    }
    
    const id = setInterval(() => {
      savedCallback.current();
    }, delay);
    
    return () => clearInterval(id);
  }, [delay, immediate]);
}

// Advanced interval with controls
function useControllableInterval(callback, delay) {
  const [isRunning, setIsRunning] = useState(false);
  const savedCallback = useRef(callback);
  const intervalId = useRef(null);
  
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  const start = useCallback(() => {
    if (!isRunning && delay !== null) {
      setIsRunning(true);
      intervalId.current = setInterval(() => {
        savedCallback.current();
      }, delay);
    }
  }, [delay, isRunning]);
  
  const stop = useCallback(() => {
    if (isRunning) {
      setIsRunning(false);
      if (intervalId.current) {
        clearInterval(intervalId.current);
        intervalId.current = null;
      }
    }
  }, [isRunning]);
  
  const toggle = useCallback(() => {
    if (isRunning) {
      stop();
    } else {
      start();
    }
  }, [isRunning, start, stop]);
  
  useEffect(() => {
    return () => {
      if (intervalId.current) {
        clearInterval(intervalId.current);
      }
    };
  }, []);
  
  return {
    isRunning,
    start,
    stop,
    toggle
  };
}

// Usage
function Timer() {
  const [time, setTime] = useState(0);
  
  const {
    isRunning,
    start,
    stop,
    toggle
  } = useControllableInterval(() => {
    setTime(prev => prev + 1);
  }, 1000);
  
  const reset = () => {
    setTime(0);
    stop();
  };
  
  return (
    <div>
      <h2>{time} seconds</h2>
      <button onClick={toggle}>
        {isRunning ? 'Pause' : 'Start'}
      </button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

---

## Data Fetching Hooks

### Basic Fetch Hook

```javascript
{% raw %}
{% raw %}
function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [url, JSON.stringify(options)]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

// Advanced fetch hook with caching
function useAdvancedFetch(url, options = {}) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null
  });
  
  const cache = useRef(new Map());
  const abortController = useRef(null);
  
  const fetchData = useCallback(async (bypassCache = false) => {
    const cacheKey = `${url}${JSON.stringify(options)}`;
    
    // Check cache first
    if (!bypassCache && cache.current.has(cacheKey)) {
      setState({
        data: cache.current.get(cacheKey),
        loading: false,
        error: null
      });
      return;
    }
    
    // Cancel previous request
    if (abortController.current) {
      abortController.current.abort();
    }
    
    abortController.current = new AbortController();
    
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await fetch(url, {
        ...options,
        signal: abortController.current.signal
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Cache the result
      cache.current.set(cacheKey, result);
      
      setState({
        data: result,
        loading: false,
        error: null
      });
    } catch (err) {
      if (err.name !== 'AbortError') {
        setState(prev => ({
          ...prev,
          loading: false,
          error: err.message
        }));
      }
    }
  }, [url, JSON.stringify(options)]);
  
  useEffect(() => {
    fetchData();
    
    return () => {
      if (abortController.current) {
        abortController.current.abort();
      }
    };
  }, [fetchData]);
  
  const invalidateCache = useCallback(() => {
    cache.current.clear();
  }, []);
  
  return {
    ...state,
    refetch: () => fetchData(true),
    invalidateCache
  };
}
{% endraw %}
{% endraw %}
```

### Mutation Hook

```javascript
function useMutation(mutationFn, options = {}) {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  });
  
  const mutate = useCallback(async (...args) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      if (options.onMutate) {
        await options.onMutate(...args);
      }
      
      const result = await mutationFn(...args);
      
      setState({
        data: result,
        loading: false,
        error: null
      });
      
      if (options.onSuccess) {
        options.onSuccess(result, ...args);
      }
      
      return result;
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.message
      }));
      
      if (options.onError) {
        options.onError(error, ...args);
      }
      
      throw error;
    }
  }, [mutationFn, options]);
  
  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null
    });
  }, []);
  
  return {
    ...state,
    mutate,
    reset
  };
}

// Usage
function CreateUserForm() {
  const createUser = useMutation(
    async (userData) => {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      return response.json();
    },
    {
      onSuccess: (newUser) => {
        console.log('User created:', newUser);
        // Invalidate user list cache, redirect, etc.
      },
      onError: (error) => {
        console.error('Failed to create user:', error);
      }
    }
  );
  
  const handleSubmit = async (formData) => {
    try {
      await createUser.mutate(formData);
    } catch (error) {
      // Error already handled in onError
    }
  };
  
  return (
    <div>
      {/* Form JSX */}
      {createUser.loading && <div>Creating user...</div>}
      {createUser.error && <div>Error: {createUser.error}</div>}
    </div>
  );
}
```

---

## Performance Optimization Hooks

### Memoization Hook

```javascript
function useMemoizedValue(factory, deps) {
  const memoizedValue = useMemo(factory, deps);
  return memoizedValue;
}

// Deep comparison memo
function useDeepMemo(factory, deps) {
  const ref = useRef();
  
  if (!ref.current || !deepEqual(deps, ref.current.deps)) {
    ref.current = {
      deps,
      value: factory()
    };
  }
  
  return ref.current.value;
}

// Deep equal implementation
function deepEqual(a, b) {
  if (a === b) return true;
  
  if (a == null || b == null) return false;
  
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    return a.every((item, index) => deepEqual(item, b[index]));
  }
  
  if (typeof a === 'object' && typeof b === 'object') {
    const keysA = Object.keys(a);
    const keysB = Object.keys(b);
    
    if (keysA.length !== keysB.length) return false;
    
    return keysA.every(key => deepEqual(a[key], b[key]));
  }
  
  return false;
}
```

### Virtualization Hook

```javascript
{% raw %}
{% raw %}
function useVirtualization({ 
  items, 
  itemHeight, 
  containerHeight, 
  overscan = 5 
}) {
  const [scrollTop, setScrollTop] = useState(0);
  
  const startIndex = Math.max(
    0, 
    Math.floor(scrollTop / itemHeight) - overscan
  );
  
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );
  
  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      ...item,
      index: startIndex + index
    }));
  }, [items, startIndex, endIndex]);
  
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;
  
  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  };
}

// Usage
function VirtualizedList({ items }) {
  const ITEM_HEIGHT = 50;
  const CONTAINER_HEIGHT = 400;
  
  const {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  } = useVirtualization({
    items,
    itemHeight: ITEM_HEIGHT,
    containerHeight: CONTAINER_HEIGHT
  });
  
  return (
    <div
      style={{ height: CONTAINER_HEIGHT, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map(item => (
            <div
              key={item.id}
              style={{ height: ITEM_HEIGHT }}
            >
              {item.name}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

---

## Form Handling Hooks

### Form Hook

```javascript
function useForm(initialValues = {}, validationSchema = {}) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const setValue = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  }, [errors]);
  
  const setFieldTouched = useCallback((name, isTouched = true) => {
    setTouched(prev => ({ ...prev, [name]: isTouched }));
  }, []);
  
  const validate = useCallback((valuesToValidate = values) => {
    const newErrors = {};
    
    Object.keys(validationSchema).forEach(field => {
      const validator = validationSchema[field];
      const value = valuesToValidate[field];
      
      if (typeof validator === 'function') {
        const error = validator(value, valuesToValidate);
        if (error) {
          newErrors[field] = error;
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [values, validationSchema]);
  
  const handleSubmit = useCallback((onSubmit) => {
    return async (e) => {
      if (e) {
        e.preventDefault();
      }
      
      setIsSubmitting(true);
      
      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce((acc, key) => {
        acc[key] = true;
        return acc;
      }, {});
      setTouched(allTouched);
      
      // Validate
      const isValid = validate();
      
      if (isValid) {
        try {
          await onSubmit(values);
        } catch (error) {
          console.error('Form submission error:', error);
        }
      }
      
      setIsSubmitting(false);
    };
  }, [values, validate]);
  
  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);
  
  const getFieldProps = useCallback((name) => ({
    name,
    value: values[name] || '',
    onChange: (e) => setValue(name, e.target.value),
    onBlur: () => setFieldTouched(name, true)
  }), [values, setValue, setFieldTouched]);
  
  const getFieldError = useCallback((name) => {
    return touched[name] && errors[name];
  }, [touched, errors]);
  
  const isValid = Object.keys(errors).length === 0;
  const isDirty = !deepEqual(values, initialValues);
  
  return {
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    isDirty,
    setValue,
    setFieldTouched,
    validate,
    handleSubmit,
    reset,
    getFieldProps,
    getFieldError
  };
}

// Usage
function LoginForm() {
  const form = useForm(
    { email: '', password: '' },
    {
      email: (value) => {
        if (!value) return 'Email is required';
        if (!/\S+@\S+\.\S+/.test(value)) return 'Email is invalid';
        return null;
      },
      password: (value) => {
        if (!value) return 'Password is required';
        if (value.length < 6) return 'Password must be at least 6 characters';
        return null;
      }
    }
  );
  
  const onSubmit = async (values) => {
    // Submit logic
    console.log('Submitting:', values);
  };
  
  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <div>
        <label>Email:</label>
        <input
          type="email"
          {...form.getFieldProps('email')}
        />
        {form.getFieldError('email') && (
          <span className="error">{form.getFieldError('email')}</span>
        )}
      </div>
      
      <div>
        <label>Password:</label>
        <input
          type="password"
          {...form.getFieldProps('password')}
        />
        {form.getFieldError('password') && (
          <span className="error">{form.getFieldError('password')}</span>
        )}
      </div>
      
      <button 
        type="submit" 
        disabled={form.isSubmitting || !form.isValid}
      >
        {form.isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

---

## Event Handling Hooks

### Event Listener Hook

```javascript
function useEventListener(eventName, handler, element = window) {
  const savedHandler = useRef();
  
  useEffect(() => {
    savedHandler.current = handler;
  }, [handler]);
  
  useEffect(() => {
    const targetElement = element?.current || element;
    if (!(targetElement && targetElement.addEventListener)) return;
    
    const eventListener = (event) => savedHandler.current(event);
    targetElement.addEventListener(eventName, eventListener);
    
    return () => {
      targetElement.removeEventListener(eventName, eventListener);
    };
  }, [eventName, element]);
}

// Click outside hook
function useOnClickOutside(ref, handler) {
  useEventListener('mousedown', (event) => {
    if (!ref.current || ref.current.contains(event.target)) return;
    handler(event);
  });
}

// Keyboard shortcut hook
function useKeyboardShortcut(keys, callback, options = {}) {
  const { target = window, preventDefault = true } = options;
  
  useEventListener('keydown', (event) => {
    const pressedKeys = [];
    
    if (event.ctrlKey) pressedKeys.push('ctrl');
    if (event.shiftKey) pressedKeys.push('shift');
    if (event.altKey) pressedKeys.push('alt');
    if (event.metaKey) pressedKeys.push('meta');
    
    const key = event.key.toLowerCase();
    if (!['control', 'shift', 'alt', 'meta'].includes(key)) {
      pressedKeys.push(key);
    }
    
    const shortcut = pressedKeys.join('+');
    const targetShortcut = Array.isArray(keys) ? keys.join('+') : keys;
    
    if (shortcut === targetShortcut) {
      if (preventDefault) {
        event.preventDefault();
      }
      callback(event);
    }
  }, target);
}

// Usage
function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef();
  
  // Close on click outside
  useOnClickOutside(modalRef, onClose);
  
  // Close on Escape key
  useKeyboardShortcut('escape', onClose);
  
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay">
      <div ref={modalRef} className="modal">
        {children}
      </div>
    </div>
  );
}
```

---

## Storage Hooks

### Local Storage Hook

```javascript
{% raw %}
{% raw %}
function useLocalStorage(key, initialValue) {
  // State to store our value
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });
  
  // Return a wrapped version of useState's setter function that persists the new value to localStorage
  const setValue = useCallback((value) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      
      // Save state
      setStoredValue(valueToStore);
      
      // Save to local storage
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);
  
  // Listen for changes in other tabs
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          console.error(`Error parsing localStorage key "${key}":`, error);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);
  
  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);
  
  return [storedValue, setValue, removeValue];
}

// Session Storage Hook
function useSessionStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });
  
  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting sessionStorage key "${key}":`, error);
    }
  }, [key, storedValue]);
  
  const removeValue = useCallback(() => {
    try {
      window.sessionStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing sessionStorage key "${key}":`, error);
    }
  }, [key, initialValue]);
  
  return [storedValue, setValue, removeValue];
}

// Usage
function UserPreferences() {
  const [theme, setTheme, removeTheme] = useLocalStorage('theme', 'light');
  const [language, setLanguage] = useLocalStorage('language', 'en');
  
  return (
    <div>
      <h2>User Preferences</h2>
      
      <div>
        <label>Theme:</label>
        <select value={theme} onChange={(e) => setTheme(e.target.value)}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
        <button onClick={removeTheme}>Reset Theme</button>
      </div>
      
      <div>
        <label>Language:</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
        </select>
      </div>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

---

## Animation and Timing Hooks

### Animation Hook

```javascript
{% raw %}
{% raw %}
function useAnimation(duration, easing = (t) => t) {
  const [progress, setProgress] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const requestRef = useRef();
  const startTimeRef = useRef();
  
  const animate = useCallback((timestamp) => {
    if (!startTimeRef.current) {
      startTimeRef.current = timestamp;
    }
    
    const elapsed = timestamp - startTimeRef.current;
    const rawProgress = Math.min(elapsed / duration, 1);
    const easedProgress = easing(rawProgress);
    
    setProgress(easedProgress);
    
    if (rawProgress < 1) {
      requestRef.current = requestAnimationFrame(animate);
    } else {
      setIsAnimating(false);
      startTimeRef.current = null;
    }
  }, [duration, easing]);
  
  const start = useCallback(() => {
    setIsAnimating(true);
    setProgress(0);
    startTimeRef.current = null;
    requestRef.current = requestAnimationFrame(animate);
  }, [animate]);
  
  const stop = useCallback(() => {
    if (requestRef.current) {
      cancelAnimationFrame(requestRef.current);
    }
    setIsAnimating(false);
    startTimeRef.current = null;
  }, []);
  
  const reset = useCallback(() => {
    stop();
    setProgress(0);
  }, [stop]);
  
  useEffect(() => {
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, []);
  
  return {
    progress,
    isAnimating,
    start,
    stop,
    reset
  };
}

// Easing functions
const easingFunctions = {
  linear: (t) => t,
  easeInQuad: (t) => t * t,
  easeOutQuad: (t) => t * (2 - t),
  easeInOutQuad: (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  easeInCubic: (t) => t * t * t,
  easeOutCubic: (t) => (--t) * t * t + 1,
  easeInOutCubic: (t) => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1
};

// Usage
function AnimatedProgressBar() {
  const { progress, isAnimating, start, stop, reset } = useAnimation(
    2000, // 2 seconds
    easingFunctions.easeInOutQuad
  );
  
  return (
    <div>
      <div 
        style={{
          width: '300px',
          height: '20px',
          background: '#f0f0f0',
          borderRadius: '10px',
          overflow: 'hidden'
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #4CAF50, #8BC34A)',
            transition: 'width 0.1s ease'
          }}
        />
      </div>
      
      <div style={{ marginTop: '10px' }}>
        <button onClick={start} disabled={isAnimating}>
          Start
        </button>
        <button onClick={stop} disabled={!isAnimating}>
          Stop
        </button>
        <button onClick={reset}>Reset</button>
      </div>
      
      <p>Progress: {Math.round(progress * 100)}%</p>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

### Timeout Hook

```javascript
function useTimeout(callback, delay) {
  const savedCallback = useRef(callback);
  
  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  // Set up the timeout
  useEffect(() => {
    if (delay === null) return;
    
    const id = setTimeout(() => savedCallback.current(), delay);
    
    return () => clearTimeout(id);
  }, [delay]);
}

// Controllable timeout
function useControllableTimeout(callback, delay) {
  const [isActive, setIsActive] = useState(false);
  const timeoutId = useRef(null);
  const savedCallback = useRef(callback);
  
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  const start = useCallback(() => {
    if (delay === null) return;
    
    setIsActive(true);
    timeoutId.current = setTimeout(() => {
      savedCallback.current();
      setIsActive(false);
    }, delay);
  }, [delay]);
  
  const stop = useCallback(() => {
    if (timeoutId.current) {
      clearTimeout(timeoutId.current);
      timeoutId.current = null;
      setIsActive(false);
    }
  }, []);
  
  const restart = useCallback(() => {
    stop();
    start();
  }, [stop, start]);
  
  useEffect(() => {
    return () => {
      if (timeoutId.current) {
        clearTimeout(timeoutId.current);
      }
    };
  }, []);
  
  return {
    isActive,
    start,
    stop,
    restart
  };
}

// Usage
function AutoSaveIndicator() {
  const [content, setContent] = useState('');
  const [lastSaved, setLastSaved] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  const saveContent = useCallback(async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setLastSaved(new Date());
    setIsSaving(false);
  }, []);
  
  const { isActive, restart } = useControllableTimeout(saveContent, 2000);
  
  const handleContentChange = (e) => {
    setContent(e.target.value);
    restart(); // Restart the auto-save timer
  };
  
  return (
    <div>
      <textarea
        value={content}
        onChange={handleContentChange}
        placeholder="Start typing... Auto-saves after 2 seconds of inactivity"
        rows={5}
        cols={50}
      />
      
      <div>
        {isSaving && <span>Saving...</span>}
        {isActive && !isSaving && <span>Will save in 2 seconds...</span>}
        {lastSaved && !isActive && !isSaving && (
          <span>Last saved: {lastSaved.toLocaleTimeString()}</span>
        )}
      </div>
    </div>
  );
}
```

---

## Testing Custom Hooks

### Testing Setup

```javascript
// For testing custom hooks, use @testing-library/react-hooks
import { renderHook, act } from '@testing-library/react-hooks';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  test('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter());
    
    expect(result.current.count).toBe(0);
  });
  
  test('should initialize with provided value', () => {
    const { result } = renderHook(() => useCounter(10));
    
    expect(result.current.count).toBe(10);
  });
  
  test('should increment counter', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
  
  test('should decrement counter', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });
  
  test('should reset counter', () => {
    const { result } = renderHook(() => useCounter(10));
    
    act(() => {
      result.current.increment();
      result.current.increment();
    });
    
    expect(result.current.count).toBe(12);
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.count).toBe(10);
  });
});

// Testing hooks with async operations
describe('useFetch', () => {
  beforeEach(() => {
    fetch.resetMocks();
  });
  
  test('should handle successful fetch', async () => {
    const mockData = { id: 1, name: 'Test' };
    fetch.mockResponseOnce(JSON.stringify(mockData));
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useFetch('/api/test')
    );
    
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    
    await waitForNextUpdate();
    
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
  });
  
  test('should handle fetch error', async () => {
    fetch.mockRejectOnce(new Error('API Error'));
    
    const { result, waitForNextUpdate } = renderHook(() => 
      useFetch('/api/test')
    );
    
    await waitForNextUpdate();
    
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe('API Error');
  });
});

// Testing hooks with context
const TestProvider = ({ children }) => (
  <ThemeProvider theme="light">
    {children}
  </ThemeProvider>
);

test('should use theme context', () => {
  const { result } = renderHook(() => useTheme(), {
    wrapper: TestProvider
  });
  
  expect(result.current.theme).toBe('light');
});
```

---

## Best Practices and Guidelines

### Custom Hook Design Principles

```javascript
// ✅ GOOD: Clear, descriptive naming
function useUserProfile(userId) {
  // Implementation
}

function useDebounce(value, delay) {
  // Implementation
}

// ❌ BAD: Vague naming
function useData() {
  // Implementation
}

function useHook() {
  // Implementation
}

// ✅ GOOD: Consistent return patterns
function useToggle(initialValue) {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => setValue(prev => !prev), []);
  
  // Return object for multiple values
  return {
    value,
    toggle,
    setTrue: () => setValue(true),
    setFalse: () => setValue(false)
  };
}

function useCounter(initialValue) {
  const [count, setCount] = useState(initialValue);
  
  // Return array for simple cases
  return [count, setCount];
}

// ✅ GOOD: Proper dependency management
function useWindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 });
  
  useEffect(() => {
    function updateSize() {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    }
    
    updateSize();
    window.addEventListener('resize', updateSize);
    
    return () => window.removeEventListener('resize', updateSize);
  }, []); // Empty dependency array - effect only runs once
  
  return size;
}

// ✅ GOOD: Memoize callbacks
function useApiCall(url) {
  const [data, setData] = useState(null);
  
  const fetchData = useCallback(async () => {
    const response = await fetch(url);
    const result = await response.json();
    setData(result);
  }, [url]); // Re-create when url changes
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, refetch: fetchData };
}
```

### Error Handling in Custom Hooks

```javascript
function useSafeAsyncOperation() {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  });
  
  const execute = useCallback(async (asyncFn) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await asyncFn();
      
      setState({
        data: result,
        loading: false,
        error: null
      });
      
      return result;
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.message
      }));
      
      throw error; // Re-throw for component to handle
    }
  }, []);
  
  return {
    ...state,
    execute
  };
}
```

### Performance Considerations

```javascript
// ✅ GOOD: Avoid unnecessary re-renders
function useExpensiveCalculation(data, options) {
  return useMemo(() => {
    return performExpensiveCalculation(data, options);
  }, [data, options]);
}

// ✅ GOOD: Cleanup resources
function useWebSocket(url) {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onmessage = (event) => {
      setMessages(prev => [...prev, JSON.parse(event.data)]);
    };
    
    setSocket(ws);
    
    // Cleanup on unmount or url change
    return () => {
      ws.close();
    };
  }, [url]);
  
  return { socket, messages };
}

// ✅ GOOD: Stable references
function useStableCallback(callback, deps) {
  return useCallback(callback, deps);
}
```

### Documentation and TypeScript

```typescript
interface UseCounterOptions {
  min?: number;
  max?: number;
  step?: number;
}

interface UseCounterReturn {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
  setValue: (value: number | ((prev: number) => number)) => void;
}

/**
 * Hook for managing counter state with optional constraints
 * 
 * @param initialValue - Initial counter value
 * @param options - Configuration options
 * @returns Counter state and control functions
 * 
 * @example
 * ```tsx
 * function Counter() {
 *   const { count, increment, decrement } = useCounter(0, {
 *     min: 0,
 *     max: 10
 *   });
 *   
 *   return (
 *     <div>
 *       <span>{count}</span>
 *       <button onClick={increment}>+</button>
 *       <button onClick={decrement}>-</button>
 *     </div>
 *   );
 * }
 * ```
 */
function useCounter(
  initialValue: number = 0,
  options: UseCounterOptions = {}
): UseCounterReturn {
  // Implementation
}
```

---

## Summary

Custom hooks are a powerful feature that enables:

1. **Logic Reuse**: Share stateful logic across components
2. **Separation of Concerns**: Keep business logic separate from UI
3. **Testability**: Test complex logic in isolation
4. **Composition**: Combine multiple hooks for complex behaviors
5. **Abstraction**: Hide complex implementation details

### Key Takeaways

- **Follow naming conventions**: Always start with "use"
- **Follow hooks rules**: No conditional hooks, only call from React functions
- **Design clear APIs**: Use consistent return patterns
- **Handle edge cases**: Properly manage errors and cleanup
- **Optimize performance**: Use memoization and stable references
- **Document well**: Provide clear examples and TypeScript types
- **Test thoroughly**: Use testing library for comprehensive coverage

Custom hooks are the key to writing maintainable, reusable React applications. They allow you to extract and share complex logic while keeping components focused on rendering.
