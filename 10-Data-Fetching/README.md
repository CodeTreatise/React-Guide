# Module 10: Data Fetching

## Learning Objectives
By the end of this module, you will be able to:
- Master modern data fetching patterns in React applications
- Implement efficient caching and synchronization strategies
- Handle complex async operations with proper error handling
- Build real-time data synchronization with WebSockets and SSE
- Optimize API calls and manage request lifecycles
- Implement offline-first data strategies
- Create type-safe API integrations
- Handle large datasets with pagination and virtual scrolling

## Overview
This module covers comprehensive data fetching strategies for modern React applications, from basic HTTP requests to real-time synchronization and offline capabilities.

## Duration: Week 10 (40 hours)
- **Reading & Research**: 10 hours
- **Hands-on Practice**: 20 hours
- **Projects**: 8 hours
- **Assessment**: 2 hours

---

## Topics Covered

### 1. Modern Data Fetching with React Query / TanStack Query
```javascript
// Advanced React Query setup
import { QueryClient, QueryClientProvider, useQuery, useMutation, useInfiniteQuery } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 10, // 10 minutes
      retry: (failureCount, error) => {
        if (error.status === 404) return false
        return failureCount < 3
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
      onError: (error) => {
        toast.error(`Operation failed: ${error.message}`)
      },
    },
  },
})

// Custom hooks with React Query
function useUsers(filters = {}) {
  return useQuery({
    queryKey: ['users', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters)
      const response = await fetch(`/api/users?${params}`)
      if (!response.ok) throw new Error('Failed to fetch users')
      return response.json()
    },
    enabled: !!filters, // Only run if filters are provided
    staleTime: 1000 * 60 * 2, // Override default stale time
    select: (data) => data.users, // Transform data
  })
}

function useUserMutation() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (userData) => {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      })
      if (!response.ok) throw new Error('Failed to create user')
      return response.json()
    },
    onSuccess: (newUser) => {
      // Optimistic updates
      queryClient.setQueryData(['users'], (old) => ({
        ...old,
        users: [...(old?.users || []), newUser],
      }))
      
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['users'] })
      queryClient.invalidateQueries({ queryKey: ['stats', 'users'] })
    },
    onMutate: async (newUser) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['users'] })
      
      // Snapshot current value
      const previousUsers = queryClient.getQueryData(['users'])
      
      // Optimistically update
      queryClient.setQueryData(['users'], (old) => ({
        ...old,
        users: [...(old?.users || []), { ...newUser, id: 'temp-' + Date.now() }],
      }))
      
      return { previousUsers }
    },
    onError: (err, newUser, context) => {
      // Rollback on error
      queryClient.setQueryData(['users'], context.previousUsers)
    },
  })
}

// Infinite queries for pagination
function useInfiniteUsers(filters = {}) {
  return useInfiniteQuery({
    queryKey: ['users', 'infinite', filters],
    queryFn: async ({ pageParam = 1 }) => {
      const params = new URLSearchParams({ ...filters, page: pageParam, limit: 20 })
      const response = await fetch(`/api/users?${params}`)
      if (!response.ok) throw new Error('Failed to fetch users')
      return response.json()
    },
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.hasNextPage) {
        return pages.length + 1
      }
      return undefined
    },
    getPreviousPageParam: (firstPage, pages) => {
      if (pages.length > 1) {
        return pages.length - 1
      }
      return undefined
    },
  })
}
```

