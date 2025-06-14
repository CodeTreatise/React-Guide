# 📅 Week 1: JavaScript Prerequisites - Daily Challenges

> **Goal**: Master ES6+ and async JavaScript through hands-on practice  
> **Format**: One challenge per day with increasing difficulty  
> **Time**: 30-60 minutes per challenge

---

## 🎯 Challenge Structure

Each challenge includes:
- **Problem Statement**: What you need to build
- **Requirements**: Specific features to implement
- **Starter Code**: Basic structure to begin with
- **Solution Tips**: Hints without giving away the answer
- **Bonus**: Extra features for advanced practice

---

## Day 1: ES6+ Transformation Challenge

### Problem Statement
Transform an old ES5 JavaScript utility library to modern ES6+ syntax while adding new features.

### Requirements
1. Convert all ES5 functions to arrow functions where appropriate
2. Use template literals for string formatting
3. Implement destructuring for object/array operations
4. Add default parameters
5. Use spread operator for array/object operations
6. Export functions using ES6 modules

### Starter Code
```javascript
// ES5 Legacy Code (transform this)
var UserUtils = {
    createUser: function(firstName, lastName, age, email) {
        var fullName = firstName + ' ' + lastName;
        var user = {
            id: Math.floor(Math.random() * 1000),
            firstName: firstName,
            lastName: lastName,
            fullName: fullName,
            age: age,
            email: email,
            isAdult: age >= 18,
            createdAt: new Date().toISOString()
        };
        return user;
    },
    
    formatUserInfo: function(user) {
        var ageStatus = user.isAdult ? 'Adult' : 'Minor';
        return 'Name: ' + user.fullName + ', Age: ' + user.age + ' (' + ageStatus + '), Email: ' + user.email;
    },
    
    updateUser: function(originalUser, updates) {
        var updatedUser = {};
        for (var key in originalUser) {
            updatedUser[key] = originalUser[key];
        }
        for (var key in updates) {
            updatedUser[key] = updates[key];
        }
        updatedUser.updatedAt = new Date().toISOString();
        return updatedUser;
    },
    
    filterActiveUsers: function(users) {
        var activeUsers = [];
        for (var i = 0; i < users.length; i++) {
            if (users[i].isActive) {
                activeUsers.push(users[i]);
            }
        }
        return activeUsers;
    }
};
```

### Your Task
Transform the above code to modern ES6+ and add these features:
1. Add input validation
2. Create a `UserCollection` class to manage multiple users
3. Add search functionality
4. Implement user sorting by different criteria

### Solution Tips
- Use object shorthand where possible
- Consider when to use arrow functions vs regular functions
- Use array methods instead of for loops
- Implement proper error handling

### Bonus Challenge
- Add TypeScript-style JSDoc comments
- Implement method chaining
- Add user statistics calculation

---

## Day 2: Async Data Pipeline Challenge

### Problem Statement
Build an async data processing pipeline that fetches, transforms, and caches user data from multiple sources.

### Requirements
1. Fetch data from multiple mock APIs simultaneously
2. Transform and combine the data
3. Implement retry logic for failed requests
4. Add caching mechanism
5. Handle all errors gracefully
6. Provide loading progress updates

### Starter Code
```javascript
{% raw %}
{% raw %}
// Mock API functions (simulate real APIs)
function fetchUserBasicInfo(userId) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.2) { // 80% success rate
                resolve({
                    id: userId,
                    name: `User ${userId}`,
                    email: `user${userId}@example.com`
                });
            } else {
                reject(new Error('Failed to fetch basic info'));
            }
        }, Math.random() * 1000 + 500); // 500-1500ms delay
    });
}

function fetchUserProfile(userId) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.15) { // 85% success rate
                resolve({
                    userId: userId,
                    bio: `Bio for user ${userId}`,
                    avatar: `https://api.avatar.com/${userId}`,
                    joinDate: new Date().toISOString()
                });
            } else {
                reject(new Error('Failed to fetch profile'));
            }
        }, Math.random() * 800 + 300); // 300-1100ms delay
    });
}

