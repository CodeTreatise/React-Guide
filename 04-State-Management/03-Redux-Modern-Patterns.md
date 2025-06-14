# Redux Modern Patterns with Redux Toolkit

## Table of Contents
1. [Redux Toolkit Overview](#redux-toolkit-overview)
2. [Modern Redux Architecture](#modern-redux-architecture)
3. [RTK Query for Data Fetching](#rtk-query-for-data-fetching)
4. [Advanced State Patterns](#advanced-state-patterns)
5. [Middleware and Enhancers](#middleware-and-enhancers)
6. [Performance Optimization](#performance-optimization)
7. [Testing Redux Applications](#testing-redux-applications)
8. [Real-World Applications](#real-world-applications)
9. [Migration Strategies](#migration-strategies)
10. [Best Practices](#best-practices)

## Redux Toolkit Overview

Redux Toolkit (RTK) is the official, opinionated, batteries-included toolset for efficient Redux development. It simplifies Redux usage and incorporates best practices.

### Core Benefits

- **Simplified Store Setup**: Pre-configured store with good defaults
- **Immer Integration**: Write "mutative" logic that's actually immutable
- **Built-in DevTools**: Redux DevTools extension integration
- **Type Safety**: Excellent TypeScript support
- **RTK Query**: Powerful data fetching solution

### Basic Setup

```jsx
// store/index.js
import { configureStore } from '@reduxjs/toolkit';
import { authSlice } from './slices/authSlice';
import { todosSlice } from './slices/todosSlice';
import { uiSlice } from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    todos: todosSlice.reducer,
    ui: uiSlice.reducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE']
      }
    }),
  devTools: process.env.NODE_ENV !== 'production'
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Creating Slices

```jsx
// slices/authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      localStorage.setItem('token', response.token);
      return response.user;
    } catch (error) {
      return rejectWithValue(error.response.data.message);
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logoutUser',
  async (_, { dispatch }) => {
    await authAPI.logout();
    localStorage.removeItem('token');
    dispatch(uiSlice.actions.showNotification({
      type: 'success',
      message: 'Successfully logged out'
    }));
  }
);

export const refreshAuth = createAsyncThunk(
  'auth/refreshAuth',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No token found');
      
      const response = await authAPI.refreshToken(token);
      return response.user;
    } catch (error) {
      localStorage.removeItem('token');
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  loading: false,
  error: null,
  isAuthenticated: false
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCredentials: (state, action) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
    },
    clearCredentials: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
    }
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
        state.user = null;
      })
      // Logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      // Refresh
      .addCase(refreshAuth.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(refreshAuth.rejected, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      });
  }
});

export const { clearError, setCredentials, clearCredentials } = authSlice.actions;
```

## Modern Redux Architecture

### Feature-Based Structure

```
src/
├── store/
│   ├── index.ts                 # Store configuration
│   ├── middleware.ts            # Custom middleware
│   └── rootReducer.ts          # Root reducer
├── features/
│   ├── auth/
│   │   ├── authSlice.ts        # Auth slice
│   │   ├── authAPI.ts          # API calls
│   │   ├── authSelectors.ts    # Memoized selectors
│   │   ├── authMiddleware.ts   # Feature-specific middleware
│   │   └── index.ts            # Feature exports
│   ├── todos/
│   │   ├── todosSlice.ts
│   │   ├── todosAPI.ts
│   │   ├── todosSelectors.ts
│   │   └── index.ts
│   └── ui/
│       ├── uiSlice.ts
│       ├── uiSelectors.ts
│       └── index.ts
└── hooks/
    ├── useAppDispatch.ts
    ├── useAppSelector.ts
    └── useAuth.ts
```

### Typed Hooks

```tsx
// hooks/redux.ts
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from '../store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// Feature-specific hooks
export const useAuth = () => {
  const dispatch = useAppDispatch();
  const auth = useAppSelector(state => state.auth);
  
  return {
    ...auth,
    login: (credentials) => dispatch(loginUser(credentials)),
    logout: () => dispatch(logoutUser()),
    clearError: () => dispatch(clearError())
  };
};
```

### Memoized Selectors

```jsx
// features/todos/todosSelectors.js
import { createSelector } from '@reduxjs/toolkit';

const selectTodosState = (state) => state.todos;

export const selectAllTodos = createSelector(
  [selectTodosState],
  (todos) => todos.items
);

export const selectTodoById = createSelector(
  [selectAllTodos, (state, todoId) => todoId],
  (todos, todoId) => todos.find(todo => todo.id === todoId)
);

export const selectCompletedTodos = createSelector(
  [selectAllTodos],
  (todos) => todos.filter(todo => todo.completed)
);

export const selectActiveTodos = createSelector(
  [selectAllTodos],
  (todos) => todos.filter(todo => !todo.completed)
);

export const selectTodoStats = createSelector(
  [selectAllTodos],
  (todos) => ({
    total: todos.length,
    completed: todos.filter(todo => todo.completed).length,
    active: todos.filter(todo => !todo.completed).length
  })
);

export const selectFilteredTodos = createSelector(
  [selectAllTodos, (state) => state.todos.filter],
  (todos, filter) => {
    switch (filter) {
      case 'completed':
        return todos.filter(todo => todo.completed);
      case 'active':
        return todos.filter(todo => !todo.completed);
      default:
        return todos;
    }
  }
);

export const selectTodosByCategory = createSelector(
  [selectAllTodos, (state, category) => category],
  (todos, category) => todos.filter(todo => todo.category === category)
);
```

## RTK Query for Data Fetching

### API Slice Setup

```tsx
{% raw %}
{% raw %}
// features/api/apiSlice.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../../store';

// Base query with auth
const baseQuery = fetchBaseQuery({
  baseUrl: '/api/',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    return headers;
  }
});

// Base query with re-authentication
const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);
  
  if (result.error && result.error.status === 401) {
    // Try to refresh token
    const refreshResult = await baseQuery('/auth/refresh', api, extraOptions);
    
    if (refreshResult.data) {
      // Update auth state
      api.dispatch(setCredentials(refreshResult.data));
      // Retry original query
      result = await baseQuery(args, api, extraOptions);
    } else {
      api.dispatch(logoutUser());
    }
  }
  
  return result;
};

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User', 'Todo', 'Post'],
  endpoints: (builder) => ({})
});
{% endraw %}
{% endraw %}
```

### Feature API Slices

```tsx
{% raw %}
{% raw %}
// features/todos/todosAPI.ts
import { apiSlice } from '../api/apiSlice';

export interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  category: string;
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateTodoRequest {
  title: string;
  description?: string;
  category: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}

export interface UpdateTodoRequest {
  id: string;
  title?: string;
  description?: string;
  completed?: boolean;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}

export const todosApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getTodos: builder.query<Todo[], { 
      category?: string; 
      completed?: boolean;
      limit?: number;
      offset?: number;
    }>({
      query: (params) => ({
        url: 'todos',
        params
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Todo' as const, id })),
              { type: 'Todo', id: 'LIST' }
            ]
          : [{ type: 'Todo', id: 'LIST' }]
    }),
    
    getTodoById: builder.query<Todo, string>({
      query: (id) => `todos/${id}`,
      providesTags: (result, error, id) => [{ type: 'Todo', id }]
    }),
    
    createTodo: builder.mutation<Todo, CreateTodoRequest>({
      query: (todo) => ({
        url: 'todos',
        method: 'POST',
        body: todo
      }),
      invalidatesTags: [{ type: 'Todo', id: 'LIST' }],
      // Optimistic update
      onQueryStarted: async (newTodo, { dispatch, queryFulfilled }) => {
        const patchResult = dispatch(
          todosApiSlice.util.updateQueryData('getTodos', {}, (draft) => {
            draft.unshift({
              ...newTodo,
              id: `temp-${Date.now()}`,
              completed: false,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString()
            });
          })
        );
        
        try {
          await queryFulfilled;
        } catch {
          patchResult.undo();
        }
      }
    }),
    
    updateTodo: builder.mutation<Todo, UpdateTodoRequest>({
      query: ({ id, ...patch }) => ({
        url: `todos/${id}`,
        method: 'PATCH',
        body: patch
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Todo', id }],
      // Optimistic update
      onQueryStarted: async ({ id, ...patch }, { dispatch, queryFulfilled }) => {
        const patchResult = dispatch(
          todosApiSlice.util.updateQueryData('getTodos', {}, (draft) => {
            const todo = draft.find(t => t.id === id);
            if (todo) {
              Object.assign(todo, patch);
            }
          })
        );
        
        try {
          await queryFulfilled;
        } catch {
          patchResult.undo();
        }
      }
    }),
    
    deleteTodo: builder.mutation<void, string>({
      query: (id) => ({
        url: `todos/${id}`,
        method: 'DELETE'
      }),
      invalidatesTags: (result, error, id) => [{ type: 'Todo', id }],
      // Optimistic update
      onQueryStarted: async (id, { dispatch, queryFulfilled }) => {
        const patchResult = dispatch(
          todosApiSlice.util.updateQueryData('getTodos', {}, (draft) => {
            const index = draft.findIndex(todo => todo.id === id);
            if (index !== -1) {
              draft.splice(index, 1);
            }
          })
        );
        
        try {
          await queryFulfilled;
        } catch {
          patchResult.undo();
        }
      }
    }),
    
    bulkUpdateTodos: builder.mutation<Todo[], { ids: string[]; updates: Partial<Todo> }>({
      query: ({ ids, updates }) => ({
        url: 'todos/bulk',
        method: 'PATCH',
        body: { ids, updates }
      }),
      invalidatesTags: (result, error, { ids }) =>
        ids.map(id => ({ type: 'Todo' as const, id }))
    })
  })
});

