# Week 10: Data Fetching & Real-time - Daily Challenges

## Overview
This week focuses on advanced data fetching patterns, real-time data management, offline-first strategies, and building robust data synchronization systems.

## Learning Goals
- Master React Query/TanStack Query advanced patterns
- Implement real-time data with WebSockets and SSE
- Build offline-first data strategies
- Create advanced caching and synchronization systems
- Optimize data fetching performance

---

## Day 1: Advanced React Query Patterns

### Challenge: Sophisticated Data Management System
Build a comprehensive data management system using React Query with advanced patterns.

```jsx
// Advanced React Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        if (error.status === 404) return false;
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
      refetchOnReconnect: 'always',
    },
    mutations: {
      onError: (error, variables, context) => {
        console.error('Mutation failed:', error);
        queryClient.setQueryData(['errors'], (old) => [...(old || []), error]);
      },
    },
  },
});

// Advanced query hooks with complex logic
const useAdvancedUserQuery = (userId, options = {}) => {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async ({ signal }) => {
      const response = await fetch(`/api/users/${userId}`, { signal });
      if (!response.ok) {
        throw new Error(`Failed to fetch user: ${response.status}`);
      }
      return response.json();
    },
    enabled: !!userId,
    select: (data) => {
      // Transform data on the client side
      return {
        ...data,
        fullName: `${data.firstName} ${data.lastName}`,
        isActive: data.status === 'active',
        permissions: data.roles?.flatMap(role => role.permissions) || [],
      };
    },
    placeholderData: (previousData) => previousData,
    ...options,
  });
};

// Optimistic updates with rollback
const useUpdateUserMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ userId, updates }) => {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      
      if (!response.ok) {
        throw new Error(`Update failed: ${response.status}`);
      }
      
      return response.json();
    },
    
    onMutate: async ({ userId, updates }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries(['user', userId]);
      
      // Snapshot the previous value
      const previousUser = queryClient.getQueryData(['user', userId]);
      
      // Optimistically update the cache
      queryClient.setQueryData(['user', userId], (old) => ({
        ...old,
        ...updates,
        updatedAt: new Date().toISOString(),
      }));
      
      // Return a context object with the snapshotted value
      return { previousUser, userId };
    },
    
    onError: (err, { userId }, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (context?.previousUser) {
        queryClient.setQueryData(['user', userId], context.previousUser);
      }
    },
    
    onSettled: (data, error, { userId }) => {
      // Always refetch after error or success to ensure server state
      queryClient.invalidateQueries(['user', userId]);
    },
  });
};

// Infinite query with complex pagination
const useInfinitePostsQuery = (filters = {}) => {
  return useInfiniteQuery({
    queryKey: ['posts', 'infinite', filters],
    queryFn: async ({ pageParam = 1, signal }) => {
      const params = new URLSearchParams({
        page: pageParam,
        limit: 20,
        ...filters,
      });
      
      const response = await fetch(`/api/posts?${params}`, { signal });
      const data = await response.json();
      
      return {
        posts: data.posts,
        nextPage: data.hasMore ? pageParam + 1 : undefined,
        totalCount: data.totalCount,
      };
    },
    getNextPageParam: (lastPage) => lastPage.nextPage,
    select: (data) => ({
      pages: data.pages,
      posts: data.pages.flatMap(page => page.posts),
      totalCount: data.pages[0]?.totalCount || 0,
    }),
    staleTime: 2 * 60 * 1000, // 2 minutes for posts
  });
};

// Dependent queries with error handling
const useUserDashboardData = (userId) => {
  const userQuery = useAdvancedUserQuery(userId);
  
  const postsQuery = useQuery({
    queryKey: ['posts', 'user', userId],
    queryFn: () => fetchUserPosts(userId),
    enabled: !!userQuery.data && userQuery.data.isActive,
  });
  
  const analyticsQuery = useQuery({
    queryKey: ['analytics', 'user', userId],
    queryFn: () => fetchUserAnalytics(userId),
    enabled: !!userQuery.data?.permissions?.includes('view_analytics'),
  });
  
  return {
    user: userQuery.data,
    posts: postsQuery.data,
    analytics: analyticsQuery.data,
    isLoading: userQuery.isLoading || postsQuery.isLoading || analyticsQuery.isLoading,
    error: userQuery.error || postsQuery.error || analyticsQuery.error,
    refetchAll: () => {
      userQuery.refetch();
      postsQuery.refetch();
      analyticsQuery.refetch();
    },
  };
};
```

**Your Task:**
1. **Complex Query Dependencies**: Build sophisticated dependent query chains
2. **Optimistic Updates**: Implement optimistic updates with proper rollback
3. **Advanced Caching**: Create intelligent caching strategies
4. **Error Recovery**: Build robust error handling and retry logic
5. **Performance Optimization**: Optimize query performance for large datasets

**Advanced Features:**
- Background sync with conflict resolution
- Query deduplication and batching
- Streaming data updates
- Query result transformation and normalization

---

## Day 2: Real-time Data with WebSockets

### Challenge: Real-time Collaboration System
Build a real-time collaboration system using WebSockets with React Query integration.