function fetchUserActivity(userId) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.1) { // 90% success rate
                resolve({
                    userId: userId,
                    lastLogin: new Date().toISOString(),
                    activityScore: Math.floor(Math.random() * 100),
                    postsCount: Math.floor(Math.random() * 50)
                });
            } else {
                reject(new Error('Failed to fetch activity'));
            }
        }, Math.random() * 600 + 200); // 200-800ms delay
    });
}
{% endraw %}
{% endraw %}
```

### Your Task
Create a `UserDataPipeline` class with these methods:

```javascript
class UserDataPipeline {
    constructor() {
        this.cache = new Map();
        this.maxRetries = 3;
    }
    
    // Fetch complete user data with retry logic
    async fetchCompleteUserData(userId) {
        // Your implementation here
    }
    
    // Fetch multiple users in parallel
    async fetchMultipleUsers(userIds, onProgress) {
        // Your implementation here
        // onProgress(current, total, userId) callback for progress updates
    }
    
    // Cache management
    getCachedUser(userId) {
        // Your implementation here
    }
    
    setCachedUser(userId, userData) {
        // Your implementation here
    }
    
    // Retry logic
    async retryOperation(operation, maxRetries = 3) {
        // Your implementation here
    }
}
```

### Expected Output Format
```javascript
{
    id: 1,
    name: "User 1",
    email: "user1@example.com",
    bio: "Bio for user 1",
    avatar: "https://api.avatar.com/1",
    joinDate: "2024-01-01T00:00:00.000Z",
    lastLogin: "2024-06-09T10:30:00.000Z",
    activityScore: 85,
    postsCount: 23,
    fetchedAt: "2024-06-09T10:30:00.000Z",
    fromCache: false
}
```

### Solution Tips
- Use Promise.allSettled() for parallel requests
- Implement exponential backoff for retries
- Use WeakMap or Map for caching
- Consider using AbortController for request cancellation

### Bonus Challenge
- Add request deduplication (prevent duplicate simultaneous requests)
- Implement cache expiration
- Add data validation and sanitization
- Create a React hook that uses this pipeline

---

## Day 3: Functional Programming Challenge

### Problem Statement
Build a functional programming utility library for data transformation using ES6+ features.

### Requirements
1. Create pure functions for data transformation
2. Implement function composition
3. Use currying for reusable functions
4. Build pipeline operators
5. Handle immutable data updates
6. Add error handling in functional style

### Your Task
Build these functional utilities:

```javascript
// Function composition utilities
const compose = (...functions) => {
    // Your implementation
};

const pipe = (...functions) => {
    // Your implementation
};

// Currying utilities
const curry = (fn) => {
    // Your implementation
};

// Data transformation functions
const map = curry((fn, array) => {
    // Your implementation
});

const filter = curry((predicate, array) => {
    // Your implementation
});

const reduce = curry((reducer, initialValue, array) => {
    // Your implementation
});

// Object manipulation
const pick = curry((keys, obj) => {
    // Your implementation
});

const omit = curry((keys, obj) => {
    // Your implementation
});

const updateProperty = curry((path, value, obj) => {
    // Your implementation - supports nested paths like 'user.profile.name'
});

// Array utilities
const groupBy = curry((keyFn, array) => {
    // Your implementation
});

const sortBy = curry((keyFn, array) => {
    // Your implementation
});

const unique = (array) => {
    // Your implementation
};

const flatten = (array) => {
    // Your implementation
};
```

### Example Usage
```javascript
// Sample data
const users = [
    { id: 1, name: 'John', age: 25, department: 'IT', salary: 50000 },
    { id: 2, name: 'Jane', age: 30, department: 'HR', salary: 55000 },
    { id: 3, name: 'Bob', age: 35, department: 'IT', salary: 60000 },
    { id: 4, name: 'Alice', age: 28, department: 'Marketing', salary: 52000 }
];

// Example transformations
const getITUsersOver25 = pipe(
    filter(user => user.department === 'IT'),
    filter(user => user.age > 25),
    map(pick(['name', 'age', 'salary']))
);

const result = getITUsersOver25(users);
console.log(result); // [{ name: 'Bob', age: 35, salary: 60000 }]

