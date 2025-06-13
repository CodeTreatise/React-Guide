# Module 6: Performance Optimization

## 🎯 Learning Objectives
By the end of this module, you will:
- Master React's built-in performance optimization techniques
- Understand profiling and measuring React application performance
- Implement advanced memoization strategies
- Optimize bundle size and loading performance
- Handle large datasets efficiently
- Implement virtual scrolling and lazy loading
- Optimize state management for performance
- Debug and identify performance bottlenecks

## 📚 Module Overview

### What You'll Learn
Performance optimization is crucial for creating smooth, responsive React applications. This module covers everything from React-specific optimizations to broader web performance techniques that apply to React applications.

### Prerequisites
- Solid understanding of React fundamentals (Modules 1-3)
- Experience with hooks and state management (Modules 4-5)
- Basic understanding of JavaScript performance concepts
- Familiarity with browser DevTools

## 🏗️ Core Concepts

### 1. React Performance Fundamentals

#### Understanding Re-renders
```jsx
// Problem: Unnecessary re-renders
function App() {
  const [count, setCount] = useState(0);
  const [user, setUser] = useState({ name: 'John' });
  
  // This object is recreated on every render
  const userProfile = {
    ...user,
    isLoggedIn: true
  };
  
  return (
    <div>
      <Counter count={count} setCount={setCount} />
      <UserProfile user={userProfile} /> {/* Re-renders even when count changes */}
    </div>
  );
}

// Solution: Memoization
function App() {
  const [count, setCount] = useState(0);
  const [user, setUser] = useState({ name: 'John' });
  
  // Memoized to prevent unnecessary recreations
  const userProfile = useMemo(() => ({
    ...user,
    isLoggedIn: true
  }), [user]);
  
  return (
    <div>
      <Counter count={count} setCount={setCount} />
      <UserProfile user={userProfile} />
    </div>
  );
}
```

#### React.memo for Component Memoization
```jsx
// Prevent re-renders when props haven't changed
const ExpensiveComponent = React.memo(function ExpensiveComponent({ data, onUpdate }) {
  console.log('ExpensiveComponent rendered');
  
  return (
    <div>
      {data.map(item => (
        <ComplexItem key={item.id} item={item} onUpdate={onUpdate} />
      ))}
    </div>
  );
});

// Custom comparison function for complex props
const SmartComponent = React.memo(function SmartComponent({ user, settings }) {
  return <div>{user.name} - {settings.theme}</div>;
}, (prevProps, nextProps) => {
  // Custom comparison logic
  return (
    prevProps.user.id === nextProps.user.id &&
    prevProps.settings.theme === nextProps.settings.theme
  );
});
```

### 2. Advanced Memoization Patterns

#### useMemo for Expensive Calculations
```jsx
function DataAnalytics({ data, filters }) {
  // Expensive calculation that should only run when data or filters change
  const processedData = useMemo(() => {
    console.log('Processing data...');
    
    return data
      .filter(item => {
        return Object.entries(filters).every(([key, value]) => 
          !value || item[key] === value
        );
      })
      .map(item => ({
        ...item,
        score: calculateComplexScore(item), // Expensive operation
        category: determineCategory(item)   // Another expensive operation
      }))
      .sort((a, b) => b.score - a.score);
  }, [data, filters]);
  
  // Memoized chart data
  const chartData = useMemo(() => {
    return processedData.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + item.score;
      return acc;
    }, {});
  }, [processedData]);
  
  return (
    <div>
      <DataTable data={processedData} />
      <Chart data={chartData} />
    </div>
  );
}
```

#### useCallback for Function Stability
```jsx
function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [filter, setFilter] = useState('all');
  
  // Stable function references prevent child re-renders
  const addTodo = useCallback((text) => {
    setTodos(prev => [...prev, { 
      id: Date.now(), 
      text, 
      completed: false 
    }]);
  }, []);
  
  const toggleTodo = useCallback((id) => {
    setTodos(prev => prev.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  }, []);
  
  const deleteTodo = useCallback((id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  }, []);
  
  // Filtered todos with memoization
  const filteredTodos = useMemo(() => {
    switch (filter) {
      case 'active':
        return todos.filter(todo => !todo.completed);
      case 'completed':
        return todos.filter(todo => todo.completed);
      default:
        return todos;
    }
  }, [todos, filter]);
  
  return (
    <div>
      <TodoForm onAdd={addTodo} />
      <TodoList 
        todos={filteredTodos}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
      />
      <TodoFilters filter={filter} onFilterChange={setFilter} />
    </div>
  );
}

// Memoized child components
const TodoList = React.memo(function TodoList({ todos, onToggle, onDelete }) {
  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
});
```