```jsx
// WebSocket integration with React Query
class WebSocketManager {
  constructor(url, options = {}) {
    this.url = url;
    this.options = options;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000;
    this.messageQueue = [];
    this.subscribers = new Map();
    this.isConnected = false;
  }
  
  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.flushMessageQueue();
        this.notifySubscribers('connection', { status: 'connected' });
      };
      
      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.notifySubscribers('connection', { status: 'disconnected' });
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifySubscribers('error', { error });
      };
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.attemptReconnect();
    }
  }
  
  send(message) {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }
  
  subscribe(event, callback) {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    this.subscribers.get(event).add(callback);
    
    return () => {
      this.subscribers.get(event)?.delete(callback);
    };
  }
  
  handleMessage(message) {
    const { type, payload } = message;
    
    switch (type) {
      case 'user_updated':
        this.invalidateUserQuery(payload.userId);
        break;
      case 'post_created':
        this.updatePostsCache(payload);
        break;
      case 'collaboration_update':
        this.handleCollaborationUpdate(payload);
        break;
      default:
        this.notifySubscribers(type, payload);
    }
  }
  
  invalidateUserQuery(userId) {
    const queryClient = getQueryClient();
    queryClient.invalidateQueries(['user', userId]);
  }
  
  updatePostsCache(newPost) {
    const queryClient = getQueryClient();
    
    // Update infinite queries
    queryClient.setQueryData(['posts', 'infinite'], (old) => {
      if (!old) return old;
      
      const newPages = [...old.pages];
      newPages[0] = {
        ...newPages[0],
        posts: [newPost, ...newPages[0].posts],
      };
      
      return { ...old, pages: newPages };
    });
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
        this.connect();
      }, this.reconnectInterval * Math.pow(2, this.reconnectAttempts));
    }
  }
}

// React hooks for WebSocket integration
const useWebSocket = (url, options = {}) => {
  const [wsManager] = useState(() => new WebSocketManager(url, options));
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  useEffect(() => {
    wsManager.connect();
    
    const unsubscribe = wsManager.subscribe('connection', ({ status }) => {
      setConnectionStatus(status);
    });
    
    return () => {
      unsubscribe();
      wsManager.disconnect();
    };
  }, [wsManager]);
  
  const sendMessage = useCallback((message) => {
    wsManager.send(message);
  }, [wsManager]);
  
  const subscribe = useCallback((event, callback) => {
    return wsManager.subscribe(event, callback);
  }, [wsManager]);
  
  return { sendMessage, subscribe, connectionStatus };
};

// Real-time document collaboration
const useRealtimeDocument = (documentId) => {
  const { sendMessage, subscribe } = useWebSocket('/ws/documents');
  const [collaborators, setCollaborators] = useState([]);
  const [cursors, setCursors] = useState({});
  
  const documentQuery = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => fetchDocument(documentId),
  });
  
  const updateDocumentMutation = useMutation({
    mutationFn: (changes) => updateDocument(documentId, changes),
    onMutate: async (changes) => {
      // Optimistic update
      const queryClient = useQueryClient();
      await queryClient.cancelQueries(['document', documentId]);
      
      const previousDocument = queryClient.getQueryData(['document', documentId]);
      
      queryClient.setQueryData(['document', documentId], (old) => ({
        ...old,
        content: applyChanges(old.content, changes),
        version: old.version + 1,
      }));
      
      // Send to other collaborators
      sendMessage({
        type: 'document_change',
        documentId,
        changes,
        userId: getCurrentUserId(),
      });
      
      return { previousDocument };
    },
  });
  
  useEffect(() => {
    const unsubscribeChanges = subscribe('document_change', (payload) => {
      if (payload.documentId === documentId && payload.userId !== getCurrentUserId()) {
        const queryClient = useQueryClient();
        queryClient.setQueryData(['document', documentId], (old) => ({
          ...old,
          content: applyChanges(old.content, payload.changes),
          version: old.version + 1,
        }));
      }
    });
    
    const unsubscribeCollaborators = subscribe('collaborators_update', (payload) => {
      if (payload.documentId === documentId) {
        setCollaborators(payload.collaborators);
      }
    });
    
    const unsubscribeCursors = subscribe('cursor_update', (payload) => {
      if (payload.documentId === documentId) {
        setCursors(prev => ({
          ...prev,
          [payload.userId]: payload.cursor,
        }));
      }
    });
    
    return () => {
      unsubscribeChanges();
      unsubscribeCollaborators();
      unsubscribeCursors();
    };
  }, [documentId, subscribe]);
  
  return {
    document: documentQuery.data,
    collaborators,
    cursors,
    updateDocument: updateDocumentMutation.mutate,
    isLoading: documentQuery.isLoading,
    error: documentQuery.error,
  };
};
```

**Your Task:**
1. **WebSocket Management**: Build robust WebSocket connection management
2. **Real-time Cache Updates**: Sync real-time data with React Query cache
3. **Conflict Resolution**: Handle concurrent updates and conflicts
4. **Connection Recovery**: Implement automatic reconnection with backoff
5. **Collaboration Features**: Build real-time collaboration tools

**Real-time Features:**
- Live document editing
- Real-time chat system
- Live notifications
- Collaborative drawing/whiteboard
- Real-time presence indicators

---

## Day 3: Server-Sent Events & Streaming

### Challenge: Real-time Data Streaming
Implement Server-Sent Events for real-time data streaming with React integration.

