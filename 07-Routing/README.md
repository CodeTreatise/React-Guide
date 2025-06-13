# Module 7: Routing (React Router)

## 🎯 Learning Objectives
By the end of this module, you will:
- Master React Router v6 for building single-page applications
- Implement dynamic routing with parameters and query strings
- Create protected routes with authentication
- Build nested routing architectures
- Implement programmatic navigation and route guards
- Handle routing in large-scale applications
- Optimize routing performance with lazy loading
- Build accessible routing experiences

## 📚 Module Overview

### What You'll Learn
React Router is the standard routing library for React applications. This module covers everything from basic routing concepts to advanced patterns for building complex, navigable web applications.

### Prerequisites
- Solid understanding of React fundamentals (Modules 1-2)
- Experience with React hooks (Module 3)
- Understanding of JavaScript ES6+ features
- Basic knowledge of URL structure and HTTP

## 🏗️ Core Concepts

### 1. React Router Fundamentals

#### Basic Router Setup
```jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/contact">Contact</Link>
      </nav>
      
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

// Components
function Home() {
  return <h1>Welcome to Home Page</h1>;
}

function About() {
  return <h1>About Us</h1>;
}

function Contact() {
  return <h1>Contact Us</h1>;
}

function NotFound() {
  return <h1>404 - Page Not Found</h1>;
}
```

#### Different Router Types
```jsx
// BrowserRouter - Uses HTML5 history API
import { BrowserRouter } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      {/* Your routes */}
    </BrowserRouter>
  );
}

// HashRouter - Uses URL hash for routing
import { HashRouter } from 'react-router-dom';

function App() {
  return (
    <HashRouter>
      {/* Your routes */}
    </HashRouter>
  );
}

// MemoryRouter - For testing or React Native
import { MemoryRouter } from 'react-router-dom';

function App() {
  return (
    <MemoryRouter initialEntries={['/']}>
      {/* Your routes */}
    </MemoryRouter>
  );
}
```

### 2. Dynamic Routing and Parameters

#### URL Parameters
```jsx
import { useParams, useNavigate } from 'react-router-dom';

function App() {
  return (
    <Routes>
      <Route path="/users/:userId" element={<UserProfile />} />
      <Route path="/posts/:postId/comments/:commentId" element={<Comment />} />
      <Route path="/products/:category/:productId" element={<Product />} />
    </Routes>
  );
}

function UserProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchUser(userId)
      .then(setUser)
      .catch(() => navigate('/users', { replace: true }))
      .finally(() => setLoading(false));
  }, [userId, navigate]);
  
  if (loading) return <LoadingSpinner />;
  if (!user) return <UserNotFound />;
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <button onClick={() => navigate('/users')}>
        Back to Users
      </button>
    </div>
  );
}

// Multiple parameters
function Comment() {
  const { postId, commentId } = useParams();
  
  return (
    <div>
      <h2>Comment {commentId} on Post {postId}</h2>
    </div>
  );
}
```

#### Optional Parameters and Wildcards
```jsx
function App() {
  return (
    <Routes>
      {/* Optional parameter */}
      <Route path="/posts/:postId/:slug?" element={<Post />} />
      
      {/* Wildcard matching */}
      <Route path="/files/*" element={<FileExplorer />} />
      
      {/* Catch-all route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

function FileExplorer() {
  const location = useLocation();
  const filePath = location.pathname.replace('/files/', '');
  
  return (
    <div>
      <h2>File Explorer</h2>
      <p>Current path: {filePath || 'root'}</p>
    </div>
  );
}
```

### 3. Query Parameters and Search

#### Working with Query Parameters
```jsx
import { useSearchParams, useLocation } from 'react-router-dom';

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  
  // Get query parameters
  const category = searchParams.get('category') || 'all';
  const sortBy = searchParams.get('sort') || 'name';
  const page = parseInt(searchParams.get('page')) || 1;
  const search = searchParams.get('search') || '';
  
  // Update query parameters
  const updateFilters = (newFilters) => {
    const newParams = new URLSearchParams(searchParams);
    
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) {
        newParams.set(key, value);
      } else {
        newParams.delete(key);
      }
    });
    
    setSearchParams(newParams);
  };
  
  // Fetch products when filters change
  useEffect(() => {
    fetchProducts({ category, sortBy, page, search })
      .then(setProducts);
  }, [category, sortBy, page, search]);
  
  return (
    <div>
      <ProductFilters
        category={category}
        sortBy={sortBy}
        search={search}
        onFiltersChange={updateFilters}
      />
      
      <ProductGrid products={products} />
      
      <Pagination
        currentPage={page}
        onPageChange={(page) => updateFilters({ page })}
      />
    </div>
  );
}

// Custom hook for URL state management
function useUrlState(key, defaultValue) {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const value = searchParams.get(key) || defaultValue;
  
  const setValue = useCallback((newValue) => {
    const newParams = new URLSearchParams(searchParams);
    
    if (newValue) {
      newParams.set(key, newValue);
    } else {
      newParams.delete(key);
    }
    
    setSearchParams(newParams);
  }, [key, searchParams, setSearchParams]);
  
  return [value, setValue];
}
```

