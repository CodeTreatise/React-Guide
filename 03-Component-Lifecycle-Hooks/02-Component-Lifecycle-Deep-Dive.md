# Component Lifecycle Deep Dive

## Table of Contents
1. [Introduction to Component Lifecycle](#introduction-to-component-lifecycle)
2. [Class Component Lifecycle Methods](#class-component-lifecycle-methods)
3. [Lifecycle Phases in Detail](#lifecycle-phases-in-detail)
4. [Deprecated Lifecycle Methods](#deprecated-lifecycle-methods)
5. [Error Boundaries and Error Handling](#error-boundaries-and-error-handling)
6. [Lifecycle Method Patterns](#lifecycle-method-patterns)
7. [Performance Considerations](#performance-considerations)
8. [Migration from Class to Hooks](#migration-from-class-to-hooks)
9. [Advanced Lifecycle Patterns](#advanced-lifecycle-patterns)
10. [Debugging Lifecycle Issues](#debugging-lifecycle-issues)

---

## Introduction to Component Lifecycle

Component lifecycle refers to the series of methods that are invoked in different stages of a component's existence. Understanding these phases is crucial for building efficient React applications, managing side effects, and optimizing performance.

### The Three Phases of Component Lifecycle

```javascript
// Conceptual representation of component lifecycle
class ComponentLifecycle extends React.Component {
  // 1. MOUNTING PHASE
  constructor(props) {
    super(props);
    // Component is being created
  }

  componentDidMount() {
    // Component has been mounted to DOM
  }

  // 2. UPDATING PHASE
  componentDidUpdate(prevProps, prevState) {
    // Component has been updated
  }

  // 3. UNMOUNTING PHASE
  componentWillUnmount() {
    // Component is about to be removed
  }

  render() {
    // Required method for all phases
    return <div>Component Content</div>;
  }
}
```

### Why Lifecycle Methods Matter

```javascript
// Example showing the importance of lifecycle methods
class DataFetcher extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: null,
      loading: true,
      error: null
    };
  }

  // Proper place for side effects
  async componentDidMount() {
    try {
      const response = await fetch(`/api/data/${this.props.id}`);
      const data = await response.json();
      this.setState({ data, loading: false });
    } catch (error) {
      this.setState({ error: error.message, loading: false });
    }
  }

  // Handle prop changes
  async componentDidUpdate(prevProps) {
    if (prevProps.id !== this.props.id) {
      this.setState({ loading: true, error: null });
      try {
        const response = await fetch(`/api/data/${this.props.id}`);
        const data = await response.json();
        this.setState({ data, loading: false });
      } catch (error) {
        this.setState({ error: error.message, loading: false });
      }
    }
  }

  // Cleanup
  componentWillUnmount() {
    // Cancel any ongoing requests, timers, subscriptions
    if (this.abortController) {
      this.abortController.abort();
    }
  }

  render() {
    const { data, loading, error } = this.state;
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!data) return <div>No data found</div>;
    
    return <div>{JSON.stringify(data)}</div>;
  }
}
```

---

## Class Component Lifecycle Methods

### Complete Lifecycle Method Reference

```javascript
class CompleteLifecycle extends React.Component {
  // 1. CONSTRUCTOR
  constructor(props) {
    super(props);
    console.log('1. Constructor');
    
    // Initialize state
    this.state = {
      count: 0,
      items: []
    };
    
    // Bind methods (if not using arrow functions)
    this.handleClick = this.handleClick.bind(this);
  }

  // 2. STATIC GET DERIVED STATE FROM PROPS
  static getDerivedStateFromProps(nextProps, prevState) {
    console.log('2. getDerivedStateFromProps');
    
    // Return object to update state, or null for no update
    if (nextProps.resetCount && prevState.count !== 0) {
      return {
        count: 0
      };
    }
    
    return null;
  }

  // 3. RENDER
  render() {
    console.log('3. Render');
    
    return (
      <div>
        <h2>Count: {this.state.count}</h2>
        <button onClick={this.handleClick}>Increment</button>
        <ChildComponent 
          count={this.state.count}
          items={this.state.items}
        />
      </div>
    );
  }

  // 4. COMPONENT DID MOUNT
  componentDidMount() {
    console.log('4. componentDidMount');
    
    // Perfect place for:
    // - API calls
    // - Setting up subscriptions
    // - Setting up timers
    // - Accessing DOM elements
    
    this.fetchInitialData();
    this.setupEventListeners();
    this.timer = setInterval(() => {
      console.log('Timer tick');
    }, 1000);
  }

  // 5. GET SNAPSHOT BEFORE UPDATE
  getSnapshotBeforeUpdate(prevProps, prevState) {
    console.log('5. getSnapshotBeforeUpdate');
    
    // Capture DOM state before update
    // Return value is passed to componentDidUpdate
    if (prevState.items.length < this.state.items.length) {
      const list = this.listRef.current;
      return list.scrollHeight - list.scrollTop;
    }
    
    return null;
  }

  // 6. COMPONENT DID UPDATE
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('6. componentDidUpdate');
    
    // Handle prop changes
    if (prevProps.userId !== this.props.userId) {
      this.fetchUserData(this.props.userId);
    }
    
    // Handle state changes
    if (prevState.count !== this.state.count) {
      this.logCountChange();
    }
    
    // Use snapshot value
    if (snapshot !== null) {
      const list = this.listRef.current;
      list.scrollTop = list.scrollHeight - snapshot;
    }
  }

  // 7. SHOULD COMPONENT UPDATE
  shouldComponentUpdate(nextProps, nextState) {
    console.log('7. shouldComponentUpdate');
    
    // Return false to prevent re-render
    // Use React.memo or PureComponent instead
    if (nextProps.userId === this.props.userId && 
        nextState.count === this.state.count) {
      return false;
    }
    
    return true;
  }

  // 8. COMPONENT WILL UNMOUNT
  componentWillUnmount() {
    console.log('8. componentWillUnmount');
    
    // Cleanup:
    // - Cancel API calls
    // - Remove event listeners
    // - Clear timers
    // - Cancel subscriptions
    
    clearInterval(this.timer);
    this.removeEventListeners();
    
    if (this.abortController) {
      this.abortController.abort();
    }
  }

  // Helper methods
  fetchInitialData = async () => {
    this.abortController = new AbortController();
    
    try {
      const response = await fetch('/api/initial-data', {
        signal: this.abortController.signal
      });
      const data = await response.json();
      this.setState({ items: data });
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Failed to fetch data:', error);
      }
    }
  }

  setupEventListeners = () => {
    window.addEventListener('resize', this.handleResize);
    document.addEventListener('keydown', this.handleKeyDown);
  }

  removeEventListeners = () => {
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('keydown', this.handleKeyDown);
  }

  handleClick = () => {
    this.setState(prevState => ({
      count: prevState.count + 1
    }));
  }

  handleResize = () => {
    // Handle window resize
  }

  handleKeyDown = (event) => {
    // Handle keyboard events
  }
}
```

---

## Lifecycle Phases in Detail

### 1. Mounting Phase

The mounting phase occurs when a component is being created and inserted into the DOM.

```javascript
class MountingExample extends React.Component {
  constructor(props) {
    super(props);
    
    // DO: Initialize state
    this.state = {
      user: null,
      preferences: this.loadPreferences()
    };
    
    // DO: Bind methods
    this.handleUserAction = this.handleUserAction.bind(this);
    
    // DON'T: Make API calls or side effects
    // DON'T: Access DOM elements
  }

  static getDerivedStateFromProps(props, state) {
    // DO: Return new state based on props
    if (props.defaultUser && !state.user) {
      return {
        user: props.defaultUser
      };
    }
    
    // DO: Return null if no state update needed
    return null;
  }

  render() {
    // DO: Return JSX
    // DO: Use state and props
    // DON'T: Modify state
    // DON'T: Make API calls
    
    const { user } = this.state;
    
    return (
      <div>
        {user ? (
          <UserProfile user={user} />
        ) : (
          <LoginForm onLogin={this.handleLogin} />
        )}
      </div>
    );
  }

  componentDidMount() {
    // DO: Make API calls
    // DO: Set up subscriptions
    // DO: Access DOM elements
    // DO: Start timers
    
    this.fetchUserData();
    this.setupAnalytics();
    
    // Focus first input
    if (this.firstInputRef.current) {
      this.firstInputRef.current.focus();
    }
  }

  fetchUserData = async () => {
    try {
      const response = await fetch('/api/user/profile');
      const user = await response.json();
      this.setState({ user });
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  }

  loadPreferences = () => {
    try {
      const stored = localStorage.getItem('userPreferences');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      return {};
    }
  }
}
```

### 2. Updating Phase

The updating phase occurs when a component's props or state change.

```javascript
class UpdatingExample extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: null,
      filter: '',
      sortBy: 'name'
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    // Reset filter when category changes
    if (nextProps.category !== prevState.lastCategory) {
      return {
        filter: '',
        lastCategory: nextProps.category
      };
    }
    
    return null;
  }

  shouldComponentUpdate(nextProps, nextState) {
    // Optimize rendering by comparing relevant values
    return (
      nextProps.category !== this.props.category ||
      nextProps.userId !== this.props.userId ||
      nextState.data !== this.state.data ||
      nextState.filter !== this.state.filter ||
      nextState.sortBy !== this.state.sortBy
    );
  }

  getSnapshotBeforeUpdate(prevProps, prevState) {
    // Capture scroll position before update
    if (prevState.data && this.state.data && 
        this.state.data.length > prevState.data.length) {
      
      const container = this.containerRef.current;
      return {
        scrollTop: container.scrollTop,
        scrollHeight: container.scrollHeight
      };
    }
    
    return null;
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    // Handle prop changes
    if (prevProps.category !== this.props.category) {
      this.fetchDataForCategory(this.props.category);
    }
    
    if (prevProps.userId !== this.props.userId) {
      this.fetchUserSpecificData(this.props.userId);
    }

    // Handle state changes
    if (prevState.filter !== this.state.filter ||
        prevState.sortBy !== this.state.sortBy) {
      this.applyFiltersAndSort();
    }

    // Restore scroll position if new items were added
    if (snapshot) {
      const container = this.containerRef.current;
      const heightDiff = container.scrollHeight - snapshot.scrollHeight;
      container.scrollTop = snapshot.scrollTop + heightDiff;
    }

    // Auto-save preferences
    if (prevState.sortBy !== this.state.sortBy) {
      this.savePreferences();
    }
  }

  render() {
    const { data, filter, sortBy } = this.state;
    const filteredData = this.getFilteredData(data, filter, sortBy);

    return (
      <div ref={this.containerRef} className="data-container">
        <FilterControls
          filter={filter}
          sortBy={sortBy}
          onFilterChange={this.handleFilterChange}
          onSortChange={this.handleSortChange}
        />
        <DataList items={filteredData} />
      </div>
    );
  }

  fetchDataForCategory = async (category) => {
    this.setState({ loading: true });
    
    try {
      const response = await fetch(`/api/data/${category}`);
      const data = await response.json();
      this.setState({ data, loading: false });
    } catch (error) {
      this.setState({ error: error.message, loading: false });
    }
  }

  getFilteredData = (data, filter, sortBy) => {
    if (!data) return [];
    
    let filtered = data;
    
    if (filter) {
      filtered = data.filter(item => 
        item.name.toLowerCase().includes(filter.toLowerCase())
      );
    }
    
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'date':
          return new Date(a.createdAt) - new Date(b.createdAt);
        default:
          return 0;
      }
    });
  }
}
```

### 3. Unmounting Phase

The unmounting phase occurs when a component is being removed from the DOM.

```javascript
class UnmountingExample extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      timer: 0,
      isActive: true
    };
    
    // Store references for cleanup
    this.intervalId = null;
    this.timeoutId = null;
    this.abortController = null;
    this.eventListeners = [];
  }

  componentDidMount() {
    // Set up various subscriptions and listeners
    this.setupTimer();
    this.setupEventListeners();
    this.setupWebSocket();
    this.fetchData();
  }

  componentWillUnmount() {
    // CRITICAL: Clean up all subscriptions and listeners
    
    // 1. Clear timers
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }

    // 2. Abort ongoing requests
    if (this.abortController) {
      this.abortController.abort();
    }

    // 3. Remove event listeners
    this.eventListeners.forEach(({ element, event, handler }) => {
      element.removeEventListener(event, handler);
    });

    // 4. Close WebSocket connection
    if (this.websocket) {
      this.websocket.close();
    }

    // 5. Cancel animation frames
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }

    // 6. Clean up third-party libraries
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    // 7. Clear any cached data
    this.clearCache();
    
    console.log('Component cleaned up successfully');
  }

  setupTimer = () => {
    this.intervalId = setInterval(() => {
      this.setState(prevState => ({
        timer: prevState.timer + 1
      }));
    }, 1000);
  }

  setupEventListeners = () => {
    const handleResize = () => {
      this.handleWindowResize();
    };
    
    const handleScroll = () => {
      this.handleScroll();
    };

    const handleKeyDown = (event) => {
      this.handleKeyboard(event);
    };

    // Store references for cleanup
    this.eventListeners = [
      { element: window, event: 'resize', handler: handleResize },
      { element: window, event: 'scroll', handler: handleScroll },
      { element: document, event: 'keydown', handler: handleKeyDown }
    ];

    // Add listeners
    this.eventListeners.forEach(({ element, event, handler }) => {
      element.addEventListener(event, handler);
    });
  }

  setupWebSocket = () => {
    this.websocket = new WebSocket('ws://localhost:8080');
    
    this.websocket.onopen = () => {
      this.setState({ isConnected: true });
    };
    
    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleWebSocketMessage(data);
    };
    
    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.websocket.onclose = () => {
      this.setState({ isConnected: false });
    };
  }

  fetchData = async () => {
    this.abortController = new AbortController();
    
    try {
      const response = await fetch('/api/data', {
        signal: this.abortController.signal
      });
      const data = await response.json();
      this.setState({ data });
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Fetch error:', error);
      }
    }
  }

  render() {
    return (
      <div>
        <h2>Timer: {this.state.timer}</h2>
        <p>Component will clean up on unmount</p>
      </div>
    );
  }
}
```

---

## Deprecated Lifecycle Methods

### Understanding Deprecated Methods

React has deprecated several lifecycle methods due to issues with async rendering and concurrent features.

```javascript
// DEPRECATED - Do not use these methods
class DeprecatedMethods extends React.Component {
  // ❌ UNSAFE_componentWillMount (formerly componentWillMount)
  UNSAFE_componentWillMount() {
    // Problems:
    // - Called multiple times in async rendering
    // - No access to DOM
    // - Can cause memory leaks
    
    // Instead use: constructor or componentDidMount
  }

  // ❌ UNSAFE_componentWillReceiveProps (formerly componentWillReceiveProps)
  UNSAFE_componentWillReceiveProps(nextProps) {
    // Problems:
    // - Called even when props haven't changed
    // - Can cause infinite loops
    // - Difficult to understand
    
    // Instead use: getDerivedStateFromProps
  }

  // ❌ UNSAFE_componentWillUpdate (formerly componentWillUpdate)
  UNSAFE_componentWillUpdate(nextProps, nextState) {
    // Problems:
    // - Called multiple times in async rendering
    // - Can't call setState
    // - Timing issues
    
    // Instead use: getSnapshotBeforeUpdate
  }
}
```

### Migration Patterns

```javascript
// OLD: Using deprecated componentWillReceiveProps
class OldComponent extends React.Component {
  UNSAFE_componentWillReceiveProps(nextProps) {
    if (nextProps.userId !== this.props.userId) {
      this.setState({
        user: null,
        loading: true
      });
      this.fetchUser(nextProps.userId);
    }
  }
}

// NEW: Using getDerivedStateFromProps + componentDidUpdate
class NewComponent extends React.Component {
  static getDerivedStateFromProps(props, state) {
    // Reset user when userId changes
    if (props.userId !== state.prevUserId) {
      return {
        prevUserId: props.userId,
        user: null,
        loading: true
      };
    }
    return null;
  }

  componentDidUpdate(prevProps) {
    // Fetch new user data when userId changes
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser(this.props.userId);
    }
  }

  fetchUser = async (userId) => {
    try {
      const response = await fetch(`/api/users/${userId}`);
      const user = await response.json();
      this.setState({ user, loading: false });
    } catch (error) {
      this.setState({ loading: false });
    }
  }
}
```

```javascript
// OLD: Using componentWillMount for initialization
class OldInitialization extends React.Component {
  UNSAFE_componentWillMount() {
    this.setupTimer();
    this.fetchData(); // ❌ Can cause issues
  }
}

// NEW: Using constructor + componentDidMount
class NewInitialization extends React.Component {
  constructor(props) {
    super(props);
    // Initialize state and bindings
    this.state = { data: null };
  }

  componentDidMount() {
    // Side effects after mounting
    this.setupTimer();
    this.fetchData(); // ✅ Safe
  }
}
```

---

## Error Boundaries and Error Handling

### Creating Error Boundaries

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  // Catch errors during rendering
  static getDerivedStateFromError(error) {
    // Update state to show error UI
    return {
      hasError: true
    };
  }

  // Log error details
  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error);
    console.error('Error info:', errorInfo);
    
    // Log to error reporting service
    this.logErrorToService(error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });
  }

  logErrorToService = (error, errorInfo) => {
    // Example: Send to error tracking service
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        }
      });
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          
          {process.env.NODE_ENV === 'development' && (
            <details>
              <summary>Error Details</summary>
              <pre>{this.state.error && this.state.error.toString()}</pre>
              <pre>{this.state.errorInfo.componentStack}</pre>
            </details>
          )}
          
          <button onClick={this.handleReset}>
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Advanced Error Boundary Patterns

```javascript
class AdvancedErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorId: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      errorId: Date.now().toString()
    };
  }

  componentDidCatch(error, errorInfo) {
    const { onError, maxRetries = 3 } = this.props;
    
    // Custom error handling
    if (onError) {
      onError(error, errorInfo);
    }

    // Auto-retry for certain errors
    if (this.shouldRetry(error) && this.state.retryCount < maxRetries) {
      setTimeout(() => {
        this.setState(prevState => ({
          hasError: false,
          retryCount: prevState.retryCount + 1
        }));
      }, 1000 * this.state.retryCount); // Exponential backoff
    }

    this.setState({ error });
  }

  shouldRetry = (error) => {
    // Only retry network errors or certain types
    return error.name === 'NetworkError' || 
           error.message.includes('Loading chunk');
  }

  render() {
    if (this.state.hasError) {
      const { fallback: Fallback, children } = this.props;
      
      if (Fallback) {
        return (
          <Fallback 
            error={this.state.error}
            retry={() => this.setState({ hasError: false })}
            retryCount={this.state.retryCount}
          />
        );
      }

      return (
        <DefaultErrorFallback 
          error={this.state.error}
          retry={() => this.setState({ hasError: false })}
        />
      );
    }

    return children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary
      fallback={CustomErrorFallback}
      onError={(error, errorInfo) => {
        console.log('App error:', error);
      }}
      maxRetries={2}
    >
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}
```

---

## Lifecycle Method Patterns

### Data Fetching Patterns

```javascript
class DataFetchingPatterns extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: null,
      loading: false,
      error: null,
      lastFetchId: null
    };
    this.abortController = null;
  }

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(prevProps) {
    // Refetch when key props change
    if (prevProps.id !== this.props.id || 
        prevProps.filter !== this.props.filter) {
      this.fetchData();
    }
  }

  componentWillUnmount() {
    // Cancel ongoing requests
    if (this.abortController) {
      this.abortController.abort();
    }
  }

  fetchData = async () => {
    const { id, filter } = this.props;
    
    // Cancel previous request
    if (this.abortController) {
      this.abortController.abort();
    }

    // Create new abort controller
    this.abortController = new AbortController();
    const fetchId = Date.now();

    this.setState({ 
      loading: true, 
      error: null,
      lastFetchId: fetchId
    });

    try {
      const response = await fetch(`/api/data/${id}?filter=${filter}`, {
        signal: this.abortController.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Check if this is still the latest request
      if (this.state.lastFetchId === fetchId) {
        this.setState({ 
          data, 
          loading: false 
        });
      }
    } catch (error) {
      if (error.name !== 'AbortError' && this.state.lastFetchId === fetchId) {
        this.setState({ 
          error: error.message, 
          loading: false 
        });
      }
    }
  }

  render() {
    const { data, loading, error } = this.state;

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage error={error} onRetry={this.fetchData} />;
    if (!data) return <EmptyState />;

    return <DataDisplay data={data} />;
  }
}
```

### Subscription Patterns

```javascript
class SubscriptionPatterns extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      messages: [],
      isConnected: false
    };
    this.subscriptions = new Set();
  }

  componentDidMount() {
    this.setupSubscriptions();
  }

  componentDidUpdate(prevProps) {
    // Update subscriptions when userId changes
    if (prevProps.userId !== this.props.userId) {
      this.cleanupSubscriptions();
      this.setupSubscriptions();
    }
  }

  componentWillUnmount() {
    this.cleanupSubscriptions();
  }

  setupSubscriptions = () => {
    const { userId } = this.props;

    // WebSocket subscription
    const ws = new WebSocket(`ws://localhost:8080/user/${userId}`);
    
    ws.onopen = () => {
      this.setState({ isConnected: true });
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      this.setState({ isConnected: false });
    };

    this.subscriptions.add(() => ws.close());

    // EventSource subscription
    const eventSource = new EventSource(`/api/events/${userId}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };

    this.subscriptions.add(() => eventSource.close());

    // Custom event listener
    const handleCustomEvent = (event) => {
      this.handleCustomEvent(event.detail);
    };

    document.addEventListener('customEvent', handleCustomEvent);
    this.subscriptions.add(() => {
      document.removeEventListener('customEvent', handleCustomEvent);
    });

    // Interval subscription
    const intervalId = setInterval(() => {
      this.pollForUpdates();
    }, 30000);

    this.subscriptions.add(() => clearInterval(intervalId));
  }

  cleanupSubscriptions = () => {
    // Execute all cleanup functions
    this.subscriptions.forEach(cleanup => cleanup());
    this.subscriptions.clear();
  }

  handleMessage = (message) => {
    this.setState(prevState => ({
      messages: [...prevState.messages, message]
    }));
  }

  render() {
    const { messages, isConnected } = this.state;

    return (
      <div>
        <ConnectionStatus connected={isConnected} />
        <MessageList messages={messages} />
      </div>
    );
  }
}
```

---

## Performance Considerations

### Optimizing Lifecycle Methods

```javascript
class PerformanceOptimized extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      items: [],
      filter: '',
      sortBy: 'name'
    };
    
    // Memoize expensive calculations
    this.memoizedFilter = this.memoize(this.filterItems);
    this.memoizedSort = this.memoize(this.sortItems);
  }

  // Optimize shouldComponentUpdate
  shouldComponentUpdate(nextProps, nextState) {
    // Use shallow comparison for better performance
    return !this.shallowEqual(this.props, nextProps) ||
           !this.shallowEqual(this.state, nextState);
  }

  // Alternative: Use React.memo or PureComponent
  // class PerformanceOptimized extends React.PureComponent {

  componentDidUpdate(prevProps, prevState) {
    // Batch related updates
    const propsChanged = prevProps.category !== this.props.category ||
                        prevProps.userId !== this.props.userId;
    
    const stateChanged = prevState.filter !== this.state.filter ||
                        prevState.sortBy !== this.state.sortBy;

    if (propsChanged) {
      this.handlePropsChange();
    }

    if (stateChanged) {
      this.handleStateChange();
    }
  }

  handlePropsChange = () => {
    // Debounce expensive operations
    if (this.propsChangeTimeout) {
      clearTimeout(this.propsChangeTimeout);
    }

    this.propsChangeTimeout = setTimeout(() => {
      this.fetchNewData();
    }, 300);
  }

  handleStateChange = () => {
    // Use requestAnimationFrame for DOM updates
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }

    this.animationFrame = requestAnimationFrame(() => {
      this.updateUI();
    });
  }

  // Utility methods
  shallowEqual = (obj1, obj2) => {
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);

    if (keys1.length !== keys2.length) {
      return false;
    }

    for (let key of keys1) {
      if (obj1[key] !== obj2[key]) {
        return false;
      }
    }

    return true;
  }

  memoize = (fn) => {
    const cache = new Map();
    
    return (...args) => {
      const key = JSON.stringify(args);
      
      if (cache.has(key)) {
        return cache.get(key);
      }
      
      const result = fn(...args);
      cache.set(key, result);
      
      return result;
    };
  }

  filterItems = (items, filter) => {
    if (!filter) return items;
    
    return items.filter(item =>
      item.name.toLowerCase().includes(filter.toLowerCase())
    );
  }

  sortItems = (items, sortBy) => {
    return [...items].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'date':
          return new Date(a.date) - new Date(b.date);
        default:
          return 0;
      }
    });
  }

  render() {
    const { items, filter, sortBy } = this.state;
    
    // Use memoized functions
    const filteredItems = this.memoizedFilter(items, filter);
    const sortedItems = this.memoizedSort(filteredItems, sortBy);

    return (
      <VirtualizedList 
        items={sortedItems}
        renderItem={this.renderItem}
      />
    );
  }
}
```

---

## Migration from Class to Hooks

### Comprehensive Migration Guide

```javascript
// BEFORE: Class component with lifecycle methods
class ClassComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      count: 0,
      user: null,
      loading: true
    };
  }

  async componentDidMount() {
    this.timer = setInterval(() => {
      this.setState(prev => ({ count: prev.count + 1 }));
    }, 1000);

    try {
      const response = await fetch(`/api/users/${this.props.userId}`);
      const user = await response.json();
      this.setState({ user, loading: false });
    } catch (error) {
      this.setState({ loading: false });
    }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser();
    }
  }

  componentWillUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }

  fetchUser = async () => {
    this.setState({ loading: true });
    try {
      const response = await fetch(`/api/users/${this.props.userId}`);
      const user = await response.json();
      this.setState({ user, loading: false });
    } catch (error) {
      this.setState({ loading: false });
    }
  }

  render() {
    const { count, user, loading } = this.state;
    return (
      <div>
        <p>Count: {count}</p>
        {loading ? <p>Loading...</p> : <p>User: {user?.name}</p>}
      </div>
    );
  }
}

// AFTER: Functional component with hooks
function HooksComponent({ userId }) {
  const [count, setCount] = useState(0);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Timer effect (componentDidMount + componentWillUnmount)
  useEffect(() => {
    const timer = setInterval(() => {
      setCount(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []); // Empty dependency array = componentDidMount + componentWillUnmount

  // Fetch user effect (componentDidMount + componentDidUpdate)
  useEffect(() => {
    let isCancelled = false;

    const fetchUser = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        
        if (!isCancelled) {
          setUser(userData);
          setLoading(false);
        }
      } catch (error) {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    fetchUser();

    return () => {
      isCancelled = true;
    };
  }, [userId]); // Dependency array = triggers when userId changes

  return (
    <div>
      <p>Count: {count}</p>
      {loading ? <p>Loading...</p> : <p>User: {user?.name}</p>}
    </div>
  );
}
```

### Complex Migration Examples

```javascript
// BEFORE: Complex class component
class ComplexClass extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: null,
      filter: '',
      sortBy: 'name',
      page: 1,
      hasMore: true
    };
    this.abortController = null;
  }

  componentDidMount() {
    this.fetchData();
    this.setupEventListeners();
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevProps.category !== this.props.category) {
      this.resetAndFetch();
    }

    if (prevState.filter !== this.state.filter ||
        prevState.sortBy !== this.state.sortBy) {
      this.debouncedFetch();
    }

    if (prevState.page !== this.state.page) {
      this.fetchMoreData();
    }
  }

  componentWillUnmount() {
    if (this.abortController) {
      this.abortController.abort();
    }
    this.removeEventListeners();
    this.clearTimeouts();
  }

  // ... methods
}

// AFTER: Complex functional component with hooks
function ComplexHooks({ category }) {
  const [data, setData] = useState(null);
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const abortControllerRef = useRef(null);
  const timeoutsRef = useRef(new Set());

  // Custom hooks for reusability
  const debouncedFilter = useDebounce(filter, 300);
  const debouncedSortBy = useDebounce(sortBy, 300);

  // Reset when category changes
  useEffect(() => {
    setData(null);
    setPage(1);
    setHasMore(true);
  }, [category]);

  // Fetch initial data
  useEffect(() => {
    fetchData();
  }, [category]);

  // Fetch when filter/sort changes
  useEffect(() => {
    if (debouncedFilter || debouncedSortBy !== 'name') {
      resetAndFetch();
    }
  }, [debouncedFilter, debouncedSortBy, category]);

  // Fetch more data when page changes
  useEffect(() => {
    if (page > 1) {
      fetchMoreData();
    }
  }, [page]);

  // Setup/cleanup event listeners
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setFilter('');
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      timeoutsRef.current.forEach(clearTimeout);
    };
  }, []);

  const fetchData = async () => {
    // Implementation
  };

  const resetAndFetch = () => {
    setData(null);
    setPage(1);
    fetchData();
  };

  // ... other methods

  return (
    <div>
      {/* JSX */}
    </div>
  );
}

// Custom hooks for reusability
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

---

## Advanced Lifecycle Patterns

### Higher-Order Component Lifecycle

```javascript
// HOC that adds lifecycle logging
function withLifecycleLogging(WrappedComponent, componentName = 'Component') {
  return class extends React.Component {
    componentDidMount() {
      console.log(`${componentName} mounted`);
    }

    componentDidUpdate(prevProps, prevState) {
      console.log(`${componentName} updated`, {
        prevProps,
        nextProps: this.props,
        prevState,
        nextState: this.state
      });
    }

    componentWillUnmount() {
      console.log(`${componentName} will unmount`);
    }

    render() {
      return <WrappedComponent {...this.props} />;
    }
  };
}

// HOC that adds data fetching lifecycle
function withDataFetching(WrappedComponent, fetchConfig) {
  return class extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        data: null,
        loading: true,
        error: null
      };
    }

    async componentDidMount() {
      await this.fetchData();
    }

    async componentDidUpdate(prevProps) {
      const shouldRefetch = fetchConfig.refetchOn.some(prop => 
        prevProps[prop] !== this.props[prop]
      );

      if (shouldRefetch) {
        await this.fetchData();
      }
    }

    fetchData = async () => {
      this.setState({ loading: true, error: null });

      try {
        const url = typeof fetchConfig.url === 'function' 
          ? fetchConfig.url(this.props)
          : fetchConfig.url;

        const response = await fetch(url);
        const data = await response.json();

        this.setState({ data, loading: false });
      } catch (error) {
        this.setState({ error: error.message, loading: false });
      }
    }

    render() {
      return (
        <WrappedComponent
          {...this.props}
          {...this.state}
          refetch={this.fetchData}
        />
      );
    }
  };
}

// Usage
const UserProfile = withDataFetching(
  ({ data, loading, error, refetch }) => {
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
      <div>
        <h1>{data.name}</h1>
        <button onClick={refetch}>Refresh</button>
      </div>
    );
  },
  {
    url: (props) => `/api/users/${props.userId}`,
    refetchOn: ['userId']
  }
);
```

### Render Props with Lifecycle

```javascript
class DataProvider extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: null,
      loading: false,
      error: null
    };
  }

  componentDidMount() {
    if (this.props.fetchOnMount) {
      this.fetch();
    }
  }

  componentDidUpdate(prevProps) {
    if (this.props.url !== prevProps.url) {
      this.fetch();
    }
  }

  fetch = async () => {
    const { url, transform } = this.props;

    this.setState({ loading: true, error: null });

    try {
      const response = await fetch(url);
      const data = await response.json();

      if (transform) {
        data = transform(data);
      }

      this.setState({ data, loading: false });
    } catch (error) {
      this.setState({ error: error.message, loading: false });
    }
  }

  render() {
    return this.props.children({
      ...this.state,
      fetch: this.fetch
    });
  }
}

