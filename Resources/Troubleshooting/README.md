# 🎯 React Problem Solving & Troubleshooting Guide

> **Common React issues, debugging strategies, and solutions**

---

## 📋 Table of Contents

1. [Common Error Messages](#common-error-messages)
2. [Performance Issues](#performance-issues)
3. [State Management Problems](#state-management-problems)
4. [Component Issues](#component-issues)
5. [Hooks Troubleshooting](#hooks-troubleshooting)
6. [Build & Deployment Issues](#build--deployment-issues)
7. [Testing Problems](#testing-problems)
8. [Debugging Strategies](#debugging-strategies)

---

## ❌ Common Error Messages

### "Cannot read property of undefined"
```javascript
// ❌ Problem
function UserProfile({ user }) {
  return <div>{user.name}</div>; // Error if user is undefined
}

// ✅ Solutions
// 1. Optional chaining
function UserProfile({ user }) {
  return <div>{user?.name}</div>;
}

// 2. Default props
function UserProfile({ user = {} }) {
  return <div>{user.name || 'Guest'}</div>;
}

// 3. Conditional rendering
function UserProfile({ user }) {
  if (!user) return <div>Loading...</div>;
  return <div>{user.name}</div>;
}

// 4. Loading state
function UserProfile({ user, loading }) {
  if (loading) return <div>Loading...</div>;
  if (!user) return <div>No user found</div>;
  return <div>{user.name}</div>;
}
```

### "Each child in a list should have a unique key prop"
```jsx
{% raw %}
// ❌ Problem
{items.map(item => (
  <div>{item.name}</div> // Missing key
))}

// ✅ Solutions
// 1. Use unique ID
{items.map(item => (
  <div key={item.id}>{item.name}</div>
))}

// 2. Use index as last resort
{items.map((item, index) => (
  <div key={index}>{item.name}</div>
))}

// 3. Composite key for nested data
{categories.map(category => (
  <div key={category.id}>
    {category.items.map(item => (
      <div key={`${category.id}-${item.id}`}>{item.name}</div>
    ))}
  </div>
))}
{% endraw %}
```

### "Cannot update a component while rendering a different component"
```jsx
// ❌ Problem - Setting state during render
function Parent() {
  const [count, setCount] = useState(0);
  
  return (
    <Child onMount={() => setCount(1)} /> // Called during render
  );
}

// ✅ Solution - Use useEffect
function Parent() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    setCount(1);
  }, []);
  
  return <Child />;
}
```

### "Maximum update depth exceeded"
```jsx
// ❌ Problem - Infinite re-renders
function Component() {
  const [count, setCount] = useState(0);
  
  setCount(count + 1); // Called on every render
  
  return <div>{count}</div>;
}

// ✅ Solution - Move to event handler or useEffect
function Component() {
  const [count, setCount] = useState(0);
  
  const handleClick = () => {
    setCount(count + 1);
  };
  
  return <div onClick={handleClick}>{count}</div>;
}
```

### "Can't perform a React state update on an unmounted component"
```jsx
// ❌ Problem - State update after unmount
function Component() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData().then(setData); // Component might unmount before this resolves
  }, []);
  
  return <div>{data}</div>;
}

// ✅ Solution - Check if mounted
function Component() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    let isMounted = true;
    
    fetchData().then(result => {
      if (isMounted) {
        setData(result);
      }
    });
    
    return () => {
      isMounted = false;
    };
  }, []);
  
  return <div>{data}</div>;
}

// ✅ Alternative - Use AbortController
function Component() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const controller = new AbortController();
    
    fetch('/api/data', { signal: controller.signal })
      .then(response => response.json())
      .then(setData)
      .catch(error => {
        if (error.name !== 'AbortError') {
          console.error('Fetch error:', error);
        }
      });
    
    return () => controller.abort();
  }, []);
  
  return <div>{data}</div>;
}
```

---

## 🐌 Performance Issues

### Unnecessary Re-renders
```jsx
// ❌ Problem - Parent re-renders cause child re-renders
function Parent() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  return (
    <div>
      <input value={name} onChange={e => setName(e.target.value)} />
      <button onClick={() => setCount(count + 1)}>Count: {count}</button>
      <ExpensiveChild /> {/* Re-renders when count or name changes */}
    </div>
  );
}

// ✅ Solution - Use React.memo
const ExpensiveChild = React.memo(function ExpensiveChild() {
  console.log('ExpensiveChild rendered');
  return <div>Expensive operations...</div>;
});

// ✅ Solution - Split components
function Parent() {
  return (
    <div>
      <NameInput />
      <Counter />
      <ExpensiveChild />
    </div>
  );
}

function NameInput() {
  const [name, setName] = useState('');
  return <input value={name} onChange={e => setName(e.target.value)} />;
}

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>;
}
```

### Expensive Calculations in Render
```jsx
{% raw %}
// ❌ Problem - Expensive calculation on every render
function Component({ items }) {
  const total = items.reduce((sum, item) => sum + item.price, 0); // Runs every render
  
  return <div>Total: ${total}</div>;
}

// ✅ Solution - Use useMemo
function Component({ items }) {
  const total = useMemo(() => {
    return items.reduce((sum, item) => sum + item.price, 0);
  }, [items]);
  
  return <div>Total: ${total}</div>;
}
{% endraw %}
```

### Function Recreation in JSX
```jsx
// ❌ Problem - New function on every render
function TodoList({ todos, onToggle }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <button onClick={() => onToggle(todo.id)}>
            {todo.text}
          </button>
        </li>
      ))}
    </ul>
  );
}

// ✅ Solution - useCallback
function TodoList({ todos, onToggle }) {
  const handleToggle = useCallback((id) => () => {
    onToggle(id);
  }, [onToggle]);
  
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <button onClick={handleToggle(todo.id)}>
            {todo.text}
          </button>
        </li>
      ))}
    </ul>
  );
}
```

---

## 🔄 State Management Problems

### Stale Closure
```jsx
// ❌ Problem - Stale closure in useEffect
function Counter() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCount(count + 1); // Always uses initial count value (0)
    }, 1000);
    
    return () => clearInterval(interval);
  }, []); // Empty dependency array
  
  return <div>{count}</div>;
}

// ✅ Solution 1 - Functional update
function Counter() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCount(prevCount => prevCount + 1);
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return <div>{count}</div>;
}

// ✅ Solution 2 - Include in dependencies
function Counter() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCount(count + 1);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [count]); // Include count in dependencies
  
  return <div>{count}</div>;
}
```

### State Mutation
```jsx
// ❌ Problem - Direct state mutation
function TodoList() {
  const [todos, setTodos] = useState([]);
  
  const addTodo = (text) => {
    todos.push({ id: Date.now(), text }); // Mutation!
    setTodos(todos);
  };
  
  const toggleTodo = (id) => {
    const todo = todos.find(t => t.id === id);
    todo.completed = !todo.completed; // Mutation!
    setTodos(todos);
  };
}

// ✅ Solution - Immutable updates
function TodoList() {
  const [todos, setTodos] = useState([]);
  
  const addTodo = (text) => {
    setTodos([...todos, { id: Date.now(), text, completed: false }]);
  };
  
  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };
}
```

### Race Conditions
```jsx
// ❌ Problem - Race condition with async state updates
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId).then(setUser); // Race condition if userId changes quickly
  }, [userId]);
  
  return user ? <div>{user.name}</div> : <div>Loading...</div>;
}

// ✅ Solution - Cleanup and ignore stale responses
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    let ignore = false;
    
    fetchUser(userId).then(userData => {
      if (!ignore) {
        setUser(userData);
      }
    });
    
    return () => {
      ignore = true;
    };
  }, [userId]);
  
  return user ? <div>{user.name}</div> : <div>Loading...</div>;
}
```

---

## 🧩 Component Issues

### Props Drilling
```jsx
// ❌ Problem - Passing props through multiple levels
function App() {
  const [user, setUser] = useState(null);
  
  return <Layout user={user} setUser={setUser} />;
}

function Layout({ user, setUser }) {
  return (
    <div>
      <Header user={user} setUser={setUser} />
      <Main user={user} />
    </div>
  );
}

function Header({ user, setUser }) {
  return <UserMenu user={user} setUser={setUser} />;
}

// ✅ Solution - Context API
const UserContext = createContext();

function App() {
  const [user, setUser] = useState(null);
  
  return (
    <UserContext.Provider value={{ user, setUser }}>
      <Layout />
    </UserContext.Provider>
  );
}

function Layout() {
  return (
    <div>
      <Header />
      <Main />
    </div>
  );
}

function UserMenu() {
  const { user, setUser } = useContext(UserContext);
  // Use user and setUser directly
}
```

### Conditional Hooks
```jsx
// ❌ Problem - Conditional hook usage
function Component({ showFeature }) {
  if (showFeature) {
    const [count, setCount] = useState(0); // Breaks rules of hooks
  }
  
  return <div>Component</div>;
}

// ✅ Solution - Always call hooks, conditionally use values
function Component({ showFeature }) {
  const [count, setCount] = useState(0);
  
  if (showFeature) {
    // Use count here
  }
  
  return <div>Component</div>;
}

// ✅ Alternative - Separate components
function Component({ showFeature }) {
  return (
    <div>
      {showFeature ? <FeatureComponent /> : <RegularComponent />}
    </div>
  );
}

function FeatureComponent() {
  const [count, setCount] = useState(0);
  return <div>Feature with count: {count}</div>;
}
```

---

## 🎣 Hooks Troubleshooting

### useEffect Dependencies
```jsx
// ❌ Problem - Missing dependencies
function Component({ userId }) {
  const [user, setUser] = useState(null);
  
  const fetchUserData = async () => {
    const userData = await fetchUser(userId);
    setUser(userData);
  };
  
  useEffect(() => {
    fetchUserData(); // Missing fetchUserData in dependencies
  }, [userId]);
}

// ✅ Solution 1 - Include function in dependencies
function Component({ userId }) {
  const [user, setUser] = useState(null);
  
  const fetchUserData = useCallback(async () => {
    const userData = await fetchUser(userId);
    setUser(userData);
  }, [userId]);
  
  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);
}

// ✅ Solution 2 - Move function inside useEffect
function Component({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    const fetchUserData = async () => {
      const userData = await fetchUser(userId);
      setUser(userData);
    };
    
    fetchUserData();
  }, [userId]);
}
```

### Infinite useEffect Loop
```jsx
// ❌ Problem - Object/array in dependencies
function Component() {
  const [data, setData] = useState(null);
  const config = { timeout: 5000 }; // New object every render
  
  useEffect(() => {
    fetchData(config).then(setData);
  }, [config]); // Infinite loop!
}

// ✅ Solution 1 - Move object outside component
const config = { timeout: 5000 };

function Component() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData(config).then(setData);
  }, []); // No dependencies needed
}

// ✅ Solution 2 - useMemo for objects
function Component() {
  const [data, setData] = useState(null);
  
  const config = useMemo(() => ({ timeout: 5000 }), []);
  
  useEffect(() => {
    fetchData(config).then(setData);
  }, [config]);
}

// ✅ Solution 3 - Primitive dependencies
function Component({ timeout = 5000 }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData({ timeout }).then(setData);
  }, [timeout]);
}
```

---

## 🏗️ Build & Deployment Issues

### Import/Export Errors
```javascript
// ❌ Problem - Mixed import/export styles
// file1.js
export default function Component() {} // Default export
export const utils = {}; // Named export

// file2.js
import Component, utils from './file1'; // Wrong import

// ✅ Solution - Correct import syntax
import Component, { utils } from './file1';
// or
import Component from './file1';
import { utils } from './file1';
```

### Bundle Size Issues
```javascript
// ❌ Problem - Importing entire library
import _ from 'lodash'; // Imports entire lodash library
import { Button } from '@material-ui/core'; // Imports more than needed

// ✅ Solution - Tree shaking and specific imports
import debounce from 'lodash/debounce';
import Button from '@material-ui/core/Button';

// ✅ Using babel-plugin-import
// In .babelrc
{
  "plugins": [
    ["import", { "libraryName": "lodash", "libraryDirectory": "", "camel2DashComponentName": false }, "lodash"]
  ]
}
```

### Environment Variables
```javascript
// ❌ Problem - Environment variables not loading
console.log(process.env.API_URL); // undefined in production

// ✅ Solution - Proper naming and loading
// .env file
REACT_APP_API_URL=https://api.example.com

// Component
console.log(process.env.REACT_APP_API_URL);

// ✅ For Next.js
// next.config.js
module.exports = {
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
}
```

---

## 🧪 Testing Problems

### Testing Async Components
```jsx
// ❌ Problem - Not waiting for async operations
test('renders user data', () => {
  render(<UserProfile userId="123" />);
  expect(screen.getByText('John Doe')).toBeInTheDocument(); // Fails - data not loaded yet
});

// ✅ Solution - Wait for async operations
test('renders user data', async () => {
  render(<UserProfile userId="123" />);
  
  // Wait for the user data to load
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});

// ✅ Alternative - findBy queries (built-in waiting)
test('renders user data', async () => {
  render(<UserProfile userId="123" />);
  
  const userName = await screen.findByText('John Doe');
  expect(userName).toBeInTheDocument();
});
```

### Mocking API Calls
```javascript
// ❌ Problem - Not mocking external dependencies
test('fetches and displays data', async () => {
  render(<DataComponent />);
  // This will make actual API calls!
});

// ✅ Solution - Mock fetch
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/data', (req, res, ctx) => {
    return res(ctx.json({ name: 'John Doe' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('fetches and displays data', async () => {
  render(<DataComponent />);
  
  const userName = await screen.findByText('John Doe');
  expect(userName).toBeInTheDocument();
});
```

---

## 🔍 Debugging Strategies

### React Developer Tools
```javascript
// Access selected component in browser console
$r // Selected component
$r.props // Component props
$r.state // Component state (class components)

// Find component by name
$ReactDebugCurrentFrame
```

### Console Debugging
```jsx
{% raw %}
function Component(props) {
  // Debug props
  console.log('Component props:', props);
  
  // Debug render count
  const renderCount = useRef(0);
  renderCount.current++;
  console.log(`Component rendered ${renderCount.current} times`);
  
  // Debug state changes
  const [state, setState] = useState(initialState);
  
  useEffect(() => {
    console.log('State changed:', state);
  }, [state]);
  
  return <div>Component content</div>;
}
{% endraw %}
```

### Performance Debugging
```jsx
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration, baseDuration, startTime, commitTime) {
  console.log('Profiler:', {
    id,
    phase, // 'mount' or 'update'
    actualDuration, // Time spent rendering
    baseDuration, // Estimated time without memoization
    startTime,
    commitTime
  });
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Header />
      <Main />
    </Profiler>
  );
}
```

### Network Debugging
```javascript
// Debug fetch requests
const originalFetch = window.fetch;
window.fetch = (...args) => {
  console.log('Fetch request:', args);
  return originalFetch(...args)
    .then(response => {
      console.log('Fetch response:', response);
      return response;
    });
};
```

---

## 🚀 Quick Fixes Checklist

### Component Not Rendering
- [ ] Check if component is exported/imported correctly
- [ ] Verify component is called with proper JSX syntax (`<Component />`)
- [ ] Check for JavaScript errors in console
- [ ] Ensure component returns valid JSX
- [ ] Verify parent component is rendering

### State Not Updating
- [ ] Check if state setter is called correctly
- [ ] Verify you're not mutating state directly
- [ ] Check useEffect dependencies
- [ ] Look for stale closure issues
- [ ] Ensure async operations are handled properly

### Props Not Passed
- [ ] Check prop names match between parent and child
- [ ] Verify props are passed with correct syntax
- [ ] Check for typos in prop names
- [ ] Ensure parent component has the data to pass
- [ ] Use React Developer Tools to inspect props

### Performance Issues
- [ ] Use React.memo for pure components
- [ ] Wrap callbacks in useCallback
- [ ] Memoize expensive calculations with useMemo
- [ ] Check for unnecessary re-renders
- [ ] Profile with React Developer Tools

### Build Errors
- [ ] Check import/export syntax
- [ ] Verify all dependencies are installed
- [ ] Clear node_modules and reinstall
- [ ] Check for TypeScript errors
- [ ] Verify environment variables are set

---

*This troubleshooting guide covers the most common React issues. When debugging, start with the console errors and React Developer Tools for the fastest resolution.*
