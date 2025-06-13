# Integration Testing, End-to-End Testing & Advanced Testing Patterns

## Table of Contents
1. [Integration Testing Fundamentals](#integration-testing-fundamentals)
2. [API Integration Testing](#api-integration-testing)
3. [End-to-End Testing with Cypress](#end-to-end-testing-with-cypress)
4. [Playwright for Modern E2E Testing](#playwright-for-modern-e2e-testing)
5. [Visual Regression Testing](#visual-regression-testing)
6. [Performance Testing](#performance-testing)
7. [Accessibility Testing](#accessibility-testing)
8. [Advanced Testing Patterns](#advanced-testing-patterns)
9. [Testing in Production](#testing-in-production)
10. [Continuous Integration Testing](#continuous-integration-testing)

---

## Integration Testing Fundamentals

### Understanding Integration Testing

Integration testing verifies that different parts of your application work together correctly. Unlike unit tests that test components in isolation, integration tests examine the interactions between components, services, and external dependencies.

```javascript
// Integration test example - Testing component interaction with context
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserProvider, UserContext } from '../contexts/UserContext';
import UserProfile from '../components/UserProfile';
import UserSettings from '../components/UserSettings';

describe('User Management Integration', () => {
  const TestWrapper = ({ children }) => (
    <UserProvider>
      {children}
    </UserProvider>
  );

  test('should update user profile and reflect changes in settings', async () => {
    render(
      <TestWrapper>
        <UserProfile />
        <UserSettings />
      </TestWrapper>
    );

    // Update profile
    const nameInput = screen.getByLabelText(/name/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.click(screen.getByText(/save profile/i));

    // Verify changes appear in settings
    await waitFor(() => {
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
    });
  });
});
```

### Testing Component Hierarchies

```javascript
// Testing parent-child component interactions
import { render, screen, fireEvent } from '@testing-library/react';
import TodoApp from '../components/TodoApp';

describe('Todo App Integration', () => {
  test('should add todo and update list', () => {
    render(<TodoApp />);
    
    // Add new todo
    const input = screen.getByPlaceholderText(/add new todo/i);
    fireEvent.change(input, { target: { value: 'Learn React Testing' } });
    fireEvent.click(screen.getByText(/add todo/i));
    
    // Verify todo appears in list
    expect(screen.getByText('Learn React Testing')).toBeInTheDocument();
    
    // Verify input is cleared
    expect(input.value).toBe('');
  });

  test('should complete todo and update status', () => {
    render(<TodoApp />);
    
    // Add todo first
    const input = screen.getByPlaceholderText(/add new todo/i);
    fireEvent.change(input, { target: { value: 'Test todo' } });
    fireEvent.click(screen.getByText(/add todo/i));
    
    // Complete todo
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    
    // Verify completion
    expect(checkbox).toBeChecked();
    expect(screen.getByText('Test todo')).toHaveClass('completed');
  });
});
```

### Testing Routing Integration

```javascript
// Testing routing with React Router
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

describe('Navigation Integration', () => {
  test('should navigate between pages', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    // Start at home page
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();

    // Navigate to about page
    fireEvent.click(screen.getByText(/about/i));
    expect(screen.getByText(/about us/i)).toBeInTheDocument();

    // Navigate to contact page
    fireEvent.click(screen.getByText(/contact/i));
    expect(screen.getByText(/contact form/i)).toBeInTheDocument();
  });

  test('should handle protected routes', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    );

    // Should redirect to login for protected route
    expect(screen.getByText(/please log in/i)).toBeInTheDocument();
  });
});
```

---

## API Integration Testing

### Mocking API Calls with MSW

```javascript
// Setting up Mock Service Worker for API testing
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
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

  rest.delete('/api/users/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Testing Data Fetching Components

```javascript
// Testing components that fetch data
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import UserList from '../components/UserList';

describe('UserList API Integration', () => {
  let queryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
  });

  test('should fetch and display users', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <UserList />
      </QueryClientProvider>
    );

    // Should show loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Should display users after loading
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  test('should handle API errors', async () => {
    // Override default handler to return error
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    render(
      <QueryClientProvider client={queryClient}>
        <UserList />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/error loading users/i)).toBeInTheDocument();
    });
  });
});
```

### Testing Real-time Features

```javascript
// Testing WebSocket connections
import { render, screen, act } from '@testing-library/react';
import WS from 'jest-websocket-mock';
import ChatComponent from '../components/ChatComponent';

describe('Real-time Chat Integration', () => {
  let server;

  beforeEach(async () => {
    server = new WS('ws://localhost:8080');
  });

  afterEach(() => {
    WS.clean();
  });

  test('should connect to WebSocket and receive messages', async () => {
    render(<ChatComponent />);

    await server.connected;
    expect(server).toHaveReceivedMessages(['{"type":"connect"}']);

    // Simulate incoming message
    act(() => {
      server.send('{"type":"message","content":"Hello World","user":"Alice"}');
    });

    expect(screen.getByText('Alice: Hello World')).toBeInTheDocument();
  });

  test('should send messages through WebSocket', async () => {
    render(<ChatComponent />);

    await server.connected;

    // Send message
    const input = screen.getByPlaceholderText(/type message/i);
    const sendButton = screen.getByText(/send/i);

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await expect(server).toReceiveMessage(
      JSON.stringify({ type: 'message', content: 'Test message' })
    );
  });
});
```

---

## End-to-End Testing with Cypress

### Cypress Setup and Configuration

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
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

### Basic E2E Test Structure

```javascript
// cypress/e2e/user-journey.cy.js
describe('User Journey E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should complete user registration flow', () => {
    // Navigate to registration
    cy.get('[data-cy="register-link"]').click();
    cy.url().should('include', '/register');

    // Fill registration form
    cy.get('[data-cy="email-input"]').type('test@example.com');
    cy.get('[data-cy="password-input"]').type('securePassword123');
    cy.get('[data-cy="confirm-password-input"]').type('securePassword123');
    cy.get('[data-cy="register-button"]').click();

    // Verify successful registration
    cy.get('[data-cy="success-message"]')
      .should('be.visible')
      .and('contain', 'Registration successful');

    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('[data-cy="welcome-message"]').should('be.visible');
  });

  it('should handle login flow', () => {
    cy.get('[data-cy="login-link"]').click();
    
    cy.get('[data-cy="email-input"]').type('existing@example.com');
    cy.get('[data-cy="password-input"]').type('password123');
    cy.get('[data-cy="login-button"]').click();

    cy.get('[data-cy="dashboard"]').should('be.visible');
    cy.get('[data-cy="user-menu"]').should('contain', 'existing@example.com');
  });
});
```

### Advanced Cypress Patterns

```javascript
// Custom commands
// cypress/support/commands.js
Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: '/api/auth/login',
    body: { email, password }
  }).then((response) => {
    localStorage.setItem('authToken', response.body.token);
  });
});

