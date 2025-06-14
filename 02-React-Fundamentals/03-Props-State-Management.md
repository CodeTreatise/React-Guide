# Props & State Management Deep Dive

## Table of Contents
1. [Props Fundamentals](#props-fundamentals)
2. [State Management](#state-management)
3. [Advanced Props Patterns](#advanced-props-patterns)
4. [State vs Props](#state-vs-props)
5. [Performance Considerations](#performance-considerations)
6. [Best Practices](#best-practices)

## Props Fundamentals

### What are Props?
Props (short for properties) are read-only inputs that components receive from their parent components.

```jsx
// Basic prop passing
function Greeting({ name, age }) {
  return <h1>Hello {name}, you are {age} years old!</h1>;
}

// Usage
<Greeting name="Alice" age={25} />
```

### Prop Types and Validation

```jsx
{% raw %}
import PropTypes from 'prop-types';

function UserCard({ user, isOnline, onClick }) {
  return (
    <div className={`user-card ${isOnline ? 'online' : 'offline'}`}>
      <img src={user.avatar} alt={user.name} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={onClick}>Contact</button>
    </div>
  );
}

UserCard.propTypes = {
  user: PropTypes.shape({
    name: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired,
    avatar: PropTypes.string
  }).isRequired,
  isOnline: PropTypes.bool,
  onClick: PropTypes.func.isRequired
};

UserCard.defaultProps = {
  isOnline: false
};
{% endraw %}
```

### Default Props

```jsx
{% raw %}
// Method 1: defaultProps
function Button({ text, variant, size }) {
  return (
    <button className={`btn btn-${variant} btn-${size}`}>
      {text}
    </button>
  );
}

Button.defaultProps = {
  variant: 'primary',
  size: 'medium'
};

// Method 2: Default parameters
function Button({ text, variant = 'primary', size = 'medium' }) {
  return (
    <button className={`btn btn-${variant} btn-${size}`}>
      {text}
    </button>
  );
}
{% endraw %}
```

### Children Prop

```jsx
// Basic children usage
function Card({ children, title }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-content">
        {children}
      </div>
    </div>
  );
}

// Usage
<Card title="User Profile">
  <p>This is the card content</p>
  <button>Edit Profile</button>
</Card>

// Render props pattern
function DataProvider({ children, data }) {
  return children(data);
}

// Usage
<DataProvider data={users}>
  {(data) => (
    <ul>
      {data.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  )}
</DataProvider>
```

## State Management

### useState Hook Basics

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => setCount(0);
  
  return (
    <div>
      <h2>Count: {count}</h2>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

### Functional Updates

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  // Functional update - safer for async operations
  const increment = () => setCount(prevCount => prevCount + 1);
  const decrement = () => setCount(prevCount => prevCount - 1);
  
  // Multiple updates in sequence
  const incrementByFive = () => {
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
  };
  
  return (
    <div>
      <h2>Count: {count}</h2>
      <button onClick={increment}>+1</button>
      <button onClick={incrementByFive}>+5</button>
    </div>
  );
}
```

### Complex State Objects

```jsx
function UserForm() {
  const [user, setUser] = useState({
    name: '',
    email: '',
    age: '',
    preferences: {
      theme: 'light',
      notifications: true
    }
  });
  
  const updateUser = (field, value) => {
    setUser(prevUser => ({
      ...prevUser,
      [field]: value
    }));
  };
  
  const updatePreference = (preference, value) => {
    setUser(prevUser => ({
      ...prevUser,
      preferences: {
        ...prevUser.preferences,
        [preference]: value
      }
    }));
  };
  
  return (
    <form>
      <input
        value={user.name}
        onChange={(e) => updateUser('name', e.target.value)}
        placeholder="Name"
      />
      <input
        value={user.email}
        onChange={(e) => updateUser('email', e.target.value)}
        placeholder="Email"
      />
      <select
        value={user.preferences.theme}
        onChange={(e) => updatePreference('theme', e.target.value)}
      >
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
    </form>
  );
}
```

### State with Arrays

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
            <span
              style={{
                textDecoration: todo.completed ? 'line-through' : 'none'
              }}
              onClick={() => toggleTodo(todo.id)}
            >
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

## Advanced Props Patterns

### Prop Drilling and Solutions

```jsx
// Problem: Prop drilling
function App() {
  const [user, setUser] = useState({ name: 'John', role: 'admin' });
  
  return <Header user={user} setUser={setUser} />;
}

function Header({ user, setUser }) {
  return <Navigation user={user} setUser={setUser} />;
}

function Navigation({ user, setUser }) {
  return <UserMenu user={user} setUser={setUser} />;
}

function UserMenu({ user, setUser }) {
  return (
    <div>
      <span>Welcome, {user.name}</span>
      <button onClick={() => setUser({ ...user, name: 'Jane' })}>
        Change Name
      </button>
    </div>
  );
}

// Solution 1: Component Composition
function App() {
  const [user, setUser] = useState({ name: 'John', role: 'admin' });
  
  return (
    <Header>
      <Navigation>
        <UserMenu user={user} setUser={setUser} />
      </Navigation>
    </Header>
  );
}

function Header({ children }) {
  return <header>{children}</header>;
}

function Navigation({ children }) {
  return <nav>{children}</nav>;
}
```

### Compound Components Pattern

```jsx
{% raw %}
function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  
  return (
    <div className="tabs">
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child, { activeTab, setActiveTab, index })
      )}
    </div>
  );
}

function TabList({ children, activeTab, setActiveTab }) {
  return (
    <div className="tab-list">
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child, { activeTab, setActiveTab, index })
      )}
    </div>
  );
}