// Usage
function App() {
  return (
    <DataProvider
      url="/api/users"
      fetchOnMount
      transform={users => users.filter(u => u.active)}
    >
      {({ data, loading, error, fetch }) => (
        <div>
          {loading && <div>Loading...</div>}
          {error && <div>Error: {error}</div>}
          {data && (
            <div>
              <UserList users={data} />
              <button onClick={fetch}>Refresh</button>
            </div>
          )}
        </div>
      )}
    </DataProvider>
  );
}
```

---

## Debugging Lifecycle Issues

### Lifecycle Debugging Tools

```javascript
class LifecycleDebugger extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    this.logLifecycle('constructor');
  }

  static getDerivedStateFromProps(props, state) {
    console.log('getDerivedStateFromProps', { props, state });
    return null;
  }

  componentDidMount() {
    this.logLifecycle('componentDidMount');
  }

  shouldComponentUpdate(nextProps, nextState) {
    this.logLifecycle('shouldComponentUpdate', { nextProps, nextState });
    return true;
  }

  getSnapshotBeforeUpdate(prevProps, prevState) {
    this.logLifecycle('getSnapshotBeforeUpdate', { prevProps, prevState });
    return null;
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    this.logLifecycle('componentDidUpdate', { prevProps, prevState, snapshot });
  }

  componentWillUnmount() {
    this.logLifecycle('componentWillUnmount');
  }

  logLifecycle = (method, data = {}) => {
    console.group(`🔄 ${this.constructor.name}: ${method}`);
    console.log('Props:', this.props);
    console.log('State:', this.state);
    if (Object.keys(data).length > 0) {
      console.log('Data:', data);
    }
    console.log('Stack:', new Error().stack);
    console.groupEnd();
  }

  render() {
    this.logLifecycle('render');
    
    return (
      <div>
        <h2>Count: {this.state.count}</h2>
        <button onClick={() => this.setState(prev => ({ count: prev.count + 1 }))}>
          Increment
        </button>
      </div>
    );
  }
}
```

### Performance Profiling

```javascript
class PerformanceProfiler extends React.Component {
  constructor(props) {
    super(props);
    this.state = { data: [] };
    this.performanceMarks = new Map();
  }

