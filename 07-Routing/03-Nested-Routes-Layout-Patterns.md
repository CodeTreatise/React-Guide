# Nested Routes & Layout Patterns

## 🎯 Learning Objectives
By the end of this section, you will:
- Master nested routing architectures in React Router v6
- Implement complex layout patterns with Outlet components
- Build hierarchical navigation systems
- Create reusable layout components
- Handle route inheritance and data flow
- Implement breadcrumb navigation systems
- Optimize nested route performance
- Design scalable routing architectures

## 📚 Table of Contents
1. [Nested Routes Fundamentals](#nested-routes-fundamentals)
2. [Outlet Component Deep Dive](#outlet-component-deep-dive)
3. [Layout Component Patterns](#layout-component-patterns)
4. [Route Hierarchy Design](#route-hierarchy-design)
5. [Data Flow in Nested Routes](#data-flow-in-nested-routes)
6. [Advanced Layout Patterns](#advanced-layout-patterns)
7. [Performance Optimization](#performance-optimization)
8. [Best Practices](#best-practices)
9. [Real-World Examples](#real-world-examples)

## Nested Routes Fundamentals

### Basic Nested Route Structure
Nested routes allow you to build complex UI hierarchies that mirror your URL structure.

```jsx
import { Routes, Route, Outlet } from 'react-router-dom';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="contact" element={<Contact />} />
        
        {/* Nested dashboard routes */}
        <Route path="dashboard" element={<DashboardLayout />}>
          <Route index element={<DashboardHome />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        
        {/* User routes with nested structure */}
        <Route path="users" element={<UsersLayout />}>
          <Route index element={<UsersList />} />
          <Route path=":userId" element={<UserProfile />}>
            <Route index element={<UserOverview />} />
            <Route path="posts" element={<UserPosts />} />
            <Route path="followers" element={<UserFollowers />} />
            <Route path="settings" element={<UserSettings />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}

// Main layout component
function Layout() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <nav>
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/users">Users</Link>
        </nav>
      </header>
      
      <main className="app-main">
        <Outlet />
      </main>
      
      <footer className="app-footer">
        <p>&copy; 2025 My App</p>
      </footer>
    </div>
  );
}
```

### Index Routes
Index routes render when the parent route path matches exactly.

```jsx
function DashboardLayout() {
  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        <nav>
          <NavLink to="/dashboard" end>
            Overview
          </NavLink>
          <NavLink to="/dashboard/analytics">
            Analytics
          </NavLink>
          <NavLink to="/dashboard/users">
            User Management
          </NavLink>
          <NavLink to="/dashboard/settings">
            Settings
          </NavLink>
        </nav>
      </aside>
      
      <div className="dashboard-content">
        <Outlet />
      </div>
    </div>
  );
}

// This renders when visiting "/dashboard"
function DashboardHome() {
  return (
    <div className="dashboard-home">
      <h1>Dashboard Overview</h1>
      <div className="stats-grid">
        <StatCard title="Total Users" value="1,234" />
        <StatCard title="Revenue" value="$12,345" />
        <StatCard title="Orders" value="567" />
        <StatCard title="Growth" value="+12%" />
      </div>
    </div>
  );
}
```

## Outlet Component Deep Dive

### Basic Outlet Usage
The Outlet component renders the child route element.

```jsx
import { Outlet, useLocation } from 'react-router-dom';

function ParentLayout() {
  const location = useLocation();

  return (
    <div className="parent-layout">
      <div className="layout-header">
        <h2>Parent Layout</h2>
        <p>Current path: {location.pathname}</p>
      </div>
      
      <div className="layout-body">
        <Outlet />
      </div>
    </div>
  );
}
```

### Outlet with Context
Pass data to child routes through Outlet context.

```jsx
import { Outlet } from 'react-router-dom';
import { useState, useEffect } from 'react';

function UserLayout() {
  const { userId } = useParams();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  if (loading) {
    return <div>Loading user...</div>;
  }

  if (!user) {
    return <div>User not found</div>;
  }

  // Pass user data to child routes
  return (
    <div className="user-layout">
      <div className="user-header">
        <img src={user.avatar} alt={user.name} />
        <h1>{user.name}</h1>
        <p>@{user.username}</p>
      </div>
      
      <nav className="user-nav">
        <NavLink to={`/users/${userId}`} end>
          Overview
        </NavLink>
        <NavLink to={`/users/${userId}/posts`}>
          Posts ({user.postsCount})
        </NavLink>
        <NavLink to={`/users/${userId}/followers`}>
          Followers ({user.followersCount})
        </NavLink>
      </nav>
      
      <div className="user-content">
        <Outlet context={{ user }} />
      </div>
    </div>
  );
}

// Child route accessing context
function UserPosts() {
  const { user } = useOutletContext();
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetchUserPosts(user.id).then(setPosts);
  }, [user.id]);

  return (
    <div className="user-posts">
      <h2>{user.name}'s Posts</h2>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

### Multiple Outlets
Advanced layouts can use multiple outlets with different contexts.

```jsx
function AdminLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [notifications, setNotifications] = useState([]);

  return (
    <div className="admin-layout">
      <header className="admin-header">
        <Outlet 
          context={{ 
            type: 'header',
            sidebarCollapsed,
            setSidebarCollapsed,
            notifications 
          }} 
        />
      </header>
      
      <div className="admin-body">
        <aside className={`admin-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <Outlet 
            context={{ 
              type: 'sidebar',
              collapsed: sidebarCollapsed 
            }} 
          />
        </aside>
        
        <main className="admin-main">
          <Outlet 
            context={{ 
              type: 'main',
              notifications,
              setNotifications 
            }} 
          />
        </main>
      </div>
    </div>
  );
}
```

## Layout Component Patterns

### Responsive Layout Pattern
```jsx
import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';

function ResponsiveLayout() {
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className={`responsive-layout ${isMobile ? 'mobile' : 'desktop'}`}>
      {isMobile && (
        <button 
          className="mobile-menu-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          ☰
        </button>
      )}
      
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <nav>
          <NavLink to="/dashboard" onClick={() => setS SidebarOpen(false)}>
            Dashboard
          </NavLink>
          <NavLink to="/users" onClick={() => setSidebarOpen(false)}>
            Users
          </NavLink>
          <NavLink to="/settings" onClick={() => setSidebarOpen(false)}>
            Settings
          </NavLink>
        </nav>
      </aside>
      
      {isMobile && sidebarOpen && (
        <div 
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      <main className="main-content">
        <Outlet context={{ isMobile, setSidebarOpen }} />
      </main>
    </div>
  );
}
```

### Tab Layout Pattern
```jsx
function TabLayout() {
  const location = useLocation();
  const { userId } = useParams();
  
  const tabs = [
    { path: '', label: 'Overview', end: true },
    { path: '/posts', label: 'Posts' },
    { path: '/followers', label: 'Followers' },
    { path: '/following', label: 'Following' },
    { path: '/settings', label: 'Settings' }
  ];

  return (
    <div className="tab-layout">
      <div className="tab-header">
        <nav className="tabs">
          {tabs.map(tab => (
            <NavLink
              key={tab.path}
              to={`/users/${userId}${tab.path}`}
              end={tab.end}
              className={({ isActive }) => 
                `tab ${isActive ? 'active' : ''}`
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </div>
      
      <div className="tab-content">
        <Outlet />
      </div>
    </div>
  );
}
```

### Master-Detail Layout
```jsx
function MasterDetailLayout() {
  const [selectedItem, setSelectedItem] = useState(null);
  const [items, setItems] = useState([]);

  return (
    <div className="master-detail-layout">
      <div className="master-panel">
        <div className="master-header">
          <h2>Items</h2>
          <button onClick={createNewItem}>New Item</button>
        </div>
        
        <div className="master-list">
          {items.map(item => (
            <div
              key={item.id}
              className={`master-item ${selectedItem?.id === item.id ? 'selected' : ''}`}
              onClick={() => setSelectedItem(item)}
            >
              {item.name}
            </div>
          ))}
        </div>
      </div>
      
      <div className="detail-panel">
        <Outlet context={{ selectedItem, setSelectedItem, items, setItems }} />
      </div>
    </div>
  );
}

function ItemDetail() {
  const { selectedItem } = useOutletContext();
  const { itemId } = useParams();

  if (!selectedItem && !itemId) {
    return (
      <div className="detail-placeholder">
        <p>Select an item to view details</p>
      </div>
    );
  }

  return (
    <div className="item-detail">
      <h1>{selectedItem?.name || 'Loading...'}</h1>
      {/* Item details */}
    </div>
  );
}
```

## Route Hierarchy Design

### Logical Hierarchy Structure
```jsx
function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="contact" element={<Contact />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
      </Route>

      {/* Authenticated routes */}
      <Route path="/" element={<AuthenticatedLayout />}>
        <Route path="dashboard" element={<DashboardLayout />}>
          <Route index element={<DashboardHome />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="reports" element={<Reports />} />
        </Route>

        {/* User management */}
        <Route path="users" element={<UsersLayout />}>
          <Route index element={<UsersList />} />
          <Route path="create" element={<CreateUser />} />
          <Route path=":userId" element={<UserDetailLayout />}>
            <Route index element={<UserProfile />} />
            <Route path="edit" element={<EditUser />} />
            <Route path="posts" element={<UserPosts />} />
            <Route path="activity" element={<UserActivity />} />
          </Route>
        </Route>

        {/* Content management */}
        <Route path="content" element={<ContentLayout />}>
          <Route index element={<ContentDashboard />} />
          
          <Route path="posts" element={<PostsLayout />}>
            <Route index element={<PostsList />} />
            <Route path="create" element={<CreatePost />} />
            <Route path=":postId" element={<PostDetailLayout />}>
              <Route index element={<PostView />} />
              <Route path="edit" element={<EditPost />} />
              <Route path="comments" element={<PostComments />} />
            </Route>
          </Route>
          
          <Route path="media" element={<MediaLayout />}>
            <Route index element={<MediaLibrary />} />
            <Route path="upload" element={<MediaUpload />} />
            <Route path=":mediaId" element={<MediaDetail />} />
          </Route>
        </Route>
      </Route>

      {/* Admin routes */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        <Route path="system" element={<SystemSettings />} />
        <Route path="logs" element={<SystemLogs />} />
      </Route>
    </Routes>
  );
}
```

### Route Configuration with Metadata
```jsx
// config/routeConfig.js
export const routeConfig = {
  public: {
    layout: 'PublicLayout',
    routes: [
      { path: '/', component: 'Home', title: 'Home' },
      { path: '/about', component: 'About', title: 'About Us' },
      { path: '/contact', component: 'Contact', title: 'Contact' }
    ]
  },
  
  dashboard: {
    layout: 'DashboardLayout',
    basePath: '/dashboard',
    requiresAuth: true,
    routes: [
      { 
        path: '', 
        component: 'DashboardHome', 
        title: 'Dashboard',
        breadcrumbs: ['Dashboard']
      },
      { 
        path: '/analytics', 
        component: 'Analytics', 
        title: 'Analytics',
        breadcrumbs: ['Dashboard', 'Analytics']
      },
      { 
        path: '/reports', 
        component: 'Reports', 
        title: 'Reports',
        breadcrumbs: ['Dashboard', 'Reports']
      }
    ]
  },
  
  users: {
    layout: 'UsersLayout',
    basePath: '/users',
    requiresAuth: true,
    routes: [
      {
        path: '',
        component: 'UsersList',
        title: 'Users',
        breadcrumbs: ['Users']
      },
      {
        path: '/:userId',
        component: 'UserProfile',
        title: 'User Profile',
        breadcrumbs: ['Users', 'Profile'],
        children: [
          { path: '', component: 'UserOverview' },
          { path: '/posts', component: 'UserPosts' },
          { path: '/settings', component: 'UserSettings' }
        ]
      }
    ]
  }
};

// Route generator
function generateNestedRoutes(config, layouts, components) {
  return Object.entries(config).map(([key, section]) => {
    const Layout = layouts[section.layout];
    
    return (
      <Route
        key={key}
        path={section.basePath || '/'}
        element={
          section.requiresAuth ? (
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          ) : (
            <Layout />
          )
        }
      >
        {section.routes.map(route => {
          const Component = components[route.component];
          
          if (route.children) {
            return (
              <Route key={route.path} path={route.path} element={<Component />}>
                {route.children.map(child => {
                  const ChildComponent = components[child.component];
                  return (
                    <Route
                      key={child.path}
                      path={child.path}
                      element={<ChildComponent />}
                    />
                  );
                })}
              </Route>
            );
          }
          
          return (
            <Route
              key={route.path}
              path={route.path}
              element={<Component />}
            />
          );
        })}
      </Route>
    );
  });
}
```

## Data Flow in Nested Routes

### Context-Based Data Sharing
```jsx
import { createContext, useContext, useState, useEffect } from 'react';

// Layout-specific context
const DashboardContext = createContext();

export function DashboardProvider({ children }) {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [userRes, permissionsRes, settingsRes] = await Promise.all([
          fetch('/api/user/current'),
          fetch('/api/user/permissions'),
          fetch('/api/user/settings')
        ]);

        const [userData, permissionsData, settingsData] = await Promise.all([
          userRes.json(),
          permissionsRes.json(),
          settingsRes.json()
        ]);

        setUser(userData);
        setPermissions(permissionsData);
        setSettings(settingsData);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  return (
    <DashboardContext.Provider value={{
      user,
      permissions,
      settings,
      loading,
      updateSettings: setSettings
    }}>
      {children}
    </DashboardContext.Provider>
  );
}

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within DashboardProvider');
  }
  return context;
};

// Layout component with context
function DashboardLayout() {
  return (
    <DashboardProvider>
      <div className="dashboard-layout">
        <DashboardSidebar />
        <main className="dashboard-main">
          <Outlet />
        </main>
      </div>
    </DashboardProvider>
  );
}

// Child component using context
function Analytics() {
  const { user, permissions } = useDashboard();

  if (!permissions.includes('view_analytics')) {
    return <div>Access denied</div>;
  }

  return (
    <div className="analytics">
      <h1>Analytics for {user.name}</h1>
      {/* Analytics content */}
    </div>
  );
}
```

### Loader Pattern for Data Fetching
```jsx
// hooks/useRouteData.js
import { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';

export function useRouteData(dataLoader, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const params = useParams();
  const location = useLocation();

  useEffect(() => {
    let cancelled = false;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const result = await dataLoader(params, location);
        
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      cancelled = true;
    };
  }, [params, location, ...dependencies]);

  return { data, loading, error, refetch: () => loadData() };
}

// Usage in layout
function UserLayout() {
  const { data: user, loading, error } = useRouteData(
    async (params) => {
      const response = await fetch(`/api/users/${params.userId}`);
      return response.json();
    }
  );

  if (loading) return <div>Loading user...</div>;
  if (error) return <div>Error loading user</div>;

  return (
    <div className="user-layout">
      <UserHeader user={user} />
      <UserNavigation userId={user.id} />
      <Outlet context={{ user }} />
    </div>
  );
}
```

## Advanced Layout Patterns

### Modal Routes in Nested Layouts
```jsx
function AppWithModals() {
  const location = useLocation();
  const background = location.state?.background;

  return (
    <div className="app">
      {/* Main routes */}
      <Routes location={background || location}>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="gallery" element={<Gallery />} />
          <Route path="users" element={<UsersLayout />}>
            <Route index element={<UsersList />} />
            <Route path=":userId" element={<UserProfile />} />
          </Route>
        </Route>
      </Routes>

      {/* Modal routes */}
      {background && (
        <Routes>
          <Route 
            path="/gallery/:photoId" 
            element={<PhotoModal />} 
          />
          <Route 
            path="/users/:userId/edit" 
            element={<EditUserModal />} 
          />
        </Routes>
      )}
    </div>
  );
}

function PhotoModal() {
  const navigate = useNavigate();
  const { photoId } = useParams();

  return (
    <Modal onClose={() => navigate(-1)}>
      <PhotoViewer photoId={photoId} />
    </Modal>
  );
}
```

### Conditional Layout Rendering
```jsx
function ConditionalLayout() {
  const { user } = useAuth();
  const location = useLocation();

  // Different layouts based on user role
  if (user?.role === 'admin') {
    return <AdminLayout />;
  }

  if (user?.role === 'moderator') {
    return <ModeratorLayout />;
  }

  // Different layouts based on route
  if (location.pathname.startsWith('/dashboard')) {
    return <DashboardLayout />;
  }

  if (location.pathname.startsWith('/profile')) {
    return <ProfileLayout />;
  }

  return <DefaultLayout />;
}
```

### Split Layout with Independent Navigation
```jsx
function SplitLayout() {
  return (
    <div className="split-layout">
      <div className="left-panel">
        <Routes>
          <Route path="/split/left/*" element={<LeftPanelRoutes />} />
        </Routes>
      </div>
      
      <div className="right-panel">
        <Routes>
          <Route path="/split/right/*" element={<RightPanelRoutes />} />
        </Routes>
      </div>
    </div>
  );
}

function LeftPanelRoutes() {
  return (
    <Routes>
      <Route index element={<LeftHome />} />
      <Route path="settings" element={<LeftSettings />} />
      <Route path="profile" element={<LeftProfile />} />
    </Routes>
  );
}

function RightPanelRoutes() {
  return (
    <Routes>
      <Route index element={<RightHome />} />
      <Route path="details/:id" element={<RightDetails />} />
      <Route path="edit/:id" element={<RightEdit />} />
    </Routes>
  );
}
```

## Performance Optimization

### Lazy Loading Nested Routes
```jsx
import { lazy, Suspense } from 'react';

// Lazy load layout components
const DashboardLayout = lazy(() => import('./layouts/DashboardLayout'));
const UsersLayout = lazy(() => import('./layouts/UsersLayout'));
const ContentLayout = lazy(() => import('./layouts/ContentLayout'));

// Lazy load page components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analytics = lazy(() => import('./pages/Analytics'));
const UsersList = lazy(() => import('./pages/UsersList'));
const UserProfile = lazy(() => import('./pages/UserProfile'));

function OptimizedRoutes() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          
          <Route path="dashboard" element={<DashboardLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="analytics" element={<Analytics />} />
          </Route>
          
          <Route path="users" element={<UsersLayout />}>
            <Route index element={<UsersList />} />
            <Route path=":userId" element={<UserProfile />} />
          </Route>
        </Route>
      </Routes>
    </Suspense>
  );
}

// Preload critical routes
function preloadCriticalRoutes() {
  // Preload dashboard after initial load
  setTimeout(() => {
    import('./layouts/DashboardLayout');
    import('./pages/Dashboard');
  }, 2000);
}
```

### Route-Based Code Splitting
```jsx
// utils/routeSplitting.js
const createLazyRoute = (importFn, fallback = <div>Loading...</div>) => {
  const LazyComponent = lazy(importFn);
  
  return (props) => (
    <Suspense fallback={fallback}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Usage
const LazyDashboard = createLazyRoute(
  () => import('./pages/Dashboard'),
  <DashboardSkeleton />
);

const LazyUserProfile = createLazyRoute(
  () => import('./pages/UserProfile'),
  <ProfileSkeleton />
);
```

## Best Practices

### 1. Layout Component Organization
```jsx
// layouts/
//   ├── BaseLayout.jsx
//   ├── PublicLayout.jsx
//   ├── AuthenticatedLayout.jsx
//   ├── DashboardLayout.jsx
//   └── AdminLayout.jsx

// Base layout with common functionality
function BaseLayout({ children, className = '' }) {
  const [theme, setTheme] = useTheme();
  const [loading, setLoading] = useState(false);

  return (
    <div className={`base-layout ${theme} ${className}`}>
      {loading && <LoadingOverlay />}
      <ErrorBoundary>
        {children}
      </ErrorBoundary>
      <Notifications />
    </div>
  );
}

// Specialized layouts extending base
function DashboardLayout() {
  return (
    <BaseLayout className="dashboard">
      <DashboardSidebar />
      <main className="dashboard-main">
        <Outlet />
      </main>
    </BaseLayout>
  );
}
```

### 2. Route Component Composition
```jsx
// components/RouteGuard.jsx
function RouteGuard({ children, requiresAuth = false, requiredRole = null }) {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();

  if (requiresAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && (!user || user.role !== requiredRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}

// Usage in routes
<Route path="/admin" element={
  <RouteGuard requiresAuth requiredRole="admin">
    <AdminLayout />
  </RouteGuard>
}>
  <Route index element={<AdminDashboard />} />
</Route>
```

### 3. Breadcrumb Integration
```jsx
// hooks/useBreadcrumbs.js
export function useBreadcrumbs() {
  const location = useLocation();
  const { user } = useAuth();
  
  const breadcrumbs = useMemo(() => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const crumbs = [{ label: 'Home', path: '/' }];
    
    let currentPath = '';
    
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      
      // Generate breadcrumb label based on segment
      let label = segment.charAt(0).toUpperCase() + segment.slice(1);
      
      // Special cases for dynamic segments
      if (segment.match(/^\d+$/)) {
        // Numeric ID - fetch name if needed
        label = `Item ${segment}`;
      }
      
      crumbs.push({
        label,
        path: currentPath,
        isLast: index === pathSegments.length - 1
      });
    });
    
    return crumbs;
  }, [location.pathname]);
  
  return breadcrumbs;
}

// Breadcrumb component
function Breadcrumbs() {
  const breadcrumbs = useBreadcrumbs();
  
  return (
    <nav className="breadcrumbs">
      {breadcrumbs.map((crumb, index) => (
        <span key={crumb.path}>
          {index > 0 && ' > '}
          {crumb.isLast ? (
            <span className="current">{crumb.label}</span>
          ) : (
            <Link to={crumb.path}>{crumb.label}</Link>
          )}
        </span>
      ))}
    </nav>
  );
}
```

## Real-World Examples

### E-commerce Admin Dashboard
```jsx
function EcommerceAdminRoutes() {
  return (
    <Routes>
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminDashboard />} />
        
        {/* Product Management */}
        <Route path="products" element={<ProductsLayout />}>
          <Route index element={<ProductsList />} />
          <Route path="create" element={<CreateProduct />} />
          <Route path=":productId" element={<ProductDetailLayout />}>
            <Route index element={<ProductOverview />} />
            <Route path="edit" element={<EditProduct />} />
            <Route path="variants" element={<ProductVariants />} />
            <Route path="media" element={<ProductMedia />} />
            <Route path="seo" element={<ProductSEO />} />
          </Route>
          <Route path="categories" element={<CategoriesLayout />}>
            <Route index element={<CategoriesList />} />
            <Route path="create" element={<CreateCategory />} />
            <Route path=":categoryId" element={<CategoryDetail />} />
          </Route>
        </Route>
        
        {/* Order Management */}
        <Route path="orders" element={<OrdersLayout />}>
          <Route index element={<OrdersList />} />
          <Route path=":orderId" element={<OrderDetailLayout />}>
            <Route index element={<OrderOverview />} />
            <Route path="items" element={<OrderItems />} />
            <Route path="shipping" element={<OrderShipping />} />
            <Route path="payment" element={<OrderPayment />} />
            <Route path="history" element={<OrderHistory />} />
          </Route>
        </Route>
        
        {/* Customer Management */}
        <Route path="customers" element={<CustomersLayout />}>
          <Route index element={<CustomersList />} />
          <Route path=":customerId" element={<CustomerDetailLayout />}>
            <Route index element={<CustomerProfile />} />
            <Route path="orders" element={<CustomerOrders />} />
            <Route path="addresses" element={<CustomerAddresses />} />
            <Route path="payment-methods" element={<CustomerPayments />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}
```

### Social Media Platform
```jsx
function SocialMediaRoutes() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Feed />} />
        <Route path="explore" element={<Explore />} />
        
        {/* User Profiles */}
        <Route path="users/:username" element={<UserProfileLayout />}>
          <Route index element={<UserPosts />} />
          <Route path="about" element={<UserAbout />} />
          <Route path="photos" element={<UserPhotos />} />
          <Route path="videos" element={<UserVideos />} />
          <Route path="followers" element={<UserFollowers />} />
          <Route path="following" element={<UserFollowing />} />
        </Route>
        
        {/* Content */}
        <Route path="posts/:postId" element={<PostDetailLayout />}>
          <Route index element={<PostView />} />
          <Route path="comments" element={<PostComments />} />
          <Route path="likes" element={<PostLikes />} />
          <Route path="shares" element={<PostShares />} />
        </Route>
        
        {/* Groups */}
        <Route path="groups" element={<GroupsLayout />}>
          <Route index element={<GroupsList />} />
          <Route path="discover" element={<DiscoverGroups />} />
          <Route path=":groupId" element={<GroupDetailLayout />}>
            <Route index element={<GroupFeed />} />
            <Route path="about" element={<GroupAbout />} />
            <Route path="members" element={<GroupMembers />} />
            <Route path="events" element={<GroupEvents />} />
            <Route path="photos" element={<GroupPhotos />} />
          </Route>
        </Route>
        
        {/* Messages */}
        <Route path="messages" element={<MessagesLayout />}>
          <Route index element={<MessagesList />} />
          <Route path=":conversationId" element={<Conversation />} />
        </Route>
      </Route>
    </Routes>
  );
}
```

This comprehensive guide covers nested routes and layout patterns in React Router v6. The next section will focus on protected routes and authentication patterns.