```jsx
// Server-Sent Events manager
class SSEManager {
  constructor(url, options = {}) {
    this.url = url;
    this.options = options;
    this.eventSource = null;
    this.subscribers = new Map();
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }
  
  connect() {
    try {
      this.eventSource = new EventSource(this.url, this.options);
      
      this.eventSource.onopen = () => {
        console.log('SSE connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifySubscribers('connection', { status: 'connected' });
      };
      
      this.eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };
      
      this.eventSource.onerror = () => {
        console.log('SSE connection error');
        this.isConnected = false;
        this.notifySubscribers('connection', { status: 'error' });
        this.attemptReconnect();
      };
      
      // Custom event listeners
      this.eventSource.addEventListener('user_update', (event) => {
        const data = JSON.parse(event.data);
        this.handleUserUpdate(data);
      });
      
      this.eventSource.addEventListener('notification', (event) => {
        const data = JSON.parse(event.data);
        this.handleNotification(data);
      });
      
    } catch (error) {
      console.error('Failed to connect SSE:', error);
      this.attemptReconnect();
    }
  }
  
  subscribe(event, callback) {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    this.subscribers.get(event).add(callback);
    
    return () => {
      this.subscribers.get(event)?.delete(callback);
    };
  }
  
  handleUserUpdate(data) {
    const queryClient = getQueryClient();
    
    // Update user cache
    queryClient.setQueryData(['user', data.userId], (old) => ({
      ...old,
      ...data.updates,
      lastUpdated: data.timestamp,
    }));
    
    // Invalidate related queries
    queryClient.invalidateQueries(['users', 'list']);
  }
  
  handleNotification(data) {
    const queryClient = getQueryClient();
    
    // Add to notifications cache
    queryClient.setQueryData(['notifications'], (old) => [
      data,
      ...(old || []).slice(0, 99), // Keep only latest 100
    ]);
    
    this.notifySubscribers('notification', data);
  }
  
  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.isConnected = false;
    }
  }
}

// React hooks for SSE
const useServerSentEvents = (url, options = {}) => {
  const [sseManager] = useState(() => new SSEManager(url, options));
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  useEffect(() => {
    sseManager.connect();
    
    const unsubscribe = sseManager.subscribe('connection', ({ status }) => {
      setConnectionStatus(status);
    });
    
    return () => {
      unsubscribe();
      sseManager.disconnect();
    };
  }, [sseManager]);
  
  const subscribe = useCallback((event, callback) => {
    return sseManager.subscribe(event, callback);
  }, [sseManager]);
  
  return { subscribe, connectionStatus };
};

// Real-time analytics dashboard
const useRealtimeAnalytics = () => {
  const { subscribe } = useServerSentEvents('/api/analytics/stream');
  const [metrics, setMetrics] = useState({
    activeUsers: 0,
    pageViews: 0,
    revenue: 0,
    conversionRate: 0,
  });
  
  const [realtimeEvents, setRealtimeEvents] = useState([]);
  
  useEffect(() => {
    const unsubscribeMetrics = subscribe('metrics_update', (data) => {
      setMetrics(prev => ({
        ...prev,
        ...data.metrics,
      }));
    });
    
    const unsubscribeEvents = subscribe('user_event', (event) => {
      setRealtimeEvents(prev => [
        event,
        ...prev.slice(0, 49), // Keep only latest 50 events
      ]);
      
      // Update relevant metrics
      if (event.type === 'page_view') {
        setMetrics(prev => ({
          ...prev,
          pageViews: prev.pageViews + 1,
        }));
      }
    });
    
    return () => {
      unsubscribeMetrics();
      unsubscribeEvents();
    };
  }, [subscribe]);
  
  return { metrics, realtimeEvents };
};

// Live data visualization
const LiveChart = ({ dataSource, chartType = 'line' }) => {
  const { subscribe } = useServerSentEvents(dataSource);
  const [chartData, setChartData] = useState([]);
  const maxDataPoints = 50;
  
  useEffect(() => {
    const unsubscribe = subscribe('data_point', (dataPoint) => {
      setChartData(prev => {
        const newData = [...prev, dataPoint];
        return newData.slice(-maxDataPoints); // Keep only latest points
      });
    });
    
    return unsubscribe;
  }, [subscribe]);
  
  const chartConfig = useMemo(() => ({
    type: chartType,
    data: {
      labels: chartData.map(point => point.timestamp),
      datasets: [{
        label: 'Live Data',
        data: chartData.map(point => point.value),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      }],
    },
    options: {
      responsive: true,
      animation: {
        duration: 0, // Disable animation for real-time updates
      },
      scales: {
        x: {
          type: 'time',
          time: {
            displayFormats: {
              minute: 'HH:mm',
            },
          },
        },
      },
    },
  }), [chartData, chartType]);
  
  return <Chart {...chartConfig} />;
};
```

**Your Task:**
1. **SSE Integration**: Build robust Server-Sent Events management
2. **Streaming Data**: Handle continuous data streams efficiently
3. **Real-time Charts**: Create live updating data visualizations
4. **Cache Synchronization**: Sync streaming data with query cache
5. **Performance**: Optimize for high-frequency updates

**Streaming Use Cases:**
- Real-time analytics dashboard
- Live stock price feeds
- Chat message streams
- Live sports scores
- System monitoring dashboards

---

## Day 4: Offline-First Data Strategy

### Challenge: Comprehensive Offline Support
Build a robust offline-first data management system.

