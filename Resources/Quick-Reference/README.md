# 🚀 React Quick Reference & Cheatsheets

> **Essential React syntax, patterns, and APIs at your fingertips**

---

## 📋 Table of Contents

1. [Component Syntax](#component-syntax)
2. [Hooks Reference](#hooks-reference)
3. [Event Handling](#event-handling)
4. [Styling Patterns](#styling-patterns)
5. [Common Patterns](#common-patterns)
6. [Performance Tips](#performance-tips)
7. [TypeScript Integration](#typescript-integration)
8. [Debugging Commands](#debugging-commands)

---

## 🧩 Component Syntax

### Function Components
```jsx
// Basic function component
function Welcome(props) {
  return <h1>Hello, {props.name}!</h1>;
}

// Arrow function component
const Welcome = (props) => {
  return <h1>Hello, {props.name}!</h1>;
};

// Arrow function with implicit return
const Welcome = ({ name }) => <h1>Hello, {name}!</h1>;

// Component with default props
const Welcome = ({ name = "World" }) => <h1>Hello, {name}!</h1>;
```

### JSX Essentials
```jsx
// JSX expression
const element = <h1>Hello, world!</h1>;

// JSX with expressions
const name = 'Josh Perez';
const element = <h1>Hello, {name}</h1>;

// JSX attributes
const element = <div tabIndex="0"></div>;
const element = <img src={user.avatarUrl}></img>;

// JSX children
const element = (
  <div>
    <h1>Hello!</h1>
    <h2>Good to see you here.</h2>
  </div>
);

// Conditional rendering
const element = condition ? <Component1 /> : <Component2 />;
const element = condition && <Component />;

// List rendering
const numbers = [1, 2, 3, 4, 5];
const listItems = numbers.map((number) => 
  <li key={number.toString()}>{number}</li>
);
```

---

## 🎣 Hooks Reference

### useState
```jsx
import { useState } from 'react';

// Basic state
const [count, setCount] = useState(0);
const [name, setName] = useState('');
const [user, setUser] = useState(null);

// State with object
const [state, setState] = useState({ name: '', age: 0 });

// Functional update
setCount(prevCount => prevCount + 1);
setState(prevState => ({ ...prevState, name: 'John' }));

// Lazy initial state
const [state, setState] = useState(() => {
  const initialState = someExpensiveComputation(props);
  return initialState;
});
```

### useEffect
```jsx
import { useEffect } from 'react';

// Effect with no dependencies (runs on every render)
useEffect(() => {
  console.log('Render');
});

// Effect with empty dependencies (runs once)
useEffect(() => {
  console.log('Mount');
}, []);

// Effect with dependencies
useEffect(() => {
  fetchData(id);
}, [id]);

// Effect with cleanup
useEffect(() => {
  const subscription = subscribeToSomething(id);
  return () => subscription.unsubscribe();
}, [id]);

// Multiple effects
useEffect(() => {
  document.title = `You clicked ${count} times`;
}, [count]);

useEffect(() => {
  const interval = setInterval(() => {
    setSeconds(seconds => seconds + 1);
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### useContext
```jsx
import { useContext, createContext } from 'react';

// Create context
const ThemeContext = createContext();

// Provider
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Component />
    </ThemeContext.Provider>
  );
}

// Consumer
function Component() {
  const theme = useContext(ThemeContext);
  return <div className={theme}>Content</div>;
}
```

### useReducer
```jsx
import { useReducer } from 'react';

// Reducer function
function counterReducer(state, action) {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 };
    case 'decrement':
      return { count: state.count - 1 };
    case 'reset':
      return { count: 0 };
    default:
      throw new Error();
  }
}

// Component using useReducer
function Counter() {
  const [state, dispatch] = useReducer(counterReducer, { count: 0 });
  
  return (
    <div>
      Count: {state.count}
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
}
```

### useMemo & useCallback
```jsx
import { useMemo, useCallback } from 'react';

// useMemo for expensive calculations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);

// useCallback for function references
const memoizedCallback = useCallback(
  () => {
    doSomething(a, b);
  },
  [a, b]
);

// useCallback with dependencies
const handleClick = useCallback((id) => {
  onClick(id);
}, [onClick]);
```

### useRef
```jsx
import { useRef, useEffect } from 'react';

function TextInputWithFocusButton() {
  const inputEl = useRef(null);
  
  const onButtonClick = () => {
    inputEl.current.focus();
  };
  
  return (
    <>
      <input ref={inputEl} type="text" />
      <button onClick={onButtonClick}>Focus the input</button>
    </>
  );
}

// Storing mutable values
function Timer() {
  const intervalRef = useRef();
  
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      // timer logic
    }, 1000);
    
    return () => clearInterval(intervalRef.current);
  }, []);
}
```

### Custom Hooks
```jsx
// Custom hook for API calls
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetch(url)
      .then(response => response.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);
  
  return { data, loading, error };
}

