# Advanced Async State Management

## Table of Contents
1. [Introduction](#introduction)
2. [Async State Patterns](#async-state-patterns)
3. [Redux Middleware Deep Dive](#redux-middleware-deep-dive)
4. [Saga Patterns](#saga-patterns)
5. [Observable Streams with RxJS](#observable-streams-with-rxjs)
6. [React Query & SWR Advanced](#react-query--swr-advanced)
7. [State Machines for Async Operations](#state-machines-for-async-operations)
8. [Error Boundaries and Recovery](#error-boundaries-and-recovery)
9. [Performance Optimization](#performance-optimization)
10. [Testing Strategies](#testing-strategies)

## Introduction

Advanced async state management goes beyond simple loading states to handle complex scenarios like:
- Concurrent requests and race conditions
- Optimistic updates and rollbacks
- Real-time data synchronization
- Complex error handling and recovery
- Background sync and offline capabilities

## Async State Patterns

### The Async State Model

```javascript
// Complete async state representation
const asyncState = {
  data: null,
  loading: false,
  error: null,
  lastFetch: null,
  stale: false,
  optimistic: false,
  retryCount: 0,
  abortController: null
}

// Action types for complete async flow
const ASYNC_ACTIONS = {
  REQUEST: 'REQUEST',
  SUCCESS: 'SUCCESS',
  FAILURE: 'FAILURE',
  CANCEL: 'CANCEL',
  RETRY: 'RETRY',
  INVALIDATE: 'INVALIDATE',
  OPTIMISTIC_UPDATE: 'OPTIMISTIC_UPDATE',
  ROLLBACK: 'ROLLBACK'
}
```

### Advanced Async Reducer Pattern

```javascript
function createAsyncReducer(actionType) {
  const initialState = {
    data: null,
    loading: false,
    error: null,
    lastFetch: null,
    stale: false,
    optimistic: null,
    retryCount: 0
  }

  return (state = initialState, action) => {
    switch (action.type) {
      case `${actionType}_REQUEST`:
        return {
          ...state,
          loading: true,
          error: null,
          retryCount: action.isRetry ? state.retryCount + 1 : 0
        }

      case `${actionType}_SUCCESS`:
        return {
          ...state,
          loading: false,
          data: action.payload,
          error: null,
          lastFetch: Date.now(),
          stale: false,
          optimistic: null
        }

      case `${actionType}_FAILURE`:
        return {
          ...state,
          loading: false,
          error: action.error,
          optimistic: null
        }

      case `${actionType}_OPTIMISTIC_UPDATE`:
        return {
          ...state,
          optimistic: action.payload,
          data: action.payload // Apply optimistically
        }

      case `${actionType}_ROLLBACK`:
        return {
          ...state,
          data: state.optimistic ? 
            action.previousData : state.data,
          optimistic: null,
          error: action.error
        }

      case `${actionType}_INVALIDATE`:
        return {
          ...state,
          stale: true
        }

      case `${actionType}_CANCEL`:
        return {
          ...state,
          loading: false,
          error: { type: 'CANCELLED', message: 'Request cancelled' }
        }

      default:
        return state
    }
  }
}
```

### Optimistic Updates Pattern

```javascript
// Optimistic update hook
function useOptimisticMutation(mutationFn, options = {}) {
  const [state, dispatch] = useReducer(asyncReducer, initialAsyncState)
  const previousDataRef = useRef(null)

  const mutate = useCallback(async (variables) => {
    try {
      // Store previous data for rollback
      previousDataRef.current = state.data

      // Apply optimistic update
      if (options.optimisticUpdate) {
        const optimisticData = options.optimisticUpdate(state.data, variables)
        dispatch({
          type: 'OPTIMISTIC_UPDATE',
          payload: optimisticData
        })
      }

      dispatch({ type: 'REQUEST' })

      // Perform actual mutation
      const result = await mutationFn(variables)

      dispatch({
        type: 'SUCCESS',
        payload: result
      })

      return result
    } catch (error) {
      // Rollback on error
      dispatch({
        type: 'ROLLBACK',
        error,
        previousData: previousDataRef.current
      })
      throw error
    }
  }, [mutationFn, state.data])

  return {
    ...state,
    mutate,
    isOptimistic: state.optimistic !== null
  }
}

// Usage example
function PostEditor({ postId }) {
  const { mutate: updatePost, isOptimistic, error } = useOptimisticMutation(
    updatePostAPI,
    {
      optimisticUpdate: (currentData, { title, content }) => ({
        ...currentData,
        title,
        content,
        updatedAt: new Date().toISOString()
      })
    }
  )

  const handleSave = async (formData) => {
    try {
      await updatePost(formData)
      toast.success('Post updated successfully')
    } catch (error) {
      toast.error('Failed to update post')
    }
  }

  return (
    <div>
      {isOptimistic && (
        <Badge variant="secondary">Saving...</Badge>
      )}
      {error && (
        <Alert variant="destructive">
          Update failed: {error.message}
        </Alert>
      )}
      {/* Form components */}
    </div>
  )
}
```

## Redux Middleware Deep Dive

### Custom Async Middleware

```javascript
// Advanced async middleware with cancellation and retries
const asyncMiddleware = (store) => (next) => (action) => {
  if (!action.async) {
    return next(action)
  }

  const {
    types,
    promise,
    onSuccess,
    onFailure,
    shouldCancel,
    retryConfig,
    optimistic
  } = action.async

  const [REQUEST, SUCCESS, FAILURE] = types
  const state = store.getState()

  // Check if should cancel existing request
  if (shouldCancel && shouldCancel(state)) {
    store.dispatch({ type: `${REQUEST}_CANCEL` })
    return Promise.resolve()
  }

  // Apply optimistic update
  if (optimistic) {
    store.dispatch({
      type: `${REQUEST}_OPTIMISTIC`,
      payload: optimistic(action.payload)
    })
  }

  store.dispatch({ type: REQUEST, payload: action.payload })

  const executeRequest = async (attempt = 1) => {
    try {
      const result = await promise
      
      store.dispatch({
        type: SUCCESS,
        payload: result,
        meta: { attempt }
      })

      if (onSuccess) {
        onSuccess(result, store.dispatch, store.getState)
      }

      return result
    } catch (error) {
      const shouldRetry = retryConfig &&
        attempt < retryConfig.maxAttempts &&
        retryConfig.shouldRetry(error)

      if (shouldRetry) {
        await new Promise(resolve => 
          setTimeout(resolve, retryConfig.delay * attempt)
        )
        return executeRequest(attempt + 1)
      }

      store.dispatch({
        type: FAILURE,
        error,
        meta: { attempt }
      })

      if (onFailure) {
        onFailure(error, store.dispatch, store.getState)
      }

      throw error
    }
  }

  return executeRequest()
}

// Usage
const fetchUserAction = (userId) => ({
  async: {
    types: ['FETCH_USER_REQUEST', 'FETCH_USER_SUCCESS', 'FETCH_USER_FAILURE'],
    promise: api.getUser(userId),
    shouldCancel: (state) => state.user.loading,
    retryConfig: {
      maxAttempts: 3,
      delay: 1000,
      shouldRetry: (error) => error.status >= 500
    },
    onSuccess: (user, dispatch) => {
      dispatch(fetchUserPreferences(user.id))
    }
  },
  payload: { userId }
})
```

### Request Deduplication Middleware

```javascript
const deduplicationMiddleware = (store) => {
  const pendingRequests = new Map()

  return (next) => (action) => {
    if (!action.async || !action.dedupe) {
      return next(action)
    }

    const key = action.dedupe.key || JSON.stringify(action.payload)
    
    if (pendingRequests.has(key)) {
      // Return existing promise
      return pendingRequests.get(key)
    }

    const promise = next(action)
    pendingRequests.set(key, promise)

    promise.finally(() => {
      pendingRequests.delete(key)
    })

    return promise
  }
}

// Usage
const fetchDataAction = (params) => ({
  async: {
    types: ['FETCH_DATA_REQUEST', 'FETCH_DATA_SUCCESS', 'FETCH_DATA_FAILURE'],
    promise: api.getData(params)
  },
  dedupe: {
    key: `fetch_data_${JSON.stringify(params)}`
  },
  payload: params
})
```

## Saga Patterns

### Advanced Saga Patterns

```javascript
import { 
  call, 
  put, 
  take, 
  fork, 
  cancel, 
  cancelled,
  race,
  delay,
  select,
  takeEvery,
  takeLatest
} from 'redux-saga/effects'

// Race condition handling
function* fetchWithTimeout(action) {
  try {
    const { response, timeout } = yield race({
      response: call(api.fetchData, action.payload),
      timeout: delay(5000)
    })

    if (timeout) {
      yield put({ type: 'FETCH_TIMEOUT' })
    } else {
      yield put({ type: 'FETCH_SUCCESS', payload: response })
    }
  } catch (error) {
    yield put({ type: 'FETCH_FAILURE', error })
  }
}

// Cancellable task pattern
function* cancellableTask(action) {
  try {
    const result = yield call(longRunningOperation, action.payload)
    yield put({ type: 'TASK_SUCCESS', payload: result })
  } catch (error) {
    if (yield cancelled()) {
      yield put({ type: 'TASK_CANCELLED' })
    } else {
      yield put({ type: 'TASK_FAILURE', error })
    }
  }
}

function* taskManager() {
  let currentTask = null

  while (true) {
    const action = yield take(['START_TASK', 'CANCEL_TASK'])

    if (action.type === 'START_TASK') {
      if (currentTask) {
        yield cancel(currentTask)
      }
      currentTask = yield fork(cancellableTask, action)
    } else if (action.type === 'CANCEL_TASK') {
      if (currentTask) {
        yield cancel(currentTask)
        currentTask = null
      }
    }
  }
}

// Retry pattern with exponential backoff
function* retryableSaga(action) {
  const maxAttempts = 3
  let attempt = 1

  while (attempt <= maxAttempts) {
    try {
      const result = yield call(api.unstableEndpoint, action.payload)
      yield put({ type: 'REQUEST_SUCCESS', payload: result })
      return
    } catch (error) {
      if (attempt === maxAttempts) {
        yield put({ type: 'REQUEST_FAILURE', error })
        return
      }

      yield put({
        type: 'REQUEST_RETRY',
        payload: { attempt, error }
      })

      // Exponential backoff
      yield delay(1000 * Math.pow(2, attempt - 1))
      attempt++
    }
  }
}

// Background sync pattern
function* backgroundSyncSaga() {
  while (true) {
    try {
      const isOnline = yield select(getOnlineStatus)
      
      if (isOnline) {
        const pendingActions = yield select(getPendingActions)
        
        for (const pendingAction of pendingActions) {
          try {
            yield call(syncAction, pendingAction)
            yield put(removePendingAction(pendingAction.id))
          } catch (error) {
            console.warn('Failed to sync action:', error)
          }
        }
      }

      yield delay(30000) // Check every 30 seconds
    } catch (error) {
      console.error('Background sync error:', error)
      yield delay(60000) // Wait longer on error
    }
  }
}
```

### Saga Channel Patterns

```javascript
import { eventChannel, buffers } from 'redux-saga'

// WebSocket channel
function createWebSocketChannel(url) {
  return eventChannel(emitter => {
    const ws = new WebSocket(url)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      emitter(data)
    }

    ws.onerror = (error) => {
      emitter({ type: 'ERROR', error })
    }

    ws.onclose = () => {
      emitter({ type: 'CLOSED' })
    }

    return () => {
      ws.close()
    }
  }, buffers.expanding(100))
}

function* webSocketSaga() {
  const channel = yield call(createWebSocketChannel, 'ws://localhost:8080')

  try {
    while (true) {
      const message = yield take(channel)
      
      if (message.type === 'ERROR') {
        yield put({ type: 'WEBSOCKET_ERROR', error: message.error })
      } else if (message.type === 'CLOSED') {
        yield put({ type: 'WEBSOCKET_DISCONNECTED' })
        break
      } else {
        yield put({ type: 'WEBSOCKET_MESSAGE', payload: message })
      }
    }
  } finally {
    channel.close()
  }
}

// Server-Sent Events channel
function createSSEChannel(url) {
  return eventChannel(emitter => {
    const eventSource = new EventSource(url)

    eventSource.onmessage = (event) => {
      emitter(JSON.parse(event.data))
    }

    eventSource.onerror = (error) => {
      emitter({ type: 'SSE_ERROR', error })
    }

    return () => {
      eventSource.close()
    }
  })
}
```

## Observable Streams with RxJS

### RxJS Integration with React

```javascript
import { BehaviorSubject, combineLatest, fromEvent, merge } from 'rxjs'
import { 
  map, 
  filter, 
  debounceTime, 
  distinctUntilChanged,
  switchMap,
  catchError,
  retry,
  share
} from 'rxjs/operators'

// Observable store pattern
class ObservableStore {
  constructor(initialState) {
    this.state$ = new BehaviorSubject(initialState)
    this.actions$ = new Subject()
    
    this.setupReducers()
  }

  setupReducers() {
    this.actions$
      .pipe(
        map(action => this.reduce(this.state$.value, action)),
        catchError((error, caught) => {
          console.error('Reducer error:', error)
          return caught
        })
      )
      .subscribe(newState => this.state$.next(newState))
  }

  reduce(state, action) {
    switch (action.type) {
      case 'SET_LOADING':
        return { ...state, loading: action.payload }
      case 'SET_DATA':
        return { ...state, data: action.payload, loading: false }
      case 'SET_ERROR':
        return { ...state, error: action.payload, loading: false }
      default:
        return state
    }
  }

  dispatch(action) {
    this.actions$.next(action)
  }

  select(selector) {
    return this.state$.pipe(
      map(selector),
      distinctUntilChanged()
    )
  }
}

// React hook for observable store
function useObservableStore(store, selector) {
  const [state, setState] = useState(() => selector(store.state$.value))

  useEffect(() => {
    const subscription = store.select(selector).subscribe(setState)
    return () => subscription.unsubscribe()
  }, [store, selector])

  return [state, store.dispatch.bind(store)]
}

// Advanced async operations with RxJS
function createDataService(apiUrl) {
  const cache = new Map()
  
  return {
    // Cached data fetching with refresh
    getData: (id, forceRefresh = false) => {
      const cacheKey = `data_${id}`
      
      if (!forceRefresh && cache.has(cacheKey)) {
        return cache.get(cacheKey)
      }

      const stream$ = fromFetch(`${apiUrl}/data/${id}`)
        .pipe(
          switchMap(response => {
            if (response.ok) {
              return response.json()
            } else {
              throw new Error(`HTTP ${response.status}`)
            }
          }),
          retry(3),
          share(),
          catchError(error => {
            console.error('Data fetch error:', error)
            throw error
          })
        )

      cache.set(cacheKey, stream$)
      
      // Clear cache after 5 minutes
      setTimeout(() => cache.delete(cacheKey), 5 * 60 * 1000)
      
      return stream$
    },

    // Real-time updates
    getDataUpdates: (id) => {
      return new WebSocket(`ws://localhost:8080/data/${id}`)
        |> fromEvent('message')
        |> map(event => JSON.parse(event.data))
        |> retry(3)
    },

    // Search with debouncing
    search: (query$) => {
      return query$.pipe(
        debounceTime(300),
        distinctUntilChanged(),
        filter(query => query.length >= 2),
        switchMap(query =>
          fromFetch(`${apiUrl}/search?q=${encodeURIComponent(query)}`)
            .pipe(
              switchMap(response => response.json()),
              catchError(() => of([]))
            )
        )
      )
    }
  }
}

// React component using RxJS
function SearchComponent() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  
  const querySubject = useMemo(() => new BehaviorSubject(''), [])
  const dataService = useMemo(() => createDataService('/api'), [])

  useEffect(() => {
    const subscription = dataService.search(querySubject)
      .pipe(
        tap(() => setLoading(true)),
        map(results => {
          setLoading(false)
          return results
        })
      )
      .subscribe(setResults)

    return () => subscription.unsubscribe()
  }, [dataService, querySubject])

  const handleQueryChange = (e) => {
    const newQuery = e.target.value
    setQuery(newQuery)
    querySubject.next(newQuery)
  }

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={handleQueryChange}
        placeholder="Search..."
      />
      {loading && <div>Searching...</div>}
      <ul>
        {results.map(result => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  )
}
```

## React Query & SWR Advanced

### Advanced React Query Patterns

```javascript
import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  useInfiniteQuery
} from '@tanstack/react-query'

// Advanced query configuration
function useAdvancedUserQuery(userId, options = {}) {
  const queryClient = useQueryClient()

  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch user')
      }
      return response.json()
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error) => {
      if (error.status === 404) return false
      return failureCount < 3
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    onSuccess: (data) => {
      // Prefetch related data
      queryClient.prefetchQuery({
        queryKey: ['userPosts', data.id],
        queryFn: () => fetchUserPosts(data.id)
      })
    },
    select: (data) => {
      // Transform data
      return {
        ...data,
        fullName: `${data.firstName} ${data.lastName}`,
        isActive: data.lastLoginAt > Date.now() - 30 * 24 * 60 * 60 * 1000
      }
    },
    ...options
  })
}

// Optimistic mutations with rollback
function useOptimisticUserUpdate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (userData) => {
      const response = await fetch(`/api/users/${userData.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      })
      
      if (!response.ok) {
        throw new Error('Failed to update user')
      }
      
      return response.json()
    },
    onMutate: async (userData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries(['user', userData.id])

      // Snapshot previous value
      const previousUser = queryClient.getQueryData(['user', userData.id])

      // Optimistically update
      queryClient.setQueryData(['user', userData.id], userData)

      return { previousUser }
    },
    onError: (error, userData, context) => {
      // Rollback on error
      if (context?.previousUser) {
        queryClient.setQueryData(
          ['user', userData.id], 
          context.previousUser
        )
      }
    },
    onSettled: (data, error, userData) => {
      // Always refetch after error or success
      queryClient.invalidateQueries(['user', userData.id])
    }
  })
}

// Infinite scroll with pagination
function useInfinitePostsList(filters = {}) {
  return useInfiniteQuery({
    queryKey: ['posts', 'infinite', filters],
    queryFn: async ({ pageParam = 0 }) => {
      const searchParams = new URLSearchParams({
        page: pageParam.toString(),
        limit: '10',
        ...filters
      })
      
      const response = await fetch(`/api/posts?${searchParams}`)
      return response.json()
    },
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.posts.length < 10) return undefined
      return pages.length
    },
    staleTime: 30 * 1000, // 30 seconds
    select: (data) => ({
      pages: data.pages,
      posts: data.pages.flatMap(page => page.posts),
      totalCount: data.pages[0]?.totalCount || 0
    })
  })
}

// Background updates and sync
function useBackgroundSync() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const interval = setInterval(() => {
      // Refetch all stale queries in the background
      queryClient.refetchQueries({
        stale: true,
        type: 'active'
      })
    }, 30000) // Every 30 seconds

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        queryClient.resumePausedMutations()
        queryClient.refetchQueries({ stale: true })
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      clearInterval(interval)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [queryClient])
}
```

### Advanced SWR Patterns

```javascript
import useSWR, { useSWRConfig } from 'swr'
import useSWRMutation from 'swr/mutation'

// Global SWR configuration
const swrConfig = {
  fetcher: async (url) => {
    const response = await fetch(url)
    if (!response.ok) {
      const error = new Error('An error occurred while fetching the data.')
      error.info = await response.json()
      error.status = response.status
      throw error
    }
    return response.json()
  },
  onError: (error, key) => {
    console.error('SWR error:', error, 'for key:', key)
  },
  onLoadingSlow: (key, config) => {
    console.warn('SWR loading slow for key:', key)
  },
  loadingTimeout: 3000,
  errorRetryCount: 3,
  errorRetryInterval: 1000,
  focusThrottleInterval: 5000
}

// Advanced data fetching with dependencies
function useUserWithPosts(userId) {
  const { data: user, error: userError } = useSWR(
    userId ? `/api/users/${userId}` : null
  )

  const { data: posts, error: postsError } = useSWR(
    user ? `/api/users/${user.id}/posts` : null
  )

  return {
    user,
    posts,
    loading: !user && !userError,
    error: userError || postsError
  }
}

// Optimistic mutations
function useOptimisticPost(postId) {
  const { mutate } = useSWRConfig()
  
  const updatePost = useSWRMutation(
    `/api/posts/${postId}`,
    async (url, { arg: updates }) => {
      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      return response.json()
    },
    {
      optimisticData: (current) => ({ ...current, ...updates }),
      rollbackOnError: true,
      populateCache: true,
      revalidate: false
    }
  )

  return { updatePost }
}

// Real-time updates with SWR
function useRealtimeData(key) {
  const { data, error, mutate } = useSWR(key)

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8080${key}`)
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      mutate(update, false) // Update without revalidation
    }

    return () => ws.close()
  }, [key, mutate])

  return { data, error, loading: !data && !error }
}

