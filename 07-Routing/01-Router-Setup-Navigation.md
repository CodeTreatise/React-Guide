# Router Setup & Navigation

## 🎯 Learning Objectives
By the end of this section, you will:
- Set up React Router v6 in your applications
- Understand different router types and when to use them
- Master navigation components and hooks
- Implement programmatic navigation
- Handle browser history and navigation state
- Build accessible navigation patterns
- Optimize navigation performance

## 📚 Table of Contents
1. [React Router Installation & Setup](#react-router-installation--setup)
2. [Router Types & Configuration](#router-types--configuration)
3. [Navigation Components](#navigation-components)
4. [Navigation Hooks](#navigation-hooks)
5. [Programmatic Navigation](#programmatic-navigation)
6. [Navigation State Management](#navigation-state-management)
7. [Accessibility in Navigation](#accessibility-in-navigation)
8. [Performance Optimization](#performance-optimization)
9. [Best Practices](#best-practices)
10. [Common Patterns](#common-patterns)

## React Router Installation & Setup

### Installation
```bash
# Install React Router v6
npm install react-router-dom

# For React Native
npm install @react-navigation/native

# TypeScript types (if using TypeScript)
npm install --save-dev @types/react-router-dom
```

### Basic Setup
```jsx
// App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Contact from './pages/Contact';
import NotFound from './pages/NotFound';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

### TypeScript Setup
```typescript
// App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Home, About, Contact, NotFound } from './pages';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
```

## Router Types & Configuration

### BrowserRouter
The most common router for web applications using HTML5 history API.

```jsx
import { BrowserRouter } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter basename="/my-app">
      {/* Your routes */}
    </BrowserRouter>
  );
}
```

**Pros:**
- Clean URLs without hash
- Full browser history support
- Server-side rendering friendly

**Cons:**
- Requires server configuration for deep links
- Not suitable for static hosting without configuration

### HashRouter
Uses URL hash for routing, suitable for static hosting.

```jsx
import { HashRouter } from 'react-router-dom';

function App() {
  return (
    <HashRouter>
      {/* Your routes */}
    </HashRouter>
  );
}
```

**Pros:**
- Works with any web server
- No server configuration needed
- Supports older browsers

**Cons:**
- URLs contain hash (#)
- Not ideal for SEO
- Limited server-side rendering support

### MemoryRouter
Keeps history in memory, useful for testing and React Native.

```jsx
import { MemoryRouter } from 'react-router-dom';

function App() {
  return (
    <MemoryRouter initialEntries={['/home', '/about']} initialIndex={0}>
      {/* Your routes */}
    </MemoryRouter>
  );
}
```

### Configuration Options
```jsx
// Advanced BrowserRouter configuration
<BrowserRouter
  basename="/app"
  window={window}
  future={{
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }}
>
  <Routes>
    {/* Routes */}
  </Routes>
</BrowserRouter>
```

## Navigation Components

### Link Component
Basic navigation component for internal routing.

```jsx
import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/about">About</Link>
      <Link to="/contact">Contact</Link>
      
      {/* Link with state */}
      <Link 
        to="/profile" 
        state={{ from: 'navigation' }}
      >
        Profile
      </Link>
      
      {/* Replace current entry in history */}
      <Link to="/login" replace>
        Login
      </Link>
    </nav>
  );
}
```

### NavLink Component
Link with active state styling capabilities.

```jsx
import { NavLink } from 'react-router-dom';

function Navigation() {
  return (
    <nav>
      <NavLink
        to="/"
        className={({ isActive }) => 
          isActive ? 'nav-link active' : 'nav-link'
        }
      >
        Home
      </NavLink>
      
      <NavLink
        to="/about"
        style={({ isActive }) => ({
          color: isActive ? '#007bff' : '#333',
          fontWeight: isActive ? 'bold' : 'normal'
        })}
      >
        About
      </NavLink>
      
      {/* Using end prop for exact matching */}
      <NavLink
        to="/dashboard"
        end
        className={({ isActive }) => 
          isActive ? 'nav-link active' : 'nav-link'
        }
      >
        Dashboard
      </NavLink>
    </nav>
  );
}
```

### Advanced NavLink Patterns
```jsx
// Custom NavLink component
function CustomNavLink({ to, children, ...props }) {
  return (
    <NavLink
      to={to}
      className={({ isActive, isPending }) => {
        const baseClass = 'nav-link';
        if (isPending) return `${baseClass} pending`;
        if (isActive) return `${baseClass} active`;
        return baseClass;
      }}
      {...props}
    >
      {children}
    </NavLink>
  );
}

// NavLink with icon
function IconNavLink({ to, icon, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => 
        `nav-link ${isActive ? 'active' : ''}`
      }
    >
      <span className="nav-icon">{icon}</span>
      <span className="nav-text">{children}</span>
    </NavLink>
  );
}
```

## Navigation Hooks

### useNavigate Hook
Programmatic navigation with the navigate function.

```jsx
import { useNavigate } from 'react-router-dom';

function LoginForm() {
  const navigate = useNavigate();

  const handleLogin = async (credentials) => {
    try {
      await login(credentials);
      
      // Navigate to dashboard
      navigate('/dashboard');
      
      // Navigate with replace (no back button)
      navigate('/dashboard', { replace: true });
      
      // Navigate with state
      navigate('/dashboard', { 
        state: { from: 'login' },
        replace: true 
      });
      
      // Go back
      navigate(-1);
      
      // Go forward
      navigate(1);
      
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      {/* Form fields */}
    </form>
  );
}
```

### useLocation Hook
Access current location information.

```jsx
import { useLocation } from 'react-router-dom';

function CurrentPage() {
  const location = useLocation();

  return (
    <div>
      <p>Current pathname: {location.pathname}</p>
      <p>Search params: {location.search}</p>
      <p>Hash: {location.hash}</p>
      <p>State: {JSON.stringify(location.state)}</p>
      <p>Key: {location.key}</p>
    </div>
  );
}

// Using location state
function ProfilePage() {
  const location = useLocation();
  const { from } = location.state || { from: 'unknown' };

  return (
    <div>
      <h1>Profile</h1>
      <p>Navigated from: {from}</p>
    </div>
  );
}
```

### useParams Hook
Access URL parameters.

```jsx
import { useParams } from 'react-router-dom';

function UserProfile() {
  const { userId } = useParams();

  return (
    <div>
      <h1>User Profile</h1>
      <p>User ID: {userId}</p>
    </div>
  );
}

// Multiple parameters
function BlogPost() {
  const { category, postId } = useParams();

  return (
    <div>
      <h1>Blog Post</h1>
      <p>Category: {category}</p>
      <p>Post ID: {postId}</p>
    </div>
  );
}
```

### useSearchParams Hook
Handle URL search parameters.

```jsx
import { useSearchParams } from 'react-router-dom';

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();

  const search = searchParams.get('search') || '';
  const category = searchParams.get('category') || 'all';
  const page = parseInt(searchParams.get('page') || '1');

  const updateSearch = (newSearch) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      if (newSearch) {
        newParams.set('search', newSearch);
      } else {
        newParams.delete('search');
      }
      newParams.set('page', '1'); // Reset page on search
      return newParams;
    });
  };

  const updateCategory = (newCategory) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      newParams.set('category', newCategory);
      newParams.set('page', '1'); // Reset page on category change
      return newParams;
    });
  };

  return (
    <div>
      <input
        value={search}
        onChange={(e) => updateSearch(e.target.value)}
        placeholder="Search products..."
      />
      
      <select 
        value={category}
        onChange={(e) => updateCategory(e.target.value)}
      >
        <option value="all">All Categories</option>
        <option value="electronics">Electronics</option>
        <option value="clothing">Clothing</option>
      </select>
      
      <div>
        Current search: {search}
        Current category: {category}
        Current page: {page}
      </div>
    </div>
  );
}
```

## Programmatic Navigation

### Navigation Patterns
```jsx
import { useNavigate, useLocation } from 'react-router-dom';

