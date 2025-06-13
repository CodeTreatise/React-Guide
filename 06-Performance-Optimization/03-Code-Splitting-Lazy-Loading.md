# Code Splitting & Lazy Loading Strategies

## Table of Contents
1. [Introduction to Code Splitting](#introduction-to-code-splitting)
2. [React Lazy Loading](#react-lazy-loading)
3. [Advanced Code Splitting Patterns](#advanced-code-splitting-patterns)
4. [Dynamic Imports & Module Loading](#dynamic-imports--module-loading)
5. [Route-Based Code Splitting](#route-based-code-splitting)
6. [Component-Level Lazy Loading](#component-level-lazy-loading)
7. [Asset & Resource Optimization](#asset--resource-optimization)
8. [Preloading & Prefetching Strategies](#preloading--prefetching-strategies)

## Introduction to Code Splitting

Code splitting is the practice of breaking your application bundle into smaller chunks that can be loaded on-demand, reducing the initial load time and improving performance.

### Why Code Splitting Matters

```jsx
// ❌ BAD: Everything loaded upfront
import Dashboard from './Dashboard';
import UserProfile from './UserProfile';
import AdminPanel from './AdminPanel';
import Reports from './Reports';
import Settings from './Settings';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  
  // All components are bundled even if never used
  const renderView = () => {
    switch (currentView) {
      case 'dashboard': return <Dashboard />;
      case 'profile': return <UserProfile />;
      case 'admin': return <AdminPanel />;
      case 'reports': return <Reports />;
      case 'settings': return <Settings />;
      default: return <Dashboard />;
    }
  };
  
  return (
    <div>
      <Navigation onViewChange={setCurrentView} />
      {renderView()}
    </div>
  );
}

// ✅ GOOD: Load components only when needed
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));
const UserProfile = lazy(() => import('./UserProfile'));
const AdminPanel = lazy(() => import('./AdminPanel'));
const Reports = lazy(() => import('./Reports'));
const Settings = lazy(() => import('./Settings'));

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  
  const renderView = () => {
    switch (currentView) {
      case 'dashboard': return <Dashboard />;
      case 'profile': return <UserProfile />;
      case 'admin': return <AdminPanel />;
      case 'reports': return <Reports />;
      case 'settings': return <Settings />;
      default: return <Dashboard />;
    }
  };
  
  return (
    <div>
      <Navigation onViewChange={setCurrentView} />
      <Suspense fallback={<LoadingSpinner />}>
        {renderView()}
      </Suspense>
    </div>
  );
}
```

### Bundle Analysis

```jsx
// Hook for analyzing bundle impact
function useBundleAnalysis() {
  const [bundleStats, setBundleStats] = useState({
    initialSize: 0,
    lazyChunks: [],
    loadedChunks: new Set(),
    totalSaved: 0
  });
  
  useEffect(() => {
    // Monitor chunk loading
    const originalImport = window.__webpack_require__;
    if (originalImport) {
      window.__webpack_require__ = function(chunkId) {
        setBundleStats(prev => ({
          ...prev,
          loadedChunks: new Set([...prev.loadedChunks, chunkId])
        }));
        return originalImport.apply(this, arguments);
      };
    }
    
    // Analyze performance marks
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        if (entry.name.includes('chunk')) {
          console.log(`Chunk loaded: ${entry.name} in ${entry.duration}ms`);
        }
      });
    });
    
    observer.observe({ entryTypes: ['measure', 'mark'] });
    
    return () => observer.disconnect();
  }, []);
  
  return bundleStats;
}
```

## React Lazy Loading

### Basic Lazy Loading

```jsx
import { lazy, Suspense } from 'react';

// Simple lazy loading
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
}
```

### Enhanced Lazy Loading with Error Boundaries

```jsx
// Error boundary for lazy components
class LazyErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
    
    // Send to error reporting service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'exception', {
        description: `Lazy loading failed: ${error.message}`,
        fatal: false
      });
    }
  }
  
  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };
  
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '20px', 
          textAlign: 'center',
          border: '1px solid #ff6b6b',
          borderRadius: '8px',
          backgroundColor: '#ffe0e0'
        }}>
          <h3>Failed to load component</h3>
          <p>{this.state.error?.message}</p>
          <button 
            onClick={this.handleRetry}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

// Enhanced lazy wrapper
function createLazyComponent(importFunction, options = {}) {
  const {
    fallback = <div>Loading...</div>,
    errorFallback = null,
    retryCount = 3,
    retryDelay = 1000
  } = options;
  
  const LazyComponent = lazy(() => 
    retryImport(importFunction, retryCount, retryDelay)
  );
  
  return function WrappedLazyComponent(props) {
    return (
      <LazyErrorBoundary errorFallback={errorFallback}>
        <Suspense fallback={fallback}>
          <LazyComponent {...props} />
        </Suspense>
      </LazyErrorBoundary>
    );
  };
}

// Retry logic for failed imports
async function retryImport(importFunction, retryCount, retryDelay) {
  for (let attempt = 0; attempt <= retryCount; attempt++) {
    try {
      return await importFunction();
    } catch (error) {
      if (attempt === retryCount) {
        throw error;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
      console.warn(`Import failed, retrying... (${attempt + 1}/${retryCount})`);
    }
  }
}
```

### Conditional Lazy Loading

```jsx
// Hook for conditional lazy loading
function useConditionalLazy(condition, importFunction) {
  const [Component, setComponent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (condition && !Component) {
      setLoading(true);
      setError(null);
      
      importFunction()
        .then(module => {
          setComponent(() => module.default);
          setLoading(false);
        })
        .catch(err => {
          setError(err);
          setLoading(false);
        });
    }
  }, [condition, Component, importFunction]);
  
  return { Component, loading, error };
}

// Usage example
function ConditionalComponent({ shouldLoad }) {
  const { Component, loading, error } = useConditionalLazy(
    shouldLoad,
    () => import('./HeavyComponent')
  );
  
  if (!shouldLoad) return null;
  if (loading) return <div>Loading heavy component...</div>;
  if (error) return <div>Error loading component: {error.message}</div>;
  if (!Component) return null;
  
  return <Component />;
}
```

## Advanced Code Splitting Patterns

### Feature-Based Code Splitting

```jsx
// Feature module structure
const featureModules = {
  dashboard: () => import('./features/dashboard'),
  analytics: () => import('./features/analytics'),
  userManagement: () => import('./features/userManagement'),
  billing: () => import('./features/billing'),
  reports: () => import('./features/reports')
};

// Feature loader hook
function useFeatureLoader() {
  const [loadedFeatures, setLoadedFeatures] = useState(new Map());
  const [loadingFeatures, setLoadingFeatures] = useState(new Set());
  
  const loadFeature = useCallback(async (featureName) => {
    if (loadedFeatures.has(featureName) || loadingFeatures.has(featureName)) {
      return loadedFeatures.get(featureName);
    }
    
    const importFunction = featureModules[featureName];
    if (!importFunction) {
      throw new Error(`Feature "${featureName}" not found`);
    }
    
    setLoadingFeatures(prev => new Set(prev).add(featureName));
    
    try {
      const module = await importFunction();
      setLoadedFeatures(prev => new Map(prev).set(featureName, module));
      
      return module;
    } finally {
      setLoadingFeatures(prev => {
        const newSet = new Set(prev);
        newSet.delete(featureName);
        return newSet;
      });
    }
  }, [loadedFeatures, loadingFeatures]);
  
  const preloadFeature = useCallback((featureName) => {
    if (!loadedFeatures.has(featureName) && !loadingFeatures.has(featureName)) {
      loadFeature(featureName).catch(console.error);
    }
  }, [loadFeature, loadedFeatures, loadingFeatures]);
  
  const isFeatureLoaded = useCallback((featureName) => {
    return loadedFeatures.has(featureName);
  }, [loadedFeatures]);
  
  const isFeatureLoading = useCallback((featureName) => {
    return loadingFeatures.has(featureName);
  }, [loadingFeatures]);
  
  return {
    loadFeature,
    preloadFeature,
    isFeatureLoaded,
    isFeatureLoading,
    loadedFeatures: Array.from(loadedFeatures.keys())
  };
}

// Feature component wrapper
function FeatureComponent({ featureName, componentName, fallback, ...props }) {
  const { loadFeature, isFeatureLoaded, isFeatureLoading } = useFeatureLoader();
  const [Component, setComponent] = useState(null);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    loadFeature(featureName)
      .then(module => {
        const FeatureComponent = module[componentName] || module.default;
        setComponent(() => FeatureComponent);
      })
      .catch(setError);
  }, [featureName, componentName, loadFeature]);
  
  if (error) {
    return <div>Error loading feature: {error.message}</div>;
  }
  
  if (isFeatureLoading(featureName) || !Component) {
    return fallback || <div>Loading {featureName}...</div>;
  }
  
  return <Component {...props} />;
}
```

### Library Code Splitting

```jsx
// Split third-party libraries
const LibraryLoaders = {
  chart: () => import('chart.js'),
  datePicker: () => import('react-datepicker'),
  editor: () => import('@monaco-editor/react'),
  dataTable: () => import('react-data-table-component'),
  pdf: () => import('react-pdf')
};

// Library loading hook
function useLibraryLoader() {
  const [loadedLibraries, setLoadedLibraries] = useState(new Map());
  const [loadingLibraries, setLoadingLibraries] = useState(new Set());
  
  const loadLibrary = useCallback(async (libraryName) => {
    if (loadedLibraries.has(libraryName)) {
      return loadedLibraries.get(libraryName);
    }
    
    if (loadingLibraries.has(libraryName)) {
      // Wait for ongoing load
      return new Promise((resolve) => {
        const checkLoaded = () => {
          if (loadedLibraries.has(libraryName)) {
            resolve(loadedLibraries.get(libraryName));
          } else {
            setTimeout(checkLoaded, 50);
          }
        };
        checkLoaded();
      });
    }
    
    const loader = LibraryLoaders[libraryName];
    if (!loader) {
      throw new Error(`Library "${libraryName}" not configured`);
    }
    
    setLoadingLibraries(prev => new Set(prev).add(libraryName));
    
    try {
      const library = await loader();
      setLoadedLibraries(prev => new Map(prev).set(libraryName, library));
      return library;
    } finally {
      setLoadingLibraries(prev => {
        const newSet = new Set(prev);
        newSet.delete(libraryName);
        return newSet;
      });
    }
  }, [loadedLibraries, loadingLibraries]);
  
  return { loadLibrary, isLoading: (name) => loadingLibraries.has(name) };
}

// Chart component with lazy library loading
function LazyChart({ data, type = 'line', ...options }) {
  const { loadLibrary } = useLibraryLoader();
  const [ChartComponent, setChartComponent] = useState(null);
  const canvasRef = useRef(null);
  
  useEffect(() => {
    loadLibrary('chart')
      .then(({ Chart, registerables }) => {
        Chart.register(...registerables);
        
        // Create custom Chart component
        const ChartWrapper = ({ data, type, ...options }) => {
          useEffect(() => {
            if (canvasRef.current) {
              const chart = new Chart(canvasRef.current, {
                type,
                data,
                options
              });
              
              return () => chart.destroy();
            }
          }, [data, type, options]);
          
          return <canvas ref={canvasRef} />;
        };
        
        setChartComponent(() => ChartWrapper);
      })
      .catch(console.error);
  }, [loadLibrary]);
  
  if (!ChartComponent) {
    return <div>Loading chart...</div>;
  }
  
  return <ChartComponent data={data} type={type} {...options} />;
}
```

## Dynamic Imports & Module Loading

### Advanced Dynamic Import Patterns

```jsx
// Dynamic import with caching
class ModuleCache {
  constructor() {
    this.cache = new Map();
    this.pending = new Map();
  }
  
  async import(modulePath, options = {}) {
    const { bust = false, timeout = 30000 } = options;
    const cacheKey = modulePath;
    
    // Return cached module
    if (this.cache.has(cacheKey) && !bust) {
      return this.cache.get(cacheKey);
    }
    
    // Return pending promise
    if (this.pending.has(cacheKey)) {
      return this.pending.get(cacheKey);
    }
    
    // Create import promise with timeout
    const importPromise = Promise.race([
      import(modulePath),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error(`Import timeout: ${modulePath}`)), timeout)
      )
    ]);
    
    this.pending.set(cacheKey, importPromise);
    
    try {
      const module = await importPromise;
      this.cache.set(cacheKey, module);
      this.pending.delete(cacheKey);
      return module;
    } catch (error) {
      this.pending.delete(cacheKey);
      throw error;
    }
  }
  
  preload(modulePath) {
    return this.import(modulePath).catch(() => {
      // Ignore preload errors
    });
  }
  
  clear(modulePath) {
    if (modulePath) {
      this.cache.delete(modulePath);
      this.pending.delete(modulePath);
    } else {
      this.cache.clear();
      this.pending.clear();
    }
  }
}

const moduleCache = new ModuleCache();

// Hook for dynamic imports
function useDynamicImport(modulePath, options = {}) {
  const [state, setState] = useState({
    module: null,
    loading: false,
    error: null
  });
  
  const { 
    lazy = true,
    preload = false,
    retryCount = 3,
    retryDelay = 1000 
  } = options;
  
  const loadModule = useCallback(async () => {
    if (!modulePath) return;
    
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    for (let attempt = 0; attempt <= retryCount; attempt++) {
      try {
        const module = await moduleCache.import(modulePath);
        setState({ module, loading: false, error: null });
        return module;
      } catch (error) {
        if (attempt === retryCount) {
          setState({ module: null, loading: false, error });
          throw error;
        }
        
        await new Promise(resolve => 
          setTimeout(resolve, retryDelay * (attempt + 1))
        );
      }
    }
  }, [modulePath, retryCount, retryDelay]);
  
  // Load immediately if not lazy
  useEffect(() => {
    if (!lazy) {
      loadModule();
    }
  }, [lazy, loadModule]);
  
  // Preload if requested
  useEffect(() => {
    if (preload && lazy) {
      moduleCache.preload(modulePath);
    }
  }, [preload, lazy, modulePath]);
  
  return {
    ...state,
    loadModule,
    clearCache: () => moduleCache.clear(modulePath)
  };
}
```

### Module Federation Pattern

```jsx
// Micro-frontend module loader
class ModuleFederationLoader {
  constructor() {
    this.remotes = new Map();
    this.loadedModules = new Map();
  }
  
  addRemote(name, url) {
    this.remotes.set(name, url);
  }
  
  async loadRemoteModule(remoteName, moduleName) {
    const cacheKey = `${remoteName}/${moduleName}`;
    
    if (this.loadedModules.has(cacheKey)) {
      return this.loadedModules.get(cacheKey);
    }
    
    const remoteUrl = this.remotes.get(remoteName);
    if (!remoteUrl) {
      throw new Error(`Remote "${remoteName}" not configured`);
    }
    
    try {
      // Load remote container
      const container = await this.loadRemoteContainer(remoteUrl);
      
      // Initialize container
      await container.init(__webpack_share_scopes__.default);
      
      // Get module factory
      const factory = await container.get(moduleName);
      const module = factory();
      
      this.loadedModules.set(cacheKey, module);
      return module;
    } catch (error) {
      console.error(`Failed to load remote module ${cacheKey}:`, error);
      throw error;
    }
  }
  
  async loadRemoteContainer(url) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = url;
      script.onload = () => {
        const containerName = url.split('/').pop().replace('.js', '');
        resolve(window[containerName]);
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
}

// Hook for remote modules
function useRemoteModule(remoteName, moduleName) {
  const [state, setState] = useState({
    module: null,
    loading: false,
    error: null
  });
  
  const federationLoader = useRef(new ModuleFederationLoader());
  
  useEffect(() => {
    if (!remoteName || !moduleName) return;
    
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    federationLoader.current
      .loadRemoteModule(remoteName, moduleName)
      .then(module => {
        setState({ module, loading: false, error: null });
      })
      .catch(error => {
        setState({ module: null, loading: false, error });
      });
  }, [remoteName, moduleName]);
  
  return state;
}
```

## Route-Based Code Splitting

### Advanced Route Splitting

```jsx
import { lazy } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';

// Route configuration with lazy loading
const routeConfigs = [
  {
    path: '/',
    component: lazy(() => import('./pages/Home')),
    preload: true
  },
  {
    path: '/dashboard',
    component: lazy(() => import('./pages/Dashboard')),
    preload: false,
    chunkName: 'dashboard'
  },
  {
    path: '/users',
    component: lazy(() => import('./pages/Users')),
    roles: ['admin', 'manager']
  },
  {
    path: '/settings',
    component: lazy(() => import('./pages/Settings')),
    preload: false
  }
];

// Route preloader
function useRoutePreloader() {
  const location = useLocation();
  const preloadedRoutes = useRef(new Set());
  
  const preloadRoute = useCallback((routePath) => {
    const route = routeConfigs.find(r => r.path === routePath);
    if (route && !preloadedRoutes.current.has(routePath)) {
      // Trigger module loading
      route.component._payload._result?.();
      preloadedRoutes.current.add(routePath);
    }
  }, []);
  
  const preloadAdjacentRoutes = useCallback(() => {
    const currentIndex = routeConfigs.findIndex(r => r.path === location.pathname);
    
    // Preload next and previous routes
    if (currentIndex > 0) {
      preloadRoute(routeConfigs[currentIndex - 1].path);
    }
    if (currentIndex < routeConfigs.length - 1) {
      preloadRoute(routeConfigs[currentIndex + 1].path);
    }
  }, [location.pathname, preloadRoute]);
  
  // Preload routes marked for preloading
  useEffect(() => {
    routeConfigs
      .filter(route => route.preload)
      .forEach(route => preloadRoute(route.path));
  }, [preloadRoute]);
  
  // Preload adjacent routes when location changes
  useEffect(() => {
    const timer = setTimeout(preloadAdjacentRoutes, 1000);
    return () => clearTimeout(timer);
  }, [preloadAdjacentRoutes]);
  
  return { preloadRoute };
}

// Smart route component
function SmartRoute({ path, component: Component, roles, ...props }) {
  const [hasAccess, setHasAccess] = useState(true);
  
  // Role-based access check
  useEffect(() => {
    if (roles) {
      // Check user roles (implement your auth logic)
      checkUserRoles(roles).then(setHasAccess);
    }
  }, [roles]);
  
  if (!hasAccess) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return (
    <Route
      path={path}
      element={
        <Suspense fallback={<RouteLoadingFallback />}>
          <Component {...props} />
        </Suspense>
      }
    />
  );
}

// Main router with preloading
function AppRouter() {
  const { preloadRoute } = useRoutePreloader();
  
  return (
    <Router>
      <Navigation onLinkHover={preloadRoute} />
      <Routes>
        {routeConfigs.map(route => (
          <SmartRoute key={route.path} {...route} />
        ))}
      </Routes>
    </Router>
  );
}
```

### Nested Route Splitting

```jsx
// Nested route lazy loading
const DashboardRoutes = lazy(() => import('./routes/DashboardRoutes'));
const UserRoutes = lazy(() => import('./routes/UserRoutes'));
const AdminRoutes = lazy(() => import('./routes/AdminRoutes'));

function NestedRoutesExample() {
  return (
    <Routes>
      <Route path="/dashboard/*" element={
        <Suspense fallback={<DashboardSkeleton />}>
          <DashboardRoutes />
        </Suspense>
      } />
      <Route path="/users/*" element={
        <Suspense fallback={<UsersSkeleton />}>
          <UserRoutes />
        </Suspense>
      } />
      <Route path="/admin/*" element={
        <Suspense fallback={<AdminSkeleton />}>
          <AdminRoutes />
        </Suspense>
      } />
    </Routes>
  );
}

// Dashboard sub-routes
function DashboardRoutes() {
  return (
    <Routes>
      <Route index element={<DashboardOverview />} />
      <Route path="analytics" element={
        <Suspense fallback={<div>Loading analytics...</div>}>
          <AnalyticsComponent />
        </Suspense>
      } />
      <Route path="reports" element={
        <Suspense fallback={<div>Loading reports...</div>}>
          <ReportsComponent />
        </Suspense>
      } />
    </Routes>
  );
}
```

## Component-Level Lazy Loading

### Intelligent Component Loading

```jsx
// Component visibility-based loading
function useVisibilityBasedLoading(threshold = 0.1) {
  const [isVisible, setIsVisible] = useState(false);
  const [hasBeenVisible, setHasBeenVisible] = useState(false);
  const elementRef = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        const visible = entry.isIntersecting;
        setIsVisible(visible);
        
        if (visible && !hasBeenVisible) {
          setHasBeenVisible(true);
        }
      },
      { threshold }
    );
    
    const element = elementRef.current;
    if (element) {
      observer.observe(element);
    }
    
    return () => {
      if (element) {
        observer.unobserve(element);
      }
    };
  }, [threshold, hasBeenVisible]);
  
  return { elementRef, isVisible, hasBeenVisible };
}

// Lazy component with intersection observer
function LazyOnVisible({ 
  children, 
  fallback = <div>Loading...</div>,
  height = 200,
  threshold = 0.1 
}) {
  const { elementRef, hasBeenVisible } = useVisibilityBasedLoading(threshold);
  
  return (
    <div 
      ref={elementRef}
      style={{ minHeight: height }}
    >
      {hasBeenVisible ? children : fallback}
    </div>
  );
}

// Usage
function ComponentWithLazyContent() {
  return (
    <div>
      <h2>Page Content</h2>
      <p>Some initial content...</p>
      
      <LazyOnVisible fallback={<ContentSkeleton />}>
        <HeavyComponent />
      </LazyOnVisible>
      
      <LazyOnVisible fallback={<ChartSkeleton />}>
        <LazyChart data={chartData} />
      </LazyOnVisible>
    </div>
  );
}
```

### Modal and Overlay Lazy Loading

```jsx
// Lazy modal hook
function useLazyModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [ModalComponent, setModalComponent] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const openModal = useCallback(async (modalImport) => {
    setLoading(true);
    setIsOpen(true);
    
    try {
      const module = await modalImport();
      setModalComponent(() => module.default);
    } catch (error) {
      console.error('Failed to load modal:', error);
      setIsOpen(false);
    } finally {
      setLoading(false);
    }
  }, []);
  
  const closeModal = useCallback(() => {
    setIsOpen(false);
    // Clear component after animation
    setTimeout(() => {
      setModalComponent(null);
    }, 300);
  }, []);
  
  return {
    isOpen,
    loading,
    ModalComponent,
    openModal,
    closeModal
  };
}

// Modal manager component
function ModalManager() {
  const { isOpen, loading, ModalComponent, openModal, closeModal } = useLazyModal();
  
  const handleOpenUserModal = () => {
    openModal(() => import('./modals/UserModal'));
  };
  
  const handleOpenSettingsModal = () => {
    openModal(() => import('./modals/SettingsModal'));
  };
  
  return (
    <div>
      <button onClick={handleOpenUserModal}>Open User Modal</button>
      <button onClick={handleOpenSettingsModal}>Open Settings Modal</button>
      
      {isOpen && (
        <div className="modal-overlay">
          {loading ? (
            <div className="modal-loading">Loading modal...</div>
          ) : (
            ModalComponent && <ModalComponent onClose={closeModal} />
          )}
        </div>
      )}
    </div>
  );
}
```

### Tab-Based Lazy Loading

```jsx
// Lazy tab content
function useLazyTabs(tabs) {
  const [activeTab, setActiveTab] = useState(tabs[0]?.id);
  const [loadedTabs, setLoadedTabs] = useState(new Set([tabs[0]?.id]));
  const [tabComponents, setTabComponents] = useState(new Map());
  
  const loadTab = useCallback(async (tabId) => {
    const tab = tabs.find(t => t.id === tabId);
    if (!tab || loadedTabs.has(tabId)) return;
    
    try {
      const module = await tab.import();
      setTabComponents(prev => new Map(prev).set(tabId, module.default));
      setLoadedTabs(prev => new Set(prev).add(tabId));
    } catch (error) {
      console.error(`Failed to load tab ${tabId}:`, error);
    }
  }, [tabs, loadedTabs]);
  
  const activateTab = useCallback((tabId) => {
    setActiveTab(tabId);
    loadTab(tabId);
  }, [loadTab]);
  
  // Preload adjacent tabs
  const preloadAdjacentTabs = useCallback(() => {
    const currentIndex = tabs.findIndex(t => t.id === activeTab);
    
    if (currentIndex > 0) {
      loadTab(tabs[currentIndex - 1].id);
    }
    if (currentIndex < tabs.length - 1) {
      loadTab(tabs[currentIndex + 1].id);
    }
  }, [activeTab, tabs, loadTab]);
  
  useEffect(() => {
    // Preload adjacent tabs after a delay
    const timer = setTimeout(preloadAdjacentTabs, 2000);
    return () => clearTimeout(timer);
  }, [preloadAdjacentTabs]);
  
  return {
    activeTab,
    activateTab,
    loadedTabs,
    tabComponents,
    isTabLoaded: (tabId) => loadedTabs.has(tabId)
  };
}

// Tab container component
function LazyTabContainer({ tabs }) {
  const {
    activeTab,
    activateTab,
    tabComponents,
    isTabLoaded
  } = useLazyTabs(tabs);
  
  return (
    <div className="tab-container">
      <div className="tab-nav">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => activateTab(tab.id)}
          >
            {tab.title}
            {!isTabLoaded(tab.id) && <span className="lazy-indicator">⚡</span>}
          </button>
        ))}
      </div>
      
      <div className="tab-content">
        {tabs.map(tab => {
          const TabComponent = tabComponents.get(tab.id);
          const isActive = activeTab === tab.id;
          
          return (
            <div 
              key={tab.id}
              className={`tab-panel ${isActive ? 'active' : 'hidden'}`}
            >
              {isActive && (
                TabComponent ? (
                  <TabComponent />
                ) : (
                  <div className="tab-loading">Loading {tab.title}...</div>
                )
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

## Asset & Resource Optimization

### Image Lazy Loading

```jsx
// Advanced image lazy loading
function LazyImage({ 
  src, 
  alt, 
  placeholder,
  className,
  threshold = 0.1,
  onLoad,
  onError,
  ...props 
}) {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const imgRef = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          const img = new Image();
          
          img.onload = () => {
            setImageSrc(src);
            setLoading(false);
            onLoad?.();
          };
          
          img.onerror = () => {
            setError(true);
            setLoading(false);
            onError?.();
          };
          
          img.src = src;
          observer.disconnect();
        }
      },
      { threshold }
    );
    
    const currentImg = imgRef.current;
    if (currentImg) {
      observer.observe(currentImg);
    }
    
    return () => observer.disconnect();
  }, [src, threshold, onLoad, onError]);
  
  return (
    <div className={`lazy-image-container ${className || ''}`}>
      <img
        ref={imgRef}
        src={imageSrc}
        alt={alt}
        className={`lazy-image ${loading ? 'loading' : ''} ${error ? 'error' : ''}`}
        {...props}
      />
      {loading && (
        <div className="lazy-image-placeholder">
          <div className="loading-spinner" />
        </div>
      )}
      {error && (
        <div className="lazy-image-error">
          Failed to load image
        </div>
      )}
    </div>
  );
}
```

### CSS Lazy Loading

```jsx
// Dynamic CSS loading
function useLazyCSS() {
  const loadedStyles = useRef(new Set());
  
  const loadCSS = useCallback((href, options = {}) => {
    const { media = 'all', id } = options;
    
    if (loadedStyles.current.has(href)) {
      return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.media = media;
      if (id) link.id = id;
      
      link.onload = () => {
        loadedStyles.current.add(href);
        resolve();
      };
      
      link.onerror = reject;
      
      document.head.appendChild(link);
    });
  }, []);
  
  const unloadCSS = useCallback((href) => {
    const link = document.querySelector(`link[href="${href}"]`);
    if (link) {
      link.remove();
      loadedStyles.current.delete(href);
    }
  }, []);
  
  return { loadCSS, unloadCSS };
}

// Component with theme-based CSS loading
function ThemedComponent({ theme = 'default' }) {
  const { loadCSS, unloadCSS } = useLazyCSS();
  const [cssLoaded, setCSSLoaded] = useState(false);
  
  useEffect(() => {
    setCSSLoaded(false);
    
    loadCSS(`/themes/${theme}.css`, { id: `theme-${theme}` })
      .then(() => setCSSLoaded(true))
      .catch(console.error);
    
    return () => {
      unloadCSS(`/themes/${theme}.css`);
    };
  }, [theme, loadCSS, unloadCSS]);
  
  if (!cssLoaded) {
    return <div>Loading theme...</div>;
  }
  
  return (
    <div className={`themed-component theme-${theme}`}>
      <h2>Themed Content</h2>
      <p>This content uses the {theme} theme.</p>
    </div>
  );
}
```

## Preloading & Prefetching Strategies

### Intelligent Preloading

```jsx
// Preloading strategy based on user behavior
function useIntelligentPreloading() {
  const userBehavior = useRef({
    clickPatterns: new Map(),
    navigationTimes: [],
    preferredRoutes: new Set()
  });
  
  const [preloadQueue, setPreloadQueue] = useState([]);
  const [preloadedResources, setPreloadedResources] = useState(new Set());
  
  // Track user interactions
  const trackInteraction = useCallback((type, target) => {
    const behavior = userBehavior.current;
    
    if (type === 'click') {
      const count = behavior.clickPatterns.get(target) || 0;
      behavior.clickPatterns.set(target, count + 1);
    }
    
    if (type === 'navigation') {
      behavior.navigationTimes.push(Date.now());
      behavior.preferredRoutes.add(target);
    }
  }, []);
  
  // Predictive preloading
  const predictNextResources = useCallback(() => {
    const behavior = userBehavior.current;
    const predictions = [];
    
    // Most clicked resources
    const popularTargets = Array.from(behavior.clickPatterns.entries())
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([target]) => target);
    
    predictions.push(...popularTargets);
    
    // Time-based patterns
    const currentHour = new Date().getHours();
    if (currentHour >= 9 && currentHour <= 17) {
      predictions.push('/dashboard', '/reports');
    }
    
    return predictions;
  }, []);
  
  // Preload resources
  const preloadResource = useCallback(async (resource) => {
    if (preloadedResources.has(resource)) return;
    
    try {
      if (resource.startsWith('/')) {
        // Route preloading
        const routeComponent = getRouteComponent(resource);
        if (routeComponent) {
          await routeComponent();
        }
      } else {
        // Asset preloading
        await preloadAsset(resource);
      }
      
      setPreloadedResources(prev => new Set(prev).add(resource));
    } catch (error) {
      console.warn(`Failed to preload ${resource}:`, error);
    }
  }, [preloadedResources]);
  
  // Process preload queue
  useEffect(() => {
    const processQueue = async () => {
      for (const resource of preloadQueue) {
        await preloadResource(resource);
        // Add delay to prevent overwhelming
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      setPreloadQueue([]);
    };
    
    if (preloadQueue.length > 0) {
      processQueue();
    }
  }, [preloadQueue, preloadResource]);
  
  // Auto-predict and preload
  useEffect(() => {
    const interval = setInterval(() => {
      const predictions = predictNextResources();
      setPreloadQueue(predictions.filter(p => !preloadedResources.has(p)));
    }, 5000);
    
    return () => clearInterval(interval);
  }, [predictNextResources, preloadedResources]);
  
  return {
    trackInteraction,
    preloadResource,
    preloadedResources: Array.from(preloadedResources)
  };
}

// Asset preloading utilities
async function preloadAsset(url) {
  const link = document.createElement('link');
  
  return new Promise((resolve, reject) => {
    link.rel = 'preload';
    link.href = url;
    
    // Determine asset type
    if (url.includes('.css')) {
      link.as = 'style';
    } else if (url.includes('.js')) {
      link.as = 'script';
    } else if (url.match(/\.(png|jpg|jpeg|gif|webp)$/)) {
      link.as = 'image';
    } else if (url.includes('.woff')) {
      link.as = 'font';
      link.type = 'font/woff2';
      link.crossOrigin = 'anonymous';
    }
    
    link.onload = resolve;
    link.onerror = reject;
    
    document.head.appendChild(link);
  });
}
```

### Hover-Based Preloading

```jsx
// Hover-triggered preloading
function useHoverPreloading(delay = 300) {
  const timeouts = useRef(new Map());
  const preloadedLinks = useRef(new Set());
  
  const handleMouseEnter = useCallback((href, preloadFunction) => {
    if (preloadedLinks.current.has(href)) return;
    
    const timeoutId = setTimeout(() => {
      preloadFunction()
        .then(() => {
          preloadedLinks.current.add(href);
        })
        .catch(console.error);
    }, delay);
    
    timeouts.current.set(href, timeoutId);
  }, [delay]);
  
  const handleMouseLeave = useCallback((href) => {
    const timeoutId = timeouts.current.get(href);
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeouts.current.delete(href);
    }
  }, []);
  
  return { handleMouseEnter, handleMouseLeave };
}

// Smart navigation component
function SmartNavigation({ links }) {
  const { handleMouseEnter, handleMouseLeave } = useHoverPreloading();
  
  return (
    <nav>
      {links.map(link => (
        <Link
          key={link.href}
          to={link.href}
          onMouseEnter={() => handleMouseEnter(link.href, link.preload)}
          onMouseLeave={() => handleMouseLeave(link.href)}
        >
          {link.title}
        </Link>
      ))}
    </nav>
  );
}
```

## Summary

Code splitting and lazy loading are essential techniques for optimizing React application performance. Key takeaways:

### Benefits:
1. **Reduced initial bundle size** - Faster first page load
2. **Improved perceived performance** - Progressive loading
3. **Better resource utilization** - Load only what's needed
4. **Enhanced user experience** - Responsive navigation

### Best Practices:
1. **Split at route boundaries** for maximum impact
2. **Use intersection observer** for component-level lazy loading
3. **Implement intelligent preloading** based on user behavior
4. **Add proper loading states** and error boundaries
5. **Monitor bundle sizes** and loading performance

### When to Use:
- Large applications with multiple routes
- Feature-rich dashboards with conditional components
- Applications with heavy third-party libraries
- Multi-tenant applications with different feature sets
- Progressive web applications (PWAs)

These strategies ensure your React applications load quickly and efficiently, providing users with fast, responsive experiences regardless of application complexity.
