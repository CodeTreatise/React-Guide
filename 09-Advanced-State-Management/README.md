# Module 9: Advanced State Management

## Learning Objectives
By the end of this module, you will be able to:
- Master complex state management patterns in React applications
- Implement advanced Redux patterns with middleware and selectors
- Build reactive state management with RxJS and observables
- Create type-safe state management with TypeScript
- Implement state persistence and hydration strategies
- Design scalable state architectures for large applications
- Optimize state management performance
- Handle complex async state scenarios

## Overview
This module covers advanced state management concepts that go beyond basic Redux and Context API. You'll learn enterprise-level patterns, performance optimization techniques, and how to architect state for complex applications.

## Duration: Week 9 (40 hours)
- **Reading & Research**: 10 hours
- **Hands-on Practice**: 20 hours
- **Projects**: 8 hours
- **Assessment**: 2 hours

---

## Topics Covered

### 1. Advanced Redux Patterns
```javascript
{% raw %}
// Redux Toolkit Query (RTK Query) for data fetching
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/',
    prepareHeaders: (headers, { getState }) => {
      const token = getState().auth.token
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['Post', 'User'],
  endpoints: (builder) => ({
    getPosts: builder.query({
      query: () => 'posts',
      providesTags: ['Post'],
    }),
    getPost: builder.query({
      query: (id) => `posts/${id}`,
      providesTags: (result, error, id) => [{ type: 'Post', id }],
    }),
    addPost: builder.mutation({
      query: (newPost) => ({
        url: 'posts',
        method: 'POST',
        body: newPost,
      }),
      invalidatesTags: ['Post'],
    }),
  }),
})

export const { useGetPostsQuery, useGetPostQuery, useAddPostMutation } = api
{% endraw %}
```

### 2. Normalized State Structure
```javascript
// Entity normalization with Redux Toolkit
import { createEntityAdapter, createSlice } from '@reduxjs/toolkit'

const postsAdapter = createEntityAdapter({
  selectId: (post) => post.id,
  sortComparer: (a, b) => b.date.localeCompare(a.date),
})

const postsSlice = createSlice({
  name: 'posts',
  initialState: postsAdapter.getInitialState({
    loading: false,
    error: null,
  }),
  reducers: {
    postAdded: postsAdapter.addOne,
    postUpdated: postsAdapter.updateOne,
    postRemoved: postsAdapter.removeOne,
    postsReceived: (state, action) => {
      postsAdapter.setAll(state, action.payload)
    },
  },
})

// Selectors
export const {
  selectAll: selectAllPosts,
  selectById: selectPostById,
  selectIds: selectPostIds,
} = postsAdapter.getSelectors((state) => state.posts)
```

### 3. Reactive State Management with RxJS
```javascript
import { BehaviorSubject, combineLatest } from 'rxjs'
import { map, distinctUntilChanged } from 'rxjs/operators'

// Observable-based state management
class AppStateManager {
  private userSubject = new BehaviorSubject(null)
  private settingsSubject = new BehaviorSubject({})
  private notificationsSubject = new BehaviorSubject([])

  // Computed state streams
  user$ = this.userSubject.asObservable()
  settings$ = this.settingsSubject.asObservable()
  notifications$ = this.notificationsSubject.asObservable()

  // Derived state
  isAuthenticated$ = this.user$.pipe(
    map(user => !!user),
    distinctUntilChanged()
  )

  unreadCount$ = this.notifications$.pipe(
    map(notifications => notifications.filter(n => !n.read).length),
    distinctUntilChanged()
  )

  appState$ = combineLatest([
    this.user$,
    this.settings$,
    this.notifications$
  ]).pipe(
    map(([user, settings, notifications]) => ({
      user,
      settings,
      notifications,
      isAuthenticated: !!user,
      unreadCount: notifications.filter(n => !n.read).length
    }))
  )

  // Actions
  setUser(user) {
    this.userSubject.next(user)
  }

  updateSettings(settings) {
    this.settingsSubject.next({ ...this.settingsSubject.value, ...settings })
  }

  addNotification(notification) {
    const current = this.notificationsSubject.value
    this.notificationsSubject.next([...current, notification])
  }
}

// React hook for observable state
import { useObservableState } from 'observable-hooks'

function useAppState() {
  const appState = useObservableState(stateManager.appState$, {
    user: null,
    settings: {},
    notifications: [],
    isAuthenticated: false,
    unreadCount: 0
  })

  return {
    ...appState,
    setUser: stateManager.setUser.bind(stateManager),
    updateSettings: stateManager.updateSettings.bind(stateManager),
    addNotification: stateManager.addNotification.bind(stateManager),
  }
}
```

