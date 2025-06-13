# Advanced Routing Patterns & Performance

## 🎯 Learning Objectives
By the end of this section, you will:
- Implement advanced routing patterns and architectures
- Optimize routing performance for large applications
- Build complex navigation flows and user journeys
- Create route-based animations and transitions
- Implement advanced route caching and preloading
- Handle complex routing edge cases
- Build scalable routing solutions for enterprise applications
- Monitor and debug routing performance

## 📚 Table of Contents
1. [Advanced Route Patterns](#advanced-route-patterns)
2. [Route-Based Code Splitting](#route-based-code-splitting)
3. [Route Caching & Preloading](#route-caching--preloading)
4. [Route Animations & Transitions](#route-animations--transitions)
5. [Complex Navigation Flows](#complex-navigation-flows)
6. [Route Performance Monitoring](#route-performance-monitoring)
7. [Error Recovery Patterns](#error-recovery-patterns)
8. [Enterprise Routing Architecture](#enterprise-routing-architecture)
9. [Testing Routing Logic](#testing-routing-logic)
10. [Best Practices & Patterns](#best-practices--patterns)

## Advanced Route Patterns

### Route Factories and Dynamic Configuration
```jsx
// utils/routeFactory.js
export class RouteFactory {
  constructor() {
    this.routes = new Map();
    this.middlewares = [];
    this.guards = [];
  }

  // Register a route pattern
  register(pattern, config) {
    this.routes.set(pattern, {
      ...config,
      pattern,
      compiled: this.compilePattern(pattern)
    });
    return this;
  }

  // Add global middleware
  use(middleware) {
    this.middlewares.push(middleware);
    return this;
  }

  // Add route guard
  guard(guardFn) {
    this.guards.push(guardFn);
    return this;
  }

  // Compile pattern to regex
  compilePattern(pattern) {
    const paramRegex = /:([^/]+)/g;
    const compiled = pattern.replace(paramRegex, '([^/]+)');
    return new RegExp(`^${compiled}$`);
  }

  // Generate routes
  generate() {
    return Array.from(this.routes.values()).map(route => {
      const Component = route.component;
      
      return (
        <Route
          key={route.pattern}
          path={route.pattern}
          element={
            <RouteWrapper
              middlewares={[...this.middlewares, ...(route.middlewares || [])]}
              guards={[...this.guards, ...(route.guards || [])]}
              meta={route.meta}
            >
              <Component />
            </RouteWrapper>
          }
        />
      );
    });
  }
}

// Usage
const routeFactory = new RouteFactory()
  .use(authMiddleware)
  .use(analyticsMiddleware)
  .guard(rateLimitGuard)
  .register('/users/:userId', {
    component: UserProfile,
    middlewares: [userDataMiddleware],
    meta: { title: 'User Profile', breadcrumb: 'Profile' }
  })
  .register('/admin/:section/:id?', {
    component: AdminPanel,
    guards: [adminGuard],
    meta: { title: 'Admin Panel', requiresRole: 'admin' }
  });

function AppRoutes() {
  return (
    <Routes>
      {routeFactory.generate()}
    </Routes>
  );
}
```

### Multi-Tenant Routing
```jsx
// hooks/useMultiTenantRouting.js
import { useParams, useNavigate } from 'react-router-dom';
import { createContext, useContext, useEffect, useState } from 'react';

const TenantContext = createContext();

export function TenantProvider({ children }) {
  const { tenantId } = useParams();
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadTenant = async () => {
      if (!tenantId) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`/api/tenants/${tenantId}`);
        
        if (response.status === 404) {
          navigate('/tenant-not-found', { replace: true });
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to load tenant');
        }

        const tenantData = await response.json();
        setTenant(tenantData);
      } catch (error) {
        console.error('Tenant loading error:', error);
        navigate('/error', { replace: true });
      } finally {
        setLoading(false);
      }
    };

    loadTenant();
  }, [tenantId, navigate]);

  return (
    <TenantContext.Provider value={{ tenant, loading, tenantId }}>
      {children}
    </TenantContext.Provider>
  );
}

export const useTenant = () => {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within TenantProvider');
  }
  return context;
};

// Multi-tenant route structure
function MultiTenantRoutes() {
  return (
    <Routes>
      {/* Tenant-agnostic routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/pricing" element={<Pricing />} />
      
      {/* Tenant-specific routes */}
      <Route path="/tenant/:tenantId" element={<TenantProvider><TenantLayout /></TenantProvider>}>
        <Route index element={<TenantDashboard />} />
        <Route path="users" element={<TenantUsers />} />
        <Route path="settings" element={<TenantSettings />} />
        
        {/* Nested tenant features */}
        <Route path="projects" element={<ProjectsLayout />}>
          <Route index element={<ProjectsList />} />
          <Route path=":projectId" element={<ProjectDetail />} />
        </Route>
      </Route>
      
      {/* Error routes */}
      <Route path="/tenant-not-found" element={<TenantNotFound />} />
    </Routes>
  );
}

function TenantLayout() {
  const { tenant, loading } = useTenant();

  if (loading) {
    return <div>Loading tenant...</div>;
  }

  if (!tenant) {
    return <Navigate to="/tenant-not-found" replace />;
  }

  return (
    <div className="tenant-layout" data-tenant={tenant.id}>
      <header className="tenant-header">
        <h1>{tenant.name}</h1>
        <TenantNavigation />
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
```

### Feature Flag Routing
```jsx
// hooks/useFeatureRouting.js
import { createContext, useContext, useEffect, useState } from 'react';

const FeatureContext = createContext();

export function FeatureProvider({ children }) {
  const [features, setFeatures] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFeatures = async () => {
      try {
        const response = await fetch('/api/features');
        const featureData = await response.json();
        setFeatures(featureData);
      } catch (error) {
        console.error('Failed to load features:', error);
      } finally {
        setLoading(false);
      }
    };

    loadFeatures();
  }, []);

  const isFeatureEnabled = (featureName) => {
    return features[featureName]?.enabled === true;
  };

  return (
    <FeatureContext.Provider value={{ features, loading, isFeatureEnabled }}>
      {children}
    </FeatureContext.Provider>
  );
}

export const useFeatures = () => {
  const context = useContext(FeatureContext);
  if (!context) {
    throw new Error('useFeatures must be used within FeatureProvider');
  }
  return context;
};

// Feature-gated route component
function FeatureRoute({ feature, children, fallback = null }) {
  const { isFeatureEnabled, loading } = useFeatures();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isFeatureEnabled(feature)) {
    return fallback || <Navigate to="/404" replace />;
  }

  return children;
}

// Usage in routes
function AppRoutes() {
  return (
    <FeatureProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        
        {/* Feature-gated routes */}
        <Route path="/beta-feature" element={
          <FeatureRoute 
            feature="beta_features"
            fallback={<div>Feature not available</div>}
          >
            <BetaFeature />
          </FeatureRoute>
        } />
        
        <Route path="/new-dashboard" element={
          <FeatureRoute feature="new_dashboard">
            <NewDashboard />
          </FeatureRoute>
        } />
      </Routes>
    </FeatureProvider>
  );
}
```

## Route-Based Code Splitting

### Advanced Code Splitting Strategies
```jsx
// utils/advancedLazyLoading.js
import { lazy, Suspense } from 'react';

// Route-based splitting with retry logic
export function createRetryableLazyComponent(importFn, retries = 3) {
  return lazy(() => {
    return new Promise((resolve, reject) => {
      const attemptImport = (remainingRetries) => {
        importFn()
          .then(resolve)
          .catch((error) => {
            if (remainingRetries === 0) {
              reject(error);
            } else {
              setTimeout(() => attemptImport(remainingRetries - 1), 1000);
            }
          });
      };
      
      attemptImport(retries);
    });
  });
}

// Preload with priority
export function createPreloadableLazyComponent(importFn, priority = 'low') {
  const LazyComponent = lazy(importFn);
  
  LazyComponent.preload = () => {
    if (priority === 'high') {
      // Immediate preload
      importFn();
    } else {
      // Idle preload
      if ('requestIdleCallback' in window) {
        requestIdleCallback(() => importFn());
      } else {
        setTimeout(() => importFn(), 0);
      }
    }
  };
  
  return LazyComponent;
}

// Bundle splitting by feature
export const createFeatureBundle = (featureName) => {
  const components = {};
  
  return {
    register: (componentName, importFn) => {
      components[componentName] = createRetryableLazyComponent(importFn);
    },
    
    preloadAll: () => {
      Object.values(components).forEach(component => {
        if (component.preload) {
          component.preload();
        }
      });
    },
    
    get: (componentName) => components[componentName]
  };
};

// Usage
const dashboardBundle = createFeatureBundle('dashboard');
dashboardBundle.register('Dashboard', () => import('../pages/Dashboard'));
dashboardBundle.register('Analytics', () => import('../pages/Analytics'));
dashboardBundle.register('Reports', () => import('../pages/Reports'));

// Progressive loading wrapper
function ProgressiveLoader({ children, skeleton }) {
  const [showSkeleton, setShowSkeleton] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowSkeleton(false), 300);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Suspense fallback={showSkeleton ? skeleton : <div>Loading...</div>}>
      {children}
    </Suspense>
  );
}
```

### Smart Route Prefetching
```jsx
// hooks/useRoutePrefetch.js
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export function useRoutePrefetch() {
  const prefetchedRoutes = useRef(new Set());
  const location = useLocation();

  const prefetchRoute = async (routePath, options = {}) => {
    if (prefetchedRoutes.current.has(routePath)) {
      return;
    }

    try {
      // Mark as prefetching
      prefetchedRoutes.current.add(routePath);

      // Dynamic import based on route
      const moduleMap = {
        '/dashboard': () => import('../pages/Dashboard'),
        '/profile': () => import('../pages/Profile'),
        '/settings': () => import('../pages/Settings'),
        '/admin': () => import('../pages/Admin')
      };

      const importFn = moduleMap[routePath];
      if (importFn) {
        if (options.immediate) {
          await importFn();
        } else {
          // Prefetch during idle time
          if ('requestIdleCallback' in window) {
            requestIdleCallback(() => importFn());
          } else {
            setTimeout(() => importFn(), 100);
          }
        }
      }

      // Prefetch route data
      if (options.prefetchData) {
        fetch(`/api${routePath}/prefetch`, {
          method: 'GET',
          headers: { 'X-Prefetch': 'true' }
        });
      }
    } catch (error) {
      console.warn('Route prefetch failed:', routePath, error);
      prefetchedRoutes.current.delete(routePath);
    }
  };

  const prefetchOnHover = (routePath) => {
    return {
      onMouseEnter: () => prefetchRoute(routePath, { immediate: false }),
      onTouchStart: () => prefetchRoute(routePath, { immediate: false })
    };
  };

  const prefetchVisible = (routePath) => {
    return (element) => {
      if (!element) return;

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              prefetchRoute(routePath);
              observer.unobserve(element);
            }
          });
        },
        { threshold: 0.1 }
      );

      observer.observe(element);
    };
  };

  return {
    prefetchRoute,
    prefetchOnHover,
    prefetchVisible
  };
}

// Enhanced Link component with prefetching
function SmartLink({ to, prefetch = 'hover', children, ...props }) {
  const { prefetchRoute, prefetchOnHover, prefetchVisible } = useRoutePrefetch();
  const linkRef = useRef();

  useEffect(() => {
    if (prefetch === 'visible') {
      prefetchVisible(to)(linkRef.current);
    } else if (prefetch === 'immediate') {
      prefetchRoute(to, { immediate: true, prefetchData: true });
    }
  }, [to, prefetch]);

  const hoverProps = prefetch === 'hover' ? prefetchOnHover(to) : {};

  return (
    <Link ref={linkRef} to={to} {...hoverProps} {...props}>
      {children}
    </Link>
  );
}
```

## Route Caching & Preloading

### Route Data Caching
```jsx
// utils/routeCache.js
class RouteCache {
  constructor(maxSize = 50, ttl = 5 * 60 * 1000) {
    this.cache = new Map();
    this.maxSize = maxSize;
    this.ttl = ttl;
  }

  set(key, value, customTTL = null) {
    // Remove oldest entries if cache is full
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl: customTTL || this.ttl
    });
  }

  get(key) {
    const item = this.cache.get(key);
    
    if (!item) return null;

    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    // Move to end (LRU)
    this.cache.delete(key);
    this.cache.set(key, item);
    
    return item.value;
  }

  has(key) {
    return this.get(key) !== null;
  }

  invalidate(pattern) {
    const regex = new RegExp(pattern);
    
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  clear() {
    this.cache.clear();
  }
}

const routeCache = new RouteCache();

// Hook for cached route data
export function useCachedRouteData(key, fetcher, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Check cache first
        const cached = routeCache.get(key);
        if (cached && !options.forceRefresh) {
          setData(cached);
          setLoading(false);
          return;
        }

        // Fetch fresh data
        const result = await fetcher();
        
        // Cache the result
        routeCache.set(key, result, options.ttl);
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [key, options.forceRefresh]);

  const invalidate = () => {
    routeCache.invalidate(key);
  };

  const refresh = () => {
    loadData();
  };

  return { data, loading, error, invalidate, refresh };
}
```

### Background Route Preloading
```jsx
// hooks/useBackgroundPreloader.js
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export function useBackgroundPreloader() {
  const location = useLocation();
  const preloadQueueRef = useRef([]);
  const isPreloadingRef = useRef(false);

  const preloadQueue = [
    { path: '/dashboard', priority: 1 },
    { path: '/profile', priority: 2 },
    { path: '/settings', priority: 3 }
  ];

  useEffect(() => {
    const processPreloadQueue = async () => {
      if (isPreloadingRef.current) return;
      
      isPreloadingRef.current = true;

      // Sort by priority
      const sortedQueue = [...preloadQueue].sort((a, b) => a.priority - b.priority);

      for (const item of sortedQueue) {
        // Skip if current route
        if (location.pathname === item.path) continue;

        try {
          // Wait for network idle
          await new Promise(resolve => {
            if ('requestIdleCallback' in window) {
              requestIdleCallback(resolve, { timeout: 5000 });
            } else {
              setTimeout(resolve, 100);
            }
          });

          // Preload route component
          const moduleMap = {
            '/dashboard': () => import('../pages/Dashboard'),
            '/profile': () => import('../pages/Profile'),
            '/settings': () => import('../pages/Settings')
          };

          const importFn = moduleMap[item.path];
          if (importFn) {
            await importFn();
          }

          // Preload route data
          if (item.preloadData !== false) {
            fetch(`/api${item.path}/prefetch`, {
              method: 'HEAD',
              headers: { 'X-Prefetch': 'true' }
            });
          }

        } catch (error) {
          console.warn('Background preload failed:', item.path, error);
        }
      }

      isPreloadingRef.current = false;
    };

    // Start preloading after initial page load
    const timer = setTimeout(processPreloadQueue, 2000);
    
    return () => clearTimeout(timer);
  }, [location.pathname]);

  return null;
}
```

## Route Animations & Transitions

### Page Transition System
```jsx
// components/PageTransition.jsx
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { CSSTransition, TransitionGroup } from 'react-transition-group';

function PageTransition({ children }) {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransitionStage] = useState('fadeIn');

  useEffect(() => {
    if (location !== displayLocation) {
      setTransitionStage('fadeOut');
    }
  }, [location, displayLocation]);

  return (
    <TransitionGroup>
      <CSSTransition
        key={displayLocation.pathname}
        classNames="page"
        timeout={300}
        onEnter={() => {
          setTransitionStage('fadeIn');
        }}
        onExited={() => {
          setDisplayLocation(location);
        }}
      >
        <div className={`page-wrapper ${transitionStage}`}>
          {children}
        </div>
      </CSSTransition>
    </TransitionGroup>
  );
}

// CSS for transitions
const transitionStyles = `
.page-enter {
  opacity: 0;
  transform: translateX(100%);
}

.page-enter-active {
  opacity: 1;
  transform: translateX(0%);
  transition: opacity 300ms, transform 300ms;
}

.page-exit {
  opacity: 1;
  transform: translateX(0%);
}

.page-exit-active {
  opacity: 0;
  transform: translateX(-100%);
  transition: opacity 300ms, transform 300ms;
}
`;
```

### Advanced Route Animations
```jsx
// hooks/useRouteTransition.js
import { useState, useEffect } from 'react';
import { useLocation, useNavigationType } from 'react-router-dom';

export function useRouteTransition() {
  const location = useLocation();
  const navigationType = useNavigationType();
  const [transitionState, setTransitionState] = useState({
    stage: 'idle',
    direction: 'forward',
    previousLocation: null
  });

  useEffect(() => {
    setTransitionState(prev => ({
      ...prev,
      stage: 'leaving',
      direction: navigationType === 'POP' ? 'backward' : 'forward',
      previousLocation: prev.currentLocation || null,
      currentLocation: location
    }));

    const timer = setTimeout(() => {
      setTransitionState(prev => ({
        ...prev,
        stage: 'entering'
      }));
    }, 50);

    const completeTimer = setTimeout(() => {
      setTransitionState(prev => ({
        ...prev,
        stage: 'idle'
      }));
    }, 350);

    return () => {
      clearTimeout(timer);
      clearTimeout(completeTimer);
    };
  }, [location, navigationType]);

  return transitionState;
}

// Route-specific transition component
function AnimatedRoute({ children, animation = 'slide' }) {
  const { stage, direction } = useRouteTransition();

  const getAnimationClass = () => {
    const baseClass = `route-${animation}`;
    
    switch (stage) {
      case 'leaving':
        return `${baseClass} ${baseClass}--leaving-${direction}`;
      case 'entering':
        return `${baseClass} ${baseClass}--entering-${direction}`;
      default:
        return baseClass;
    }
  };

  return (
    <div className={getAnimationClass()}>
      {children}
    </div>
  );
}

// Usage
function App() {
  return (
    <Routes>
      <Route path="/" element={
        <AnimatedRoute animation="fade">
          <Home />
        </AnimatedRoute>
      } />
      <Route path="/about" element={
        <AnimatedRoute animation="slide">
          <About />
        </AnimatedRoute>
      } />
    </Routes>
  );
}
```

## Complex Navigation Flows

### Multi-Step Wizard Navigation
```jsx
// hooks/useWizardNavigation.js
import { useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export function useWizardNavigation(steps, options = {}) {
  const { basePath = '/wizard', onComplete = null, onCancel = null } = options;
  const navigate = useNavigate();
  const location = useLocation();
  
  const currentStepIndex = steps.findIndex(step => 
    location.pathname === `${basePath}/${step.path}`
  );

  const [wizardData, setWizardData] = useState({});
  const [completedSteps, setCompletedSteps] = useState(new Set());

  const updateData = useCallback((stepData) => {
    setWizardData(prev => ({ ...prev, ...stepData }));
  }, []);

  const markStepComplete = useCallback((stepIndex) => {
    setCompletedSteps(prev => new Set(prev).add(stepIndex));
  }, []);

  const goToStep = useCallback((stepIndex) => {
    if (stepIndex >= 0 && stepIndex < steps.length) {
      navigate(`${basePath}/${steps[stepIndex].path}`);
    }
  }, [navigate, basePath, steps]);

  const nextStep = useCallback(() => {
    if (currentStepIndex < steps.length - 1) {
      markStepComplete(currentStepIndex);
      goToStep(currentStepIndex + 1);
    } else {
      // Wizard complete
      if (onComplete) {
        onComplete(wizardData);
      }
    }
  }, [currentStepIndex, steps.length, markStepComplete, goToStep, onComplete, wizardData]);

  const previousStep = useCallback(() => {
    if (currentStepIndex > 0) {
      goToStep(currentStepIndex - 1);
    }
  }, [currentStepIndex, goToStep]);

  const canGoToStep = useCallback((stepIndex) => {
    // Can go to current or previous steps, or next if current is complete
    return stepIndex <= currentStepIndex || 
           (stepIndex === currentStepIndex + 1 && completedSteps.has(currentStepIndex));
  }, [currentStepIndex, completedSteps]);

  const cancel = useCallback(() => {
    if (onCancel) {
      onCancel();
    } else {
      navigate(-1);
    }
  }, [onCancel, navigate]);

  return {
    currentStepIndex,
    currentStep: steps[currentStepIndex],
    wizardData,
    completedSteps,
    updateData,
    nextStep,
    previousStep,
    goToStep,
    canGoToStep,
    cancel,
    isFirstStep: currentStepIndex === 0,
    isLastStep: currentStepIndex === steps.length - 1,
    progress: (currentStepIndex + 1) / steps.length
  };
}

// Wizard component
function Wizard({ steps, basePath = '/wizard' }) {
  const wizard = useWizardNavigation(steps, {
    basePath,
    onComplete: (data) => {
      console.log('Wizard completed:', data);
      navigate('/success');
    }
  });

  return (
    <div className="wizard">
      <div className="wizard-header">
        <div className="wizard-progress">
          <div 
            className="wizard-progress-bar"
            style={{ width: `${wizard.progress * 100}%` }}
          />
        </div>
        
        <div className="wizard-steps">
          {steps.map((step, index) => (
            <button
              key={step.path}
              className={`wizard-step ${
                index === wizard.currentStepIndex ? 'active' : ''
              } ${
                wizard.completedSteps.has(index) ? 'completed' : ''
              }`}
              onClick={() => wizard.canGoToStep(index) && wizard.goToStep(index)}
              disabled={!wizard.canGoToStep(index)}
            >
              {step.title}
            </button>
          ))}
        </div>
      </div>

      <div className="wizard-content">
        <Routes>
          {steps.map((step, index) => {
            const StepComponent = step.component;
            return (
              <Route
                key={step.path}
                path={step.path}
                element={<StepComponent wizard={wizard} />}
              />
            );
          })}
        </Routes>
      </div>

      <div className="wizard-actions">
        <button onClick={wizard.cancel}>Cancel</button>
        <button 
          onClick={wizard.previousStep}
          disabled={wizard.isFirstStep}
        >
          Previous
        </button>
        <button onClick={wizard.nextStep}>
          {wizard.isLastStep ? 'Complete' : 'Next'}
        </button>
      </div>
    </div>
  );
}
```

### Conditional Navigation Flows
```jsx
// hooks/useConditionalNavigation.js
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function useConditionalNavigation() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const navigateConditional = (path, conditions = {}) => {
    const {
      requiresAuth = false,
      requiredRole = null,
      requiredFeature = null,
      fallbackPath = '/unauthorized',
      beforeNavigate = null,
      afterNavigate = null
    } = conditions;

    // Pre-navigation hook
    if (beforeNavigate) {
      const shouldContinue = beforeNavigate({ path, user });
      if (!shouldContinue) return false;
    }

    // Authentication check
    if (requiresAuth && !isAuthenticated) {
      navigate('/login', { state: { from: path } });
      return false;
    }

    // Role check
    if (requiredRole && user?.role !== requiredRole) {
      navigate(fallbackPath);
      return false;
    }

    // Feature check
    if (requiredFeature && !user?.features?.includes(requiredFeature)) {
      navigate('/feature-not-available');
      return false;
    }

    // Perform navigation
    navigate(path);

    // Post-navigation hook
    if (afterNavigate) {
      afterNavigate({ path, user });
    }

    return true;
  };

  const navigateBasedOnRole = (roleRoutes, defaultRoute = '/') => {
    const userRole = user?.role;
    const targetRoute = roleRoutes[userRole] || defaultRoute;
    navigate(targetRoute);
  };

  const navigateWithAnalytics = (path, eventData = {}) => {
    // Track navigation event
    analytics.track('Navigation', {
      from: location.pathname,
      to: path,
      userId: user?.id,
      ...eventData
    });

    navigate(path);
  };

  return {
    navigateConditional,
    navigateBasedOnRole,
    navigateWithAnalytics
  };
}
```

## Route Performance Monitoring

### Performance Metrics Collection
```jsx
// utils/routePerformanceMonitor.js
class RoutePerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = [];
  }

  startTracking(routePath) {
    const startTime = performance.now();
    const entry = {
      startTime,
      routePath,
      loadTime: null,
      renderTime: null,
      interactionTime: null,
      memoryUsage: this.getMemoryUsage()
    };

    this.metrics.set(routePath, entry);
    return entry;
  }

  endTracking(routePath, type = 'load') {
    const entry = this.metrics.get(routePath);
    if (!entry) return;

    const endTime = performance.now();
    entry[`${type}Time`] = endTime - entry.startTime;

    // Update memory usage
    entry.memoryUsageAfter = this.getMemoryUsage();

    this.notifyObservers(routePath, entry);
  }

  getMemoryUsage() {
    if ('memory' in performance) {
      return {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      };
    }
    return null;
  }

  addObserver(callback) {
    this.observers.push(callback);
  }

  notifyObservers(routePath, metrics) {
    this.observers.forEach(callback => {
      try {
        callback(routePath, metrics);
      } catch (error) {
        console.error('Performance observer error:', error);
      }
    });
  }

  getMetrics(routePath) {
    return this.metrics.get(routePath);
  }

  getAllMetrics() {
    return Object.fromEntries(this.metrics);
  }

  clearMetrics() {
    this.metrics.clear();
  }
}

const performanceMonitor = new RoutePerformanceMonitor();

// Hook for route performance tracking
export function useRoutePerformance() {
  const location = useLocation();

  useEffect(() => {
    const routePath = location.pathname;
    
    // Start tracking
    performanceMonitor.startTracking(routePath);

    // Track render completion
    const renderTimer = setTimeout(() => {
      performanceMonitor.endTracking(routePath, 'render');
    }, 0);

    // Track interaction readiness
    const interactionTimer = setTimeout(() => {
      performanceMonitor.endTracking(routePath, 'interaction');
    }, 100);

    return () => {
      clearTimeout(renderTimer);
      clearTimeout(interactionTimer);
      performanceMonitor.endTracking(routePath, 'load');
    };
  }, [location.pathname]);

  return {
    getMetrics: (path) => performanceMonitor.getMetrics(path),
    getAllMetrics: () => performanceMonitor.getAllMetrics()
  };
}

// Performance monitoring component
function PerformanceMonitor() {
  const [showMetrics, setShowMetrics] = useState(false);
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    const updateMetrics = () => {
      setMetrics(performanceMonitor.getAllMetrics());
    };

    performanceMonitor.addObserver(updateMetrics);
    updateMetrics();
  }, []);

  if (!showMetrics) {
    return (
      <button 
        className="perf-toggle"
        onClick={() => setShowMetrics(true)}
      >
        📊
      </button>
    );
  }

  return (
    <div className="performance-panel">
      <div className="perf-header">
        <h3>Route Performance</h3>
        <button onClick={() => setShowMetrics(false)}>✕</button>
      </div>
      
      <div className="perf-metrics">
        {Object.entries(metrics).map(([route, metric]) => (
          <div key={route} className="perf-route">
            <h4>{route}</h4>
            <div>Load: {metric.loadTime?.toFixed(2)}ms</div>
            <div>Render: {metric.renderTime?.toFixed(2)}ms</div>
            <div>Interaction: {metric.interactionTime?.toFixed(2)}ms</div>
            {metric.memoryUsage && (
              <div>
                Memory: {(metric.memoryUsage.used / 1024 / 1024).toFixed(2)}MB
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Error Recovery Patterns

### Route Error Recovery
```jsx
// components/RouteErrorBoundary.jsx
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

class RouteErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    
    // Log error to monitoring service
    this.props.onError?.(error, errorInfo, this.props.location);
  }

  componentDidUpdate(prevProps) {
    // Reset error state on route change
    if (prevProps.location !== this.props.location && this.state.hasError) {
      this.setState({ 
        hasError: false, 
        error: null, 
        errorInfo: null,
        retryCount: 0 
      });
    }
  }

  retry = () => {
    this.setState(prev => ({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryCount: prev.retryCount + 1
    }));
  };

  render() {
    if (this.state.hasError) {
      return (
        <RouteErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          retry={this.retry}
          retryCount={this.state.retryCount}
          location={this.props.location}
          navigate={this.props.navigate}
        />
      );
    }

    return this.props.children;
  }
}

function RouteErrorFallback({ error, retry, retryCount, location, navigate }) {
  const canRetry = retryCount < 3;

  return (
    <div className="route-error">
      <h2>Something went wrong</h2>
      <p>An error occurred while loading this page.</p>
      
      <details>
        <summary>Error details</summary>
        <pre>{error?.stack}</pre>
      </details>

      <div className="error-actions">
        {canRetry && (
          <button onClick={retry}>
            Try Again ({3 - retryCount} attempts left)
          </button>
        )}
        
        <button onClick={() => navigate(-1)}>
          Go Back
        </button>
        
        <button onClick={() => navigate('/')}>
          Go Home
        </button>
        
        <button onClick={() => window.location.reload()}>
          Reload Page
        </button>
      </div>
    </div>
  );
}

// HOC for route error boundary
export function withRouteErrorBoundary(Component) {
  return function RouteErrorBoundaryWrapper(props) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
      <RouteErrorBoundary 
        navigate={navigate} 
        location={location}
        onError={(error, errorInfo, location) => {
          // Send to error reporting service
          errorReporting.captureException(error, {
            tags: { route: location.pathname },
            extra: errorInfo
          });
        }}
      >
        <Component {...props} />
      </RouteErrorBoundary>
    );
  };
}
```

## Testing Routing Logic

### Route Testing Utilities
```jsx
// test-utils/routeTestUtils.js
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';

export function renderWithRouter(ui, options = {}) {
  const {
    initialEntries = ['/'],
    initialIndex = 0,
    user = null,
    ...renderOptions
  } = options;

  const Wrapper = ({ children }) => (
    <MemoryRouter initialEntries={initialEntries} initialIndex={initialIndex}>
      <AuthProvider initialUser={user}>
        {children}
      </AuthProvider>
    </MemoryRouter>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    // Utility to change route
    navigate: (to) => {
      window.history.pushState({}, '', to);
    }
  };
}

export function createRouteTest(routeConfig) {
  return {
    async testRoute(path, expectedComponent, options = {}) {
      const { getByTestId } = renderWithRouter(
        <Routes>
          {routeConfig.map(route => (
            <Route key={route.path} {...route} />
          ))}
        </Routes>,
        {
          initialEntries: [path],
          ...options
        }
      );

      expect(getByTestId(expectedComponent)).toBeInTheDocument();
    },

    async testProtectedRoute(path, options = {}) {
      const { queryByTestId, getByTestId } = renderWithRouter(
        <Routes>
          {routeConfig.map(route => (
            <Route key={route.path} {...route} />
          ))}
        </Routes>,
        {
          initialEntries: [path],
          user: null, // No authenticated user
          ...options
        }
      );

      // Should redirect to login
      expect(queryByTestId('login-form')).toBeInTheDocument();
    },

    async testRoleBasedRoute(path, role, shouldAccess, options = {}) {
      const { queryByTestId } = renderWithRouter(
        <Routes>
          {routeConfig.map(route => (
            <Route key={route.path} {...route} />
          ))}
        </Routes>,
        {
          initialEntries: [path],
          user: { role },
          ...options
        }
      );

      if (shouldAccess) {
        expect(queryByTestId('unauthorized')).not.toBeInTheDocument();
      } else {
        expect(queryByTestId('unauthorized')).toBeInTheDocument();
      }
    }
  };
}

// Example tests
describe('Route Protection', () => {
  const routeTest = createRouteTest([
    { path: '/', element: <Home data-testid="home" /> },
    { 
      path: '/dashboard', 
      element: (
        <ProtectedRoute>
          <Dashboard data-testid="dashboard" />
        </ProtectedRoute>
      )
    },
    {
      path: '/admin',
      element: (
        <AdvancedProtectedRoute requiredRole="admin">
          <Admin data-testid="admin" />
        </AdvancedProtectedRoute>
      )
    }
  ]);

  test('allows access to public routes', async () => {
    await routeTest.testRoute('/', 'home');
  });

  test('redirects unauthenticated users from protected routes', async () => {
    await routeTest.testProtectedRoute('/dashboard');
  });

  test('allows admin access to admin routes', async () => {
    await routeTest.testRoleBasedRoute('/admin', 'admin', true);
  });

  test('denies non-admin access to admin routes', async () => {
    await routeTest.testRoleBasedRoute('/admin', 'user', false);
  });
});
```

This comprehensive guide covers advanced routing patterns and performance optimization in React Router v6. Combined with all the previous sections, you now have a complete, enterprise-ready routing system with advanced features, performance optimizations, and robust error handling.