```jsx
// Offline-first data manager
class OfflineDataManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.pendingMutations = [];
    this.syncQueue = [];
    this.conflictResolver = new ConflictResolver();
    
    this.initializeServiceWorker();
    this.setupEventListeners();
    this.loadPendingMutations();
  }
  
  initializeServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration);
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });
    }
  }
  
  setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.syncPendingMutations();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }
  
  // Queue mutations when offline
  queueMutation(mutation) {
    const queuedMutation = {
      id: generateId(),
      mutation,
      timestamp: Date.now(),
      retryCount: 0,
    };
    
    this.pendingMutations.push(queuedMutation);
    this.savePendingMutations();
    
    if (this.isOnline) {
      this.syncPendingMutations();
    }
    
    return queuedMutation.id;
  }
  
  // Sync mutations when back online
  async syncPendingMutations() {
    const mutations = [...this.pendingMutations];
    
    for (const queuedMutation of mutations) {
      try {
        await this.executeMutation(queuedMutation);
        this.removePendingMutation(queuedMutation.id);
      } catch (error) {
        await this.handleMutationError(queuedMutation, error);
      }
    }
  }
  
  async executeMutation(queuedMutation) {
    const { mutation } = queuedMutation;
    
    // Check for conflicts
    const conflict = await this.checkForConflicts(mutation);
    if (conflict) {
      const resolution = await this.conflictResolver.resolve(conflict);
      mutation.variables = { ...mutation.variables, ...resolution };
    }
    
    // Execute the mutation
    const result = await mutation.mutationFn(mutation.variables);
    
    // Update local cache
    if (mutation.onSuccess) {
      mutation.onSuccess(result, mutation.variables);
    }
    
    return result;
  }
  
  async handleMutationError(queuedMutation, error) {
    queuedMutation.retryCount++;
    
    if (queuedMutation.retryCount >= 3) {
      // Move to failed mutations
      this.failedMutations.push(queuedMutation);
      this.removePendingMutation(queuedMutation.id);
    } else {
      // Retry with exponential backoff
      setTimeout(() => {
        this.syncPendingMutations();
      }, Math.pow(2, queuedMutation.retryCount) * 1000);
    }
  }
  
  // Local storage management
  savePendingMutations() {
    localStorage.setItem('pendingMutations', JSON.stringify(this.pendingMutations));
  }
  
  loadPendingMutations() {
    const stored = localStorage.getItem('pendingMutations');
    if (stored) {
      this.pendingMutations = JSON.parse(stored);
    }
  }
}

// Offline-aware React Query integration
const useOfflineMutation = (mutationConfig) => {
  const offlineManager = useOfflineManager();
  const queryClient = useQueryClient();
  
  return useMutation({
    ...mutationConfig,
    mutationFn: async (variables) => {
      if (!navigator.onLine) {
        // Queue for later execution
        const queueId = offlineManager.queueMutation({
          mutationFn: mutationConfig.mutationFn,
          variables,
          onSuccess: mutationConfig.onSuccess,
        });
        
        // Return a pending result
        return { pending: true, queueId };
      }
      
      return mutationConfig.mutationFn(variables);
    },
    onMutate: async (variables) => {
      // Always run optimistic updates
      if (mutationConfig.onMutate) {
        return mutationConfig.onMutate(variables);
      }
    },
  });
};

// Offline-first query hook
const useOfflineQuery = (queryKey, queryFn, options = {}) => {
  const [cachedData, setCachedData] = useState();
  const [isStale, setIsStale] = useState(false);
  
  // Load from cache immediately
  useEffect(() => {
    const loadCachedData = async () => {
      const cached = await getCachedData(queryKey);
      if (cached) {
        setCachedData(cached.data);
        setIsStale(Date.now() - cached.timestamp > (options.staleTime || 300000));
      }
    };
    
    loadCachedData();
  }, [queryKey]);
  
  const query = useQuery({
    queryKey,
    queryFn: async (...args) => {
      const data = await queryFn(...args);
      
      // Cache the result
      await setCachedData(queryKey, {
        data,
        timestamp: Date.now(),
      });
      
      return data;
    },
    enabled: navigator.onLine || !cachedData,
    placeholderData: cachedData,
    ...options,
  });
  
  return {
    ...query,
    data: query.data || cachedData,
    isStale: !navigator.onLine || isStale,
    isOffline: !navigator.onLine,
  };
};

// Background sync with service worker
const useBackgroundSync = () => {
  const registerBackgroundSync = useCallback(async (tag, data) => {
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      const registration = await navigator.serviceWorker.ready;
      
      // Store data for background sync
      await storeBackgroundSyncData(tag, data);
      
      // Register for background sync
      await registration.sync.register(tag);
    }
  }, []);
  
  const cancelBackgroundSync = useCallback(async (tag) => {
    // Remove stored data
    await removeBackgroundSyncData(tag);
  }, []);
  
  return { registerBackgroundSync, cancelBackgroundSync };
};

// Conflict resolution system
class ConflictResolver {
  constructor() {
    this.strategies = new Map();
    this.setupDefaultStrategies();
  }
  
  setupDefaultStrategies() {
    // Last write wins
    this.strategies.set('last-write-wins', (local, remote) => ({
      ...remote,
      resolvedAt: Date.now(),
    }));
    
    // Merge non-conflicting fields
    this.strategies.set('merge', (local, remote) => {
      const merged = { ...local };
      
      Object.keys(remote).forEach(key => {
        if (local[key] !== remote[key]) {
          // Use server value for conflicts
          merged[key] = remote[key];
        }
      });
      
      return merged;
    });
    
    // User-defined resolution
    this.strategies.set('user-resolve', async (local, remote) => {
      return new Promise((resolve) => {
        // Show conflict resolution UI
        showConflictResolutionModal({
          local,
          remote,
          onResolve: resolve,
        });
      });
    });
  }
  
  async resolve(conflict) {
    const strategy = this.strategies.get(conflict.strategy || 'last-write-wins');
    return strategy(conflict.local, conflict.remote);
  }
}
```

**Your Task:**
1. **Offline Detection**: Build robust online/offline detection
2. **Data Synchronization**: Implement conflict-free data sync
3. **Queue Management**: Create mutation queue with retry logic
4. **Cache Management**: Build intelligent caching strategies
5. **Conflict Resolution**: Handle data conflicts elegantly

**Offline Features:**
- Background sync with service workers
- Optimistic UI updates
- Conflict-free replicated data types (CRDTs)
- Progressive data loading
- Smart cache invalidation

---

## Day 5: Data Synchronization & Conflict Resolution

### Challenge: Advanced Data Sync System
Build a sophisticated data synchronization system with conflict resolution.