export const {
  useGetTodosQuery,
  useGetTodoByIdQuery,
  useCreateTodoMutation,
  useUpdateTodoMutation,
  useDeleteTodoMutation,
  useBulkUpdateTodosMutation,
  useLazyGetTodosQuery,
  usePrefetch
} = todosApiSlice;
{% endraw %}
{% endraw %}
```

### Advanced RTK Query Patterns

```tsx
// Custom hook with RTK Query
export function useTodosWithLocalState() {
  const [filter, setFilter] = useState<'all' | 'completed' | 'active'>('all');
  const [category, setCategory] = useState<string | undefined>();
  
  const {
    data: todos = [],
    isLoading,
    error,
    refetch
  } = useGetTodosQuery({
    category,
    completed: filter === 'completed' ? true : filter === 'active' ? false : undefined
  });
  
  const [createTodo, { isLoading: isCreating }] = useCreateTodoMutation();
  const [updateTodo, { isLoading: isUpdating }] = useUpdateTodoMutation();
  const [deleteTodo, { isLoading: isDeleting }] = useDeleteTodoMutation();
  
  const handleCreateTodo = async (todoData: CreateTodoRequest) => {
    try {
      await createTodo(todoData).unwrap();
      // Handle success
    } catch (error) {
      // Handle error
      console.error('Failed to create todo:', error);
    }
  };
  
  const handleToggleTodo = async (id: string, completed: boolean) => {
    try {
      await updateTodo({ id, completed }).unwrap();
    } catch (error) {
      console.error('Failed to update todo:', error);
    }
  };
  
  return {
    todos,
    isLoading: isLoading || isCreating || isUpdating || isDeleting,
    error,
    filter,
    setFilter,
    category,
    setCategory,
    createTodo: handleCreateTodo,
    toggleTodo: handleToggleTodo,
    deleteTodo: (id: string) => deleteTodo(id),
    refetch
  };
}

// Polling and background refetching
export function useLiveTodos() {
  const {
    data: todos,
    isLoading,
    error
  } = useGetTodosQuery({}, {
    pollingInterval: 30000, // Poll every 30 seconds
    refetchOnFocus: true,
    refetchOnReconnect: true,
    skip: false
  });
  
  return { todos, isLoading, error };
}

// Manual cache management
export function useTodoActions() {
  const dispatch = useAppDispatch();
  
  const invalidateAllTodos = () => {
    dispatch(todosApiSlice.util.invalidateTags([{ type: 'Todo', id: 'LIST' }]));
  };
  
  const prefetchTodo = (id: string) => {
    dispatch(todosApiSlice.util.prefetch('getTodoById', id, { force: true }));
  };
  
  const updateTodoInCache = (id: string, updates: Partial<Todo>) => {
    dispatch(
      todosApiSlice.util.updateQueryData('getTodos', {}, (draft) => {
        const todo = draft.find(t => t.id === id);
        if (todo) {
          Object.assign(todo, updates);
        }
      })
    );
  };
  
  return {
    invalidateAllTodos,
    prefetchTodo,
    updateTodoInCache
  };
}
```

## Advanced State Patterns

### Entity Adapter Pattern

```tsx
// Using createEntityAdapter for normalized state
import { createSlice, createEntityAdapter, createSelector } from '@reduxjs/toolkit';

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  lastSeen: string;
  isOnline: boolean;
}

// Create entity adapter
const usersAdapter = createEntityAdapter<User>({
  // Sort by name
  sortComparer: (a, b) => a.name.localeCompare(b.name),
  // Select ID field (default is 'id')
  selectId: (user) => user.id
});

const initialState = usersAdapter.getInitialState({
  loading: false,
  error: null,
  lastFetch: null
});