### 3. Virtual Scrolling and Windowing

#### Basic Virtual Scrolling Implementation
```jsx
import { FixedSizeList as List } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ItemComponent item={items[index]} />
    </div>
  );
  
  return (
    <List
      height={600}      // Container height
      itemCount={items.length}
      itemSize={50}     // Height of each item
    >
      {Row}
    </List>
  );
}

// Custom virtual scrolling hook
function useVirtualScrolling(items, containerHeight, itemHeight) {
  const [scrollTop, setScrollTop] = useState(0);
  
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length - 1
  );
  
  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    onScroll: (e) => setScrollTop(e.target.scrollTop)
  };
}
```

### 4. Lazy Loading and Code Splitting

#### Component-Level Lazy Loading
```jsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const Dashboard = lazy(() => import('./Dashboard'));
const Reports = lazy(() => import('./Reports'));
const Settings = lazy(() => import('./Settings'));

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  
  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
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

// Advanced lazy loading with error boundaries
const LazyComponent = lazy(() => 
  import('./HeavyComponent').catch(error => {
    console.error('Failed to load component:', error);
    return { default: ErrorFallback };
  })
);
```

#### Image Lazy Loading
```jsx
function LazyImage({ src, alt, placeholder, ...props }) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [inView, setInView] = useState(false);
  const imgRef = useRef();
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    
    return () => observer.disconnect();
  }, []);
  
  return (
    <div ref={imgRef} {...props}>
      {inView && (
        <>
          {!imageLoaded && placeholder && (
            <img src={placeholder} alt={alt} />
          )}
          <img
            src={src}
            alt={alt}
            style={{ display: imageLoaded ? 'block' : 'none' }}
            onLoad={() => setImageLoaded(true)}
          />
        </>
      )}
    </div>
  );
}
```

### 5. State Management Optimization

#### Optimizing Context Performance
```jsx
// Split contexts to prevent unnecessary re-renders
const UserContext = createContext();
const ThemeContext = createContext();
const NotificationContext = createContext();

// Instead of one large context
const AppContext = createContext();

// Optimize context updates
function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  
  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(() => ({
    user,
    setUser,
    updateUser: (updates) => setUser(prev => ({ ...prev, ...updates })),
    logout: () => setUser(null)
  }), [user]);
  
  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}

// Selector pattern for fine-grained updates
function useUserSelector(selector) {
  const context = useContext(UserContext);
  return useMemo(() => selector(context), [context, selector]);
}

// Usage with selector
function UserName() {
  const name = useUserSelector(ctx => ctx.user?.name);
  return <span>{name}</span>;
}
```

#### State Normalization
```jsx
// Problem: Nested state causes deep updates
const [posts, setPosts] = useState([
  {
    id: 1,
    title: 'Post 1',
    author: { id: 1, name: 'John' },
    comments: [
      { id: 1, text: 'Comment 1', author: { id: 2, name: 'Jane' } }
    ]
  }
]);

// Solution: Normalized state structure
const [entities, setEntities] = useState({
  posts: {
    1: { id: 1, title: 'Post 1', authorId: 1, commentIds: [1] }
  },
  users: {
    1: { id: 1, name: 'John' },
    2: { id: 2, name: 'Jane' }
  },
  comments: {
    1: { id: 1, text: 'Comment 1', authorId: 2 }
  }
});

// Selectors for denormalized data
const usePost = (id) => {
  return useMemo(() => {
    const post = entities.posts[id];
    if (!post) return null;
    
    return {
      ...post,
      author: entities.users[post.authorId],
      comments: post.commentIds.map(commentId => ({
        ...entities.comments[commentId],
        author: entities.users[entities.comments[commentId].authorId]
      }))
    };
  }, [entities, id]);
};
```

### 6. Performance Monitoring and Profiling

#### React DevTools Profiler
```jsx
import { Profiler } from 'react';

function App() {
  const onRenderCallback = (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
    console.log('Profiler:', {
      id,
      phase,
      actualDuration,
      baseDuration,
      startTime,
      commitTime
    });
  };
  
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Router>
    </Profiler>
  );
}
```