### 2. Advanced SWR Patterns
```javascript
import useSWR, { useSWRConfig, SWRConfig } from 'swr'
import useSWRInfinite from 'swr/infinite'
import useSWRMutation from 'swr/mutation'

// Global SWR configuration
const swrConfig = {
  fetcher: async (url) => {
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    })
    if (!response.ok) {
      const error = new Error('API Error')
      error.status = response.status
      error.info = await response.json()
      throw error
    }
    return response.json()
  },
  onError: (error, key) => {
    if (error.status === 401) {
      // Redirect to login
      window.location.href = '/login'
    }
    console.error(`SWR Error for ${key}:`, error)
  },
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  dedupingInterval: 2000,
}

// Custom hooks with SWR
function useUser(id, options = {}) {
  const { data, error, isLoading, mutate } = useSWR(
    id ? `/api/users/${id}` : null,
    null,
    {
      revalidateOnMount: true,
      ...options,
    }
  )

  return {
    user: data,
    isLoading,
    error,
    updateUser: (updates) => mutate({ ...data, ...updates }, false),
    refreshUser: () => mutate(),
  }
}

// SWR with mutations
function useUserActions(userId) {
  const { trigger: updateUser, isMutating: isUpdating } = useSWRMutation(
    `/api/users/${userId}`,
    async (url, { arg: updates }) => {
      const response = await fetch(url, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      })
      if (!response.ok) throw new Error('Update failed')
      return response.json()
    },
    {
      onSuccess: (data) => {
        // Update cache
        mutate(`/api/users/${userId}`, data, false)
        // Update list cache
        mutate('/api/users', (users) => 
          users.map(u => u.id === userId ? data : u), false
        )
      },
    }
  )

  const { trigger: deleteUser, isMutating: isDeleting } = useSWRMutation(
    `/api/users/${userId}`,
    async (url) => {
      const response = await fetch(url, { method: 'DELETE' })
      if (!response.ok) throw new Error('Delete failed')
      return response.json()
    },
    {
      onSuccess: () => {
        // Remove from cache
        mutate(`/api/users/${userId}`, undefined, false)
        // Update list cache
        mutate('/api/users', (users) => 
          users.filter(u => u.id !== userId), false
        )
      },
    }
  )

  return {
    updateUser,
    deleteUser,
    isUpdating,
    isDeleting,
  }
}

// Infinite pagination with SWR
function useInfiniteUserList(filters = {}) {
  const getKey = (pageIndex, previousPageData) => {
    if (previousPageData && !previousPageData.hasNextPage) return null
    const params = new URLSearchParams({
      ...filters,
      page: pageIndex + 1,
      limit: 20,
    })
    return `/api/users?${params}`
  }

  const { data, error, isLoading, isValidating, size, setSize, mutate } = useSWRInfinite(
    getKey,
    null,
    {
      revalidateOnFocus: false,
      revalidateOnMount: true,
    }
  )

  const users = data ? data.flatMap(page => page.users) : []
  const hasNextPage = data?.[data.length - 1]?.hasNextPage
  const isLoadingMore = isLoading || (size > 0 && data && typeof data[size - 1] === 'undefined')

  return {
    users,
    error,
    isLoading,
    isValidating,
    isLoadingMore,
    hasNextPage,
    loadMore: () => setSize(size + 1),
    refresh: () => mutate(),
  }
}
```

