# Module 5: Advanced Hooks Patterns

## 🎯 Learning Objectives
By the end of this module, you will:
- Master advanced custom hooks patterns and composition
- Understand compound component patterns with hooks
- Implement render props pattern using hooks
- Build reusable hook libraries
- Apply the Container/Presenter pattern with hooks
- Create hooks for complex state machines
- Implement advanced data fetching patterns
- Master hooks for performance optimization
- Build accessible components using hooks

## 📚 Module Overview

### What You'll Learn
This module dives deep into advanced React hooks patterns that are essential for building scalable, maintainable, and reusable React applications. You'll learn how to combine multiple hooks to create powerful abstractions and design patterns.

### Prerequisites
- Solid understanding of all basic React hooks (Module 3)
- Experience with state management patterns (Module 4)
- Understanding of JavaScript closures and higher-order functions
- Familiarity with TypeScript (recommended)

## 🏗️ Core Concepts

### 1. Advanced Custom Hooks Patterns

#### Hook Composition
```jsx
// Combining multiple hooks for complex functionality
function useAuthenticatedApi(url) {
  const { user, isAuthenticated } = useAuth();
  const { data, loading, error, refetch } = useApi(url, {
    enabled: isAuthenticated,
    headers: { Authorization: `Bearer ${user?.token}` }
  });
  
  return { data, loading, error, refetch, isAuthenticated };
}

// Usage
function UserProfile() {
  const { data: profile, loading, error } = useAuthenticatedApi('/api/profile');
  
  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return <ProfileCard profile={profile} />;
}
```

#### Generic Hooks
```jsx
// Generic hook for any list operations
function useList<T>(initialItems: T[] = []) {
  const [items, setItems] = useState<T[]>(initialItems);
  
  const addItem = useCallback((item: T) => {
    setItems(prev => [...prev, item]);
  }, []);
  
  const removeItem = useCallback((index: number) => {
    setItems(prev => prev.filter((_, i) => i !== index));
  }, []);
  
  const updateItem = useCallback((index: number, newItem: T) => {
    setItems(prev => prev.map((item, i) => i === index ? newItem : item));
  }, []);
  
  const clearItems = useCallback(() => {
    setItems([]);
  }, []);
  
  return {
    items,
    addItem,
    removeItem,
    updateItem,
    clearItems,
    count: items.length,
    isEmpty: items.length === 0
  };
}
```

### 2. Compound Component Pattern with Hooks

#### Context-Based Compound Components
```jsx
// Create context for compound component
const TabsContext = createContext();

function Tabs({ children, defaultValue }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  
  const value = {
    activeTab,
    setActiveTab
  };
  
  return (
    <TabsContext.Provider value={value}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children }) {
  return <div className="tab-list">{children}</div>;
}

function Tab({ value, children }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  const isActive = activeTab === value;
  
  return (
    <button
      className={`tab ${isActive ? 'active' : ''}`}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
}

function TabPanels({ children }) {
  return <div className="tab-panels">{children}</div>;
}

function TabPanel({ value, children }) {
  const { activeTab } = useContext(TabsContext);
  
  if (activeTab !== value) return null;
  
  return <div className="tab-panel">{children}</div>;
}

// Compound component API
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panels = TabPanels;
Tabs.Panel = TabPanel;
```

### 3. State Machine Patterns with Hooks

#### Finite State Machine Hook
```jsx
function useStateMachine(initialState, transitions) {
  const [state, setState] = useState(initialState);
  const [context, setContext] = useState({});
  
  const send = useCallback((event, payload = {}) => {
    const currentTransitions = transitions[state];
    const transition = currentTransitions?.[event];
    
    if (transition) {
      if (typeof transition === 'string') {
        setState(transition);
      } else if (typeof transition === 'function') {
        const result = transition(context, payload);
        setState(result.nextState);
        setContext(prev => ({ ...prev, ...result.context }));
      }
    }
  }, [state, context, transitions]);
  
  return [state, send, context];
}

// Usage: Login state machine
const loginTransitions = {
  idle: {
    SUBMIT: 'loading'
  },
  loading: {
    SUCCESS: 'success',
    ERROR: 'error'
  },
  success: {
    RESET: 'idle'
  },
  error: {
    RETRY: 'loading',
    RESET: 'idle'
  }
};

function LoginForm() {
  const [state, send, context] = useStateMachine('idle', loginTransitions);
  
  const handleSubmit = async (credentials) => {
    send('SUBMIT');
    try {
      await login(credentials);
      send('SUCCESS');
    } catch (error) {
      send('ERROR', { error: error.message });
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {state === 'loading' && <Spinner />}
      {state === 'error' && <ErrorMessage message={context.error} />}
      {state === 'success' && <SuccessMessage />}
      <button disabled={state === 'loading'}>
        {state === 'loading' ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  );
}
```

### 4. Advanced Data Fetching Patterns