```jsx
// Advanced synchronization manager
class DataSynchronizer {
  constructor() {
    this.syncStrategies = new Map();
    this.conflictResolvers = new Map();
    this.syncQueue = [];
    this.isProcessing = false;
    
    this.setupDefaultStrategies();
  }
  
  setupDefaultStrategies() {
    // Operational Transform for text editing
    this.syncStrategies.set('operational-transform', {
      apply: (document, operations) => {
        return operations.reduce((doc, op) => {
          return this.applyOperation(doc, op);
        }, document);
      },
      transform: (op1, op2) => {
        return this.transformOperations(op1, op2);
      },
    });
    
    // CRDT (Conflict-free Replicated Data Type) for sets
    this.syncStrategies.set('crdt-set', {
      merge: (set1, set2) => {
        const merged = new CRDTSet();
        merged.merge(set1);
        merged.merge(set2);
        return merged;
      },
    });
    
    // Vector clocks for causality
    this.syncStrategies.set('vector-clock', {
      compare: (clock1, clock2) => {
        return this.compareVectorClocks(clock1, clock2);
      },
      update: (clock, nodeId) => {
        return this.updateVectorClock(clock, nodeId);
      },
    });
  }
  
  // Operational Transform implementation
  applyOperation(document, operation) {
    switch (operation.type) {
      case 'insert':
        return document.slice(0, operation.position) + 
               operation.content + 
               document.slice(operation.position);
      case 'delete':
        return document.slice(0, operation.position) + 
               document.slice(operation.position + operation.length);
      case 'retain':
        return document;
      default:
        return document;
    }
  }
  
  transformOperations(op1, op2) {
    // Transform op1 against op2
    if (op1.type === 'insert' && op2.type === 'insert') {
      if (op1.position <= op2.position) {
        return [op1, { ...op2, position: op2.position + op1.content.length }];
      } else {
        return [{ ...op1, position: op1.position + op2.content.length }, op2];
      }
    }
    
    if (op1.type === 'delete' && op2.type === 'delete') {
      if (op1.position + op1.length <= op2.position) {
        return [op1, { ...op2, position: op2.position - op1.length }];
      } else if (op2.position + op2.length <= op1.position) {
        return [{ ...op1, position: op1.position - op2.length }, op2];
      } else {
        // Overlapping deletes - complex transformation
        return this.handleOverlappingDeletes(op1, op2);
      }
    }
    
    // More transformation rules...
    return [op1, op2];
  }
  
  // CRDT Set implementation
  class CRDTSet {
    constructor() {
      this.added = new Map(); // element -> timestamp
      this.removed = new Map(); // element -> timestamp
    }
    
    add(element, timestamp = Date.now()) {
      this.added.set(element, timestamp);
    }
    
    remove(element, timestamp = Date.now()) {
      this.removed.set(element, timestamp);
    }
    
    has(element) {
      const addedTime = this.added.get(element) || 0;
      const removedTime = this.removed.get(element) || 0;
      return addedTime > removedTime;
    }
    
    merge(otherSet) {
      // Merge added elements
      for (const [element, timestamp] of otherSet.added) {
        const currentTimestamp = this.added.get(element) || 0;
        if (timestamp > currentTimestamp) {
          this.added.set(element, timestamp);
        }
      }
      
      // Merge removed elements
      for (const [element, timestamp] of otherSet.removed) {
        const currentTimestamp = this.removed.get(element) || 0;
        if (timestamp > currentTimestamp) {
          this.removed.set(element, timestamp);
        }
      }
    }
    
    toArray() {
      return Array.from(this.added.keys()).filter(element => this.has(element));
    }
  }
  
  // Real-time collaborative editing hook
  const useCollaborativeEditor = (documentId) => {
    const [document, setDocument] = useState('');
    const [operations, setOperations] = useState([]);
    const [localCursor, setLocalCursor] = useState(0);
    const [remoteCursors, setRemoteCursors] = useState({});
    
    const { sendMessage, subscribe } = useWebSocket('/ws/documents');
    const synchronizer = useMemo(() => new DataSynchronizer(), []);
    
    const applyLocalOperation = useCallback((operation) => {
      // Apply operation locally
      const newDocument = synchronizer.applyOperation(document, operation);
      setDocument(newDocument);
      
      // Send to server
      sendMessage({
        type: 'operation',
        documentId,
        operation,
        userId: getCurrentUserId(),
      });
      
      // Update local operations list
      setOperations(prev => [...prev, operation]);
    }, [document, documentId, sendMessage, synchronizer]);
    
    const handleRemoteOperation = useCallback((operation) => {
      // Transform against local operations
      const transformedOp = operations.reduce((op, localOp) => {
        return synchronizer.transformOperations(op, localOp)[0];
      }, operation);
      
      // Apply transformed operation
      const newDocument = synchronizer.applyOperation(document, transformedOp);
      setDocument(newDocument);
      
      // Update cursor positions
      setLocalCursor(prev => 
        synchronizer.transformCursor(prev, transformedOp)
      );
    }, [document, operations, synchronizer]);
    
    useEffect(() => {
      const unsubscribe = subscribe('operation', (payload) => {
        if (payload.documentId === documentId && 
            payload.userId !== getCurrentUserId()) {
          handleRemoteOperation(payload.operation);
        }
      });
      
      const unsubscribeCursors = subscribe('cursor_update', (payload) => {
        if (payload.documentId === documentId) {
          setRemoteCursors(prev => ({
            ...prev,
            [payload.userId]: payload.cursor,
          }));
        }
      });
      
      return () => {
        unsubscribe();
        unsubscribeCursors();
      };
    }, [documentId, subscribe, handleRemoteOperation]);
    
    return {
      document,
      applyLocalOperation,
      localCursor,
      remoteCursors,
    };
  };
}

// Three-way merge for complex conflicts
const useThreeWayMerge = () => {
  const performMerge = useCallback((base, local, remote) => {
    const merge = {
      conflicts: [],
      resolved: {},
      automatic: {},
    };
    
    // Find all changed fields
    const allKeys = new Set([
      ...Object.keys(base || {}),
      ...Object.keys(local || {}),
      ...Object.keys(remote || {}),
    ]);
    
    allKeys.forEach(key => {
      const baseValue = base?.[key];
      const localValue = local?.[key];
      const remoteValue = remote?.[key];
      
      if (localValue === remoteValue) {
        // No conflict
        merge.automatic[key] = localValue;
      } else if (localValue === baseValue) {
        // Only remote changed
        merge.automatic[key] = remoteValue;
      } else if (remoteValue === baseValue) {
        // Only local changed
        merge.automatic[key] = localValue;
      } else {
        // Conflict - both changed
        merge.conflicts.push({
          key,
          base: baseValue,
          local: localValue,
          remote: remoteValue,
        });
      }
    });
    
    return merge;
  }, []);
  
  return { performMerge };
};
```

**Your Task:**
1. **Operational Transform**: Implement OT for collaborative editing
2. **CRDT Implementation**: Build conflict-free replicated data types
3. **Vector Clocks**: Implement causality tracking
4. **Three-way Merge**: Handle complex merge scenarios
5. **Real-time Collaboration**: Build collaborative editing features

**Synchronization Challenges:**
- Concurrent text editing
- Collaborative document editing
- Real-time form collaboration
- Distributed state management
- Conflict-free data structures

---

## Day 6: Performance & Caching Optimization