export const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    // Generated actions: addOne, addMany, setOne, setMany, setAll, updateOne, updateMany, upsertOne, upsertMany, removeOne, removeMany, removeAll
    userOnline: (state, action) => {
      usersAdapter.updateOne(state, {
        id: action.payload.userId,
        changes: { 
          isOnline: true, 
          lastSeen: new Date().toISOString() 
        }
      });
    },
    userOffline: (state, action) => {
      usersAdapter.updateOne(state, {
        id: action.payload.userId,
        changes: { 
          isOnline: false, 
          lastSeen: new Date().toISOString() 
        }
      });
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        usersAdapter.setAll(state, action.payload);
        state.lastFetch = Date.now();
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

// Export entity adapter selectors
export const {
  selectAll: selectAllUsers,
  selectById: selectUserById,
  selectIds: selectUserIds
} = usersAdapter.getSelectors((state) => state.users);

// Custom selectors
export const selectOnlineUsers = createSelector(
  [selectAllUsers],
  (users) => users.filter(user => user.isOnline)
);

export const selectUsersByName = createSelector(
  [selectAllUsers, (state, searchTerm) => searchTerm],
  (users, searchTerm) => 
    users.filter(user => 
      user.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
);

export const { userOnline, userOffline, setLoading, setError } = usersSlice.actions;
```

### Complex State Patterns

```tsx
// Multi-level state with relationships
interface Post {
  id: string;
  title: string;
  content: string;
  authorId: string;
  tags: string[];
  createdAt: string;
  likes: number;
  comments: string[]; // Comment IDs
}

interface Comment {
  id: string;
  postId: string;
  authorId: string;
  content: string;
  parentId?: string; // For nested comments
  createdAt: string;
  likes: number;
}

// Normalized state structure
const postsAdapter = createEntityAdapter<Post>();
const commentsAdapter = createEntityAdapter<Comment>();

interface BlogState {
  posts: ReturnType<typeof postsAdapter.getInitialState>;
  comments: ReturnType<typeof commentsAdapter.getInitialState>;
  ui: {
    selectedPostId: string | null;
    isCreatingPost: boolean;
    isCreatingComment: boolean;
  };
}

const initialState: BlogState = {
  posts: postsAdapter.getInitialState(),
  comments: commentsAdapter.getInitialState(),
  ui: {
    selectedPostId: null,
    isCreatingPost: false,
    isCreatingComment: false
  }
};

export const blogSlice = createSlice({
  name: 'blog',
  initialState,
  reducers: {
    postAdded: (state, action) => {
      postsAdapter.addOne(state.posts, action.payload);
    },
    postUpdated: (state, action) => {
      postsAdapter.updateOne(state.posts, action.payload);
    },
    postDeleted: (state, action) => {
      postsAdapter.removeOne(state.posts, action.payload);
      // Remove associated comments
      const commentsToRemove = Object.values(state.comments.entities)
        .filter(comment => comment?.postId === action.payload)
        .map(comment => comment!.id);
      commentsAdapter.removeMany(state.comments, commentsToRemove);
    },
    commentAdded: (state, action) => {
      const comment = action.payload;
      commentsAdapter.addOne(state.comments, comment);
      // Add comment ID to post
      const post = state.posts.entities[comment.postId];
      if (post) {
        post.comments.push(comment.id);
      }
    },
    postLiked: (state, action) => {
      const post = state.posts.entities[action.payload];
      if (post) {
        post.likes += 1;
      }
    },
    selectPost: (state, action) => {
      state.ui.selectedPostId = action.payload;
    }
  }
});

// Complex selectors with relationships
export const selectPostsState = (state: RootState) => state.blog.posts;
export const selectCommentsState = (state: RootState) => state.blog.comments;

export const {
  selectAll: selectAllPosts,
  selectById: selectPostById
} = postsAdapter.getSelectors(selectPostsState);

export const {
  selectAll: selectAllComments,
  selectById: selectCommentById
} = commentsAdapter.getSelectors(selectCommentsState);

export const selectPostWithComments = createSelector(
  [selectPostById, selectAllComments, (state, postId) => postId],
  (post, comments, postId) => {
    if (!post) return null;
    
    const postComments = comments.filter(comment => comment.postId === postId);
    return {
      ...post,
      comments: postComments
    };
  }
);

export const selectPostsByTag = createSelector(
  [selectAllPosts, (state, tag) => tag],
  (posts, tag) => posts.filter(post => post.tags.includes(tag))
);
```

## Middleware and Enhancers

### Custom Middleware

```tsx
{% raw %}
{% raw %}
// Logger middleware
const loggerMiddleware: Middleware = (store) => (next) => (action) => {
  const prevState = store.getState();
  const result = next(action);
  const nextState = store.getState();
  
  console.group(`Action: ${action.type}`);
  console.log('Previous State:', prevState);
  console.log('Action:', action);
  console.log('Next State:', nextState);
  console.groupEnd();
  
  return result;
};

// Error handling middleware
const errorMiddleware: Middleware = (store) => (next) => (action) => {
  try {
    return next(action);
  } catch (error) {
    console.error('Redux error:', error);
    store.dispatch(uiSlice.actions.showError({
      message: 'An unexpected error occurred',
      details: error.message
    }));
    throw error;
  }
};

// API middleware for side effects
const apiMiddleware: Middleware = (store) => (next) => (action) => {
  const result = next(action);
  
  // Handle auth actions
  if (action.type === 'auth/loginUser/fulfilled') {
    // Auto-fetch user data after login
    store.dispatch(fetchUserProfile());
  }
  
  if (action.type === 'auth/logoutUser/fulfilled') {
    // Clear sensitive data
    store.dispatch(clearUserData());
  }
  
  return result;
};

// Persistence middleware
const persistenceMiddleware: Middleware = (store) => (next) => (action) => {
  const result = next(action);
  
  // Save specific state to localStorage
  if (action.type.startsWith('auth/')) {
    const { auth } = store.getState();
    localStorage.setItem('auth', JSON.stringify({
      token: auth.token,
      user: auth.user
    }));
  }
  
  return result;
};
{% endraw %}
{% endraw %}
```

### Performance Monitoring

```tsx
{% raw %}
{% raw %}
// Performance monitoring middleware
const performanceMiddleware: Middleware = (store) => (next) => (action) => {
  const start = performance.now();
  const result = next(action);
  const end = performance.now();
  
  const duration = end - start;
  
  if (duration > 10) { // Log slow actions
    console.warn(`Slow action detected: ${action.type} took ${duration.toFixed(2)}ms`);
  }
  
  // Track action performance in development
  if (process.env.NODE_ENV === 'development') {
    window.__REDUX_PERFORMANCE__ = window.__REDUX_PERFORMANCE__ || {};
    window.__REDUX_PERFORMANCE__[action.type] = 
      (window.__REDUX_PERFORMANCE__[action.type] || 0) + duration;
  }
  
  return result;
};

// Memory usage tracking
const memoryMiddleware: Middleware = (store) => (next) => (action) => {
  const result = next(action);
  
  if (performance.memory) {
    const memoryInfo = {
      used: performance.memory.usedJSHeapSize,
      total: performance.memory.totalJSHeapSize,
      limit: performance.memory.jsHeapSizeLimit
    };
    
    if (memoryInfo.used / memoryInfo.limit > 0.8) {
      console.warn('High memory usage detected:', memoryInfo);
    }
  }
  
  return result;
};
{% endraw %}
{% endraw %}
```

## Performance Optimization

### Selector Optimization

```tsx
// Avoid creating new objects in selectors
// ❌ Bad - creates new array every time
const selectTodoTitles = (state) => 
  state.todos.map(todo => todo.title);

// ✅ Good - memoized selector
const selectTodoTitles = createSelector(
  [selectAllTodos],
  (todos) => todos.map(todo => todo.title)
);

// Reselect patterns for complex calculations
const selectExpensiveComputation = createSelector(
  [selectAllTodos, selectFilter],
  (todos, filter) => {
    // Expensive computation only runs when todos or filter changes
    return todos
      .filter(todo => {
        switch (filter) {
          case 'completed': return todo.completed;
          case 'active': return !todo.completed;
          default: return true;
        }
      })
      .sort((a, b) => {
        // Complex sorting logic
        if (a.priority !== b.priority) {
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        }
        return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
      });
  }
);

// Parameterized selectors
const makeSelectTodosByCategory = () => createSelector(
  [selectAllTodos, (state, category) => category],
  (todos, category) => todos.filter(todo => todo.category === category)
);

// Usage in component
function TodosByCategory({ category }) {
  const selectTodosByCategory = useMemo(makeSelectTodosByCategory, []);
  const todos = useAppSelector(state => selectTodosByCategory(state, category));
  
  return (
    <div>
      {todos.map(todo => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
    </div>
  );
}
```

### Component Optimization

```tsx
{% raw %}
{% raw %}
// Memoized component with specific selectors
const TodoItem = React.memo(({ todoId }: { todoId: string }) => {
  const todo = useAppSelector(state => selectTodoById(state, todoId));
  const dispatch = useAppDispatch();
  
  const handleToggle = useCallback(() => {
    if (todo) {
      dispatch(updateTodo({ id: todo.id, completed: !todo.completed }));
    }
  }, [dispatch, todo]);
  
  if (!todo) return null;
  
  return (
    <div className={`todo-item ${todo.completed ? 'completed' : ''}`}>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={handleToggle}
      />
      <span>{todo.title}</span>
    </div>
  );
});

// List component that only re-renders when todo IDs change
const TodoList = React.memo(() => {
  const todoIds = useAppSelector(selectTodoIds);
  
  return (
    <div className="todo-list">
      {todoIds.map(id => (
        <TodoItem key={id} todoId={id} />
      ))}
    </div>
  );
});

// Optimized form component
const TodoForm = React.memo(() => {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('personal');
  const dispatch = useAppDispatch();
  const isLoading = useAppSelector(state => state.todos.loading);
  
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      dispatch(createTodo({ title: title.trim(), category }));
      setTitle('');
    }
  }, [dispatch, title, category]);
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Add a todo..."
        disabled={isLoading}
      />
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        disabled={isLoading}
      >
        <option value="personal">Personal</option>
        <option value="work">Work</option>
        <option value="shopping">Shopping</option>
      </select>
      <button type="submit" disabled={isLoading || !title.trim()}>
        {isLoading ? 'Adding...' : 'Add Todo'}
      </button>
    </form>
  );
});
{% endraw %}
{% endraw %}
```

## Testing Redux Applications

### Slice Testing

```tsx
// Testing slices
import { configureStore } from '@reduxjs/toolkit';
import { authSlice, loginUser, logoutUser } from '../authSlice';

