# 🎣 Advanced Todo App Implementation Guide

> **Project**: Advanced Todo App with Custom Hooks  
> **Level**: Intermediate  
> **Estimated Time**: 4-6 hours  
> **Focus**: Custom hooks, useReducer, advanced state patterns

---

## 🚀 Quick Start (30 minutes)

### Step 1: Setup Project
```bash
npx create-react-app advanced-todo-app
cd advanced-todo-app
npm install uuid date-fns
npm start
```

### Step 2: Create Basic Structure
```jsx
// src/App.js
import TodoApp from './components/TodoApp';
import './App.css';

function App() {
  return (
    <div className="App">
      <TodoApp />
    </div>
  );
}

export default App;
```

### Step 3: Basic Todo Hook
```jsx
// src/hooks/useTodos.js
import { useReducer, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useLocalStorage } from './useLocalStorage';

const initialState = {
  todos: [],
  filter: 'all',
  searchTerm: '',
  selectedTodos: [],
  history: []
};

function todoReducer(state, action) {
  switch (action.type) {
    case 'LOAD_TODOS':
      return { ...state, todos: action.payload };
    case 'ADD_TODO':
      const newTodo = {
        id: uuidv4(),
        text: action.payload.text,
        completed: false,
        category: action.payload.category || 'general',
        priority: action.payload.priority || 'medium',
        createdAt: new Date().toISOString(),
        tags: action.payload.tags || []
      };
      return { 
        ...state, 
        todos: [...state.todos, newTodo],
        history: [...state.history, { action: 'ADD', todo: newTodo }]
      };
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed }
            : todo
        )
      };
    case 'DELETE_TODO':
      const todoToDelete = state.todos.find(t => t.id === action.payload);
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload),
        history: [...state.history, { action: 'DELETE', todo: todoToDelete }]
      };
    case 'SET_FILTER':
      return { ...state, filter: action.payload };
    case 'SET_SEARCH':
      return { ...state, searchTerm: action.payload };
    default:
      return state;
  }
}

export const useTodos = () => {
  const [savedTodos, setSavedTodos] = useLocalStorage('todos', []);
  const [state, dispatch] = useReducer(todoReducer, {
    ...initialState,
    todos: savedTodos
  });

  const addTodo = useCallback((todoData) => {
    dispatch({ type: 'ADD_TODO', payload: todoData });
  }, []);

  const toggleTodo = useCallback((id) => {
    dispatch({ type: 'TOGGLE_TODO', payload: id });
  }, []);

  const deleteTodo = useCallback((id) => {
    dispatch({ type: 'DELETE_TODO', payload: id });
  }, []);

  const setFilter = useCallback((filter) => {
    dispatch({ type: 'SET_FILTER', payload: filter });
  }, []);

  const setSearchTerm = useCallback((term) => {
    dispatch({ type: 'SET_SEARCH', payload: term });
  }, []);

  // Save to localStorage whenever todos change
  React.useEffect(() => {
    setSavedTodos(state.todos);
  }, [state.todos, setSavedTodos]);

  return {
    ...state,
    addTodo,
    toggleTodo,
    deleteTodo,
    setFilter,
    setSearchTerm
  };
};
```

---

## 📚 Complete Implementation

### 1. Custom Hooks Foundation

#### Local Storage Hook
```jsx
{% raw %}
{% raw %}
// src/hooks/useLocalStorage.js
import { useState, useEffect } from 'react';

export const useLocalStorage = (key, initialValue) => {
  // Get from local storage then parse stored json or return initialValue
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function that persists the new value to localStorage
  const setValue = (value) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
};
{% endraw %}
{% endraw %}
```

#### Debounce Hook
```jsx
// src/hooks/useDebounce.js
import { useState, useEffect } from 'react';

export const useDebounce = (value, delay) => {
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
};
```