  startPerformanceMark(name) {
    const markName = `${this.constructor.name}-${name}-start`;
    performance.mark(markName);
    this.performanceMarks.set(name, markName);
  }

  endPerformanceMark(name) {
    const startMark = this.performanceMarks.get(name);
    if (startMark) {
      const endMark = `${this.constructor.name}-${name}-end`;
      performance.mark(endMark);
      performance.measure(
        `${this.constructor.name}-${name}`,
        startMark,
        endMark
      );
      
      // Log timing
      const measures = performance.getEntriesByName(`${this.constructor.name}-${name}`);
      const duration = measures[measures.length - 1].duration;
      console.log(`⏱️ ${name} took ${duration.toFixed(2)}ms`);
    }
  }

  componentDidMount() {
    this.startPerformanceMark('initial-load');
    this.fetchData().then(() => {
      this.endPerformanceMark('initial-load');
    });
  }

  componentDidUpdate() {
    this.startPerformanceMark('update');
    // Defer to next tick to measure render time
    setTimeout(() => {
      this.endPerformanceMark('update');
    }, 0);
  }

  fetchData = async () => {
    this.startPerformanceMark('data-fetch');
    
    try {
      const response = await fetch('/api/data');
      const data = await response.json();
      this.setState({ data });
    } finally {
      this.endPerformanceMark('data-fetch');
    }
  }