// Prefetching and cache warming
function usePrefetch() {
  const { mutate } = useSWRConfig()

  const prefetch = useCallback((key) => {
    mutate(key) // This will trigger a fetch and cache the result
  }, [mutate])

  const warmCache = useCallback((key, data) => {
    mutate(key, data, false) // Populate cache without revalidation
  }, [mutate])

  return { prefetch, warmCache }
}
```

## State Machines for Async Operations

### XState Integration

```javascript
import { createMachine, assign, interpret } from 'xstate'
import { useMachine } from '@xstate/react'

// Async operation state machine
const asyncMachine = createMachine({
  id: 'async',
  initial: 'idle',
  context: {
    data: null,
    error: null,
    retryCount: 0
  },
  states: {
    idle: {
      on: {
        FETCH: 'loading'
      }
    },
    loading: {
      invoke: {
        id: 'fetchData',
        src: 'fetchData',
        onDone: {
          target: 'success',
          actions: assign({
            data: (context, event) => event.data,
            error: null,
            retryCount: 0
          })
        },
        onError: [
          {
            target: 'retrying',
            cond: 'canRetry',
            actions: assign({
              error: (context, event) => event.data,
              retryCount: (context) => context.retryCount + 1
            })
          },
          {
            target: 'failure',
            actions: assign({
              error: (context, event) => event.data
            })
          }
        ]
      },
      on: {
        CANCEL: 'idle'
      }
    },
    success: {
      on: {
        FETCH: 'loading',
        INVALIDATE: 'idle'
      }
    },
    failure: {
      on: {
        RETRY: 'loading',
        FETCH: 'loading'
      }
    },
    retrying: {
      after: {
        1000: 'loading'
      },
      on: {
        CANCEL: 'idle'
      }
    }
  }
}, {
  services: {
    fetchData: async (context, event) => {
      const response = await fetch(event.url)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      return response.json()
    }
  },
  guards: {
    canRetry: (context) => context.retryCount < 3
  }
})

