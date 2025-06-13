# Module 13: Testing

## 📚 Learning Objectives

By the end of this module, you will:
- Master React component testing strategies and best practices
- Learn unit testing with Jest and React Testing Library
- Implement integration testing for React applications
- Test React hooks, context, and custom components
- Apply Test-Driven Development (TDD) principles
- Understand end-to-end testing with Cypress/Playwright
- Debug and troubleshoot test failures effectively
- Build comprehensive test suites for production applications

## 🎯 Prerequisites

- Completed Modules 1-12
- Understanding of React components, hooks, and state management
- Basic knowledge of JavaScript testing concepts
- Familiarity with async/await and promises

## 📖 Module Content

### 1. Testing Fundamentals

#### **Types of Testing**
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows
- **Visual Regression Tests**: Test UI appearance

#### **Testing Philosophy**
- Test behavior, not implementation
- Write tests that give confidence
- Test user interactions, not internal state
- Focus on testing contracts and APIs

### 2. Testing Environment Setup

#### **Jest Configuration**
```json
// package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:debug": "node --inspect-brk node_modules/.bin/jest --runInBand"
  },
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/src/setupTests.js"],
    "moduleNameMapping": {
      "\\.(css|less|scss|sass)$": "identity-obj-proxy",
      "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2)$": "jest-transform-stub"
    },
    "collectCoverageFrom": [
      "src/**/*.{js,jsx}",
      "!src/index.js",
      "!src/reportWebVitals.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

#### **Setup Files**
```javascript
// src/setupTests.js
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configure testing library
configure({ testIdAttribute: 'data-testid' });

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};
```

### 3. React Testing Library Fundamentals

#### **Basic Component Testing**
```jsx
// Button.jsx
import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'primary',
  ...props 
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
      data-testid="button"
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
```

```javascript
// Button.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from './Button';