#### Keyboard Shortcuts Hook
```jsx
{% raw %}
{% raw %}
// src/hooks/useKeyboardShortcuts.js
import { useEffect, useCallback } from 'react';

export const useKeyboardShortcuts = (shortcuts) => {
  const handleKeyPress = useCallback((event) => {
    const { key, ctrlKey, shiftKey, altKey } = event;
    const combination = `${ctrlKey ? 'ctrl+' : ''}${shiftKey ? 'shift+' : ''}${altKey ? 'alt+' : ''}${key.toLowerCase()}`;
    
    if (shortcuts[combination]) {
      event.preventDefault();
      shortcuts[combination]();
    }
  }, [shortcuts]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyPress);
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleKeyPress]);
};
{% endraw %}
{% endraw %}
```

### 2. Enhanced Todo Reducer
```jsx
// src/reducers/todoReducer.js
import { v4 as uuidv4 } from 'uuid';

export const initialState = {
  todos: [],
  filter: 'all',
  sortBy: 'createdAt',
  sortOrder: 'desc',
  searchTerm: '',
  selectedTodos: [],
  history: [],
  categories: ['general', 'work', 'personal', 'shopping'],
  showCompleted: true
};

export function todoReducer(state, action) {
  switch (action.type) {
    case 'LOAD_TODOS':
      return { ...state, todos: action.payload };

    case 'ADD_TODO':
      const newTodo = {
        id: uuidv4(),
        text: action.payload.text,
        completed: false,
        category: action.payload.category || 'general',
        priority: action.payload.priority || 'medium',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        tags: action.payload.tags || [],
        dueDate: action.payload.dueDate || null
      };
      return { 
        ...state, 
        todos: [...state.todos, newTodo],
        history: [...state.history.slice(-9), { 
          action: 'ADD', 
          todo: newTodo, 
          timestamp: Date.now() 
        }]
      };

    case 'UPDATE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload.id
            ? { ...todo, ...action.payload.updates, updatedAt: new Date().toISOString() }
            : todo
        )
      };

    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed, updatedAt: new Date().toISOString() }
            : todo
        )
      };

    case 'DELETE_TODO':
      const todoToDelete = state.todos.find(t => t.id === action.payload);
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload),
        selectedTodos: state.selectedTodos.filter(id => id !== action.payload),
        history: [...state.history.slice(-9), { 
          action: 'DELETE', 
          todo: todoToDelete, 
          timestamp: Date.now() 
        }]
      };

    case 'BULK_DELETE':
      const todosToDelete = state.todos.filter(t => action.payload.includes(t.id));
      return {
        ...state,
        todos: state.todos.filter(todo => !action.payload.includes(todo.id)),
        selectedTodos: [],
        history: [...state.history.slice(-9), { 
          action: 'BULK_DELETE', 
          todos: todosToDelete, 
          timestamp: Date.now() 
        }]
      };

    case 'BULK_TOGGLE':
      return {
        ...state,
        todos: state.todos.map(todo =>
          action.payload.includes(todo.id)
            ? { ...todo, completed: action.payload.completed, updatedAt: new Date().toISOString() }
            : todo
        ),
        selectedTodos: []
      };

    case 'SELECT_TODO':
      const isSelected = state.selectedTodos.includes(action.payload);
      return {
        ...state,
        selectedTodos: isSelected
          ? state.selectedTodos.filter(id => id !== action.payload)
          : [...state.selectedTodos, action.payload]
      };

    case 'SELECT_ALL':
      const visibleTodos = getFilteredTodos(state);
      const allSelected = visibleTodos.every(todo => state.selectedTodos.includes(todo.id));
      return {
        ...state,
        selectedTodos: allSelected ? [] : visibleTodos.map(todo => todo.id)
      };

    case 'CLEAR_SELECTION':
      return { ...state, selectedTodos: [] };

    case 'SET_FILTER':
      return { ...state, filter: action.payload };

    case 'SET_SORT':
      return { 
        ...state, 
        sortBy: action.payload.sortBy,
        sortOrder: action.payload.sortOrder 
      };

    case 'SET_SEARCH':
      return { ...state, searchTerm: action.payload };

    case 'TOGGLE_SHOW_COMPLETED':
      return { ...state, showCompleted: !state.showCompleted };

    case 'ADD_CATEGORY':
      return {
        ...state,
        categories: [...state.categories, action.payload]
      };

    case 'UNDO':
      const lastAction = state.history[state.history.length - 1];
      if (!lastAction) return state;

      let newTodos = [...state.todos];
      if (lastAction.action === 'DELETE') {
        newTodos.push(lastAction.todo);
      } else if (lastAction.action === 'ADD') {
        newTodos = newTodos.filter(t => t.id !== lastAction.todo.id);
      } else if (lastAction.action === 'BULK_DELETE') {
        newTodos.push(...lastAction.todos);
      }

      return {
        ...state,
        todos: newTodos,
        history: state.history.slice(0, -1)
      };

    case 'IMPORT_TODOS':
      return {
        ...state,
        todos: [...state.todos, ...action.payload],
        history: [...state.history.slice(-9), { 
          action: 'IMPORT', 
          count: action.payload.length, 
          timestamp: Date.now() 
        }]
      };

    default:
      return state;
  }
}

// Helper function to get filtered todos
function getFilteredTodos(state) {
  let filtered = state.todos;

  // Filter by completion status
  if (state.filter === 'active') {
    filtered = filtered.filter(todo => !todo.completed);
  } else if (state.filter === 'completed') {
    filtered = filtered.filter(todo => todo.completed);
  } else if (state.filter !== 'all') {
    // Filter by category
    filtered = filtered.filter(todo => todo.category === state.filter);
  }

  // Filter by search term
  if (state.searchTerm) {
    filtered = filtered.filter(todo =>
      todo.text.toLowerCase().includes(state.searchTerm.toLowerCase()) ||
      todo.tags.some(tag => tag.toLowerCase().includes(state.searchTerm.toLowerCase()))
    );
  }

  // Hide completed if option is set
  if (!state.showCompleted) {
    filtered = filtered.filter(todo => !todo.completed);
  }

  // Sort
  filtered.sort((a, b) => {
    let aValue = a[state.sortBy];
    let bValue = b[state.sortBy];

    if (state.sortBy === 'priority') {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      aValue = priorityOrder[a.priority];
      bValue = priorityOrder[b.priority];
    }

    if (state.sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  return filtered;
}
```

