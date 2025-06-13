# Alternative State Management Solutions

## Table of Contents
1. [Modern State Management Landscape](#modern-state-management-landscape)
2. [Zustand - Lightweight State Management](#zustand---lightweight-state-management)
3. [Jotai - Atomic State Management](#jotai---atomic-state-management)
4. [Valtio - Proxy-based State](#valtio---proxy-based-state)
5. [React Query/TanStack Query](#react-query-tanstack-query)
6. [SWR - Data Fetching](#swr---data-fetching)
7. [Recoil - Facebook's Solution](#recoil---facebooks-solution)
8. [Comparison and Decision Matrix](#comparison-and-decision-matrix)
9. [Integration Patterns](#integration-patterns)
10. [Migration Strategies](#migration-strategies)
11. [Best Practices](#best-practices)

## Modern State Management Landscape

The React state management ecosystem has evolved significantly, offering various solutions for different use cases. Understanding when to use each tool is crucial for building efficient applications.

### State Management Categories

```jsx
// 1. Component State - useState, useReducer
function SimpleCounter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <span>{count}</span>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  );
}

// 2. Global Client State - Zustand, Jotai, Redux
// 3. Server State - React Query, SWR
// 4. Form State - React Hook Form, Formik
// 5. URL State - React Router, Next.js Router
```

### Decision Framework

```jsx
// When to use what?
const stateManagementDecision = {
  // Local component state
  useState: {
    when: 'Simple component state, no sharing needed',
    examples: ['Form inputs', 'Toggle states', 'Local UI state']
  },
  
  // Context + useReducer
  contextAPI: {
    when: 'Medium complexity, infrequent updates',
    examples: ['Theme', 'Auth state', 'App configuration']
  },
  
  // Zustand
  zustand: {
    when: 'Global state, simple to medium complexity',
    examples: ['Shopping cart', 'User preferences', 'UI state']
  },
  
  // Redux Toolkit
  redux: {
    when: 'Complex state logic, time travel debugging needed',
    examples: ['Large apps', 'Complex workflows', 'State snapshots']
  },
  
  // React Query
  reactQuery: {
    when: 'Server state management, caching needed',
    examples: ['API data', 'Background updates', 'Optimistic updates']
  }
};
```

## Zustand - Lightweight State Management

Zustand is a small, fast, and scalable state management solution with minimal boilerplate.

### Basic Usage

```jsx
// store/userStore.js
import { create } from 'zustand';

export const useUserStore = create((set, get) => ({
  // State
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,
  
  // Actions
  login: async (credentials) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.login(credentials);
      set({ 
        user: response.user, 
        isAuthenticated: true, 
        loading: false 
      });
    } catch (error) {
      set({ 
        error: error.message, 
        loading: false 
      });
    }
  },
  
  logout: () => {
    set({ 
      user: null, 
      isAuthenticated: false, 
      error: null 
    });
  },
  
  updateProfile: (updates) => {
    set((state) => ({
      user: { ...state.user, ...updates }
    }));
  },
  
  clearError: () => set({ error: null })
}));

// Component usage
function LoginForm() {
  const { login, loading, error, clearError } = useUserStore();
  const [formData, setFormData] = useState({ email: '', password: '' });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(formData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="error">
          {error}
          <button onClick={clearError}>×</button>
        </div>
      )}
      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
        placeholder="Email"
      />
      <input
        type="password"
        value={formData.password}
        onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
        placeholder="Password"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Advanced Zustand Patterns

```jsx
// Slices pattern for large stores
const createUserSlice = (set, get) => ({
  user: null,
  isAuthenticated: false,
  login: async (credentials) => {
    // Login logic
  },
  logout: () => {
    // Logout logic
  }
});

const createCartSlice = (set, get) => ({
  items: [],
  total: 0,
  addItem: (item) => {
    set((state) => ({
      items: [...state.items, item],
      total: state.total + item.price
    }));
  },
  removeItem: (id) => {
    set((state) => ({
      items: state.items.filter(item => item.id !== id),
      total: state.items
        .filter(item => item.id !== id)
        .reduce((sum, item) => sum + item.price, 0)
    }));
  }
});

const createUISlice = (set, get) => ({
  theme: 'light',
  sidebarOpen: false,
  notifications: [],
  toggleTheme: () => {
    set((state) => ({
      theme: state.theme === 'light' ? 'dark' : 'light'
    }));
  },
  toggleSidebar: () => {
    set((state) => ({
      sidebarOpen: !state.sidebarOpen
    }));
  }
});

// Combine slices
export const useAppStore = create((set, get) => ({
  ...createUserSlice(set, get),
  ...createCartSlice(set, get),
  ...createUISlice(set, get)
}));

// Selectors for performance
export const useUser = () => useAppStore((state) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated,
  login: state.login,
  logout: state.logout
}));

export const useCart = () => useAppStore((state) => ({
  items: state.items,
  total: state.total,
  addItem: state.addItem,
  removeItem: state.removeItem
}));
```

### Zustand with Persistence

```jsx
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export const useSettingsStore = create(
  persist(
    (set, get) => ({
      theme: 'light',
      language: 'en',
      notifications: true,
      autoSave: false,
      
      updateSettings: (newSettings) => {
        set((state) => ({
          ...state,
          ...newSettings
        }));
      },
      
      resetSettings: () => {
        set({
          theme: 'light',
          language: 'en',
          notifications: true,
          autoSave: false
        });
      }
    }),
    {
      name: 'app-settings',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        notifications: state.notifications
      }),
      onRehydrateStorage: (state) => {
        console.log('Hydration starts');
        return (state, error) => {
          if (error) {
            console.log('An error happened during hydration', error);
          } else {
            console.log('Hydration finished');
          }
        };
      }
    }
  )
);

// Custom storage implementation
const customStorage = {
  getItem: async (name) => {
    const value = await AsyncStorage.getItem(name);
    return value ? JSON.parse(value) : null;
  },
  setItem: async (name, value) => {
    await AsyncStorage.setItem(name, JSON.stringify(value));
  },
  removeItem: async (name) => {
    await AsyncStorage.removeItem(name);
  }
};
```

### Zustand with Immer

```jsx
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

export const useTodosStore = create(
  immer((set, get) => ({
    todos: [],
    filter: 'all',
    
    addTodo: (todo) => {
      set((state) => {
        state.todos.push({
          ...todo,
          id: Date.now(),
          completed: false,
          createdAt: new Date()
        });
      });
    },
    
    toggleTodo: (id) => {
      set((state) => {
        const todo = state.todos.find(t => t.id === id);
        if (todo) {
          todo.completed = !todo.completed;
        }
      });
    },
    
    deleteTodo: (id) => {
      set((state) => {
        const index = state.todos.findIndex(t => t.id === id);
        if (index !== -1) {
          state.todos.splice(index, 1);
        }
      });
    },
    
    updateTodo: (id, updates) => {
      set((state) => {
        const todo = state.todos.find(t => t.id === id);
        if (todo) {
          Object.assign(todo, updates);
        }
      });
    },
    
    setFilter: (filter) => {
      set((state) => {
        state.filter = filter;
      });
    },
    
    clearCompleted: () => {
      set((state) => {
        state.todos = state.todos.filter(todo => !todo.completed);
      });
    }
  }))
);
```

## Jotai - Atomic State Management

Jotai provides atomic state management where state is composed of atoms.

### Basic Atoms

```jsx
// atoms/userAtoms.js
import { atom } from 'jotai';

// Primitive atoms
export const userAtom = atom(null);
export const loadingAtom = atom(false);
export const errorAtom = atom(null);

// Derived atoms
export const isAuthenticatedAtom = atom(
  (get) => get(userAtom) !== null
);

export const userNameAtom = atom(
  (get) => get(userAtom)?.name || 'Guest'
);

// Write-only atoms (actions)
export const loginAtom = atom(
  null, // no read function
  async (get, set, credentials) => {
    set(loadingAtom, true);
    set(errorAtom, null);
    
    try {
      const response = await authAPI.login(credentials);
      set(userAtom, response.user);
    } catch (error) {
      set(errorAtom, error.message);
    } finally {
      set(loadingAtom, false);
    }
  }
);

export const logoutAtom = atom(
  null,
  async (get, set) => {
    set(loadingAtom, true);
    
    try {
      await authAPI.logout();
      set(userAtom, null);
      set(errorAtom, null);
    } catch (error) {
      set(errorAtom, error.message);
    } finally {
      set(loadingAtom, false);
    }
  }
);

// Component usage
import { useAtom, useAtomValue, useSetAtom } from 'jotai';

function UserProfile() {
  const [user, setUser] = useAtom(userAtom);
  const isAuthenticated = useAtomValue(isAuthenticatedAtom);
  const userName = useAtomValue(userNameAtom);
  const logout = useSetAtom(logoutAtom);
  
  if (!isAuthenticated) {
    return <LoginForm />;
  }
  
  return (
    <div>
      <h1>Welcome, {userName}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Complex Atoms and Families

```jsx
// atoms/todosAtoms.js
import { atom } from 'jotai';
import { atomFamily } from 'jotai/utils';

// Todo list atom
export const todosAtom = atom([]);

// Todo family for individual todos
export const todoAtomFamily = atomFamily((id) =>
  atom(
    (get) => get(todosAtom).find(todo => todo.id === id),
    (get, set, update) => {
      set(todosAtom, (todos) =>
        todos.map(todo =>
          todo.id === id ? { ...todo, ...update } : todo
        )
      );
    }
  )
);

// Filter atom
export const filterAtom = atom('all');

// Derived atom for filtered todos
export const filteredTodosAtom = atom((get) => {
  const todos = get(todosAtom);
  const filter = get(filterAtom);
  
  switch (filter) {
    case 'completed':
      return todos.filter(todo => todo.completed);
    case 'active':
      return todos.filter(todo => !todo.completed);
    default:
      return todos;
  }
});

// Stats atom
export const todoStatsAtom = atom((get) => {
  const todos = get(todosAtom);
  return {
    total: todos.length,
    completed: todos.filter(todo => todo.completed).length,
    active: todos.filter(todo => !todo.completed).length
  };
});

// Actions
export const addTodoAtom = atom(
  null,
  (get, set, title) => {
    const newTodo = {
      id: Date.now(),
      title,
      completed: false,
      createdAt: new Date()
    };
    set(todosAtom, (todos) => [...todos, newTodo]);
  }
);

export const removeTodoAtom = atom(
  null,
  (get, set, id) => {
    set(todosAtom, (todos) => todos.filter(todo => todo.id !== id));
  }
);

// Component usage
function TodoList() {
  const filteredTodos = useAtomValue(filteredTodosAtom);
  const stats = useAtomValue(todoStatsAtom);
  const addTodo = useSetAtom(addTodoAtom);
  const [filter, setFilter] = useAtom(filterAtom);
  
  return (
    <div>
      <div>
        Total: {stats.total}, 
        Completed: {stats.completed}, 
        Active: {stats.active}
      </div>
      
      <select value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="completed">Completed</option>
      </select>
      
      {filteredTodos.map(todo => (
        <TodoItem key={todo.id} todoId={todo.id} />
      ))}
      
      <button onClick={() => addTodo('New Todo')}>
        Add Todo
      </button>
    </div>
  );
}

function TodoItem({ todoId }) {
  const todoAtom = todoAtomFamily(todoId);
  const [todo, updateTodo] = useAtom(todoAtom);
  const removeTodo = useSetAtom(removeTodoAtom);
  
  return (
    <div>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={(e) => updateTodo({ completed: e.target.checked })}
      />
      <span>{todo.title}</span>
      <button onClick={() => removeTodo(todoId)}>Remove</button>
    </div>
  );
}
```

### Jotai with Async

```jsx
// Async atoms
export const userIdAtom = atom(1);

export const userAtom = atom(async (get) => {
  const userId = get(userIdAtom);
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
});

export const postsAtom = atom(async (get) => {
  const userId = get(userIdAtom);
  const response = await fetch(`/api/users/${userId}/posts`);
  return response.json();
});

// Component with Suspense
function UserProfile() {
  const user = useAtomValue(userAtom);
  const posts = useAtomValue(postsAtom);
  
  return (
    <div>
      <h1>{user.name}</h1>
      <div>
        {posts.map(post => (
          <article key={post.id}>
            <h3>{post.title}</h3>
            <p>{post.excerpt}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

// Wrap with Suspense
function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <UserProfile />
    </Suspense>
  );
}
```

## Valtio - Proxy-based State

Valtio creates a proxy-based state that automatically tracks mutations.

### Basic Usage

```jsx
// store/appState.js
import { proxy, useSnapshot } from 'valtio';

export const state = proxy({
  user: null,
  settings: {
    theme: 'light',
    language: 'en'
  },
  todos: [],
  ui: {
    sidebarOpen: false,
    loading: false,
    error: null
  }
});

// Actions (just regular functions)
export const actions = {
  login: async (credentials) => {
    state.ui.loading = true;
    state.ui.error = null;
    
    try {
      const response = await authAPI.login(credentials);
      state.user = response.user;
    } catch (error) {
      state.ui.error = error.message;
    } finally {
      state.ui.loading = false;
    }
  },
  
  logout: () => {
    state.user = null;
    state.ui.error = null;
  },
  
  addTodo: (title) => {
    state.todos.push({
      id: Date.now(),
      title,
      completed: false,
      createdAt: new Date()
    });
  },
  
  toggleTodo: (id) => {
    const todo = state.todos.find(t => t.id === id);
    if (todo) {
      todo.completed = !todo.completed;
    }
  },
  
  updateSettings: (newSettings) => {
    Object.assign(state.settings, newSettings);
  },
  
  toggleSidebar: () => {
    state.ui.sidebarOpen = !state.ui.sidebarOpen;
  }
};

// Component usage
function App() {
  const snap = useSnapshot(state);
  
  return (
    <div className={`app theme-${snap.settings.theme}`}>
      <Sidebar 
        isOpen={snap.ui.sidebarOpen} 
        onToggle={actions.toggleSidebar}
      />
      <main>
        {snap.ui.loading && <LoadingSpinner />}
        {snap.ui.error && <ErrorMessage message={snap.ui.error} />}
        {snap.user ? <Dashboard /> : <LoginForm />}
      </main>
    </div>
  );
}

function TodoList() {
  const snap = useSnapshot(state);
  
  return (
    <div>
      {snap.todos.map(todo => (
        <div key={todo.id}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => actions.toggleTodo(todo.id)}
          />
          <span>{todo.title}</span>
        </div>
      ))}
      <button onClick={() => actions.addTodo('New Todo')}>
        Add Todo
      </button>
    </div>
  );
}
```

### Advanced Valtio Patterns

```jsx
// Computed values with derive
import { derive } from 'valtio/utils';

export const derived = derive({
  completedTodos: (get) => get(state).todos.filter(todo => todo.completed),
  activeTodos: (get) => get(state).todos.filter(todo => !todo.completed),
  todoStats: (get) => {
    const todos = get(state).todos;
    return {
      total: todos.length,
      completed: todos.filter(todo => todo.completed).length,
      active: todos.filter(todo => !todo.completed).length
    };
  },
  isAuthenticated: (get) => get(state).user !== null
});

// Subscriptions for side effects
import { subscribe } from 'valtio';

// Auto-save to localStorage
subscribe(state.settings, () => {
  localStorage.setItem('settings', JSON.stringify(state.settings));
});

// Log user actions
subscribe(state.user, (ops) => {
  console.log('User state changed:', ops);
});

// Middleware pattern
const withLogging = (target) => {
  return new Proxy(target, {
    set(obj, prop, value) {
      console.log(`Setting ${prop} to`, value);
      obj[prop] = value;
      return true;
    }
  });
};

export const loggedState = withLogging(state);
```

## React Query/TanStack Query

React Query excels at server state management with built-in caching, background updates, and optimistic updates.

### Basic Setup

```jsx
// setup/queryClient.js
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 3,
      refetchOnWindowFocus: false
    },
    mutations: {
      retry: 1
    }
  }
});

// App.jsx
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/todos" element={<TodosPage />} />
        </Routes>
      </Router>
      <ReactQueryDevtools />
    </QueryClientProvider>
  );
}
```

### Queries and Mutations

```jsx
// hooks/useTodos.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Query hooks
export function useTodos(filters = {}) {
  return useQuery({
    queryKey: ['todos', filters],
    queryFn: () => todosAPI.getTodos(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
    select: (data) => data.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  });
}

export function useTodo(id) {
  return useQuery({
    queryKey: ['todo', id],
    queryFn: () => todosAPI.getTodo(id),
    enabled: !!id, // Only run if id exists
    staleTime: 1000 * 60 * 10 // 10 minutes for individual todos
  });
}

// Mutation hooks
export function useCreateTodo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: todosAPI.createTodo,
    onMutate: async (newTodo) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['todos'] });
      
      // Snapshot previous value
      const previousTodos = queryClient.getQueryData(['todos']);
      
      // Optimistically update
      queryClient.setQueryData(['todos'], (old) => [
        ...old,
        { ...newTodo, id: Date.now(), createdAt: new Date() }
      ]);
      
      return { previousTodos };
    },
    onError: (err, newTodo, context) => {
      // Rollback on error
      queryClient.setQueryData(['todos'], context.previousTodos);
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    }
  });
}

export function useUpdateTodo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, ...updates }) => todosAPI.updateTodo(id, updates),
    onMutate: async ({ id, ...updates }) => {
      await queryClient.cancelQueries({ queryKey: ['todo', id] });
      
      const previousTodo = queryClient.getQueryData(['todo', id]);
      
      queryClient.setQueryData(['todo', id], (old) => ({
        ...old,
        ...updates
      }));
      
      // Update in todos list too
      queryClient.setQueryData(['todos'], (old) =>
        old?.map(todo => 
          todo.id === id ? { ...todo, ...updates } : todo
        )
      );
      
      return { previousTodo };
    },
    onError: (err, { id }, context) => {
      queryClient.setQueryData(['todo', id], context.previousTodo);
    },
    onSettled: (data, error, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['todo', id] });
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    }
  });
}

export function useDeleteTodo() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: todosAPI.deleteTodo,
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] });
      
      const previousTodos = queryClient.getQueryData(['todos']);
      
      queryClient.setQueryData(['todos'], (old) =>
        old?.filter(todo => todo.id !== id)
      );
      
      return { previousTodos };
    },
    onError: (err, id, context) => {
      queryClient.setQueryData(['todos'], context.previousTodos);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    }
  });
}

// Component usage
function TodosPage() {
  const [filter, setFilter] = useState('all');
  
  const { 
    data: todos = [], 
    isLoading, 
    error, 
    refetch 
  } = useTodos({ status: filter });
  
  const createTodoMutation = useCreateTodo();
  const updateTodoMutation = useUpdateTodo();
  const deleteTodoMutation = useDeleteTodo();
  
  const handleCreateTodo = async (title) => {
    try {
      await createTodoMutation.mutateAsync({ title });
    } catch (error) {
      console.error('Failed to create todo:', error);
    }
  };
  
  if (isLoading) return <div>Loading todos...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <TodoForm onSubmit={handleCreateTodo} />
      <FilterButtons filter={filter} onFilterChange={setFilter} />
      <TodoList 
        todos={todos}
        onUpdate={updateTodoMutation.mutate}
        onDelete={deleteTodoMutation.mutate}
      />
    </div>
  );
}
```

### Advanced React Query Patterns

```jsx
// Infinite queries for pagination
export function useInfiniteTodos() {
  return useInfiniteQuery({
    queryKey: ['todos', 'infinite'],
    queryFn: ({ pageParam = 0 }) => 
      todosAPI.getTodos({ offset: pageParam, limit: 20 }),
    getNextPageParam: (lastPage, pages) => 
      lastPage.hasMore ? pages.length * 20 : undefined,
    select: (data) => ({
      pages: data.pages,
      pageParams: data.pageParams,
      todos: data.pages.flatMap(page => page.data)
    })
  });
}

// Dependent queries
export function useUserTodos(userId) {
  const { data: user } = useUser(userId);
  
  return useQuery({
    queryKey: ['todos', 'user', userId],
    queryFn: () => todosAPI.getUserTodos(userId),
    enabled: !!user, // Only fetch if user exists
    staleTime: 1000 * 60 * 5
  });
}

// Parallel queries
export function useDashboardData() {
  const todosQuery = useTodos();
  const statsQuery = useQuery({
    queryKey: ['stats'],
    queryFn: statsAPI.getStats
  });
  const notificationsQuery = useQuery({
    queryKey: ['notifications'],
    queryFn: notificationsAPI.getNotifications
  });
  
  return {
    todos: todosQuery.data,
    stats: statsQuery.data,
    notifications: notificationsQuery.data,
    isLoading: todosQuery.isLoading || statsQuery.isLoading || notificationsQuery.isLoading,
    error: todosQuery.error || statsQuery.error || notificationsQuery.error
  };
}

// Background updates
export function useRealtimeTodos() {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    const eventSource = new EventSource('/api/todos/stream');
    
    eventSource.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      // Update cache based on the event
      switch (update.type) {
        case 'TODO_CREATED':
          queryClient.setQueryData(['todos'], (old) => [
            update.todo,
            ...old
          ]);
          break;
          
        case 'TODO_UPDATED':
          queryClient.setQueryData(['todos'], (old) =>
            old.map(todo => 
              todo.id === update.todo.id ? update.todo : todo
            )
          );
          break;
          
        case 'TODO_DELETED':
          queryClient.setQueryData(['todos'], (old) =>
            old.filter(todo => todo.id !== update.todoId)
          );
          break;
      }
    };
    
    return () => eventSource.close();
  }, [queryClient]);
  
  return useTodos();
}
```

## SWR - Data Fetching

SWR is a lightweight data fetching library with a focus on user experience.

### Basic Usage

```jsx
// hooks/useSWR.js
import useSWR from 'swr';

const fetcher = (url) => fetch(url).then(res => res.json());

export function useTodos() {
  const { data, error, mutate } = useSWR('/api/todos', fetcher, {
    refreshInterval: 60000, // Refresh every minute
    revalidateOnFocus: true,
    revalidateOnReconnect: true
  });
  
  return {
    todos: data,
    isLoading: !error && !data,
    error,
    mutate
  };
}

export function useTodo(id) {
  const { data, error, mutate } = useSWR(
    id ? `/api/todos/${id}` : null,
    fetcher
  );
  
  return {
    todo: data,
    isLoading: !error && !data,
    error,
    mutate
  };
}

// Component usage
function TodoList() {
  const { todos, isLoading, error, mutate } = useTodos();
  
  const handleCreateTodo = async (title) => {
    // Optimistic update
    const newTodo = { id: Date.now(), title, completed: false };
    mutate([newTodo, ...todos], false);
    
    try {
      await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });
      
      // Revalidate
      mutate();
    } catch (error) {
      // Rollback
      mutate();
    }
  };
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {todos?.map(todo => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
      <button onClick={() => handleCreateTodo('New Todo')}>
        Add Todo
      </button>
    </div>
  );
}
```

### SWR with Global Configuration

```jsx
// App.jsx
import { SWRConfig } from 'swr';

function App() {
  return (
    <SWRConfig
      value={{
        fetcher: (url) => fetch(url).then(res => res.json()),
        refreshInterval: 60000,
        revalidateOnFocus: false,
        errorRetryCount: 3,
        onError: (error) => {
          console.error('SWR Error:', error);
          // Global error handling
        }
      }}
    >
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/todos" element={<TodosPage />} />
        </Routes>
      </Router>
    </SWRConfig>
  );
}
```

## Recoil - Facebook's Solution

Recoil provides a graph-based state management approach.

### Basic Usage

```jsx
// atoms/userAtoms.js
import { atom, selector } from 'recoil';

export const userState = atom({
  key: 'userState',
  default: null
});

export const isAuthenticatedSelector = selector({
  key: 'isAuthenticatedSelector',
  get: ({ get }) => {
    const user = get(userState);
    return user !== null;
  }
});

// atoms/todosAtoms.js
export const todosState = atom({
  key: 'todosState',
  default: []
});

export const todoFilterState = atom({
  key: 'todoFilterState',
  default: 'all'
});

export const filteredTodosSelector = selector({
  key: 'filteredTodosSelector',
  get: ({ get }) => {
    const todos = get(todosState);
    const filter = get(todoFilterState);
    
    switch (filter) {
      case 'completed':
        return todos.filter(todo => todo.completed);
      case 'active':
        return todos.filter(todo => !todo.completed);
      default:
        return todos;
    }
  }
});

// Component usage
import { useRecoilState, useRecoilValue } from 'recoil';

function TodoList() {
  const [todos, setTodos] = useRecoilState(todosState);
  const [filter, setFilter] = useRecoilState(todoFilterState);
  const filteredTodos = useRecoilValue(filteredTodosSelector);
  
  const addTodo = (title) => {
    setTodos(prev => [
      ...prev,
      {
        id: Date.now(),
        title,
        completed: false
      }
    ]);
  };
  
  return (
    <div>
      <select value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="completed">Completed</option>
      </select>
      
      {filteredTodos.map(todo => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
      
      <button onClick={() => addTodo('New Todo')}>
        Add Todo
      </button>
    </div>
  );
}

// App with RecoilRoot
import { RecoilRoot } from 'recoil';

function App() {
  return (
    <RecoilRoot>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/todos" element={<TodoList />} />
        </Routes>
      </Router>
    </RecoilRoot>
  );
}
```

## Comparison and Decision Matrix

### Feature Comparison

| Feature | Zustand | Jotai | Valtio | React Query | Redux Toolkit |
|---------|---------|-------|--------|-------------|---------------|
| Bundle Size | 2.7kb | 3.8kb | 3.5kb | 36kb | 52kb |
| Learning Curve | Low | Medium | Low | Medium | High |
| TypeScript | Excellent | Excellent | Good | Excellent | Excellent |
| DevTools | Basic | React DevTools | Basic | Excellent | Excellent |
| Async Support | Manual | Built-in | Manual | Excellent | Good |
| Server State | Manual | Manual | Manual | Excellent | Manual |
| Boilerplate | Minimal | Minimal | Minimal | Low | Medium |

### Use Case Matrix

```jsx
const useCaseDecisionMatrix = {
  // Simple global state
  simpleGlobalState: {
    recommended: ['Zustand', 'Valtio'],
    reason: 'Minimal boilerplate, easy to learn'
  },
  
  // Complex state logic
  complexStateLogic: {
    recommended: ['Redux Toolkit', 'Jotai'],
    reason: 'Better for complex state relationships'
  },
  
  // Server state management
  serverState: {
    recommended: ['React Query', 'SWR'],
    reason: 'Built-in caching, background updates, optimistic updates'
  },
  
  // Real-time applications
  realTimeApps: {
    recommended: ['React Query + WebSocket', 'SWR + WebSocket'],
    reason: 'Background synchronization capabilities'
  },
  
  // Form-heavy applications
  formHeavyApps: {
    recommended: ['React Hook Form + Zustand', 'Formik + Context'],
    reason: 'Specialized form libraries work better'
  },
  
  // Large team projects
  largeTeamProjects: {
    recommended: ['Redux Toolkit', 'React Query'],
    reason: 'Better tooling, established patterns'
  },
  
  // Prototyping
  prototyping: {
    recommended: ['Zustand', 'Valtio'],
    reason: 'Quick to set up, minimal configuration'
  }
};
```

### Performance Comparison

```jsx
// Performance characteristics
const performanceComparison = {
  zustand: {
    reRenders: 'Minimal - only components that use changed state',
    memoryUsage: 'Low - simple object references',
    bundleSize: '2.7kb gzipped'
  },
  
  jotai: {
    reRenders: 'Atomic - only components using specific atoms',
    memoryUsage: 'Medium - atom dependency graph',
    bundleSize: '3.8kb gzipped'
  },
  
  valtio: {
    reRenders: 'Efficient - proxy-based fine-grained reactivity',
    memoryUsage: 'Medium - proxy overhead',
    bundleSize: '3.5kb gzipped'
  },
  
  reactQuery: {
    reRenders: 'Optimized - smart query result memoization',
    memoryUsage: 'Higher - extensive caching',
    bundleSize: '36kb gzipped'
  },
  
  reduxToolkit: {
    reRenders: 'Good - with proper selectors',
    memoryUsage: 'Medium - normalized state',
    bundleSize: '52kb gzipped'
  }
};
```

## Integration Patterns

### Hybrid Approach

```jsx
// Combining multiple solutions
// Client state with Zustand
export const useClientStore = create((set) => ({
  theme: 'light',
  sidebarOpen: false,
  toggleTheme: () => set(state => ({ 
    theme: state.theme === 'light' ? 'dark' : 'light' 
  })),
  toggleSidebar: () => set(state => ({ 
    sidebarOpen: !state.sidebarOpen 
  }))
}));

// Server state with React Query
export function useTodos() {
  return useQuery({
    queryKey: ['todos'],
    queryFn: todosAPI.getTodos
  });
}

// Form state with React Hook Form
export function useCreateTodoForm() {
  const createTodo = useCreateTodo();
  
  return useForm({
    onSubmit: async (data) => {
      await createTodo.mutateAsync(data);
    }
  });
}

// Component using all three
function TodoApp() {
  const { theme, toggleTheme } = useClientStore();
  const { data: todos } = useTodos();
  const form = useCreateTodoForm();
  
  return (
    <div className={`app theme-${theme}`}>
      <button onClick={toggleTheme}>Toggle Theme</button>
      <form onSubmit={form.handleSubmit}>
        <input {...form.register('title')} />
        <button type="submit">Add Todo</button>
      </form>
      <TodoList todos={todos} />
    </div>
  );
}
```

### State Boundaries

```jsx
// Clear separation of concerns
const stateArchitecture = {
  // Local component state
  local: {
    tools: ['useState', 'useReducer'],
    examples: ['Form inputs', 'Toggle states', 'Local UI state'],
    when: 'State not shared between components'
  },
  
  // Client-side global state
  clientGlobal: {
    tools: ['Zustand', 'Jotai', 'Context'],
    examples: ['Theme', 'User preferences', 'App configuration'],
    when: 'Shared across many components, infrequent updates'
  },
  
  // Server state
  server: {
    tools: ['React Query', 'SWR'],
    examples: ['API data', 'User profile', 'Real-time data'],
    when: 'Data from external sources, needs caching'
  },
  
  // URL state
  url: {
    tools: ['React Router', 'Next.js Router'],
    examples: ['Current page', 'Search filters', 'Pagination'],
    when: 'State should survive page refresh'
  },
  
  // Form state
  form: {
    tools: ['React Hook Form', 'Formik'],
    examples: ['Form data', 'Validation', 'Form UI state'],
    when: 'Complex forms with validation'
  }
};
```

## Migration Strategies

### From Redux to Zustand

```jsx
// Before: Redux slice
const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [], loading: false },
  reducers: {
    addTodo: (state, action) => {
      state.items.push(action.payload);
    },
    toggleTodo: (state, action) => {
      const todo = state.items.find(t => t.id === action.payload);
      if (todo) todo.completed = !todo.completed;
    }
  }
});

// After: Zustand store
const useTodosStore = create((set, get) => ({
  items: [],
  loading: false,
  
  addTodo: (todo) => set(state => ({
    items: [...state.items, todo]
  })),
  
  toggleTodo: (id) => set(state => ({
    items: state.items.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    )
  }))
}));

// Migration component wrapper
function TodosProvider({ children }) {
  // Gradually migrate by providing both APIs
  const zustandStore = useTodosStore();
  const dispatch = useAppDispatch();
  
  // Bridge Zustand to Redux actions
  useEffect(() => {
    const unsubscribe = useTodosStore.subscribe(
      (state) => state.items,
      (items) => {
        dispatch(todosSlice.actions.setTodos(items));
      }
    );
    return unsubscribe;
  }, [dispatch]);
  
  return children;
}
```

### From Context to Jotai

```jsx
// Before: Context API
const UserContext = createContext();

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const login = async (credentials) => {
    setLoading(true);
    try {
      const user = await authAPI.login(credentials);
      setUser(user);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <UserContext.Provider value={{ user, loading, login }}>
      {children}
    </UserContext.Provider>
  );
}

// After: Jotai atoms
export const userAtom = atom(null);
export const loadingAtom = atom(false);

export const loginAtom = atom(
  null,
  async (get, set, credentials) => {
    set(loadingAtom, true);
    try {
      const user = await authAPI.login(credentials);
      set(userAtom, user);
    } finally {
      set(loadingAtom, false);
    }
  }
);

// Migration bridge
export function useUser() {
  const [user, setUser] = useAtom(userAtom);
  const [loading] = useAtom(loadingAtom);
  const login = useSetAtom(loginAtom);
  
  return { user, loading, login };
}
```

## Best Practices

### 1. Choose the Right Tool

```jsx
// Decision flowchart
const chooseStateTool = (requirements) => {
  if (requirements.serverState) {
    return 'React Query or SWR';
  }
  
  if (requirements.complexity === 'low') {
    return 'useState or Zustand';
  }
  
  if (requirements.complexity === 'medium') {
    return 'Zustand or Jotai';
  }
  
  if (requirements.complexity === 'high') {
    return 'Redux Toolkit or Jotai';
  }
  
  if (requirements.teamSize === 'large') {
    return 'Redux Toolkit';
  }
  
  return 'Zustand';
};
```

### 2. Performance Optimization

```jsx
// Optimize selectors
// ❌ Bad - creates new object every render
const selectUserData = (state) => ({
  name: state.user.name,
  email: state.user.email
});

// ✅ Good - memoized selector
const selectUserData = createSelector(
  [state => state.user],
  (user) => ({
    name: user.name,
    email: user.email
  })
);

// ❌ Bad - subscribes to entire state
const user = useAppSelector(state => state);

// ✅ Good - specific subscription
const userName = useAppSelector(state => state.user.name);
```

### 3. Type Safety

```tsx
// Define clear interfaces
interface User {
  id: string;
  name: string;
  email: string;
}

interface AppState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

// Use discriminated unions for actions
type UserAction = 
  | { type: 'SET_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string };
```

### 4. Testing

```jsx
// Test state logic separately
describe('useTodosStore', () => {
  beforeEach(() => {
    useTodosStore.setState({ items: [] });
  });
  
  test('adds todo', () => {
    const { addTodo } = useTodosStore.getState();
    addTodo({ id: 1, title: 'Test', completed: false });
    
    const { items } = useTodosStore.getState();
    expect(items).toHaveLength(1);
    expect(items[0].title).toBe('Test');
  });
});
```

### 5. Error Handling

```jsx
// Centralized error handling
const errorHandler = (error, errorInfo) => {
  console.error('State error:', error, errorInfo);
  
  // Report to error tracking service
  errorTracker.captureException(error);
  
  // Show user-friendly message
  toast.error('Something went wrong. Please try again.');
};

// Use error boundaries
function StateErrorBoundary({ children }) {
  return (
    <ErrorBoundary 
      FallbackComponent={ErrorFallback}
      onError={errorHandler}
    >
      {children}
    </ErrorBoundary>
  );
}
```

Choose the right state management solution based on your specific needs, team size, and application complexity. Each tool has its strengths and optimal use cases.