function Tab({ children, index, activeTab, setActiveTab }) {
  return (
    <button
      className={`tab ${activeTab === index ? 'active' : ''}`}
      onClick={() => setActiveTab(index)}
    >
      {children}
    </button>
  );
}

function TabPanel({ children, index, activeTab }) {
  return activeTab === index ? <div className="tab-panel">{children}</div> : null;
}

// Usage
<Tabs defaultTab={0}>
  <TabList>
    <Tab>Tab 1</Tab>
    <Tab>Tab 2</Tab>
    <Tab>Tab 3</Tab>
  </TabList>
  <TabPanel>Content for Tab 1</TabPanel>
  <TabPanel>Content for Tab 2</TabPanel>
  <TabPanel>Content for Tab 3</TabPanel>
</Tabs>
{% endraw %}
```

### Higher-Order Components (HOCs)

```jsx
function withLoading(WrappedComponent) {
  return function WithLoadingComponent({ isLoading, ...props }) {
    if (isLoading) {
      return <div>Loading...</div>;
    }
    
    return <WrappedComponent {...props} />;
  };
}

// Usage
const UserListWithLoading = withLoading(UserList);

function App() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    fetchUsers().then(data => {
      setUsers(data);
      setIsLoading(false);
    });
  }, []);
  
  return <UserListWithLoading users={users} isLoading={isLoading} />;
}
```

## State vs Props

### Key Differences

| Aspect | Props | State |
|--------|-------|-------|
| Mutability | Immutable | Mutable |
| Ownership | Parent component | Component itself |
| Purpose | Pass data down | Manage component data |
| Updates | Parent re-renders | setState triggers re-render |

### When to Use Each

```jsx
// Props: For data passed from parent
function UserProfile({ user, onEdit, isEditing }) {
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      {isEditing && <EditForm user={user} onSave={onEdit} />}
    </div>
  );
}