#### Performance Metrics Hook
```jsx
function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState({});
  
  useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        setMetrics(prev => ({
          ...prev,
          [entry.name]: {
            duration: entry.duration,
            startTime: entry.startTime,
            type: entry.entryType
          }
        }));
      });
    });
    
    observer.observe({ entryTypes: ['measure', 'navigation', 'paint'] });
    
    return () => observer.disconnect();
  }, []);
  
  const measurePerformance = useCallback((name, fn) => {
    performance.mark(`${name}-start`);
    const result = fn();
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    return result;
  }, []);
  
  return { metrics, measurePerformance };
}
```

## 🛠️ Practical Exercises

### Exercise 1: Optimize a Slow Component
Take a component that renders a large list and apply various optimization techniques:
- React.memo
- useMemo for filtering/sorting
- useCallback for event handlers
- Virtual scrolling

### Exercise 2: Bundle Size Analysis
Analyze and optimize your app's bundle size:
- Use webpack-bundle-analyzer
- Implement code splitting
- Optimize dependencies
- Implement tree shaking

### Exercise 3: Performance Profiling
Profile a React app and identify bottlenecks:
- Use React DevTools Profiler
- Implement performance monitoring
- Create performance budgets
- Set up automated performance testing

### Exercise 4: State Management Optimization
Optimize a complex state management scenario:
- Normalize state structure
- Split contexts appropriately
- Implement selectors
- Reduce unnecessary re-renders

## 🎯 Assessment Criteria

### Beginner Level (60-70%)
- [ ] Understands when and how to use React.memo
- [ ] Can implement basic useMemo and useCallback optimizations
- [ ] Knows how to identify performance issues in React DevTools

### Intermediate Level (70-85%)
- [ ] Masters advanced memoization patterns
- [ ] Implements virtual scrolling for large datasets
- [ ] Understands bundle optimization techniques
- [ ] Can profile and debug performance issues

### Advanced Level (85-100%)
- [ ] Implements comprehensive performance monitoring
- [ ] Optimizes complex state management scenarios
- [ ] Creates performance budgets and automated testing
- [ ] Mentors others on React performance best practices

## 📊 Performance Checklist

### React-Specific Optimizations
- [ ] Use React.memo for expensive components
- [ ] Implement useMemo for expensive calculations
- [ ] Use useCallback for stable function references
- [ ] Avoid inline objects and functions in JSX
- [ ] Optimize context usage and prevent unnecessary re-renders
- [ ] Implement proper key props for lists
- [ ] Use lazy loading for route-based code splitting

### Bundle Optimization
- [ ] Implement tree shaking
- [ ] Use dynamic imports for code splitting
- [ ] Optimize dependencies (prefer smaller alternatives)
- [ ] Implement proper caching strategies
- [ ] Minimize and compress assets
- [ ] Use CDN for static assets

### Runtime Performance
- [ ] Implement virtual scrolling for large lists
- [ ] Use intersection observer for lazy loading
- [ ] Optimize images (lazy loading, proper formats, compression)
- [ ] Implement service workers for caching
- [ ] Monitor and track performance metrics
- [ ] Set up performance budgets

## 📖 Additional Resources

### Tools
- [React DevTools Profiler](https://react.dev/blog/2018/09/10/introducing-the-react-profiler)
- [webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Web Vitals](https://web.dev/vitals/)

### Libraries
- [react-window](https://github.com/bvaughn/react-window) - Efficient virtual scrolling
- [react-intersection-observer](https://github.com/thebuilder/react-intersection-observer)
- [react-loadable](https://github.com/jamiebuilds/react-loadable) - Code splitting

### Articles
- [React Performance Optimization](https://kentcdodds.com/blog/usememo-and-usecallback)
- [Profiling React Performance](https://calibreapp.com/blog/react-performance-profiling-optimization)

## 🔗 Next Steps
After completing this module, proceed to:
- Module 7: Routing (React Router)
- Module 8: Forms and Validation
- Advanced Projects: Build performance-optimized applications

---

⚡ **Pro Tips:**
- Profile first, optimize second - don't guess where the bottlenecks are
- Not all optimizations are worth it - measure the impact
- Consider the user experience when implementing optimizations
- Use performance budgets to prevent regressions
- Optimize for the right metrics (First Contentful Paint, Largest Contentful Paint, etc.)