// React component using state machine
function DataFetcher({ url }) {
  const [state, send] = useMachine(asyncMachine)

  const { data, error, retryCount } = state.context

  const handleFetch = () => {
    send({ type: 'FETCH', url })
  }

  const handleRetry = () => {
    send('RETRY')
  }

  const handleCancel = () => {
    send('CANCEL')
  }

  return (
    <div>
      <button onClick={handleFetch} disabled={state.matches('loading')}>
        Fetch Data
      </button>

      {state.matches('loading') && (
        <div>
          Loading... 
          <button onClick={handleCancel}>Cancel</button>
        </div>
      )}

      {state.matches('retrying') && (
        <div>Retrying... (Attempt {retryCount})</div>
      )}

      {state.matches('success') && (
        <div>
          <h3>Data:</h3>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}

      {state.matches('failure') && (
        <div>
          <p>Error: {error.message}</p>
          <button onClick={handleRetry}>Retry</button>
        </div>
      )}
    </div>
  )
}
```

### Complex Form State Machine

```javascript
const formMachine = createMachine({
  id: 'form',
  initial: 'editing',
  context: {
    values: {},
    errors: {},
    touched: {},
    isDirty: false
  },
  states: {
    editing: {
      on: {
        CHANGE: {
          actions: assign({
            values: (context, event) => ({
              ...context.values,
              [event.field]: event.value
            }),
            touched: (context, event) => ({
              ...context.touched,
              [event.field]: true
            }),
            isDirty: true
          })
        },
        VALIDATE: {
          target: 'validating'
        },
        SUBMIT: {
          target: 'validating'
        }
      }
    },
    validating: {
      invoke: {
        id: 'validate',
        src: 'validateForm',
        onDone: [
          {
            target: 'submitting',
            cond: 'isValid',
            actions: assign({
              errors: {}
            })
          },
          {
            target: 'editing',
            actions: assign({
              errors: (context, event) => event.data
            })
          }
        ]
      }
    },
    submitting: {
      invoke: {
        id: 'submit',
        src: 'submitForm',
        onDone: {
          target: 'success',
          actions: assign({
            isDirty: false
          })
        },
        onError: {
          target: 'editing',
          actions: assign({
            errors: (context, event) => ({
              _form: event.data.message
            })
          })
        }
      }
    },
    success: {
      on: {
        RESET: {
          target: 'editing',
          actions: assign({
            values: {},
            errors: {},
            touched: {},
            isDirty: false
          })
        }
      }
    }
  }
}, {
  services: {
    validateForm: async (context) => {
      const errors = {}
      
      if (!context.values.email) {
        errors.email = 'Email is required'
      } else if (!/\S+@\S+\.\S+/.test(context.values.email)) {
        errors.email = 'Email is invalid'
      }

      if (!context.values.password) {
        errors.password = 'Password is required'
      } else if (context.values.password.length < 8) {
        errors.password = 'Password must be at least 8 characters'
      }

      if (Object.keys(errors).length > 0) {
        throw errors
      }

      return {}
    },
    submitForm: async (context) => {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context.values)
      })

      if (!response.ok) {
        throw new Error('Submission failed')
      }

      return response.json()
    }
  },
  guards: {
    isValid: (context, event) => Object.keys(event.data).length === 0
  }
})
```

## Error Boundaries and Recovery

### Advanced Error Boundary

```javascript
class AsyncErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo })
    
    // Log error to monitoring service
    this.logError(error, errorInfo)
  }

  logError = (error, errorInfo) => {
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    }

    // Send to error reporting service
    fetch('/api/errors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorReport)
    }).catch(console.error)
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }))
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
            <pre>{this.state.error?.stack}</pre>
          </details>
          <button onClick={this.handleRetry}>
            Try Again ({this.state.retryCount}/3)
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook for error recovery
function useErrorRecovery() {
  const [error, setError] = useState(null)
  const [retryCount, setRetryCount] = useState(0)

  const throwError = useCallback((error) => {
    setError(error)
  }, [])

  const recover = useCallback(() => {
    setError(null)
    setRetryCount(count => count + 1)
  }, [])

  const reset = useCallback(() => {
    setError(null)
    setRetryCount(0)
  }, [])

  return { error, retryCount, throwError, recover, reset }
}
```

## Performance Optimization

### Async State Performance

```javascript
// Memoized async hook
function useMemoizedAsync(asyncFn, deps, options = {}) {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  })

  const memoizedFn = useMemo(asyncFn, deps)

  const execute = useCallback(async (...args) => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const result = await memoizedFn(...args)
      setState({ data: result, loading: false, error: null })
      return result
    } catch (error) {
      setState({ data: null, loading: false, error })
      throw error
    }
  }, [memoizedFn])

  return { ...state, execute }
}