function NavigationExamples() {
  const navigate = useNavigate();
  const location = useLocation();

  // Basic navigation
  const goToHome = () => navigate('/');
  
  // Navigation with state
  const goToProfile = () => {
    navigate('/profile', {
      state: { 
        from: location.pathname,
        timestamp: Date.now()
      }
    });
  };

  // Replace current entry
  const redirectToLogin = () => {
    navigate('/login', { replace: true });
  };

  // Relative navigation
  const goToNext = () => navigate('../next');
  const goToPrevious = () => navigate('../previous');

  // History navigation
  const goBack = () => navigate(-1);
  const goForward = () => navigate(1);

  // Conditional navigation
  const handleSubmit = async (data) => {
    try {
      await submitData(data);
      
      // Navigate based on user role
      const userRole = getUserRole();
      if (userRole === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/user/dashboard');
      }
    } catch (error) {
      navigate('/error', { 
        state: { error: error.message }
      });
    }
  };

  return (
    <div>
      <button onClick={goToHome}>Go Home</button>
      <button onClick={goToProfile}>View Profile</button>
      <button onClick={redirectToLogin}>Login</button>
      <button onClick={goBack}>Back</button>
      <button onClick={goForward}>Forward</button>
    </div>
  );
}
```

### Navigation Guards
```jsx
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function useNavigationGuard() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();

  const navigateWithGuard = (to, options = {}) => {
    // Check authentication
    if (!isAuthenticated && requiresAuth(to)) {
      navigate('/login', {
        state: { from: to },
        replace: true
      });
      return false;
    }

    // Check permissions
    if (!hasPermission(user, to)) {
      navigate('/unauthorized', { replace: true });
      return false;
    }

    // Check if leaving unsaved changes
    if (hasUnsavedChanges() && !options.force) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave?'
      );
      if (!confirmed) return false;
    }

    navigate(to, options);
    return true;
  };

  return { navigateWithGuard };
}

