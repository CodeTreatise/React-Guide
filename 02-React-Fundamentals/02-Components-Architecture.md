# React Components Architecture

## Table of Contents
1. [Introduction to Components](#introduction-to-components)
2. [Functional vs Class Components](#functional-vs-class-components)
3. [Component Composition](#component-composition)
4. [Component Architecture Patterns](#component-architecture-patterns)
5. [Higher-Order Components (HOCs)](#higher-order-components-hocs)
6. [Render Props Pattern](#render-props-pattern)
7. [Component Design Principles](#component-design-principles)
8. [Performance Considerations](#performance-considerations)
9. [Component Testing Architecture](#component-testing-architecture)
10. [Best Practices](#best-practices)

---

## Introduction to Components

Components are the building blocks of React applications. They are reusable pieces of UI that can manage their own state and lifecycle.

### What is a Component?

A React component is a JavaScript function or class that returns JSX elements describing what should appear on the screen.

```jsx
// Simple functional component
function Welcome(props) {
  return <h1>Hello, {props.name}!</h1>;
}

// Using the component
function App() {
  return (
    <div>
      <Welcome name="Alice" />
      <Welcome name="Bob" />
      <Welcome name="Charlie" />
    </div>
  );
}
```

### Component Hierarchy

React applications are built as a tree of components, where:
- **Root Component**: The top-level component (usually `App`)
- **Container Components**: Manage state and logic
- **Presentational Components**: Focus on how things look

```jsx
// Component hierarchy example
App
├── Header
│   ├── Logo
│   └── Navigation
├── Main
│   ├── Sidebar
│   └── Content
│       ├── Article
│       └── Comments
│           └── Comment
└── Footer
```

---

## Functional vs Class Components

### Functional Components (Recommended)

Modern React development primarily uses functional components with hooks.

```jsx
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId)
      .then(userData => {
        setUser(userData);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="user-profile">
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

### Class Components (Legacy)

Class components were the primary way to create stateful components before hooks.

```jsx
import React, { Component } from 'react';

class UserProfile extends Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
      loading: true
    };
  }

  componentDidMount() {
    this.fetchUser(this.props.userId);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser(this.props.userId);
    }
  }

  fetchUser = (userId) => {
    fetchUser(userId)
      .then(userData => {
        this.setState({ user: userData, loading: false });
      });
  }

  render() {
    const { user, loading } = this.state;
    
    if (loading) return <div>Loading...</div>;
    
    return (
      <div className="user-profile">
        <img src={user.avatar} alt={user.name} />
        <h2>{user.name}</h2>
        <p>{user.email}</p>
      </div>
    );
  }
}
```

### Comparison Table

| Feature | Functional Components | Class Components |
|---------|----------------------|------------------|
| Syntax | Simpler, more concise | More verbose |
| State Management | useState hook | this.state |
| Lifecycle Methods | useEffect hook | Built-in methods |
| Performance | Better (with hooks) | Good |
| Testing | Easier to test | More complex |
| Reusability | Higher | Lower |
| Learning Curve | Easier | Steeper |

---

## Component Composition

Component composition is the practice of combining smaller components to build larger, more complex components.

### Composition vs Inheritance

React recommends composition over inheritance for code reuse.

```jsx
// Good: Composition
function Dialog({ title, children, footer }) {
  return (
    <div className="dialog">
      <div className="dialog-header">
        <h3>{title}</h3>
      </div>
      <div className="dialog-body">
        {children}
      </div>
      {footer && (
        <div className="dialog-footer">
          {footer}
        </div>
      )}
    </div>
  );
}

function ConfirmDialog({ onConfirm, onCancel }) {
  return (
    <Dialog 
      title="Confirm Action"
      footer={
        <div>
          <button onClick={onCancel}>Cancel</button>
          <button onClick={onConfirm}>Confirm</button>
        </div>
      }
    >
      <p>Are you sure you want to perform this action?</p>
    </Dialog>
  );
}
```

### Slot Pattern

Using children prop to create flexible, reusable components.

```jsx
{% raw %}
function Card({ header, children, footer, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {header && <div className="card-header">{header}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

// Usage
function ProductCard({ product }) {
  return (
    <Card
      header={<h3>{product.name}</h3>}
      footer={
        <div>
          <span>${product.price}</span>
          <button>Add to Cart</button>
        </div>
      }
    >
      <img src={product.image} alt={product.name} />
      <p>{product.description}</p>
    </Card>
  );
}
{% endraw %}
```

### Compound Components

Components that work together to form a cohesive UI.

```jsx
{% raw %}
function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  
  return (
    <div className="tabs">
      <div className="tab-list">
        {React.Children.map(children, (child, index) => (
          <button
            key={index}
            className={`tab ${index === activeTab ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            {child.props.label}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {React.Children.toArray(children)[activeTab]}
      </div>
    </div>
  );
}

function TabPanel({ children, label }) {
  return <div>{children}</div>;
}

// Usage
function App() {
  return (
    <Tabs>
      <TabPanel label="Tab 1">
        <h3>Content for Tab 1</h3>
        <p>This is the first tab content.</p>
      </TabPanel>
      <TabPanel label="Tab 2">
        <h3>Content for Tab 2</h3>
        <p>This is the second tab content.</p>
      </TabPanel>
    </Tabs>
  );
}
{% endraw %}
```

---

## Component Architecture Patterns

### Container and Presentational Components

Separate components that manage data from components that render UI.

```jsx
// Presentational Component
function UserList({ users, onUserSelect, loading }) {
  if (loading) return <div>Loading users...</div>;
  
  return (
    <ul className="user-list">
      {users.map(user => (
        <li key={user.id} onClick={() => onUserSelect(user)}>
          <img src={user.avatar} alt={user.name} />
          <span>{user.name}</span>
        </li>
      ))}
    </ul>
  );
}

// Container Component
function UserListContainer() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    fetchUsers()
      .then(userData => {
        setUsers(userData);
        setLoading(false);
      });
  }, []);

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    // Additional logic for user selection
  };

  return (
    <div>
      <UserList 
        users={users}
        loading={loading}
        onUserSelect={handleUserSelect}
      />
      {selectedUser && <UserDetails user={selectedUser} />}
    </div>
  );
}
```

### Provider Pattern

Use React Context to provide data to component trees.

```jsx
{% raw %}
// Create context
const ThemeContext = createContext();

// Provider component
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Hook for consuming context
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// Component using the context
function Header() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <header className={`header ${theme}`}>
      <h1>My App</h1>
      <button onClick={toggleTheme}>
        Switch to {theme === 'light' ? 'dark' : 'light'} mode
      </button>
    </header>
  );
}
{% endraw %}
```

### Atomic Design Pattern

Organize components into a hierarchy based on their complexity.

```jsx
{% raw %}
// Atoms - Basic building blocks
function Button({ children, variant = 'primary', ...props }) {
  return (
    <button className={`btn btn-${variant}`} {...props}>
      {children}
    </button>
  );
}

function Input({ label, error, ...props }) {
  return (
    <div className="input-group">
      {label && <label>{label}</label>}
      <input {...props} />
      {error && <span className="error">{error}</span>}
    </div>
  );
}

// Molecules - Simple groups of atoms
function SearchBox({ onSearch, placeholder = "Search..." }) {
  const [query, setQuery] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="search-box">
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
      />
      <Button type="submit">Search</Button>
    </form>
  );
}

// Organisms - Complex components
function ProductGrid({ products, onSearch }) {
  return (
    <div className="product-grid">
      <SearchBox onSearch={onSearch} />
      <div className="products">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}
{% endraw %}
```

---

## Higher-Order Components (HOCs)

HOCs are functions that take a component and return a new component with additional functionality.

### Basic HOC Pattern

```jsx
function withLoading(WrappedComponent) {
  return function WithLoadingComponent(props) {
    if (props.loading) {
      return <div className="loading">Loading...</div>;
    }
    
    return <WrappedComponent {...props} />;
  };
}

// Usage
const UserListWithLoading = withLoading(UserList);

function App() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  return (
    <UserListWithLoading 
      users={users} 
      loading={loading} 
    />
  );
}
```

### Authentication HOC

```jsx
function withAuth(WrappedComponent) {
  return function WithAuthComponent(props) {
    const { user, loading } = useAuth();
    
    if (loading) {
      return <div>Checking authentication...</div>;
    }
    
    if (!user) {
      return <Redirect to="/login" />;
    }
    
    return <WrappedComponent {...props} user={user} />;
  };
}

// Usage
const ProtectedProfile = withAuth(UserProfile);
```

### HOC with Configuration

```jsx
function withErrorBoundary(fallbackComponent) {
  return function(WrappedComponent) {
    return class extends Component {
      constructor(props) {
        super(props);
        this.state = { hasError: false };
      }

      static getDerivedStateFromError(error) {
        return { hasError: true };
      }

      componentDidCatch(error, errorInfo) {
        console.error('Error caught by HOC:', error, errorInfo);
      }

      render() {
        if (this.state.hasError) {
          return fallbackComponent || <div>Something went wrong.</div>;
        }

        return <WrappedComponent {...this.props} />;
      }
    };
  };
}

// Usage
const SafeUserProfile = withErrorBoundary(
  <div>Error loading user profile</div>
)(UserProfile);
```

---

## Render Props Pattern

A technique for sharing code between components using a prop whose value is a function.

### Basic Render Props

```jsx
function DataFetcher({ url, render }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(response => response.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, [url]);

  return render({ data, loading, error });
}

// Usage
function App() {
  return (
    <DataFetcher
      url="/api/users"
      render={({ data, loading, error }) => {
        if (loading) return <div>Loading...</div>;
        if (error) return <div>Error: {error.message}</div>;
        return (
          <ul>
            {data.map(user => (
              <li key={user.id}>{user.name}</li>
            ))}
          </ul>
        );
      }}
    />
  );
}
```

### Children as Function

```jsx
function MouseTracker({ children }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    setPosition({ x: e.clientX, y: e.clientY });
  };

  return (
    <div onMouseMove={handleMouseMove} style={{ height: '100vh' }}>
      {children(position)}
    </div>
  );
}

// Usage
function App() {
  return (
    <MouseTracker>
      {({ x, y }) => (
        <div>
          <h1>Mouse position:</h1>
          <p>X: {x}, Y: {y}</p>
        </div>
      )}
    </MouseTracker>
  );
}
```

---

## Component Design Principles

### Single Responsibility Principle

Each component should have one reason to change.

```jsx
// Bad: Multiple responsibilities
function UserDashboard({ userId }) {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  
  // Fetching logic, rendering logic, state management all mixed
  return (
    <div>
      {/* Complex JSX with multiple concerns */}
    </div>
  );
}

// Good: Separated responsibilities
function UserDashboard({ userId }) {
  return (
    <div className="dashboard">
      <UserProfile userId={userId} />
      <UserPosts userId={userId} />
      <UserNotifications userId={userId} />
    </div>
  );
}
```

### Open/Closed Principle

Components should be open for extension but closed for modification.

```jsx
{% raw %}
// Base button component
function Button({ variant = 'primary', size = 'medium', children, ...props }) {
  const classes = `btn btn-${variant} btn-${size}`;
  
  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}

// Extended without modifying the base
function IconButton({ icon, children, ...props }) {
  return (
    <Button {...props}>
      <span className="icon">{icon}</span>
      {children}
    </Button>
  );
}
{% endraw %}
```

### Dependency Inversion

Depend on abstractions, not concretions.

```jsx
// Bad: Tightly coupled to specific API
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Directly calling specific API
    fetch('/api/users')
      .then(response => response.json())
      .then(setUsers);
  }, []);

  return (
    <ul>
      {users.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}

// Good: Injected dependency
function UserList({ userService }) {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    userService.getUsers().then(setUsers);
  }, [userService]);

  return (
    <ul>
      {users.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}
```

---

## Performance Considerations

### React.memo for Functional Components

Prevent unnecessary re-renders of functional components.

```jsx
const UserCard = React.memo(function UserCard({ user, onSelect }) {
  console.log('UserCard rendering for:', user.name);
  
  return (
    <div className="user-card" onClick={() => onSelect(user)}>
      <img src={user.avatar} alt={user.name} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
});

// Custom comparison function
const UserCardOptimized = React.memo(UserCard, (prevProps, nextProps) => {
  return prevProps.user.id === nextProps.user.id &&
         prevProps.user.name === nextProps.user.name;
});
```

### useMemo and useCallback

Optimize expensive calculations and function references.

```jsx
function UserAnalytics({ users, filters }) {
  // Memoize expensive calculation
  const analytics = useMemo(() => {
    return calculateUserAnalytics(users, filters);
  }, [users, filters]);

  // Memoize callback to prevent child re-renders
  const handleUserClick = useCallback((user) => {
    console.log('User clicked:', user.name);
    // Handle user click
  }, []);

  return (
    <div>
      <AnalyticsChart data={analytics} />
      <UserList users={users} onUserClick={handleUserClick} />
    </div>
  );
}
```

### Lazy Loading Components

Load components only when needed.

```jsx
import { Suspense, lazy } from 'react';

// Lazy load heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));
const DataTable = lazy(() => import('./DataTable'));

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div>
      <nav>
        <button onClick={() => setActiveTab('overview')}>Overview</button>
        <button onClick={() => setActiveTab('charts')}>Charts</button>
        <button onClick={() => setActiveTab('data')}>Data</button>
      </nav>
      
      <Suspense fallback={<div>Loading...</div>}>
        {activeTab === 'charts' && <HeavyChart />}
        {activeTab === 'data' && <DataTable />}
      </Suspense>
    </div>
  );
}
```

---

## Component Testing Architecture

### Testing Strategies

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  const mockUser = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    avatar: '/avatar.jpg'
  };

  test('renders user information', () => {
    render(<UserCard user={mockUser} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByAltText('John Doe')).toHaveAttribute('src', '/avatar.jpg');
  });

  test('calls onSelect when clicked', () => {
    const mockOnSelect = jest.fn();
    render(<UserCard user={mockUser} onSelect={mockOnSelect} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(mockOnSelect).toHaveBeenCalledWith(mockUser);
  });
});
```

### Testing Component Composition

```jsx
import { render, screen } from '@testing-library/react';
import { Dialog } from './Dialog';

describe('Dialog', () => {
  test('renders with custom header and footer', () => {
    render(
      <Dialog
        title="Test Dialog"
        footer={<button>Custom Footer</button>}
      >
        <p>Dialog content</p>
      </Dialog>
    );

    expect(screen.getByText('Test Dialog')).toBeInTheDocument();
    expect(screen.getByText('Dialog content')).toBeInTheDocument();
    expect(screen.getByText('Custom Footer')).toBeInTheDocument();
  });
});
```

---

## Best Practices

### Component Organization

```
src/
├── components/
│   ├── common/          # Reusable components
│   │   ├── Button/
│   │   ├── Input/
│   │   └── Modal/
│   ├── layout/          # Layout components
│   │   ├── Header/
│   │   ├── Sidebar/
│   │   └── Footer/
│   └── features/        # Feature-specific components
│       ├── UserProfile/
│       ├── ProductList/
│       └── ShoppingCart/
```

### Component File Structure

```
Button/
├── index.js             # Export file
├── Button.jsx           # Main component
├── Button.test.js       # Tests
├── Button.stories.js    # Storybook stories
└── Button.module.css    # Styles
```

### Naming Conventions

```jsx
// Component names: PascalCase
function UserProfile() { }
function ShoppingCart() { }

// Props: camelCase
function Button({ onClick, isDisabled, variant }) { }

// Event handlers: handle + Action
const handleClick = () => { };
const handleSubmit = () => { };
const handleInputChange = () => { };
```

### PropTypes and TypeScript

```jsx
import PropTypes from 'prop-types';

function UserCard({ user, onSelect, showEmail = true }) {
  return (
    <div onClick={() => onSelect(user)}>
      <h3>{user.name}</h3>
      {showEmail && <p>{user.email}</p>}
    </div>
  );
}

UserCard.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
  showEmail: PropTypes.bool
};
```

### TypeScript Version

```tsx
interface User {
  id: number;
  name: string;
  email: string;
  avatar?: string;
}

interface UserCardProps {
  user: User;
  onSelect: (user: User) => void;
  showEmail?: boolean;
}

function UserCard({ user, onSelect, showEmail = true }: UserCardProps) {
  return (
    <div onClick={() => onSelect(user)}>
      <h3>{user.name}</h3>
      {showEmail && <p>{user.email}</p>}
    </div>
  );
}
```

### Error Boundaries

```jsx
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            {this.state.error && this.state.error.toString()}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <UserDashboard />
    </ErrorBoundary>
  );
}
```

---

## Summary

Components are the foundation of React applications. Understanding component architecture patterns, composition techniques, and best practices is crucial for building maintainable and scalable React applications.

### Key Takeaways

1. **Favor functional components** with hooks over class components
2. **Use composition over inheritance** for code reuse
3. **Separate concerns** between container and presentational components
4. **Optimize performance** with React.memo, useMemo, and useCallback
5. **Follow naming conventions** and organize components logically
6. **Write tests** for component behavior and interactions
7. **Use TypeScript or PropTypes** for type safety
8. **Implement error boundaries** to handle component errors gracefully

### Component Architecture Checklist

- [ ] Single responsibility principle followed
- [ ] Props are well-defined and typed
- [ ] Component is reusable and composable
- [ ] Performance optimizations applied where needed
- [ ] Error handling implemented
- [ ] Tests written for critical functionality
- [ ] Accessibility considerations included
- [ ] Documentation and examples provided