Cypress.Commands.add('createUser', (userData) => {
  return cy.request({
    method: 'POST',
    url: '/api/users',
    body: userData,
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('authToken')}`
    }
  });
});

// Using custom commands
describe('User Management E2E', () => {
  beforeEach(() => {
    cy.login('admin@example.com', 'adminPassword');
    cy.visit('/admin/users');
  });

  it('should create and manage users', () => {
    // Create new user
    cy.get('[data-cy="add-user-button"]').click();
    cy.get('[data-cy="user-form"]').should('be.visible');

    cy.get('[data-cy="name-input"]').type('New User');
    cy.get('[data-cy="email-input"]').type('newuser@example.com');
    cy.get('[data-cy="role-select"]').select('Editor');
    cy.get('[data-cy="save-user-button"]').click();

    // Verify user appears in list
    cy.get('[data-cy="user-table"]')
      .should('contain', 'New User')
      .and('contain', 'newuser@example.com');

    // Edit user
    cy.get('[data-cy="user-row"]')
      .contains('New User')
      .find('[data-cy="edit-button"]')
      .click();

    cy.get('[data-cy="role-select"]').select('Admin');
    cy.get('[data-cy="save-user-button"]').click();

    // Verify changes
    cy.get('[data-cy="user-table"]')
      .contains('New User')
      .should('contain', 'Admin');
  });
});
```

### Testing Complex User Interactions

```javascript
// Testing drag and drop
describe('Kanban Board E2E', () => {
  beforeEach(() => {
    cy.login('user@example.com', 'password');
    cy.visit('/kanban');
  });

  it('should drag tasks between columns', () => {
    // Create a task first
    cy.get('[data-cy="add-task-button"]').click();
    cy.get('[data-cy="task-title-input"]').type('Test Task');
    cy.get('[data-cy="create-task-button"]').click();

    // Verify task is in "To Do" column
    cy.get('[data-cy="todo-column"]')
      .should('contain', 'Test Task');

    // Drag task to "In Progress"
    cy.get('[data-cy="task"]')
      .contains('Test Task')
      .trigger('mousedown', { button: 0 })
      .trigger('mousemove', { clientX: 400, clientY: 200 })
      .trigger('mouseup');

    // Verify task moved
    cy.get('[data-cy="inprogress-column"]')
      .should('contain', 'Test Task');
    cy.get('[data-cy="todo-column"]')
      .should('not.contain', 'Test Task');
  });
});
```

---

## Playwright for Modern E2E Testing

### Playwright Setup

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...require('@playwright/test').devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...require('@playwright/test').devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...require('@playwright/test').devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm start',
    port: 3000,
  },
});
```

### Playwright Test Examples

```javascript
// tests/user-flow.spec.js
const { test, expect } = require('@playwright/test');