// Grouping and statistics
const departmentStats = pipe(
    groupBy(user => user.department),
    Object.entries,
    map(([dept, users]) => ({
        department: dept,
        count: users.length,
        avgSalary: users.reduce((sum, user) => sum + user.salary, 0) / users.length
    }))
);
```

### Solution Tips
- Use rest/spread operators extensively
- Implement proper currying with variable arguments
- Consider using Symbols for private properties
- Add type checking for development

### Bonus Challenge
- Add async versions of map, filter, reduce
- Implement memoization decorator
- Create a Maybe/Optional monad for null safety
- Add performance benchmarking utilities

---

## Day 4: Module System & Architecture Challenge

### Problem Statement
Design and implement a modular JavaScript architecture for a task management system using ES6 modules.

### Requirements
1. Create separate modules for different concerns
2. Implement proper import/export patterns
3. Use namespace imports and default exports appropriately
4. Build a plugin system
5. Handle circular dependencies
6. Implement lazy loading

### Project Structure
```
task-manager/
├── core/
│   ├── TaskManager.js
│   ├── EventEmitter.js
│   └── Storage.js
├── models/
│   ├── Task.js
│   ├── User.js
│   └── Project.js
├── plugins/
│   ├── PluginSystem.js
│   ├── NotificationPlugin.js
│   └── AnalyticsPlugin.js
├── utils/
│   ├── validators.js
│   ├── formatters.js
│   └── constants.js
├── services/
│   ├── ApiService.js
│   └── SyncService.js
└── index.js
```

### Your Task
Implement each module following these patterns:

```javascript
// models/Task.js
export class Task {
    constructor(data) {
        // Implementation
    }
    
    static create(data) {
        // Static factory method
    }
    
    update(updates) {
        // Update method returning new instance
    }
    
    validate() {
        // Validation logic
    }
}

export const TaskStatus = {
    PENDING: 'pending',
    IN_PROGRESS: 'in_progress',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled'
};

export default Task;

// core/EventEmitter.js
export default class EventEmitter {
    constructor() {
        this.events = new Map();
    }
    
    on(event, listener) {
        // Implementation
    }
    
    off(event, listener) {
        // Implementation
    }
    
    emit(event, ...args) {
        // Implementation
    }
    
    once(event, listener) {
        // Implementation
    }
}

// plugins/PluginSystem.js
export class PluginSystem {
    constructor() {
        this.plugins = new Map();
        this.hooks = new Map();
    }
    
    register(plugin) {
        // Plugin registration
    }
    
    unregister(pluginName) {
        // Plugin removal
    }
    
    async loadPlugin(pluginPath) {
        // Dynamic import for lazy loading
    }
    
    addHook(hookName, callback) {
        // Hook system for extensibility
    }
    
    executeHook(hookName, ...args) {
        // Hook execution
    }
}
```

### Features to Implement
1. **Task CRUD operations** with validation
2. **Event system** for loose coupling
3. **Plugin architecture** for extensibility
4. **Storage abstraction** (localStorage, IndexedDB, etc.)
5. **API service** with retry logic
6. **Sync service** for offline support

### Integration Example
```javascript
// index.js
import TaskManager from './core/TaskManager.js';
import NotificationPlugin from './plugins/NotificationPlugin.js';
import AnalyticsPlugin from './plugins/AnalyticsPlugin.js';
import { ApiService } from './services/ApiService.js';

const taskManager = new TaskManager({
    storage: 'localStorage',
    apiEndpoint: 'https://api.example.com'
});

// Load plugins
taskManager.plugins.register(new NotificationPlugin());
taskManager.plugins.register(new AnalyticsPlugin());

// Usage
const task = await taskManager.createTask({
    title: 'Learn React',
    description: 'Complete React fundamentals',
    dueDate: '2024-06-15'
});

console.log('Task created:', task.id);
```

### Solution Tips
- Use default exports for main classes
- Use named exports for utilities and constants
- Implement proper error boundaries
- Consider using Proxy for advanced features

### Bonus Challenge
- Add TypeScript definitions
- Implement hot module replacement
- Create CLI tools for the task manager
- Add internationalization support

---

## Day 5: Advanced Async Patterns Challenge

### Problem Statement
Build a sophisticated async data synchronization system that handles real-time updates, offline support, and conflict resolution.

### Requirements
1. Real-time data synchronization
2. Offline queue management
3. Conflict resolution strategies
4. Background sync with Web Workers
5. Progressive data loading
6. Connection state management

### Your Task
Create a `DataSyncManager` that handles complex async scenarios:

```javascript
class DataSyncManager {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl;
        this.storage = options.storage || localStorage;
        this.syncQueue = [];
        this.isOnline = navigator.onLine;
        this.conflictResolver = options.conflictResolver;
        
