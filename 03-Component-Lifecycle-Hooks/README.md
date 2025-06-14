# Module 3: Component Lifecycle & Hooks

## 📚 Learning Objectives

By the end of this module, you will:
- Master React component lifecycle methods and phases
- Understand the complete lifecycle of React components
- Learn React Hooks fundamentals and built-in hooks
- Apply hooks in real-world scenarios
- Build custom hooks for reusable logic
- Understand hooks rules and best practices
- Debug component lifecycle and hook behaviors

## 🎯 Prerequisites

- Completed Module 1: JavaScript Prerequisites
- Completed Module 2: React Fundamentals
- Understanding of React components, props, and state
- Basic knowledge of ES6+ features

## 📖 Module Content

### 1. Component Lifecycle Overview

React components go through three main phases:

#### **Mounting Phase**
- Component is being created and inserted into the DOM
- Methods: `constructor()`, `render()`, `componentDidMount()`

#### **Updating Phase**
- Component is being re-rendered as a result of changes to props or state
- Methods: `render()`, `componentDidUpdate()`, `getSnapshotBeforeUpdate()`

#### **Unmounting Phase**
- Component is being removed from the DOM
- Methods: `componentWillUnmount()`

### 2. Class Component Lifecycle Methods

```jsx
{% raw %}
class LifecycleExample extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    console.log('1. Constructor called');
  }

  componentDidMount() {
    console.log('3. Component mounted');
    // Perfect for API calls, subscriptions
    this.timer = setInterval(() => {
      this.setState(prevState => ({ count: prevState.count + 1 }));
    }, 1000);
  }

  componentDidUpdate(prevProps, prevState) {
    console.log('4. Component updated');
    if (prevState.count !== this.state.count) {
      document.title = `Count: ${this.state.count}`;
    }
  }

  componentWillUnmount() {
    console.log('5. Component will unmount');
    // Cleanup: clear timers, cancel subscriptions
    clearInterval(this.timer);
  }

  render() {
    console.log('2. Render called');
    return (
      <div>
        <h2>Count: {this.state.count}</h2>
        <button onClick={() => this.setState({ count: 0 })}>
          Reset
        </button>
      </div>
    );
  }
}
{% endraw %}
```

### 3. Introduction to React Hooks

Hooks allow you to use state and other React features in functional components.

#### **Rules of Hooks**
1. Only call hooks at the top level (not inside loops, conditions, or nested functions)
2. Only call hooks from React function components or custom hooks

```jsx
// ❌ Wrong - Hook inside condition
function BadExample() {
  if (someCondition) {
    const [count, setCount] = useState(0); // Don't do this!
  }
}

// ✅ Correct - Hook at top level
function GoodExample() {
  const [count, setCount] = useState(0);
  
  if (someCondition) {
    // Use the state here
  }
}
```

### 4. Built-in React Hooks

#### **useState Hook**
Manages local state in functional components.

```jsx
import React, { useState } from 'react';

function Counter() {
  // Declare state variable with initial value
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  // Multiple state updates
  const handleIncrement = () => {
    setCount(prevCount => prevCount + 1);
  };

  // Object state
  const [user, setUser] = useState({
    name: '',
    email: '',
    age: 0
  });

  const updateUser = (field, value) => {
    setUser(prevUser => ({
      ...prevUser,
      [field]: value
    }));
  };

  return (
    <div>
      <h2>Count: {count}</h2>
      <button onClick={handleIncrement}>Increment</button>
      
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter name"
      />
      
      <div>
        <input
          type="text"
          value={user.name}
          onChange={(e) => updateUser('name', e.target.value)}
          placeholder="User name"
        />
        <input
          type="email"
          value={user.email}
          onChange={(e) => updateUser('email', e.target.value)}
          placeholder="User email"
        />
      </div>
    </div>
  );
}
```

#### **useEffect Hook**
Performs side effects in functional components (replaces lifecycle methods).

```jsx
{% raw %}
import React, { useState, useEffect } from 'react';

function DataFetcher() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [count, setCount] = useState(0);

  // Effect runs after every render (componentDidMount + componentDidUpdate)
  useEffect(() => {
    console.log('Effect runs on every render');
  });

  // Effect runs only once (componentDidMount)
  useEffect(() => {
    console.log('Component mounted');
    fetchData();
  }, []); // Empty dependency array

  // Effect runs when count changes
  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]); // count dependency

  // Effect with cleanup (componentWillUnmount)
  useEffect(() => {
    const timer = setInterval(() => {
      console.log('Timer tick');
    }, 1000);

    // Cleanup function
    return () => {
      clearInterval(timer);
      console.log('Timer cleared');
    };
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://jsonplaceholder.typicode.com/posts/1');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>{data?.title}</h2>
      <p>{data?.body}</p>
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
    </div>
  );
}
{% endraw %}
```