  render() {
    return (
      <div>
        <h2>Performance Profiler Example</h2>
        <p>Check console for timing information</p>
        <pre>{JSON.stringify(this.state.data, null, 2)}</pre>
      </div>
    );
  }
}
```

### Common Lifecycle Issues and Solutions

```javascript
// Issue 1: Memory leaks from uncleared timers
class MemoryLeakExample extends React.Component {
  componentDidMount() {
    // ❌ WRONG: Timer not cleared
    setInterval(() => {
      console.log('Timer tick');
    }, 1000);
  }
}

// ✅ CORRECT: Clear timer on unmount
class MemoryLeakFixed extends React.Component {
  componentDidMount() {
    this.timer = setInterval(() => {
      console.log('Timer tick');
    }, 1000);
  }

  componentWillUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }
}

// Issue 2: setState after unmount
class SetStateAfterUnmount extends React.Component {
  componentDidMount() {
    // ❌ WRONG: No cleanup for async operations
    fetch('/api/data')
      .then(response => response.json())
      .then(data => {
        this.setState({ data }); // Might be called after unmount
      });
  }
}

// ✅ CORRECT: Track mount status
class SetStateAfterUnmountFixed extends React.Component {
  constructor(props) {
    super(props);
    this.isMounted = false;
  }

  componentDidMount() {
    this.isMounted = true;
    
    fetch('/api/data')
      .then(response => response.json())
      .then(data => {
        if (this.isMounted) {
          this.setState({ data });
        }
      });
  }