test.describe('User Authentication Flow', () => {
  test('should register new user', async ({ page }) => {
    await page.goto('/register');

    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'securePassword123');
    await page.fill('[data-testid="confirmPassword"]', 'securePassword123');
    
    await page.click('[data-testid="register-button"]');

    await expect(page.locator('[data-testid="success-message"]'))
      .toContainText('Registration successful');
    
    await expect(page).toHaveURL('/dashboard');
  });

  test('should handle login with valid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[data-testid="email"]', 'existing@example.com');
    await page.fill('[data-testid="password"]', 'validPassword');
    
    await page.click('[data-testid="login-button"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-welcome"]'))
      .toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[data-testid="email"]', 'wrong@example.com');
    await page.fill('[data-testid="password"]', 'wrongPassword');
    
    await page.click('[data-testid="login-button"]');

    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Invalid credentials');
  });
});
```

### Advanced Playwright Features

```javascript
// Testing with multiple contexts and pages
test('should handle multi-tab scenarios', async ({ context }) => {
  // Create two pages
  const page1 = await context.newPage();
  const page2 = await context.newPage();

  // Login on first page
  await page1.goto('/login');
  await page1.fill('[data-testid="email"]', 'user@example.com');
  await page1.fill('[data-testid="password"]', 'password');
  await page1.click('[data-testid="login-button"]');

  // Navigate to dashboard on second page
  await page2.goto('/dashboard');
  
  // Should be logged in due to shared context
  await expect(page2.locator('[data-testid="user-welcome"]'))
    .toBeVisible();

  // Logout on first page
  await page1.click('[data-testid="logout-button"]');

  // Refresh second page - should redirect to login
  await page2.reload();
  await expect(page2).toHaveURL('/login');
});

// Testing with network interception
test('should handle API failures gracefully', async ({ page }) => {
  // Intercept and mock API call
  await page.route('/api/users', route => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' })
    });
  });

  await page.goto('/users');

  await expect(page.locator('[data-testid="error-message"]'))
    .toContainText('Failed to load users');
  await expect(page.locator('[data-testid="retry-button"]'))
    .toBeVisible();
});
```

---

## Visual Regression Testing

### Setting up Visual Testing with Playwright

```javascript
// Visual regression test examples
test('should match homepage design', async ({ page }) => {
  await page.goto('/');
  
  // Take full page screenshot
  await expect(page).toHaveScreenshot('homepage.png');
});

