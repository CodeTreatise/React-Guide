# React Hooks Deep Dive

## Table of Contents
1. [Hook Fundamentals](#hook-fundamentals)
2. [useState Patterns](#usestate-patterns)
3. [useEffect Mastery](#useeffect-mastery)
4. [Performance Hooks](#performance-hooks)
5. [Advanced Hook Patterns](#advanced-hook-patterns)
6. [Custom Hook Design](#custom-hook-design)
7. [Hook Testing](#hook-testing)
8. [Common Pitfalls](#common-pitfalls)

## Hook Fundamentals

### What are Hooks?

Hooks are functions that let you "hook into" React features from function components. They allow you to use state and other React features without writing a class.

```jsx
{% raw %}
import React, { useState, useEffect } from 'react';

function Example() {
  // This is a Hook
  const [count, setCount] = useState(0);

  // This is also a Hook
  useEffect(() => {
    document.title = `You clicked ${count} times`;
  });

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
{% endraw %}
```

### Rules of Hooks (Essential!)

#### Rule 1: Only Call Hooks at the Top Level

```jsx
// ❌ Don't call Hooks inside loops, conditions, or nested functions
function BadExample() {
  const [name, setName] = useState('');
  
  if (name !== '') {
    // 🔴 This is wrong!
    useEffect(() => {
      localStorage.setItem('name', name);
    });
  }
}

// ✅ Do call Hooks at the top level
function GoodExample() {
  const [name, setName] = useState('');
  
  useEffect(() => {
    if (name !== '') {
      localStorage.setItem('name', name);
    }
  }, [name]);
}
```

#### Rule 2: Only Call Hooks from React Functions

```jsx
{% raw %}
// ❌ Don't call Hooks from regular JavaScript functions
function formatName(user) {
  const [formattedName, setFormattedName] = useState(''); // 🔴 Wrong!
  return formattedName;
}

// ✅ Do call Hooks from React function components
function UserProfile({ user }) {
  const [formattedName, setFormattedName] = useState('');
  
  useEffect(() => {
    setFormattedName(`${user.firstName} ${user.lastName}`);
  }, [user]);
  
  return <h1>{formattedName}</h1>;
}

// ✅ Do call Hooks from custom Hooks
function useFormattedName(user) {
  const [formattedName, setFormattedName] = useState('');
  
  useEffect(() => {
    setFormattedName(`${user.firstName} ${user.lastName}`);
  }, [user]);
  
  return formattedName;
}
{% endraw %}
```

## useState Patterns

### Basic State Management

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
      <button onClick={() => setCount(count - 1)}>-</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

### Functional Updates

When the new state depends on the previous state, use functional updates:

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  const increment = () => {
    // ✅ Functional update
    setCount(prevCount => prevCount + 1);
  };
  
  const incrementTwice = () => {
    // ✅ Both updates will work correctly
    setCount(prevCount => prevCount + 1);
    setCount(prevCount => prevCount + 1);
  };
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
      <button onClick={incrementTwice}>Increment Twice</button>
    </div>
  );
}
```

### Object State

```jsx
function UserProfile() {
  const [user, setUser] = useState({
    name: '',
    email: '',
    age: 0,
    preferences: {
      theme: 'light',
      notifications: true
    }
  });
  
  const updateName = (name) => {
    setUser(prevUser => ({
      ...prevUser,
      name
    }));
  };
  
  const updatePreference = (key, value) => {
    setUser(prevUser => ({
      ...prevUser,
      preferences: {
        ...prevUser.preferences,
        [key]: value
      }
    }));
  };
  
  return (
    <div>
      <input
        value={user.name}
        onChange={(e) => updateName(e.target.value)}
        placeholder="Name"
      />
      <label>
        <input
          type="checkbox"
          checked={user.preferences.notifications}
          onChange={(e) => updatePreference('notifications', e.target.checked)}
        />
        Enable Notifications
      </label>
    </div>
  );
}
```

### Array State

```jsx
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');
  
  const addTodo = () => {
    if (inputValue.trim()) {
      setTodos(prevTodos => [
        ...prevTodos,
        {
          id: Date.now(),
          text: inputValue,
          completed: false
        }
      ]);
      setInputValue('');
    }
  };
  
  const toggleTodo = (id) => {
    setTodos(prevTodos =>
      prevTodos.map(todo =>
        todo.id === id
          ? { ...todo, completed: !todo.completed }
          : todo
      )
    );
  };
  
  const deleteTodo = (id) => {
    setTodos(prevTodos => prevTodos.filter(todo => todo.id !== id));
  };
  
  return (
    <div>
      <input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && addTodo()}
      />
      <button onClick={addTodo}>Add Todo</button>
      
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{
              textDecoration: todo.completed ? 'line-through' : 'none'
            }}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## useEffect Mastery

### Effect Patterns

#### 1. Effect with No Dependencies (Runs on Every Render)

```jsx
function Component() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    console.log('Effect runs on every render');
  });
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

#### 2. Effect with Empty Dependencies (Runs Once on Mount)

```jsx
function DataFetcher() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData();
  }, []); // Empty dependency array
  
  const fetchData = async () => {
    const response = await fetch('/api/data');
    const result = await response.json();
    setData(result);
  };
  
  return <div>{data ? JSON.stringify(data) : 'Loading...'}</div>;
}
```

#### 3. Effect with Dependencies

```jsx
{% raw %}
function SearchResults({ query }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }
    
    setLoading(true);
    
    const searchData = async () => {
      try {
        const response = await fetch(`/api/search?q=${query}`);
        const data = await response.json();
        setResults(data);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setLoading(false);
      }
    };
    
    searchData();
  }, [query]); // Effect runs when query changes
  
  return (
    <div>
      {loading ? 'Searching...' : (
        <ul>
          {results.map(result => (
            <li key={result.id}>{result.title}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
{% endraw %}
```

### Cleanup Functions

```jsx
function Timer() {
  const [seconds, setSeconds] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(prevSeconds => prevSeconds + 1);
    }, 1000);
    
    // Cleanup function
    return () => {
      clearInterval(interval);
    };
  }, []);
  
  return <div>Seconds: {seconds}</div>;
}

function WindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);
  
  useEffect(() => {
    const handleResize = () => {
      setWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  return <div>Window width: {width}px</div>;
}
```

### Advanced useEffect Patterns

#### Debouncing with useEffect

```jsx
function SearchInput() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 500);
    
    return () => {
      clearTimeout(timer);
    };
  }, [query]);
  
  useEffect(() => {
    if (debouncedQuery) {
      // Perform search
      console.log('Searching for:', debouncedQuery);
    }
  }, [debouncedQuery]);
  
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

