# Week 13: React Testing - Daily Challenges

## Overview
Master React testing with Jest, React Testing Library, and advanced testing strategies. Build confidence in your code through comprehensive testing practices.

## Learning Objectives
- Master React Testing Library fundamentals
- Write effective unit and integration tests
- Test React components, hooks, and context
- Implement E2E testing with Playwright/Cypress
- Practice Test-Driven Development (TDD)
- Learn testing best practices and patterns

---

## Day 1: Testing Environment Setup & Fundamentals

### 🎯 Challenge: Test Environment Configuration
Set up a comprehensive testing environment for React applications.

#### Tasks:
1. **Configure Jest & React Testing Library**
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom
```

2. **Create Test Configuration**
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/src/__mocks__/fileMock.js'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

3. **Write Your First Component Test**
```javascript
// components/Button/Button.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from './Button';

describe('Button Component', () => {
  test('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies custom className', () => {
    render(<Button className="custom-class">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('custom-class');
  });

  test('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled Button</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

#### 💡 Learning Focus:
- Testing library setup and configuration
- Basic component testing patterns
- Jest matchers and assertions
- Test file organization

---

## Day 2: Testing User Interactions

### 🎯 Challenge: Interactive Component Testing
Test complex user interactions and form submissions.

#### Tasks:
1. **Test Form Component with Validation**
```javascript
// components/ContactForm/ContactForm.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ContactForm from './ContactForm';

describe('ContactForm', () => {
  test('validates email format', async () => {
    const user = userEvent.setup();
    render(<ContactForm />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
    });
  });

  test('submits form with valid data', async () => {
    const mockSubmit = jest.fn();
    const user = userEvent.setup();
    
    render(<ContactForm onSubmit={mockSubmit} />);
    
    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'john@example.com');
    await user.type(screen.getByLabelText(/message/i), 'Hello world');
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        message: 'Hello world'
      });
    });
  });
});
```

2. **Test Modal Component**
```javascript
// components/Modal/Modal.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from './Modal';

describe('Modal Component', () => {
  test('opens and closes modal', async () => {
    const user = userEvent.setup();
    const mockClose = jest.fn();
    
    render(
      <Modal isOpen={true} onClose={mockClose}>
        <p>Modal content</p>
      </Modal>
    );
    
    expect(screen.getByText('Modal content')).toBeInTheDocument();
    
    // Test close on overlay click
    const overlay = screen.getByTestId('modal-overlay');
    await user.click(overlay);
    expect(mockClose).toHaveBeenCalled();
  });

  test('prevents close on content click', async () => {
    const user = userEvent.setup();
    const mockClose = jest.fn();
    
    render(
      <Modal isOpen={true} onClose={mockClose}>
        <p>Modal content</p>
      </Modal>
    );
    
    const content = screen.getByText('Modal content');
    await user.click(content);
    expect(mockClose).not.toHaveBeenCalled();
  });

  test('closes on escape key', () => {
    const mockClose = jest.fn();
    
    render(
      <Modal isOpen={true} onClose={mockClose}>
        <p>Modal content</p>
      </Modal>
    );
    
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
    expect(mockClose).toHaveBeenCalled();
  });
});
```

#### 💡 Learning Focus:
- User event simulation
- Form testing patterns
- Async testing with waitFor
- Testing keyboard interactions

---

## Day 3: Testing React Hooks

### 🎯 Challenge: Custom Hook Testing
Learn to test custom hooks and hook-based components effectively.

#### Tasks:
1. **Test Custom Hook with renderHook**
```javascript
// hooks/useCounter/useCounter.test.js
import { renderHook, act } from '@testing-library/react';
import useCounter from './useCounter';

describe('useCounter Hook', () => {
  test('initializes with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  test('initializes with custom value', () => {
    const { result } = renderHook(() => useCounter(5));
    expect(result.current.count).toBe(5);
  });

  test('increments count', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  test('decrements count', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });

  test('resets count', () => {
    const { result } = renderHook(() => useCounter(10));
    
    act(() => {
      result.current.increment();
      result.current.reset();
    });
    
    expect(result.current.count).toBe(10);
  });
});
```

2. **Test Hook with External Dependencies**
```javascript
// hooks/useFetch/useFetch.test.js
import { renderHook, waitFor } from '@testing-library/react';
import useFetch from './useFetch';

// Mock fetch
global.fetch = jest.fn();

describe('useFetch Hook', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('returns loading state initially', () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'test' })
    });

    const { result } = renderHook(() => useFetch('/api/test'));
    
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);
  });

  test('returns data on successful fetch', async () => {
    const mockData = { id: 1, name: 'Test' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    const { result } = renderHook(() => useFetch('/api/test'));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
  });

  test('returns error on failed fetch', async () => {
    fetch.mockRejectedValueOnce(new Error('API Error'));

    const { result } = renderHook(() => useFetch('/api/test'));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe('API Error');
  });
});
```

3. **Test Component Using Hooks**
```javascript
// components/UserProfile/UserProfile.test.js
import { render, screen, waitFor } from '@testing-library/react';
import UserProfile from './UserProfile';
import * as useFetch from '../../hooks/useFetch';

jest.mock('../../hooks/useFetch');

describe('UserProfile Component', () => {
  test('shows loading state', () => {
    useFetch.default.mockReturnValue({
      loading: true,
      data: null,
      error: null
    });

    render(<UserProfile userId="123" />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays user data', async () => {
    const userData = { id: '123', name: 'John Doe', email: 'john@example.com' };
    
    useFetch.default.mockReturnValue({
      loading: false,
      data: userData,
      error: null
    });

    render(<UserProfile userId="123" />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  test('displays error message', () => {
    useFetch.default.mockReturnValue({
      loading: false,
      data: null,
      error: 'Failed to load user'
    });

    render(<UserProfile userId="123" />);
    expect(screen.getByText(/failed to load user/i)).toBeInTheDocument();
  });
});
```

#### 💡 Learning Focus:
- Testing custom hooks with renderHook
- Mocking external dependencies
- Testing hook state changes with act
- Testing components that use custom hooks

---

## Day 4: Context and Provider Testing

### 🎯 Challenge: Testing React Context
Test React Context providers and consumers effectively.

#### Tasks:
1. **Test Context Provider**
```javascript
// context/AuthContext/AuthContext.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';

// Test component that uses the context
const TestComponent = () => {
  const { user, login, logout, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      {user ? (
        <div>
          <span>Welcome, {user.name}</span>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <button onClick={() => login('test@example.com', 'password')}>
          Login
        </button>
      )}
    </div>
  );
};

describe('AuthContext', () => {
  test('provides initial state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('handles login', async () => {
    // Mock API call
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user: { id: 1, name: 'John Doe' } })
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText('Welcome, John Doe')).toBeInTheDocument();
    });
  });

  test('handles logout', async () => {
    // Mock authenticated state
    const AuthProviderWithUser = ({ children }) => (
      <AuthProvider initialUser={{ id: 1, name: 'John Doe' }}>
        {children}
      </AuthProvider>
    );

    render(
      <AuthProviderWithUser>
        <TestComponent />
      </AuthProviderWithUser>
    );
    
    fireEvent.click(screen.getByRole('button', { name: /logout/i }));
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });
  });
});
```

2. **Test Multiple Providers**
```javascript
// context/AppContext/AppContext.test.js
import { render, screen } from '@testing-library/react';
import { AuthProvider } from '../AuthContext/AuthContext';
import { ThemeProvider } from '../ThemeContext/ThemeContext';
import App from '../../App';

const AllProviders = ({ children }) => (
  <AuthProvider>
    <ThemeProvider>
      {children}
    </ThemeProvider>
  </AuthProvider>
);

describe('App with Multiple Providers', () => {
  test('renders app with all providers', () => {
    render(
      <AllProviders>
        <App />
      </AllProviders>
    );
    
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
```

#### 💡 Learning Focus:
- Testing context providers and consumers
- Mocking context values for testing
- Testing provider composition
- Testing context state changes

---

## Day 5: Mocking and API Testing

### 🎯 Challenge: Advanced Mocking Strategies
Master different mocking techniques for testing React applications.

#### Tasks:
1. **Mock External Libraries**
```javascript
// components/Chart/Chart.test.js
import { render, screen } from '@testing-library/react';
import Chart from './Chart';

// Mock the chart library
jest.mock('react-chartjs-2', () => ({
  Line: ({ data, options }) => (
    <div data-testid="line-chart">
      Chart with {data.datasets.length} datasets
    </div>
  )
}));

describe('Chart Component', () => {
  test('renders chart with data', () => {
    const chartData = {
      labels: ['Jan', 'Feb', 'Mar'],
      datasets: [{
        label: 'Sales',
        data: [100, 200, 150]
      }]
    };

    render(<Chart data={chartData} />);
    
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    expect(screen.getByText('Chart with 1 datasets')).toBeInTheDocument();
  });
});
```

2. **Mock API Calls with MSW**
```javascript
{% raw %}
{% raw %}
// test/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
      ])
    );
  }),

  rest.post('/api/users', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({ id: 3, name: 'New User', email: 'new@example.com' })
    );
  }),

  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(
      ctx.status(200),
      ctx.json({ id: Number(id), name: `User ${id}`, email: `user${id}@example.com` })
    );
  })
];
{% endraw %}
{% endraw %}
```

```javascript
// test/mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

```javascript
// components/UserList/UserList.test.js
import { render, screen, waitFor } from '@testing-library/react';
import { server } from '../../test/mocks/server';
import UserList from './UserList';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserList Component', () => {
  test('fetches and displays users', async () => {
    render(<UserList />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  test('handles API error', async () => {
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    render(<UserList />);
    
    await waitFor(() => {
      expect(screen.getByText(/error loading users/i)).toBeInTheDocument();
    });
  });
});
```

3. **Test Component with Date/Time**
```javascript
// components/CurrentTime/CurrentTime.test.js
import { render, screen } from '@testing-library/react';
import CurrentTime from './CurrentTime';

describe('CurrentTime Component', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2023-01-01 12:00:00'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('displays current time', () => {
    render(<CurrentTime />);
    expect(screen.getByText('12:00:00 PM')).toBeInTheDocument();
  });

  test('updates time every second', () => {
    render(<CurrentTime />);
    
    expect(screen.getByText('12:00:00 PM')).toBeInTheDocument();
    
    jest.advanceTimersByTime(1000);
    
    expect(screen.getByText('12:00:01 PM')).toBeInTheDocument();
  });
});
```

#### 💡 Learning Focus:
- Mocking external libraries and modules
- API mocking with MSW (Mock Service Worker)
- Testing time-dependent code
- Handling async operations in tests

---

## Day 6: Integration Testing

### 🎯 Challenge: Integration Test Scenarios
Test how multiple components work together in realistic scenarios.

#### Tasks:
1. **Test User Registration Flow**
```javascript
// integration/UserRegistration.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import { server } from '../test/mocks/server';
import { rest } from 'msw';

const AppWithRouter = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

describe('User Registration Integration', () => {
  test('complete user registration flow', async () => {
    const user = userEvent.setup();
    
    // Mock successful registration
    server.use(
      rest.post('/api/register', (req, res, ctx) => {
        return res(
          ctx.status(201),
          ctx.json({ 
            user: { id: 1, name: 'John Doe', email: 'john@example.com' },
            token: 'fake-jwt-token'
          })
        );
      })
    );

    render(<AppWithRouter />);
    
    // Navigate to registration
    await user.click(screen.getByRole('link', { name: /sign up/i }));
    
    // Fill registration form
    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'john@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /sign up/i }));
    
    // Verify successful registration
    await waitFor(() => {
      expect(screen.getByText(/welcome, john doe/i)).toBeInTheDocument();
    });
    
    // Verify navigation to dashboard
    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
  });

  test('handles registration validation errors', async () => {
    const user = userEvent.setup();
    
    // Mock validation error
    server.use(
      rest.post('/api/register', (req, res, ctx) => {
        return res(
          ctx.status(400),
          ctx.json({ 
            errors: { 
              email: 'Email already exists',
              password: 'Password too weak'
            }
          })
        );
      })
    );

    render(<AppWithRouter />);
    
    await user.click(screen.getByRole('link', { name: /sign up/i }));
    
    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'existing@example.com');
    await user.type(screen.getByLabelText(/password/i), '123');
    await user.type(screen.getByLabelText(/confirm password/i), '123');
    
    await user.click(screen.getByRole('button', { name: /sign up/i }));
    
    await waitFor(() => {
      expect(screen.getByText('Email already exists')).toBeInTheDocument();
      expect(screen.getByText('Password too weak')).toBeInTheDocument();
    });
  });
});
```

2. **Test Shopping Cart Flow**
```javascript
// integration/ShoppingCart.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CartProvider } from '../context/CartContext';
import ProductList from '../components/ProductList';
import Cart from '../components/Cart';

const AppWithCart = () => (
  <CartProvider>
    <div>
      <ProductList />
      <Cart />
    </div>
  </CartProvider>
);

describe('Shopping Cart Integration', () => {
  test('add products to cart and checkout', async () => {
    const user = userEvent.setup();
    
    render(<AppWithCart />);
    
    // Add first product
    const addButtons = screen.getAllByRole('button', { name: /add to cart/i });
    await user.click(addButtons[0]);
    
    // Verify cart shows 1 item
    expect(screen.getByText('Cart (1)')).toBeInTheDocument();
    
    // Add second product
    await user.click(addButtons[1]);
    
    // Verify cart shows 2 items
    expect(screen.getByText('Cart (2)')).toBeInTheDocument();
    
    // Open cart
    await user.click(screen.getByRole('button', { name: /view cart/i }));
    
    // Verify products in cart
    expect(screen.getByText('Product 1')).toBeInTheDocument();
    expect(screen.getByText('Product 2')).toBeInTheDocument();
    
    // Update quantity
    const quantityInput = screen.getAllByLabelText(/quantity/i)[0];
    await user.clear(quantityInput);
    await user.type(quantityInput, '3');
    
    // Verify total updated
    await waitFor(() => {
      expect(screen.getByText(/total: \$89.97/i)).toBeInTheDocument();
    });
    
    // Proceed to checkout
    await user.click(screen.getByRole('button', { name: /checkout/i }));
    
    // Verify checkout page
    expect(screen.getByRole('heading', { name: /checkout/i })).toBeInTheDocument();
  });
});
```

#### 💡 Learning Focus:
- Integration testing patterns
- Testing user workflows end-to-end
- Testing component communication
- Complex state management testing

---

## Day 7: E2E Testing & Test-Driven Development

### 🎯 Challenge: End-to-End Testing & TDD
Learn E2E testing with Playwright and practice Test-Driven Development.

#### Tasks:
1. **Set up Playwright E2E Tests**
```bash
npm install --save-dev @playwright/test
npx playwright install
```

```javascript
// e2e/user-authentication.spec.js
import { test, expect } from '@playwright/test';

test.describe('User Authentication', () => {
  test('user can sign up and login', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:3000');
    
    // Click sign up
    await page.click('text=Sign Up');
    
    // Fill registration form
    await page.fill('[data-testid="name-input"]', 'John Doe');
    await page.fill('[data-testid="email-input"]', 'john@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.fill('[data-testid="confirm-password-input"]', 'password123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h1')).toContainText('Welcome, John Doe');
    
    // Logout
    await page.click('[data-testid="logout-button"]');
    
    // Verify redirect to home
    await expect(page).toHaveURL('http://localhost:3000');
    
    // Login with same credentials
    await page.click('text=Login');
    await page.fill('[data-testid="email-input"]', 'john@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Verify successful login
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h1')).toContainText('Welcome, John Doe');
  });

  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    await page.click('text=Login');
    await page.fill('[data-testid="email-input"]', 'wrong@example.com');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Invalid email or password');
  });
});
```

2. **Practice TDD with Todo Component**
```javascript
// First, write the test
// components/TodoList/TodoList.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TodoList from './TodoList';

