# Protected Routes & Authentication

## 🎯 Learning Objectives
By the end of this section, you will:
- Implement authentication-based route protection
- Build role-based access control systems
- Create secure routing patterns
- Handle authentication redirects and state
- Implement route guards and middleware
- Build logout and session management
- Handle authentication errors and edge cases
- Optimize authentication performance

## 📚 Table of Contents
1. [Authentication Fundamentals](#authentication-fundamentals)
2. [Protected Route Implementation](#protected-route-implementation)
3. [Role-Based Access Control](#role-based-access-control)
4. [Authentication Context](#authentication-context)
5. [Route Guards & Middleware](#route-guards--middleware)
6. [Redirect Handling](#redirect-handling)
7. [Session Management](#session-management)
8. [Error Handling](#error-handling)
9. [Performance Optimization](#performance-optimization)
10. [Best Practices](#best-practices)

## Authentication Fundamentals

### Basic Authentication Setup
```jsx
// context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) {
          setLoading(false);
          return;
        }

        const response = await fetch('/api/auth/verify', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          localStorage.removeItem('authToken');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('authToken');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const { user: userData, token } = await response.json();
      
      localStorage.setItem('authToken', token);
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('authToken');
      setUser(null);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      const { user: newUser, token } = await response.json();
      
      localStorage.setItem('authToken', token);
      setUser(newUser);
      
      return { success: true };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    register,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Authentication Hook with Persistence
```jsx
// hooks/useAuthPersistence.js
import { useState, useEffect } from 'react';

export function useAuthPersistence() {
  const [authState, setAuthState] = useState({
    user: null,
    token: null,
    isAuthenticated: false,
    loading: true
  });

  useEffect(() => {
    const loadPersistedAuth = async () => {
      try {
        // Check multiple storage mechanisms
        const token = localStorage.getItem('authToken') || 
                     sessionStorage.getItem('authToken');
        
        if (!token) {
          setAuthState(prev => ({ ...prev, loading: false }));
          return;
        }

        // Verify token validity
        const response = await fetch('/api/auth/verify', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
          const userData = await response.json();
          setAuthState({
            user: userData,
            token,
            isAuthenticated: true,
            loading: false
          });
        } else {
          // Invalid token, clear storage
          localStorage.removeItem('authToken');
          sessionStorage.removeItem('authToken');
          setAuthState(prev => ({ ...prev, loading: false }));
        }
      } catch (error) {
        console.error('Auth persistence error:', error);
        setAuthState(prev => ({ ...prev, loading: false }));
      }
    };

    loadPersistedAuth();
  }, []);

  const persistAuth = (user, token, rememberMe = false) => {
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem('authToken', token);
    
    setAuthState({
      user,
      token,
      isAuthenticated: true,
      loading: false
    });
  };

  const clearAuth = () => {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false
    });
  };

  return {
    ...authState,
    persistAuth,
    clearAuth
  };
}
```

## Protected Route Implementation

### Basic Protected Route Component
```jsx
// components/ProtectedRoute.jsx
import { useAuth } from '../context/AuthContext';
import { Navigate, useLocation } from 'react-router-dom';

function ProtectedRoute({ children, fallback = null }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return fallback || <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    // Redirect to login with current location
    return (
      <Navigate 
        to="/login" 
        state={{ from: location }} 
        replace 
      />
    );
  }

  return children;
}

export default ProtectedRoute;
```

### Advanced Protected Route with Role Check
```jsx
// components/AdvancedProtectedRoute.jsx
import { useAuth } from '../context/AuthContext';
import { Navigate, useLocation } from 'react-router-dom';

function AdvancedProtectedRoute({ 
  children, 
  requiredRole = null,
  requiredPermissions = [],
  fallback = null,
  unauthorizedFallback = null
}) {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return fallback || <div>Checking authentication...</div>;
  }

  if (!isAuthenticated) {
    return (
      <Navigate 
        to="/login" 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // Check role requirements
  if (requiredRole && user.role !== requiredRole) {
    return unauthorizedFallback || (
      <Navigate to="/unauthorized" replace />
    );
  }

  // Check permission requirements
  if (requiredPermissions.length > 0) {
    const hasPermissions = requiredPermissions.every(permission =>
      user.permissions?.includes(permission)
    );

    if (!hasPermissions) {
      return unauthorizedFallback || (
        <Navigate to="/unauthorized" replace />
      );
    }
  }

  return children;
}

export default AdvancedProtectedRoute;
```

### Route Configuration with Protection
```jsx
// routes/AppRoutes.jsx
import { Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import AdvancedProtectedRoute from '../components/AdvancedProtectedRoute';

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      
      {/* Protected routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Admin only routes */}
      <Route path="/admin" element={
        <AdvancedProtectedRoute requiredRole="admin">
          <AdminLayout />
        </AdvancedProtectedRoute>
      }>
        <Route index element={<AdminDashboard />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="settings" element={<AdminSettings />} />
      </Route>

      {/* Permission-based routes */}
      <Route path="/reports" element={
        <AdvancedProtectedRoute 
          requiredPermissions={['view_reports', 'access_analytics']}
        >
          <ReportsLayout />
        </AdvancedProtectedRoute>
      }>
        <Route index element={<ReportsList />} />
        <Route path=":reportId" element={<ReportDetail />} />
      </Route>

      {/* Error routes */}
      <Route path="/unauthorized" element={<Unauthorized />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
```

## Role-Based Access Control

### Role and Permission System
```jsx
// utils/rbac.js
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  MODERATOR: 'moderator',
  USER: 'user',
  GUEST: 'guest'
};

export const PERMISSIONS = {
  // User management
  CREATE_USER: 'create_user',
  READ_USER: 'read_user',
  UPDATE_USER: 'update_user',
  DELETE_USER: 'delete_user',
  
  // Content management
  CREATE_CONTENT: 'create_content',
  READ_CONTENT: 'read_content',
  UPDATE_CONTENT: 'update_content',
  DELETE_CONTENT: 'delete_content',
  MODERATE_CONTENT: 'moderate_content',
  
  // System administration
  SYSTEM_CONFIG: 'system_config',
  VIEW_LOGS: 'view_logs',
  MANAGE_ROLES: 'manage_roles'
};

export const ROLE_PERMISSIONS = {
  [ROLES.SUPER_ADMIN]: Object.values(PERMISSIONS),
  [ROLES.ADMIN]: [
    PERMISSIONS.CREATE_USER,
    PERMISSIONS.READ_USER,
    PERMISSIONS.UPDATE_USER,
    PERMISSIONS.DELETE_USER,
    PERMISSIONS.CREATE_CONTENT,
    PERMISSIONS.READ_CONTENT,
    PERMISSIONS.UPDATE_CONTENT,
    PERMISSIONS.DELETE_CONTENT,
    PERMISSIONS.MODERATE_CONTENT,
    PERMISSIONS.VIEW_LOGS
  ],
  [ROLES.MODERATOR]: [
    PERMISSIONS.READ_USER,
    PERMISSIONS.UPDATE_USER,
    PERMISSIONS.CREATE_CONTENT,
    PERMISSIONS.READ_CONTENT,
    PERMISSIONS.UPDATE_CONTENT,
    PERMISSIONS.MODERATE_CONTENT
  ],
  [ROLES.USER]: [
    PERMISSIONS.READ_USER,
    PERMISSIONS.CREATE_CONTENT,
    PERMISSIONS.READ_CONTENT,
    PERMISSIONS.UPDATE_CONTENT
  ],
  [ROLES.GUEST]: [
    PERMISSIONS.READ_CONTENT
  ]
};

export function hasPermission(user, permission) {
  if (!user || !user.role) return false;
  
  const rolePermissions = ROLE_PERMISSIONS[user.role] || [];
  return rolePermissions.includes(permission);
}

export function hasAnyPermission(user, permissions) {
  return permissions.some(permission => hasPermission(user, permission));
}

export function hasAllPermissions(user, permissions) {
  return permissions.every(permission => hasPermission(user, permission));
}

export function canAccess(user, requiredRole, requiredPermissions = []) {
  // Check role hierarchy
  const roleHierarchy = [
    ROLES.GUEST,
    ROLES.USER,
    ROLES.MODERATOR,
    ROLES.ADMIN,
    ROLES.SUPER_ADMIN
  ];
  
  const userRoleIndex = roleHierarchy.indexOf(user?.role);
  const requiredRoleIndex = roleHierarchy.indexOf(requiredRole);
  
  if (requiredRole && userRoleIndex < requiredRoleIndex) {
    return false;
  }
  
  // Check permissions
  if (requiredPermissions.length > 0) {
    return hasAllPermissions(user, requiredPermissions);
  }
  
  return true;
}
```

### RBAC Hook
```jsx
// hooks/useRBAC.js
import { useAuth } from '../context/AuthContext';
import { hasPermission, hasAnyPermission, hasAllPermissions, canAccess } from '../utils/rbac';

export function useRBAC() {
  const { user } = useAuth();

  return {
    user,
    hasPermission: (permission) => hasPermission(user, permission),
    hasAnyPermission: (permissions) => hasAnyPermission(user, permissions),
    hasAllPermissions: (permissions) => hasAllPermissions(user, permissions),
    canAccess: (requiredRole, requiredPermissions) => 
      canAccess(user, requiredRole, requiredPermissions),
    isRole: (role) => user?.role === role,
    isAdmin: () => ['admin', 'super_admin'].includes(user?.role),
    isSuperAdmin: () => user?.role === 'super_admin'
  };
}
```

### Permission-Based Component Rendering
```jsx
// components/PermissionGate.jsx
import { useRBAC } from '../hooks/useRBAC';

function PermissionGate({ 
  children, 
  permission = null,
  permissions = [],
  role = null,
  requireAll = true,
  fallback = null 
}) {
  const { hasPermission, hasAnyPermission, hasAllPermissions, canAccess } = useRBAC();

  let hasAccess = true;

  if (permission) {
    hasAccess = hasPermission(permission);
  } else if (permissions.length > 0) {
    hasAccess = requireAll 
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions);
  } else if (role) {
    hasAccess = canAccess(role);
  }

  if (!hasAccess) {
    return fallback;
  }

  return children;
}

// Usage examples
function AdminPanel() {
  return (
    <div>
      <h1>Dashboard</h1>
      
      <PermissionGate permission="create_user">
        <button>Create User</button>
      </PermissionGate>
      
      <PermissionGate 
        permissions={['delete_user', 'manage_roles']}
        requireAll={false}
      >
        <button>Advanced Actions</button>
      </PermissionGate>
      
      <PermissionGate 
        role="admin"
        fallback={<div>Admin access required</div>}
      >
        <AdminSettings />
      </PermissionGate>
    </div>
  );
}
```

## Authentication Context

### Enhanced Authentication Context
```jsx
// context/EnhancedAuthContext.jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';

const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, loading: true, error: null };
      
    case 'AUTH_SUCCESS':
      return {
        ...state,
        loading: false,
        error: null,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true
      };
      
    case 'AUTH_FAILURE':
      return {
        ...state,
        loading: false,
        error: action.payload,
        user: null,
        token: null,
        isAuthenticated: false
      };
      
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        error: null
      };
      
    case 'UPDATE_USER':
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
      
    case 'CLEAR_ERROR':
      return { ...state, error: null };
      
    default:
      return state;
  }
};

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
  error: null
};

export function EnhancedAuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Auto-refresh token
  useEffect(() => {
    if (!state.token) return;

    const refreshInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/auth/refresh', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${state.token}`
          }
        });

        if (response.ok) {
          const { token } = await response.json();
          localStorage.setItem('authToken', token);
          dispatch({
            type: 'UPDATE_TOKEN',
            payload: { token }
          });
        }
      } catch (error) {
        console.error('Token refresh failed:', error);
      }
    }, 15 * 60 * 1000); // Refresh every 15 minutes

    return () => clearInterval(refreshInterval);
  }, [state.token]);

  // Session timeout
  useEffect(() => {
    let timeoutId;

    const resetTimeout = () => {
      if (timeoutId) clearTimeout(timeoutId);
      
      if (state.isAuthenticated) {
        timeoutId = setTimeout(() => {
          dispatch({ type: 'AUTH_LOGOUT' });
          localStorage.removeItem('authToken');
        }, 30 * 60 * 1000); // 30 minutes
      }
    };

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    
    events.forEach(event => {
      document.addEventListener(event, resetTimeout, true);
    });

    resetTimeout();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      events.forEach(event => {
        document.removeEventListener(event, resetTimeout, true);
      });
    };
  }, [state.isAuthenticated]);

  const login = async (credentials, rememberMe = false) => {
    dispatch({ type: 'AUTH_START' });

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const { user, token } = await response.json();
      
      if (rememberMe) {
        localStorage.setItem('authToken', token);
      } else {
        sessionStorage.setItem('authToken', token);
      }

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, token }
      });

      return { success: true };
    } catch (error) {
      dispatch({
        type: 'AUTH_FAILURE',
        payload: error.message
      });
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${state.token}`
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('authToken');
      sessionStorage.removeItem('authToken');
      dispatch({ type: 'AUTH_LOGOUT' });
    }
  };

  const updateUser = (updates) => {
    dispatch({ type: 'UPDATE_USER', payload: updates });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value = {
    ...state,
    login,
    logout,
    updateUser,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useEnhancedAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useEnhancedAuth must be used within EnhancedAuthProvider');
  }
  return context;
};
```

## Route Guards & Middleware

### Route Guard Hook
```jsx
// hooks/useRouteGuard.js
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { canAccess } from '../utils/rbac';

export function useRouteGuard(options = {}) {
  const {
    requiresAuth = false,
    requiredRole = null,
    requiredPermissions = [],
    redirectTo = '/login',
    onUnauthorized = null
  } = options;

  const { user, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (loading) return;

    // Check authentication
    if (requiresAuth && !isAuthenticated) {
      navigate(redirectTo, {
        state: { from: location.pathname },
        replace: true
      });
      return;
    }

    // Check authorization
    if (isAuthenticated && !canAccess(user, requiredRole, requiredPermissions)) {
      if (onUnauthorized) {
        onUnauthorized();
      } else {
        navigate('/unauthorized', { replace: true });
      }
      return;
    }
  }, [
    isAuthenticated, 
    user, 
    loading, 
    requiresAuth, 
    requiredRole, 
    requiredPermissions,
    redirectTo,
    navigate,
    location,
    onUnauthorized
  ]);

  return {
    canAccess: isAuthenticated && canAccess(user, requiredRole, requiredPermissions),
    isLoading: loading
  };
}
```

### Route Middleware Component
```jsx
// components/RouteMiddleware.jsx
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

function RouteMiddleware({ 
  children, 
  middlewares = [],
  fallback = <div>Loading...</div>
}) {
  const [middlewareState, setMiddlewareState] = useState({
    loading: true,
    passed: false,
    error: null
  });

  const auth = useAuth();

  useEffect(() => {
    const runMiddlewares = async () => {
      try {
        setMiddlewareState({ loading: true, passed: false, error: null });

        for (const middleware of middlewares) {
          const result = await middleware(auth);
          if (!result.passed) {
            setMiddlewareState({
              loading: false,
              passed: false,
              error: result.error || 'Middleware check failed'
            });
            return;
          }
        }

        setMiddlewareState({ loading: false, passed: true, error: null });
      } catch (error) {
        setMiddlewareState({
          loading: false,
          passed: false,
          error: error.message
        });
      }
    };

    runMiddlewares();
  }, [middlewares, auth]);

  if (middlewareState.loading) {
    return fallback;
  }

  if (!middlewareState.passed) {
    return <div>Access denied: {middlewareState.error}</div>;
  }

  return children;
}

// Middleware functions
const authMiddleware = async (auth) => {
  if (!auth.isAuthenticated) {
    return { passed: false, error: 'Authentication required' };
  }
  return { passed: true };
};

const roleMiddleware = (requiredRole) => async (auth) => {
  if (auth.user?.role !== requiredRole) {
    return { passed: false, error: `Role ${requiredRole} required` };
  }
  return { passed: true };
};

const permissionMiddleware = (permissions) => async (auth) => {
  const hasPermissions = permissions.every(permission =>
    auth.user?.permissions?.includes(permission)
  );
  
  if (!hasPermissions) {
    return { passed: false, error: 'Insufficient permissions' };
  }
  return { passed: true };
};

// Usage
function AdminRoute({ children }) {
  return (
    <RouteMiddleware
      middlewares={[
        authMiddleware,
        roleMiddleware('admin'),
        permissionMiddleware(['admin_access'])
      ]}
    >
      {children}
    </RouteMiddleware>
  );
}
```

## Redirect Handling

### Advanced Redirect Management
```jsx
// hooks/useRedirect.js
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function useRedirect() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  const redirectAfterLogin = () => {
    const from = location.state?.from || '/dashboard';
    navigate(from, { replace: true });
  };

  const redirectToLogin = (returnUrl = null) => {
    const from = returnUrl || location.pathname + location.search;
    navigate('/login', {
      state: { from },
      replace: true
    });
  };

  const conditionalRedirect = (condition, to, replace = false) => {
    if (condition) {
      navigate(to, { replace });
    }
  };

  const smartRedirect = (to, options = {}) => {
    const { requiresAuth = false, fallback = '/login' } = options;
    
    if (requiresAuth && !isAuthenticated) {
      redirectToLogin(to);
    } else {
      navigate(to, options);
    }
  };

  return {
    redirectAfterLogin,
    redirectToLogin,
    conditionalRedirect,
    smartRedirect
  };
}
```

### Login Component with Redirect
```jsx
// components/Login.jsx
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useRedirect } from '../hooks/useRedirect';
import { useLocation } from 'react-router-dom';

function Login() {
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [loading, setLoading] = useState(false);

  const { login, error } = useAuth();
  const { redirectAfterLogin } = useRedirect();
  const location = useLocation();

  const from = location.state?.from || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await login(credentials, credentials.rememberMe);
    
    if (result.success) {
      redirectAfterLogin();
    }
    
    setLoading(false);
  };

  return (
    <div className="login-form">
      <h1>Login</h1>
      
      {from !== '/dashboard' && (
        <p className="redirect-notice">
          Please log in to access {from}
        </p>
      )}

      {error && (
        <div className="error-message">{error}</div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={credentials.email}
            onChange={(e) => setCredentials(prev => ({
              ...prev,
              email: e.target.value
            }))}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials(prev => ({
              ...prev,
              password: e.target.value
            }))}
            required
          />
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={credentials.rememberMe}
              onChange={(e) => setCredentials(prev => ({
                ...prev,
                rememberMe: e.target.checked
              }))}
            />
            Remember me
          </label>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}
```

## Session Management

### Session Monitoring
```jsx
// hooks/useSessionMonitor.js
import { useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

export function useSessionMonitor(options = {}) {
  const {
    warningTime = 5 * 60 * 1000, // 5 minutes before expiry
    sessionDuration = 30 * 60 * 1000, // 30 minutes
    onWarning = null,
    onExpiry = null
  } = options;

  const { isAuthenticated, logout } = useAuth();
  const lastActivityRef = useRef(Date.now());
  const warningTimerRef = useRef(null);
  const expiryTimerRef = useRef(null);

  const resetTimers = () => {
    lastActivityRef.current = Date.now();
    
    if (warningTimerRef.current) {
      clearTimeout(warningTimerRef.current);
    }
    if (expiryTimerRef.current) {
      clearTimeout(expiryTimerRef.current);
    }

    if (isAuthenticated) {
      // Set warning timer
      warningTimerRef.current = setTimeout(() => {
        if (onWarning) {
          onWarning();
        }
      }, sessionDuration - warningTime);

      // Set expiry timer
      expiryTimerRef.current = setTimeout(() => {
        if (onExpiry) {
          onExpiry();
        } else {
          logout();
        }
      }, sessionDuration);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) return;

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    
    const handleActivity = () => {
      resetTimers();
    };

    events.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    resetTimers();

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
      
      if (warningTimerRef.current) {
        clearTimeout(warningTimerRef.current);
      }
      if (expiryTimerRef.current) {
        clearTimeout(expiryTimerRef.current);
      }
    };
  }, [isAuthenticated, sessionDuration, warningTime]);

  const extendSession = () => {
    resetTimers();
  };

  const getTimeRemaining = () => {
    const elapsed = Date.now() - lastActivityRef.current;
    return Math.max(0, sessionDuration - elapsed);
  };

  return {
    extendSession,
    getTimeRemaining
  };
}
```

### Session Warning Component
```jsx
// components/SessionWarning.jsx
import { useState, useEffect } from 'react';
import { useSessionMonitor } from '../hooks/useSessionMonitor';

function SessionWarning() {
  const [showWarning, setShowWarning] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);

  const { extendSession, getTimeRemaining } = useSessionMonitor({
    onWarning: () => {
      setShowWarning(true);
      setTimeRemaining(getTimeRemaining());
    },
    onExpiry: () => {
      setShowWarning(false);
      // Logout handled by useSessionMonitor
    }
  });

  useEffect(() => {
    if (!showWarning) return;

    const interval = setInterval(() => {
      const remaining = getTimeRemaining();
      setTimeRemaining(remaining);
      
      if (remaining <= 0) {
        setShowWarning(false);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [showWarning, getTimeRemaining]);

  const handleExtend = () => {
    extendSession();
    setShowWarning(false);
  };

  if (!showWarning) return null;

  const minutes = Math.floor(timeRemaining / 60000);
  const seconds = Math.floor((timeRemaining % 60000) / 1000);

  return (
    <div className="session-warning-overlay">
      <div className="session-warning-dialog">
        <h3>Session Expiring Soon</h3>
        <p>
          Your session will expire in {minutes}:{seconds.toString().padStart(2, '0')}
        </p>
        <div className="session-warning-actions">
          <button onClick={handleExtend}>
            Extend Session
          </button>
          <button onClick={() => setShowWarning(false)}>
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Error Handling

### Authentication Error Boundary
```jsx
// components/AuthErrorBoundary.jsx
import React from 'react';

class AuthErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    if (error.name === 'AuthenticationError' || error.status === 401) {
      return { hasError: true, error };
    }
    return null;
  }

  componentDidCatch(error, errorInfo) {
    if (error.name === 'AuthenticationError' || error.status === 401) {
      console.error('Authentication Error:', error, errorInfo);
      
      // Clear authentication state
      localStorage.removeItem('authToken');
      sessionStorage.removeItem('authToken');
      
      // Redirect to login
      window.location.href = '/login';
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="auth-error">
          <h2>Authentication Error</h2>
          <p>Please log in again to continue.</p>
          <button onClick={() => window.location.href = '/login'}>
            Go to Login
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### API Error Handler
```jsx
// utils/apiErrorHandler.js
import { useAuth } from '../context/AuthContext';

export function useApiErrorHandler() {
  const { logout } = useAuth();

  const handleApiError = async (response) => {
    if (response.status === 401) {
      // Unauthorized - token expired or invalid
      await logout();
      throw new Error('Session expired. Please log in again.');
    }

    if (response.status === 403) {
      // Forbidden - insufficient permissions
      throw new Error('Access denied. Insufficient permissions.');
    }

    if (response.status >= 500) {
      // Server error
      throw new Error('Server error. Please try again later.');
    }

    // Other client errors
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Error: ${response.status}`);
  };

  return { handleApiError };
}