### 3. Real-time Data with WebSockets
```javascript
// WebSocket hook with automatic reconnection
function useWebSocket(url, options = {}) {
  const [socket, setSocket] = useState(null)
  const [lastMessage, setLastMessage] = useState(null)
  const [readyState, setReadyState] = useState(WebSocket.CONNECTING)
  const [connectionError, setConnectionError] = useState(null)

  const {
    onOpen,
    onClose,
    onMessage,
    onError,
    shouldReconnect = true,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
  } = options

  const reconnectTimeouts = useRef([])
  const reconnectCount = useRef(0)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url)
      
      ws.onopen = (event) => {
        setReadyState(WebSocket.OPEN)
        setConnectionError(null)
        reconnectCount.current = 0
        onOpen?.(event)
      }

      ws.onclose = (event) => {
        setReadyState(WebSocket.CLOSED)
        onClose?.(event)
        
        // Attempt reconnection
        if (shouldReconnect && reconnectCount.current < reconnectAttempts) {
          const timeout = setTimeout(() => {
            reconnectCount.current++
            connect()
          }, reconnectInterval * Math.pow(2, reconnectCount.current))
          
          reconnectTimeouts.current.push(timeout)
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          onMessage?.(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (event) => {
        setConnectionError(event)
        onError?.(event)
      }

      setSocket(ws)
    } catch (error) {
      setConnectionError(error)
    }
  }, [url, onOpen, onClose, onMessage, onError, shouldReconnect, reconnectAttempts, reconnectInterval])

  useEffect(() => {
    connect()
    
    return () => {
      // Cleanup
      reconnectTimeouts.current.forEach(clearTimeout)
      socket?.close()
    }
  }, [connect])

  const sendMessage = useCallback((message) => {
    if (socket && readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [socket, readyState])

  const disconnect = useCallback(() => {
    reconnectTimeouts.current.forEach(clearTimeout)
    socket?.close()
  }, [socket])

  return {
    lastMessage,
    readyState,
    connectionError,
    sendMessage,
    disconnect,
    reconnect: connect,
  }
}

// Real-time data synchronization
function useRealTimeData(endpoint, initialData = null) {
  const [data, setData] = useState(initialData)
  const [isConnected, setIsConnected] = useState(false)
  const queryClient = useQueryClient()

  const { lastMessage, readyState, sendMessage } = useWebSocket(
    `ws://localhost:8080/${endpoint}`,
    {
      onOpen: () => {
        setIsConnected(true)
        // Request initial data
        sendMessage({ type: 'SUBSCRIBE', endpoint })
      },
      onClose: () => setIsConnected(false),
      onMessage: (message) => {
        switch (message.type) {
          case 'INITIAL_DATA':
            setData(message.data)
            break
          case 'DATA_UPDATE':
            setData(current => ({ ...current, ...message.data }))
            // Update React Query cache
            queryClient.setQueryData([endpoint], message.data)
            break
          case 'DATA_DELETE':
            setData(current => {
              const updated = { ...current }
              delete updated[message.id]
              return updated
            })
            break
          default:
            console.log('Unknown message type:', message.type)
        }
      },
    }
  )

  return {
    data,
    isConnected,
    readyState,
    sendMessage,
  }
}
```

### 4. Server-Sent Events (SSE)
```javascript
// Server-Sent Events hook
function useServerSentEvents(url, options = {}) {
  const [data, setData] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)
  const eventSourceRef = useRef(null)

  const {
    onMessage,
    onError,
    onOpen,
    withCredentials = false,
    reconnect = true,
  } = options

  useEffect(() => {
    if (!url) return

    const eventSource = new EventSource(url, { withCredentials })
    eventSourceRef.current = eventSource

    eventSource.onopen = (event) => {
      setIsConnected(true)
      setError(null)
      onOpen?.(event)
    }

    eventSource.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data)
        setData(parsedData)
        onMessage?.(parsedData)
      } catch (err) {
        console.error('Failed to parse SSE data:', err)
      }
    }

    eventSource.onerror = (event) => {
      setIsConnected(false)
      setError(event)
      onError?.(event)
      
      if (reconnect && eventSource.readyState === EventSource.CLOSED) {
        // Attempt reconnection after delay
        setTimeout(() => {
          if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
            eventSourceRef.current = new EventSource(url, { withCredentials })
          }
        }, 3000)
      }
    }

    // Custom event listeners
    eventSource.addEventListener('update', (event) => {
      const update = JSON.parse(event.data)
      setData(current => ({ ...current, ...update }))
    })

    eventSource.addEventListener('notification', (event) => {
      const notification = JSON.parse(event.data)
      // Handle notifications
      toast.info(notification.message)
    })

    return () => {
      eventSource.close()
    }
  }, [url, withCredentials, reconnect, onMessage, onError, onOpen])

  const close = useCallback(() => {
    eventSourceRef.current?.close()
    setIsConnected(false)
  }, [])

  return {
    data,
    isConnected,
    error,
    close,
  }
}

// Real-time notifications
function useNotifications() {
  const [notifications, setNotifications] = useState([])
  
  useServerSentEvents('/api/notifications/stream', {
    onMessage: (notification) => {
      setNotifications(prev => [notification, ...prev].slice(0, 50)) // Keep last 50
    },
  })

  const markAsRead = useCallback((id) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
    // Sync with server
    fetch(`/api/notifications/${id}/read`, { method: 'POST' })
  }, [])

  return {
    notifications,
    unreadCount: notifications.filter(n => !n.read).length,
    markAsRead,
  }
}
```

### 5. Offline-First Data Strategies
```javascript
// Service Worker registration and management
function useServiceWorker() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [updateAvailable, setUpdateAvailable] = useState(false)
  const [registration, setRegistration] = useState(null)

  useEffect(() => {
    // Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then((reg) => {
          setRegistration(reg)
          
          // Check for updates
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing
            newWorker?.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                setUpdateAvailable(true)
              }
            })
          })
        })
        .catch(console.error)
    }

    // Network status listeners
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const updateApp = useCallback(() => {
    if (registration?.waiting) {
      registration.waiting.postMessage({ type: 'SKIP_WAITING' })
      window.location.reload()
    }
  }, [registration])

  return {
    isOnline,
    updateAvailable,
    updateApp,
  }
}