describe('TodoList Component (TDD)', () => {
  test('renders empty todo list', () => {
    render(<TodoList />);
    expect(screen.getByText('No todos yet')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Add a new todo')).toBeInTheDocument();
  });

  test('adds a new todo', async () => {
    const user = userEvent.setup();
    render(<TodoList />);
    
    const input = screen.getByPlaceholderText('Add a new todo');
    await user.type(input, 'Learn React Testing');
    await user.press('Enter');
    
    expect(screen.getByText('Learn React Testing')).toBeInTheDocument();
    expect(input).toHaveValue('');
  });

  test('toggles todo completion', async () => {
    const user = userEvent.setup();
    render(<TodoList />);
    
    // Add todo
    const input = screen.getByPlaceholderText('Add a new todo');
    await user.type(input, 'Test todo item');
    await user.press('Enter');
    
    // Toggle completion
    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);
    
    expect(checkbox).toBeChecked();
    expect(screen.getByText('Test todo item')).toHaveStyle('text-decoration: line-through');
  });

  test('deletes a todo', async () => {
    const user = userEvent.setup();
    render(<TodoList />);
    
    // Add todo
    const input = screen.getByPlaceholderText('Add a new todo');
    await user.type(input, 'Todo to delete');
    await user.press('Enter');
    
    // Delete todo
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);
    
    expect(screen.queryByText('Todo to delete')).not.toBeInTheDocument();
    expect(screen.getByText('No todos yet')).toBeInTheDocument();
  });

  test('filters todos by status', async () => {
    const user = userEvent.setup();
    render(<TodoList />);
    
    // Add multiple todos
    const input = screen.getByPlaceholderText('Add a new todo');
    await user.type(input, 'Completed todo');
    await user.press('Enter');
    await user.type(input, 'Pending todo');
    await user.press('Enter');
    
    // Complete first todo
    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[0]);
    
    // Filter by completed
    await user.click(screen.getByText('Completed'));
    
    expect(screen.getByText('Completed todo')).toBeInTheDocument();
    expect(screen.queryByText('Pending todo')).not.toBeInTheDocument();
    
    // Filter by active
    await user.click(screen.getByText('Active'));
    
    expect(screen.queryByText('Completed todo')).not.toBeInTheDocument();
    expect(screen.getByText('Pending todo')).toBeInTheDocument();
  });
});