### Challenge: Advanced Caching & Performance
Build a high-performance caching system with intelligent cache management.

```jsx
// Advanced cache manager
class AdvancedCacheManager {
  constructor() {
    this.cache = new Map();
    this.metadata = new Map();
    this.subscribers = new Map();
    this.policies = new Map();
    
    this.setupDefaultPolicies();
    this.startCleanupInterval();
  }
  
  setupDefaultPolicies() {
    // LRU (Least Recently Used) policy
    this.policies.set('lru', {
      shouldEvict: (metadata, maxSize) => {
        if (this.cache.size <= maxSize) return [];
        
        const entries = Array.from(this.metadata.entries())
          .sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);
        
        return entries.slice(0, this.cache.size - maxSize).map(([key]) => key);
      },
    });
    
    // TTL (Time To Live) policy
    this.policies.set('ttl', {
      shouldEvict: (metadata) => {
        const now = Date.now();
        return Array.from(this.metadata.entries())
          .filter(([key, meta]) => now > meta.expiresAt)
          .map(([key]) => key);
      },
    });
    
    // Size-based eviction
    this.policies.set('size', {
      shouldEvict: (metadata, maxSize) => {
        const totalSize = Array.from(this.metadata.values())
          .reduce((sum, meta) => sum + meta.size, 0);
        
        if (totalSize <= maxSize) return [];
        
        const entries = Array.from(this.metadata.entries())
          .sort((a, b) => b[1].size - a[1].size);
        
        const toEvict = [];
        let currentSize = totalSize;
        
        for (const [key, meta] of entries) {
          if (currentSize <= maxSize) break;
          toEvict.push(key);
          currentSize -= meta.size;
        }
        
        return toEvict;
      },
    });
  }
  
  set(key, value, options = {}) {
    const metadata = {
      size: this.calculateSize(value),
      createdAt: Date.now(),
      lastAccessed: Date.now(),
      accessCount: 0,
      expiresAt: options.ttl ? Date.now() + options.ttl : Infinity,
      tags: options.tags || [],
      priority: options.priority || 0,
    };
    
    // Check if eviction needed
    this.runEvictionPolicies(options);
    
    this.cache.set(key, value);
    this.metadata.set(key, metadata);
    
    // Notify subscribers
    this.notifySubscribers(key, 'set', value);
  }
  
  get(key) {
    if (!this.cache.has(key)) return undefined;
    
    // Update access metadata
    const metadata = this.metadata.get(key);
    metadata.lastAccessed = Date.now();
    metadata.accessCount++;
    
    const value = this.cache.get(key);
    this.notifySubscribers(key, 'get', value);
    
    return value;
  }
  
  invalidateByTag(tag) {
    const keysToInvalidate = [];
    
    for (const [key, metadata] of this.metadata.entries()) {
      if (metadata.tags.includes(tag)) {
        keysToInvalidate.push(key);
      }
    }
    
    keysToInvalidate.forEach(key => this.delete(key));
  }
  
  // Smart prefetching
  prefetch(keys, priority = 0) {
    return Promise.all(
      keys.map(async (key) => {
        if (!this.cache.has(key)) {
          try {
            const value = await this.fetchFunction(key);
            this.set(key, value, { priority });
          } catch (error) {
            console.warn(`Prefetch failed for ${key}:`, error);
          }
        }
      })
    );
  }
  
  // Cache analytics
  getAnalytics() {
    const totalRequests = Array.from(this.metadata.values())
      .reduce((sum, meta) => sum + meta.accessCount, 0);
    
    const hitRate = this.cache.size > 0 ? 
      (totalRequests / this.cache.size) : 0;
    
    return {
      size: this.cache.size,
      totalSize: Array.from(this.metadata.values())
        .reduce((sum, meta) => sum + meta.size, 0),
      hitRate,
      totalRequests,
      avgAccessTime: this.calculateAvgAccessTime(),
    };
  }
}

// Intelligent query caching hook
const useIntelligentCache = (queryKey, queryFn, options = {}) => {
  const cacheManager = useCacheManager();
  const [cacheHit, setCacheHit] = useState(false);
  
  const query = useQuery({
    queryKey,
    queryFn: async (...args) => {
      const cached = cacheManager.get(queryKey);
      if (cached && !isStale(cached, options.staleTime)) {
        setCacheHit(true);
        return cached.data;
      }
      
      setCacheHit(false);
      const data = await queryFn(...args);
      
      // Intelligent caching based on query patterns
      const cacheOptions = {
        ttl: options.ttl || calculateOptimalTTL(queryKey, data),
        tags: options.tags || extractTags(queryKey),
        priority: options.priority || calculatePriority(queryKey),
      };
      
      cacheManager.set(queryKey, { data, timestamp: Date.now() }, cacheOptions);
      
      // Predictive prefetching
      const relatedKeys = generateRelatedKeys(queryKey);
      cacheManager.prefetch(relatedKeys);
      
      return data;
    },
    ...options,
  });
  
  return {
    ...query,
    cacheHit,
    cacheStats: cacheManager.getAnalytics(),
  };
};

// Background cache warming
const useCacheWarming = () => {
  const cacheManager = useCacheManager();
  
  const warmCache = useCallback(async (strategy = 'user-behavior') => {
    switch (strategy) {
      case 'user-behavior':
        // Analyze user patterns and preload likely queries
        const userPatterns = await analyzeUserBehavior();
        const likelyQueries = predictLikelyQueries(userPatterns);
        await cacheManager.prefetch(likelyQueries);
        break;
        
      case 'critical-path':
        // Preload critical application data
        const criticalQueries = getCriticalQueries();
        await cacheManager.prefetch(criticalQueries, 10); // High priority
        break;
        
      case 'time-based':
        // Preload based on time of day
        const timeBasedQueries = getTimeBasedQueries();
        await cacheManager.prefetch(timeBasedQueries);
        break;
    }
  }, [cacheManager]);
  
  const scheduleWarming = useCallback((schedule) => {
    // Schedule cache warming at specific times
    const intervals = schedule.map(time => {
      const delay = calculateDelay(time);
      return setTimeout(() => warmCache(), delay);
    });
    
    return () => intervals.forEach(clearTimeout);
  }, [warmCache]);
  
  return { warmCache, scheduleWarming };
};

// Cache invalidation strategies
const useCacheInvalidation = () => {
  const queryClient = useQueryClient();
  const cacheManager = useCacheManager();
  
  const invalidateStrategies = {
    // Time-based invalidation
    timeBasedInvalidation: (queryKey, interval) => {
      return setInterval(() => {
        queryClient.invalidateQueries(queryKey);
        cacheManager.delete(queryKey);
      }, interval);
    },
    
    // Dependency-based invalidation
    dependencyInvalidation: (queryKey, dependencies) => {
      dependencies.forEach(dep => {
        cacheManager.subscribe(dep, () => {
          queryClient.invalidateQueries(queryKey);
          cacheManager.delete(queryKey);
        });
      });
    },
    
    // Smart invalidation based on mutation
    mutationBasedInvalidation: (mutationKey, affectedQueries) => {
      return useMutation({
        mutationKey,
        onSuccess: () => {
          affectedQueries.forEach(queryKey => {
            queryClient.invalidateQueries(queryKey);
            cacheManager.invalidateByTag(extractTags(queryKey));
          });
        },
      });
    },
  };
  
  return invalidateStrategies;
};
```

