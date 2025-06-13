# Performance State Optimization

## Table of Contents
1. [Introduction](#introduction)
2. [State Structure Optimization](#state-structure-optimization)
3. [Selector Performance](#selector-performance)
4. [Memoization Strategies](#memoization-strategies)
5. [Bundle Size Optimization](#bundle-size-optimization)
6. [Memory Management](#memory-management)
7. [Concurrent Rendering](#concurrent-rendering)
8. [State Persistence](#state-persistence)
9. [Monitoring and Profiling](#monitoring-and-profiling)
10. [Best Practices](#best-practices)

## Introduction

Performance optimization in state management goes beyond just making things fast. It's about creating sustainable, scalable architectures that maintain responsiveness as your application grows in complexity and data volume.

### Performance Considerations

```javascript
// Performance anti-patterns to avoid
const BadStateExample = {
  // 1. Deeply nested objects (hard to update)
  user: {
    profile: {
      personal: {
        details: {
          name: 'John',
          email: 'john@example.com',
          address: {
            street: '123 Main St',
            city: 'Anytown'
          }
        }
      }
    }
  },
  
  // 2. Arrays without keys/IDs (expensive updates)
  posts: [
    { title: 'Post 1', content: '...' },
    { title: 'Post 2', content: '...' }
  ],
  
  // 3. Derived data in state (should be computed)
  postsCount: 2,
  hasUnreadPosts: true,
  
  // 4. UI state mixed with domain data
  isModalOpen: false,
  selectedPostId: null
}

// Optimized state structure
const OptimizedStateExample = {
  // 1. Normalized, flat structure
  entities: {
    users: {
      byId: {
        '1': { id: '1', name: 'John', email: 'john@example.com' }
      },
      allIds: ['1']
    },
    posts: {
      byId: {
        '1': { id: '1', userId: '1', title: 'Post 1', content: '...' },
        '2': { id: '2', userId: '1', title: 'Post 2', content: '...' }
      },
      allIds: ['1', '2']
    }
  },
  
  // 2. Separate UI state
  ui: {
    modals: {
      postEditor: { isOpen: false, postId: null }
    },
    loading: {
      posts: false,
      users: false
    }
  }
}
```

## State Structure Optimization

### Normalization Patterns

```javascript
// Normalization utility
function normalize(data, schema) {
  const entities = {}
  const result = []

  function processEntity(entity, entitySchema) {
    const { id, ...attributes } = entity
    
    if (!entities[entitySchema.name]) {
      entities[entitySchema.name] = { byId: {}, allIds: [] }
    }

    entities[entitySchema.name].byId[id] = {
      id,
      ...Object.keys(attributes).reduce((acc, key) => {
        const value = attributes[key]
        const fieldSchema = entitySchema.fields[key]

        if (fieldSchema && Array.isArray(value)) {
          acc[key] = value.map(item => 
            typeof item === 'object' && item.id 
              ? processEntity(item, fieldSchema.schema)
              : item
          )
        } else if (fieldSchema && typeof value === 'object' && value.id) {
          acc[key] = processEntity(value, fieldSchema.schema)
        } else {
          acc[key] = value
        }

        return acc
      }, {})
    }

    if (!entities[entitySchema.name].allIds.includes(id)) {
      entities[entitySchema.name].allIds.push(id)
    }

    return id
  }

  if (Array.isArray(data)) {
    result.push(...data.map(item => processEntity(item, schema)))
  } else {
    result.push(processEntity(data, schema))
  }

  return { entities, result }
}

// Usage example
const userSchema = {
  name: 'users',
  fields: {
    posts: {
      schema: {
        name: 'posts',
        fields: {}
      }
    }
  }
}

const rawData = {
  id: '1',
  name: 'John',
  posts: [
    { id: '1', title: 'First Post' },
    { id: '2', title: 'Second Post' }
  ]
}

const { entities, result } = normalize(rawData, userSchema)
```

### State Slicing

```javascript
// Feature-based state slicing
const createFeatureSlice = (name, initialState, reducers) => {
  const actionCreators = {}
  const actionTypes = {}

  Object.keys(reducers).forEach(reducerName => {
    const actionType = `${name}/${reducerName}`
    actionTypes[reducerName] = actionType
    actionCreators[reducerName] = (payload) => ({
      type: actionType,
      payload
    })
  })

  const reducer = (state = initialState, action) => {
    const reducer = Object.keys(reducers).find(key => 
      actionTypes[key] === action.type
    )
    
    if (reducer) {
      return reducers[reducer](state, action)
    }
    
    return state
  }

  return {
    name,
    reducer,
    actions: actionCreators,
    actionTypes
  }
}

// User slice
const userSlice = createFeatureSlice('user', {
  currentUser: null,
  isAuthenticated: false,
  loading: false
}, {
  setCurrentUser: (state, action) => ({
    ...state,
    currentUser: action.payload,
    isAuthenticated: true
  }),
  clearCurrentUser: (state) => ({
    ...state,
    currentUser: null,
    isAuthenticated: false
  }),
  setLoading: (state, action) => ({
    ...state,
    loading: action.payload
  })
})

// Posts slice
const postsSlice = createFeatureSlice('posts', {
  byId: {},
  allIds: [],
  loading: false,
  error: null
}, {
  addPost: (state, action) => {
    const post = action.payload
    return {
      ...state,
      byId: { ...state.byId, [post.id]: post },
      allIds: state.allIds.includes(post.id) 
        ? state.allIds 
        : [...state.allIds, post.id]
    }
  },
  updatePost: (state, action) => {
    const { id, updates } = action.payload
    return {
      ...state,
      byId: {
        ...state.byId,
        [id]: { ...state.byId[id], ...updates }
      }
    }
  },
  removePost: (state, action) => {
    const id = action.payload
    const { [id]: removed, ...remainingPosts } = state.byId
    return {
      ...state,
      byId: remainingPosts,
      allIds: state.allIds.filter(postId => postId !== id)
    }
  }
})
```

## Selector Performance

### Memoized Selectors

```javascript
import { createSelector } from 'reselect'

// Basic selectors
const selectUsers = (state) => state.entities.users
const selectPosts = (state) => state.entities.posts
const selectCurrentUserId = (state) => state.auth.currentUserId

// Memoized derived selectors
const selectAllUsers = createSelector(
  [selectUsers],
  (users) => users.allIds.map(id => users.byId[id])
)

const selectAllPosts = createSelector(
  [selectPosts],
  (posts) => posts.allIds.map(id => posts.byId[id])
)

const selectCurrentUser = createSelector(
  [selectUsers, selectCurrentUserId],
  (users, currentUserId) => 
    currentUserId ? users.byId[currentUserId] : null
)

const selectPostsByUser = createSelector(
  [selectAllPosts, (state, userId) => userId],
  (posts, userId) => posts.filter(post => post.userId === userId)
)

const selectCurrentUserPosts = createSelector(
  [selectAllPosts, selectCurrentUserId],
  (posts, currentUserId) => 
    posts.filter(post => post.userId === currentUserId)
)

// Complex derived data
const selectPostStats = createSelector(
  [selectAllPosts],
  (posts) => {
    const now = Date.now()
    const oneWeekAgo = now - (7 * 24 * 60 * 60 * 1000)
    
    return {
      total: posts.length,
      published: posts.filter(post => post.status === 'published').length,
      drafts: posts.filter(post => post.status === 'draft').length,
      recentPosts: posts.filter(post => 
        new Date(post.createdAt).getTime() > oneWeekAgo
      ).length
    }
  }
)

// Parametric selectors factory
const makeSelectPostsByTag = () => createSelector(
  [selectAllPosts, (state, tag) => tag],
  (posts, tag) => posts.filter(post => 
    post.tags && post.tags.includes(tag)
  )
)

// Usage in component
function PostsByTag({ tag }) {
  const selectPostsByTag = useMemo(makeSelectPostsByTag, [])
  const posts = useSelector(state => selectPostsByTag(state, tag))
  
  return (
    <div>
      {posts.map(post => (
        <PostItem key={post.id} post={post} />
      ))}
    </div>
  )
}
```

### Advanced Selector Patterns

```javascript
// Selector composition
const selectPostsWithAuthors = createSelector(
  [selectAllPosts, selectUsers],
  (posts, users) => posts.map(post => ({
    ...post,
    author: users.byId[post.userId]
  }))
)

// Selector with multiple parameters
const selectFilteredAndSortedPosts = createSelector(
  [
    selectAllPosts,
    (state, filters) => filters,
    (state, filters, sortBy) => sortBy
  ],
  (posts, filters, sortBy) => {
    let filteredPosts = posts

    // Apply filters
    if (filters.status) {
      filteredPosts = filteredPosts.filter(post => 
        post.status === filters.status
      )
    }

    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      filteredPosts = filteredPosts.filter(post =>
        post.title.toLowerCase().includes(searchLower) ||
        post.content.toLowerCase().includes(searchLower)
      )
    }

    if (filters.tags && filters.tags.length > 0) {
      filteredPosts = filteredPosts.filter(post =>
        filters.tags.some(tag => post.tags.includes(tag))
      )
    }

    // Apply sorting
    switch (sortBy) {
      case 'title':
        return filteredPosts.sort((a, b) => a.title.localeCompare(b.title))
      case 'date':
        return filteredPosts.sort((a, b) => 
          new Date(b.createdAt) - new Date(a.createdAt)
        )
      case 'popularity':
        return filteredPosts.sort((a, b) => (b.likes || 0) - (a.likes || 0))
      default:
        return filteredPosts
    }
  }
)

// Tree-structured selectors for hierarchical data
const selectCategoriesTree = createSelector(
  [selectCategories],
  (categories) => {
    const categoriesMap = new Map()
    const rootCategories = []

    // First pass: create map and identify roots
    categories.forEach(category => {
      categoriesMap.set(category.id, { ...category, children: [] })
      if (!category.parentId) {
        rootCategories.push(category.id)
      }
    })

    // Second pass: build tree structure
    categories.forEach(category => {
      if (category.parentId) {
        const parent = categoriesMap.get(category.parentId)
        const child = categoriesMap.get(category.id)
        if (parent && child) {
          parent.children.push(child)
        }
      }
    })

    return rootCategories.map(id => categoriesMap.get(id))
  }
)
```

## Memoization Strategies

### Component-Level Memoization

```javascript
// Smart memoization with React.memo
const PostItem = React.memo(({ post, onEdit, onDelete }) => {
  const handleEdit = useCallback(() => {
    onEdit(post.id)
  }, [post.id, onEdit])

  const handleDelete = useCallback(() => {
    onDelete(post.id)
  }, [post.id, onDelete])

  return (
    <article className="post-item">
      <h3>{post.title}</h3>
      <p>{post.excerpt}</p>
      <div className="post-actions">
        <button onClick={handleEdit}>Edit</button>
        <button onClick={handleDelete}>Delete</button>
      </div>
    </article>
  )
}, (prevProps, nextProps) => {
  // Custom comparison function
  return (
    prevProps.post.id === nextProps.post.id &&
    prevProps.post.title === nextProps.post.title &&
    prevProps.post.excerpt === nextProps.post.excerpt &&
    prevProps.post.updatedAt === nextProps.post.updatedAt
  )
})

// Memoized list component
const PostList = React.memo(({ posts, onEditPost, onDeletePost }) => {
  const memoizedOnEdit = useCallback((postId) => {
    onEditPost(postId)
  }, [onEditPost])

  const memoizedOnDelete = useCallback((postId) => {
    onDeletePost(postId)
  }, [onDeletePost])

  return (
    <div className="post-list">
      {posts.map(post => (
        <PostItem
          key={post.id}
          post={post}
          onEdit={memoizedOnEdit}
          onDelete={memoizedOnDelete}
        />
      ))}
    </div>
  )
})

// Container component with optimal state selection
function PostListContainer() {
  const posts = useSelector(selectVisiblePosts)
  const dispatch = useDispatch()

  const handleEditPost = useCallback((postId) => {
    dispatch(openPostEditor(postId))
  }, [dispatch])

  const handleDeletePost = useCallback((postId) => {
    dispatch(deletePost(postId))
  }, [dispatch])

  return (
    <PostList
      posts={posts}
      onEditPost={handleEditPost}
      onDeletePost={handleDeletePost}
    />
  )
}
```

### Hook Memoization

```javascript
// Memoized data fetching hook
function useOptimizedPosts(filters, sortBy) {
  const selectFilteredPosts = useMemo(
    () => createSelector(
      [selectAllPosts],
      (posts) => {
        // Apply filters and sorting
        let result = posts

        if (filters.status) {
          result = result.filter(post => post.status === filters.status)
        }

        if (filters.search) {
          const searchTerm = filters.search.toLowerCase()
          result = result.filter(post =>
            post.title.toLowerCase().includes(searchTerm)
          )
        }

        // Sort
        switch (sortBy) {
          case 'date':
            result = result.sort((a, b) => 
              new Date(b.createdAt) - new Date(a.createdAt)
            )
            break
          case 'title':
            result = result.sort((a, b) => a.title.localeCompare(b.title))
            break
        }

        return result
      }
    ),
    [filters.status, filters.search, sortBy]
  )

  const posts = useSelector(selectFilteredPosts)
  const loading = useSelector(selectPostsLoading)
  const error = useSelector(selectPostsError)

  return { posts, loading, error }
}

// Memoized computed values hook
function usePostStatistics() {
  const stats = useSelector(selectPostStats)
  
  const chartData = useMemo(() => ({
    labels: ['Published', 'Drafts', 'Archived'],
    datasets: [{
      data: [stats.published, stats.drafts, stats.archived],
      backgroundColor: ['#10B981', '#F59E0B', '#6B7280']
    }]
  }), [stats.published, stats.drafts, stats.archived])

  const summaryText = useMemo(() => 
    `You have ${stats.total} posts total: ${stats.published} published, ${stats.drafts} drafts, and ${stats.archived} archived.`,
    [stats.total, stats.published, stats.drafts, stats.archived]
  )

  return { stats, chartData, summaryText }
}
```

## Bundle Size Optimization

### Code Splitting for State Management

```javascript
// Lazy-loaded state slices
const createAsyncSlice = (sliceName, importFn) => {
  return {
    [sliceName]: (state = null, action) => {
      // Placeholder reducer until slice is loaded
      if (action.type === `${sliceName}/SLICE_LOADED`) {
        return action.payload.initialState
      }
      return state
    }
  }
}

// Dynamic slice loading
async function loadSlice(sliceName) {
  const sliceModule = await import(`./slices/${sliceName}Slice`)
  const slice = sliceModule.default
  
  // Replace placeholder reducer
  store.replaceReducer(combineReducers({
    ...store.getState(),
    [sliceName]: slice.reducer
  }))
  
  // Initialize state
  store.dispatch({
    type: `${sliceName}/SLICE_LOADED`,
    payload: { initialState: slice.initialState }
  })
  
  return slice
}

// Route-based code splitting
const AdminRoutes = lazy(() => import('./routes/AdminRoutes'))
const AdminStateProvider = lazy(() => 
  import('./state/AdminStateProvider').then(module => ({
    default: module.AdminStateProvider
  }))
)

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/admin/*" element={
          <Suspense fallback={<div>Loading admin...</div>}>
            <AdminStateProvider>
              <AdminRoutes />
            </AdminStateProvider>
          </Suspense>
        } />
      </Routes>
    </Router>
  )
}
```

### Tree Shaking Optimization

```javascript
// Optimized imports
// ❌ Bad - imports entire library
import * as Redux from 'redux'
import * as ReactRedux from 'react-redux'

// ✅ Good - only imports needed functions
import { createStore, combineReducers } from 'redux'
import { useSelector, useDispatch } from 'react-redux'

// Library-specific optimizations
// ❌ Bad - imports entire lodash
import _ from 'lodash'

// ✅ Good - imports specific functions
import debounce from 'lodash/debounce'
import memoize from 'lodash/memoize'

// Custom utility functions for better tree shaking
const createOptimizedSelector = (dependencies, computeFn) => {
  let lastDependencies = []
  let lastResult = null

  return (...args) => {
    const currentDependencies = dependencies.map(dep => 
      typeof dep === 'function' ? dep(...args) : dep
    )

    const hasChanged = currentDependencies.some((dep, index) => 
      dep !== lastDependencies[index]
    )

    if (hasChanged) {
      lastResult = computeFn(...currentDependencies)
      lastDependencies = currentDependencies
    }

    return lastResult
  }
}
```

## Memory Management

### Preventing Memory Leaks

```javascript
// Cleanup patterns for state subscriptions
function useStateSubscription(selector, callback) {
  const selectorRef = useRef(selector)
  const callbackRef = useRef(callback)
  
  // Update refs without causing re-renders
  selectorRef.current = selector
  callbackRef.current = callback

  useEffect(() => {
    let lastValue = selectorRef.current(store.getState())
    
    const unsubscribe = store.subscribe(() => {
      const currentValue = selectorRef.current(store.getState())
      
      if (currentValue !== lastValue) {
        callbackRef.current(currentValue, lastValue)
        lastValue = currentValue
      }
    })

    return unsubscribe
  }, [])
}

// WeakMap-based caching to prevent memory leaks
const selectorCache = new WeakMap()

const createCachedSelector = (selector) => {
  return (state) => {
    if (selectorCache.has(state)) {
      return selectorCache.get(state)
    }
    
    const result = selector(state)
    selectorCache.set(state, result)
    return result
  }
}

// Cleanup for large data sets
const useLargeDataSet = (dataKey) => {
  const [data, setData] = useState(null)
  const cleanupRef = useRef(null)

  useEffect(() => {
    // Load large data
    loadLargeDataSet(dataKey).then(result => {
      setData(result)
      
      // Set up cleanup
      cleanupRef.current = () => {
        // Clear large objects
        result.items = null
        result.cache = null
        setData(null)
      }
    })

    return () => {
      if (cleanupRef.current) {
        cleanupRef.current()
      }
    }
  }, [dataKey])

  // Cleanup on memory pressure
  useEffect(() => {
    const handleMemoryPressure = () => {
      if (cleanupRef.current) {
        cleanupRef.current()
      }
    }

    // Listen for memory pressure events (where supported)
    if ('memory' in performance) {
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
          setTimeout(handleMemoryPressure, 30000) // Cleanup after 30s
        }
      })
    }

    return () => {
      document.removeEventListener('visibilitychange', handleMemoryPressure)
    }
  }, [])

  return data
}
```

### State Cleanup Strategies

```javascript
// Automatic state cleanup middleware
const createCleanupMiddleware = (config = {}) => {
  const {
    maxAge = 300000, // 5 minutes
    maxSize = 1000,
    cleanupInterval = 60000 // 1 minute
  } = config

  const stateTimestamps = new Map()
  const stateAccessCount = new Map()

  // Periodic cleanup
  setInterval(() => {
    const now = Date.now()
    
    stateTimestamps.forEach((timestamp, key) => {
      if (now - timestamp > maxAge) {
        stateTimestamps.delete(key)
        stateAccessCount.delete(key)
        
        // Dispatch cleanup action
        store.dispatch({
          type: 'CLEANUP_STATE_SLICE',
          payload: { key }
        })
      }
    })
  }, cleanupInterval)

  return (store) => (next) => (action) => {
    const result = next(action)
    
    // Track state access
    if (action.type.includes('REQUEST') || action.type.includes('SUCCESS')) {
      const key = action.type.split('/')[0]
      stateTimestamps.set(key, Date.now())
      stateAccessCount.set(key, (stateAccessCount.get(key) || 0) + 1)
    }

    return result
  }
}

// Component-level cleanup
function useComponentStateCleanup(componentId) {
  const dispatch = useDispatch()

  useEffect(() => {
    return () => {
      // Cleanup component-specific state
      dispatch({
        type: 'CLEANUP_COMPONENT_STATE',
        payload: { componentId }
      })
    }
  }, [componentId, dispatch])
}

// LRU cache for computed values
class LRUCache {
  constructor(maxSize = 100) {
    this.maxSize = maxSize
    this.cache = new Map()
  }

  get(key) {
    if (this.cache.has(key)) {
      const value = this.cache.get(key)
      // Move to end (most recent)
      this.cache.delete(key)
      this.cache.set(key, value)
      return value
    }
    return undefined
  }

  set(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key)
    } else if (this.cache.size >= this.maxSize) {
      // Remove least recently used
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    this.cache.set(key, value)
  }

  clear() {
    this.cache.clear()
  }
}

const selectorLRUCache = new LRUCache(50)

const createLRUCachedSelector = (selector, keyFn) => {
  return (...args) => {
    const key = keyFn ? keyFn(...args) : JSON.stringify(args)
    
    let cached = selectorLRUCache.get(key)
    if (cached === undefined) {
      cached = selector(...args)
      selectorLRUCache.set(key, cached)
    }
    
    return cached
  }
}
```

## Concurrent Rendering

### React 18+ Optimizations

```javascript
// Transition-aware state updates
function useTransitionState(initialState) {
  const [state, setState] = useState(initialState)
  const [isPending, startTransition] = useTransition()

  const setStateWithTransition = useCallback((newState) => {
    startTransition(() => {
      setState(newState)
    })
  }, [])

  return [state, setStateWithTransition, isPending]
}

// Deferred state updates for large lists
function useDeferredFiltering(data, filters) {
  const deferredFilters = useDeferredValue(filters)
  
  const filteredData = useMemo(() => {
    return data.filter(item => {
      return Object.entries(deferredFilters).every(([key, value]) => {
        if (!value) return true
        return item[key]?.toString().toLowerCase().includes(value.toLowerCase())
      })
    })
  }, [data, deferredFilters])

  return filteredData
}

// Concurrent-safe state updates
const createConcurrentSafeReducer = (reducer) => {
  return (state, action) => {
    // Use startTransition for non-urgent updates
    if (action.meta?.concurrent) {
      return state // Return current state, update will be deferred
    }
    
    return reducer(state, action)
  }
}

// Suspense-compatible data fetching
function SuspenseDataProvider({ children, dataKey }) {
  const data = use(fetchData(dataKey)) // React 18 use() hook
  
  return (
    <DataContext.Provider value={data}>
      {children}
    </DataContext.Provider>
  )
}

function DataBoundaryWithSuspense({ children, dataKey }) {
  return (
    <ErrorBoundary fallback={<ErrorDisplay />}>
      <Suspense fallback={<LoadingSpinner />}>
        <SuspenseDataProvider dataKey={dataKey}>
          {children}
        </SuspenseDataProvider>
      </Suspense>
    </ErrorBoundary>
  )
}
```

### Optimistic Updates with Concurrent Features

```javascript
// Concurrent-aware optimistic updates
function useOptimisticMutation(mutationFn, options = {}) {
  const [optimisticState, setOptimisticState] = useState(null)
  const [isPending, startTransition] = useTransition()
  
  const mutate = useCallback(async (variables) => {
    // Apply optimistic update
    if (options.optimisticUpdate) {
      startTransition(() => {
        setOptimisticState(options.optimisticUpdate(variables))
      })
    }

    try {
      const result = await mutationFn(variables)
      
      // Clear optimistic state on success
      startTransition(() => {
        setOptimisticState(null)
      })
      
      return result
    } catch (error) {
      // Revert optimistic state on error
      startTransition(() => {
        setOptimisticState(null)
      })
      
      throw error
    }
  }, [mutationFn, options.optimisticUpdate])

  return {
    mutate,
    isPending,
    optimisticState
  }
}

// High-priority vs low-priority updates
function usePriorityUpdates() {
  const [urgentData, setUrgentData] = useState(null)
  const [deferredData, setDeferredData] = useState(null)

  const updateUrgent = useCallback((data) => {
    // High priority - update immediately
    setUrgentData(data)
  }, [])

  const updateDeferred = useCallback((data) => {
    // Low priority - can be interrupted
    startTransition(() => {
      setDeferredData(data)
    })
  }, [])

  return {
    urgentData,
    deferredData,
    updateUrgent,
    updateDeferred
  }
}
```

## State Persistence

### Selective Persistence

```javascript
// Configurable persistence
const createPersistenceConfig = (config) => {
  const {
    key = 'app-state',
    storage = localStorage,
    whitelist = [],
    blacklist = [],
    transforms = {},
    debounceMs = 1000
  } = config

  const shouldPersist = (stateKey) => {
    if (blacklist.includes(stateKey)) return false
    if (whitelist.length > 0) return whitelist.includes(stateKey)
    return true
  }

  const persistState = debounce((state) => {
    const stateToPersist = Object.keys(state)
      .filter(shouldPersist)
      .reduce((acc, key) => {
        let value = state[key]
        
        // Apply transforms
        if (transforms[key]?.serialize) {
          value = transforms[key].serialize(value)
        }
        
        acc[key] = value
        return acc
      }, {})

    try {
      storage.setItem(key, JSON.stringify(stateToPersist))
    } catch (error) {
      console.warn('Failed to persist state:', error)
    }
  }, debounceMs)

  const loadPersistedState = () => {
    try {
      const persistedData = storage.getItem(key)
      if (!persistedData) return {}

      const parsed = JSON.parse(persistedData)
      
      // Apply transforms
      Object.keys(parsed).forEach(stateKey => {
        if (transforms[stateKey]?.deserialize) {
          parsed[stateKey] = transforms[stateKey].deserialize(parsed[stateKey])
        }
      })

      return parsed
    } catch (error) {
      console.warn('Failed to load persisted state:', error)
      return {}
    }
  }

  return { persistState, loadPersistedState }
}

// Usage example
const persistenceConfig = createPersistenceConfig({
  key: 'my-app-state',
  whitelist: ['user', 'preferences', 'drafts'],
  blacklist: ['ui', 'network'],
  transforms: {
    drafts: {
      serialize: (drafts) => ({
        ...drafts,
        // Don't persist temporary data
        tempData: undefined
      }),
      deserialize: (drafts) => ({
        ...drafts,
        // Restore default temp data
        tempData: {}
      })
    }
  },
  debounceMs: 2000
})

// Middleware for automatic persistence
const createPersistenceMiddleware = (persistenceConfig) => {
  const { persistState } = persistenceConfig

  return (store) => (next) => (action) => {
    const result = next(action)
    
    // Don't persist on every action, only on significant changes
    if (!action.type.includes('TEMPORARY') && !action.type.includes('UI')) {
      persistState(store.getState())
    }
    
    return result
  }
}
```

### Version Management

```javascript
// State migration system
const migrations = {
  1: (state) => {
    // Migration from version 0 to 1
    return {
      ...state,
      version: 1,
      user: {
        ...state.user,
        preferences: state.user.settings // Rename settings to preferences
      }
    }
  },
  2: (state) => {
    // Migration from version 1 to 2
    return {
      ...state,
      version: 2,
      posts: {
        byId: state.posts.reduce((acc, post) => {
          acc[post.id] = post
          return acc
        }, {}),
        allIds: state.posts.map(post => post.id)
      }
    }
  }
}

const migrateState = (persistedState) => {
  const currentVersion = 2 // Current app version
  let state = persistedState
  let version = state.version || 0

  while (version < currentVersion) {
    const nextVersion = version + 1
    if (migrations[nextVersion]) {
      console.log(`Migrating state from version ${version} to ${nextVersion}`)
      state = migrations[nextVersion](state)
      version = nextVersion
    } else {
      console.warn(`No migration found for version ${nextVersion}`)
      break
    }
  }

  return state
}

// Load state with migration
const loadStateWithMigration = () => {
  const persistedState = loadPersistedState()
  
  if (Object.keys(persistedState).length === 0) {
    return {} // No persisted state
  }

  return migrateState(persistedState)
}
```

## Monitoring and Profiling

### Performance Monitoring

```javascript
// Performance metrics collection
class StatePerformanceMonitor {
  constructor() {
    this.metrics = {
      actionCounts: new Map(),
      actionTimes: new Map(),
      selectorTimes: new Map(),
      reRenderCounts: new Map()
    }
  }

  startActionTimer(actionType) {
    this.metrics.actionTimes.set(actionType, performance.now())
  }

  endActionTimer(actionType) {
    const startTime = this.metrics.actionTimes.get(actionType)
    if (startTime) {
      const duration = performance.now() - startTime
      
      console.log(`Action ${actionType} took ${duration.toFixed(2)}ms`)
      
      if (duration > 16) { // Longer than one frame
        console.warn(`Slow action detected: ${actionType}`)
      }
    }
  }

  trackActionCount(actionType) {
    const current = this.metrics.actionCounts.get(actionType) || 0
    this.metrics.actionCounts.set(actionType, current + 1)
  }

  trackSelectorPerformance(selectorName, startTime) {
    const duration = performance.now() - startTime
    
    if (!this.metrics.selectorTimes.has(selectorName)) {
      this.metrics.selectorTimes.set(selectorName, [])
    }
    
    this.metrics.selectorTimes.get(selectorName).push(duration)
    
    if (duration > 5) { // Selector taking longer than 5ms
      console.warn(`Slow selector: ${selectorName} (${duration.toFixed(2)}ms)`)
    }
  }

  getMetrics() {
    const selectorAverages = new Map()
    
    this.metrics.selectorTimes.forEach((times, selector) => {
      const average = times.reduce((a, b) => a + b, 0) / times.length
      selectorAverages.set(selector, average)
    })

    return {
      actionCounts: Object.fromEntries(this.metrics.actionCounts),
      selectorAverages: Object.fromEntries(selectorAverages),
      reRenderCounts: Object.fromEntries(this.metrics.reRenderCounts)
    }
  }
}

const performanceMonitor = new StatePerformanceMonitor()

// Monitoring middleware
const performanceMiddleware = (store) => (next) => (action) => {
  if (process.env.NODE_ENV === 'development') {
    performanceMonitor.trackActionCount(action.type)
    performanceMonitor.startActionTimer(action.type)
  }

  const result = next(action)

  if (process.env.NODE_ENV === 'development') {
    performanceMonitor.endActionTimer(action.type)
  }

  return result
}

// Monitored selector factory
const createMonitoredSelector = (name, selector) => {
  return (...args) => {
    if (process.env.NODE_ENV === 'development') {
      const startTime = performance.now()
      const result = selector(...args)
      performanceMonitor.trackSelectorPerformance(name, startTime)
      return result
    }
    
    return selector(...args)
  }
}
```

### React DevTools Integration

```javascript
// Enhanced Redux DevTools configuration
const configureDevtools = () => {
  if (process.env.NODE_ENV === 'development' && window.__REDUX_DEVTOOLS_EXTENSION__) {
    return window.__REDUX_DEVTOOLS_EXTENSION__({
      name: 'My App',
      trace: true,
      traceLimit: 25,
      actionSanitizer: (action) => ({
        ...action,
        // Sanitize sensitive data
        payload: action.type.includes('AUTH') 
          ? '***SANITIZED***' 
          : action.payload
      }),
      stateSanitizer: (state) => ({
        ...state,
        // Hide sensitive data
        auth: state.auth ? { ...state.auth, token: '***' } : state.auth
      }),
      actionCreators: {
        // Add action creators for easier testing
        ...userActions,
        ...postActions
      }
    })
  }
  
  return undefined
}

// Performance profiling with React DevTools
function ProfiledComponent({ children }) {
  const [profileId] = useState(() => `profile-${Date.now()}`)

  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.time(profileId)
      return () => console.timeEnd(profileId)
    }
  }, [profileId])

  return (
    <Profiler
      id={profileId}
      onRender={(id, phase, actualDuration, baseDuration, startTime, commitTime) => {
        if (actualDuration > 16) { // Longer than one frame
          console.warn(`Slow render detected in ${id}:`, {
            phase,
            actualDuration,
            baseDuration,
            startTime,
            commitTime
          })
        }
      }}
    >
      {children}
    </Profiler>
  )
}
```

## Best Practices

### 1. State Structure
- Normalize data to avoid deep nesting
- Separate domain data from UI state
- Use consistent naming conventions
- Keep state minimal and derive when possible

### 2. Selector Optimization
- Use memoized selectors for expensive computations
- Avoid creating selectors in render functions
- Cache parametric selectors appropriately
- Monitor selector performance in development

### 3. Component Performance
- Use React.memo for components that re-render frequently
- Memoize callbacks and expensive calculations
- Split large components into smaller, focused ones
- Use concurrent features for non-critical updates

### 4. Memory Management
- Clean up subscriptions and timers
- Use WeakMap for caching when appropriate
- Implement state cleanup for unused data
- Monitor memory usage in production

### 5. Monitoring and Debugging
- Use performance profiling tools
- Monitor action frequency and timing
- Track component re-render counts
- Implement error boundaries for state operations

## Conclusion

Performance optimization in state management is an ongoing process that requires careful attention to both the technical implementation and the user experience. By following these patterns and practices, you can build state management solutions that scale efficiently and provide excellent performance even with complex data requirements.

Key optimization areas:
- **Structure**: Normalize and organize state for efficient updates
- **Selection**: Use memoized selectors to avoid unnecessary computations
- **Rendering**: Optimize React components to minimize re-renders
- **Memory**: Manage memory usage and prevent leaks
- **Monitoring**: Track performance metrics and identify bottlenecks

Remember that premature optimization can be counterproductive. Always measure performance before and after optimizations to ensure they provide real benefits.