describe('authSlice', () => {
  let store: ReturnType<typeof configureStore>;
  
  beforeEach(() => {
    store = configureStore({
      reducer: { auth: authSlice.reducer }
    });
  });
  
  test('should handle initial state', () => {
    expect(store.getState().auth).toEqual({
      user: null,
      token: null,
      loading: false,
      error: null,
      isAuthenticated: false
    });
  });
  
  test('should handle clearError', () => {
    // Set up state with error
    store.dispatch(authSlice.actions.setError('Some error'));
    expect(store.getState().auth.error).toBe('Some error');
    
    // Clear error
    store.dispatch(authSlice.actions.clearError());
    expect(store.getState().auth.error).toBe(null);
  });
  
  test('should handle loginUser.pending', () => {
    store.dispatch(loginUser.pending('', { email: 'test@test.com', password: 'password' }));
    
    const state = store.getState().auth;
    expect(state.loading).toBe(true);
    expect(state.error).toBe(null);
  });
  
  test('should handle loginUser.fulfilled', () => {
    const user = { id: '1', name: 'John Doe', email: 'john@test.com' };
    
    store.dispatch(loginUser.fulfilled(user, '', { email: 'test@test.com', password: 'password' }));
    
    const state = store.getState().auth;
    expect(state.loading).toBe(false);
    expect(state.user).toEqual(user);
    expect(state.isAuthenticated).toBe(true);
    expect(state.error).toBe(null);
  });
  
  test('should handle loginUser.rejected', () => {
    const errorMessage = 'Invalid credentials';
    
    store.dispatch(loginUser.rejected(
      new Error(errorMessage),
      '',
      { email: 'test@test.com', password: 'password' },
      errorMessage
    ));
    
    const state = store.getState().auth;
    expect(state.loading).toBe(false);
    expect(state.error).toBe(errorMessage);
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBe(null);
  });
});
```

### Testing Async Thunks

```tsx
// Testing async thunks with mocked API
import { loginUser } from '../authSlice';
import * as authAPI from '../authAPI';