describe('Button Component', () => {
  test('renders button with text', () => {
    render(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
  });

  test('calls onClick when clicked', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByRole('button');
    await user.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  test('applies correct CSS class for variant', () => {
    render(<Button variant="secondary">Secondary</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-secondary');
  });

  test('does not call onClick when disabled', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(
      <Button onClick={handleClick} disabled>
        Disabled Button
      </Button>
    );
    
    const button = screen.getByRole('button');
    await user.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

#### **Testing Form Components**
```jsx
// ContactForm.jsx
import React, { useState } from 'react';

const ContactForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    }
    
    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validateForm();
    
    if (Object.keys(newErrors).length === 0) {
      onSubmit(formData);
      setFormData({ name: '', email: '', message: '' });
    } else {
      setErrors(newErrors);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} data-testid="contact-form">
      <div>
        <label htmlFor="name">Name:</label>
        <input
          id="name"
          name="name"
          type="text"
          value={formData.name}
          onChange={handleChange}
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <span id="name-error" role="alert">
            {errors.name}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <span id="email-error" role="alert">
            {errors.email}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="message">Message:</label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          aria-invalid={!!errors.message}
          aria-describedby={errors.message ? 'message-error' : undefined}
        />
        {errors.message && (
          <span id="message-error" role="alert">
            {errors.message}
          </span>
        )}
      </div>

      <button type="submit">Submit</button>
    </form>
  );
};

export default ContactForm;
```

```javascript
// ContactForm.test.jsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ContactForm from './ContactForm';

describe('ContactForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test('renders all form fields', () => {
    render(<ContactForm onSubmit={mockOnSubmit} />);
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    const user = userEvent.setup();
    render(<ContactForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'john@example.com');
    await user.type(screen.getByLabelText(/message/i), 'Hello World');
    
    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(mockOnSubmit).toHaveBeenCalledWith({
      name: 'John Doe',
      email: 'john@example.com',
      message: 'Hello World'
    });
  });

  test('shows validation errors for empty fields', async () => {
    const user = userEvent.setup();
    render(<ContactForm onSubmit={mockOnSubmit} />);

    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
      expect(screen.getByText('Email is required')).toBeInTheDocument();
      expect(screen.getByText('Message is required')).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('shows error for invalid email', async () => {
    const user = userEvent.setup();
    render(<ContactForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText('Email is invalid')).toBeInTheDocument();
    });
  });

  test('clears error when user starts typing', async () => {
    const user = userEvent.setup();
    render(<ContactForm onSubmit={mockOnSubmit} />);

    // Trigger validation error
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
    });

    // Start typing to clear error
    await user.type(screen.getByLabelText(/name/i), 'J');
    
    expect(screen.queryByText('Name is required')).not.toBeInTheDocument();
  });
});
```

### 4. Testing Hooks

#### **Testing Custom Hooks**
```javascript
// hooks/useCounter.js
import { useState, useCallback } from 'react';

export const useCounter = (initialValue = 0) => {
  const [count, setCount] = useState(initialValue);

  const increment = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  const decrement = useCallback(() => {
    setCount(prev => prev - 1);
  }, []);

  const reset = useCallback(() => {
    setCount(initialValue);
  }, [initialValue]);

  return { count, increment, decrement, reset };
};
```

```javascript
// hooks/useCounter.test.js
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  test('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter());
    
    expect(result.current.count).toBe(0);
  });

  test('should initialize with provided value', () => {
    const { result } = renderHook(() => useCounter(10));
    
    expect(result.current.count).toBe(10);
  });

  test('should increment count', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  test('should decrement count', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });

  test('should reset to initial value', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.increment();
      result.current.increment();
    });
    
    expect(result.current.count).toBe(7);
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.count).toBe(5);
  });
});
```

#### **Testing Async Hooks**
```javascript
// hooks/useApi.js
import { useState, useEffect } from 'react';

export const useApi = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (url) {
      fetchData();
    }
  }, [url]);

  return { data, loading, error };
};
```

```javascript
// hooks/useApi.test.js
import { renderHook, waitFor } from '@testing-library/react';
import { useApi } from './useApi';

// Mock fetch
global.fetch = jest.fn();

describe('useApi', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('should return loading state initially', () => {
    const { result } = renderHook(() => useApi('https://api.example.com/data'));
    
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);
  });

  test('should fetch and return data successfully', async () => {
    const mockData = { id: 1, name: 'Test' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useApi('https://api.example.com/data'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
    expect(fetch).toHaveBeenCalledWith('https://api.example.com/data');
  });

  test('should handle fetch error', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    const { result } = renderHook(() => useApi('https://api.example.com/data'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe('HTTP error! status: 404');
  });

  test('should handle network error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useApi('https://api.example.com/data'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe('Network error');
  });
});
```

### 5. Testing Context and State Management

#### **Testing Context Providers**
```jsx
// ThemeContext.jsx
import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

```javascript
// ThemeContext.test.jsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, useTheme } from './ThemeContext';

// Test component that uses the context
const TestComponent = () => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </div>
  );
};

describe('ThemeContext', () => {
  test('provides default theme value', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme')).toHaveTextContent('light');
  });

  test('toggles theme when button clicked', async () => {
    const user = userEvent.setup();
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const button = screen.getByRole('button', { name: /toggle theme/i });
    
    await user.click(button);
    expect(screen.getByTestId('theme')).toHaveTextContent('dark');
    
    await user.click(button);
    expect(screen.getByTestId('theme')).toHaveTextContent('light');
  });

  test('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useTheme must be used within ThemeProvider');
    
    consoleSpy.mockRestore();
  });
});
```

### 6. Mocking and Test Utilities

#### **Mocking External Dependencies**
```javascript
// utils/api.js
export const fetchUser = async (id) => {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
};
```

```javascript
// UserProfile.jsx
import React, { useState, useEffect } from 'react';
import { fetchUser } from './utils/api';

const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadUser = async () => {
      try {
        setLoading(true);
        const userData = await fetchUser(userId);
        setUser(userData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      loadUser();
    }
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return <div>No user found</div>;

  return (
    <div data-testid="user-profile">
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
};

export default UserProfile;
```

```javascript
// UserProfile.test.jsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import UserProfile from './UserProfile';
import { fetchUser } from './utils/api';

// Mock the API module
jest.mock('./utils/api');

const mockFetchUser = fetchUser as jest.MockedFunction<typeof fetchUser>;

describe('UserProfile', () => {
  beforeEach(() => {
    mockFetchUser.mockClear();
  });

  test('displays loading state initially', () => {
    render(<UserProfile userId="1" />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('displays user data when fetch succeeds', async () => {
    const mockUser = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com'
    };

    mockFetchUser.mockResolvedValueOnce(mockUser);

    render(<UserProfile userId="1" />);

    await waitFor(() => {
      expect(screen.getByTestId('user-profile')).toBeInTheDocument();
    });

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(mockFetchUser).toHaveBeenCalledWith('1');
  });

  test('displays error when fetch fails', async () => {
    mockFetchUser.mockRejectedValueOnce(new Error('Failed to fetch user'));

    render(<UserProfile userId="1" />);

    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch user')).toBeInTheDocument();
    });
  });

  test('does not fetch when userId is not provided', () => {
    render(<UserProfile />);
    
    expect(mockFetchUser).not.toHaveBeenCalled();
  });
});
```

### 7. Integration Testing

#### **Testing Component Integration**
```jsx
// TodoApp.jsx
import React, { useState } from 'react';
import TodoList from './TodoList';
import AddTodo from './AddTodo';

const TodoApp = () => {
  const [todos, setTodos] = useState([]);

  const addTodo = (text) => {
    const newTodo = {
      id: Date.now(),
      text,
      completed: false
    };
    setTodos(prev => [...prev, newTodo]);
  };

  const toggleTodo = (id) => {
    setTodos(prev =>
      prev.map(todo =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  const deleteTodo = (id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };

  return (
    <div data-testid="todo-app">
      <h1>Todo App</h1>
      <AddTodo onAdd={addTodo} />
      <TodoList
        todos={todos}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
      />
    </div>
  );
};

export default TodoApp;
```

```javascript
// TodoApp.test.jsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TodoApp from './TodoApp';

describe('TodoApp Integration', () => {
  test('adds and displays a new todo', async () => {
    const user = userEvent.setup();
    render(<TodoApp />);

    // Add a new todo
    const input = screen.getByLabelText(/add todo/i);
    const addButton = screen.getByRole('button', { name: /add/i });

    await user.type(input, 'Buy groceries');
    await user.click(addButton);

    // Check if todo appears in the list
    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
  });

  test('toggles todo completion status', async () => {
    const user = userEvent.setup();
    render(<TodoApp />);

    // Add a todo
    const input = screen.getByLabelText(/add todo/i);
    await user.type(input, 'Test todo');
    await user.click(screen.getByRole('button', { name: /add/i }));

    // Toggle completion
    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);

    expect(checkbox).toBeChecked();
  });

  test('deletes a todo', async () => {
    const user = userEvent.setup();
    render(<TodoApp />);

    // Add a todo
    const input = screen.getByLabelText(/add todo/i);
    await user.type(input, 'Todo to delete');
    await user.click(screen.getByRole('button', { name: /add/i }));

    // Delete the todo
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(screen.queryByText('Todo to delete')).not.toBeInTheDocument();
  });

  test('handles multiple todos correctly', async () => {
    const user = userEvent.setup();
    render(<TodoApp />);

    const input = screen.getByLabelText(/add todo/i);
    const addButton = screen.getByRole('button', { name: /add/i });

    // Add multiple todos
    await user.type(input, 'First todo');
    await user.click(addButton);

    await user.clear(input);
    await user.type(input, 'Second todo');
    await user.click(addButton);

    // Check both todos are displayed
    expect(screen.getByText('First todo')).toBeInTheDocument();
    expect(screen.getByText('Second todo')).toBeInTheDocument();

    // Toggle first todo
    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[0]);

    expect(checkboxes[0]).toBeChecked();
    expect(checkboxes[1]).not.toBeChecked();
  });
});
```

### 8. End-to-End Testing with Cypress

#### **Cypress Configuration**
```javascript
// cypress.config.js
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
  component: {
    devServer: {
      framework: 'create-react-app',
      bundler: 'webpack',
    },
  },
});
```

#### **E2E Test Examples**
```javascript
// cypress/e2e/todo-app.cy.js
describe('Todo App E2E', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should add a new todo', () => {
    cy.get('[data-testid="add-todo-input"]').type('Learn Cypress');
    cy.get('[data-testid="add-todo-button"]').click();
    
    cy.get('[data-testid="todo-list"]').should('contain', 'Learn Cypress');
  });

  it('should complete a todo', () => {
    // Add a todo first
    cy.get('[data-testid="add-todo-input"]').type('Complete this task');
    cy.get('[data-testid="add-todo-button"]').click();
    
    // Mark as complete
    cy.get('[data-testid="todo-checkbox"]').first().check();
    
    // Verify it's marked as complete
    cy.get('[data-testid="todo-item"]')
      .first()
      .should('have.class', 'completed');
  });

  it('should delete a todo', () => {
    // Add a todo first
    cy.get('[data-testid="add-todo-input"]').type('Delete me');
    cy.get('[data-testid="add-todo-button"]').click();
    
    // Delete the todo
    cy.get('[data-testid="delete-todo-button"]').first().click();
    
    // Verify it's gone
    cy.get('[data-testid="todo-list"]').should('not.contain', 'Delete me');
  });

  it('should filter todos', () => {
    // Add multiple todos
    cy.get('[data-testid="add-todo-input"]').type('Active todo');
    cy.get('[data-testid="add-todo-button"]').click();
    
    cy.get('[data-testid="add-todo-input"]').type('Completed todo');
    cy.get('[data-testid="add-todo-button"]').click();
    
    // Complete one todo
    cy.get('[data-testid="todo-checkbox"]').last().check();
    
    // Filter by active
    cy.get('[data-testid="filter-active"]').click();
    cy.get('[data-testid="todo-list"]').should('contain', 'Active todo');
    cy.get('[data-testid="todo-list"]').should('not.contain', 'Completed todo');
    
    // Filter by completed
    cy.get('[data-testid="filter-completed"]').click();
    cy.get('[data-testid="todo-list"]').should('not.contain', 'Active todo');
    cy.get('[data-testid="todo-list"]').should('contain', 'Completed todo');
  });
});
```

### 9. Performance Testing

#### **Testing Component Performance**
```javascript
// PerformanceComponent.test.jsx
import React from 'react';
import { render } from '@testing-library/react';
import { measurePerformance } from './test-utils/performance';
import ExpensiveComponent from './ExpensiveComponent';