### 3. Enhanced Todo Hook
```jsx
{% raw %}
{% raw %}
// src/hooks/useTodos.js (Enhanced version)
import { useReducer, useCallback, useMemo, useEffect } from 'react';
import { useLocalStorage } from './useLocalStorage';
import { useDebounce } from './useDebounce';
import { todoReducer, initialState } from '../reducers/todoReducer';
import { format } from 'date-fns';

export const useTodos = () => {
  const [savedTodos, setSavedTodos] = useLocalStorage('todos', []);
  const [savedCategories, setSavedCategories] = useLocalStorage('categories', initialState.categories);
  
  const [state, dispatch] = useReducer(todoReducer, {
    ...initialState,
    todos: savedTodos,
    categories: savedCategories
  });

  const debouncedSearchTerm = useDebounce(state.searchTerm, 300);

  // Memoized filtered and sorted todos
  const filteredTodos = useMemo(() => {
    let filtered = state.todos;

    // Filter by completion status
    if (state.filter === 'active') {
      filtered = filtered.filter(todo => !todo.completed);
    } else if (state.filter === 'completed') {
      filtered = filtered.filter(todo => todo.completed);
    } else if (state.filter !== 'all') {
      // Filter by category
      filtered = filtered.filter(todo => todo.category === state.filter);
    }

    // Filter by search term
    if (debouncedSearchTerm) {
      filtered = filtered.filter(todo =>
        todo.text.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
        todo.tags.some(tag => tag.toLowerCase().includes(debouncedSearchTerm.toLowerCase()))
      );
    }

    // Hide completed if option is set
    if (!state.showCompleted) {
      filtered = filtered.filter(todo => !todo.completed);
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue = a[state.sortBy];
      let bValue = b[state.sortBy];

      if (state.sortBy === 'priority') {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        aValue = priorityOrder[a.priority];
        bValue = priorityOrder[b.priority];
      }

      if (state.sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [state.todos, state.filter, state.sortBy, state.sortOrder, debouncedSearchTerm, state.showCompleted]);

  // Statistics
  const stats = useMemo(() => {
    const total = state.todos.length;
    const completed = state.todos.filter(t => t.completed).length;
    const active = total - completed;
    const overdue = state.todos.filter(t => 
      t.dueDate && new Date(t.dueDate) < new Date() && !t.completed
    ).length;

    return { total, completed, active, overdue };
  }, [state.todos]);

  // Actions
  const addTodo = useCallback((todoData) => {
    dispatch({ type: 'ADD_TODO', payload: todoData });
  }, []);

  const updateTodo = useCallback((id, updates) => {
    dispatch({ type: 'UPDATE_TODO', payload: { id, updates } });
  }, []);

  const toggleTodo = useCallback((id) => {
    dispatch({ type: 'TOGGLE_TODO', payload: id });
  }, []);

  const deleteTodo = useCallback((id) => {
    dispatch({ type: 'DELETE_TODO', payload: id });
  }, []);

  const bulkDelete = useCallback((ids) => {
    dispatch({ type: 'BULK_DELETE', payload: ids });
  }, []);

  const bulkToggle = useCallback((ids, completed) => {
    dispatch({ type: 'BULK_TOGGLE', payload: { ids, completed } });
  }, []);

  const selectTodo = useCallback((id) => {
    dispatch({ type: 'SELECT_TODO', payload: id });
  }, []);

  const selectAll = useCallback(() => {
    dispatch({ type: 'SELECT_ALL' });
  }, []);

  const clearSelection = useCallback(() => {
    dispatch({ type: 'CLEAR_SELECTION' });
  }, []);

  const setFilter = useCallback((filter) => {
    dispatch({ type: 'SET_FILTER', payload: filter });
  }, []);

  const setSort = useCallback((sortBy, sortOrder = 'desc') => {
    dispatch({ type: 'SET_SORT', payload: { sortBy, sortOrder } });
  }, []);

  const setSearchTerm = useCallback((term) => {
    dispatch({ type: 'SET_SEARCH', payload: term });
  }, []);

  const toggleShowCompleted = useCallback(() => {
    dispatch({ type: 'TOGGLE_SHOW_COMPLETED' });
  }, []);

  const addCategory = useCallback((category) => {
    dispatch({ type: 'ADD_CATEGORY', payload: category });
  }, []);

  const undo = useCallback(() => {
    dispatch({ type: 'UNDO' });
  }, []);

  const exportTodos = useCallback(() => {
    const dataStr = JSON.stringify(state.todos, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `todos-${format(new Date(), 'yyyy-MM-dd')}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [state.todos]);

  const importTodos = useCallback((file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedTodos = JSON.parse(e.target.result);
        if (Array.isArray(importedTodos)) {
          dispatch({ type: 'IMPORT_TODOS', payload: importedTodos });
        }
      } catch (error) {
        console.error('Error importing todos:', error);
      }
    };
    reader.readAsText(file);
  }, []);

  // Save to localStorage
  useEffect(() => {
    setSavedTodos(state.todos);
  }, [state.todos, setSavedTodos]);

  useEffect(() => {
    setSavedCategories(state.categories);
  }, [state.categories, setSavedCategories]);

  return {
    todos: filteredTodos,
    allTodos: state.todos,
    selectedTodos: state.selectedTodos,
    filter: state.filter,
    sortBy: state.sortBy,
    sortOrder: state.sortOrder,
    searchTerm: state.searchTerm,
    showCompleted: state.showCompleted,
    categories: state.categories,
    history: state.history,
    stats,
    addTodo,
    updateTodo,
    toggleTodo,
    deleteTodo,
    bulkDelete,
    bulkToggle,
    selectTodo,
    selectAll,
    clearSelection,
    setFilter,
    setSort,
    setSearchTerm,
    toggleShowCompleted,
    addCategory,
    undo,
    exportTodos,
    importTodos
  };
};
{% endraw %}
{% endraw %}
```

### 4. Main Component
```jsx
// src/components/TodoApp.jsx
import React from 'react';
import { useTodos } from '../hooks/useTodos';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';
import TodoForm from './TodoForm/TodoForm';
import TodoList from './TodoList/TodoList';
import TodoFilters from './TodoFilters/TodoFilters';
import TodoStats from './TodoStats/TodoStats';
import BulkActions from './BulkActions/BulkActions';
import './TodoApp.css';