// Mock the API
jest.mock('../authAPI');
const mockedAuthAPI = authAPI as jest.Mocked<typeof authAPI>;

describe('auth async thunks', () => {
  test('loginUser success', async () => {
    const mockUser = { id: '1', name: 'John Doe', email: 'john@test.com' };
    const mockResponse = { user: mockUser, token: 'mock-token' };
    
    mockedAuthAPI.login.mockResolvedValue(mockResponse);
    
    const dispatch = jest.fn();
    const getState = jest.fn();
    
    const thunk = loginUser({ email: 'john@test.com', password: 'password' });
    const result = await thunk(dispatch, getState, undefined);
    
    expect(mockedAuthAPI.login).toHaveBeenCalledWith({
      email: 'john@test.com',
      password: 'password'
    });
    
    expect(result.type).toBe('auth/loginUser/fulfilled');
    expect(result.payload).toEqual(mockUser);
  });
  
  test('loginUser failure', async () => {
    const errorMessage = 'Invalid credentials';
    mockedAuthAPI.login.mockRejectedValue({
      response: { data: { message: errorMessage } }
    });
    
    const dispatch = jest.fn();
    const getState = jest.fn();
    
    const thunk = loginUser({ email: 'wrong@test.com', password: 'wrong' });
    const result = await thunk(dispatch, getState, undefined);
    
    expect(result.type).toBe('auth/loginUser/rejected');
    expect(result.payload).toBe(errorMessage);
  });
});
```

### Testing Components with Redux

```tsx
// Testing components connected to Redux
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { LoginForm } from '../LoginForm';
import { authSlice } from '../authSlice';

function renderWithRedux(
  ui: React.ReactElement,
  {
    preloadedState = {},
    store = configureStore({
      reducer: { auth: authSlice.reducer },
      preloadedState
    })
  } = {}
) {
  return {
    ...render(<Provider store={store}>{ui}</Provider>),
    store
  };
}

describe('LoginForm', () => {
  test('submits login form', async () => {
    const { store } = renderWithRedux(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      const state = store.getState();
      expect(state.auth.loading).toBe(true);
    });
  });
  
  test('displays error message', () => {
    renderWithRedux(<LoginForm />, {
      preloadedState: {
        auth: {
          user: null,
          token: null,
          loading: false,
          error: 'Invalid credentials',
          isAuthenticated: false
        }
      }
    });
    
    expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
  });
});
```

### Testing RTK Query

```tsx
// Testing RTK Query endpoints
import { setupApiStore } from '../test-utils';
import { todosApiSlice } from '../todosAPI';

describe('todosApiSlice', () => {
  let storeRef: ReturnType<typeof setupApiStore>;
  
  beforeEach(() => {
    storeRef = setupApiStore(todosApiSlice);
  });
  
  test('should fetch todos', async () => {
    const mockTodos = [
      { id: '1', title: 'Test Todo', completed: false, category: 'work' }
    ];
    
    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockTodos)
    });
    
    const result = await storeRef.store.dispatch(
      todosApiSlice.endpoints.getTodos.initiate({})
    );
    
    expect(result.data).toEqual(mockTodos);
  });
  
  test('should create todo with optimistic update', async () => {
    const newTodo = { title: 'New Todo', category: 'personal' };
    const createdTodo = { ...newTodo, id: '1', completed: false };
    
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(createdTodo)
    });
    
    // Start mutation
    const promise = storeRef.store.dispatch(
      todosApiSlice.endpoints.createTodo.initiate(newTodo)
    );
    
    // Check optimistic update
    const cacheEntry = todosApiSlice.endpoints.getTodos.select({})(
      storeRef.store.getState()
    );
    
    // Optimistic update should be visible
    expect(cacheEntry.data?.some(todo => todo.title === newTodo.title)).toBe(true);
    
    await promise;
  });
});
```

## Real-World Applications

### E-commerce Store

```tsx
// Complex e-commerce state management
interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  image: string;
  stock: number;
  rating: number;
  reviews: number;
}