**Your Task:**
1. **Advanced Caching**: Build intelligent cache management
2. **Cache Policies**: Implement LRU, TTL, and size-based eviction
3. **Predictive Prefetching**: Smart data preloading
4. **Cache Analytics**: Monitor cache performance
5. **Invalidation Strategies**: Intelligent cache invalidation

**Performance Targets:**
- Cache hit rate >90% for frequently accessed data
- Cache response time <10ms
- Memory usage <100MB for cache
- Background prefetch accuracy >70%

---

## Day 7: Production Data Architecture

### Challenge: Enterprise Data Management System
Build a production-ready data management architecture.

```jsx
// Enterprise data architecture
class EnterpriseDataManager {
  constructor(config) {
    this.config = config;
    this.dataLayers = new Map();
    this.middleware = [];
    this.monitors = [];
    this.securityLayer = new SecurityLayer(config.security);
    
    this.setupDataLayers();
    this.setupMonitoring();
    this.setupErrorHandling();
  }
  
  setupDataLayers() {
    // API Layer
    this.dataLayers.set('api', new APILayer({
      baseURL: this.config.apiBaseURL,
      timeout: this.config.timeout || 30000,
      retryConfig: this.config.retryConfig,
    }));
    
    // Cache Layer
    this.dataLayers.set('cache', new CacheLayer({
      strategy: this.config.cacheStrategy || 'intelligent',
      maxSize: this.config.maxCacheSize || 100,
      ttl: this.config.defaultTTL || 300000,
    }));
    
    // Persistence Layer
    this.dataLayers.set('persistence', new PersistenceLayer({
      storage: this.config.storageType || 'indexeddb',
      encryption: this.config.encryption || false,
    }));
    
    // Real-time Layer
    this.dataLayers.set('realtime', new RealtimeLayer({
      websocketURL: this.config.websocketURL,
      sseURL: this.config.sseURL,
    }));
  }
  
  setupMonitoring() {
    this.monitors.push(new PerformanceMonitor());
    this.monitors.push(new ErrorMonitor());
    this.monitors.push(new SecurityMonitor());
    this.monitors.push(new UsageMonitor());
  }
  
  // Data request orchestration
  async getData(request) {
    const startTime = performance.now();
    
    try {
      // Security check
      await this.securityLayer.validateRequest(request);
      
      // Try cache first
      const cached = await this.dataLayers.get('cache').get(request.key);
      if (cached && !this.isStale(cached, request.staleTime)) {
        this.recordMetric('cache_hit', performance.now() - startTime);
        return cached;
      }
      
      // Try offline storage
      const persisted = await this.dataLayers.get('persistence').get(request.key);
      if (persisted && !navigator.onLine) {
        this.recordMetric('offline_hit', performance.now() - startTime);
        return persisted;
      }
      
      // Fetch from API
      const apiData = await this.dataLayers.get('api').fetch(request);
      
      // Update cache and persistence
      await this.dataLayers.get('cache').set(request.key, apiData);
      await this.dataLayers.get('persistence').set(request.key, apiData);
      
      this.recordMetric('api_fetch', performance.now() - startTime);
      return apiData;
      
    } catch (error) {
      this.handleError(error, request);
      throw error;
    }
  }
  
  // Data mutation orchestration
  async mutateData(mutation) {
    const startTime = performance.now();
    
    try {
      // Security check
      await this.securityLayer.validateMutation(mutation);
      
      // Optimistic update
      if (mutation.optimistic) {
        await this.applyOptimisticUpdate(mutation);
      }
      
      if (!navigator.onLine) {
        // Queue for later
        await this.queueMutation(mutation);
        return { queued: true };
      }
      
      // Execute mutation
      const result = await this.dataLayers.get('api').mutate(mutation);
      
      // Update cache and persistence
      await this.invalidateRelatedData(mutation);
      await this.updateRelatedData(mutation, result);
      
      this.recordMetric('mutation_success', performance.now() - startTime);
      return result;
      
    } catch (error) {
      // Rollback optimistic update
      if (mutation.optimistic) {
        await this.rollbackOptimisticUpdate(mutation);
      }
      
      this.handleError(error, mutation);
      throw error;
    }
  }
  
  // Security layer
  class SecurityLayer {
    constructor(config) {
      this.config = config;
      this.tokenManager = new TokenManager(config.tokenConfig);
      this.encryptionManager = new EncryptionManager(config.encryptionConfig);
    }
    
    async validateRequest(request) {
      // Rate limiting
      if (!await this.checkRateLimit(request)) {
        throw new Error('Rate limit exceeded');
      }
      
      // Authentication
      if (!await this.validateToken(request.token)) {
        throw new Error('Invalid authentication');
      }
      
      // Authorization
      if (!await this.checkPermissions(request)) {
        throw new Error('Insufficient permissions');
      }
      
      // Data sanitization
      request.params = this.sanitizeParams(request.params);
    }
    
    async validateMutation(mutation) {
      await this.validateRequest(mutation);
      
      // Additional mutation validation
      if (!await this.validateMutationPayload(mutation.payload)) {
        throw new Error('Invalid mutation payload');
      }
    }
    
    sanitizeParams(params) {
      // Remove potentially dangerous parameters
      const sanitized = { ...params };
      
      delete sanitized.__proto__;
      delete sanitized.constructor;
      
      // Sanitize strings
      Object.keys(sanitized).forEach(key => {
        if (typeof sanitized[key] === 'string') {
          sanitized[key] = this.sanitizeString(sanitized[key]);
        }
      });
      
      return sanitized;
    }
  }
  
  // Performance monitoring
  recordMetric(type, duration, metadata = {}) {
    this.monitors.forEach(monitor => {
      monitor.record({
        type,
        duration,
        timestamp: Date.now(),
        metadata,
      });
    });
  }
  
  // Error handling and recovery
  handleError(error, context) {
    this.monitors.forEach(monitor => {
      if (monitor instanceof ErrorMonitor) {
        monitor.recordError(error, context);
      }
    });
    
    // Auto-recovery strategies
    if (error.code === 'NETWORK_ERROR') {
      this.initializeOfflineMode();
    } else if (error.code === 'AUTH_ERROR') {
      this.refreshAuthentication();
    }
  }
}

// Production data provider
const EnterpriseDataProvider = ({ children, config }) => {
  const [dataManager] = useState(() => new EnterpriseDataManager(config));
  
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        queryFn: async ({ queryKey, signal }) => {
          return dataManager.getData({
            key: queryKey,
            signal,
            staleTime: 5 * 60 * 1000,
          });
        },
      },
      mutations: {
        mutationFn: async (mutation) => {
          return dataManager.mutateData(mutation);
        },
      },
    },
  });
  
  return (
    <QueryClientProvider client={queryClient}>
      <DataManagerContext.Provider value={dataManager}>
        {children}
      </DataManagerContext.Provider>
    </QueryClientProvider>
  );
};

// Production monitoring dashboard
const DataMonitoringDashboard = () => {
  const dataManager = useContext(DataManagerContext);
  const [metrics, setMetrics] = useState({});
  
  useEffect(() => {
    const interval = setInterval(() => {
      const currentMetrics = dataManager.getMetrics();
      setMetrics(currentMetrics);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [dataManager]);
  
  return (
    <div className="monitoring-dashboard">
      <MetricCard 
        title="API Response Time" 
        value={metrics.avgResponseTime} 
        unit="ms"
        threshold={1000}
      />
      <MetricCard 
        title="Cache Hit Rate" 
        value={metrics.cacheHitRate} 
        unit="%"
        threshold={90}
      />
      <MetricCard 
        title="Error Rate" 
        value={metrics.errorRate} 
        unit="%"
        threshold={1}
      />
      <MetricCard 
        title="Data Freshness" 
        value={metrics.avgDataAge} 
        unit="min"
        threshold={5}
      />
    </div>
  );
};
```