### 4. Type-Safe State Management with TypeScript
```typescript
// Advanced TypeScript patterns for state management
interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user' | 'moderator'
}

interface Post {
  id: string
  title: string
  content: string
  authorId: string
  createdAt: string
  tags: string[]
}

// Discriminated union for async states
type AsyncState<T, E = string> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: E }

// Type-safe state structure
interface AppState {
  auth: {
    user: User | null
    token: string | null
    isAuthenticated: boolean
  }
  posts: {
    items: Record<string, Post>
    ids: string[]
    currentPost: AsyncState<Post>
    list: AsyncState<Post[]>
  }
  ui: {
    theme: 'light' | 'dark'
    sidebar: {
      isOpen: boolean
      activeTab: 'posts' | 'users' | 'settings'
    }
    notifications: {
      items: Notification[]
      position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
    }
  }
}

// Type-safe action creators
type Action<T extends string, P = void> = P extends void
  ? { type: T }
  : { type: T; payload: P }

type AuthActions =
  | Action<'AUTH_LOGIN_START'>
  | Action<'AUTH_LOGIN_SUCCESS', { user: User; token: string }>
  | Action<'AUTH_LOGIN_FAILURE', string>
  | Action<'AUTH_LOGOUT'>

type PostActions =
  | Action<'POSTS_FETCH_START'>
  | Action<'POSTS_FETCH_SUCCESS', Post[]>
  | Action<'POSTS_FETCH_FAILURE', string>
  | Action<'POST_ADD', Post>
  | Action<'POST_UPDATE', { id: string; updates: Partial<Post> }>
  | Action<'POST_DELETE', string>

type AppActions = AuthActions | PostActions

// Type-safe reducer
function appReducer(state: AppState, action: AppActions): AppState {
  switch (action.type) {
    case 'AUTH_LOGIN_SUCCESS':
      return {
        ...state,
        auth: {
          user: action.payload.user,
          token: action.payload.token,
          isAuthenticated: true,
        },
      }
    // ... other cases
    default:
      return state
  }
}
```

### 5. State Persistence and Hydration
```javascript
// Advanced persistence strategies
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { createTransform } from 'redux-persist'

// Transform for encrypting sensitive data
const encryptTransform = createTransform(
  // Transform state before persisting
  (inboundState, key) => {
    if (key === 'auth' && inboundState.token) {
      return {
        ...inboundState,
        token: encrypt(inboundState.token)
      }
    }
    return inboundState
  },
  // Transform state after rehydrating
  (outboundState, key) => {
    if (key === 'auth' && outboundState.token) {
      return {
        ...outboundState,
        token: decrypt(outboundState.token)
      }
    }
    return outboundState
  },
  { whitelist: ['auth'] }
)

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth', 'settings', 'preferences'],
  blacklist: ['temporaryData', 'cache'],
  transforms: [encryptTransform],
  migrate: (state) => {
    // Handle state migrations between app versions
    if (state && state._persist.version < 2) {
      return migrateToV2(state)
    }
    return Promise.resolve(state)
  },
}

const persistedReducer = persistReducer(persistConfig, rootReducer)

// Custom hydration hook
function useHydrationState() {
  const [isHydrated, setIsHydrated] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const persistor = persistStore(store, null, () => {
      setIsHydrated(true)
    })

    persistor.subscribe(() => {
      const state = persistor.getState()
      if (state.bootstrapped) {
        setIsHydrated(true)
      }
    })

    return () => persistor.pause()
  }, [])

  return { isHydrated, error }
}

// App wrapper with hydration
function App() {
  const { isHydrated } = useHydrationState()

  if (!isHydrated) {
    return <LoadingScreen />
  }

  return <MainApp />
}
```