// Enhanced fetch with error handling
export function useAuthenticatedFetch() {
  const { logout } = useAuth();

  const authenticatedFetch = async (url, options = {}) => {
    const token = localStorage.getItem('authToken') || 
                 sessionStorage.getItem('authToken');

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    });

    if (response.status === 401) {
      await logout();
      throw new Error('Session expired');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    return response;
  };

  return { authenticatedFetch };
}
```

## Performance Optimization

### Lazy Loading with Authentication
```jsx
// utils/lazyLoadWithAuth.js
import { lazy, Suspense } from 'react';
import { useAuth } from '../context/AuthContext';

export function createAuthenticatedLazyComponent(importFn, fallback = <div>Loading...</div>) {
  const LazyComponent = lazy(importFn);
  
  return function AuthenticatedLazyComponent(props) {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
      return fallback;
    }

    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    return (
      <Suspense fallback={fallback}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };
}

// Usage
const LazyAdminDashboard = createAuthenticatedLazyComponent(
  () => import('../pages/AdminDashboard'),
  <div>Loading admin dashboard...</div>
);
```

### Authentication State Optimization
```jsx
// hooks/useOptimizedAuth.js
import { useMemo } from 'react';
import { useAuth } from '../context/AuthContext';

export function useOptimizedAuth() {
  const auth = useAuth();

  // Memoize derived states
  const authState = useMemo(() => ({
    isAuthenticated: auth.isAuthenticated,
    isAdmin: auth.user?.role === 'admin',
    isSuperAdmin: auth.user?.role === 'super_admin',
    hasPermissions: (permissions) => 
      permissions.every(p => auth.user?.permissions?.includes(p)),
    userInitials: auth.user ? 
      `${auth.user.firstName?.[0] || ''}${auth.user.lastName?.[0] || ''}`.toUpperCase() :
      '',
    displayName: auth.user?.displayName || auth.user?.email || 'User'
  }), [auth.user, auth.isAuthenticated]);

  return {
    ...auth,
    ...authState
  };
}
```

## Best Practices

### 1. Security Best Practices
```jsx
// Secure token storage
const TokenManager = {
  setToken(token, remember = false) {
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem('authToken', token);
  },

  getToken() {
    return localStorage.getItem('authToken') || 
           sessionStorage.getItem('authToken');
  },

  removeToken() {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
  },

  isTokenExpired(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }
};