#### **useContext Hook**
Consumes context values without nesting.

```jsx
import React, { createContext, useContext, useState } from 'react';

// Create context
const ThemeContext = createContext();

// Provider component
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Consumer component using useContext
function ThemedButton() {
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    <button
      onClick={toggleTheme}
      style={{
        backgroundColor: theme === 'light' ? '#fff' : '#333',
        color: theme === 'light' ? '#333' : '#fff'
      }}
    >
      Toggle Theme (Current: {theme})
    </button>
  );
}

// App component
function App() {
  return (
    <ThemeProvider>
      <div>
        <h1>Theme Example</h1>
        <ThemedButton />
      </div>
    </ThemeProvider>
  );
}
```

#### **useReducer Hook**
Manages complex state logic with reducer function.

```jsx
{% raw %}
import React, { useReducer } from 'react';

// Reducer function
function counterReducer(state, action) {
  switch (action.type) {
    case 'INCREMENT':
      return { count: state.count + 1 };
    case 'DECREMENT':
      return { count: state.count - 1 };
    case 'RESET':
      return { count: 0 };
    case 'SET_COUNT':
      return { count: action.payload };
    default:
      throw new Error(`Unhandled action type: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(counterReducer, { count: 0 });

  return (
    <div>
      <h2>Count: {state.count}</h2>
      <button onClick={() => dispatch({ type: 'INCREMENT' })}>
        +
      </button>
      <button onClick={() => dispatch({ type: 'DECREMENT' })}>
        -
      </button>
      <button onClick={() => dispatch({ type: 'RESET' })}>
        Reset
      </button>
      <button onClick={() => dispatch({ type: 'SET_COUNT', payload: 10 })}>
        Set to 10
      </button>
    </div>
  );
}
{% endraw %}
```

### 5. Additional Built-in Hooks

#### **useMemo Hook**
Memoizes expensive calculations.

```jsx
import React, { useState, useMemo } from 'react';

function ExpensiveComponent() {
  const [count, setCount] = useState(0);
  const [todos, setTodos] = useState([]);

  // Expensive calculation - only recalculates when count changes
  const expensiveValue = useMemo(() => {
    console.log('Calculating expensive value...');
    return count * 2;
  }, [count]);

  // Filter todos - only recalculates when todos change
  const completedTodos = useMemo(() => {
    console.log('Filtering todos...');
    return todos.filter(todo => todo.completed);
  }, [todos]);

  return (
    <div>
      <h2>Count: {count}</h2>
      <h3>Expensive Value: {expensiveValue}</h3>
      <h3>Completed Todos: {completedTodos.length}</h3>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

#### **useCallback Hook**
Memoizes function references.

```jsx
import React, { useState, useCallback, memo } from 'react';

// Memoized child component
const Button = memo(({ onClick, children }) => {
  console.log('Button rendered:', children);
  return <button onClick={onClick}>{children}</button>;
});

function Parent() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  // Without useCallback - new function on every render
  const handleClick1 = () => {
    console.log('Button 1 clicked');
  };

  // With useCallback - function memoized
  const handleClick2 = useCallback(() => {
    console.log('Button 2 clicked');
  }, []);

  // useCallback with dependencies
  const handleClick3 = useCallback(() => {
    console.log('Count is:', count);
  }, [count]);

  return (
    <div>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Type to trigger re-render"
      />
      
      <Button onClick={handleClick1}>Button 1 (re-renders)</Button>
      <Button onClick={handleClick2}>Button 2 (stable)</Button>
      <Button onClick={handleClick3}>Button 3 (depends on count)</Button>
      
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
    </div>
  );
}
```

#### **useRef Hook**
Creates mutable refs and accesses DOM elements.

```jsx
{% raw %}
import React, { useRef, useEffect, useState } from 'react';

function RefExample() {
  const inputRef = useRef(null);
  const countRef = useRef(0);
  const [renders, setRenders] = useState(0);

  useEffect(() => {
    // Focus input on mount
    inputRef.current.focus();
  }, []);

  useEffect(() => {
    // Track renders without causing re-render
    countRef.current += 1;
  });

  const handleFocus = () => {
    inputRef.current.focus();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Input value: ${inputRef.current.value}`);
  };

  return (
    <div>
      <p>Renders: {countRef.current}</p>
      
      <form onSubmit={handleSubmit}>
        <input ref={inputRef} type="text" placeholder="Focus me!" />
        <button type="submit">Submit</button>
      </form>
      
      <button onClick={handleFocus}>Focus Input</button>
      <button onClick={() => setRenders(renders + 1)}>
        Force Re-render
      </button>
    </div>
  );
}
{% endraw %}
```

### 6. Custom Hooks

Create reusable stateful logic.

```jsx
{% raw %}
// Custom hook for local storage
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading localStorage:', error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error setting localStorage:', error);
    }
  };

  return [storedValue, setValue];
}