test('should match component designs', async ({ page }) => {
  await page.goto('/components');
  
  // Screenshot specific component
  await expect(page.locator('[data-testid="button-component"]'))
    .toHaveScreenshot('button-component.png');
    
  // Screenshot with specific viewport
  await page.setViewportSize({ width: 375, height: 667 });
  await expect(page.locator('[data-testid="mobile-nav"]'))
    .toHaveScreenshot('mobile-nav.png');
});

test('should match dark theme', async ({ page }) => {
  await page.goto('/');
  
  // Switch to dark theme
  await page.click('[data-testid="theme-toggle"]');
  
  await expect(page).toHaveScreenshot('homepage-dark.png');
});
```

### Visual Testing with Storybook

```javascript
// .storybook/test-runner.js
const { getStoryContext } = require('@storybook/test-runner');

module.exports = {
  async postRender(page, context) {
    const storyContext = await getStoryContext(page, context);
    
    // Take screenshot for visual regression
    await page.screenshot({
      path: `screenshots/${context.id}.png`,
      fullPage: true
    });
    
    // Test accessibility
    await page.evaluate(() => {
      const axe = require('axe-core');
      return axe.run();
    });
  }
};
```

---

## Performance Testing

### Web Vitals Testing

```javascript
// Performance testing with Playwright
test('should meet Core Web Vitals thresholds', async ({ page }) => {
  // Navigate to page
  await page.goto('/');

  // Measure performance metrics
  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const vitals = {};
        
        entries.forEach((entry) => {
          if (entry.name === 'FCP') vitals.fcp = entry.value;
          if (entry.name === 'LCP') vitals.lcp = entry.value;
          if (entry.name === 'CLS') vitals.cls = entry.value;
          if (entry.name === 'FID') vitals.fid = entry.value;
        });
        
        resolve(vitals);
      }).observe({ entryTypes: ['navigation', 'paint', 'largest-contentful-paint'] });
    });
  });

  // Assert performance thresholds
  expect(metrics.fcp).toBeLessThan(2000); // First Contentful Paint < 2s
  expect(metrics.lcp).toBeLessThan(3000); // Largest Contentful Paint < 3s
  expect(metrics.cls).toBeLessThan(0.1);  // Cumulative Layout Shift < 0.1
});
```

### Load Testing with Artillery

```yaml
# artillery-config.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 50
    - duration: 60
      arrivalRate: 100

scenarios:
  - name: "Homepage load test"
    flow:
      - get:
          url: "/"
      - think: 1
      - get:
          url: "/api/users"
      - think: 2
      - post:
          url: "/api/analytics"
          json:
            event: "page_view"
            page: "/"