        this.setupEventListeners();
        this.startBackgroundSync();
    }
    
    // Real-time synchronization
    async sync(resourceType, resourceId) {
        // Implementation
    }
    
    // Offline queue management
    queueOperation(operation) {
        // Implementation
    }
    
    async processQueue() {
        // Implementation
    }
    
    // Conflict resolution
    async resolveConflict(localData, remoteData) {
        // Implementation
    }
    
    // Progressive loading
    async loadDataPage(resource, page, pageSize) {
        // Implementation
    }
    
    // Background sync setup
    startBackgroundSync() {
        // Implementation with Web Workers
    }
    
    // Connection monitoring
    setupEventListeners() {
        // Implementation
    }
}
```

### Scenarios to Handle
1. **User goes offline** while editing data
2. **Multiple users** editing the same resource
3. **Network intermittency** causing partial failures
4. **Large datasets** requiring pagination
5. **Background updates** while app is idle

### Example Usage
```javascript
{% raw %}
{% raw %}
const syncManager = new DataSyncManager({
    apiUrl: 'https://api.example.com',
    conflictResolver: 'lastWriteWins', // or 'manual' or custom function
    storage: window.localStorage
});

// Real-time sync
syncManager.on('data-updated', (resource, data) => {
    console.log(`${resource} updated:`, data);
});

// Handle offline operations
const user = await syncManager.update('users', userId, userData);
// Automatically queued if offline, synced when online

// Progressive loading
const tasks = await syncManager.loadDataPage('tasks', 1, 20);
// Load more as needed
{% endraw %}
{% endraw %}
```

### Solution Tips
- Use Service Workers for background sync
- Implement exponential backoff for retries
- Use timestamps for conflict resolution
- Consider using IndexedDB for complex offline storage

### Bonus Challenge
- Add real-time WebSocket integration
- Implement operational transformation for text
- Create a React hook for the sync manager
- Add performance monitoring and analytics

---

## Day 6: Testing & Debugging Challenge

### Problem Statement
Create a comprehensive testing and debugging toolkit for JavaScript applications using modern testing practices.

### Requirements
1. Unit testing utilities
2. Integration testing helpers
3. Mock and spy functions
4. Performance benchmarking
5. Error tracking and reporting
6. Debug utilities with better console output

### Your Task
Build a testing framework and debugging toolkit:

```javascript
// TestFramework.js
class TestFramework {
    constructor() {
        this.tests = [];
        this.results = {
            passed: 0,
            failed: 0,
            skipped: 0
        };
    }
    
    describe(description, testFunction) {
        // Implementation
    }
    
    it(description, testFunction) {
        // Implementation
    }
    
    expect(actual) {
        // Implementation returning assertion object
    }
    
    beforeEach(setupFunction) {
        // Implementation
    }
    
    afterEach(teardownFunction) {
        // Implementation
    }
    
    run() {
        // Implementation
    }
}

// Mock and Spy utilities
class MockFunction {
    constructor(implementation) {
        this.calls = [];
        this.implementation = implementation;
    }
    
    (...args) {
        // Track calls and execute implementation
    }
    
    toHaveBeenCalled() {
        // Assertion
    }
    
    toHaveBeenCalledWith(...args) {
        // Assertion
    }
}

// Performance benchmarking
class Benchmark {
    static measure(name, fn) {
        // Implementation
    }
    
    static compare(tests) {
        // Implementation
    }
}

// Debug utilities
class Debugger {
    static trace(obj, methods = []) {
        // Implementation using Proxy
    }
    
    static log(data, options = {}) {
        // Enhanced console logging
    }
    
    static assert(condition, message) {
        // Custom assertions
    }
}
```

### Testing Scenarios
Create tests for the previous challenges:

```javascript
// Example test suite
const framework = new TestFramework();

framework.describe('UserUtils', () => {
    let userUtils;
    
    framework.beforeEach(() => {
        userUtils = new UserUtils();
    });
    
    framework.it('should create user with valid data', () => {
        const user = userUtils.createUser('John', 'Doe', 25, 'john@example.com');
        
        framework.expect(user.name).toBe('John Doe');
        framework.expect(user.age).toBe(25);
        framework.expect(user.isAdult).toBe(true);
    });
    
    framework.it('should handle async operations', async () => {
        const mock = new MockFunction();
        const result = await userUtils.fetchUserAsync(123, mock);
        
        framework.expect(mock).toHaveBeenCalledWith(null, result);
    });
});