### 4. Nested Routing

#### Outlet and Nested Routes
```jsx
import { Outlet, NavLink } from 'react-router-dom';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<Dashboard />}>
          <Route index element={<DashboardOverview />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="users" element={<UsersLayout />}>
          <Route index element={<UsersList />} />
          <Route path=":userId" element={<UserDetail />} />
          <Route path=":userId/edit" element={<UserEdit />} />
        </Route>
      </Route>
    </Routes>
  );
}

// Layout component with navigation
function Layout() {
  return (
    <div className="layout">
      <header>
        <nav>
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/users">Users</NavLink>
        </nav>
      </header>
      
      <main>
        <Outlet /> {/* Child routes render here */}
      </main>
      
      <footer>
        <p>&copy; 2024 My App</p>
      </footer>
    </div>
  );
}

// Dashboard with nested navigation
function Dashboard() {
  return (
    <div className="dashboard">
      <aside>
        <nav>
          <NavLink to="/dashboard" end>Overview</NavLink>
          <NavLink to="/dashboard/analytics">Analytics</NavLink>
          <NavLink to="/dashboard/reports">Reports</NavLink>
          <NavLink to="/dashboard/settings">Settings</NavLink>
        </nav>
      </aside>
      
      <section className="dashboard-content">
        <Outlet /> {/* Nested dashboard routes render here */}
      </section>
    </div>
  );
}
```

### 5. Protected Routes and Authentication

#### Route Guards Implementation
```jsx
import { Navigate, useLocation } from 'react-router-dom';

// Protected Route component
function ProtectedRoute({ children, requiredRole }) {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();
  
  // Show loading while checking authentication
  if (loading) {
    return <LoadingSpinner />;
  }
  
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <Navigate 
        to="/login" 
        state={{ from: location }} 
        replace 
      />
    );
  }
  
  // Check role-based access
  if (requiredRole && !user.roles.includes(requiredRole)) {
    return <UnauthorizedAccess />;
  }
  
  return children;
}

// Usage in routes
function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Admin-only routes */}
      <Route 
        path="/admin" 
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminPanel />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}

// Login component with redirect
function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  
  const from = location.state?.from?.pathname || '/dashboard';
  
  const handleLogin = async (credentials) => {
    try {
      await login(credentials);
      navigate(from, { replace: true });
    } catch (error) {
      setError('Invalid credentials');
    }
  };
  
  return (
    <form onSubmit={handleLogin}>
      {/* Login form */}
    </form>
  );
}
```

### 6. Programmatic Navigation

#### useNavigate Hook
```jsx
import { useNavigate } from 'react-router-dom';

function ProductForm({ product, onSave }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(product || {});
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await onSave(formData);
      
      // Navigate with success message
      navigate('/products', {
        state: { message: 'Product saved successfully!' }
      });
    } catch (error) {
      // Handle error
    }
  };
  
  const handleCancel = () => {
    // Navigate back or to specific route
    navigate(-1); // Go back
    // OR
    navigate('/products', { replace: true });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit">Save</button>
      <button type="button" onClick={handleCancel}>
        Cancel
      </button>
    </form>
  );
}

// Navigation with state
function ProductList() {
  const location = useLocation();
  const message = location.state?.message;
  
  useEffect(() => {
    if (message) {
      showNotification(message);
      // Clear the state to prevent showing on refresh
      window.history.replaceState({}, document.title);
    }
  }, [message]);
  
  return (
    <div>
      {/* Product list */}
    </div>
  );
}
```

### 7. Route Configuration and Lazy Loading

#### Code Splitting with Lazy Loading
```jsx
import { lazy, Suspense } from 'react';

// Lazy load components
const Dashboard = lazy(() => import('./components/Dashboard'));
const UserProfile = lazy(() => import('./components/UserProfile'));
const AdminPanel = lazy(() => import('./components/AdminPanel'));

// Route configuration
const routeConfig = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      {
        path: 'dashboard',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <Dashboard />
          </Suspense>
        )
      },
      {
        path: 'users/:userId',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <UserProfile />
          </Suspense>
        )
      },
      {
        path: 'admin',
        element: (
          <ProtectedRoute requiredRole="admin">
            <Suspense fallback={<LoadingSpinner />}>
              <AdminPanel />
            </Suspense>
          </ProtectedRoute>
        )
      }
    ]
  }
];

// Create routes from configuration
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const router = createBrowserRouter(routeConfig);

function App() {
  return <RouterProvider router={router} />;
}
```