// Custom hook for API data fetching
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(url);
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
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
}

// Custom hook for form handling
function useForm(initialValues) {
  const [values, setValues] = useState(initialValues);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prevValues => ({
      ...prevValues,
      [name]: value
    }));
  };

  const reset = () => {
    setValues(initialValues);
  };

  return { values, handleChange, reset };
}

// Usage examples
function CustomHookExamples() {
  const [name, setName] = useLocalStorage('name', '');
  const { data, loading, error } = useApi('https://jsonplaceholder.typicode.com/posts/1');
  const { values, handleChange, reset } = useForm({
    email: '',
    password: ''
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Custom Hooks Example</h2>
      
      <div>
        <label>Name (stored in localStorage):</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

      <div>
        <h3>API Data:</h3>
        <p>{data?.title}</p>
      </div>

      <div>
        <h3>Form:</h3>
        <input
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          placeholder="Email"
        />
        <input
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          placeholder="Password"
        />
        <button onClick={reset}>Reset Form</button>
      </div>
    </div>
  );
}
{% endraw %}
```

## 🎯 Practical Exercises

### Exercise 1: Lifecycle Logger
Create a component that logs all lifecycle events and demonstrates proper cleanup.

### Exercise 2: Hook Conversion
Convert class components to functional components using hooks.

### Exercise 3: Custom Hook Development
Build a custom hook for managing API requests with loading, error, and retry functionality.

### Exercise 4: Performance Optimization
Use `useMemo` and `useCallback` to optimize a component with expensive calculations.

## 📊 Assessment Criteria

### Knowledge Check
- [ ] Explain the three phases of React component lifecycle
- [ ] List the rules of hooks and explain why they exist
- [ ] Demonstrate proper use of `useEffect` with different dependency arrays
- [ ] Create custom hooks for reusable logic
- [ ] Optimize components using `useMemo` and `useCallback`
- [ ] Properly handle cleanup in effects

### Practical Assessment
- [ ] Build a component that fetches data on mount and cleans up on unmount
- [ ] Create a form using hooks with validation and local storage persistence
- [ ] Develop a custom hook that other team members can reuse
- [ ] Optimize a performance-heavy component using appropriate hooks

### Code Quality
- [ ] Follow hooks rules consistently
- [ ] Implement proper error handling in effects
- [ ] Use appropriate hook dependencies
- [ ] Write clean, readable custom hooks
- [ ] Document hook usage and dependencies

## 🚀 Project: Todo List with Hooks

Build a complete todo list application using hooks:

**Requirements:**
- Add, edit, delete todos
- Mark todos as complete
- Filter todos (all, active, completed)
- Persist data in localStorage
- Search functionality
- Dark/light theme toggle

**Hooks to Use:**
- `useState` for todo state
- `useEffect` for localStorage persistence
- `useContext` for theme management
- `useReducer` for complex todo operations
- `useMemo` for filtered todo lists
- `useCallback` for optimized event handlers
- Custom hooks for localStorage and theme

## 📚 Additional Resources

### Documentation
- [React Hooks Documentation](https://reactjs.org/docs/hooks-intro.html)
- [Component Lifecycle](https://reactjs.org/docs/react-component.html)

### Articles
- "A Complete Guide to useEffect" by Dan Abramov
- "When to useMemo and useCallback" by Kent C. Dodds
- "Rules of Hooks Explained"

### Practice
- Build components using only hooks
- Convert existing class components to hooks
- Create a library of custom hooks

## ⏭️ Next Steps

After mastering this module, you'll be ready for:
- **Module 4**: State Management (Context API, Redux basics)
- Advanced component patterns
- Performance optimization techniques
- Building complex applications with multiple hooks

---

**Estimated Time:** 1-2 weeks  
**Difficulty:** Intermediate  
**Prerequisites:** Modules 1-2 completed