// Usage
function MyComponent() {
  const { navigateWithGuard } = useNavigationGuard();

  const handleNavigation = (path) => {
    navigateWithGuard(path);
  };

  return (
    <button onClick={() => handleNavigation('/admin')}>
      Go to Admin
    </button>
  );
}
```

## Navigation State Management

### Persistent Navigation State
```jsx
import { useNavigate, useLocation } from 'react-router-dom';
import { useLocalStorage } from '../hooks/useLocalStorage';

function NavigationStateManager() {
  const navigate = useNavigate();
  const location = useLocation();
  const [navigationHistory, setNavigationHistory] = useLocalStorage(
    'navigation-history', 
    []
  );

  useEffect(() => {
    // Track navigation history
    setNavigationHistory(prev => {
      const newHistory = [...prev, {
        pathname: location.pathname,
        search: location.search,
        timestamp: Date.now()
      }].slice(-10); // Keep last 10 entries
      
      return newHistory;
    });
  }, [location, setNavigationHistory]);

  const goToLastVisited = () => {
    if (navigationHistory.length > 1) {
      const lastVisited = navigationHistory[navigationHistory.length - 2];
      navigate(lastVisited.pathname + lastVisited.search);
    }
  };

  return (
    <div>
      <button onClick={goToLastVisited}>
        Go to Last Visited Page
      </button>
      
      <div>
        <h3>Recent Pages:</h3>
        {navigationHistory.slice(-5).map((entry, index) => (
          <div key={index}>
            <button 
              onClick={() => navigate(entry.pathname + entry.search)}
            >
              {entry.pathname}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Navigation State Context
```jsx
import React, { createContext, useContext, useReducer } from 'react';

const NavigationContext = createContext();

const navigationReducer = (state, action) => {
  switch (action.type) {
    case 'SET_BREADCRUMBS':
      return { ...state, breadcrumbs: action.payload };
    case 'SET_TITLE':
      return { ...state, title: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
};

export function NavigationProvider({ children }) {
  const [state, dispatch] = useReducer(navigationReducer, {
    breadcrumbs: [],
    title: '',
    isLoading: false,
    error: null
  });

  const setBreadcrumbs = (breadcrumbs) => {
    dispatch({ type: 'SET_BREADCRUMBS', payload: breadcrumbs });
  };

  const setTitle = (title) => {
    dispatch({ type: 'SET_TITLE', payload: title });
    document.title = title;
  };

  const setLoading = (isLoading) => {
    dispatch({ type: 'SET_LOADING', payload: isLoading });
  };

  const setError = (error) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  return (
    <NavigationContext.Provider value={{
      ...state,
      setBreadcrumbs,
      setTitle,
      setLoading,
      setError
    }}>
      {children}
    </NavigationContext.Provider>
  );
}

export const useNavigation = () => {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within NavigationProvider');
  }
  return context;
};
```

## Accessibility in Navigation

### ARIA Labels and Roles
```jsx
function AccessibleNavigation() {
  return (
    <nav role="navigation" aria-label="Main navigation">
      <ul>
        <li>
          <NavLink
            to="/"
            aria-current={({ isActive }) => isActive ? 'page' : undefined}
          >
            Home
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/about"
            aria-current={({ isActive }) => isActive ? 'page' : undefined}
          >
            About
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/contact"
            aria-current={({ isActive }) => isActive ? 'page' : undefined}
          >
            Contact
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}
```

### Skip Links
```jsx
function SkipLinks() {
  return (
    <>
      <a 
        href="#main-content" 
        className="skip-link"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById('main-content')?.focus();
        }}
      >
        Skip to main content
      </a>
      <a 
        href="#navigation" 
        className="skip-link"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById('navigation')?.focus();
        }}
      >
        Skip to navigation
      </a>
    </>
  );
}
```

### Focus Management
```jsx
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

function FocusManager({ children }) {
  const location = useLocation();
  const skipLinkRef = useRef(null);

  useEffect(() => {
    // Announce route changes to screen readers
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.textContent = `Navigated to ${location.pathname}`;
    
    document.body.appendChild(announcement);
    
    // Focus management for route changes
    if (skipLinkRef.current) {
      skipLinkRef.current.focus();
    }

    // Cleanup
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }, [location]);

  return (
    <div>
      <a
        ref={skipLinkRef}
        href="#main-content"
        className="skip-link"
        tabIndex={-1}
      >
        Skip to main content
      </a>
      {children}
    </div>
  );
}
```

## Performance Optimization

### Lazy Loading Navigation
```jsx
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load components
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Contact = lazy(() => import('./pages/Contact'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </Suspense>
  );
}
```

### Preloading Routes
```jsx
import { useEffect } from 'react';

// Preload critical routes
const preloadRoute = (routeComponent) => {
  const componentImport = routeComponent();
  return componentImport;
};

function App() {
  useEffect(() => {
    // Preload important routes after initial render
    const timer = setTimeout(() => {
      preloadRoute(() => import('./pages/Dashboard'));
      preloadRoute(() => import('./pages/Profile'));
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <Routes>
      {/* Routes */}
    </Routes>
  );
}
```

### Navigation Performance Monitoring
```jsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

function NavigationPerformanceMonitor() {
  const location = useLocation();

  useEffect(() => {
    const startTime = performance.now();

    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const navigationEntry = entries.find(
        entry => entry.entryType === 'navigation'
      );

      if (navigationEntry) {
        console.log('Navigation Performance:', {
          pathname: location.pathname,
          loadTime: navigationEntry.loadEventEnd - navigationEntry.fetchStart,
          domContentLoaded: navigationEntry.domContentLoadedEventEnd - navigationEntry.fetchStart,
          firstPaint: entries.find(e => e.name === 'first-paint')?.startTime,
          firstContentfulPaint: entries.find(e => e.name === 'first-contentful-paint')?.startTime
        });
      }
    });

    observer.observe({ entryTypes: ['navigation', 'paint'] });

    return () => {
      observer.disconnect();
      const endTime = performance.now();
      console.log(`Route render time: ${endTime - startTime}ms`);
    };
  }, [location]);

  return null;
}
```

## Best Practices

### 1. Route Organization
```jsx
// routes/index.js
import { Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { publicRoutes, privateRoutes, adminRoutes } from './routeConfig';

export function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      {publicRoutes.map(route => (
        <Route
          key={route.path}
          path={route.path}
          element={route.element}
        />
      ))}

      {/* Protected routes */}
      {privateRoutes.map(route => (
        <Route
          key={route.path}
          path={route.path}
          element={
            <ProtectedRoute>
              {route.element}
            </ProtectedRoute>
          }
        />
      ))}

      {/* Admin routes */}
      {adminRoutes.map(route => (
        <Route
          key={route.path}
          path={route.path}
          element={
            <ProtectedRoute requiredRole="admin">
              {route.element}
            </ProtectedRoute>
          }
        />
      ))}
    </Routes>
  );
}
```

### 2. Navigation Patterns
```jsx
// components/Navigation.jsx
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function Navigation() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', public: true },
    { path: '/about', label: 'About', public: true },
    { path: '/dashboard', label: 'Dashboard', requiresAuth: true },
    { path: '/admin', label: 'Admin', requiresRole: 'admin' }
  ];

  const filteredNavItems = navItems.filter(item => {
    if (item.public) return true;
    if (item.requiresAuth && !user) return false;
    if (item.requiresRole && user?.role !== item.requiresRole) return false;
    return true;
  });

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <Link to="/">MyApp</Link>
      </div>
      
      <ul className="nav-menu">
        {filteredNavItems.map(item => (
          <li key={item.path}>
            <NavLink
              to={item.path}
              className={({ isActive }) => 
                `nav-link ${isActive ? 'active' : ''}`
              }
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>

      {user && (
        <div className="nav-user">
          <span>Welcome, {user.name}</span>
          <button onClick={logout}>Logout</button>
        </div>
      )}
    </nav>
  );
}
```

### 3. Error Boundaries for Routes
```jsx
import React from 'react';

class RouteErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Route Error:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong with this page.</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try Again
          </button>
          <button onClick={() => window.location.href = '/'}>
            Go Home
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={
          <RouteErrorBoundary>
            <AppRoutes />
          </RouteErrorBoundary>
        } />
      </Routes>
    </BrowserRouter>
  );
}
```

## Common Patterns

### 1. Breadcrumb Navigation
```jsx
import { useLocation, Link } from 'react-router-dom';

function Breadcrumbs() {
  const location = useLocation();
  
  const pathnames = location.pathname.split('/').filter(x => x);
  
  return (
    <nav aria-label="breadcrumb">
      <ol className="breadcrumb">
        <li className="breadcrumb-item">
          <Link to="/">Home</Link>
        </li>
        {pathnames.map((name, index) => {
          const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
          const isLast = index === pathnames.length - 1;
          
          return (
            <li key={name} className={`breadcrumb-item ${isLast ? 'active' : ''}`}>
              {isLast ? (
                <span aria-current="page">{name}</span>
              ) : (
                <Link to={routeTo}>{name}</Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
```

### 2. Route Guards with Hooks
```jsx
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function useRouteGuard(options = {}) {
  const { requiresAuth = false, requiredRole = null, redirectTo = '/login' } = options;
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (isLoading) return;

    if (requiresAuth && !isAuthenticated) {
      navigate(redirectTo, {
        state: { from: location.pathname },
        replace: true
      });
      return;
    }

    if (requiredRole && (!user || user.role !== requiredRole)) {
      navigate('/unauthorized', { replace: true });
      return;
    }
  }, [isAuthenticated, user, isLoading, requiresAuth, requiredRole, redirectTo, navigate, location]);

  return { canAccess: isAuthenticated && (!requiredRole || user?.role === requiredRole) };
}

// Usage in components
function AdminPage() {
  const { canAccess } = useRouteGuard({
    requiresAuth: true,
    requiredRole: 'admin'
  });

  if (!canAccess) {
    return <div>Checking permissions...</div>;
  }

  return <div>Admin Content</div>;
}
```

### 3. Modal Routes
```jsx
import { useLocation, useNavigate } from 'react-router-dom';
import { Modal } from '../components/Modal';

function ModalRoute({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const background = location.state?.background;

  const closeModal = () => {
    navigate(-1);
  };

  if (background) {
    return (
      <Modal onClose={closeModal} isOpen={true}>
        {children}
      </Modal>
    );
  }

  return children;
}

// Usage
function App() {
  const location = useLocation();
  const background = location.state?.background;

  return (
    <div>
      {/* Main routes */}
      <Routes location={background || location}>
        <Route path="/" element={<Home />} />
        <Route path="/gallery" element={<Gallery />} />
        <Route path="/photo/:id" element={<Photo />} />
      </Routes>

      {/* Modal routes */}
      {background && (
        <Routes>
          <Route path="/photo/:id" element={
            <ModalRoute>
              <Photo />
            </ModalRoute>
          } />
        </Routes>
      )}
    </div>
  );
}
```

This comprehensive guide covers router setup and navigation fundamentals in React Router v6. The next sections will dive deeper into dynamic routing, nested routes, and advanced routing patterns.