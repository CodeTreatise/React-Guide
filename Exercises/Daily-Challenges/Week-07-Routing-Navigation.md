# Week 7: Routing & Navigation - Daily Challenges

## Overview
This week focuses on advanced routing patterns with React Router v6, including dynamic routing, protected routes, navigation patterns, and route-based code splitting.

## Learning Goals
- Master React Router v6 advanced features
- Implement complex navigation patterns
- Build protected route systems
- Create dynamic route generation
- Optimize routing performance

---

## Day 1: Advanced Route Configuration

### Challenge: Dynamic Route System
Build a flexible routing system that can handle dynamic route configuration.

```jsx
// Expected route configuration
const routeConfig = {
  public: [
    { path: '/', component: 'Home', exact: true },
    { path: '/about', component: 'About' },
    { path: '/contact', component: 'Contact' }
  ],
  protected: [
    { 
      path: '/dashboard', 
      component: 'Dashboard',
      children: [
        { path: 'overview', component: 'Overview' },
        { path: 'analytics', component: 'Analytics' },
        { path: 'settings', component: 'Settings' }
      ]
    }
  ],
  admin: [
    { path: '/admin', component: 'AdminPanel', roles: ['admin'] }
  ]
};
```

**Your Task:**
1. Create a dynamic route generator
2. Implement route-based access control
3. Add route parameter validation
4. Build route transition animations
5. Create route-level error boundaries

**Requirements:**
- Support nested route configuration
- Implement role-based route access
- Add route parameter type checking
- Include loading states for async routes
- Create route change analytics

---

## Day 2: Advanced Navigation Patterns

### Challenge: Intelligent Navigation System
Build a smart navigation system with advanced features.

```jsx
// Expected navigation features
const Navigation = () => {
  const nav = useSmartNavigation();
  
  return (
    <nav>
      <NavItem to="/dashboard" preload>Dashboard</NavItem>
      <NavItem to="/analytics" badge={unreadCount}>Analytics</NavItem>
      <NavItem to="/settings" disabled={!hasPermission}>Settings</NavItem>
      <SearchableNav items={navItems} />
      <BreadcrumbNav />
      <RecentNav maxItems={5} />
    </nav>
  );
};
```

**Your Task:**
1. **Smart Preloading**: Preload routes based on user behavior
2. **Contextual Navigation**: Show/hide nav items based on user role
3. **Search Navigation**: Implement searchable navigation
4. **Breadcrumb System**: Dynamic breadcrumb generation
5. **Navigation Analytics**: Track navigation patterns

**Advanced Features:**
- Keyboard navigation shortcuts
- Navigation state persistence
- Mobile-optimized navigation patterns
- Voice navigation integration

---

## Day 3: Protected Routes & Authentication

### Challenge: Comprehensive Auth Route System
Build a sophisticated authentication and authorization routing system.

```jsx
// Expected auth route structure
<Router>
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    
    {/* Protected routes */}
    <Route path="/" element={<RequireAuth />}>
      <Route index element={<Dashboard />} />
      
      {/* Role-based routes */}
      <Route path="admin" element={<RequireRole role="admin" />}>
        <Route path="users" element={<UserManagement />} />
        <Route path="settings" element={<AdminSettings />} />
      </Route>
      
      {/* Permission-based routes */}
      <Route path="analytics" element={<RequirePermission permission="view_analytics" />}>
        <Route index element={<Analytics />} />
      </Route>
    </Route>
  </Routes>
</Router>
```

**Your Task:**
1. **Multi-level Protection**: Implement nested protection layers
2. **Token Management**: Handle token refresh and expiration
3. **Redirect Logic**: Smart redirects after authentication
4. **Session Management**: Handle concurrent sessions
5. **Route Guards**: Implement complex authorization logic

**Security Features:**
- CSRF protection for route changes
- Rate limiting for sensitive routes
- Audit logging for protected route access
- Suspicious activity detection