#### Conditional Effects

```jsx
{% raw %}
function ConditionalEffect({ shouldFetch, userId }) {
  const [userData, setUserData] = useState(null);
  
  useEffect(() => {
    if (shouldFetch && userId) {
      fetchUserData(userId);
    }
  }, [shouldFetch, userId]);
  
  const fetchUserData = async (id) => {
    const response = await fetch(`/api/users/${id}`);
    const data = await response.json();
    setUserData(data);
  };
  
  return <div>{userData?.name || 'No user data'}</div>;
}
{% endraw %}
```

## Performance Hooks

### useMemo

Use `useMemo` to memoize expensive calculations:

```jsx
function ExpensiveComponent({ items, filter }) {
  // Expensive calculation memoized
  const filteredItems = useMemo(() => {
    console.log('Filtering items...');
    return items.filter(item => 
      item.name.toLowerCase().includes(filter.toLowerCase())
    );
  }, [items, filter]);
  
  // Expensive sort operation
  const sortedItems = useMemo(() => {
    console.log('Sorting items...');
    return [...filteredItems].sort((a, b) => a.name.localeCompare(b.name));
  }, [filteredItems]);
  
  return (
    <ul>
      {sortedItems.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

### useCallback

Use `useCallback` to memoize function references:

```jsx
import React, { useState, useCallback, memo } from 'react';

// Memoized child component
const ExpensiveChild = memo(({ onClick, children }) => {
  console.log('ExpensiveChild rendered');
  return <button onClick={onClick}>{children}</button>;
});

function Parent() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  // Without useCallback - new function every render
  const handleClick = () => {
    console.log('Button clicked');
  };
  
  // With useCallback - stable function reference
  const handleClickMemoized = useCallback(() => {
    console.log('Memoized button clicked');
  }, []);
  
  // useCallback with dependencies
  const handleCountClick = useCallback(() => {
    console.log('Current count:', count);
  }, [count]);
  
  return (
    <div>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="This will cause re-renders"
      />
      
      <ExpensiveChild onClick={handleClick}>
        Regular (re-renders on every parent render)
      </ExpensiveChild>
      
      <ExpensiveChild onClick={handleClickMemoized}>
        Memoized (stable reference)
      </ExpensiveChild>
      
      <ExpensiveChild onClick={handleCountClick}>
        Count-dependent (re-renders when count changes)
      </ExpensiveChild>
      
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
    </div>
  );
}
```

## Advanced Hook Patterns

### useReducer for Complex State

```jsx
{% raw %}
const initialState = {
  users: [],
  loading: false,
  error: null,
  filter: 'all'
};