// Offline storage with IndexedDB
class OfflineStorage {
  constructor(dbName = 'ReactApp', version = 1) {
    this.dbName = dbName
    this.version = version
    this.db = null
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version)
      
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.db = request.result
        resolve(this.db)
      }
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        
        // Create object stores
        if (!db.objectStoreNames.contains('cache')) {
          const cacheStore = db.createObjectStore('cache', { keyPath: 'key' })
          cacheStore.createIndex('timestamp', 'timestamp', { unique: false })
        }
        
        if (!db.objectStoreNames.contains('pending')) {
          db.createObjectStore('pending', { keyPath: 'id', autoIncrement: true })
        }
      }
    })
  }

  async set(key, data, ttl = 3600000) { // 1 hour default TTL
    const transaction = this.db.transaction(['cache'], 'readwrite')
    const store = transaction.objectStore('cache')
    
    await store.put({
      key,
      data,
      timestamp: Date.now(),
      ttl,
    })
  }

  async get(key) {
    const transaction = this.db.transaction(['cache'], 'readonly')
    const store = transaction.objectStore('cache')
    const result = await store.get(key)
    
    if (!result) return null
    
    // Check TTL
    if (Date.now() - result.timestamp > result.ttl) {
      await this.delete(key)
      return null
    }
    
    return result.data
  }

  async delete(key) {
    const transaction = this.db.transaction(['cache'], 'readwrite')
    const store = transaction.objectStore('cache')
    await store.delete(key)
  }

  async addPendingRequest(request) {
    const transaction = this.db.transaction(['pending'], 'readwrite')
    const store = transaction.objectStore('pending')
    await store.add({
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers.entries()),
      body: await request.text(),
      timestamp: Date.now(),
    })
  }

  async getPendingRequests() {
    const transaction = this.db.transaction(['pending'], 'readonly')
    const store = transaction.objectStore('pending')
    return store.getAll()
  }

  async clearPendingRequests() {
    const transaction = this.db.transaction(['pending'], 'readwrite')
    const store = transaction.objectStore('pending')
    await store.clear()
  }
}

