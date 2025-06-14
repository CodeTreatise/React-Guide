# TypeScript State Architecture

## Table of Contents
1. [Introduction](#introduction)
2. [TypeScript Fundamentals for State](#typescript-fundamentals-for-state)
3. [Redux with TypeScript](#redux-with-typescript)
4. [Context API with TypeScript](#context-api-with-typescript)
5. [State Machine Types](#state-machine-types)
6. [Advanced Type Patterns](#advanced-type-patterns)
7. [Performance Optimization](#performance-optimization)
8. [Testing with Types](#testing-with-types)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)

## Introduction

TypeScript brings static typing to JavaScript, enabling better development experience through autocomplete, refactoring support, and compile-time error detection. When applied to state management, TypeScript helps create more maintainable and reliable applications.

### Benefits of TypeScript in State Management

```typescript
// Without TypeScript - Runtime errors possible
const updateUser = (user, updates) => {
  return { ...user, ...updates }
}

// Runtime error - typo in property name
const updatedUser = updateUser(user, { usrname: 'john' })

// With TypeScript - Compile-time error detection
interface User {
  id: string
  username: string
  email: string
  profile: UserProfile
}

interface UserProfile {
  firstName: string
  lastName: string
  avatar?: string
}

const updateUser = (user: User, updates: Partial<User>): User => {
  return { ...user, ...updates }
}

// Compile-time error - Property 'usrname' does not exist
// const updatedUser = updateUser(user, { usrname: 'john' })

// Correct usage with autocomplete support
const updatedUser = updateUser(user, { username: 'john' })
```

## TypeScript Fundamentals for State

### Basic State Types

```typescript
// Primitive state types
type LoadingState = boolean
type ErrorState = string | null
type CountState = number

// Object state types
interface UserState {
  id: string
  username: string
  email: string
  isVerified: boolean
  createdAt: Date
  profile: {
    firstName: string
    lastName: string
    bio?: string
  }
}

// Array state types
type PostsState = Post[]

interface Post {
  id: string
  title: string
  content: string
  authorId: string
  tags: string[]
  publishedAt: Date | null
  status: 'draft' | 'published' | 'archived'
}

// Union types for state variants
type ThemeState = 'light' | 'dark' | 'auto'
type ViewMode = 'grid' | 'list' | 'card'

// Discriminated unions for complex state
type RequestState<T> = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string }

// Generic state types
interface EntityState<T> {
  byId: Record<string, T>
  allIds: string[]
}

interface PaginatedState<T> {
  items: T[]
  page: number
  pageSize: number
  totalCount: number
  hasMore: boolean
  loading: boolean
}
```

### Advanced State Modeling

```typescript
{% raw %}
{% raw %}
// Recursive types for tree structures
interface TreeNode<T = any> {
  id: string
  data: T
  children: TreeNode<T>[]
  parent?: TreeNode<T>
}

type CategoryTree = TreeNode<{
  name: string
  description: string
  icon?: string
}>

// Conditional types for dynamic state shape
type ConfigurableState<T extends Record<string, any>> = {
  [K in keyof T]: T[K] extends boolean 
    ? T[K] 
    : T[K] extends string 
    ? T[K] | null 
    : T[K]
} & {
  isConfigured: boolean
  lastUpdated: Date
}

// Mapped types for form state
type FormState<T> = {
  [K in keyof T]: {
    value: T[K]
    error?: string
    touched: boolean
    dirty: boolean
  }
} & {
  isValid: boolean
  isSubmitting: boolean
  submitCount: number
}

// Example usage
interface UserRegistration {
  username: string
  email: string
  password: string
  confirmPassword: string
  agreeToTerms: boolean
}

type UserRegistrationForm = FormState<UserRegistration>

// Template literal types for action naming
type EntityActions<T extends string> = 
  | `FETCH_${T}_REQUEST`
  | `FETCH_${T}_SUCCESS`
  | `FETCH_${T}_FAILURE`
  | `CREATE_${T}_REQUEST`
  | `CREATE_${T}_SUCCESS`
  | `CREATE_${T}_FAILURE`
  | `UPDATE_${T}_REQUEST`
  | `UPDATE_${T}_SUCCESS`
  | `UPDATE_${T}_FAILURE`
  | `DELETE_${T}_REQUEST`
  | `DELETE_${T}_SUCCESS`
  | `DELETE_${T}_FAILURE`

type UserActions = EntityActions<'USER'>
type PostActions = EntityActions<'POST'>
{% endraw %}
{% endraw %}
```

## Redux with TypeScript

### Action Types and Creators

```typescript
{% raw %}
{% raw %}
// Action type definitions
interface LoadUsersAction {
  type: 'LOAD_USERS_REQUEST'
}

interface LoadUsersSuccessAction {
  type: 'LOAD_USERS_SUCCESS'
  payload: User[]
}

interface LoadUsersFailureAction {
  type: 'LOAD_USERS_FAILURE'
  payload: string
}

interface UpdateUserAction {
  type: 'UPDATE_USER'
  payload: {
    id: string
    updates: Partial<User>
  }
}

// Union type for all actions
type UserAction = 
  | LoadUsersAction
  | LoadUsersSuccessAction
  | LoadUsersFailureAction
  | UpdateUserAction

// Action creator functions with proper typing
const loadUsers = (): LoadUsersAction => ({
  type: 'LOAD_USERS_REQUEST'
})

const loadUsersSuccess = (users: User[]): LoadUsersSuccessAction => ({
  type: 'LOAD_USERS_SUCCESS',
  payload: users
})

const loadUsersFailure = (error: string): LoadUsersFailureAction => ({
  type: 'LOAD_USERS_FAILURE',
  payload: error
})

const updateUser = (id: string, updates: Partial<User>): UpdateUserAction => ({
  type: 'UPDATE_USER',
  payload: { id, updates }
})

// Generic action creator factory
function createAsyncActions<T>(entityName: string) {
  const upperName = entityName.toUpperCase()
  
  return {
    request: () => ({ type: `${upperName}_REQUEST` as const }),
    success: (data: T[]) => ({ 
      type: `${upperName}_SUCCESS` as const, 
      payload: data 
    }),
    failure: (error: string) => ({ 
      type: `${upperName}_FAILURE` as const, 
      payload: error 
    })
  }
}

const userActions = createAsyncActions<User>('LOAD_USERS')
{% endraw %}
{% endraw %}
```

### Reducer Types

```typescript
{% raw %}
{% raw %}
// State interface
interface UsersState {
  entities: EntityState<User>
  loading: boolean
  error: string | null
  filters: {
    search: string
    status: User['status'] | 'all'
  }
}

// Initial state with proper typing
const initialUsersState: UsersState = {
  entities: {
    byId: {},
    allIds: []
  },
  loading: false,
  error: null,
  filters: {
    search: '',
    status: 'all'
  }
}

// Typed reducer
const usersReducer = (
  state: UsersState = initialUsersState, 
  action: UserAction
): UsersState => {
  switch (action.type) {
    case 'LOAD_USERS_REQUEST':
      return {
        ...state,
        loading: true,
        error: null
      }
    
    case 'LOAD_USERS_SUCCESS':
      const entities = action.payload.reduce(
        (acc, user) => {
          acc.byId[user.id] = user
          acc.allIds.push(user.id)
          return acc
        },
        { byId: {} as Record<string, User>, allIds: [] as string[] }
      )
      
      return {
        ...state,
        entities,
        loading: false,
        error: null
      }
    
    case 'LOAD_USERS_FAILURE':
      return {
        ...state,
        loading: false,
        error: action.payload
      }
    
    case 'UPDATE_USER':
      const { id, updates } = action.payload
      return {
        ...state,
        entities: {
          ...state.entities,
          byId: {
            ...state.entities.byId,
            [id]: { ...state.entities.byId[id], ...updates }
          }
        }
      }
    
    default:
      return state
  }
}

// Generic reducer factory
function createEntityReducer<T extends { id: string }>(
  entityName: string
) {
  type EntityActions = 
    | { type: `${string}_REQUEST` }
    | { type: `${string}_SUCCESS`; payload: T[] }
    | { type: `${string}_FAILURE`; payload: string }
    | { type: `UPDATE_${string}`; payload: { id: string; updates: Partial<T> } }

  interface State {
    entities: EntityState<T>
    loading: boolean
    error: string | null
  }

  const initialState: State = {
    entities: { byId: {}, allIds: [] },
    loading: false,
    error: null
  }

  return (state: State = initialState, action: EntityActions): State => {
    const upperName = entityName.toUpperCase()
    
    switch (action.type) {
      case `${upperName}_REQUEST`:
        return { ...state, loading: true, error: null }
      
      case `${upperName}_SUCCESS`:
        const entities = (action as any).payload.reduce(
          (acc: EntityState<T>, item: T) => {
            acc.byId[item.id] = item
            acc.allIds.push(item.id)
            return acc
          },
          { byId: {} as Record<string, T>, allIds: [] as string[] }
        )
        
        return { ...state, entities, loading: false, error: null }
      
      case `${upperName}_FAILURE`:
        return { ...state, loading: false, error: (action as any).payload }
      
      default:
        return state
    }
  }
}
{% endraw %}
{% endraw %}
```

### Store Configuration

```typescript
// Root state interface
interface RootState {
  users: UsersState
  posts: PostsState
  auth: AuthState
  ui: UIState
}

// Selector types
type RootSelector<T> = (state: RootState) => T

// Typed selectors
const selectUsers: RootSelector<User[]> = (state) =>
  state.users.entities.allIds.map(id => state.users.entities.byId[id])

const selectUsersLoading: RootSelector<boolean> = (state) =>
  state.users.loading

const selectUserById = (id: string): RootSelector<User | undefined> => 
  (state) => state.users.entities.byId[id]

// Selector with parameters using reselect
const makeSelectUserPosts = () => createSelector(
  [
    (state: RootState) => state.posts.entities.byId,
    (state: RootState) => state.posts.entities.allIds,
    (state: RootState, userId: string) => userId
  ],
  (postsById, allIds, userId) =>
    allIds
      .map(id => postsById[id])
      .filter(post => post.authorId === userId)
)

// Store configuration with TypeScript
const store = configureStore({
  reducer: {
    users: usersReducer,
    posts: postsReducer,
    auth: authReducer,
    ui: uiReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE']
      }
    })
})

// Infer types from store
export type AppDispatch = typeof store.dispatch
export type AppSelector<T> = (state: RootState) => T

// Typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>()
export const useAppSelector = <T>(selector: AppSelector<T>) => 
  useSelector(selector)
```

### Redux Toolkit with TypeScript

```typescript
// Using createSlice with TypeScript
interface CounterState {
  value: number
  step: number
}

const initialState: CounterState = {
  value: 0,
  step: 1
}

const counterSlice = createSlice({
  name: 'counter',
  initialState,
  reducers: {
    increment: (state) => {
      state.value += state.step
    },
    decrement: (state) => {
      state.value -= state.step
    },
    incrementByAmount: (state, action: PayloadAction<number>) => {
      state.value += action.payload
    },
    setStep: (state, action: PayloadAction<number>) => {
      state.step = action.payload
    },
    reset: (state) => {
      state.value = 0
    }
  }
})

export const { increment, decrement, incrementByAmount, setStep, reset } = 
  counterSlice.actions
export default counterSlice.reducer

// Async thunks with TypeScript
interface FetchUsersParams {
  page: number
  limit: number
  search?: string
}

interface FetchUsersResponse {
  users: User[]
  totalCount: number
  hasMore: boolean
}

export const fetchUsers = createAsyncThunk<
  FetchUsersResponse,
  FetchUsersParams,
  { rejectValue: string }
>(
  'users/fetchUsers',
  async (params, { rejectWithValue }) => {
    try {
      const response = await api.getUsers(params)
      return response.data
    } catch (error) {
      return rejectWithValue(
        error instanceof Error ? error.message : 'Unknown error'
      )
    }
  }
)

// Slice with async thunk
const usersSlice = createSlice({
  name: 'users',
  initialState: {
    entities: { byId: {} as Record<string, User>, allIds: [] as string[] },
    loading: false,
    error: null as string | null,
    pagination: {
      page: 1,
      totalCount: 0,
      hasMore: true
    }
  },
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    updateUser: (state, action: PayloadAction<{ id: string; updates: Partial<User> }>) => {
      const { id, updates } = action.payload
      if (state.entities.byId[id]) {
        state.entities.byId[id] = { ...state.entities.byId[id], ...updates }
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false
        const { users, totalCount, hasMore } = action.payload
        
        users.forEach(user => {
          state.entities.byId[user.id] = user
          if (!state.entities.allIds.includes(user.id)) {
            state.entities.allIds.push(user.id)
          }
        })
        
        state.pagination = {
          ...state.pagination,
          totalCount,
          hasMore
        }
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload || 'Failed to fetch users'
      })
  }
})
```

## Context API with TypeScript

### Typed Context Creation

```typescript
// Context value type definition
interface UserContextValue {
  user: User | null
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  updateProfile: (updates: Partial<User>) => Promise<void>
  isLoading: boolean
  error: string | null
}

// Create context with proper typing
const UserContext = createContext<UserContextValue | undefined>(undefined)

// Custom hook with type safety
function useUserContext(): UserContextValue {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUserContext must be used within a UserProvider')
  }
  return context
}

// Provider component with TypeScript
interface UserProviderProps {
  children: React.ReactNode
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await authAPI.login(credentials)
      setUser(response.user)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    authAPI.logout()
  }, [])

  const updateProfile = useCallback(async (updates: Partial<User>) => {
    if (!user) throw new Error('No user logged in')
    
    setIsLoading(true)
    setError(null)
    
    try {
      const updatedUser = await userAPI.updateProfile(user.id, updates)
      setUser(updatedUser)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [user])

  const value: UserContextValue = {
    user,
    login,
    logout,
    updateProfile,
    isLoading,
    error
  }

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>
}
```

### Generic Context Pattern

```typescript
// Generic context factory
function createGenericContext<T>() {
  const Context = createContext<T | undefined>(undefined)
  
  function useContext(): T {
    const context = React.useContext(Context)
    if (!context) {
      throw new Error('useContext must be used within Provider')
    }
    return context
  }
  
  return [useContext, Context.Provider] as const
}

// Usage example
interface ThemeContextValue {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const [useTheme, ThemeProvider] = createGenericContext<ThemeContextValue>()

// Provider implementation
const ThemeProviderComponent: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  
  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }, [])

  const value: ThemeContextValue = {
    theme,
    toggleTheme
  }

  return <ThemeProvider value={value}>{children}</ThemeProvider>
}

// Complex state context with reducer
interface AppState {
  user: User | null
  posts: Post[]
  notifications: Notification[]
  ui: {
    sidebarOpen: boolean
    theme: 'light' | 'dark'
    loading: boolean
  }
}

type AppAction = 
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'ADD_POST'; payload: Post }
  | { type: 'UPDATE_POST'; payload: { id: string; updates: Partial<Post> } }
  | { type: 'DELETE_POST'; payload: string }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'SET_LOADING'; payload: boolean }

const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload }
    
    case 'ADD_POST':
      return { ...state, posts: [...state.posts, action.payload] }
    
    case 'UPDATE_POST':
      return {
        ...state,
        posts: state.posts.map(post =>
          post.id === action.payload.id 
            ? { ...post, ...action.payload.updates }
            : post
        )
      }
    
    case 'DELETE_POST':
      return {
        ...state,
        posts: state.posts.filter(post => post.id !== action.payload)
      }
    
    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        ui: { ...state.ui, sidebarOpen: !state.ui.sidebarOpen }
      }
    
    case 'SET_THEME':
      return {
        ...state,
        ui: { ...state.ui, theme: action.payload }
      }
    
    default:
      return state
  }
}

interface AppContextValue {
  state: AppState
  dispatch: React.Dispatch<AppAction>
}

const [useApp, AppProvider] = createGenericContext<AppContextValue>()
```

## State Machine Types

### XState with TypeScript

```typescript
// State machine context type
interface UserMachineContext {
  user: User | null
  error: string | null
  retryCount: number
}

// State machine events
type UserMachineEvent = 
  | { type: 'LOGIN'; credentials: LoginCredentials }
  | { type: 'LOGOUT' }
  | { type: 'RETRY' }
  | { type: 'CLEAR_ERROR' }

// State machine configuration
const userMachine = createMachine<UserMachineContext, UserMachineEvent>({
  id: 'user',
  initial: 'idle',
  context: {
    user: null,
    error: null,
    retryCount: 0
  },
  states: {
    idle: {
      on: {
        LOGIN: 'authenticating'
      }
    },
    authenticating: {
      invoke: {
        id: 'authenticate',
        src: 'authenticateUser',
        onDone: {
          target: 'authenticated',
          actions: assign({
            user: (context, event) => event.data,
            error: null,
            retryCount: 0
          })
        },
        onError: [
          {
            target: 'error',
            cond: 'maxRetriesReached',
            actions: assign({
              error: (context, event) => event.data.message,
              retryCount: (context) => context.retryCount + 1
            })
          },
          {
            target: 'retrying',
            actions: assign({
              error: (context, event) => event.data.message,
              retryCount: (context) => context.retryCount + 1
            })
          }
        ]
      }
    },
    authenticated: {
      on: {
        LOGOUT: {
          target: 'idle',
          actions: assign({
            user: null,
            error: null,
            retryCount: 0
          })
        }
      }
    },
    retrying: {
      after: {
        2000: 'authenticating'
      },
      on: {
        RETRY: 'authenticating'
      }
    },
    error: {
      on: {
        RETRY: 'authenticating',
        CLEAR_ERROR: {
          target: 'idle',
          actions: assign({
            error: null,
            retryCount: 0
          })
        }
      }
    }
  }
}, {
  services: {
    authenticateUser: async (context, event) => {
      if (event.type !== 'LOGIN') {
        throw new Error('Invalid event')
      }
      
      const response = await authAPI.login(event.credentials)
      return response.user
    }
  },
  guards: {
    maxRetriesReached: (context) => context.retryCount >= 3
  }
})

// Type-safe interpreter
const userService = interpret(userMachine)

// React hook for state machine
function useUserMachine() {
  const [state, send] = useMachine(userMachine)
  
  const login = useCallback((credentials: LoginCredentials) => {
    send({ type: 'LOGIN', credentials })
  }, [send])
  
  const logout = useCallback(() => {
    send('LOGOUT')
  }, [send])
  
  const retry = useCallback(() => {
    send('RETRY')
  }, [send])
  
  const clearError = useCallback(() => {
    send('CLEAR_ERROR')
  }, [send])
  
  return {
    user: state.context.user,
    error: state.context.error,
    retryCount: state.context.retryCount,
    isIdle: state.matches('idle'),
    isAuthenticating: state.matches('authenticating'),
    isAuthenticated: state.matches('authenticated'),
    isRetrying: state.matches('retrying'),
    hasError: state.matches('error'),
    login,
    logout,
    retry,
    clearError
  }
}
```

### Complex State Machine Types

```typescript
// Hierarchical state machine
interface FormMachineContext {
  formData: Record<string, any>
  errors: Record<string, string>
  touched: Record<string, boolean>
  submitCount: number
}

type FormMachineEvent = 
  | { type: 'CHANGE'; field: string; value: any }
  | { type: 'BLUR'; field: string }
  | { type: 'SUBMIT' }
  | { type: 'RESET' }
  | { type: 'SET_ERRORS'; errors: Record<string, string> }

const formMachine = createMachine<FormMachineContext, FormMachineEvent>({
  id: 'form',
  initial: 'editing',
  context: {
    formData: {},
    errors: {},
    touched: {},
    submitCount: 0
  },
  states: {
    editing: {
      initial: 'idle',
      states: {
        idle: {
          on: {
            CHANGE: {
              actions: assign({
                formData: (context, event) => ({
                  ...context.formData,
                  [event.field]: event.value
                }),
                // Clear error when field changes
                errors: (context, event) => {
                  const { [event.field]: removed, ...rest } = context.errors
                  return rest
                }
              })
            },
            BLUR: {
              target: 'validating',
              actions: assign({
                touched: (context, event) => ({
                  ...context.touched,
                  [event.field]: true
                })
              })
            }
          }
        },
        validating: {
          invoke: {
            id: 'validateField',
            src: 'validateField',
            onDone: {
              target: 'idle',
              actions: assign({
                errors: (context, event) => ({
                  ...context.errors,
                  ...event.data
                })
              })
            }
          }
        }
      },
      on: {
        SUBMIT: {
          target: 'submitting',
          cond: 'isValid'
        }
      }
    },
    submitting: {
      entry: assign({
        submitCount: (context) => context.submitCount + 1
      }),
      invoke: {
        id: 'submitForm',
        src: 'submitForm',
        onDone: {
          target: 'success'
        },
        onError: {
          target: 'editing',
          actions: assign({
            errors: (context, event) => ({
              ...context.errors,
              _form: event.data.message
            })
          })
        }
      }
    },
    success: {
      type: 'final'
    }
  },
  on: {
    RESET: {
      target: 'editing',
      actions: assign({
        formData: {},
        errors: {},
        touched: {},
        submitCount: 0
      })
    }
  }
}, {
  services: {
    validateField: async (context, event) => {
      // Field validation logic
      const errors: Record<string, string> = {}
      
      if (event.type === 'BLUR') {
        const { field } = event
        const value = context.formData[field]
        
        if (field === 'email' && (!value || !value.includes('@'))) {
          errors.email = 'Valid email is required'
        }
        
        if (field === 'password' && (!value || value.length < 8)) {
          errors.password = 'Password must be at least 8 characters'
        }
      }
      
      return errors
    },
    submitForm: async (context) => {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context.formData)
      })
      
      if (!response.ok) {
        throw new Error('Submission failed')
      }
      
      return response.json()
    }
  },
  guards: {
    isValid: (context) => Object.keys(context.errors).length === 0
  }
})
```

## Advanced Type Patterns

### Branded Types

```typescript
// Branded types for domain-specific IDs
declare const UserIdBrand: unique symbol
declare const PostIdBrand: unique symbol

type UserId = string & { readonly [UserIdBrand]: typeof UserIdBrand }
type PostId = string & { readonly [PostIdBrand]: typeof PostIdBrand }

// Type guards
const isUserId = (id: string): id is UserId => {
  return /^user_/.test(id)
}

const isPostId = (id: string): id is PostId => {
  return /^post_/.test(id)
}

// Factory functions
const createUserId = (id: string): UserId => {
  if (!isUserId(id)) {
    throw new Error('Invalid user ID format')
  }
  return id
}

const createPostId = (id: string): PostId => {
  if (!isPostId(id)) {
    throw new Error('Invalid post ID format')
  }
  return id
}

// Usage in state
interface TypedUserState {
  currentUserId: UserId | null
  users: Record<UserId, User>
  posts: Record<PostId, Post>
}

// This prevents mixing up ID types
// const userPost = state.posts[state.currentUserId] // Type error!
```

### Template Literal Types for Actions

```typescript
{% raw %}
{% raw %}
// Generate action types from entity names
type EntityName = 'user' | 'post' | 'comment'
type ActionType = 'create' | 'read' | 'update' | 'delete'
type AsyncPhase = 'request' | 'success' | 'failure'

type EntityActionType = `${Uppercase<EntityName>}_${Uppercase<ActionType>}_${Uppercase<AsyncPhase>}`

// Results in types like: 'USER_CREATE_REQUEST' | 'POST_UPDATE_SUCCESS' | etc.

// Action creator factory with proper typing
function createEntityActions<T extends EntityName>(entityName: T) {
  const upperEntity = entityName.toUpperCase() as Uppercase<T>
  
  return {
    create: {
      request: () => ({ type: `${upperEntity}_CREATE_REQUEST` as const }),
      success: <TData>(data: TData) => ({ 
        type: `${upperEntity}_CREATE_SUCCESS` as const, 
        payload: data 
      }),
      failure: (error: string) => ({ 
        type: `${upperEntity}_CREATE_FAILURE` as const, 
        payload: error 
      })
    },
    read: {
      request: () => ({ type: `${upperEntity}_READ_REQUEST` as const }),
      success: <TData>(data: TData) => ({ 
        type: `${upperEntity}_READ_SUCCESS` as const, 
        payload: data 
      }),
      failure: (error: string) => ({ 
        type: `${upperEntity}_READ_FAILURE` as const, 
        payload: error 
      })
    }
    // ... update and delete
  }
}

const userActions = createEntityActions('user')
// userActions.create.request() has type { type: 'USER_CREATE_REQUEST' }
{% endraw %}
{% endraw %}
```

### Recursive Types for Nested State

```typescript
{% raw %}
{% raw %}
// Recursive type for nested state updates
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// Path-based state updates
type Path<T, K extends keyof T = keyof T> = K extends string
  ? T[K] extends Record<string, any>
    ? `${K}` | `${K}.${Path<T[K]>}`
    : `${K}`
  : never

type PathValue<T, P extends Path<T>> = P extends `${infer K}.${infer Rest}`
  ? K extends keyof T
    ? Rest extends Path<T[K]>
      ? PathValue<T[K], Rest>
      : never
    : never
  : P extends keyof T
  ? T[P]
  : never

// Type-safe deep state updates
function setDeepState<T, P extends Path<T>>(
  state: T,
  path: P,
  value: PathValue<T, P>
): T {
  const keys = path.split('.')
  const result = { ...state }
  let current: any = result
  
  for (let i = 0; i < keys.length - 1; i++) {
    current[keys[i]] = { ...current[keys[i]] }
    current = current[keys[i]]
  }
  
  current[keys[keys.length - 1]] = value
  return result
}

// Usage
interface NestedState {
  user: {
    profile: {
      personal: {
        name: string
        email: string
      }
      preferences: {
        theme: string
        notifications: boolean
      }
    }
  }
}

const state: NestedState = {
  user: {
    profile: {
      personal: { name: 'John', email: 'john@example.com' },
      preferences: { theme: 'dark', notifications: true }
    }
  }
}

// Type-safe deep update
const newState = setDeepState(state, 'user.profile.personal.name', 'Jane')
{% endraw %}
{% endraw %}
```

## Performance Optimization

### Memoization with Types

```typescript
// Generic memoization
function memoize<TArgs extends any[], TReturn>(
  fn: (...args: TArgs) => TReturn,
  getKey: (...args: TArgs) => string = (...args) => JSON.stringify(args)
): (...args: TArgs) => TReturn {
  const cache = new Map<string, TReturn>()
  
  return (...args: TArgs): TReturn => {
    const key = getKey(...args)
    
    if (cache.has(key)) {
      return cache.get(key)!
    }
    
    const result = fn(...args)
    cache.set(key, result)
    return result
  }
}

// Typed selector memoization
type Selector<TState, TResult> = (state: TState) => TResult

function createMemoizedSelector<TState, TResult>(
  selector: Selector<TState, TResult>,
  equalityFn: (a: TResult, b: TResult) => boolean = Object.is
): Selector<TState, TResult> {
  let lastState: TState
  let lastResult: TResult
  let hasResult = false
  
  return (state: TState): TResult => {
    if (!hasResult || state !== lastState) {
      const newResult = selector(state)
      
      if (!hasResult || !equalityFn(lastResult, newResult)) {
        lastResult = newResult
      }
      
      lastState = state
      hasResult = true
    }
    
    return lastResult
  }
}

// Parametric selector factory
function createParametricSelector<TState, TParams extends any[], TResult>(
  selector: (state: TState, ...params: TParams) => TResult
) {
  const selectorCache = new Map<string, Selector<TState, TResult>>()
  
  return (...params: TParams): Selector<TState, TResult> => {
    const key = JSON.stringify(params)
    
    if (!selectorCache.has(key)) {
      const memoizedSelector = createMemoizedSelector(
        (state: TState) => selector(state, ...params)
      )
      selectorCache.set(key, memoizedSelector)
    }
    
    return selectorCache.get(key)!
  }
}

// Usage
const selectUserPosts = createParametricSelector(
  (state: RootState, userId: string) =>
    state.posts.allIds
      .map(id => state.posts.byId[id])
      .filter(post => post.authorId === userId)
)

// In component
function UserPosts({ userId }: { userId: string }) {
  const userPostsSelector = useMemo(() => selectUserPosts(userId), [userId])
  const posts = useAppSelector(userPostsSelector)
  
  return (
    <div>
      {posts.map(post => (
        <PostItem key={post.id} post={post} />
      ))}
    </div>
  )
}
```

### Structural Sharing

```typescript
// Immutable update helpers with TypeScript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P]
}

class ImmutableHelper {
  static set<T, K extends keyof T>(obj: T, key: K, value: T[K]): T {
    if (obj[key] === value) return obj
    return { ...obj, [key]: value }
  }
  
  static setIn<T>(obj: T, path: string[], value: any): T {
    if (path.length === 0) return value
    
    const [head, ...tail] = path
    const currentValue = (obj as any)[head]
    const newValue = tail.length === 0 ? value : this.setIn(currentValue, tail, value)
    
    if (currentValue === newValue) return obj
    
    return { ...obj, [head]: newValue }
  }
  
  static updateIn<T>(obj: T, path: string[], updater: (value: any) => any): T {
    const currentValue = this.getIn(obj, path)
    const newValue = updater(currentValue)
    return this.setIn(obj, path, newValue)
  }
  
  static getIn(obj: any, path: string[]): any {
    return path.reduce((current, key) => current?.[key], obj)
  }
}

// Structural sharing for arrays
class ImmutableArray {
  static set<T>(arr: readonly T[], index: number, value: T): readonly T[] {
    if (arr[index] === value) return arr
    
    const result = [...arr]
    result[index] = value
    return result
  }
  
  static push<T>(arr: readonly T[], ...items: T[]): readonly T[] {
    return [...arr, ...items]
  }
  
  static remove<T>(arr: readonly T[], index: number): readonly T[] {
    return [...arr.slice(0, index), ...arr.slice(index + 1)]
  }
  
  static filter<T>(arr: readonly T[], predicate: (item: T) => boolean): readonly T[] {
    const result = arr.filter(predicate)
    return result.length === arr.length ? arr : result
  }
  
  static map<T, U>(arr: readonly T[], mapper: (item: T) => U): readonly U[] {
    const result: U[] = []
    let changed = false
    
    for (let i = 0; i < arr.length; i++) {
      const newItem = mapper(arr[i])
      result.push(newItem)
      if (newItem !== (arr[i] as any)) {
        changed = true
      }
    }
    
    return changed ? result : (arr as any)
  }
}
```

## Testing with Types

### Type-Safe Test Utilities

```typescript
// Test state factory
function createTestState<T extends Partial<RootState>>(overrides: T): RootState {
  const defaultState: RootState = {
    users: {
      entities: { byId: {}, allIds: [] },
      loading: false,
      error: null,
      filters: { search: '', status: 'all' }
    },
    posts: {
      entities: { byId: {}, allIds: [] },
      loading: false,
      error: null
    },
    auth: {
      user: null,
      token: null,
      isAuthenticated: false
    },
    ui: {
      theme: 'light',
      sidebarOpen: false
    }
  }
  
  return { ...defaultState, ...overrides }
}

// Type-safe mock store
function createMockStore(initialState: Partial<RootState> = {}) {
  const state = createTestState(initialState)
  const actions: any[] = []
  
  const store = {
    getState: () => state,
    dispatch: jest.fn((action) => {
      actions.push(action)
      return action
    }),
    subscribe: jest.fn(),
    replaceReducer: jest.fn()
  }
  
  return { store, actions }
}

// Selector testing utilities
function testSelector<TResult>(
  selector: Selector<RootState, TResult>,
  state: Partial<RootState>,
  expected: TResult
) {
  const fullState = createTestState(state)
  const result = selector(fullState)
  expect(result).toEqual(expected)
}

// Action testing
function testAction<TAction extends { type: string }>(
  actionCreator: (...args: any[]) => TAction,
  args: Parameters<typeof actionCreator>,
  expected: TAction
) {
  const result = actionCreator(...args)
  expect(result).toEqual(expected)
}

// Reducer testing
function testReducer<TState, TAction>(
  reducer: (state: TState, action: TAction) => TState,
  initialState: TState,
  action: TAction,
  expectedState: TState
) {
  const result = reducer(initialState, action)
  expect(result).toEqual(expectedState)
}

// Usage in tests
describe('User selectors', () => {
  test('selectAllUsers returns all users', () => {
    const users: User[] = [
      { id: '1', username: 'john', email: 'john@example.com' },
      { id: '2', username: 'jane', email: 'jane@example.com' }
    ]
    
    testSelector(
      selectAllUsers,
      {
        users: {
          entities: {
            byId: {
              '1': users[0],
              '2': users[1]
            },
            allIds: ['1', '2']
          },
          loading: false,
          error: null,
          filters: { search: '', status: 'all' }
        }
      },
      users
    )
  })
})

describe('User actions', () => {
  test('updateUser creates correct action', () => {
    testAction(
      updateUser,
      ['1', { username: 'newname' }],
      {
        type: 'UPDATE_USER',
        payload: { id: '1', updates: { username: 'newname' } }
      }
    )
  })
})
```

### Component Testing with State

```typescript
// Test wrapper with typed providers
interface TestWrapperProps {
  initialState?: Partial<RootState>
  children: React.ReactNode
}

const TestWrapper: React.FC<TestWrapperProps> = ({ 
  initialState = {}, 
  children 
}) => {
  const { store } = createMockStore(initialState)
  
  return (
    <Provider store={store as any}>
      <ThemeProvider theme="light">
        {children}
      </ThemeProvider>
    </Provider>
  )
}

// Custom render function
function renderWithState(
  ui: React.ReactElement,
  options: {
    initialState?: Partial<RootState>
    ...?RenderOptions
  } = {}
) {
  const { initialState, ...renderOptions } = options
  
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <TestWrapper initialState={initialState}>{children}</TestWrapper>
  )
  
  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Usage
test('UserProfile displays user information', () => {
  const user: User = {
    id: '1',
    username: 'john',
    email: 'john@example.com'
  }
  
  renderWithState(<UserProfile userId="1" />, {
    initialState: {
      users: {
        entities: {
          byId: { '1': user },
          allIds: ['1']
        },
        loading: false,
        error: null,
        filters: { search: '', status: 'all' }
      }
    }
  })
  
  expect(screen.getByText('john')).toBeInTheDocument()
  expect(screen.getByText('john@example.com')).toBeInTheDocument()
})
```

## Error Handling

### Type-Safe Error Boundaries

```typescript
// Error types
interface AppError {
  message: string
  code: string
  details?: Record<string, any>
}

interface StateError extends AppError {
  action?: string
  state?: string
}

// Error boundary with TypeScript
interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class TypedErrorBoundary extends React.Component<
  React.PropsWithChildren<{
    fallback: React.ComponentType<{ error: Error; errorInfo: ErrorInfo }>
    onError?: (error: Error, errorInfo: ErrorInfo) => void
  }>,
  ErrorBoundaryState
> {
  constructor(props: any) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }
  
  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error
    }
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo })
    this.props.onError?.(error, errorInfo)
  }
  
  render() {
    if (this.state.hasError && this.state.error && this.state.errorInfo) {
      const { fallback: Fallback } = this.props
      return <Fallback error={this.state.error} errorInfo={this.state.errorInfo} />
    }
    
    return this.props.children
  }
}

// Error state management
interface ErrorState {
  global: AppError | null
  byFeature: Record<string, AppError | null>
  history: AppError[]
}

type ErrorAction = 
  | { type: 'SET_GLOBAL_ERROR'; payload: AppError }
  | { type: 'CLEAR_GLOBAL_ERROR' }
  | { type: 'SET_FEATURE_ERROR'; payload: { feature: string; error: AppError } }
  | { type: 'CLEAR_FEATURE_ERROR'; payload: string }
  | { type: 'ADD_TO_HISTORY'; payload: AppError }

const errorReducer = (state: ErrorState, action: ErrorAction): ErrorState => {
  switch (action.type) {
    case 'SET_GLOBAL_ERROR':
      return {
        ...state,
        global: action.payload,
        history: [...state.history, action.payload]
      }
    
    case 'CLEAR_GLOBAL_ERROR':
      return { ...state, global: null }
    
    case 'SET_FEATURE_ERROR':
      return {
        ...state,
        byFeature: {
          ...state.byFeature,
          [action.payload.feature]: action.payload.error
        },
        history: [...state.history, action.payload.error]
      }
    
    case 'CLEAR_FEATURE_ERROR':
      return {
        ...state,
        byFeature: {
          ...state.byFeature,
          [action.payload]: null
        }
      }
    
    default:
      return state
  }
}
```

### Result Types for Error Handling

```typescript
{% raw %}
{% raw %}
// Result type for operations that can fail
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E }

// Helper functions
function success<T>(data: T): Result<T, never> {
  return { success: true, data }
}

function failure<E>(error: E): Result<never, E> {
  return { success: false, error }
}

// Async operations with Result type
async function fetchUserSafe(id: string): Promise<Result<User, AppError>> {
  try {
    const response = await fetch(`/api/users/${id}`)
    
    if (!response.ok) {
      return failure({
        message: 'Failed to fetch user',
        code: 'FETCH_ERROR',
        details: { status: response.status, userId: id }
      })
    }
    
    const user = await response.json()
    return success(user)
  } catch (error) {
    return failure({
      message: error instanceof Error ? error.message : 'Unknown error',
      code: 'NETWORK_ERROR',
      details: { userId: id }
    })
  }
}

// Usage in state management
interface AsyncState<T> {
  result: Result<T, AppError> | null
  loading: boolean
}

const userAsyncReducer = (
  state: AsyncState<User>,
  action: { type: string; payload?: any }
): AsyncState<User> => {
  switch (action.type) {
    case 'FETCH_REQUEST':
      return { ...state, loading: true }
    
    case 'FETCH_SUCCESS':
      return {
        loading: false,
        result: success(action.payload)
      }
    
    case 'FETCH_FAILURE':
      return {
        loading: false,
        result: failure(action.payload)
      }
    
    default:
      return state
  }
}
{% endraw %}
{% endraw %}
```

## Best Practices

### 1. Type Organization
- Define types in separate files and export them
- Use consistent naming conventions
- Group related types together
- Avoid overly complex nested types

### 2. State Shape Design
- Keep state flat and normalized
- Use discriminated unions for different states
- Separate domain data from UI state
- Make impossible states unrepresentable

### 3. Action Design
- Use string literal types for action types
- Include all necessary data in payloads
- Use generic action creators where appropriate
- Consider using Redux Toolkit for better TypeScript support

### 4. Performance Considerations
- Use proper selector memoization
- Avoid creating new objects in selectors
- Consider structural sharing for large state trees
- Profile your state operations

### 5. Error Handling
- Use Result types for operations that can fail
- Implement proper error boundaries
- Provide meaningful error messages
- Log errors for debugging and monitoring

## Conclusion

TypeScript provides powerful tools for creating type-safe, maintainable state management solutions. By leveraging TypeScript's type system effectively, you can:

- Catch errors at compile time
- Improve developer experience with autocomplete and refactoring
- Create more maintainable and self-documenting code
- Ensure consistency across your application

The patterns and techniques covered in this guide provide a solid foundation for building robust, type-safe state management architectures that scale with your application's complexity.