// Now implement the component to make tests pass
// components/TodoList/TodoList.js
import React, { useState } from 'react';
import './TodoList.css';

const TodoList = () => {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [filter, setFilter] = useState('all');

  const addTodo = () => {
    if (inputValue.trim()) {
      setTodos([...todos, {
        id: Date.now(),
        text: inputValue,
        completed: false
      }]);
      setInputValue('');
    }
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  const filteredTodos = todos.filter(todo => {
    if (filter === 'completed') return todo.completed;
    if (filter === 'active') return !todo.completed;
    return true;
  });

  return (
    <div className="todo-list">
      <input
        type="text"
        placeholder="Add a new todo"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && addTodo()}
      />
      
      <div className="filters">
        <button onClick={() => setFilter('all')}>All</button>
        <button onClick={() => setFilter('active')}>Active</button>
        <button onClick={() => setFilter('completed')}>Completed</button>
      </div>

      {filteredTodos.length === 0 ? (
        <p>No todos yet</p>
      ) : (
        <ul>
          {filteredTodos.map(todo => (
            <li key={todo.id}>
              <input
                type="checkbox"
                checked={todo.completed}
                onChange={() => toggleTodo(todo.id)}
              />
              <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
                {todo.text}
              </span>
              <button onClick={() => deleteTodo(todo.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TodoList;
```

3. **Visual Regression Testing**
```javascript
// e2e/visual-regression.spec.js
import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('homepage screenshot', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await expect(page).toHaveScreenshot('homepage.png');
  });

  test('modal dialog screenshot', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.click('[data-testid="open-modal"]');
    await expect(page.locator('.modal')).toHaveScreenshot('modal.png');
  });
});
```

#### 💡 Learning Focus:
- End-to-end testing with Playwright
- Test-Driven Development workflow
- Visual regression testing
- Testing complete user journeys

---

## 🎯 Weekly Project: Testing Strategy Implementation

### Project: Comprehensive Testing Suite for React App

Create a complete testing strategy for a React application with the following requirements:

#### Core Features to Test:
1. **User Authentication System**
   - Registration with validation
   - Login/logout functionality
   - Protected routes
   - Session management

2. **Data Management**
   - CRUD operations for entities
   - API error handling
   - Loading states
   - Optimistic updates

3. **Complex UI Components**
   - Multi-step forms
   - Data tables with sorting/filtering
   - Modal dialogs
   - Dynamic content rendering

#### Testing Requirements:
1. **Unit Tests (70% coverage minimum)**
   - All utility functions
   - Custom hooks
   - Individual components
   - Context providers

2. **Integration Tests**
   - Component interactions
   - Context consumption
   - API integration
   - Route navigation

3. **E2E Tests**
   - Critical user paths
   - Cross-browser compatibility
   - Mobile responsiveness
   - Performance benchmarks

#### Implementation Tasks:
```javascript
// Example test structure
src/
  __tests__/
    unit/
      components/
      hooks/
      utils/
    integration/
      auth-flow.test.js
      data-management.test.js
    e2e/
      user-journeys.spec.js
      visual-regression.spec.js
  __mocks__/
    api.js
    localStorage.js
  test-utils/
    render-with-providers.js
    mock-data.js
  setupTests.js
```

#### Success Criteria:
- [ ] 80%+ test coverage
- [ ] All critical paths covered by E2E tests
- [ ] CI/CD pipeline with automated testing
- [ ] Performance regression prevention
- [ ] Accessibility testing included
- [ ] Documentation for testing conventions

---

## 📚 Additional Resources

### Testing Tools & Libraries:
- **Jest**: JavaScript testing framework
- **React Testing Library**: Simple and complete testing utilities
- **Playwright**: Modern E2E testing framework
- **MSW**: API mocking library
- **Jest-dom**: Custom Jest matchers

### Best Practices:
- Write tests before or alongside code (TDD)
- Test behavior, not implementation
- Use descriptive test names
- Keep tests simple and focused
- Mock external dependencies
- Test edge cases and error scenarios

### Performance Testing:
- Use React DevTools Profiler
- Measure component render times
- Test with realistic data volumes
- Monitor bundle size impact
- Implement visual regression testing

---

## ✅ Week 13 Completion Checklist

### Daily Challenges Completed:
- [ ] Day 1: Testing Environment Setup & Fundamentals
- [ ] Day 2: Testing User Interactions
- [ ] Day 3: Testing React Hooks
- [ ] Day 4: Context and Provider Testing
- [ ] Day 5: Mocking and API Testing
- [ ] Day 6: Integration Testing
- [ ] Day 7: E2E Testing & Test-Driven Development

### Weekly Project:
- [ ] Comprehensive testing suite implemented
- [ ] All testing types covered (unit, integration, E2E)
- [ ] CI/CD pipeline configured
- [ ] Testing documentation created

### Key Skills Mastered:
- [ ] React Testing Library proficiency
- [ ] Jest testing framework
- [ ] Custom hook testing
- [ ] Context testing patterns
- [ ] API mocking strategies
- [ ] Integration testing approaches
- [ ] E2E testing with Playwright
- [ ] Test-Driven Development
- [ ] Testing best practices

**Next Week Preview**: Week 14 will focus on Code Quality, including ESLint, Prettier, TypeScript integration, code reviews, and maintainability best practices.

---

*"Testing is not about finding bugs; it's about building confidence in your code and ensuring it works as expected for your users."*