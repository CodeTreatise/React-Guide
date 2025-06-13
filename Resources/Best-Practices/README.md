# 🏆 React Best Practices & Style Guide

> **Professional coding standards and conventions for React development**

---

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Component Organization](#component-organization)
3. [Naming Conventions](#naming-conventions)
4. [Code Style Guidelines](#code-style-guidelines)
5. [State Management](#state-management)
6. [Performance Best Practices](#performance-best-practices)
7. [Security Guidelines](#security-guidelines)
8. [Accessibility Standards](#accessibility-standards)

---

## 📁 Project Structure

### Recommended Folder Structure
```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components (Button, Input, etc.)
│   ├── forms/           # Form-specific components
│   └── layout/          # Layout components (Header, Footer, etc.)
├── pages/               # Page-level components
├── hooks/               # Custom hooks
├── context/             # React context providers
├── services/            # API calls and external services
├── utils/               # Utility functions
├── constants/           # Application constants
├── types/               # TypeScript type definitions
├── styles/              # Global styles and themes
├── assets/              # Static assets (images, fonts, etc.)
└── tests/               # Test utilities and setup
```

### File Naming Conventions
```
// Component files - PascalCase
UserProfile.tsx
UserProfile.test.tsx
UserProfile.stories.tsx
UserProfile.module.css

// Hook files - camelCase starting with 'use'
useLocalStorage.ts
useDebounce.ts

// Utility files - camelCase
dateUtils.ts
apiHelpers.ts

// Constant files - camelCase
apiEndpoints.ts
appConfig.ts
```

---

## 🧩 Component Organization

### Component File Structure
```tsx
// 1. Imports - External libraries first, then internal
import React, { useState, useEffect } from 'react';
import { Button } from '@material-ui/core';

import { useApi } from '../hooks/useApi';
import { formatDate } from '../utils/dateUtils';
import styles from './UserProfile.module.css';

// 2. Types and Interfaces
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

// 3. Component Definition
export const UserProfile: React.FC<UserProfileProps> = ({ 
  userId, 
  onUpdate 
}) => {
  // Hooks at the top
  const [isEditing, setIsEditing] = useState(false);
  const { data: user, loading, error } = useApi<User>(`/users/${userId}`);

  // Event handlers
  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = (updatedUser: User) => {
    setIsEditing(false);
    onUpdate?.(updatedUser);
  };

  // Early returns for loading/error states
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return <div>User not found</div>;

  // Main render
  return (
    <div className={styles.container}>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <p>Member since: {formatDate(user.createdAt)}</p>
      
      {isEditing ? (
        <UserEditForm user={user} onSave={handleSave} />
      ) : (
        <Button onClick={handleEdit}>Edit Profile</Button>
      )}
    </div>
  );
};

// 4. Default export (if needed)
export default UserProfile;
```

### Component Composition Patterns
```tsx
// ✅ Good - Small, focused components
function UserCard({ user }) {
  return (
    <div className="user-card">
      <UserAvatar src={user.avatar} alt={user.name} />
      <UserInfo user={user} />
      <UserActions userId={user.id} />
    </div>
  );
}

// ✅ Good - Compound components
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
  <Tab>Profile</Tab>
  <Tab>Settings</Tab>
  <Tab>Activity</Tab>
</Tabs>
```

---

## 🏷️ Naming Conventions

### Components
```tsx
// ✅ PascalCase for components
const UserProfile = () => {};
const NavigationMenu = () => {};
const ProductCard = () => {};

// ✅ Descriptive names
const LoadingSpinner = () => {};  // Not just "Spinner"
const UserSettingsForm = () => {}; // Not just "Form"
const PrimaryButton = () => {};    // Not just "Button"
```

### Props and State
```tsx
// ✅ Descriptive prop names
interface ButtonProps {
  isLoading: boolean;        // Not just "loading"
  onClick: () => void;       // Clear action
  variant: 'primary' | 'secondary';
  children: React.ReactNode;
}

// ✅ Boolean props with 'is', 'has', 'can', 'should' prefixes
interface UserProps {
  isLoggedIn: boolean;
  hasPermission: boolean;
  canEdit: boolean;
  shouldShowWelcome: boolean;
}

// ✅ Event handler naming
const handleSubmit = () => {};
const handleUserSelect = () => {};
const handleModalClose = () => {};
```

### Hooks and Utilities
```tsx
// ✅ Custom hooks start with 'use'
const useLocalStorage = () => {};
const useDebounce = () => {};
const useApi = () => {};

// ✅ Utility functions are descriptive
const formatCurrency = () => {};
const validateEmail = () => {};
const debounce = () => {};
```

---

## 💅 Code Style Guidelines

### JSX Formatting
```tsx
// ✅ Multi-line JSX with proper indentation
const UserCard = ({ user, onEdit, onDelete }) => (
  <div className="user-card">
    <img 
      src={user.avatar} 
      alt={`${user.name}'s avatar`}
      className="avatar"
    />
    <div className="user-info">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
    <div className="actions">
      <button onClick={() => onEdit(user.id)}>
        Edit
      </button>
      <button 
        onClick={() => onDelete(user.id)}
        className="danger"
      >
        Delete
      </button>
    </div>
  </div>
);

// ✅ Conditional rendering patterns
{isLoading && <LoadingSpinner />}
{error && <ErrorMessage error={error} />}
{data?.length > 0 ? (
  <DataList items={data} />
) : (
  <EmptyState />
)}
```

### Props Destructuring
```tsx
// ✅ Destructure props in function signature
const UserProfile = ({ 
  user, 
  isEditing, 
  onEdit, 
  onSave,
  className = '' 
}) => {
  // Component logic
};

// ✅ For many props, destructure in component body
const ComplexComponent = (props) => {
  const {
    user,
    settings,
    permissions,
    onUserUpdate,
    onSettingsChange,
    onPermissionToggle,
    className,
    children
  } = props;
};
```

### Component Props Interface
```tsx
// ✅ Well-defined props interface
interface UserProfileProps {
  /** User object containing profile information */
  user: User;
  /** Whether the profile is in edit mode */
  isEditing?: boolean;
  /** Callback fired when edit button is clicked */
  onEdit?: () => void;
  /** Callback fired when profile is saved */
  onSave?: (user: User) => void;
  /** Additional CSS class names */
  className?: string;
  /** Child components */
  children?: React.ReactNode;
}

// ✅ Optional props with defaults
const UserProfile: React.FC<UserProfileProps> = ({
  user,
  isEditing = false,
  onEdit,
  onSave,
  className = '',
  children
}) => {
  // Component implementation
};
```

---

## 🔄 State Management

### Local State Guidelines
```tsx
// ✅ Use useState for simple local state
const [isOpen, setIsOpen] = useState(false);
const [formData, setFormData] = useState({ name: '', email: '' });

// ✅ Use useReducer for complex state logic
const [state, dispatch] = useReducer(userReducer, initialState);

// ✅ Separate concerns - one useState per concept
const [users, setUsers] = useState([]);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

// ❌ Avoid - Don't combine unrelated state
const [state, setState] = useState({
  users: [],
  loading: false,
  error: null,
  theme: 'light',
  sidebarOpen: false
});
```

### State Updates
```tsx
// ✅ Immutable updates
const addUser = (newUser) => {
  setUsers([...users, newUser]);
};

const updateUser = (id, updates) => {
  setUsers(users.map(user => 
    user.id === id ? { ...user, ...updates } : user
  ));
};

const removeUser = (id) => {
  setUsers(users.filter(user => user.id !== id));
};

// ✅ Functional updates for dependent state
const incrementCounter = () => {
  setCount(prevCount => prevCount + 1);
};
```

### Context Usage
```tsx
// ✅ Create specific contexts for different concerns
const AuthContext = createContext();
const ThemeContext = createContext();
const NotificationContext = createContext();

// ✅ Provide type safety
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ✅ Custom hook for context consumption
const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

---

## ⚡ Performance Best Practices

### Component Optimization
```tsx
// ✅ Use React.memo for pure components
const UserCard = React.memo(({ user, onEdit }) => (
  <div>
    <h3>{user.name}</h3>
    <button onClick={() => onEdit(user.id)}>Edit</button>
  </div>
));

// ✅ Custom comparison function when needed
const UserList = React.memo(({ users, selectedId }) => (
  <div>
    {users.map(user => (
      <UserCard 
        key={user.id} 
        user={user} 
        isSelected={user.id === selectedId}
      />
    ))}
  </div>
), (prevProps, nextProps) => {
  return (
    prevProps.users.length === nextProps.users.length &&
    prevProps.selectedId === nextProps.selectedId
  );
});
```

### Hook Optimization
```tsx
// ✅ Memoize expensive calculations
const expensiveValue = useMemo(() => {
  return processLargeDataSet(data);
}, [data]);

// ✅ Memoize callbacks passed to children
const handleUserSelect = useCallback((userId) => {
  setSelectedUser(userId);
  onUserSelect?.(userId);
}, [onUserSelect]);

// ✅ Memoize objects and arrays
const searchConfig = useMemo(() => ({
  fuzzy: true,
  threshold: 0.6,
  keys: ['name', 'email']
}), []);
```

### Code Splitting
```tsx
// ✅ Lazy load components
const Dashboard = lazy(() => import('./Dashboard'));
const UserSettings = lazy(() => import('./UserSettings'));

function App() {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<UserSettings />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

// ✅ Lazy load with error boundary
const LazyComponent = lazy(() => 
  import('./Component').catch(() => ({
    default: () => <div>Failed to load component</div>
  }))
);
```

---

## 🔒 Security Guidelines

### Input Sanitization
```tsx
// ✅ Validate and sanitize user input
const sanitizeInput = (input) => {
  return input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
};

// ✅ Use libraries for HTML sanitization
import DOMPurify from 'dompurify';

const SafeHTML = ({ htmlContent }) => (
  <div 
    dangerouslySetInnerHTML={{
      __html: DOMPurify.sanitize(htmlContent)
    }}
  />
);
```

### Environment Variables
```tsx
// ✅ Use REACT_APP_ prefix for client-side variables
const API_URL = process.env.REACT_APP_API_URL;

// ✅ Validate environment variables
if (!API_URL) {
  throw new Error('REACT_APP_API_URL is required');
}

// ❌ Never expose sensitive data
// const SECRET_KEY = process.env.SECRET_KEY; // DON'T DO THIS
```

### XSS Prevention
```tsx
// ✅ React automatically escapes values
const userName = '<script>alert("xss")</script>';
return <div>{userName}</div>; // Safe - will render as text

// ⚠️ Be careful with dangerouslySetInnerHTML
const UserBio = ({ bio }) => (
  <div 
    dangerouslySetInnerHTML={{
      __html: DOMPurify.sanitize(bio) // Always sanitize!
    }}
  />
);
```

---

## ♿ Accessibility Standards

### Semantic HTML
```tsx
// ✅ Use semantic HTML elements
const NavigationMenu = () => (
  <nav role="navigation">
    <ul>
      <li><a href="/home">Home</a></li>
      <li><a href="/about">About</a></li>
      <li><a href="/contact">Contact</a></li>
    </ul>
  </nav>
);

// ✅ Proper heading hierarchy
const ArticlePage = () => (
  <article>
    <h1>Article Title</h1>
    <section>
      <h2>Section Title</h2>
      <h3>Subsection Title</h3>
    </section>
  </article>
);
```

### ARIA Attributes
```tsx
// ✅ Use ARIA labels and roles
const SearchBox = () => (
  <div role="search">
    <label htmlFor="search-input" className="sr-only">
      Search articles
    </label>
    <input
      id="search-input"
      type="text"
      placeholder="Search..."
      aria-describedby="search-help"
    />
    <span id="search-help" className="sr-only">
      Type to search articles and press enter
    </span>
  </div>
);

// ✅ Button accessibility
const ToggleButton = ({ isExpanded, onToggle }) => (
  <button
    onClick={onToggle}
    aria-expanded={isExpanded}
    aria-controls="expandable-content"
  >
    {isExpanded ? 'Collapse' : 'Expand'}
  </button>
);
```

### Keyboard Navigation
```tsx
// ✅ Handle keyboard events
const Modal = ({ isOpen, onClose, children }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      role="dialog" 
      aria-modal="true"
      className="modal-overlay"
      onClick={onClose}
    >
      <div 
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
};
```

---

## 📋 Code Review Checklist

### Component Review
- [ ] Component has a single responsibility
- [ ] Props are properly typed and documented
- [ ] Component is properly named (PascalCase)
- [ ] No unnecessary re-renders
- [ ] Proper error handling
- [ ] Accessibility considerations

### Code Quality
- [ ] No console.log statements in production code
- [ ] No hardcoded values - use constants
- [ ] Proper error boundaries where needed
- [ ] Loading and error states handled
- [ ] No memory leaks (cleanup in useEffect)

### Performance
- [ ] Components memoized where appropriate
- [ ] Expensive operations memoized
- [ ] Proper dependency arrays in hooks
- [ ] No unnecessary object/array creation in render

### Testing
- [ ] Unit tests for component logic
- [ ] Integration tests for user flows
- [ ] Accessibility tests
- [ ] Edge cases covered

---

*Following these best practices will help you write maintainable, performant, and accessible React applications that scale well with your team and project requirements.*