describe('ExpensiveComponent Performance', () => {
  test('renders within acceptable time', async () => {
    const measurement = await measurePerformance(async () => {
      render(<ExpensiveComponent items={Array.from({ length: 1000 }, (_, i) => i)} />);
    });

    expect(measurement.duration).toBeLessThan(100); // Should render in less than 100ms
  });

  test('does not cause memory leaks', () => {
    const { unmount } = render(<ExpensiveComponent />);
    
    const initialMemory = performance.memory?.usedJSHeapSize || 0;
    
    // Create and destroy component multiple times
    for (let i = 0; i < 100; i++) {
      const { unmount: destroyComponent } = render(<ExpensiveComponent />);
      destroyComponent();
    }
    
    const finalMemory = performance.memory?.usedJSHeapSize || 0;
    const memoryIncrease = finalMemory - initialMemory;
    
    // Memory increase should be minimal (less than 1MB)
    expect(memoryIncrease).toBeLessThan(1024 * 1024);
    
    unmount();
  });
});
```

### 10. Accessibility Testing

#### **Testing Accessibility**
```javascript
// AccessibilityTest.test.jsx
import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import ContactForm from './ContactForm';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  test('ContactForm should not have accessibility violations', async () => {
    const { container } = render(<ContactForm onSubmit={() => {}} />);
    const results = await axe(container);
    
    expect(results).toHaveNoViolations();
  });

  test('form should have proper keyboard navigation', async () => {
    const user = userEvent.setup();
    render(<ContactForm onSubmit={() => {}} />);
    
    const nameInput = screen.getByLabelText(/name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const messageInput = screen.getByLabelText(/message/i);
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    // Test tab navigation
    await user.tab();
    expect(nameInput).toHaveFocus();
    
    await user.tab();
    expect(emailInput).toHaveFocus();
    
    await user.tab();
    expect(messageInput).toHaveFocus();
    
    await user.tab();
    expect(submitButton).toHaveFocus();
  });
});
```

## 🎯 Practical Exercises

### Exercise 1: Component Test Suite
Create comprehensive tests for a complex component with multiple props, state, and event handlers.

### Exercise 2: Hook Testing
Build and test a custom hook that manages complex state logic with proper error handling.

### Exercise 3: Integration Testing
Test the interaction between multiple components in a feature workflow.

### Exercise 4: E2E Testing
Write end-to-end tests for a complete user journey in your application.

## 📊 Assessment Criteria

### Knowledge Check
- [ ] Explain different types of testing and their purposes
- [ ] Demonstrate proper use of React Testing Library
- [ ] Write effective tests for hooks and context
- [ ] Implement proper mocking strategies
- [ ] Test component accessibility
- [ ] Set up and configure testing environments

### Practical Assessment
- [ ] Build comprehensive test suites with good coverage
- [ ] Test both happy path and error scenarios
- [ ] Write maintainable and readable tests
- [ ] Implement proper test setup and teardown
- [ ] Test asynchronous operations correctly
- [ ] Ensure tests run reliably and fast

### Test Quality
- [ ] Tests are isolated and independent
- [ ] Good test descriptions and organization
- [ ] Proper use of test utilities and helpers
- [ ] Tests focus on behavior, not implementation
- [ ] Good balance of unit, integration, and E2E tests

## 🚀 Project: E-Commerce Testing Suite

Build a comprehensive testing suite for an e-commerce application:

**Components to Test:**
- Product listing and filtering
- Shopping cart functionality
- User authentication
- Checkout process
- Order history

**Testing Requirements:**
- Unit tests for all components
- Integration tests for user workflows
- E2E tests for complete purchase flow
- Performance tests for large product lists
- Accessibility tests for all pages
- API mocking for data fetching

**Testing Goals:**
- 90%+ code coverage
- All tests pass consistently
- Fast test execution (< 30 seconds)
- Comprehensive error scenario coverage

## 📚 Additional Resources

### Documentation
- [React Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Cypress Documentation](https://docs.cypress.io)

### Tools
- React Testing Library
- Jest
- Cypress
- Playwright
- MSW (Mock Service Worker)
- jest-axe for accessibility testing

### Best Practices
- Test behavior, not implementation
- Write descriptive test names
- Keep tests simple and focused
- Use proper test data and fixtures
- Mock external dependencies appropriately

## ⏭️ Next Steps

After mastering this module, you'll be ready for:
- **Module 14**: Code Quality (ESLint, Prettier, TypeScript)
- Advanced testing patterns and strategies
- Test-driven development workflows
- Continuous integration and automated testing

---

**Estimated Time:** 2-3 weeks  
**Difficulty:** Advanced  
**Prerequisites:** Modules 1-12 completed
