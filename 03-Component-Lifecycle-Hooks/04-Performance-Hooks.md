# Performance Hooks

## Table of Contents
1. [Introduction to Performance Hooks](#introduction-to-performance-hooks)
2. [useMemo Hook](#usememo-hook)
3. [useCallback Hook](#usecallback-hook)
4. [React.memo and Component Optimization](#reactmemo-and-component-optimization)
5. [useRef for Performance](#useref-for-performance)
6. [Advanced Performance Patterns](#advanced-performance-patterns)
7. [Performance Measurement Hooks](#performance-measurement-hooks)
8. [Virtual Lists and Windowing](#virtual-lists-and-windowing)
9. [Lazy Loading and Code Splitting](#lazy-loading-and-code-splitting)
10. [Memory Management](#memory-management)
11. [Performance Anti-patterns](#performance-anti-patterns)
12. [Profiling and Debugging](#profiling-and-debugging)

---

## Introduction to Performance Hooks

Performance hooks in React help optimize your application by preventing unnecessary re-renders, expensive calculations, and memory leaks. Understanding when and how to use these hooks is crucial for building fast, responsive applications.

### Why Performance Matters

```javascript
// ❌ SLOW: Expensive calculation on every render
function ExpensiveComponent({ items, filter }) {
  // This runs on every render, even if items/filter haven't changed
  const filteredItems = items.filter(item => {
    // Expensive operation
    return performComplexCalculation(item, filter);
  });

  const handleClick = () => {
    // This creates a new function on every render
    console.log('Clicked');
  };

  return (
    <div>
      {filteredItems.map(item => (
        <ExpensiveChild 
          key={item.id} 
          item={item} 
          onClick={handleClick} // Child will re-render unnecessarily
        />
      ))}
    </div>
  );
}

// ✅ FAST: Optimized with performance hooks
function OptimizedComponent({ items, filter }) {
  // Only recalculate when items or filter change
  const filteredItems = useMemo(() => {
    return items.filter(item => {
      return performComplexCalculation(item, filter);
    });
  }, [items, filter]);

  // Stable function reference
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []);

  return (
    <div>
      {filteredItems.map(item => (
        <ExpensiveChild 
          key={item.id} 
          item={item} 
          onClick={handleClick} // Won't cause unnecessary re-renders
        />
      ))}
    </div>
  );
}

// Memoized child component
const ExpensiveChild = React.memo(({ item, onClick }) => {
  console.log(`Rendering item ${item.id}`); // Will only log when item changes
  
  return (
    <div onClick={onClick}>
      {item.name}
    </div>
  );
});
```

### Performance Optimization Principles

1. **Prevent unnecessary re-renders** with React.memo
2. **Cache expensive calculations** with useMemo
3. **Stabilize function references** with useCallback
4. **Avoid creating objects/arrays in render**
5. **Use refs for values that don't need to trigger re-renders**
6. **Implement virtualization for large lists**
7. **Lazy load components and data**

---

## useMemo Hook

`useMemo` caches the result of expensive calculations and only recalculates when dependencies change.

### Basic Usage

```javascript
function DataProcessor({ data, filters, sortBy }) {
  // ❌ BAD: Expensive operation on every render
  const processedData = processLargeDataset(data, filters, sortBy);

  // ✅ GOOD: Only process when dependencies change
  const processedDataMemo = useMemo(() => {
    console.log('Processing data...'); // Only logs when dependencies change
    return processLargeDataset(data, filters, sortBy);
  }, [data, filters, sortBy]);

  return (
    <div>
      <DataVisualization data={processedDataMemo} />
    </div>
  );
}

function processLargeDataset(data, filters, sortBy) {
  // Simulate expensive processing
  return data
    .filter(item => {
      return Object.entries(filters).every(([key, value]) => {
        return item[key].includes(value);
      });
    })
    .sort((a, b) => {
      return a[sortBy].localeCompare(b[sortBy]);
    })
    .map(item => ({
      ...item,
      processedValue: expensiveCalculation(item)
    }));
}
```

### Complex Memoization Patterns

```javascript
function AdvancedMemoExample({ users, projects, tasks }) {
  // Memoize filtered users
  const activeUsers = useMemo(() => {
    return users.filter(user => user.isActive);
  }, [users]);

  // Memoize project statistics
  const projectStats = useMemo(() => {
    return projects.reduce((stats, project) => {
      stats[project.status] = (stats[project.status] || 0) + 1;
      return stats;
    }, {});
  }, [projects]);

  // Memoize complex aggregation
  const userTaskSummary = useMemo(() => {
    return activeUsers.map(user => {
      const userTasks = tasks.filter(task => task.assigneeId === user.id);
      const completedTasks = userTasks.filter(task => task.status === 'completed');
      
      return {
        ...user,
        totalTasks: userTasks.length,
        completedTasks: completedTasks.length,
        completionRate: userTasks.length > 0 
          ? (completedTasks.length / userTasks.length) * 100 
          : 0
      };
    });
  }, [activeUsers, tasks]); // Note: activeUsers is already memoized

  // Memoize expensive chart data
  const chartData = useMemo(() => {
    return generateChartData(userTaskSummary, projectStats);
  }, [userTaskSummary, projectStats]);

  return (
    <div>
      <UserSummary users={userTaskSummary} />
      <ProjectChart data={chartData} />
    </div>
  );
}

function generateChartData(userSummary, projectStats) {
  // Expensive chart data generation
  console.log('Generating chart data...');
  
  return {
    userPerformance: userSummary.map(user => ({
      name: user.name,
      efficiency: calculateEfficiency(user),
      workload: calculateWorkload(user)
    })),
    projectDistribution: Object.entries(projectStats).map(([status, count]) => ({
      status,
      count,
      percentage: (count / Object.values(projectStats).reduce((a, b) => a + b, 0)) * 100
    }))
  };
}
```

### Memoization with Custom Comparisons

```javascript
// Custom hook for deep memoization
function useDeepMemo(factory, deps) {
  const ref = useRef();
  
  if (!ref.current || !deepEqual(deps, ref.current.deps)) {
    ref.current = {
      deps,
      value: factory()
    };
  }
  
  return ref.current.value;
}

function deepEqual(a, b) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    return a.every((item, index) => deepEqual(item, b[index]));
  }
  
  if (typeof a === 'object' && typeof b === 'object') {
    const keysA = Object.keys(a);
    const keysB = Object.keys(b);
    
    if (keysA.length !== keysB.length) return false;
    return keysA.every(key => deepEqual(a[key], b[key]));
  }
  
  return false;
}

// Usage with complex objects
function DeepMemoComponent({ complexConfig }) {
  // Regular useMemo would re-calculate even for shallow changes
  const processedConfig = useDeepMemo(() => {
    console.log('Processing complex config...');
    return processComplexConfiguration(complexConfig);
  }, [complexConfig]);

  return <ConfigDisplay config={processedConfig} />;
}
```

---

## useCallback Hook

`useCallback` returns a memoized version of the callback that only changes if one of the dependencies has changed.

### Basic Usage

```javascript
function ParentComponent({ items }) {
  const [filter, setFilter] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');

  // ❌ BAD: New function on every render
  const handleItemClick = (item) => {
    console.log('Item clicked:', item);
    // Handle item click logic
  };

  // ✅ GOOD: Stable function reference
  const handleItemClickCallback = useCallback((item) => {
    console.log('Item clicked:', item);
    // Handle item click logic
  }, []); // No dependencies - function never changes

  // ✅ GOOD: Function that depends on state
  const handleSort = useCallback((newSortOrder) => {
    setSortOrder(newSortOrder);
    analytics.track('sort_changed', { sortOrder: newSortOrder });
  }, []); // Empty deps because we only use setState

  // ✅ GOOD: Function that uses current state/props
  const handleFilter = useCallback((newFilter) => {
    setFilter(newFilter);
    console.log(`Filtering by: ${newFilter}, current sort: ${sortOrder}`);
  }, [sortOrder]); // Depends on sortOrder

  const filteredItems = useMemo(() => {
    return items
      .filter(item => item.name.toLowerCase().includes(filter.toLowerCase()))
      .sort((a, b) => {
        const modifier = sortOrder === 'asc' ? 1 : -1;
        return a.name.localeCompare(b.name) * modifier;
      });
  }, [items, filter, sortOrder]);

  return (
    <div>
      <FilterControl onFilter={handleFilter} />
      <SortControl onSort={handleSort} />
      <ItemList 
        items={filteredItems} 
        onItemClick={handleItemClickCallback} 
      />
    </div>
  );
}

// Memoized child components
const FilterControl = React.memo(({ onFilter }) => {
  console.log('FilterControl rendered');
  
  return (
    <input
      type="text"
      placeholder="Filter items..."
      onChange={(e) => onFilter(e.target.value)}
    />
  );
});

const SortControl = React.memo(({ onSort }) => {
  console.log('SortControl rendered');
  
  return (
    <div>
      <button onClick={() => onSort('asc')}>Sort A-Z</button>
      <button onClick={() => onSort('desc')}>Sort Z-A</button>
    </div>
  );
});

const ItemList = React.memo(({ items, onItemClick }) => {
  console.log('ItemList rendered');
  
  return (
    <ul>
      {items.map(item => (
        <ItemComponent
          key={item.id}
          item={item}
          onClick={onItemClick}
        />
      ))}
    </ul>
  );
});

const ItemComponent = React.memo(({ item, onClick }) => {
  console.log(`Item ${item.id} rendered`);
  
  return (
    <li onClick={() => onClick(item)}>
      {item.name}
    </li>
  );
});
```

### Advanced useCallback Patterns

```javascript
function AdvancedCallbackComponent({ userId, onUserUpdate }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  // Callback that depends on external prop
  const handleUserSave = useCallback(async (userData) => {
    setLoading(true);
    try {
      const updatedUser = await saveUser(userId, userData);
      setUser(updatedUser);
      onUserUpdate?.(updatedUser); // Optional callback
    } catch (error) {
      console.error('Failed to save user:', error);
    } finally {
      setLoading(false);
    }
  }, [userId, onUserUpdate]);

  // Callback with state setter pattern
  const updateUserField = useCallback((field, value) => {
    setUser(prevUser => ({
      ...prevUser,
      [field]: value
    }));
  }, []); // No dependencies needed with functional updates

  // Debounced callback
  const debouncedSave = useCallback(
    debounce(handleUserSave, 500),
    [handleUserSave]
  );

  // Callback factory pattern
  const createFieldUpdater = useCallback((field) => {
    return (value) => updateUserField(field, value);
  }, [updateUserField]);

  return (
    <UserForm
      user={user}
      loading={loading}
      onSave={handleUserSave}
      onFieldChange={updateUserField}
      createFieldUpdater={createFieldUpdater}
    />
  );
}

// Helper function for debouncing
function debounce(func, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}
```

### useCallback vs useMemo Comparison

```javascript
function CallbackVsMemoExample() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState([]);

  // useCallback - memoizes the function
  const handleIncrement = useCallback(() => {
    setCount(prev => prev + 1);
  }, []); // Function never changes

  // useMemo - memoizes the result of the function
  const expensiveValue = useMemo(() => {
    console.log('Calculating expensive value...');
    return items.reduce((sum, item) => sum + item.value, 0) * count;
  }, [items, count]); // Recalculates when items or count change

  // These are equivalent:
  const memoizedCallback = useCallback(() => {
    doSomething();
  }, [dep]);

  const memoizedCallbackAlt = useMemo(() => {
    return () => {
      doSomething();
    };
  }, [dep]);

  return (
    <div>
      <p>Count: {count}</p>
      <p>Expensive Value: {expensiveValue}</p>
      <button onClick={handleIncrement}>Increment</button>
    </div>
  );
}
```

---

## React.memo and Component Optimization

React.memo is a higher-order component that memoizes the result of a component and only re-renders if props have changed.

### Basic React.memo

```javascript
// ❌ BAD: Component re-renders even when props haven't changed
function ExpensiveComponent({ name, age, hobbies }) {
  console.log(`Rendering ${name}`); // Logs on every parent render
  
  return (
    <div>
      <h2>{name}</h2>
      <p>Age: {age}</p>
      <ul>
        {hobbies.map((hobby, index) => (
          <li key={index}>{hobby}</li>
        ))}
      </ul>
    </div>
  );
}

// ✅ GOOD: Component only re-renders when props change
const OptimizedComponent = React.memo(function OptimizedComponent({ name, age, hobbies }) {
  console.log(`Rendering ${name}`); // Only logs when props actually change
  
  return (
    <div>
      <h2>{name}</h2>
      <p>Age: {age}</p>
      <ul>
        {hobbies.map((hobby, index) => (
          <li key={index}>{hobby}</li>
        ))}
      </ul>
    </div>
  );
});

function ParentComponent() {
  const [count, setCount] = useState(0);
  
  // These props don't change when count changes
  const userProps = {
    name: 'John Doe',
    age: 30,
    hobbies: ['reading', 'gaming'] // ⚠️ This creates a new array on every render
  };

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
      <ExpensiveComponent {...userProps} />
      <OptimizedComponent {...userProps} />
    </div>
  );
}
```

### React.memo with Custom Comparison

```javascript
// Custom comparison function for complex props
const ComplexComponent = React.memo(
  function ComplexComponent({ user, settings, onAction }) {
    console.log('ComplexComponent rendered');
    
    return (
      <div>
        <h3>{user.name}</h3>
        <p>Theme: {settings.theme}</p>
        <button onClick={() => onAction(user.id)}>
          Action
        </button>
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Custom comparison logic
    // Return true if props are equal (skip re-render)
    // Return false if props are different (re-render)
    
    const userEqual = 
      prevProps.user.id === nextProps.user.id &&
      prevProps.user.name === nextProps.user.name;
    
    const settingsEqual = 
      prevProps.settings.theme === nextProps.settings.theme;
    
    const actionEqual = prevProps.onAction === nextProps.onAction;
    
    return userEqual && settingsEqual && actionEqual;
  }
);

// Optimized parent component
function OptimizedParent() {
  const [count, setCount] = useState(0);
  const [user] = useState({ id: 1, name: 'John' }); // Stable reference
  const [settings] = useState({ theme: 'dark' }); // Stable reference

  // Stable callback
  const handleAction = useCallback((userId) => {
    console.log(`Action for user ${userId}`);
  }, []);

  return (
    <div>
      <button onClick={() => setCount(count + 1)}>
        Count: {count}
      </button>
      <ComplexComponent
        user={user}
        settings={settings}
        onAction={handleAction}
      />
    </div>
  );
}
```

### Memo Patterns and Best Practices

```javascript
// Pattern 1: Memoizing expensive list items
const ListItem = React.memo(({ item, onEdit, onDelete, isSelected }) => {
  console.log(`Rendering item ${item.id}`);
  
  return (
    <div className={`item ${isSelected ? 'selected' : ''}`}>
      <h4>{item.title}</h4>
      <p>{item.description}</p>
      <button onClick={() => onEdit(item.id)}>Edit</button>
      <button onClick={() => onDelete(item.id)}>Delete</button>
    </div>
  );
});

function ItemList({ items, selectedId, onEdit, onDelete }) {
  // Memoize callbacks to prevent unnecessary re-renders
  const handleEdit = useCallback((id) => {
    onEdit(id);
  }, [onEdit]);

  const handleDelete = useCallback((id) => {
    onDelete(id);
  }, [onDelete]);

  return (
    <div>
      {items.map(item => (
        <ListItem
          key={item.id}
          item={item}
          isSelected={item.id === selectedId}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}

// Pattern 2: Memoizing form components
const FormField = React.memo(({ 
  label, 
  value, 
  onChange, 
  error, 
  ...inputProps 
}) => {
  console.log(`Rendering field: ${label}`);
  
  return (
    <div className="form-field">
      <label>{label}</label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        {...inputProps}
      />
      {error && <span className="error">{error}</span>}
    </div>
  );
});

function UserForm({ user, errors, onChange }) {
  // Create stable field change handlers
  const createFieldHandler = useCallback((field) => {
    return (value) => onChange(field, value);
  }, [onChange]);

  // Memoize field handlers
  const handleNameChange = useMemo(() => createFieldHandler('name'), [createFieldHandler]);
  const handleEmailChange = useMemo(() => createFieldHandler('email'), [createFieldHandler]);
  const handleAgeChange = useMemo(() => createFieldHandler('age'), [createFieldHandler]);

  return (
    <form>
      <FormField
        label="Name"
        value={user.name}
        onChange={handleNameChange}
        error={errors.name}
      />
      <FormField
        label="Email"
        type="email"
        value={user.email}
        onChange={handleEmailChange}
        error={errors.email}
      />
      <FormField
        label="Age"
        type="number"
        value={user.age}
        onChange={handleAgeChange}
        error={errors.age}
      />
    </form>
  );
}
```

---

## useRef for Performance

useRef can be used for performance optimizations by storing values that don't need to trigger re-renders.

### Preventing Unnecessary Effects

```javascript
function ComponentWithExpensiveEffect({ userId, settings }) {
  const [data, setData] = useState(null);
  const previousUserIdRef = useRef();
  const previousSettingsRef = useRef();

  useEffect(() => {
    // Only fetch if userId actually changed
    if (previousUserIdRef.current !== userId) {
      fetchUserData(userId).then(setData);
      previousUserIdRef.current = userId;
    }
  }, [userId]);

  useEffect(() => {
    // Only apply settings if they actually changed
    if (!shallowEqual(previousSettingsRef.current, settings)) {
      applySettings(settings);
      previousSettingsRef.current = settings;
    }
  }, [settings]);

  return <div>{/* Component JSX */}</div>;
}

// Custom hook for previous value
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

// Usage with custom hook
function OptimizedComponent({ userId, settings }) {
  const [data, setData] = useState(null);
  const previousUserId = usePrevious(userId);
  const previousSettings = usePrevious(settings);

  useEffect(() => {
    if (userId !== previousUserId) {
      fetchUserData(userId).then(setData);
    }
  }, [userId, previousUserId]);

  useEffect(() => {
    if (!shallowEqual(settings, previousSettings)) {
      applySettings(settings);
    }
  }, [settings, previousSettings]);

  return <div>{/* Component JSX */}</div>;
}
```

### Storing Callback References

```javascript
function ComponentWithStableCallbacks({ onUpdate }) {
  const [count, setCount] = useState(0);
  const onUpdateRef = useRef(onUpdate);

  // Always keep the ref current
  useEffect(() => {
    onUpdateRef.current = onUpdate;
  });

  // Stable callback that always calls the latest onUpdate
  const stableCallback = useCallback((value) => {
    onUpdateRef.current?.(value);
  }, []); // No dependencies!

  return (
    <ExpensiveChild
      count={count}
      onUpdate={stableCallback} // This never changes
    />
  );
}

// Pattern: Event listener with stable reference
function ComponentWithEventListener() {
  const [state, setState] = useState(null);
  const stateRef = useRef(state);

  // Keep ref in sync
  useEffect(() => {
    stateRef.current = state;
  });

  useEffect(() => {
    const handleEvent = (event) => {
      // Access latest state without re-creating listener
      console.log('Current state:', stateRef.current);
      console.log('Event:', event);
    };

    window.addEventListener('resize', handleEvent);
    return () => window.removeEventListener('resize', handleEvent);
  }, []); // Empty dependencies - listener is never recreated

  return <div>{/* Component JSX */}</div>;
}
```

---

## Advanced Performance Patterns

### Composition vs Configuration

```javascript
// ❌ BAD: Configuration-based (re-renders everything)
function ConfigurableComponent({ 
  showHeader, 
  showFooter, 
  headerProps, 
  footerProps, 
  children 
}) {
  return (
    <div>
      {showHeader && <Header {...headerProps} />}
      <main>{children}</main>
      {showFooter && <Footer {...footerProps} />}
    </div>
  );
}

// ✅ GOOD: Composition-based (better performance)
function ComposableComponent({ children }) {
  return (
    <div>
      {children}
    </div>
  );
}

// Usage
function App() {
  const [data, setData] = useState([]);

  return (
    <ComposableComponent>
      <Header title="My App" />
      <MainContent data={data} />
      <Footer year={2024} />
    </ComposableComponent>
  );
}
```

### State Colocation

```javascript
// ❌ BAD: State at top level causes unnecessary re-renders
function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState([]);

  return (
    <div>
      <UserProfile user={user} />
      <PostList posts={posts} />
      <CommentSection comments={comments} />
      <LikeButton likes={likes} />
    </div>
  );
}

// ✅ GOOD: State colocated with components that need it
function App() {
  return (
    <div>
      <UserProfileContainer />
      <PostListContainer />
      <CommentSectionContainer />
      <LikeButtonContainer />
    </div>
  );
}

function UserProfileContainer() {
  const [user, setUser] = useState(null);
  // User-related logic here
  return <UserProfile user={user} />;
}

function PostListContainer() {
  const [posts, setPosts] = useState([]);
  // Post-related logic here
  return <PostList posts={posts} />;
}
```

### Lazy Initialization

```javascript
function ExpensiveComponent({ config }) {
  // ❌ BAD: Expensive computation on every render
  const [state, setState] = useState(computeExpensiveInitialState(config));

  // ✅ GOOD: Lazy initialization
  const [state, setState] = useState(() => {
    console.log('Computing initial state...');
    return computeExpensiveInitialState(config);
  });

  // ✅ GOOD: Lazy initialization with useRef for one-time setup
  const expensiveInstance = useRef();
  if (!expensiveInstance.current) {
    expensiveInstance.current = new ExpensiveClass(config);
  }

  return <div>{/* Component JSX */}</div>;
}

// Custom hook for lazy initialization
function useLazyState(initializer) {
  const [state, setState] = useState(initializer);
  return [state, setState];
}

// Custom hook for lazy ref
function useLazyRef(initializer) {
  const ref = useRef();
  if (ref.current === undefined) {
    ref.current = initializer();
  }
  return ref;
}
```

---

## Performance Measurement Hooks

### Timing Hook

```javascript
function usePerformanceTimer(name) {
  const startTimeRef = useRef();
  const endTimeRef = useRef();

  const start = useCallback(() => {
    startTimeRef.current = performance.now();
    console.log(`🚀 Starting timer: ${name}`);
  }, [name]);

  const end = useCallback(() => {
    endTimeRef.current = performance.now();
    const duration = endTimeRef.current - startTimeRef.current;
    console.log(`⏱️ ${name} took ${duration.toFixed(2)}ms`);
    return duration;
  }, [name]);

  const measure = useCallback((fn) => {
    start();
    const result = fn();
    if (result instanceof Promise) {
      return result.finally(end);
    } else {
      end();
      return result;
    }
  }, [start, end]);

  return { start, end, measure };
}

// Usage
function DataProcessingComponent({ data }) {
  const { measure } = usePerformanceTimer('Data Processing');

  const processedData = useMemo(() => {
    return measure(() => {
      return expensiveDataProcessing(data);
    });
  }, [data, measure]);

  return <DataDisplay data={processedData} />;
}
```

### Render Count Hook

```javascript
function useRenderCount(componentName) {
  const renderCount = useRef(0);
  
  useEffect(() => {
    renderCount.current += 1;
    console.log(`🔄 ${componentName} rendered ${renderCount.current} times`);
  });

  return renderCount.current;
}

// Re-render tracking hook
function useWhyDidYouUpdate(name, props) {
  const previousProps = useRef();

  useEffect(() => {
    if (previousProps.current) {
      const allKeys = Object.keys({ ...previousProps.current, ...props });
      const changedProps = {};
      
      allKeys.forEach((key) => {
        if (previousProps.current[key] !== props[key]) {
          changedProps[key] = {
            from: previousProps.current[key],
            to: props[key]
          };
        }
      });

      if (Object.keys(changedProps).length) {
        console.log('[why-did-you-update]', name, changedProps);
      }
    }

    previousProps.current = props;
  });
}

// Usage
function DebuggableComponent(props) {
  const renderCount = useRenderCount('DebuggableComponent');
  useWhyDidYouUpdate('DebuggableComponent', props);

  return (
    <div>
      <p>Rendered {renderCount} times</p>
      {/* Component content */}
    </div>
  );
}
```

### Memory Usage Hook

```javascript
function useMemoryMonitor(interval = 5000) {
  const [memoryInfo, setMemoryInfo] = useState(null);

  useEffect(() => {
    if (!performance.memory) {
      console.warn('Memory API not available');
      return;
    }

    const updateMemoryInfo = () => {
      const memory = performance.memory;
      setMemoryInfo({
        usedJSHeapSize: Math.round(memory.usedJSHeapSize / 1048576), // MB
        totalJSHeapSize: Math.round(memory.totalJSHeapSize / 1048576), // MB
        jsHeapSizeLimit: Math.round(memory.jsHeapSizeLimit / 1048576), // MB
        timestamp: Date.now()
      });
    };

    updateMemoryInfo();
    const intervalId = setInterval(updateMemoryInfo, interval);

    return () => clearInterval(intervalId);
  }, [interval]);

  return memoryInfo;
}

// Usage
function MemoryMonitorDisplay() {
  const memoryInfo = useMemoryMonitor(2000);

  if (!memoryInfo) {
    return <div>Memory monitoring not available</div>;
  }

  return (
    <div style={{ 
      position: 'fixed', 
      top: 10, 
      right: 10, 
      background: 'rgba(0,0,0,0.8)', 
      color: 'white', 
      padding: '10px',
      fontSize: '12px'
    }}>
      <div>Used: {memoryInfo.usedJSHeapSize} MB</div>
      <div>Total: {memoryInfo.totalJSHeapSize} MB</div>
      <div>Limit: {memoryInfo.jsHeapSizeLimit} MB</div>
    </div>
  );
}
```

---

## Virtual Lists and Windowing

### Basic Virtual List Hook

```javascript
function useVirtualList({
  items,
  itemHeight,
  containerHeight,
  overscan = 5
}) {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.max(
    0,
    Math.floor(scrollTop / itemHeight) - overscan
  );

  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      ...item,
      index: startIndex + index
    }));
  }, [items, startIndex, endIndex]);

  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    startIndex,
    endIndex
  };
}

// Advanced virtual list with variable heights
function useVariableVirtualList({
  items,
  estimatedItemHeight,
  containerHeight,
  overscan = 5,
  getItemHeight
}) {
  const [scrollTop, setScrollTop] = useState(0);
  const [itemHeights, setItemHeights] = useState(new Map());
  const itemOffsets = useRef(new Map());

  // Calculate item offsets
  useMemo(() => {
    let offset = 0;
    itemOffsets.current.clear();
    
    items.forEach((item, index) => {
      itemOffsets.current.set(index, offset);
      const height = itemHeights.get(index) || estimatedItemHeight;
      offset += height;
    });
  }, [items, itemHeights, estimatedItemHeight]);

  // Find visible range
  const { startIndex, endIndex } = useMemo(() => {
    let start = 0;
    let end = items.length - 1;

    // Binary search for start index
    let low = 0, high = items.length - 1;
    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      const offset = itemOffsets.current.get(mid) || 0;
      
      if (offset < scrollTop) {
        low = mid + 1;
      } else {
        high = mid - 1;
        start = mid;
      }
    }

    // Find end index
    let currentOffset = itemOffsets.current.get(start) || 0;
    end = start;
    
    while (end < items.length && currentOffset < scrollTop + containerHeight) {
      const height = itemHeights.get(end) || estimatedItemHeight;
      currentOffset += height;
      end++;
    }

    return {
      startIndex: Math.max(0, start - overscan),
      endIndex: Math.min(items.length - 1, end + overscan)
    };
  }, [scrollTop, items.length, containerHeight, itemHeights, estimatedItemHeight, overscan]);

  const visibleItems = useMemo(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      ...item,
      index: startIndex + index
    }));
  }, [items, startIndex, endIndex]);

  const measureItem = useCallback((index, height) => {
    setItemHeights(prev => new Map(prev).set(index, height));
  }, []);

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  const totalHeight = Array.from(itemOffsets.current.values()).pop() || 0;
  const offsetY = itemOffsets.current.get(startIndex) || 0;

  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    measureItem,
    startIndex,
    endIndex
  };
}
```

### Virtual List Component

```javascript
const VirtualList = React.memo(({ 
  items, 
  itemHeight = 50, 
  height = 400, 
  renderItem,
  overscan = 5 
}) => {
  const {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  } = useVirtualList({
    items,
    itemHeight,
    containerHeight: height,
    overscan
  });

  return (
    <div
      style={{
        height,
        overflow: 'auto',
        border: '1px solid #ddd'
      }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map((item) => (
            <div
              key={item.id || item.index}
              style={{ height: itemHeight }}
            >
              {renderItem(item, item.index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

// Usage
function LargeListExample() {
  const items = useMemo(() => 
    Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      value: Math.random() * 100
    })),
    []
  );

  const renderItem = useCallback((item, index) => (
    <div style={{ 
      padding: '10px', 
      borderBottom: '1px solid #eee',
      background: index % 2 === 0 ? '#f9f9f9' : 'white'
    }}>
      <strong>{item.name}</strong>
      <span style={{ float: 'right' }}>
        {item.value.toFixed(2)}
      </span>
    </div>
  ), []);

  return (
    <div>
      <h2>Virtual List (10,000 items)</h2>
      <VirtualList
        items={items}
        itemHeight={60}
        height={400}
        renderItem={renderItem}
      />
    </div>
  );
}
```

---

## Lazy Loading and Code Splitting

### Component Lazy Loading

```javascript
// Lazy load components
const LazyDashboard = React.lazy(() => import('./Dashboard'));
const LazyProfile = React.lazy(() => import('./Profile'));
const LazySettings = React.lazy(() => import('./Settings'));

// Enhanced lazy loading with retry
function lazyWithRetry(componentImport, name) {
  return React.lazy(() =>
    componentImport().catch(error => {
      console.error(`Failed to load ${name}:`, error);
      
      // Retry logic
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(componentImport());
        }, 1000);
      });
    })
  );
}

const RetryableDashboard = lazyWithRetry(
  () => import('./Dashboard'),
  'Dashboard'
);

// Loading boundary component
function LoadingBoundary({ children, fallback = <div>Loading...</div> }) {
  return (
    <React.Suspense fallback={fallback}>
      {children}
    </React.Suspense>
  );
}

// Router with lazy loading
function App() {
  return (
    <Router>
      <div>
        <nav>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/profile">Profile</Link>
          <Link to="/settings">Settings</Link>
        </nav>
        
        <LoadingBoundary fallback={<PageLoader />}>
          <Routes>
            <Route path="/dashboard" element={<LazyDashboard />} />
            <Route path="/profile" element={<LazyProfile />} />
            <Route path="/settings" element={<LazySettings />} />
          </Routes>
        </LoadingBoundary>
      </div>
    </Router>
  );
}
```

### Lazy Data Loading

```javascript
function useLazyData(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { lazy = true, ...fetchOptions } = options;

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(url, fetchOptions);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [url, JSON.stringify(fetchOptions)]);

  useEffect(() => {
    if (!lazy) {
      fetchData();
    }
  }, [fetchData, lazy]);

  return {
    data,
    loading,
    error,
    fetch: fetchData
  };
}

// Intersection Observer for lazy loading
function useIntersectionObserver(options = {}) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const ref = useRef();

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
    }, options);

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [options]);

  return [ref, isIntersecting];
}

// Lazy loaded component
function LazyDataComponent({ url }) {
  const [ref, isVisible] = useIntersectionObserver({
    threshold: 0.1,
    rootMargin: '50px'
  });

  const { data, loading, error, fetch } = useLazyData(url, { 
    lazy: true 
  });

  useEffect(() => {
    if (isVisible && !data && !loading) {
      fetch();
    }
  }, [isVisible, data, loading, fetch]);

  return (
    <div ref={ref} style={{ minHeight: '200px' }}>
      {loading && <div>Loading data...</div>}
      {error && <div>Error: {error}</div>}
      {data && <DataDisplay data={data} />}
      {!isVisible && <div>Scroll to load data...</div>}
    </div>
  );
}
```

---

## Memory Management

### Cleanup Hook

```javascript
function useCleanup() {
  const cleanupFunctions = useRef([]);

  const addCleanup = useCallback((cleanupFn) => {
    cleanupFunctions.current.push(cleanupFn);
  }, []);

  const runCleanup = useCallback(() => {
    cleanupFunctions.current.forEach(fn => {
      try {
        fn();
      } catch (error) {
        console.error('Cleanup error:', error);
      }
    });
    cleanupFunctions.current = [];
  }, []);

  useEffect(() => {
    return runCleanup;
  }, [runCleanup]);

  return { addCleanup, runCleanup };
}

// Usage
function ComponentWithCleanup() {
  const { addCleanup } = useCleanup();

  useEffect(() => {
    const timer = setInterval(() => {
      console.log('Timer tick');
    }, 1000);

    const socket = new WebSocket('ws://localhost:8080');
    
    const eventHandler = () => {
      console.log('Window resize');
    };
    window.addEventListener('resize', eventHandler);

    // Register cleanup functions
    addCleanup(() => clearInterval(timer));
    addCleanup(() => socket.close());
    addCleanup(() => window.removeEventListener('resize', eventHandler));
  }, [addCleanup]);

  return <div>Component with automatic cleanup</div>;
}
```

### Memory Leak Detection

```javascript
function useMemoryLeakDetection(componentName) {
  const mountTime = useRef(Date.now());
  const isUnmounted = useRef(false);

  useEffect(() => {
    return () => {
      isUnmounted.current = true;
      console.log(`${componentName} unmounted after ${Date.now() - mountTime.current}ms`);
    };
  }, [componentName]);

  const checkIfUnmounted = useCallback((context = '') => {
    if (isUnmounted.current) {
      console.error(
        `Potential memory leak: ${componentName} - ${context} called after unmount`
      );
      return true;
    }
    return false;
  }, [componentName]);

  return { checkIfUnmounted };
}

// Safe async operation hook
function useSafeAsync() {
  const { checkIfUnmounted } = useMemoryLeakDetection('useSafeAsync');

  const safeSetState = useCallback((setState, newState, context = '') => {
    if (!checkIfUnmounted(context)) {
      setState(newState);
    }
  }, [checkIfUnmounted]);

  const safeAsyncOperation = useCallback(async (asyncFn, onSuccess, onError) => {
    try {
      const result = await asyncFn();
      
      if (!checkIfUnmounted('async success')) {
        onSuccess?.(result);
      }
    } catch (error) {
      if (!checkIfUnmounted('async error')) {
        onError?.(error);
      }
    }
  }, [checkIfUnmounted]);

  return { safeSetState, safeAsyncOperation };
}
```

---

## Performance Anti-patterns

### Common Mistakes to Avoid

```javascript
// ❌ ANTI-PATTERN 1: Creating objects in render
function BadComponent({ items }) {
  return (
    <List
      items={items}
      style={{ margin: 10 }} // New object every render!
      config={{ sortable: true }} // New object every render!
    />
  );
}

// ✅ SOLUTION: Move objects outside or memoize
const listStyle = { margin: 10 };
const listConfig = { sortable: true };

function GoodComponent({ items }) {
  return (
    <List
      items={items}
      style={listStyle}
      config={listConfig}
    />
  );
}

// ❌ ANTI-PATTERN 2: Inline functions in props
function BadParent({ items }) {
  return (
    <div>
      {items.map(item => (
        <Item
          key={item.id}
          item={item}
          onClick={() => handleClick(item.id)} // New function every render!
        />
      ))}
    </div>
  );
}

// ✅ SOLUTION: Use stable callbacks
function GoodParent({ items }) {
  const handleClick = useCallback((id) => {
    // Handle click logic
  }, []);

  return (
    <div>
      {items.map(item => (
        <Item
          key={item.id}
          item={item}
          onClick={handleClick}
          itemId={item.id} // Pass ID as separate prop
        />
      ))}
    </div>
  );
}

// ❌ ANTI-PATTERN 3: Unnecessary dependencies in hooks
function BadHook({ userId }) {
  const [user, setUser] = useState(null);

  const fetchUser = useCallback(async () => {
    const userData = await api.getUser(userId);
    setUser(userData);
  }, [userId, setUser]); // setUser is unnecessary dependency

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return user;
}

// ✅ SOLUTION: Remove unnecessary dependencies
function GoodHook({ userId }) {
  const [user, setUser] = useState(null);

  const fetchUser = useCallback(async () => {
    const userData = await api.getUser(userId);
    setUser(userData);
  }, [userId]); // Only userId is needed

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return user;
}

// ❌ ANTI-PATTERN 4: Overusing useMemo/useCallback
function OverOptimizedComponent({ count }) {
  // Unnecessary memoization for simple values
  const doubledCount = useMemo(() => count * 2, [count]);
  const message = useMemo(() => `Count is ${count}`, [count]);
  
  // Unnecessary callback for simple functions
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  return (
    <div onClick={handleClick}>
      {message}: {doubledCount}
    </div>
  );
}

// ✅ SOLUTION: Only optimize when necessary
function ReasonablyOptimizedComponent({ count }) {
  // These are fine without memoization
  const doubledCount = count * 2;
  const message = `Count is ${count}`;
  
  const handleClick = () => {
    console.log('clicked');
  };

  return (
    <div onClick={handleClick}>
      {message}: {doubledCount}
    </div>
  );
}
```

---

## Profiling and Debugging

### React DevTools Profiler Hook

```javascript
function useProfiler(id, onRender) {
  const { Profiler } = React;
  
  const ProfilerWrapper = useCallback(({ children }) => (
    <Profiler id={id} onRender={onRender}>
      {children}
    </Profiler>
  ), [id, onRender]);

  return ProfilerWrapper;
}

// Performance monitoring hook
function usePerformanceMonitor(componentName) {
  const renderCount = useRef(0);
  const renderTimes = useRef([]);

  const onRender = useCallback((id, phase, actualDuration) => {
    renderCount.current += 1;
    renderTimes.current.push({
      phase,
      duration: actualDuration,
      timestamp: Date.now()
    });

    // Log slow renders
    if (actualDuration > 16) { // More than one frame at 60fps
      console.warn(
        `Slow render detected in ${componentName}:`,
        `${actualDuration.toFixed(2)}ms (${phase})`
      );
    }

    // Keep only last 100 renders
    if (renderTimes.current.length > 100) {
      renderTimes.current = renderTimes.current.slice(-100);
    }
  }, [componentName]);

  const ProfilerWrapper = useProfiler(componentName, onRender);

  const getStats = useCallback(() => {
    const times = renderTimes.current.map(r => r.duration);
    const avg = times.reduce((sum, time) => sum + time, 0) / times.length;
    const max = Math.max(...times);
    const min = Math.min(...times);

    return {
      renderCount: renderCount.current,
      averageRenderTime: avg,
      maxRenderTime: max,
      minRenderTime: min,
      recentRenders: renderTimes.current.slice(-10)
    };
  }, []);

  return { ProfilerWrapper, getStats };
}

// Usage
function MonitoredComponent({ data }) {
  const { ProfilerWrapper, getStats } = usePerformanceMonitor('DataTable');

  useEffect(() => {
    // Log stats periodically
    const interval = setInterval(() => {
      console.log('Performance stats:', getStats());
    }, 5000);

    return () => clearInterval(interval);
  }, [getStats]);

  return (
    <ProfilerWrapper>
      <DataTable data={data} />
    </ProfilerWrapper>
  );
}
```

### Bundle Size Analysis Hook

```javascript
function useBundleAnalysis() {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      // Analyze which components are loaded
      const loadedComponents = new Set();
      
      const originalCreateElement = React.createElement;
      React.createElement = function(type, props, ...children) {
        if (typeof type === 'function' && type.name) {
          loadedComponents.add(type.name);
        }
        return originalCreateElement.call(this, type, props, ...children);
      };

      // Log loaded components after a delay
      setTimeout(() => {
        console.log('Loaded components:', Array.from(loadedComponents));
      }, 5000);
    }
  }, []);
}
```

---

## Summary

Performance hooks are essential tools for building fast React applications:

### Key Performance Hooks

1. **useMemo** - Cache expensive calculations
2. **useCallback** - Stabilize function references  
3. **React.memo** - Prevent unnecessary re-renders
4. **useRef** - Store values without triggering renders

### Best Practices

- **Profile first** - Don't optimize prematurely
- **Measure impact** - Use React DevTools Profiler
- **Target bottlenecks** - Focus on actual performance issues
- **Consider alternatives** - Sometimes architectural changes work better
- **Monitor memory** - Clean up resources properly

### When to Optimize

- **Large lists** - Use virtualization
- **Expensive calculations** - Use useMemo
- **Frequent re-renders** - Use React.memo and useCallback
- **Complex state** - Consider state management libraries
- **Heavy components** - Use lazy loading

Performance optimization is about making informed decisions based on actual measurements, not gut feelings. Always profile your application to identify real bottlenecks before applying optimizations.