// Batched state updates
function useBatchedAsync() {
  const [updates, setUpdates] = useState([])
  const timeoutRef = useRef(null)

  const batchUpdate = useCallback((update) => {
    setUpdates(prev => [...prev, update])

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      setUpdates(current => {
        // Process all batched updates
        const finalState = current.reduce((acc, update) => ({
          ...acc,
          ...update
        }), {})

        // Apply to actual state
        applyBatchedUpdates(finalState)
        
        return []
      })
    }, 16) // Next frame
  }, [])

  return { batchUpdate }
}

// Request throttling
function useThrottledRequests(limit = 5) {
  const activeRequests = useRef(0)
  const queue = useRef([])

  const throttledRequest = useCallback(async (requestFn) => {
    return new Promise((resolve, reject) => {
      const executeRequest = async () => {
        activeRequests.current++
        
        try {
          const result = await requestFn()
          resolve(result)
        } catch (error) {
          reject(error)
        } finally {
          activeRequests.current--
          processQueue()
        }
      }

      if (activeRequests.current < limit) {
        executeRequest()
      } else {
        queue.current.push(executeRequest)
      }
    })
  }, [limit])

  const processQueue = useCallback(() => {
    while (queue.current.length > 0 && activeRequests.current < limit) {
      const nextRequest = queue.current.shift()
      nextRequest()
    }
  }, [limit])

  return { throttledRequest }
}
```

## Testing Strategies

### Testing Async State

```javascript
import { renderHook, act, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock API for testing
const mockApi = {
  fetchUser: jest.fn(),
  updateUser: jest.fn()
}

// Test wrapper for React Query
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0
      },
      mutations: {
        retry: false
      }
    }
  })
}