```

---

## Accessibility Testing

### Automated Accessibility Testing

```javascript
// Accessibility testing with @testing-library/jest-dom and axe
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import App from '../App';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  test('should not have accessibility violations', async () => {
    const { container } = render(<App />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('should have proper heading hierarchy', async () => {
    const { container } = render(<App />);
    
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    expect(headings).toHaveLength.greaterThan(0);
    
    // First heading should be h1
    expect(headings[0].tagName).toBe('H1');
  });

  test('should have proper form labels', () => {
    render(<ContactForm />);
    
    const inputs = screen.getAllByRole('textbox');
    inputs.forEach(input => {
      expect(input).toHaveAccessibleName();
    });
  });
});
```

### Keyboard Navigation Testing

```javascript
// Testing keyboard navigation
test('should support keyboard navigation', async () => {
  render(<NavigationMenu />);
  
  const firstLink = screen.getByRole('link', { name: /home/i });
  firstLink.focus();
  
  // Tab through navigation
  userEvent.tab();
  expect(screen.getByRole('link', { name: /about/i })).toHaveFocus();
  
  userEvent.tab();
  expect(screen.getByRole('link', { name: /contact/i })).toHaveFocus();
  
  // Test Enter key activation
  userEvent.keyboard('{Enter}');
  expect(window.location.pathname).toBe('/contact');
});

// Testing screen reader support
test('should provide proper screen reader content', () => {
  render(<ProductCard product={mockProduct} />);
  
  // Check ARIA labels
  expect(screen.getByLabelText(/add to cart/i)).toBeInTheDocument();
  
  // Check live regions
  expect(screen.getByRole('status')).toBeInTheDocument();
  
  // Check semantic HTML
  expect(screen.getByRole('article')).toBeInTheDocument();
});
```

---

## Advanced Testing Patterns

### Property-Based Testing

```javascript
// Property-based testing with fast-check
import fc from 'fast-check';
import { formatCurrency } from '../utils/currency';

describe('Currency Formatter Properties', () => {
  test('should always return a string', () => {
    fc.assert(fc.property(
      fc.float({ min: 0, max: 1000000 }),
      (amount) => {
        const result = formatCurrency(amount);
        return typeof result === 'string';
      }
    ));
  });

  test('should handle edge cases', () => {
    fc.assert(fc.property(
      fc.oneof(
        fc.constant(0),
        fc.constant(Number.MAX_SAFE_INTEGER),
        fc.constant(Number.MIN_SAFE_INTEGER),
        fc.float()
      ),
      (amount) => {
        expect(() => formatCurrency(amount)).not.toThrow();
      }
    ));
  });
});
```

### Mutation Testing

```javascript
// Mutation testing configuration with Stryker
// stryker.conf.js
module.exports = {
  packageManager: 'npm',
  reporters: ['html', 'clear-text', 'progress'],
  testRunner: 'jest',
  jest: {
    projectType: 'react'
  },
  coverageAnalysis: 'perTest',
  mutate: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/**/*.spec.js'
  ]
};
```

### Contract Testing

```javascript
// Contract testing with Pact
import { Pact } from '@pact-foundation/pact';
import { UserService } from '../services/UserService';

describe('User Service Contract Tests', () => {
  const provider = new Pact({
    consumer: 'Frontend',
    provider: 'UserAPI',
    port: 1234,
    log: path.resolve(process.cwd(), 'logs', 'pact.log'),
    dir: path.resolve(process.cwd(), 'pacts'),
    logLevel: 'INFO'
  });

  beforeAll(() => provider.setup());
  afterEach(() => provider.verify());
  afterAll(() => provider.finalize());

  test('should get user by ID', async () => {
    await provider.addInteraction({
      state: 'user exists',
      uponReceiving: 'a request for user',
      withRequest: {
        method: 'GET',
        path: '/api/users/1',
        headers: {
          'Accept': 'application/json'
        }
      },
      willRespondWith: {
        status: 200,
        headers: {
          'Content-Type': 'application/json'
        },
        body: {
          id: 1,
          name: 'John Doe',
          email: 'john@example.com'
        }
      }
    });

    const user = await UserService.getUser(1);
    expect(user).toEqual({
      id: 1,
      name: 'John Doe',
      email: 'john@example.com'
    });
  });
});
```

---

## Testing in Production

### Feature Flag Testing

```javascript
// Testing feature flags
import { render, screen } from '@testing-library/react';
import { FeatureFlagProvider } from '../contexts/FeatureFlagContext';
import NewFeatureComponent from '../components/NewFeatureComponent';

describe('Feature Flag Tests', () => {
  test('should show new feature when flag is enabled', () => {
    render(
      <FeatureFlagProvider flags={{ newFeature: true }}>
        <NewFeatureComponent />
      </FeatureFlagProvider>
    );

    expect(screen.getByText(/new feature/i)).toBeInTheDocument();
  });

  test('should hide new feature when flag is disabled', () => {
    render(
      <FeatureFlagProvider flags={{ newFeature: false }}>
        <NewFeatureComponent />
      </FeatureFlagProvider>
    );

    expect(screen.queryByText(/new feature/i)).not.toBeInTheDocument();
  });
});
```

### A/B Testing

```javascript
// A/B testing setup
import { render, screen } from '@testing-library/react';
import { ABTestProvider } from '../contexts/ABTestContext';
import LandingPage from '../components/LandingPage';