framework.run();
```

### Debugging Examples
```javascript
// Performance testing
Benchmark.measure('Array processing', () => {
    const arr = Array.from({length: 10000}, (_, i) => i);
    return arr.map(x => x * 2).filter(x => x % 3 === 0);
});

// Object tracing
const user = Debugger.trace({
    name: 'John',
    setName(newName) { this.name = newName; }
}, ['setName']);

// Enhanced logging
Debugger.log(complexObject, {
    depth: 3,
    colors: true,
    timestamp: true
});
```

### Solution Tips
- Use console.time() and console.timeEnd() for performance
- Implement proper error stack trace parsing
- Use Proxy for object tracing
- Consider using existing libraries as reference

### Bonus Challenge
- Add visual test reports (HTML output)
- Implement snapshot testing
- Create browser-based test runner
- Add code coverage tracking

---

## Day 7: Integration & Real-World Application

### Problem Statement
Combine all the concepts from the week into a complete, production-ready application with modern JavaScript architecture.

### Requirements
1. Modern ES6+ architecture
2. Async data management
3. Functional programming patterns
4. Modular design
5. Comprehensive testing
6. Performance optimization

### Final Project: Personal Finance Tracker

Build a personal finance tracker with these features:

```javascript
// Project structure
finance-tracker/
├── src/
│   ├── core/
│   │   ├── Application.js
│   │   ├── EventBus.js
│   │   └── StateManager.js
│   ├── models/
│   │   ├── Transaction.js
│   │   ├── Account.js
│   │   └── Category.js
│   ├── services/
│   │   ├── BankApiService.js
│   │   ├── NotificationService.js
│   │   └── ReportingService.js
│   ├── utils/
│   │   ├── currency.js
│   │   ├── dateHelpers.js
│   │   └── validators.js
│   └── plugins/
│       ├── BudgetingPlugin.js
│       └── GoalsPlugin.js
├── tests/
├── docs/
└── dist/
```

### Core Features to Implement

1. **Transaction Management**
   - Add, edit, delete transactions
   - Category assignment
   - Recurring transactions
   - Bulk import from CSV

2. **Account Management**
   - Multiple account support
   - Balance tracking
   - Account synchronization
   - Transfer between accounts

3. **Reporting & Analytics**
   - Monthly/yearly reports
   - Category breakdown
   - Trend analysis
   - Export functionality

4. **Budget Management**
   - Budget creation and tracking
   - Alerts and notifications
   - Goal setting and progress

### Implementation Requirements

```javascript
// Transaction model with validation
class Transaction {
    constructor({
        id = crypto.randomUUID(),
        amount,
        description,
        category,
        account,
        date = new Date(),
        type = 'expense'
    }) {
        this.validateAndAssign({ id, amount, description, category, account, date, type });
    }
    
    validateAndAssign(data) {
        // Implement validation using functional patterns
    }
    
    static fromCSV(csvRow) {
        // Factory method for CSV import
    }
    
    toJSON() {
        // Serialization
    }
}

// Async data service with caching
class FinanceDataService {
    constructor() {
        this.cache = new Map();
        this.syncQueue = [];
    }
    
    async getTransactions(filters = {}) {
        // Implement with caching and filtering
    }
    
    async addTransaction(transaction) {
        // Add with optimistic updates
    }
    
    async syncWithBank(accountId) {
        // External API integration
    }
    
    async generateReport(type, dateRange) {
        // Report generation with async processing
    }
}

// State management with immutable updates
class FinanceStateManager {
    constructor() {
        this.state = {
            transactions: [],
            accounts: [],
            categories: [],
            budgets: [],
            user: null
        };
        this.listeners = new Set();
    }
    
    updateState(updater) {
        // Immutable state updates
    }
    