**Your Task:**
1. **Enterprise Architecture**: Design scalable data architecture
2. **Security Layer**: Implement comprehensive security measures
3. **Monitoring System**: Build production monitoring
4. **Error Recovery**: Create robust error handling
5. **Performance Optimization**: Optimize for enterprise scale

**Production Requirements:**
- Handle 10M+ requests per day
- 99.9% uptime SLA
- Sub-500ms response times
- Enterprise-grade security
- Comprehensive audit logging

---

## Week 10 Assessment

### Enterprise Data Management Platform
Build a comprehensive data management platform for enterprise applications.

**Platform Features:**
```
Data Management Platform
├── Core Data Engine
│   ├── Multi-layer data architecture
│   ├── Intelligent caching system
│   ├── Real-time synchronization
│   └── Offline-first capabilities
├── Security & Compliance
│   ├── Authentication & authorization
│   ├── Data encryption & privacy
│   ├── Audit logging & compliance
│   └── Rate limiting & protection
├── Performance & Monitoring
│   ├── Real-time performance metrics
│   ├── Error tracking & alerting
│   ├── Usage analytics
│   └── Performance optimization
└── Developer Tools
    ├── Data explorer & debugger
    ├── Query builder interface
    ├── Performance profiler
    └── Integration testing tools
```

**Technical Requirements:**
- Support for multiple data sources and formats
- Real-time collaboration and synchronization
- Comprehensive offline capabilities
- Enterprise-grade security and compliance
- Production monitoring and analytics

**Success Criteria:**
- Handle enterprise-scale data loads
- Maintain data consistency across all layers
- Provide sub-second response times
- Achieve 99.9% data accuracy
- Zero data loss scenarios

### Reflection Questions
1. How do you balance data consistency with performance in distributed systems?
2. What strategies work best for handling large-scale data synchronization?
3. How do you implement effective offline-first data strategies?
4. What monitoring and alerting strategies are essential for production data systems?
5. How do you ensure data security and compliance in enterprise environments?

---

## Additional Resources

### Data Fetching Libraries
- [TanStack Query (React Query) v4](https://tanstack.com/query/latest)
- [SWR Documentation](https://swr.vercel.app/)
- [Apollo Client](https://www.apollographql.com/docs/react/)

### Real-time & WebSockets
- [WebSocket API Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Socket.IO Documentation](https://socket.io/docs/v4/)

### Advanced Patterns
- [Operational Transform Guide](https://operational-transformation.github.io/)
- [CRDT Implementation Guide](https://crdt.tech/)
- [Offline-First Architecture](https://offlinefirst.org/)

**Estimated Time:** 3-4 hours per day  
**Difficulty:** Advanced to Expert  
**Focus:** Data architecture, real-time systems, performance optimization