// CSRF protection
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

const secureApiCall = async (url, options = {}) => {
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken,
      ...options.headers
    },
    credentials: 'same-origin'
  });
};
```

### 2. Route Organization
```jsx
// routes/config.js
export const routeConfig = {
  public: [
    { path: '/', component: 'Home' },
    { path: '/login', component: 'Login' },
    { path: '/register', component: 'Register' }
  ],
  
  authenticated: [
    { path: '/dashboard', component: 'Dashboard' },
    { path: '/profile', component: 'Profile' }
  ],
  
  admin: [
    { path: '/admin', component: 'AdminDashboard', role: 'admin' },
    { path: '/admin/users', component: 'UserManagement', permissions: ['manage_users'] }
  ]
};

// Dynamic route generation
function generateRoutes(config) {
  return Object.entries(config).map(([type, routes]) => {
    return routes.map(route => {
      const Component = lazy(() => import(`../pages/${route.component}`));
      
      if (type === 'public') {
        return <Route key={route.path} path={route.path} element={<Component />} />;
      }
      
      return (
        <Route
          key={route.path}
          path={route.path}
          element={
            <AdvancedProtectedRoute
              requiredRole={route.role}
              requiredPermissions={route.permissions}
            >
              <Component />
            </AdvancedProtectedRoute>
          }
        />
      );
    });
  });
}
```

This comprehensive guide covers protected routes and authentication patterns in React Router v6. Combined with the previous sections, you now have a complete routing system with authentication, authorization, and security best practices.