// State: For component's internal data
function EditForm({ user, onSave }) {
  const [formData, setFormData] = useState(user);
  const [errors, setErrors] = useState({});
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSave(formData);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

## Performance Considerations

### Avoid Unnecessary Re-renders

```jsx
// Problem: New object created on every render
function Parent() {
  const [count, setCount] = useState(0);
  
  return (
    <Child 
      data={{ value: count }} // New object every render
      onClick={() => setCount(count + 1)} // New function every render
    />
  );
}

// Solution: Use useMemo and useCallback
function Parent() {
  const [count, setCount] = useState(0);
  
  const data = useMemo(() => ({ value: count }), [count]);
  const handleClick = useCallback(() => setCount(prev => prev + 1), []);
  
  return <Child data={data} onClick={handleClick} />;
}

// Even better: Lift state up or use context for shared state
```

### React.memo for Props Optimization

```jsx
const ExpensiveComponent = React.memo(function ExpensiveComponent({ 
  data, 
  onUpdate 
}) {
  console.log('ExpensiveComponent rendered');
  
  return (
    <div>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function
  return prevProps.data.length === nextProps.data.length &&
         prevProps.onUpdate === nextProps.onUpdate;
});
```

## Best Practices

### 1. Props Naming and Structure

```jsx
// Good: Descriptive prop names
<UserCard 
  user={user}
  isSelected={selectedUserId === user.id}
  onSelect={handleUserSelect}
  showActions={userRole === 'admin'}
/>

// Bad: Vague prop names
<UserCard 
  data={user}
  flag={selectedUserId === user.id}
  callback={handleUserSelect}
  bool={userRole === 'admin'}
/>
```

### 2. State Initialization

```jsx
// Good: Initialize with proper types
const [user, setUser] = useState({
  name: '',
  email: '',
  preferences: {}
});

const [items, setItems] = useState([]);
const [isLoading, setIsLoading] = useState(true);

// Good: Lazy initial state for expensive computations
const [expensiveValue, setExpensiveValue] = useState(() => {
  return computeExpensiveValue();
});
```

### 3. State Updates

```jsx
// Good: Functional updates for state that depends on previous state
const increment = () => setCount(prev => prev + 1);

// Good: Proper object/array updates
const updateUser = (field, value) => {
  setUser(prev => ({ ...prev, [field]: value }));
};

const addItem = (item) => {
  setItems(prev => [...prev, item]);
};

// Bad: Direct mutations
const badUpdate = () => {
  user.name = 'New Name'; // Don't mutate directly
  setUser(user);
};
```

### 4. Component Design

```jsx
{% raw %}
// Good: Single responsibility
function UserAvatar({ src, alt, size = 'medium' }) {
  return (
    <img 
      src={src} 
      alt={alt} 
      className={`avatar avatar-${size}`}
    />
  );
}

function UserInfo({ name, email, role }) {
  return (
    <div className="user-info">
      <h3>{name}</h3>
      <p>{email}</p>
      <span className="role">{role}</span>
    </div>
  );
}

// Compose them together
function UserCard({ user, onEdit }) {
  return (
    <div className="user-card">
      <UserAvatar src={user.avatar} alt={user.name} />
      <UserInfo name={user.name} email={user.email} role={user.role} />
      <button onClick={() => onEdit(user.id)}>Edit</button>
    </div>
  );
}
{% endraw %}
```

### 5. Error Boundaries for Props

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
    console.error('Error caught by boundary:', error, errorInfo);
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
  <UserList users={users} />
</ErrorBoundary>
```

## Common Patterns and Examples

### Controlled vs Uncontrolled Components

```jsx
// Controlled Component
function ControlledInput({ value, onChange }) {
  return (
    <input 
      value={value} 
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

// Uncontrolled Component
function UncontrolledInput({ defaultValue, onSubmit }) {
  const inputRef = useRef(null);
  
  const handleSubmit = () => {
    onSubmit(inputRef.current.value);
  };
  
  return (
    <div>
      <input ref={inputRef} defaultValue={defaultValue} />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
```

### State Lifting Pattern

```jsx
function Parent() {
  const [selectedId, setSelectedId] = useState(null);
  const [items, setItems] = useState([]);
  
  return (
    <div>
      <ItemList 
        items={items}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />
      <ItemDetails 
        item={items.find(item => item.id === selectedId)}
      />
    </div>
  );
}

function ItemList({ items, selectedId, onSelect }) {
  return (
    <ul>
      {items.map(item => (
        <li 
          key={item.id}
          className={selectedId === item.id ? 'selected' : ''}
          onClick={() => onSelect(item.id)}
        >
          {item.name}
        </li>
      ))}
    </ul>
  );
}
```

This comprehensive guide covers the essential concepts of props and state management in React, providing practical examples and best practices for effective component design and data flow.