// Offline-aware fetch hook
function useOfflineFetch() {
  const { isOnline } = useServiceWorker()
  const [storage] = useState(() => new OfflineStorage())
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    storage.init().then(() => setIsReady(true))
  }, [storage])

  const fetchWithOfflineSupport = useCallback(async (url, options = {}) => {
    const cacheKey = `${options.method || 'GET'}:${url}`
    
    if (!isOnline) {
      // Try to get from cache
      const cachedData = await storage.get(cacheKey)
      if (cachedData) {
        return { data: cachedData, fromCache: true }
      }
      throw new Error('No network connection and no cached data available')
    }

    try {
      const response = await fetch(url, options)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      // Cache successful GET requests
      if (!options.method || options.method === 'GET') {
        await storage.set(cacheKey, data)
      }
      
      return { data, fromCache: false }
    } catch (error) {
      // Queue mutation requests for later
      if (options.method && options.method !== 'GET') {
        await storage.addPendingRequest(new Request(url, options))
      }
      
      // Try to return cached data as fallback
      const cachedData = await storage.get(cacheKey)
      if (cachedData) {
        return { data: cachedData, fromCache: true, error }
      }
      
      throw error
    }
  }, [isOnline, storage])

  // Sync pending requests when back online
  useEffect(() => {
    if (isOnline && isReady) {
      const syncPendingRequests = async () => {
        const pending = await storage.getPendingRequests()
        
        for (const request of pending) {
          try {
            await fetch(request.url, {
              method: request.method,
              headers: request.headers,
              body: request.body,
            })
          } catch (error) {
            console.error('Failed to sync pending request:', error)
          }
        }
        
        await storage.clearPendingRequests()
      }
      
      syncPendingRequests()
    }
  }, [isOnline, isReady, storage])

  return {
    fetchWithOfflineSupport,
    isOnline,
    isReady,
  }
}
```

### 6. Advanced Error Handling and Retry Logic
```javascript
// Enhanced error boundary for data fetching
class DataFetchingErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo })
    
    // Log to error reporting service
    this.logErrorToService(error, errorInfo)
  }

  logErrorToService = (error, errorInfo) => {
    // Send to monitoring service (e.g., Sentry, LogRocket)
    console.error('Data fetching error:', error, errorInfo)
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1,
    }))
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong while loading data.</h2>
          <details>
            <summary>Error Details</summary>
            <pre>{this.state.error && this.state.error.toString()}</pre>
            <pre>{this.state.errorInfo.componentStack}</pre>
          </details>
          <button onClick={this.handleRetry}>
            Retry ({this.state.retryCount}/3)
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// Advanced retry logic hook
function useRetryableQuery(queryFn, options = {}) {
  const [state, setState] = useState({
    data: null,
    error: null,
    isLoading: false,
    retryCount: 0,
  })

  const {
    maxRetries = 3,
    retryDelay = (attempt) => Math.min(1000 * Math.pow(2, attempt), 30000),
    retryCondition = (error) => error.status >= 500,
    onError,
    onSuccess,
  } = options

  const executeQuery = useCallback(async (isRetry = false) => {
    if (!isRetry) {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
    }

    try {
      const data = await queryFn()
      setState({
        data,
        error: null,
        isLoading: false,
        retryCount: 0,
      })
      onSuccess?.(data)
    } catch (error) {
      const shouldRetry = state.retryCount < maxRetries && retryCondition(error)
      
      if (shouldRetry) {
        const delay = retryDelay(state.retryCount)
        setState(prev => ({ ...prev, retryCount: prev.retryCount + 1 }))
        
        setTimeout(() => {
          executeQuery(true)
        }, delay)
      } else {
        setState(prev => ({
          ...prev,
          error,
          isLoading: false,
        }))
        onError?.(error)
      }
    }
  }, [queryFn, state.retryCount, maxRetries, retryDelay, retryCondition, onError, onSuccess])

  const retry = useCallback(() => {
    setState(prev => ({ ...prev, retryCount: 0 }))
    executeQuery()
  }, [executeQuery])

  useEffect(() => {
    executeQuery()
  }, []) // Only run on mount

  return {
    ...state,
    retry,
    canRetry: state.error && state.retryCount < maxRetries,
  }
}
```

---

## Best Practices

### 1. Data Fetching Strategy
- Use React Query/SWR for server state management
- Implement proper loading and error states
- Cache data appropriately with TTL
- Handle race conditions and request cancellation
- Implement optimistic updates for better UX

### 2. Performance Optimization
- Implement request deduplication
- Use pagination for large datasets
- Implement virtual scrolling for lists
- Cache responses at multiple levels
- Use background refetching for fresh data

### 3. Error Handling
- Implement comprehensive error boundaries
- Provide meaningful error messages
- Implement retry logic with exponential backoff
- Log errors for monitoring and debugging
- Graceful degradation for offline scenarios

### 4. Real-time Features
- Use WebSockets for bidirectional communication
- Implement Server-Sent Events for server updates
- Handle connection failures and reconnection
- Optimize message frequency and payload size
- Implement conflict resolution for concurrent updates

---

## Projects

### Project 1: Real-time Chat Application
Build a real-time chat with:
- WebSocket connections
- Message history with pagination
- Typing indicators
- Offline message queuing
- File sharing capabilities

### Project 2: Data Dashboard with Live Updates
Create a dashboard featuring:
- Real-time data visualization
- Multiple data sources
- Filtering and aggregation
- Export functionality
- Offline caching

### Project 3: E-commerce Product Catalog
Develop a catalog with:
- Advanced search and filtering
- Infinite scrolling
- Image lazy loading
- Shopping cart synchronization
- Inventory updates

---

## Assessment Criteria

### Knowledge Check (40 points)
- Modern data fetching patterns
- Caching and synchronization strategies
- Real-time communication protocols
- Error handling and retry logic
- Offline-first development

### Practical Skills (40 points)
- Implement efficient data fetching
- Build real-time features
- Handle complex async scenarios
- Optimize API performance
- Create offline-capable applications

### Project Quality (20 points)
- Data architecture design
- Performance optimization
- Error handling coverage
- Real-time functionality
- Code organization and testing

---

## Resources

### Essential Reading
- [React Query Documentation](https://tanstack.com/query)
- [SWR Documentation](https://swr.vercel.app/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### Advanced Resources
- [Offline First](https://offlinefirst.org/)
- [Service Workers](https://developers.google.com/web/fundamentals/primers/service-workers)
- [IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [HTTP Caching](https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching)

### Tools and Libraries
- TanStack Query (React Query)
- SWR
- Socket.io
- Axios
- React Error Boundary
- Workbox

---

## Next Steps
After completing this module, you'll be ready for Module 11: Styling Solutions, where you'll learn modern approaches to styling React applications including CSS-in-JS, design systems, and responsive design patterns.

The combination of advanced data fetching with proper styling creates the foundation for building polished, performant React applications.