### 6. State Machines with XState
```javascript
{% raw %}
import { createMachine, interpret } from 'xstate'

// Complex state machine for user authentication flow
const authMachine = createMachine({
  id: 'auth',
  initial: 'idle',
  context: {
    user: null,
    token: null,
    error: null,
    retries: 0,
  },
  states: {
    idle: {
      on: {
        LOGIN: 'authenticating',
        CHECK_AUTH: 'checking',
      },
    },
    checking: {
      invoke: {
        id: 'checkAuth',
        src: 'checkAuthService',
        onDone: {
          target: 'authenticated',
          actions: 'setUser',
        },
        onError: 'idle',
      },
    },
    authenticating: {
      invoke: {
        id: 'authenticate',
        src: 'authService',
        onDone: {
          target: 'authenticated',
          actions: 'setAuth',
        },
        onError: [
          {
            target: 'retrying',
            cond: 'shouldRetry',
            actions: 'incrementRetries',
          },
          {
            target: 'failed',
            actions: 'setError',
          },
        ],
      },
    },
    retrying: {
      after: {
        2000: 'authenticating',
      },
    },
    authenticated: {
      on: {
        LOGOUT: 'idle',
        REFRESH_TOKEN: 'refreshing',
      },
    },
    refreshing: {
      invoke: {
        id: 'refreshToken',
        src: 'refreshTokenService',
        onDone: {
          target: 'authenticated',
          actions: 'setToken',
        },
        onError: 'idle',
      },
    },
    failed: {
      on: {
        RETRY: 'authenticating',
        CANCEL: 'idle',
      },
    },
  },
}, {
  guards: {
    shouldRetry: (context) => context.retries < 3,
  },
  actions: {
    setUser: (context, event) => {
      context.user = event.data.user
      context.token = event.data.token
    },
    setAuth: (context, event) => {
      context.user = event.data.user
      context.token = event.data.token
      context.error = null
      context.retries = 0
    },
    setToken: (context, event) => {
      context.token = event.data.token
    },
    setError: (context, event) => {
      context.error = event.data
    },
    incrementRetries: (context) => {
      context.retries += 1
    },
  },
  services: {
    authService: (context, event) => {
      return fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(event.credentials),
      }).then(response => response.json())
    },
    checkAuthService: () => {
      return fetch('/api/auth/me').then(response => response.json())
    },
    refreshTokenService: (context) => {
      return fetch('/api/auth/refresh', {
        headers: {
          Authorization: `Bearer ${context.token}`,
        },
      }).then(response => response.json())
    },
  },
})

// React integration
import { useMachine } from '@xstate/react'

function useAuth() {
  const [state, send] = useMachine(authMachine)

  return {
    state: state.value,
    context: state.context,
    login: (credentials) => send({ type: 'LOGIN', credentials }),
    logout: () => send('LOGOUT'),
    checkAuth: () => send('CHECK_AUTH'),
    retry: () => send('RETRY'),
  }
}
{% endraw %}
```

### 7. Micro-Frontend State Management
```javascript
// Cross-application state sharing
class FederatedStateManager {
  constructor() {
    this.stores = new Map()
    this.subscribers = new Map()
    this.bridge = this.createBridge()
  }

  createBridge() {
    // Use postMessage for cross-origin communication
    window.addEventListener('message', (event) => {
      if (event.data.type === 'STATE_UPDATE') {
        this.handleExternalStateUpdate(event.data)
      }
    })

    return {
      send: (type, data) => {
        window.parent.postMessage({ type, data }, '*')
      },
      subscribe: (callback) => {
        this.subscribers.set(callback, true)
        return () => this.subscribers.delete(callback)
      },
    }
  }

  registerStore(name, store) {
    this.stores.set(name, store)
    
    // Sync store changes across micro-frontends
    store.subscribe(() => {
      const state = store.getState()
      this.bridge.send('STATE_UPDATE', {
        store: name,
        state: this.serializeState(state),
      })
    })
  }

  handleExternalStateUpdate({ store, state }) {
    if (this.stores.has(store)) {
      const localStore = this.stores.get(store)
      localStore.dispatch({
        type: 'EXTERNAL_STATE_UPDATE',
        payload: this.deserializeState(state),
      })
    }
  }

  serializeState(state) {
    // Custom serialization for complex objects
    return JSON.stringify(state, (key, value) => {
      if (value instanceof Date) {
        return { __type: 'Date', value: value.toISOString() }
      }
      if (value instanceof Map) {
        return { __type: 'Map', value: Array.from(value.entries()) }
      }
      return value
    })
  }

  deserializeState(serializedState) {
    return JSON.parse(serializedState, (key, value) => {
      if (value && value.__type === 'Date') {
        return new Date(value.value)
      }
      if (value && value.__type === 'Map') {
        return new Map(value.value)
      }
      return value
    })
  }
}

// Usage in micro-frontend
const federatedState = new FederatedStateManager()
federatedState.registerStore('user', userStore)
federatedState.registerStore('notifications', notificationStore)
```

### 8. Performance Optimization Strategies
```javascript
// Memoized selectors with reselect
import { createSelector, createSelectorCreator, defaultMemoize } from 'reselect'
import { isEqual } from 'lodash'

// Custom equality selector for deep comparisons
const createDeepEqualSelector = createSelectorCreator(
  defaultMemoize,
  isEqual
)

// Efficient selectors
const getUsers = (state) => state.users.items
const getActiveUserId = (state) => state.ui.activeUserId
const getFilters = (state) => state.users.filters

const getFilteredUsers = createSelector(
  [getUsers, getFilters],
  (users, filters) => {
    return Object.values(users).filter(user => {
      if (filters.role && user.role !== filters.role) return false
      if (filters.status && user.status !== filters.status) return false
      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        return user.name.toLowerCase().includes(searchLower) ||
               user.email.toLowerCase().includes(searchLower)
      }
      return true
    })
  }
)

const getActiveUser = createSelector(
  [getUsers, getActiveUserId],
  (users, activeId) => activeId ? users[activeId] : null
)

// Normalized data selectors
const getUserWithPosts = createSelector(
  [getActiveUser, (state) => state.posts.items],
  (user, posts) => {
    if (!user) return null
    return {
      ...user,
      posts: Object.values(posts).filter(post => post.authorId === user.id)
    }
  }
)

// Virtualized list selector for large datasets
const getVirtualizedPosts = createSelector(
  [getFilteredPosts, (state) => state.ui.virtualList],
  (posts, virtualList) => {
    const { startIndex, endIndex } = virtualList
    return posts.slice(startIndex, endIndex + 1)
  }
)
```