const TodoApp = () => {
  const todoHook = useTodos();
  const {
    todos,
    selectedTodos,
    filter,
    searchTerm,
    stats,
    addTodo,
    toggleTodo,
    deleteTodo,
    selectTodo,
    selectAll,
    clearSelection,
    setFilter,
    setSearchTerm,
    undo,
    exportTodos
  } = todoHook;

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'ctrl+a': selectAll,
    'ctrl+z': undo,
    'ctrl+e': exportTodos,
    'escape': clearSelection
  });

  return (
    <div className="todo-app">
      <header className="todo-header">
        <h1>Advanced Todo App</h1>
        <TodoStats stats={stats} />
      </header>

      <main className="todo-main">
        <div className="todo-controls">
          <TodoForm onAddTodo={addTodo} categories={todoHook.categories} />
          <TodoFilters
            filter={filter}
            searchTerm={searchTerm}
            onFilterChange={setFilter}
            onSearchChange={setSearchTerm}
            categories={todoHook.categories}
          />
        </div>

        {selectedTodos.length > 0 && (
          <BulkActions
            selectedCount={selectedTodos.length}
            onBulkDelete={() => todoHook.bulkDelete(selectedTodos)}
            onBulkToggle={(completed) => todoHook.bulkToggle(selectedTodos, completed)}
            onClearSelection={clearSelection}
          />
        )}

        <TodoList
          todos={todos}
          selectedTodos={selectedTodos}
          onToggleTodo={toggleTodo}
          onDeleteTodo={deleteTodo}
          onSelectTodo={selectTodo}
          onUpdateTodo={todoHook.updateTodo}
        />

        {todoHook.history.length > 0 && (
          <div className="todo-actions">
            <button 
              onClick={undo}
              className="btn btn-secondary"
              title="Ctrl+Z"
            >
              Undo Last Action
            </button>
            <button 
              onClick={exportTodos}
              className="btn btn-secondary"
              title="Ctrl+E"
            >
              Export Todos
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default TodoApp;
```

### 5. Supporting Components

#### Todo Form Component
```jsx
// src/components/TodoForm/TodoForm.jsx
import React, { useState } from 'react';
import './TodoForm.css';

const TodoForm = ({ onAddTodo, categories }) => {
  const [formData, setFormData] = useState({
    text: '',
    category: 'general',
    priority: 'medium',
    dueDate: '',
    tags: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.text.trim()) return;

    onAddTodo({
      text: formData.text.trim(),
      category: formData.category,
      priority: formData.priority,
      dueDate: formData.dueDate || null,
      tags: formData.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0)
    });

    setFormData({
      text: '',
      category: 'general',
      priority: 'medium',
      dueDate: '',
      tags: ''
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form onSubmit={handleSubmit} className="todo-form">
      <div className="form-row">
        <input
          type="text"
          name="text"
          value={formData.text}
          onChange={handleChange}
          placeholder="What needs to be done?"
          className="todo-input"
          required
        />
        <button type="submit" className="btn btn-primary">
          Add Todo
        </button>
      </div>

      <div className="form-row form-details">
        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
          className="form-select"
        >
          {categories.map(category => (
            <option key={category} value={category}>
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </option>
          ))}
        </select>

        <select
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className="form-select"
        >
          <option value="low">Low Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="high">High Priority</option>
        </select>

        <input
          type="date"
          name="dueDate"
          value={formData.dueDate}
          onChange={handleChange}
          className="form-input"
        />

        <input
          type="text"
          name="tags"
          value={formData.tags}
          onChange={handleChange}
          placeholder="Tags (comma separated)"
          className="form-input"
        />
      </div>
    </form>
  );
};

export default TodoForm;
```

#### Todo List Component
```jsx
// src/components/TodoList/TodoList.jsx
import React from 'react';
import TodoItem from './TodoItem';
import './TodoList.css';

const TodoList = ({ 
  todos, 
  selectedTodos, 
  onToggleTodo, 
  onDeleteTodo, 
  onSelectTodo,
  onUpdateTodo 
}) => {
  if (todos.length === 0) {
    return (
      <div className="todo-list-empty">
        <p>No todos found. Add one above!</p>
      </div>
    );
  }

  return (
    <div className="todo-list">
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          isSelected={selectedTodos.includes(todo.id)}
          onToggle={() => onToggleTodo(todo.id)}
          onDelete={() => onDeleteTodo(todo.id)}
          onSelect={() => onSelectTodo(todo.id)}
          onUpdate={(updates) => onUpdateTodo(todo.id, updates)}
        />
      ))}
    </div>
  );
};

export default TodoList;
```

#### Todo Item Component
```jsx
{% raw %}
{% raw %}
// src/components/TodoList/TodoItem.jsx
import React, { useState } from 'react';
import { format, isToday, isPast } from 'date-fns';
import './TodoItem.css';

const TodoItem = ({ todo, isSelected, onToggle, onDelete, onSelect, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(todo.text);

  const handleEditSubmit = (e) => {
    e.preventDefault();
    if (editText.trim()) {
      onUpdate({ text: editText.trim() });
      setIsEditing(false);
    }
  };

  const handleEditCancel = () => {
    setEditText(todo.text);
    setIsEditing(false);
  };

  const getDueDateClass = () => {
    if (!todo.dueDate) return '';
    const dueDate = new Date(todo.dueDate);
    if (isPast(dueDate) && !todo.completed) return 'overdue';
    if (isToday(dueDate)) return 'due-today';
    return '';
  };

  const getPriorityClass = () => {
    return `priority-${todo.priority}`;
  };

  return (
    <div className={`todo-item ${todo.completed ? 'completed' : ''} ${isSelected ? 'selected' : ''} ${getDueDateClass()} ${getPriorityClass()}`}>
      <div className="todo-item-main">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onSelect}
          className="todo-select"
        />
        
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={onToggle}
          className="todo-toggle"
        />

        <div className="todo-content">
          {isEditing ? (
            <form onSubmit={handleEditSubmit} className="todo-edit-form">
              <input
                type="text"
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="todo-edit-input"
                autoFocus
                onBlur={handleEditCancel}
                onKeyDown={(e) => {
                  if (e.key === 'Escape') handleEditCancel();
                }}
              />
            </form>
          ) : (
            <div className="todo-text" onDoubleClick={() => setIsEditing(true)}>
              {todo.text}
            </div>
          )}

          <div className="todo-meta">
            <span className={`todo-category category-${todo.category}`}>
              {todo.category}
            </span>
            <span className={`todo-priority priority-${todo.priority}`}>
              {todo.priority}
            </span>
            {todo.dueDate && (
              <span className={`todo-due-date ${getDueDateClass()}`}>
                Due: {format(new Date(todo.dueDate), 'MMM dd, yyyy')}
              </span>
            )}
            {todo.tags.length > 0 && (
              <div className="todo-tags">
                {todo.tags.map(tag => (
                  <span key={tag} className="todo-tag">#{tag}</span>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="todo-actions">
          <button
            onClick={() => setIsEditing(true)}
            className="btn btn-small btn-secondary"
            title="Edit todo"
          >
            ✏️
          </button>
          <button
            onClick={onDelete}
            className="btn btn-small btn-danger"
            title="Delete todo"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
};

export default TodoItem;
{% endraw %}
{% endraw %}
```

### 6. Styling

#### Main App Styles
```css
/* src/components/TodoApp.css */
.todo-app {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.todo-header {
  text-align: center;
  margin-bottom: 30px;
}

.todo-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 300;
  font-size: 2.5rem;
}

.todo-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.todo-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.todo-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  padding: 20px 0;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
}

/* Form Elements */
.form-input,
.form-select,
.todo-input {
  padding: 10px;
  border: 2px solid #ecf0f1;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-select:focus,
.todo-input:focus {
  outline: none;
  border-color: #3498db;
}

/* Responsive */
@media (max-width: 600px) {
  .todo-app {
    padding: 10px;
  }

  .todo-header h1 {
    font-size: 2rem;
  }

  .form-row {
    flex-direction: column;
  }

  .todo-actions {
    flex-direction: column;
  }
}
```

#### Todo Form Styles
```css
/* src/components/TodoForm/TodoForm.css */
.todo-form {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-row {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  align-items: center;
}

.form-row:last-child {
  margin-bottom: 0;
}

.todo-input {
  flex: 1;
  min-width: 200px;
}

.form-details {
  flex-wrap: wrap;
}

.form-details .form-select,
.form-details .form-input {
  flex: 1;
  min-width: 120px;
}

.form-select {
  background-color: white;
  cursor: pointer;
}

@media (max-width: 600px) {
  .form-details {
    flex-direction: column;
  }

  .form-details .form-select,
  .form-details .form-input {
    width: 100%;
  }
}
```

#### Todo List Styles
```css
/* src/components/TodoList/TodoList.css */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.todo-list-empty {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
  font-style: italic;
}

.todo-list-empty p {
  margin: 0;
  font-size: 18px;
}
```

#### Todo Item Styles
```css
/* src/components/TodoList/TodoItem.css */
.todo-item {
  background: white;
  border-radius: 8px;
  border: 2px solid #ecf0f1;
  transition: all 0.2s ease;
}

.todo-item:hover {
  border-color: #bdc3c7;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.todo-item.selected {
  border-color: #3498db;
  background-color: #ebf3fd;
}

.todo-item.completed {
  opacity: 0.7;
}

.todo-item.overdue {
  border-left: 4px solid #e74c3c;
}

.todo-item.due-today {
  border-left: 4px solid #f39c12;
}

.todo-item-main {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  gap: 12px;
}

.todo-select,
.todo-toggle {
  margin-top: 2px;
  cursor: pointer;
}

.todo-content {
  flex: 1;
  min-width: 0;
}

.todo-text {
  font-size: 16px;
  line-height: 1.4;
  margin-bottom: 8px;
  cursor: pointer;
  word-wrap: break-word;
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  color: #7f8c8d;
}

.todo-edit-form {
  width: 100%;
}

.todo-edit-input {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid #3498db;
  border-radius: 4px;
  font-size: 16px;
}

.todo-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.todo-category {
  background-color: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  text-transform: capitalize;
}

.category-work { background-color: #e74c3c; }
.category-personal { background-color: #27ae60; }
.category-shopping { background-color: #f39c12; }

.todo-priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.priority-high {
  background-color: #e74c3c;
  color: white;
}

.priority-medium {
  background-color: #f39c12;
  color: white;
}

.priority-low {
  background-color: #27ae60;
  color: white;
}

.todo-due-date {
  font-size: 12px;
  color: #7f8c8d;
}

.todo-due-date.overdue {
  color: #e74c3c;
  font-weight: bold;
}

.todo-due-date.due-today {
  color: #f39c12;
  font-weight: bold;
}

.todo-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.todo-tag {
  background-color: #ecf0f1;
  color: #2c3e50;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
}

.todo-actions {
  display: flex;
  gap: 5px;
  margin-left: auto;
}

/* Priority borders */
.todo-item.priority-high {
  border-left: 4px solid #e74c3c;
}

.todo-item.priority-medium {
  border-left: 4px solid #f39c12;
}

.todo-item.priority-low {
  border-left: 4px solid #27ae60;
}

@media (max-width: 600px) {
  .todo-item-main {
    padding: 10px;
  }

  .todo-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .todo-actions {
    flex-direction: column;
  }
}
```

---

## 🧪 Testing the Implementation

### Test Checklist
- [ ] **Add Todo**: Create todos with different categories and priorities
- [ ] **Edit Todo**: Double-click to edit todo text
- [ ] **Toggle Completion**: Mark todos as complete/incomplete
- [ ] **Delete Todo**: Remove individual todos
- [ ] **Bulk Operations**: Select multiple todos and delete/toggle
- [ ] **Filtering**: Filter by category, completion status
- [ ] **Search**: Search todos by text and tags
- [ ] **Sorting**: Sort by date, priority, alphabetically
- [ ] **Categories**: Add custom categories
- [ ] **Due Dates**: Set and display due dates
- [ ] **Tags**: Add and search by tags
- [ ] **Persistence**: Refresh page and verify data persists
- [ ] **Keyboard Shortcuts**: Test Ctrl+A, Ctrl+Z, Ctrl+E, Escape
- [ ] **Export/Import**: Export todos and import them back
- [ ] **Undo**: Undo last action
- [ ] **Responsive**: Test on mobile devices

### Performance Testing
```jsx
{% raw %}
{% raw %}
// Test with large datasets
const generateTestTodos = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `todo-${i}`,
    text: `Test todo ${i + 1}`,
    completed: Math.random() > 0.5,
    category: ['work', 'personal', 'shopping'][Math.floor(Math.random() * 3)],
    priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
    createdAt: new Date(Date.now() - Math.random() * 86400000 * 30).toISOString(),
    tags: [`tag${i % 5}`, `tag${(i + 1) % 5}`]
  }));
};
{% endraw %}
{% endraw %}
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Todos not persisting**
```jsx
// Ensure localStorage hook is working
useEffect(() => {
  console.log('Saving todos:', state.todos);
  setSavedTodos(state.todos);
}, [state.todos, setSavedTodos]);
```

**2. Performance issues with large lists**
```jsx
// Add React.memo to TodoItem
export default React.memo(TodoItem);

// Use useMemo for expensive calculations
const filteredTodos = useMemo(() => {
  // filtering logic
}, [todos, filter, searchTerm]);
```

**3. Keyboard shortcuts not working**
```jsx
// Ensure event listeners are properly attached
useEffect(() => {
  const handleKeyDown = (e) => {
    console.log('Key pressed:', e.key, e.ctrlKey);
    // handler logic
  };
  
  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, []);
```

**4. Search not working**
```jsx
// Debug debounced search
const debouncedSearchTerm = useDebounce(searchTerm, 300);
useEffect(() => {
  console.log('Search term changed:', debouncedSearchTerm);
}, [debouncedSearchTerm]);
```

---

## 🎓 Learning Objectives

### Custom Hooks Mastery
- ✅ **Hook Composition**: Building complex functionality with multiple hooks
- ✅ **Reusability**: Creating hooks that can be used across different components
- ✅ **Separation of Concerns**: Keeping business logic separate from UI logic
- ✅ **Hook Dependencies**: Understanding and optimizing hook dependencies

### Advanced State Management
- ✅ **useReducer**: Managing complex state with actions and reducers
- ✅ **State Normalization**: Organizing state for performance and maintainability
- ✅ **Optimistic Updates**: Providing immediate feedback while operations complete
- ✅ **History Management**: Implementing undo/redo functionality

### Performance Optimization
- ✅ **Memoization**: Using useMemo and useCallback effectively
- ✅ **Component Optimization**: Preventing unnecessary re-renders
- ✅ **Debouncing**: Optimizing search and input operations
- ✅ **Lazy Loading**: Loading features only when needed

### User Experience
- ✅ **Keyboard Navigation**: Implementing accessibility features
- ✅ **Bulk Operations**: Allowing efficient multi-item management
- ✅ **Real-time Feedback**: Providing immediate visual feedback
- ✅ **Data Persistence**: Maintaining state across sessions

---

## 🚀 Next Steps

1. **Add Unit Tests**: Test custom hooks and components
2. **Implement Drag & Drop**: Reorder todos with drag and drop
3. **Add Animations**: Smooth transitions for adding/removing todos
4. **Offline Support**: Add service worker for offline functionality
5. **Collaboration**: Add real-time multi-user editing
6. **Advanced Filtering**: Date ranges, multiple criteria
7. **Themes**: Dark mode and custom themes
8. **PWA Features**: Install app, push notifications

This implementation demonstrates advanced React patterns and provides a solid foundation for building complex, production-ready applications with custom hooks and sophisticated state management.