interface CartItem {
  productId: string;
  quantity: number;
  selectedSize?: string;
  selectedColor?: string;
}

interface Order {
  id: string;
  items: CartItem[];
  total: number;
  status: 'pending' | 'processing' | 'shipped' | 'delivered';
  createdAt: string;
}

// Products slice with filtering and search
const productsSlice = createSlice({
  name: 'products',
  initialState: {
    items: [] as Product[],
    filters: {
      category: '',
      priceRange: [0, 1000],
      rating: 0,
      inStock: false
    },
    search: '',
    sortBy: 'name' as 'name' | 'price' | 'rating',
    loading: false,
    error: null
  },
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setSearch: (state, action) => {
      state.search = action.payload;
    },
    setSortBy: (state, action) => {
      state.sortBy = action.payload;
    },
    clearFilters: (state) => {
      state.filters = {
        category: '',
        priceRange: [0, 1000],
        rating: 0,
        inStock: false
      };
      state.search = '';
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.items = action.payload;
        state.loading = false;
      });
  }
});

// Cart slice with complex item management
const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: [] as CartItem[],
    total: 0,
    shipping: 0,
    tax: 0,
    discount: 0,
    couponCode: ''
  },
  reducers: {
    addToCart: (state, action) => {
      const { productId, quantity = 1, ...options } = action.payload;
      const existingItem = state.items.find(item => 
        item.productId === productId &&
        item.selectedSize === options.selectedSize &&
        item.selectedColor === options.selectedColor
      );
      
      if (existingItem) {
        existingItem.quantity += quantity;
      } else {
        state.items.push({ productId, quantity, ...options });
      }
    },
    updateQuantity: (state, action) => {
      const { productId, quantity, ...options } = action.payload;
      const item = state.items.find(item => 
        item.productId === productId &&
        item.selectedSize === options.selectedSize &&
        item.selectedColor === options.selectedColor
      );
      
      if (item) {
        if (quantity <= 0) {
          state.items = state.items.filter(i => i !== item);
        } else {
          item.quantity = quantity;
        }
      }
    },
    removeFromCart: (state, action) => {
      state.items = state.items.filter(item => 
        !(item.productId === action.payload.productId &&
          item.selectedSize === action.payload.selectedSize &&
          item.selectedColor === action.payload.selectedColor)
      );
    },
    applyCoupon: (state, action) => {
      state.couponCode = action.payload.code;
      state.discount = action.payload.discount;
    },
    clearCart: (state) => {
      state.items = [];
      state.couponCode = '';
      state.discount = 0;
    }
  }
});

// Selectors for computed values
export const selectCartWithProducts = createSelector(
  [(state) => state.cart.items, (state) => state.products.items],
  (cartItems, products) => {
    return cartItems.map(cartItem => {
      const product = products.find(p => p.id === cartItem.productId);
      return {
        ...cartItem,
        product,
        subtotal: product ? product.price * cartItem.quantity : 0
      };
    });
  }
);

export const selectCartTotals = createSelector(
  [selectCartWithProducts, (state) => state.cart],
  (cartWithProducts, cart) => {
    const subtotal = cartWithProducts.reduce((sum, item) => sum + item.subtotal, 0);
    const discountAmount = subtotal * (cart.discount / 100);
    const taxAmount = (subtotal - discountAmount) * 0.08;
    const total = subtotal - discountAmount + taxAmount + cart.shipping;
    
    return {
      subtotal,
      discount: discountAmount,
      tax: taxAmount,
      shipping: cart.shipping,
      total
    };
  }
);

export const selectFilteredProducts = createSelector(
  [
    (state) => state.products.items,
    (state) => state.products.filters,
    (state) => state.products.search,
    (state) => state.products.sortBy
  ],
  (products, filters, search, sortBy) => {
    let filtered = products;
    
    // Apply search
    if (search) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    // Apply filters
    if (filters.category) {
      filtered = filtered.filter(product => product.category === filters.category);
    }
    
    if (filters.inStock) {
      filtered = filtered.filter(product => product.stock > 0);
    }
    
    filtered = filtered.filter(product =>
      product.price >= filters.priceRange[0] &&
      product.price <= filters.priceRange[1] &&
      product.rating >= filters.rating
    );
    
    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price':
          return a.price - b.price;
        case 'rating':
          return b.rating - a.rating;
        default:
          return a.name.localeCompare(b.name);
      }
    });
    
    return filtered;
  }
);
```

## Migration Strategies

### From Class Components to Redux Hooks

```tsx
// Before: Class component with connect
import { connect } from 'react-redux';