---

## Best Practices

### 1. State Architecture Principles
- **Single Source of Truth**: Centralize state management
- **Immutability**: Always return new state objects
- **Predictability**: State changes should be deterministic
- **Separation of Concerns**: Business logic separate from UI logic
- **Scalability**: Design for growth and complexity

### 2. Performance Guidelines
- Use normalized state structures for relational data
- Implement efficient selectors with memoization
- Avoid unnecessary re-renders with proper state structure
- Use code splitting for large state management modules
- Implement virtual scrolling for large lists

### 3. Testing Strategies
```javascript
// Testing Redux slices
import { configureStore } from '@reduxjs/toolkit'
import postsReducer, { addPost, updatePost } from './postsSlice'

describe('posts slice', () => {
  let store

  beforeEach(() => {
    store = configureStore({
      reducer: { posts: postsReducer }
    })
  })

  it('should add a new post', () => {
    const newPost = { id: '1', title: 'Test', content: 'Content' }
    store.dispatch(addPost(newPost))
    
    const state = store.getState()
    expect(state.posts.entities['1']).toEqual(newPost)
  })

  it('should update an existing post', () => {
    const post = { id: '1', title: 'Original', content: 'Content' }
    store.dispatch(addPost(post))
    store.dispatch(updatePost({ id: '1', changes: { title: 'Updated' } }))
    
    const state = store.getState()
    expect(state.posts.entities['1'].title).toBe('Updated')
  })
})

// Testing state machines
import { interpret } from 'xstate'
import { authMachine } from './authMachine'

describe('auth machine', () => {
  it('should transition from idle to authenticating on LOGIN', () => {
    const service = interpret(authMachine)
    service.start()
    
    expect(service.state.value).toBe('idle')
    
    service.send('LOGIN')
    expect(service.state.value).toBe('authenticating')
    
    service.stop()
  })
})
```

---

## Projects

### Project 1: Enterprise Task Management System
Build a complex task management application with:
- Multi-tenant architecture
- Real-time collaboration
- Advanced filtering and search
- Offline functionality
- State persistence and migration

### Project 2: E-commerce Admin Dashboard
Create an admin dashboard with:
- Product catalog management
- Order processing workflow
- Inventory tracking
- Analytics and reporting
- Bulk operations

### Project 3: Social Media Analytics Platform
Develop a platform featuring:
- Real-time data streams
- Complex data visualization
- User interaction tracking
- Performance monitoring
- Micro-frontend architecture

---

## Assessment Criteria

### Knowledge Check (40 points)
- Advanced Redux patterns and middleware
- State normalization strategies
- Performance optimization techniques
- Type safety in state management
- State persistence and hydration

### Practical Skills (40 points)
- Implement complex state machines
- Build efficient selectors and derived state
- Create type-safe state management
- Handle asynchronous state scenarios
- Optimize state management performance

### Project Quality (20 points)
- Architecture design and scalability
- Code organization and maintainability
- Testing coverage and quality
- Performance benchmarks
- Documentation and examples

---

## Resources

### Essential Reading
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)
- [XState Documentation](https://xstate.js.org/)
- [RxJS Guide](https://rxjs.dev/guide/overview)
- [Reselect Documentation](https://github.com/reduxjs/reselect)

### Advanced Resources
- [Redux Performance](https://redux.js.org/faq/performance)
- [State Management Patterns](https://kentcdodds.com/blog/application-state-management-with-react)
- [Micro-Frontend State](https://micro-frontends.org/)
- [TypeScript Advanced Types](https://www.typescriptlang.org/docs/handbook/advanced-types.html)

### Tools and Libraries
- Redux Toolkit Query
- Redux DevTools
- XState DevTools
- Reselect
- Redux Persist
- Immer
- Normalizr

---

## Next Steps
After completing this module, you'll be ready to tackle Module 10: Data Fetching, where you'll learn advanced patterns for handling API calls, caching strategies, and real-time data synchronization.

The combination of advanced state management with efficient data fetching creates the foundation for building truly scalable React applications.