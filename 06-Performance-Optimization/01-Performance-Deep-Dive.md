# React Performance Optimization Deep Dive

## Table of Contents
1. [Performance Measurement and Profiling](#performance-measurement-and-profiling)
2. [Advanced Memoization Strategies](#advanced-memoization-strategies)
3. [Bundle Optimization Techniques](#bundle-optimization-techniques)
4. [Memory Management and Leaks](#memory-management-and-leaks)
5. [Large Dataset Handling](#large-dataset-handling)
6. [Network Performance](#network-performance)
7. [Real-World Performance Patterns](#real-world-performance-patterns)

## Performance Measurement and Profiling

### 1. React DevTools Profiler Deep Dive

#### Understanding Profiler Metrics
```jsx
import { Profiler } from 'react';

function DetailedProfiler({ children, id }) {
  const onRenderCallback = (
    profilerId,     // The "id" prop of the Profiler tree that has just committed
    phase,          // Either "mount" (if the tree just mounted) or "update"
    actualDuration, // Time spent rendering the committed update
    baseDuration,   // Estimated time to render the entire subtree without memoization
    startTime,      // When React began rendering this update
    commitTime,     // When React committed this update
    interactions    // Set of interactions that were traced for this update
  ) => {
    // Performance analytics
    const performanceData = {
      component: profilerId,
      phase,
      renderTime: actualDuration,
      potentialTime: baseDuration,
      efficiency: ((baseDuration - actualDuration) / baseDuration * 100).toFixed(2),
      timestamp: commitTime
    };
    
    // Log slow renders
    if (actualDuration > 16) { // More than one frame
      console.warn(`Slow render detected in ${profilerId}:`, performanceData);
    }
    
    // Send to analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'react_render', {
        custom_parameter_1: profilerId,
        custom_parameter_2: actualDuration
      });
    }
  };
  
  return (
    <Profiler id={id} onRender={onRenderCallback}>
      {children}
    </Profiler>
  );
}
```

#### Custom Performance Hooks
```jsx
// Hook for measuring component render times
function useRenderTime(componentName) {
  const renderStartTime = useRef();
  const [renderTimes, setRenderTimes] = useState([]);
  
  // Mark render start
  useEffect(() => {
    renderStartTime.current = performance.now();
  });
  
  // Mark render end
  useLayoutEffect(() => {
    const renderTime = performance.now() - renderStartTime.current;
    setRenderTimes(prev => [...prev.slice(-9), renderTime]); // Keep last 10
    
    if (renderTime > 16) {
      console.warn(`${componentName} took ${renderTime.toFixed(2)}ms to render`);
    }
  });
  
  const averageRenderTime = renderTimes.length > 0 
    ? renderTimes.reduce((a, b) => a + b, 0) / renderTimes.length 
    : 0;
  
  return {
    lastRenderTime: renderTimes[renderTimes.length - 1] || 0,
    averageRenderTime,
    renderTimes
  };
}

// Hook for tracking component mount/unmount cycles
function useComponentLifecycle(componentName) {
  const mountTime = useRef();
  const [mountCount, setMountCount] = useState(0);
  
  useEffect(() => {
    mountTime.current = performance.now();
    setMountCount(prev => prev + 1);
    
    console.log(`${componentName} mounted at ${mountTime.current}`);
    
    return () => {
      const lifetime = performance.now() - mountTime.current;
      console.log(`${componentName} unmounted after ${lifetime.toFixed(2)}ms`);
    };
  }, [componentName]);
  
  return { mountCount };
}
```

### 2. Web Vitals Integration
```jsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function useWebVitals() {
  const [vitals, setVitals] = useState({});
  
  useEffect(() => {
    const updateVitals = (metric) => {
      setVitals(prev => ({
        ...prev,
        [metric.name]: {
          value: metric.value,
          rating: metric.rating,
          delta: metric.delta
        }
      }));
    };
    
    getCLS(updateVitals);
    getFID(updateVitals);
    getFCP(updateVitals);
    getLCP(updateVitals);
    getTTFB(updateVitals);
  }, []);
  
  return vitals;
}

// Component to display performance metrics
function PerformanceMonitor() {
  const vitals = useWebVitals();
  const isDev = process.env.NODE_ENV === 'development';
  
  if (!isDev) return null;
  
  return (
    <div style={{ 
      position: 'fixed', 
      top: 10, 
      right: 10, 
      background: 'rgba(0,0,0,0.8)', 
      color: 'white', 
      padding: '10px',
      borderRadius: '5px',
      fontSize: '12px',
      fontFamily: 'monospace'
    }}>
      <h4>Web Vitals</h4>
      {Object.entries(vitals).map(([name, metric]) => (
        <div key={name} style={{ 
          color: metric.rating === 'good' ? 'green' : 
                 metric.rating === 'needs-improvement' ? 'orange' : 'red' 
        }}>
          {name}: {metric.value.toFixed(2)} ({metric.rating})
        </div>
      ))}
    </div>
  );
}
```

## Advanced Memoization Strategies

### 1. Selective Memoization
```jsx
// Smart memoization based on prop complexity
function smartMemo(Component) {
  return React.memo(Component, (prevProps, nextProps) => {
    const prevKeys = Object.keys(prevProps);
    const nextKeys = Object.keys(nextProps);
    
    if (prevKeys.length !== nextKeys.length) {
      return false;
    }
    
    for (let key of prevKeys) {
      const prevValue = prevProps[key];
      const nextValue = nextProps[key];
      
      // Deep comparison for objects and arrays
      if (typeof prevValue === 'object' && prevValue !== null) {
        if (!deepEqual(prevValue, nextValue)) {
          return false;
        }
      } else if (prevValue !== nextValue) {
        return false;
      }
    }
    
    return true;
  });
}

// Deep equality check (simplified)
function deepEqual(obj1, obj2) {
  if (obj1 === obj2) return true;
  
  if (obj1 == null || obj2 == null) return false;
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  for (let key of keys1) {
    if (!keys2.includes(key)) return false;
    
    if (!deepEqual(obj1[key], obj2[key])) return false;
  }
  
  return true;
}
```

### 2. Memoization with Dependencies
```jsx
// Advanced useMemo with dependency tracking
function useAdvancedMemo(factory, deps) {
  const prevDepsRef = useRef();
  const memoizedValueRef = useRef();
  
  // Custom dependency comparison
  const depsChanged = useMemo(() => {
    if (!prevDepsRef.current) return true;
    
    if (!deps || !prevDepsRef.current) return true;
    
    if (deps.length !== prevDepsRef.current.length) return true;
    
    return deps.some((dep, index) => {
      const prevDep = prevDepsRef.current[index];
      
      // Handle different types of dependencies
      if (typeof dep === 'object' && dep !== null) {
        return !deepEqual(dep, prevDep);
      }
      
      return dep !== prevDep;
    });
  }, deps);
  
  if (depsChanged) {
    memoizedValueRef.current = factory();
    prevDepsRef.current = deps;
  }
  
  return memoizedValueRef.current;
}

// Memoization with expiration
function useMemoWithExpiration(factory, deps, expirationMs = 5000) {
  const timestampRef = useRef(0);
  const valueRef = useRef();
  
  const value = useMemo(() => {
    const now = Date.now();
    
    if (now - timestampRef.current > expirationMs || !valueRef.current) {
      valueRef.current = factory();
      timestampRef.current = now;
    }
    
    return valueRef.current;
  }, deps);
  
  return value;
}
```

### 3. Intelligent Component Splitting
```jsx
// Split components to optimize re-renders
function UserDashboard({ user, posts, notifications }) {
  return (
    <div>
      {/* User info rarely changes */}
      <UserProfile user={user} />
      
      {/* Posts change frequently */}
      <PostsList posts={posts} />
      
      {/* Notifications change very frequently */}
      <NotificationCenter notifications={notifications} />
    </div>
  );
}

// Optimize by splitting into separate components
const UserProfile = React.memo(function UserProfile({ user }) {
  return <div>{user.name} - {user.email}</div>;
});

const PostsList = React.memo(function PostsList({ posts }) {
  return (
    <div>
      {posts.map(post => <PostItem key={post.id} post={post} />)}
    </div>
  );
});

const NotificationCenter = React.memo(function NotificationCenter({ notifications }) {
  // Further optimization: only show recent notifications
  const recentNotifications = useMemo(() => 
    notifications.slice(0, 5), [notifications]
  );
  
  return (
    <div>
      {recentNotifications.map(notification => 
        <NotificationItem key={notification.id} notification={notification} />
      )}
    </div>
  );
});
```

## Bundle Optimization Techniques

### 1. Advanced Code Splitting
```jsx
// Route-based splitting with preloading
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));
const Profile = lazy(() => import('./Profile'));
const Settings = lazy(() => import('./Settings'));

// Preload routes on hover
function NavLink({ to, children, preload }) {
  const handleMouseEnter = () => {
    if (preload) {
      preload();
    }
  };
  
  return (
    <Link to={to} onMouseEnter={handleMouseEnter}>
      {children}
    </Link>
  );
}

// Usage with preloading
function Navigation() {
  return (
    <nav>
      <NavLink 
        to="/dashboard" 
        preload={() => import('./Dashboard')}
      >
        Dashboard
      </NavLink>
      <NavLink 
        to="/profile" 
        preload={() => import('./Profile')}
      >
        Profile
      </NavLink>
    </nav>
  );
}
```

### 2. Dynamic Imports with Error Handling
```jsx
// Robust dynamic importing
function useDynamicImport(importFunction) {
  const [state, setState] = useState({
    component: null,
    loading: true,
    error: null
  });
  
  useEffect(() => {
    let cancelled = false;
    
    importFunction()
      .then(module => {
        if (!cancelled) {
          setState({
            component: module.default,
            loading: false,
            error: null
          });
        }
      })
      .catch(error => {
        if (!cancelled) {
          setState({
            component: null,
            loading: false,
            error
          });
        }
      });
    
    return () => {
      cancelled = true;
    };
  }, [importFunction]);
  
  return state;
}

// Usage
function LazyComponentLoader({ importFunction, fallback, errorFallback }) {
  const { component: Component, loading, error } = useDynamicImport(importFunction);
  
  if (loading) return fallback || <div>Loading...</div>;
  if (error) return errorFallback || <div>Failed to load component</div>;
  if (!Component) return null;
  
  return <Component />;
}
```

### 3. Tree Shaking Optimization
```jsx
// Instead of importing entire libraries
import _ from 'lodash'; // ❌ Imports entire library

// Import only what you need
import debounce from 'lodash/debounce'; // ✅ Tree-shakeable

// Or use ES6 imports with proper tree-shaking
import { debounce } from 'lodash-es'; // ✅ Better tree-shaking

// Custom utility functions for common operations
const utils = {
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  throttle: (func, limit) => {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    }
  }
};
```

## Memory Management and Leaks

### 1. Memory Leak Detection
```jsx
// Hook to detect memory leaks
function useMemoryLeakDetection(componentName) {
  const mountTime = useRef(Date.now());
  const timers = useRef(new Set());
  const listeners = useRef(new Set());
  
  // Track timers
  const safeSetTimeout = useCallback((callback, delay) => {
    const id = setTimeout(callback, delay);
    timers.current.add(id);
    return id;
  }, []);
  
  const safeSetInterval = useCallback((callback, delay) => {
    const id = setInterval(callback, delay);
    timers.current.add(id);
    return id;
  }, []);
  
  // Track event listeners
  const safeAddEventListener = useCallback((element, event, handler, options) => {
    element.addEventListener(event, handler, options);
    listeners.current.add({ element, event, handler, options });
  }, []);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Clear all timers
      timers.current.forEach(id => {
        clearTimeout(id);
        clearInterval(id);
      });
      
      // Remove all event listeners
      listeners.current.forEach(({ element, event, handler, options }) => {
        element.removeEventListener(event, handler, options);
      });
      
      const lifetime = Date.now() - mountTime.current;
      console.log(`${componentName} cleaned up after ${lifetime}ms`);
    };
  }, [componentName]);
  
  return {
    safeSetTimeout,
    safeSetInterval,
    safeAddEventListener
  };
}

// Usage
function ComponentWithCleanup() {
  const { safeSetTimeout, safeAddEventListener } = useMemoryLeakDetection('ComponentWithCleanup');
  
  useEffect(() => {
    // Safe timer usage
    safeSetTimeout(() => {
      console.log('This will be cleaned up automatically');
    }, 1000);
    
    // Safe event listener usage
    const handleResize = () => console.log('Window resized');
    safeAddEventListener(window, 'resize', handleResize);
  }, [safeSetTimeout, safeAddEventListener]);
  
  return <div>Component with automatic cleanup</div>;
}
```

### 2. Reference Management
```jsx
// Hook for managing object references
function useStableReference(value) {
  const ref = useRef(value);
  const [, forceUpdate] = useReducer(x => x + 1, 0);
  
  // Update reference only when value actually changes
  if (!Object.is(ref.current, value)) {
    ref.current = value;
    forceUpdate();
  }
  
  return ref.current;
}

// Weak reference management for large objects
function useWeakReference(value) {
  const weakRef = useRef(new WeakRef(value));
  
  useEffect(() => {
    weakRef.current = new WeakRef(value);
  }, [value]);
  
  const getValue = useCallback(() => {
    return weakRef.current.deref();
  }, []);
  
  return getValue;
}
```

## Large Dataset Handling

### 1. Advanced Virtual Scrolling
```jsx
// Custom virtual scrolling with dynamic item heights
function useVirtualScrolling({
  items,
  containerHeight,
  estimateItemHeight,
  getItemHeight,
  overscan = 5
}) {
  const [scrollTop, setScrollTop] = useState(0);
  const [itemHeights, setItemHeights] = useState(new Map());
  
  // Calculate visible range
  const { startIndex, endIndex, totalHeight, offsetY } = useMemo(() => {
    let accumulatedHeight = 0;
    let startIndex = 0;
    let endIndex = 0;
    
    // Find start index
    for (let i = 0; i < items.length; i++) {
      const itemHeight = itemHeights.get(i) || estimateItemHeight(i);
      if (accumulatedHeight + itemHeight > scrollTop) {
        startIndex = Math.max(0, i - overscan);
        break;
      }
      accumulatedHeight += itemHeight;
    }
    
    // Find end index
    accumulatedHeight = 0;
    for (let i = startIndex; i < items.length; i++) {
      const itemHeight = itemHeights.get(i) || estimateItemHeight(i);
      accumulatedHeight += itemHeight;
      if (accumulatedHeight > containerHeight) {
        endIndex = Math.min(items.length - 1, i + overscan);
        break;
      }
    }
    
    // Calculate total height
    const totalHeight = items.reduce((total, _, index) => {
      return total + (itemHeights.get(index) || estimateItemHeight(index));
    }, 0);
    
    // Calculate offset
    let offsetY = 0;
    for (let i = 0; i < startIndex; i++) {
      offsetY += itemHeights.get(i) || estimateItemHeight(i);
    }
    
    return { startIndex, endIndex, totalHeight, offsetY };
  }, [items, scrollTop, containerHeight, itemHeights, estimateItemHeight, overscan]);
  
  // Measure item height
  const measureItem = useCallback((index, height) => {
    setItemHeights(prev => new Map(prev.set(index, height)));
  }, []);
  
  const visibleItems = items.slice(startIndex, endIndex + 1);
  
  return {
    visibleItems,
    startIndex,
    endIndex,
    totalHeight,
    offsetY,
    onScroll: (e) => setScrollTop(e.target.scrollTop),
    measureItem
  };
}
```

### 2. Data Pagination and Infinite Scroll
```jsx
// Advanced infinite scroll with bidirectional loading
function useInfiniteScroll({
  fetchMore,
  fetchPrevious,
  hasNextPage,
  hasPreviousPage,
  threshold = 100
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const containerRef = useRef();
  
  const loadMore = useCallback(async () => {
    if (loading || !hasNextPage) return;
    
    setLoading(true);
    setError(null);
    
    try {
      await fetchMore();
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [loading, hasNextPage, fetchMore]);
  
  const loadPrevious = useCallback(async () => {
    if (loading || !hasPreviousPage) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const scrollHeight = containerRef.current?.scrollHeight;
      await fetchPrevious();
      
      // Maintain scroll position when prepending items
      if (containerRef.current) {
        const newScrollHeight = containerRef.current.scrollHeight;
        containerRef.current.scrollTop += newScrollHeight - scrollHeight;
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [loading, hasPreviousPage, fetchPrevious]);
  
  // Scroll event handler
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      
      // Load more when near bottom
      if (scrollHeight - scrollTop - clientHeight < threshold) {
        loadMore();
      }
      
      // Load previous when near top
      if (scrollTop < threshold) {
        loadPrevious();
      }
    };
    
    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [loadMore, loadPrevious, threshold]);
  
  return {
    containerRef,
    loading,
    error,
    loadMore,
    loadPrevious
  };
}
```

## Network Performance

### 1. Request Deduplication and Caching
```jsx
// Advanced data fetching with caching and deduplication
class DataCache {
  constructor() {
    this.cache = new Map();
    this.pending = new Map();
  }
  
  async get(key, fetcher, options = {}) {
    const { maxAge = 300000, staleWhileRevalidate = false } = options;
    
    // Check cache
    const cached = this.cache.get(key);
    if (cached) {
      const isStale = Date.now() - cached.timestamp > maxAge;
      
      if (!isStale) {
        return cached.data;
      }
      
      if (staleWhileRevalidate) {
        // Return stale data while revalidating in background
        this.revalidate(key, fetcher, options);
        return cached.data;
      }
    }
    
    // Check if request is already pending
    if (this.pending.has(key)) {
      return this.pending.get(key);
    }
    
    // Make new request
    const promise = fetcher().then(data => {
      this.cache.set(key, {
        data,
        timestamp: Date.now()
      });
      this.pending.delete(key);
      return data;
    }).catch(error => {
      this.pending.delete(key);
      throw error;
    });
    
    this.pending.set(key, promise);
    return promise;
  }
  
  async revalidate(key, fetcher, options) {
    try {
      const data = await fetcher();
      this.cache.set(key, {
        data,
        timestamp: Date.now()
      });
    } catch (error) {
      console.error('Revalidation failed:', error);
    }
  }
  
  clear(pattern) {
    if (pattern instanceof RegExp) {
      for (const key of this.cache.keys()) {
        if (pattern.test(key)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.delete(pattern);
    }
  }
}

const dataCache = new DataCache();

// Hook for cached data fetching
function useCachedData(key, fetcher, options = {}) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null
  });
  
  useEffect(() => {
    let cancelled = false;
    
    dataCache.get(key, fetcher, options)
      .then(data => {
        if (!cancelled) {
          setState({ data, loading: false, error: null });
        }
      })
      .catch(error => {
        if (!cancelled) {
          setState({ data: null, loading: false, error });
        }
      });
    
    return () => {
      cancelled = true;
    };
  }, [key, fetcher, options]);
  
  const mutate = useCallback((newData) => {
    setState(prev => ({ ...prev, data: newData }));
    dataCache.cache.set(key, {
      data: newData,
      timestamp: Date.now()
    });
  }, [key]);
  
  return { ...state, mutate };
}
```

### 2. Request Batching
```jsx
// Batch multiple requests together
class RequestBatcher {
  constructor(batchFn, { maxBatchSize = 10, maxWaitTime = 50 } = {}) {
    this.batchFn = batchFn;
    this.maxBatchSize = maxBatchSize;
    this.maxWaitTime = maxWaitTime;
    this.queue = [];
    this.timer = null;
  }
  
  request(item) {
    return new Promise((resolve, reject) => {
      this.queue.push({ item, resolve, reject });
      
      if (this.queue.length >= this.maxBatchSize) {
        this.flush();
      } else if (!this.timer) {
        this.timer = setTimeout(() => this.flush(), this.maxWaitTime);
      }
    });
  }
  
  async flush() {
    if (this.queue.length === 0) return;
    
    const batch = this.queue.splice(0);
    this.timer = null;
    
    try {
      const results = await this.batchFn(batch.map(b => b.item));
      
      batch.forEach((b, index) => {
        b.resolve(results[index]);
      });
    } catch (error) {
      batch.forEach(b => b.reject(error));
    }
  }
}

// Usage for batching user data requests
const userBatcher = new RequestBatcher(async (userIds) => {
  const response = await fetch('/api/users/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userIds })
  });
  return response.json();
});

function useUser(userId) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    userBatcher.request(userId).then(setUser);
  }, [userId]);
  
  return user;
}
```

## Real-World Performance Patterns

### 1. E-commerce Product List Optimization
```jsx
// Optimized product list with advanced filtering
function ProductList({ filters, sortBy, searchTerm }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Debounced search to avoid excessive requests
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  
  // Memoized filtered and sorted products
  const filteredProducts = useMemo(() => {
    return products
      .filter(product => {
        // Search filter
        if (debouncedSearchTerm) {
          const searchLower = debouncedSearchTerm.toLowerCase();
          if (!product.name.toLowerCase().includes(searchLower) &&
              !product.description.toLowerCase().includes(searchLower)) {
            return false;
          }
        }
        
        // Category filter
        if (filters.category && product.category !== filters.category) {
          return false;
        }
        
        // Price range filter
        if (filters.priceRange) {
          const [min, max] = filters.priceRange;
          if (product.price < min || product.price > max) {
            return false;
          }
        }
        
        return true;
      })
      .sort((a, b) => {
        switch (sortBy) {
          case 'price-asc':
            return a.price - b.price;
          case 'price-desc':
            return b.price - a.price;
          case 'name':
            return a.name.localeCompare(b.name);
          default:
            return 0;
        }
      });
  }, [products, filters, sortBy, debouncedSearchTerm]);
  
  // Virtual scrolling for large product lists
  const {
    visibleItems,
    totalHeight,
    offsetY,
    onScroll
  } = useVirtualScrolling({
    items: filteredProducts,
    containerHeight: 600,
    estimateItemHeight: () => 200
  });
  
  return (
    <div className="product-list">
      <div 
        className="product-container"
        style={{ height: 600, overflow: 'auto' }}
        onScroll={onScroll}
      >
        <div style={{ height: totalHeight, position: 'relative' }}>
          <div style={{ transform: `translateY(${offsetY}px)` }}>
            {visibleItems.map(product => (
              <ProductCard 
                key={product.id} 
                product={product}
                onAddToCart={handleAddToCart}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Memoized product card
const ProductCard = React.memo(function ProductCard({ product, onAddToCart }) {
  const handleAddToCart = useCallback(() => {
    onAddToCart(product);
  }, [product, onAddToCart]);
  
  return (
    <div className="product-card">
      <LazyImage src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>{product.description}</p>
      <span>${product.price}</span>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
});
```

### 2. Dashboard with Real-time Updates
```jsx
// Optimized dashboard with selective updates
function Dashboard() {
  const [metrics, setMetrics] = useState({});
  const [charts, setCharts] = useState({});
  const [lastUpdate, setLastUpdate] = useState(Date.now());
  
  // Separate state updates to prevent unnecessary re-renders
  const updateMetrics = useCallback((newMetrics) => {
    setMetrics(prev => {
      // Only update if values actually changed
      const hasChanges = Object.keys(newMetrics).some(
        key => prev[key] !== newMetrics[key]
      );
      return hasChanges ? { ...prev, ...newMetrics } : prev;
    });
  }, []);
  
  const updateCharts = useCallback((newCharts) => {
    setCharts(prev => ({ ...prev, ...newCharts }));
  }, []);
  
  // WebSocket connection with selective updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/dashboard');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Route updates to appropriate state updaters
      if (data.type === 'metrics') {
        updateMetrics(data.payload);
      } else if (data.type === 'charts') {
        updateCharts(data.payload);
      }
      
      setLastUpdate(Date.now());
    };
    
    return () => ws.close();
  }, [updateMetrics, updateCharts]);
  
  return (
    <div className="dashboard">
      <MetricsPanel metrics={metrics} />
      <ChartsPanel charts={charts} />
      <LastUpdated timestamp={lastUpdate} />
    </div>
  );
}

// Memoized panels to prevent unnecessary re-renders
const MetricsPanel = React.memo(function MetricsPanel({ metrics }) {
  return (
    <div className="metrics-panel">
      {Object.entries(metrics).map(([key, value]) => (
        <MetricCard key={key} name={key} value={value} />
      ))}
    </div>
  );
});

const ChartsPanel = React.memo(function ChartsPanel({ charts }) {
  return (
    <div className="charts-panel">
      {Object.entries(charts).map(([key, data]) => (
        <Chart key={key} type={key} data={data} />
      ))}
    </div>
  );
});
```

---

This deep dive covers advanced performance optimization techniques that are essential for building high-performance React applications at scale. Focus on measuring performance before optimizing, and always validate that your optimizations actually improve performance in real-world scenarios.