#### Infinite Query Hook
```jsx
function useInfiniteQuery(queryFn, options = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasNextPage, setHasNextPage] = useState(true);
  const [isFetchingNextPage, setIsFetchingNextPage] = useState(false);
  
  const fetchNextPage = useCallback(async () => {
    if (!hasNextPage || isFetchingNextPage) return;
    
    setIsFetchingNextPage(true);
    try {
      const result = await queryFn({
        pageParam: data.length,
        ...options
      });
      
      setData(prev => [...prev, ...result.data]);
      setHasNextPage(result.hasNextPage);
    } catch (err) {
      setError(err);
    } finally {
      setIsFetchingNextPage(false);
    }
  }, [data.length, hasNextPage, isFetchingNextPage, queryFn, options]);
  
  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await queryFn({ pageParam: 0, ...options });
      setData(result.data);
      setHasNextPage(result.hasNextPage);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [queryFn, options]);
  
  useEffect(() => {
    refetch();
  }, [refetch]);
  
  return {
    data,
    loading,
    error,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
    refetch
  };
}
```

### 5. Accessibility Hooks

#### Focus Management Hook
```jsx
function useFocusManagement() {
  const focusableElements = useRef([]);
  const currentFocusIndex = useRef(-1);
  
  const registerFocusable = useCallback((element) => {
    if (element && !focusableElements.current.includes(element)) {
      focusableElements.current.push(element);
    }
  }, []);
  
  const unregisterFocusable = useCallback((element) => {
    focusableElements.current = focusableElements.current.filter(
      el => el !== element
    );
  }, []);
  
  const focusFirst = useCallback(() => {
    if (focusableElements.current.length > 0) {
      focusableElements.current[0].focus();
      currentFocusIndex.current = 0;
    }
  }, []);
  
  const focusLast = useCallback(() => {
    const lastIndex = focusableElements.current.length - 1;
    if (lastIndex >= 0) {
      focusableElements.current[lastIndex].focus();
      currentFocusIndex.current = lastIndex;
    }
  }, []);
  
  const focusNext = useCallback(() => {
    const nextIndex = (currentFocusIndex.current + 1) % focusableElements.current.length;
    if (focusableElements.current[nextIndex]) {
      focusableElements.current[nextIndex].focus();
      currentFocusIndex.current = nextIndex;
    }
  }, []);
  
  const focusPrevious = useCallback(() => {
    const prevIndex = currentFocusIndex.current - 1 < 0 
      ? focusableElements.current.length - 1 
      : currentFocusIndex.current - 1;
    if (focusableElements.current[prevIndex]) {
      focusableElements.current[prevIndex].focus();
      currentFocusIndex.current = prevIndex;
    }
  }, []);
  
  return {
    registerFocusable,
    unregisterFocusable,
    focusFirst,
    focusLast,
    focusNext,
    focusPrevious
  };
}
```

## 🛠️ Practical Exercises

### Exercise 1: Build a Multi-Step Form Hook
Create a `useMultiStepForm` hook that manages form steps, validation, and data persistence.

### Exercise 2: Implement a Shopping Cart Hook
Build a comprehensive `useShoppingCart` hook with add, remove, update quantity, calculate totals, and persistence.

### Exercise 3: Create a Modal Management System
Design a hook-based modal system that can handle multiple modals, stacking, and focus management.

### Exercise 4: Build a Real-time Chat Hook
Implement `useChatRoom` that handles WebSocket connections, message history, and typing indicators.

## 🎯 Assessment Criteria

### Beginner Level (60-70%)
- [ ] Can create basic custom hooks combining 2-3 built-in hooks
- [ ] Understands hook composition principles
- [ ] Can implement simple compound components with context

### Intermediate Level (70-85%)
- [ ] Masters advanced custom hook patterns
- [ ] Can implement state machines with hooks
- [ ] Builds reusable hook libraries
- [ ] Implements complex data fetching patterns

### Advanced Level (85-100%)
- [ ] Creates sophisticated hook abstractions
- [ ] Implements accessibility patterns with hooks
- [ ] Builds production-ready hook libraries
- [ ] Optimizes hook performance and prevents unnecessary re-renders

## 📖 Additional Resources

### Documentation
- [React Hooks Reference](https://react.dev/reference/react)
- [Rules of Hooks](https://react.dev/warnings/invalid-hook-call-warning)

### Advanced Patterns
- [Compound Components Pattern](https://kentcdodds.com/blog/compound-components-with-react-hooks)
- [State Machines in React](https://xstate.js.org/docs/packages/xstate-react/)

### Libraries to Study
- [React Hook Form](https://react-hook-form.com/)
- [SWR](https://swr.vercel.app/)
- [React Query](https://tanstack.com/query/latest)
- [Zustand](https://github.com/pmndrs/zustand)

## 🔗 Next Steps
After completing this module, proceed to:
- Module 6: Performance Optimization
- Module 7: Routing (React Router)
- Advanced Projects: Build complex applications using these patterns

---

⚡ **Pro Tips:**
- Always consider performance implications when creating custom hooks
- Use TypeScript for better hook API design and type safety
- Test your custom hooks in isolation using React Testing Library
- Document your hook APIs thoroughly for team collaboration
- Consider accessibility from the start when designing hook patterns