function TestWrapper({ children }) {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

// Testing async hooks
describe('useUserQuery', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should fetch user data successfully', async () => {
    const mockUser = { id: 1, name: 'John Doe' }
    mockApi.fetchUser.mockResolvedValue(mockUser)

    const { result } = renderHook(
      () => useUserQuery(1),
      { wrapper: TestWrapper }
    )

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockUser)
    expect(mockApi.fetchUser).toHaveBeenCalledWith(1)
  })

  it('should handle errors gracefully', async () => {
    const mockError = new Error('Network error')
    mockApi.fetchUser.mockRejectedValue(mockError)

    const { result } = renderHook(
      () => useUserQuery(1),
      { wrapper: TestWrapper }
    )

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toEqual(mockError)
  })

  it('should retry failed requests', async () => {
    mockApi.fetchUser
      .mockRejectedValueOnce(new Error('First failure'))
      .mockRejectedValueOnce(new Error('Second failure'))
      .mockResolvedValueOnce({ id: 1, name: 'John Doe' })

    const { result } = renderHook(
      () => useUserQuery(1, { retry: 2 }),
      { wrapper: TestWrapper }
    )

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(mockApi.fetchUser).toHaveBeenCalledTimes(3)
  })
})

// Testing optimistic updates
describe('useOptimisticUserUpdate', () => {
  it('should apply optimistic update and rollback on error', async () => {
    const queryClient = createTestQueryClient()
    const initialUser = { id: 1, name: 'John Doe' }
    const updatedUser = { id: 1, name: 'Jane Doe' }

    // Pre-populate cache
    queryClient.setQueryData(['user', 1], initialUser)

    mockApi.updateUser.mockRejectedValue(new Error('Update failed'))

    const { result } = renderHook(
      () => useOptimisticUserUpdate(),
      { 
        wrapper: ({ children }) => (
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        )
      }
    )

    // Trigger optimistic update
    act(() => {
      result.current.mutate(updatedUser)
    })

    // Should immediately show optimistic data
    const optimisticData = queryClient.getQueryData(['user', 1])
    expect(optimisticData).toEqual(updatedUser)

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    // Should rollback to original data
    const rolledBackData = queryClient.getQueryData(['user', 1])
    expect(rolledBackData).toEqual(initialUser)
  })
})