  componentWillUnmount() {
    this.isMounted = false;
  }
}

// Issue 3: Infinite update loops
class InfiniteUpdateLoop extends React.Component {
  componentDidUpdate() {
    // ❌ WRONG: Always calls setState
    this.setState({ timestamp: Date.now() });
  }
}

// ✅ CORRECT: Conditional updates
class InfiniteUpdateLoopFixed extends React.Component {
  componentDidUpdate(prevProps, prevState) {
    // Only update if specific conditions are met
    if (prevProps.userId !== this.props.userId) {
      this.fetchUserData();
    }
    
    if (prevState.data !== this.state.data && this.state.data) {
      this.processData();
    }
  }
}
```

---

## Summary

Component lifecycle methods provide powerful hooks into React's rendering process, allowing you to:

1. **Initialize components** properly with constructors and `componentDidMount`
2. **Handle updates** efficiently with `componentDidUpdate` and derived state
3. **Clean up resources** with `componentWillUnmount`
4. **Handle errors** gracefully with error boundaries
5. **Optimize performance** with `shouldComponentUpdate` and proper patterns

### Key Takeaways

- **Use lifecycle methods appropriately** for their intended purposes
- **Always clean up** subscriptions, timers, and event listeners
- **Avoid deprecated methods** and migrate to modern patterns
- **Consider hooks** for new components as they provide cleaner patterns
- **Debug lifecycle issues** systematically with proper tools and logging
- **Optimize performance** by understanding when and why methods are called

The lifecycle methods form the foundation of React's component model and understanding them deeply will make you a more effective React developer, even as you transition to using hooks in modern applications.