describe('A/B Testing', () => {
  test('should render variant A', () => {
    render(
      <ABTestProvider variant="A">
        <LandingPage />
      </ABTestProvider>
    );

    expect(screen.getByText(/original design/i)).toBeInTheDocument();
  });

  test('should render variant B', () => {
    render(
      <ABTestProvider variant="B">
        <LandingPage />
      </ABTestProvider>
    );

    expect(screen.getByText(/new design/i)).toBeInTheDocument();
  });
});
```

### Error Monitoring Testing

```javascript
// Testing error boundaries and monitoring
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { ErrorReporting } from '../services/ErrorReporting';

const ThrowError = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('Error Monitoring', () => {
  let errorSpy;

  beforeEach(() => {
    errorSpy = jest.spyOn(ErrorReporting, 'logError').mockImplementation();
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('should catch and report errors', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(errorSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Test error'
      })
    );
  });
});
```

---

## Continuous Integration Testing

### GitHub Actions Testing Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linting
      run: npm run lint
    
    - name: Run unit tests
      run: npm run test:unit -- --coverage
    
    - name: Run integration tests
      run: npm run test:integration
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info

  e2e:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Install Playwright
      run: npx playwright install --with-deps
    
    - name: Build application
      run: npm run build
    
    - name: Run E2E tests
      run: npm run test:e2e
    
    - name: Upload Playwright report
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: playwright-report
        path: playwright-report/
```

### Parallel Testing Strategy

```javascript
// jest.config.js for parallel testing
module.exports = {
  maxWorkers: '50%',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/?(*.)(spec|test).{js,jsx,ts,tsx}'
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js',
    '!src/serviceWorker.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js']
};
```

### Test Result Reporting

```javascript
// Custom test reporter
class CustomReporter {
  onRunComplete(contexts, results) {
    const { numFailedTests, numPassedTests, testResults } = results;
    
    // Send results to monitoring service
    const report = {
      passed: numPassedTests,
      failed: numFailedTests,
      coverage: results.coverageMap?.getCoverageSummary(),
      timestamp: new Date().toISOString(),
      branch: process.env.GITHUB_REF_NAME,
      commit: process.env.GITHUB_SHA
    };
    
    // Send to monitoring dashboard
    this.sendToMonitoring(report);
  }
  
  async sendToMonitoring(report) {
    try {
      await fetch('/api/test-results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report)
      });
    } catch (error) {
      console.error('Failed to send test results:', error);
    }
  }
}

module.exports = CustomReporter;
```

---

## Best Practices Summary

### Testing Strategy Guidelines

1. **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E tests
2. **Test Coverage**: Aim for 80%+ coverage but focus on critical paths
3. **Test Reliability**: Flaky tests are worse than no tests
4. **Performance**: Keep test suite execution time reasonable
5. **Maintainability**: Tests should be easy to read and update

### Anti-Patterns to Avoid

```javascript
// ❌ Bad: Testing implementation details
test('should call useState with initial value', () => {
  const spy = jest.spyOn(React, 'useState');
  render(<Counter />);
  expect(spy).toHaveBeenCalledWith(0);
});

// ✅ Good: Testing behavior
test('should display initial count of 0', () => {
  render(<Counter />);
  expect(screen.getByText('Count: 0')).toBeInTheDocument();
});

// ❌ Bad: Overly complex test setup
test('should update user profile', async () => {
  const mockUser = createMockUser();
  const mockDispatch = jest.fn();
  const mockHistory = createMemoryHistory();
  const mockStore = createMockStore();
  // ... 20 more lines of setup
});

// ✅ Good: Simple, focused test
test('should update user profile', async () => {
  render(<UserProfile />, { wrapper: TestWrapper });
  
  fireEvent.change(screen.getByLabelText(/name/i), { 
    target: { value: 'New Name' } 
  });
  fireEvent.click(screen.getByText(/save/i));
  
  await waitFor(() => {
    expect(screen.getByDisplayValue('New Name')).toBeInTheDocument();
  });
});
```

This comprehensive guide covers integration testing, E2E testing, and advanced testing patterns that are essential for building robust React applications. The key is to use the right testing approach for each scenario and maintain a balanced testing strategy that provides confidence without overwhelming complexity.