function userReducer(state, action) {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, users: action.payload };
    
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    
    case 'ADD_USER':
      return {
        ...state,
        users: [...state.users, action.payload]
      };
    
    case 'UPDATE_USER':
      return {
        ...state,
        users: state.users.map(user =>
          user.id === action.payload.id ? action.payload : user
        )
      };
    
    case 'DELETE_USER':
      return {
        ...state,
        users: state.users.filter(user => user.id !== action.payload)
      };
    
    case 'SET_FILTER':
      return { ...state, filter: action.payload };
    
    default:
      throw new Error(`Unhandled action type: ${action.type}`);
  }
}

function UserManager() {
  const [state, dispatch] = useReducer(userReducer, initialState);
  
  const fetchUsers = async () => {
    dispatch({ type: 'FETCH_START' });
    try {
      const response = await fetch('/api/users');
      const users = await response.json();
      dispatch({ type: 'FETCH_SUCCESS', payload: users });
    } catch (error) {
      dispatch({ type: 'FETCH_ERROR', payload: error.message });
    }
  };
  
  const addUser = (user) => {
    dispatch({ type: 'ADD_USER', payload: { ...user, id: Date.now() } });
  };
  
  const deleteUser = (id) => {
    dispatch({ type: 'DELETE_USER', payload: id });
  };
  
  useEffect(() => {
    fetchUsers();
  }, []);
  
  const filteredUsers = useMemo(() => {
    switch (state.filter) {
      case 'active':
        return state.users.filter(user => user.active);
      case 'inactive':
        return state.users.filter(user => !user.active);
      default:
        return state.users;
    }
  }, [state.users, state.filter]);
  
  if (state.loading) return <div>Loading...</div>;
  if (state.error) return <div>Error: {state.error}</div>;
  
  return (
    <div>
      <select
        value={state.filter}
        onChange={(e) => dispatch({ type: 'SET_FILTER', payload: e.target.value })}
      >
        <option value="all">All Users</option>
        <option value="active">Active Users</option>
        <option value="inactive">Inactive Users</option>
      </select>
      
      <ul>
        {filteredUsers.map(user => (
          <li key={user.id}>
            {user.name}
            <button onClick={() => deleteUser(user.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
{% endraw %}
```

### useRef Patterns

#### DOM Manipulation

```jsx
function AutoFocusInput() {
  const inputRef = useRef(null);
  
  useEffect(() => {
    inputRef.current.focus();
  }, []);
  
  return <input ref={inputRef} type="text" placeholder="Auto-focused" />;
}
```

#### Storing Mutable Values

```jsx
{% raw %}
function TrackingComponent() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);
  const renderCountRef = useRef(0);
  
  useEffect(() => {
    countRef.current = count;
    renderCountRef.current += 1;
  });
  
  const asyncAlert = () => {
    setTimeout(() => {
      // This will show the current count, not the count when button was clicked
      alert(`Current count: ${countRef.current}`);
    }, 3000);
  };
  
  return (
    <div>
      <p>Count: {count}</p>
      <p>Render count: {renderCountRef.current}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={asyncAlert}>Show count in 3 seconds</button>
    </div>
  );
}
{% endraw %}
```

#### Previous Value Tracking

```jsx
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

function Counter() {
  const [count, setCount] = useState(0);
  const prevCount = usePrevious(count);
  
  return (
    <div>
      <p>Current: {count}</p>
      <p>Previous: {prevCount}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

## Custom Hook Design

### Design Principles

1. **Single Responsibility**: Each hook should have one clear purpose
2. **Reusability**: Should be reusable across different components
3. **Abstraction**: Hide complexity behind a simple interface
4. **Composition**: Hooks should compose well together

### Example: useToggle

```jsx
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
  
  return { value, toggle, setTrue, setFalse, setValue };
}

// Usage
function ToggleExample() {
  const modal = useToggle(false);
  const darkMode = useToggle(true);
  
  return (
    <div>
      <button onClick={modal.toggle}>
        {modal.value ? 'Close' : 'Open'} Modal
      </button>
      
      <button onClick={darkMode.toggle}>
        Switch to {darkMode.value ? 'Light' : 'Dark'} Mode
      </button>
      
      {modal.value && (
        <div style={{ background: darkMode.value ? '#333' : '#fff' }}>
          Modal Content
          <button onClick={modal.setFalse}>Close</button>
        </div>
      )}
    </div>
  );
}
```

### Example: useAsync

```jsx
{% raw %}
function useAsync(asyncFunction, dependencies = []) {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  });
  
  const execute = useCallback(async (...args) => {
    setState({ data: null, loading: true, error: null });
    
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

// Usage
function UserProfile({ userId }) {
  const fetchUser = useCallback(
    (id) => fetch(`/api/users/${id}`).then(res => res.json()),
    []
  );
  
  const { data: user, loading, error, execute } = useAsync(fetchUser);
  
  useEffect(() => {
    if (userId) {
      execute(userId);
    }
  }, [userId, execute]);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return <div>No user found</div>;
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <button onClick={() => execute(userId)}>Refresh</button>
    </div>
  );
}
{% endraw %}
```

## Hook Testing

### Testing Custom Hooks with React Testing Library

```jsx
import { renderHook, act } from '@testing-library/react';
import { useToggle } from './useToggle';

describe('useToggle', () => {
  test('should toggle value', () => {
    const { result } = renderHook(() => useToggle(false));
    
    expect(result.current.value).toBe(false);
    
    act(() => {
      result.current.toggle();
    });
    
    expect(result.current.value).toBe(true);
  });
  
  test('should set value to true', () => {
    const { result } = renderHook(() => useToggle(false));
    
    act(() => {
      result.current.setTrue();
    });
    
    expect(result.current.value).toBe(true);
  });
});
```

### Testing Effects

```jsx
{% raw %}
import { renderHook } from '@testing-library/react';
import { useEffect, useState } from 'react';

function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  
  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]);
  
  return { count, setCount };
}

test('should update document title', () => {
  const { result } = renderHook(() => useCounter(5));
  
  expect(document.title).toBe('Count: 5');
  
  act(() => {
    result.current.setCount(10);
  });
  
  expect(document.title).toBe('Count: 10');
});
{% endraw %}
```

## Common Pitfalls

### 1. Stale Closures

```jsx
// ❌ Problem: stale closure
function BadTimer() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCount(count + 1); // This will always be 0 + 1
    }, 1000);
    
    return () => clearInterval(interval);
  }, []); // Missing dependency
  
  return <div>{count}</div>;
}

// ✅ Solution 1: Functional update
function GoodTimer1() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCount(prevCount => prevCount + 1);
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return <div>{count}</div>;
}

// ✅ Solution 2: Include dependency
function GoodTimer2() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCount(count + 1);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [count]); // Include count as dependency
  
  return <div>{count}</div>;
}
```

### 2. Infinite Loops

```jsx
// ❌ Problem: infinite loop
function BadExample() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetchData().then(setData);
  }, [data]); // This causes infinite loop
  
  return <div>{data.length}</div>;
}

// ✅ Solution: Remove unnecessary dependency
function GoodExample() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetchData().then(setData);
  }, []); // Only run once
  
  return <div>{data.length}</div>;
}
```

### 3. Missing Dependencies

```jsx
// ❌ Problem: missing dependencies
function BadExample({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []); // Missing userId dependency
  
  return <div>{user?.name}</div>;
}

// ✅ Solution: Include all dependencies
function GoodExample({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]); // Include userId
  
  return <div>{user?.name}</div>;
}
```

### 4. Overusing useMemo and useCallback

```jsx
// ❌ Unnecessary optimization
function OverOptimized() {
  const [count, setCount] = useState(0);
  
  // Unnecessary - this is a simple value
  const doubledCount = useMemo(() => count * 2, [count]);
  
  // Unnecessary - this function is not passed to children
  const increment = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);
  
  return (
    <div>
      <p>{doubledCount}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}

// ✅ Keep it simple
function Simple() {
  const [count, setCount] = useState(0);
  
  const doubledCount = count * 2; // Simple calculation
  
  const increment = () => {
    setCount(prev => prev + 1); // Simple function
  };
  
  return (
    <div>
      <p>{doubledCount}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}
```

## Best Practices Summary

1. **Follow the Rules of Hooks** - Always call hooks at the top level
2. **Use the dependency array correctly** - Include all dependencies in useEffect
3. **Optimize only when needed** - Don't overuse useMemo and useCallback
4. **Create custom hooks** - Extract and reuse stateful logic
5. **Test your hooks** - Write tests for custom hooks
6. **Handle cleanup** - Always clean up side effects
7. **Use functional updates** - When new state depends on previous state
8. **Keep hooks simple** - Single responsibility principle

---

This deep dive covers the essential patterns and best practices for React Hooks. Master these concepts to write efficient, maintainable React applications!