// Testing state machines
describe('asyncMachine', () => {
  it('should transition through states correctly', () => {
    const service = interpret(asyncMachine)
    
    expect(service.state.value).toBe('idle')

    service.send({ type: 'FETCH', url: '/api/data' })
    expect(service.state.value).toBe('loading')

    service.send({ type: 'CANCEL' })
    expect(service.state.value).toBe('idle')
  })

  it('should retry on failure', () => {
    const service = interpret(asyncMachine.withConfig({
      guards: {
        canRetry: () => true
      }
    }))

    service.start()
    service.send({ type: 'FETCH', url: '/api/data' })
    
    // Simulate error
    service.send({ type: 'error.platform.fetchData', data: new Error('Failed') })
    
    expect(service.state.value).toBe('retrying')
    expect(service.state.context.retryCount).toBe(1)
  })
})
```

## Best Practices

### 1. Error Handling Strategy
- Implement comprehensive error boundaries
- Use typed errors for better debugging
- Provide meaningful error messages to users
- Log errors for monitoring and analysis

### 2. Performance Considerations
- Debounce and throttle API calls
- Implement request deduplication
- Use background updates for better UX
- Cache responses appropriately

### 3. State Consistency
- Use optimistic updates carefully
- Implement proper rollback mechanisms
- Handle race conditions explicitly
- Maintain data integrity

### 4. Testing Strategy
- Mock external dependencies
- Test error scenarios
- Verify state transitions
- Use integration tests for complex flows

### 5. Monitoring and Debugging
- Implement proper logging
- Use development tools effectively
- Monitor performance metrics
- Track error rates and patterns

## Conclusion

Advanced async state management requires careful consideration of error handling, performance, and user experience. The patterns and techniques covered in this guide provide a foundation for building robust, scalable applications that handle complex async scenarios gracefully.

Key takeaways:
- Choose the right tool for your specific use case
- Implement proper error boundaries and recovery
- Optimize for performance and user experience
- Test thoroughly, especially error scenarios
- Monitor and maintain your async state management