// Custom hook for local storage
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });
  
  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(error);
    }
  };
  
  return [storedValue, setValue];
}
```

---

## 🎯 Event Handling

### Common Events
```jsx
// Click events
<button onClick={(e) => console.log('clicked')}>Click me</button>
<button onClick={handleClick}>Click me</button>

// Form events
<form onSubmit={(e) => {
  e.preventDefault();
  handleSubmit(e);
}}>
  <input 
    onChange={(e) => setValue(e.target.value)}
    onFocus={(e) => console.log('focused')}
    onBlur={(e) => console.log('blurred')}
  />
</form>

// Keyboard events
<input 
  onKeyDown={(e) => {
    if (e.key === 'Enter') {
      handleEnter();
    }
  }}
  onKeyPress={(e) => console.log(e.key)}
/>

// Mouse events
<div
  onMouseEnter={() => setHovered(true)}
  onMouseLeave={() => setHovered(false)}
  onMouseDown={(e) => console.log('mouse down')}
  onMouseUp={(e) => console.log('mouse up')}
>
  Hover me
</div>
```

### Event Handler Patterns
```jsx
// Arrow function in JSX (creates new function on each render)
<button onClick={() => handleClick(id)}>Click</button>

// useCallback for optimization
const handleClick = useCallback((id) => {
  // handle click
}, []);

// Event handler with multiple parameters
const handleClick = (id, name) => (e) => {
  console.log(id, name, e);
};

<button onClick={handleClick(user.id, user.name)}>Click</button>
```

---

## 🎨 Styling Patterns

### Inline Styles
```jsx
const style = {
  color: 'blue',
  backgroundColor: 'lightgray',
  padding: '10px',
  fontSize: '16px'
};

<div style={style}>Styled div</div>
<div style={{ color: 'red', margin: '10px' }}>Inline styled</div>
```

### CSS Classes
```jsx
// Static class
<div className="my-class">Content</div>

// Dynamic classes
<div className={isActive ? 'active' : 'inactive'}>Content</div>
<div className={`base-class ${isActive ? 'active' : ''}`}>Content</div>

// Multiple classes
<div className={['class1', 'class2', isActive && 'active'].filter(Boolean).join(' ')}>
  Content
</div>
```

### CSS Modules
```jsx
import styles from './Component.module.css';

<div className={styles.container}>
  <h1 className={styles.title}>Title</h1>
</div>
```

### Styled Components
```jsx
import styled from 'styled-components';

const Button = styled.button`
  background-color: ${props => props.primary ? 'blue' : 'gray'};
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
`;

<Button primary>Primary Button</Button>
<Button>Secondary Button</Button>
```

---

## 🔄 Common Patterns

### Conditional Rendering
```jsx
// Ternary operator
{condition ? <ComponentA /> : <ComponentB />}

// Logical AND
{condition && <Component />}

// Logical OR for fallbacks
{data || <LoadingSpinner />}

// Switch statement pattern
function renderContent() {
  switch (status) {
    case 'loading':
      return <LoadingSpinner />;
    case 'error':
      return <ErrorMessage />;
    case 'success':
      return <DataDisplay data={data} />;
    default:
      return null;
  }
}
```

### List Rendering
```jsx
// Basic list
{items.map(item => (
  <div key={item.id}>{item.name}</div>
))}

// List with index
{items.map((item, index) => (
  <div key={index}>{item.name}</div>
))}