---

## Day 4: Route Parameters & Query Management

### Challenge: Advanced Parameter Handling
Build a sophisticated system for handling route parameters and query strings.

```jsx
// Expected parameter handling
const useAdvancedParams = () => {
  const [params, setParams] = useRouteParams({
    id: { type: 'number', required: true },
    tab: { type: 'string', default: 'overview' },
    filters: { type: 'object', serialize: true },
    dateRange: { type: 'dateRange', format: 'ISO' }
  });
  
  return { params, setParams, isValid };
};

// Usage in component
const ProductDetail = () => {
  const { params, setParams } = useAdvancedParams();
  const { id, tab, filters, dateRange } = params;
  
  return (
    <div>
      <ProductInfo id={id} />
      <TabSystem 
        activeTab={tab} 
        onTabChange={(tab) => setParams({ tab })} 
      />
      <FilterSystem 
        filters={filters}
        onFiltersChange={(filters) => setParams({ filters })}
      />
    </div>
  );
};
```

**Your Task:**
1. **Type-safe Parameters**: Implement parameter type validation
2. **Query Serialization**: Handle complex object serialization
3. **Parameter History**: Track parameter changes
4. **URL State Sync**: Sync component state with URL
5. **Shareable URLs**: Generate shareable URLs with state

**Advanced Features:**
- Parameter change animations
- URL state compression for complex data
- Parameter validation with error messages
- Auto-save parameter state

---

## Day 5: Route-based Code Splitting

### Challenge: Intelligent Route Splitting
Implement advanced code splitting strategies based on routes.

```jsx
// Route-based splitting configuration
const routeSplitting = {
  strategies: {
    immediate: ['/', '/login'],           // Load immediately
    preload: ['/dashboard', '/profile'],  // Preload on idle
    lazy: ['/admin', '/reports'],         // Load on demand
    conditional: {                       // Load based on conditions
      '/premium': () => user.isPremium,
      '/mobile': () => isMobileDevice
    }
  },
  
  chunks: {
    vendor: ['react', 'react-dom'],
    ui: ['@mui/material'],
    charts: ['chart.js', 'd3'],
    admin: ['admin-components']
  }
};
```

**Your Task:**
1. **Smart Chunking**: Create intelligent bundle splitting
2. **Preload Strategies**: Implement predictive preloading
3. **Error Recovery**: Handle chunk loading failures
4. **Performance Monitoring**: Track chunk loading performance
5. **Cache Management**: Optimize chunk caching strategies

**Performance Goals:**
- Initial bundle < 100KB
- Route chunks < 50KB each
- Preload accuracy > 80%
- Zero failed chunk loads

---

## Day 6: Navigation State Management

### Challenge: Complex Navigation State
Build a comprehensive navigation state management system.

```jsx
// Navigation state system
const NavigationProvider = ({ children }) => {
  const navigation = useNavigationState({
    history: true,           // Track navigation history
    analytics: true,         // Track navigation analytics
    persistence: true,       // Persist navigation state
    breadcrumbs: true,      // Auto-generate breadcrumbs
    shortcuts: true         // Enable keyboard shortcuts
  });
  
  return (
    <NavigationContext.Provider value={navigation}>
      {children}
    </NavigationContext.Provider>
  );
};

// Usage
const useNavigation = () => {
  const {
    navigate,
    goBack,
    goForward,
    history,
    breadcrumbs,
    canGoBack,
    canGoForward,
    shortcuts
  } = useContext(NavigationContext);
  
  return {
    navigate,
    goBack,
    goForward,
    history,
    breadcrumbs,
    canGoBack,
    canGoForward,
    shortcuts
  };
};
```

**Your Task:**
1. **Navigation History**: Implement smart history management
2. **State Persistence**: Persist navigation state across sessions
3. **Analytics Integration**: Track navigation patterns
4. **Keyboard Shortcuts**: Add navigation shortcuts
5. **Mobile Navigation**: Optimize for mobile interactions