    subscribe(listener) {
        // State change subscriptions
    }
}
```

### Advanced Features

1. **Real-time Synchronization**
   ```javascript
   class BankSyncService {
       async connectToBank(bankConfig) {
           // OAuth integration
       }
       
       startRealTimeSync() {
           // WebSocket or polling implementation
       }
       
       handleSyncConflict(localTx, remoteTx) {
           // Conflict resolution strategies
       }
   }
   ```

2. **Plugin Architecture**
   ```javascript
   class BudgetingPlugin {
       constructor(financeApp) {
           this.app = financeApp;
           this.registerHooks();
       }
       
       registerHooks() {
           this.app.on('transaction:added', this.checkBudgetLimits.bind(this));
           this.app.on('month:end', this.generateBudgetReport.bind(this));
       }
       
       async checkBudgetLimits(transaction) {
           // Budget validation logic
       }
   }
   ```

3. **Performance Optimization**
   ```javascript
   // Virtual scrolling for large transaction lists
   class VirtualTransactionList {
       constructor(container, transactions) {
           this.container = container;
           this.transactions = transactions;
           this.viewport = { start: 0, end: 50 };
           this.itemHeight = 60;
           
           this.setupVirtualScrolling();
       }
       
       render() {
           // Render only visible items
       }
       
       onScroll(event) {
           // Update viewport and re-render
       }
   }
   ```

### Testing Strategy

Write comprehensive tests covering:

```javascript
// Unit tests
describe('Transaction Model', () => {
    it('should validate amount is positive for income', () => {
        // Test implementation
    });
    
    it('should throw error for invalid category', () => {
        // Test implementation
    });
});

// Integration tests
describe('Finance Data Service', () => {
    it('should sync transactions with external API', async () => {
        // Test implementation with mocks
    });
});

// Performance tests
describe('Performance', () => {
    it('should handle 10,000 transactions efficiently', () => {
        // Benchmark test
    });
});
```

### Deployment & Optimization

1. **Build Process**
   - Module bundling
   - Code minification
   - Asset optimization
   - Source maps

2. **Performance Monitoring**
   - Bundle size analysis
   - Runtime performance tracking
   - Memory usage monitoring

3. **Error Handling**
   - Global error boundary
   - Logging and reporting
   - Graceful degradation

### Success Criteria

Your application should demonstrate:

- [ ] **Modern JavaScript**: Extensive use of ES6+ features
- [ ] **Async Mastery**: Complex async flows handled elegantly
- [ ] **Functional Programming**: Pure functions and immutable patterns
- [ ] **Modular Architecture**: Clear separation of concerns
- [ ] **Performance**: Optimized for large datasets
- [ ] **Testing**: Comprehensive test coverage
- [ ] **Documentation**: Clear API documentation
- [ ] **Error Handling**: Robust error management

### Bonus Challenges

1. **Add TypeScript**: Convert to TypeScript for better type safety
2. **PWA Features**: Add service worker for offline support
3. **Machine Learning**: Add spending prediction features
4. **Mobile App**: Create React Native version
5. **Microservices**: Split into microservice architecture

---

## 🎯 Week 1 Assessment

After completing all challenges, evaluate your progress:

### Knowledge Assessment
- [ ] Can write modern ES6+ JavaScript fluently
- [ ] Understands async patterns and can handle complex scenarios
- [ ] Applies functional programming concepts effectively
- [ ] Designs modular, maintainable architectures
- [ ] Implements comprehensive testing strategies
- [ ] Optimizes code for performance

### Practical Skills
- [ ] Builds complex applications from scratch
- [ ] Integrates multiple JavaScript concepts seamlessly
- [ ] Handles edge cases and error scenarios
- [ ] Writes clean, readable, and maintainable code
- [ ] Follows modern JavaScript best practices

### Ready for React?
If you've completed these challenges successfully, you're ready to dive deep into React development! The JavaScript skills you've mastered here will be essential for:

- Understanding React's modern syntax and patterns
- Handling async operations in React components
- Building scalable React applications
- Implementing advanced React patterns
- Optimizing React application performance

**Next Week**: [React Fundamentals Daily Challenges](./Week-02-React-Fundamentals.md)

---

## 📚 Additional Resources for Further Learning

### Advanced JavaScript
- [JavaScript: The Definitive Guide](https://www.oreilly.com/library/view/javascript-the-definitive/9781491952016/)
- [You Don't Know JS](https://github.com/getify/You-Dont-Know-JS) series
- [Functional-Light JavaScript](https://github.com/getify/Functional-Light-JS)

### Testing & Performance
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Web Performance](https://developers.google.com/web/fundamentals/performance)
- [JavaScript Performance](https://developer.mozilla.org/en-US/docs/Web/Performance)

### Modern JavaScript
- [TC39 Proposals](https://github.com/tc39/proposals) - Future JavaScript features
- [ES6 Features](https://github.com/lukehoban/es6features) - Comprehensive ES6 guide
- [MDN JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Complete reference

Keep practicing and building! The foundation you've built this week will serve you throughout your React journey. 🚀