#### Advanced Route Configuration
```jsx
// routes/index.js - Route configuration file
const createRoutes = (isAuthenticated, userRole) => [
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      { index: true, element: <Home /> },
      {
        path: 'auth',
        element: isAuthenticated ? <Navigate to="/dashboard" /> : <AuthLayout />,
        children: [
          { path: 'login', element: <Login /> },
          { path: 'register', element: <Register /> },
          { path: 'forgot-password', element: <ForgotPassword /> }
        ]
      },
      {
        path: 'dashboard',
        element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
        children: [
          { index: true, element: <DashboardHome /> },
          { path: 'analytics', element: <Analytics /> },
          { path: 'reports', element: <Reports /> }
        ]
      },
      ...(userRole === 'admin' ? [{
        path: 'admin',
        element: <AdminLayout />,
        children: [
          { index: true, element: <AdminDashboard /> },
          { path: 'users', element: <UserManagement /> },
          { path: 'settings', element: <AdminSettings /> }
        ]
      }] : [])
    ]
  }
];
```

## 🛠️ Practical Exercises

### Exercise 1: E-commerce Routing
Build a complete e-commerce application with:
- Product catalog with categories and search
- Product detail pages
- Shopping cart
- User authentication
- Order history

### Exercise 2: Dashboard Application
Create a multi-tenant dashboard with:
- Role-based routing
- Nested dashboard sections
- Dynamic navigation based on permissions
- URL state management for filters

### Exercise 3: Blog Platform
Build a blog platform with:
- Public and private routes
- SEO-friendly URLs
- Comment system with nested routes
- Author profiles and post management

### Exercise 4: File Manager
Create a file manager interface with:
- Nested folder navigation
- Breadcrumb navigation
- File upload and management
- Share links with expiration

## 🎯 Assessment Criteria

### Beginner Level (60-70%)
- [ ] Can set up basic routing with React Router
- [ ] Understands the difference between Link and NavLink
- [ ] Can implement URL parameters and query strings
- [ ] Knows how to handle 404 pages

### Intermediate Level (70-85%)
- [ ] Masters nested routing with Outlet
- [ ] Implements protected routes with authentication
- [ ] Uses programmatic navigation effectively
- [ ] Handles complex URL state management

### Advanced Level (85-100%)
- [ ] Builds scalable routing architectures
- [ ] Implements advanced route guards and permissions
- [ ] Optimizes routing performance with lazy loading
- [ ] Creates accessible routing experiences

## 📊 Routing Best Practices

### URL Design
- [ ] Use descriptive, SEO-friendly URLs
- [ ] Maintain consistent URL patterns
- [ ] Implement proper URL hierarchy
- [ ] Handle URL parameters validation

### Performance
- [ ] Implement code splitting for routes
- [ ] Use lazy loading for large components
- [ ] Preload critical routes
- [ ] Optimize bundle sizes

### User Experience
- [ ] Provide loading states for route transitions
- [ ] Handle navigation errors gracefully
- [ ] Implement breadcrumb navigation
- [ ] Support browser back/forward buttons

### Accessibility
- [ ] Manage focus on route changes
- [ ] Provide skip navigation links
- [ ] Use semantic HTML structure
- [ ] Support keyboard navigation

## 📖 Additional Resources

### Documentation
- [React Router Official Docs](https://reactrouter.com/)
- [React Router Migration Guide](https://reactrouter.com/en/main/upgrading/v5)

### Advanced Topics
- [React Router Data APIs](https://reactrouter.com/en/main/routers/create-browser-router)
- [Server-Side Rendering with React Router](https://reactrouter.com/en/main/guides/ssr)

### Tools and Libraries
- [Reach Router (deprecated, merged with React Router)](https://reach.tech/router/)
- [Next.js Routing](https://nextjs.org/docs/routing/introduction)

## 🔗 Next Steps
After completing this module, proceed to:
- Module 8: Forms and Validation
- Module 9: Advanced State Management
- Build a complete SPA with routing

---

⚡ **Pro Tips:**
- Always handle loading and error states for route components
- Use React Router's data APIs for better UX in React Router v6.4+
- Consider SEO implications when designing your routing structure
- Test your routing thoroughly, including edge cases and error scenarios
- Use TypeScript with React Router for better type safety