**Advanced Features:**
- Navigation state synchronization across tabs
- Custom navigation gestures
- Voice navigation commands
- Navigation state debugging tools

---

## Day 7: Route Testing & Optimization

### Challenge: Comprehensive Route Testing
Build a complete testing suite for your routing system.

**Your Task:**
```jsx
// Route testing utilities
const RouteTestUtils = {
  // Test route rendering
  renderRoute: (path, options) => {
    return render(
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          {/* Your routes */}
        </Routes>
      </MemoryRouter>
    );
  },
  
  // Test navigation flows
  testNavigationFlow: async (steps) => {
    for (const step of steps) {
      await step.action();
      expect(step.assertion()).toBeTruthy();
    }
  },
  
  // Test protected routes
  testProtectedRoute: (path, userRole) => {
    // Test access control
  },
  
  // Performance testing
  testRoutePerformance: (path) => {
    // Measure route loading time
  }
};
```

**Testing Requirements:**
1. **Route Rendering Tests**: Test all route combinations
2. **Navigation Flow Tests**: Test complex navigation scenarios
3. **Authentication Tests**: Test protected route access
4. **Parameter Validation Tests**: Test parameter handling
5. **Performance Tests**: Test route loading performance

**Test Scenarios:**
- Direct URL access
- Programmatic navigation
- Browser back/forward
- Route parameter validation
- Authentication redirects
- Error boundary activation
- Code splitting functionality

---

## Week 7 Assessment

### Advanced Routing Application
Build a complex application showcasing advanced routing patterns.

**Application Requirements:**
```
Multi-tenant SaaS Dashboard
├── Public Routes
│   ├── Landing page (/)
│   ├── Pricing (/pricing)
│   └── Documentation (/docs/*)
├── Authentication Routes
│   ├── Login (/auth/login)
│   ├── Register (/auth/register)
│   └── Password Reset (/auth/reset)
├── Protected Routes
│   ├── Dashboard (/:tenant/dashboard)
│   ├── Analytics (/:tenant/analytics)
│   ├── Settings (/:tenant/settings/*)
│   └── Team Management (/:tenant/team)
└── Admin Routes
    ├── Tenant Management (/admin/tenants)
    ├── User Management (/admin/users)
    └── System Settings (/admin/settings)
```

**Technical Features:**
- Multi-tenant routing with tenant validation
- Role-based access control
- Dynamic navigation based on tenant features
- Route-based code splitting with preloading
- Advanced parameter handling
- Search functionality across all routes
- Mobile-optimized navigation

**Performance Requirements:**
- Initial load < 2 seconds
- Route transitions < 500ms
- Zero layout shift during navigation
- Offline route caching

### Reflection Questions
1. How do you balance SEO requirements with client-side routing?
2. What strategies help optimize routing performance in large applications?
3. How do you handle authentication in a complex routing system?
4. What testing strategies are most effective for routing code?
5. How do you implement progressive enhancement with React Router?

---

## Additional Resources

### React Router Advanced
- [React Router v6 Guide](https://reactrouter.com/en/main)
- [Code Splitting with React Router](https://reactrouter.com/en/main/route/lazy)
- [Authentication Patterns](https://ui.dev/react-router-protected-routes)

### Performance & SEO
- [Server-Side Rendering with React Router](https://reactrouter.com/en/main/guides/ssr)
- [Route-based Code Splitting](https://web.dev/reduce-javascript-payloads-with-code-splitting/)

### Testing
- [Testing React Router](https://testing-library.com/docs/example-react-router/)
- [E2E Testing Navigation Flows](https://www.cypress.io/blog/2018/11/14/testing-react-router/)

**Estimated Time:** 2-3 hours per day  
**Difficulty:** Intermediate to Advanced  
**Focus:** Routing patterns, navigation UX, performance