// Nested lists
{categories.map(category => (
  <div key={category.id}>
    <h3>{category.name}</h3>
    {category.items.map(item => (
      <div key={item.id}>{item.name}</div>
    ))}
  </div>
))}
```

### Form Patterns
```jsx
// Controlled component
function Form() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(formData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Name"
      />
      <input
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Email"
      />
      <textarea
        name="message"
        value={formData.message}
        onChange={handleChange}
        placeholder="Message"
      />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Error Boundaries
```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.log('Error caught:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    
    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>
```

---

## ⚡ Performance Tips

### React.memo
```jsx
// Prevent unnecessary re-renders
const MyComponent = React.memo(function MyComponent({ name }) {
  return <div>{name}</div>;
});

// With custom comparison
const MyComponent = React.memo(function MyComponent(props) {
  return <div>{props.name}</div>;
}, (prevProps, nextProps) => {
  return prevProps.name === nextProps.name;
});
```

### useMemo for Expensive Calculations
```jsx
function ExpensiveComponent({ items }) {
  const expensiveValue = useMemo(() => {
    return items.reduce((sum, item) => sum + item.value, 0);
  }, [items]);
  
  return <div>Total: {expensiveValue}</div>;
}
```

### useCallback for Event Handlers
```jsx
function Parent({ items }) {
  const [count, setCount] = useState(0);
  
  // Without useCallback, this creates a new function on every render
  const handleClick = useCallback((id) => {
    console.log('Clicked item:', id);
  }, []);
  
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>Count: {count}</button>
      {items.map(item => (
        <Child key={item.id} item={item} onClick={handleClick} />
      ))}
    </div>
  );
}
```

### Lazy Loading
```jsx
import { lazy, Suspense } from 'react';

// Lazy load component
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <LazyComponent />
      </Suspense>
    </div>
  );
}
```

---

## 🏷️ TypeScript Integration

### Component Props
```tsx
interface Props {
  name: string;
  age?: number;
  onClick: (id: number) => void;
  children: React.ReactNode;
}

const MyComponent: React.FC<Props> = ({ name, age = 0, onClick, children }) => {
  return (
    <div>
      <h1>{name} ({age})</h1>
      <button onClick={() => onClick(1)}>Click me</button>
      {children}
    </div>
  );
};
```

### State Types
```tsx
// Simple state
const [count, setCount] = useState<number>(0);
const [name, setName] = useState<string>('');

// Object state
interface User {
  id: number;
  name: string;
  email: string;
}

const [user, setUser] = useState<User | null>(null);

// Array state
const [items, setItems] = useState<string[]>([]);
```

### Event Types
```tsx
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  console.log('Clicked');
};

const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
};
```

### Ref Types
```tsx
const inputRef = useRef<HTMLInputElement>(null);
const divRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (inputRef.current) {
    inputRef.current.focus();
  }
}, []);
```

---

## 🐛 Debugging Commands

### React Developer Tools
```javascript
// In browser console
$r // Selected component in React DevTools
$r.props // Component props
$r.state // Component state (class components)

// Component tree inspection
$ReactDebugCurrentFrame
```

### Console Debugging
```jsx
// Debug renders
function MyComponent(props) {
  console.log('MyComponent rendered with props:', props);
  return <div>{props.children}</div>;
}

// Debug effects
useEffect(() => {
  console.log('Effect triggered');
  return () => console.log('Effect cleanup');
}, [dependency]);

// Debug state changes
const [state, setState] = useState(initialState);
console.log('Current state:', state);
```

### Performance Debugging
```jsx
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log('Profiler:', { id, phase, actualDuration });
}

<Profiler id="App" onRender={onRenderCallback}>
  <App />
</Profiler>
```

---

## 📱 Common Component Patterns

### Higher-Order Component (HOC)
```jsx
function withLoading(WrappedComponent) {
  return function WithLoadingComponent(props) {
    if (props.isLoading) {
      return <div>Loading...</div>;
    }
    return <WrappedComponent {...props} />;
  };
}

// Usage
const ComponentWithLoading = withLoading(MyComponent);
```

### Render Props
```jsx
function DataProvider({ children }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData().then(setData);
  }, []);
  
  return children({ data, loading: !data });
}

// Usage
<DataProvider>
  {({ data, loading }) => (
    loading ? <div>Loading...</div> : <div>{data}</div>
  )}
</DataProvider>
```

### Compound Components
```jsx
function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  
  return (
    <div className="tabs">
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child, { 
          isActive: index === activeTab,
          onClick: () => setActiveTab(index)
        })
      )}
    </div>
  );
}

function Tab({ children, isActive, onClick }) {
  return (
    <button 
      className={`tab ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// Usage
<Tabs>
  <Tab>Tab 1</Tab>
  <Tab>Tab 2</Tab>
  <Tab>Tab 3</Tab>
</Tabs>
```

---

*This cheatsheet covers the most commonly used React patterns and APIs. Bookmark this page for quick reference during development!*