class TodoListOld extends Component {
  componentDidMount() {
    this.props.fetchTodos();
  }
  
  render() {
    const { todos, loading, addTodo } = this.props;
    
    return (
      <div>
        {loading && <div>Loading...</div>}
        {todos.map(todo => (
          <div key={todo.id}>{todo.title}</div>
        ))}
        <button onClick={() => addTodo({ title: 'New Todo' })}>
          Add Todo
        </button>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  todos: state.todos.items,
  loading: state.todos.loading
});

const mapDispatchToProps = {
  fetchTodos,
  addTodo
};

export default connect(mapStateToProps, mapDispatchToProps)(TodoListOld);

// After: Functional component with hooks
import { useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../hooks/redux';

export function TodoListNew() {
  const dispatch = useAppDispatch();
  const todos = useAppSelector(state => state.todos.items);
  const loading = useAppSelector(state => state.todos.loading);
  
  useEffect(() => {
    dispatch(fetchTodos());
  }, [dispatch]);
  
  const handleAddTodo = () => {
    dispatch(addTodo({ title: 'New Todo' }));
  };
  
  return (
    <div>
      {loading && <div>Loading...</div>}
      {todos.map(todo => (
        <div key={todo.id}>{todo.title}</div>
      ))}
      <button onClick={handleAddTodo}>
        Add Todo
      </button>
    </div>
  );
}
```

### From Redux to Redux Toolkit

```tsx
// Before: Traditional Redux
// actions/todos.js
export const ADD_TODO = 'ADD_TODO';
export const TOGGLE_TODO = 'TOGGLE_TODO';
export const FETCH_TODOS_REQUEST = 'FETCH_TODOS_REQUEST';
export const FETCH_TODOS_SUCCESS = 'FETCH_TODOS_SUCCESS';
export const FETCH_TODOS_FAILURE = 'FETCH_TODOS_FAILURE';

export const addTodo = (todo) => ({
  type: ADD_TODO,
  payload: todo
});

export const fetchTodos = () => async (dispatch) => {
  dispatch({ type: FETCH_TODOS_REQUEST });
  try {
    const response = await api.getTodos();
    dispatch({ type: FETCH_TODOS_SUCCESS, payload: response.data });
  } catch (error) {
    dispatch({ type: FETCH_TODOS_FAILURE, payload: error.message });
  }
};

// reducers/todos.js
const initialState = {
  items: [],
  loading: false,
  error: null
};

export default function todosReducer(state = initialState, action) {
  switch (action.type) {
    case ADD_TODO:
      return {
        ...state,
        items: [...state.items, action.payload]
      };
    case FETCH_TODOS_REQUEST:
      return {
        ...state,
        loading: true,
        error: null
      };
    case FETCH_TODOS_SUCCESS:
      return {
        ...state,
        loading: false,
        items: action.payload
      };
    case FETCH_TODOS_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload
      };
    default:
      return state;
  }
}

// After: Redux Toolkit
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchTodos = createAsyncThunk(
  'todos/fetchTodos',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.getTodos();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const todosSlice = createSlice({
  name: 'todos',
  initialState: {
    items: [],
    loading: false,
    error: null
  },
  reducers: {
    addTodo: (state, action) => {
      state.items.push(action.payload);
    },
    toggleTodo: (state, action) => {
      const todo = state.items.find(todo => todo.id === action.payload);
      if (todo) {
        todo.completed = !todo.completed;
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTodos.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchTodos.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export const { addTodo, toggleTodo } = todosSlice.actions;
export default todosSlice.reducer;
```

## Best Practices

### 1. State Structure

- **Normalize data**: Use entity adapters for collections
- **Separate concerns**: Keep UI state separate from domain state
- **Minimize nesting**: Avoid deeply nested state structures
- **Use derived state**: Calculate values in selectors, not reducers

### 2. Performance

- **Memoize selectors**: Use createSelector for computed values
- **Optimize re-renders**: Use React.memo and specific selectors
- **Avoid large objects**: Split large state into smaller slices
- **Use entity adapters**: For normalized state management

### 3. Code Organization

- **Feature-based structure**: Organize by features, not by file types
- **Co-locate related code**: Keep slice, selectors, and API in same folder
- **Use TypeScript**: For better developer experience and fewer bugs
- **Consistent naming**: Follow naming conventions across the project

### 4. Error Handling

- **Centralized error handling**: Use middleware for global error handling
- **User-friendly messages**: Transform technical errors to user messages
- **Retry mechanisms**: Implement automatic retry for failed requests
- **Error boundaries**: Catch and handle React errors

### 5. Testing

- **Test slices independently**: Test reducers and selectors in isolation
- **Mock API calls**: Use MSW or similar tools for API mocking
- **Integration tests**: Test full user workflows
- **Test edge cases**: Handle loading, error, and empty states

Redux Toolkit provides a modern, efficient way to manage state in React applications. By following these patterns and best practices, you can build scalable, maintainable applications with predictable state management.
