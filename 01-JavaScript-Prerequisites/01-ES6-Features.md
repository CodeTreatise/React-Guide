# 🎯 ES6+ Features Essential for React

> **Focus**: Modern JavaScript features that form the foundation of React development  
> **Time**: 2-3 hours reading + 2-3 hours practice  
> **Difficulty**: Beginner to Intermediate

---

## 📋 Table of Contents

1. [Variable Declarations (let, const)](#1-variable-declarations)
2. [Arrow Functions](#2-arrow-functions)
3. [Template Literals](#3-template-literals)
4. [Destructuring Assignment](#4-destructuring-assignment)
5. [Spread & Rest Operators](#5-spread--rest-operators)
6. [Default Parameters](#6-default-parameters)
7. [Object Shorthand](#7-object-shorthand)
8. [Classes](#8-classes)
9. [Modules (Import/Export)](#9-modules)
10. [Array Methods](#10-enhanced-array-methods)

---

## 1. Variable Declarations

### The Evolution: var → let → const

```javascript
// ❌ Old way (var) - Problems
var name = 'John';
var name = 'Jane'; // Can redeclare (confusing)
if (true) {
    var age = 25; // Function scoped
}
console.log(age); // 25 (accessible outside block!)

// ✅ Modern way (let & const)
let userName = 'John';
const userAge = 25; // Cannot be reassigned

if (true) {
    let blockScoped = 'only here';
    const alsoBlockScoped = 'me too';
}
// console.log(blockScoped); // ❌ ReferenceError
```

### React Usage Examples

```javascript
// React component state
const [count, setCount] = useState(0); // const for useState destructuring
let isLoading = true; // let for values that change

// Props destructuring
const MyComponent = ({ title, description }) => {
    const handleClick = () => { // const for functions that don't change
        setCount(count + 1);
    };
    
    return <div onClick={handleClick}>{title}</div>;
};
```

### Key Rules
- Use `const` by default
- Use `let` when you need to reassign
- Never use `var` in modern code

---

## 2. Arrow Functions

### Syntax Evolution

```javascript
// ES5 Function Declaration
function multiply(a, b) {
    return a * b;
}

// ES5 Function Expression
var multiply = function(a, b) {
    return a * b;
};

// ES6 Arrow Function
const multiply = (a, b) => a * b;

// ES6 Arrow Function (multiple lines)
const multiply = (a, b) => {
    const result = a * b;
    return result;
};
```

### Different Arrow Function Styles

```javascript
// No parameters
const greet = () => 'Hello World!';

// One parameter (parentheses optional)
const square = x => x * x;
const square = (x) => x * x; // Both valid

// Multiple parameters
const add = (a, b) => a + b;

// Returning objects (wrap in parentheses)
const createUser = (name, age) => ({ name, age, active: true });

// Multiple lines
const processData = (data) => {
    const filtered = data.filter(item => item.active);
    const mapped = filtered.map(item => item.name);
    return mapped;
};
```

### The `this` Context Difference

```javascript
// Regular function - `this` depends on how it's called
const obj1 = {
    name: 'Regular',
    getName: function() {
        return this.name; // `this` refers to obj1
    }
};

// Arrow function - `this` is lexically bound
const obj2 = {
    name: 'Arrow',
    getName: () => {
        return this.name; // `this` refers to parent scope (not obj2!)
    }
};

console.log(obj1.getName()); // "Regular"
console.log(obj2.getName()); // undefined (or global name)
```

### React Usage Examples

```javascript
// Event handlers
const Button = () => {
    const handleClick = () => {
        console.log('Button clicked!');
    };
    
    return <button onClick={handleClick}>Click me</button>;
};

// useEffect cleanup
useEffect(() => {
    const timer = setInterval(() => {
        console.log('Timer tick');
    }, 1000);
    
    return () => clearInterval(timer); // Arrow function for cleanup
}, []);

// Array methods in JSX
const TodoList = ({ todos }) => (
    <ul>
        {todos.map(todo => (
            <li key={todo.id}>{todo.text}</li>
        ))}
    </ul>
);
```

---

## 3. Template Literals

### Basic Syntax

```javascript
// Old way (concatenation)
const name = 'John';
const age = 30;
const message = 'Hello, my name is ' + name + ' and I am ' + age + ' years old.';

// New way (template literals)
{% raw %}
const message = `Hello, my name is ${name} and I am ${age} years old.`;
{% endraw %}
```

### Advanced Features

```javascript
// Multi-line strings
{% raw %}
const html = `
    <div class="user-card">
        <h2>${user.name}</h2>
        <p>Age: ${user.age}</p>
        <p>Email: ${user.email}</p>
    </div>
`;

// Expression evaluation
const total = 100;
const tax = 0.08;
const message = `Total with tax: $${(total * (1 + tax)).toFixed(2)}`;

// Nested template literals
const users = ['John', 'Jane', 'Bob'];
const userList = `
    <ul>
        ${users.map(user => `<li>${user}</li>`).join('')}
    </ul>
`;

// Function calls in templates
const formatDate = (date) => date.toLocaleDateString();
const message = `Today is ${formatDate(new Date())}`;
{% endraw %}
```

### React Usage Examples

```javascript
// Dynamic class names
{% raw %}
const Button = ({ variant, disabled }) => (
    <button 
        className={`btn btn-${variant} ${disabled ? 'btn-disabled' : ''}`}
    >
        Click me
    </button>
);

// Dynamic styles
const Progress = ({ percentage }) => (
    <div 
        style={{{% raw %}
            width: `${percentage}%`,
            background: `hsl(${percentage * 1.2}, 70%, 50%)`{% endraw %}
        }}
    />
);

// API URLs
const fetchUser = async (userId) => {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
};
{% endraw %}
```

---

## 4. Destructuring Assignment

### Object Destructuring

```javascript
// Basic object destructuring
const user = { name: 'John', age: 30, city: 'NYC' };
const { name, age } = user;

// Renaming variables
const { name: userName, age: userAge } = user;

// Default values
const { name, age, country = 'USA' } = user;

// Nested destructuring
const user = {
    name: 'John',
    address: {
        street: '123 Main St',
        city: 'NYC',
        coordinates: { lat: 40.7, lng: -74.0 }
    }
};

const { 
    name, 
    address: { 
        city, 
        coordinates: { lat, lng } 
    } 
} = user;
```

### Array Destructuring

```javascript
// Basic array destructuring
const colors = ['red', 'green', 'blue'];
const [first, second, third] = colors;

// Skipping elements
const [first, , third] = colors; // Skip second element

// Rest elements
const [first, ...rest] = colors; // first = 'red', rest = ['green', 'blue']

// Default values
const [a, b, c = 'yellow'] = ['red', 'green']; // c = 'yellow'

// Swapping variables
let a = 1, b = 2;
[a, b] = [b, a]; // a = 2, b = 1
```

### React Usage Examples

```javascript
// Props destructuring
const UserCard = ({ name, email, avatar, isOnline = false }) => (
    <div className={`user-card ${isOnline ? 'online' : 'offline'}`}>
        <img src={avatar} alt={name} />
        <h3>{name}</h3>
        <p>{email}</p>
    </div>
);

// useState destructuring
const [count, setCount] = useState(0);
const [isLoading, setIsLoading] = useState(false);
const [user, setUser] = useState({ name: '', email: '' });

// useEffect dependencies
useEffect(() => {
    // Effect logic here
}, [count, user.name]); // Destructured values in dependency array

// Event object destructuring
const handleSubmit = (e) => {
    e.preventDefault();
    const { target: { elements } } = e;
    const { username, password } = elements;
    // Process form data
};

// API response destructuring
const fetchUserData = async () => {
    const { data: { user, posts } } = await api.getUserData();
    setUser(user);
    setPosts(posts);
};
```

---

## 5. Spread & Rest Operators

### Spread Operator (...)

```javascript
// Array spreading
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2]; // [1, 2, 3, 4, 5, 6]

// Object spreading
const obj1 = { a: 1, b: 2 };
const obj2 = { c: 3, d: 4 };
const combined = { ...obj1, ...obj2 }; // { a: 1, b: 2, c: 3, d: 4 }

// Cloning arrays and objects
const originalArray = [1, 2, 3];
const clonedArray = [...originalArray];

const originalObject = { name: 'John', age: 30 };
const clonedObject = { ...originalObject };

// Function arguments
const numbers = [1, 2, 3, 4, 5];
const max = Math.max(...numbers); // Instead of Math.max.apply(null, numbers)
```

### Rest Operator (...)

```javascript
// Rest parameters in functions
const sum = (...numbers) => {
    return numbers.reduce((total, num) => total + num, 0);
};

sum(1, 2, 3, 4, 5); // 15

// Rest in destructuring
const [first, second, ...rest] = [1, 2, 3, 4, 5];
// first = 1, second = 2, rest = [3, 4, 5]

const { name, age, ...otherProps } = { 
    name: 'John', 
    age: 30, 
    city: 'NYC', 
    country: 'USA' 
};
// name = 'John', age = 30, otherProps = { city: 'NYC', country: 'USA' }
```

### React Usage Examples

```javascript
// Immutable state updates
const [todos, setTodos] = useState([]);

const addTodo = (newTodo) => {
    setTodos([...todos, newTodo]); // Add to end
};

const updateTodo = (id, updates) => {
    setTodos(todos.map(todo => 
        todo.id === id ? { ...todo, ...updates } : todo
    ));
};

// Props spreading
const userProps = { name: 'John', age: 30, email: 'john@example.com' };

const UserProfile = () => (
    <UserCard {...userProps} isOnline={true} />
);

// Rest props pattern
const Button = ({ variant, size, ...restProps }) => (
    <button 
        className={`btn btn-${variant} btn-${size}`}
        {...restProps} // Pass through all other props
    >
        {children}
    </button>
);

// Combining arrays from different sources
const [localTodos, setLocalTodos] = useState([]);
const [remoteTodos, setRemoteTodos] = useState([]);

const allTodos = [...localTodos, ...remoteTodos];
```

---

## 6. Default Parameters

### Basic Default Parameters

```javascript
// Old way
function greet(name) {
    name = name || 'Guest';
    return 'Hello ' + name;
}

// New way
function greet(name = 'Guest') {
    return `Hello ${name}`;
}

// Arrow function with defaults
const greet = (name = 'Guest') => `Hello ${name}`;

// Multiple defaults
const createUser = (name = 'Anonymous', age = 0, role = 'user') => ({
    name, age, role, createdAt: new Date()
});
```

### Advanced Default Parameters

```javascript
// Using other parameters in defaults
const greetUser = (firstName, lastName, fullName = `${firstName} ${lastName}`) => {
    return `Hello ${fullName}`;
};

// Function calls as defaults
const getTimestamp = () => Date.now();
const createLog = (message, timestamp = getTimestamp()) => ({
    message, timestamp
});

// Object defaults
const apiCall = (url, options = {}) => {
    const config = {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        ...options
    };
    return fetch(url, config);
};
```

### React Usage Examples

```javascript
// Component props with defaults
const Button = ({ 
    children, 
    variant = 'primary', 
    size = 'medium',
    disabled = false,
    onClick = () => {}
}) => (
    <button 
        className={`btn btn-${variant} btn-${size}`}
        disabled={disabled}
        onClick={onClick}
    >
        {children}
    </button>
);

// Custom hooks with defaults
const useCounter = (initialValue = 0, step = 1) => {
    const [count, setCount] = useState(initialValue);
    
    const increment = () => setCount(count + step);
    const decrement = () => setCount(count - step);
    const reset = () => setCount(initialValue);
    
    return { count, increment, decrement, reset };
};

// API functions with defaults
const fetchUsers = async (page = 1, limit = 10, sortBy = 'name') => {
    const response = await fetch(`/api/users?page=${page}&limit=${limit}&sort=${sortBy}`);
    return response.json();
};
```

---

## 7. Object Shorthand

### Property Shorthand

```javascript
// Old way
const name = 'John';
const age = 30;
const user = {
    name: name,
    age: age
};

// New way (when variable name matches property name)
const user = { name, age };

// Mixed usage
const user = {
    name,           // Shorthand
    age,            // Shorthand
    city: 'NYC',    // Regular
    active: true    // Regular
};
```

### Method Shorthand

```javascript
// Old way
const calculator = {
    add: function(a, b) {
        return a + b;
    },
    multiply: function(a, b) {
        return a * b;
    }
};

// New way
const calculator = {
    add(a, b) {
        return a + b;
    },
    multiply(a, b) {
        return a * b;
    }
};
```

### Computed Property Names

```javascript
// Dynamic property names
const propertyName = 'dynamicKey';
const obj = {
    [propertyName]: 'dynamicValue',
    [`${propertyName}_modified`]: 'modified value'
};

// Using with functions
const createActionType = (action) => `SET_${action.toUpperCase()}`;
const actions = {
    [createActionType('user')]: 'SET_USER',
    [createActionType('loading')]: 'SET_LOADING'
};
```

### React Usage Examples

```javascript
// State object creation
const [formData, setFormData] = useState({});

const updateField = (fieldName, value) => {
    setFormData({
        ...formData,
        [fieldName]: value  // Computed property name
    });
};

// Component with shorthand
const UserCard = ({ user }) => {
    const { name, email, avatar } = user;
    
    const handleClick = () => {
        console.log('User clicked:', name);
    };
    
    // Object shorthand in return
    return {
        name,
        email,
        avatar,
        handleClick
    };
};

// Action creators (Redux style)
const createAction = (type, payload) => ({ type, payload });

// Event handlers with computed names
const FormComponent = () => {
    const [state, setState] = useState({});
    
    const handleInputChange = (fieldName) => (e) => {
        setState({
            ...state,
            [fieldName]: e.target.value
        });
    };
    
    return (
        <form>
            <input onChange={handleInputChange('username')} />
            <input onChange={handleInputChange('email')} />
            <input onChange={handleInputChange('password')} />
        </form>
    );
};
```

---

## 8. Classes

### Class Syntax

```javascript
// ES5 Constructor Function
function Person(name, age) {
    this.name = name;
    this.age = age;
}

Person.prototype.greet = function() {
    return `Hello, I'm ${this.name}`;
};

// ES6 Class
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        return `Hello, I'm ${this.name}`;
    }
    
    // Getter
    get description() {
        return `${this.name} is ${this.age} years old`;
    }
    
    // Setter
    set birthYear(year) {
        this.age = new Date().getFullYear() - year;
    }
    
    // Static method
    static createAnonymous() {
        return new Person('Anonymous', 0);
    }
}
```

### Class Inheritance

```javascript
class Student extends Person {
    constructor(name, age, grade) {
        super(name, age); // Call parent constructor
        this.grade = grade;
    }
    
    greet() {
        return `${super.greet()} and I'm in grade ${this.grade}`;
    }
    
    study() {
        return `${this.name} is studying`;
    }
}

const student = new Student('Alice', 16, 11);
console.log(student.greet()); // "Hello, I'm Alice and I'm in grade 11"
```

### React Class Components (Legacy)

```javascript
// React Class Component (older style, but still used)
class UserProfile extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: null,
            loading: true
        };
        
        // Bind methods (necessary for `this` context)
        this.handleRefresh = this.handleRefresh.bind(this);
    }
    
    componentDidMount() {
        this.fetchUser();
    }
    
    async fetchUser() {
        try {
            const user = await api.getUser(this.props.userId);
            this.setState({ user, loading: false });
        } catch (error) {
            this.setState({ error, loading: false });
        }
    }
    
    handleRefresh() {
        this.setState({ loading: true });
        this.fetchUser();
    }
    
    render() {
        const { user, loading } = this.state;
        
        if (loading) return <div>Loading...</div>;
        if (!user) return <div>User not found</div>;
        
        return (
            <div>
                <h1>{user.name}</h1>
                <p>{user.email}</p>
                <button onClick={this.handleRefresh}>
                    Refresh
                </button>
            </div>
        );
    }
}

// Modern equivalent with hooks
const UserProfile = ({ userId }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    const fetchUser = async () => {
        try {
            setLoading(true);
            const userData = await api.getUser(userId);
            setUser(userData);
        } catch (error) {
            setError(error);
        } finally {
            setLoading(false);
        }
    };
    
    useEffect(() => {
        fetchUser();
    }, [userId]);
    
    if (loading) return <div>Loading...</div>;
    if (!user) return <div>User not found</div>;
    
    return (
        <div>
            <h1>{user.name}</h1>
            <p>{user.email}</p>
            <button onClick={fetchUser}>Refresh</button>
        </div>
    );
};
```

---

## 9. Modules (Import/Export)

### Export Patterns

```javascript
// Named exports
export const PI = 3.14159;
export const E = 2.71828;

export function add(a, b) {
    return a + b;
}

export class Calculator {
    add(a, b) { return a + b; }
    subtract(a, b) { return a - b; }
}

// Export list
const multiply = (a, b) => a * b;
const divide = (a, b) => a / b;
export { multiply, divide };

// Renamed exports
export { multiply as mult, divide as div };

// Default export (one per module)
export default class MathUtils {
    static add(a, b) { return a + b; }
    static multiply(a, b) { return a * b; }
}

// Mixed exports
export const VERSION = '1.0.0';
export default MathUtils;
```

### Import Patterns

```javascript
// Named imports
import { add, multiply } from './math-utils';
import { multiply as mult } from './math-utils';

// Default import
import MathUtils from './math-utils';

// Mixed imports
import MathUtils, { VERSION, add } from './math-utils';

// Import all as namespace
import * as MathUtils from './math-utils';

// Import for side effects only
import './polyfills';

// Dynamic imports (code splitting)
const MathUtils = await import('./math-utils');
```

### React Module Patterns

```javascript
// Component exports
// Button.jsx
import React from 'react';

const Button = ({ children, onClick, variant = 'primary' }) => (
    <button 
        className={`btn btn-${variant}`}
        onClick={onClick}
    >
        {children}
    </button>
);

export default Button;

// utils.js - Multiple utilities
export const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US').format(date);
};

export const debounce = (func, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(null, args), delay);
    };
};

export const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

// hooks.js - Custom hooks
export const useLocalStorage = (key, initialValue) => {
    const [storedValue, setStoredValue] = useState(() => {
        try {
            const item = window.localStorage.getItem(key);
            return item ? JSON.parse(item) : initialValue;
        } catch (error) {
            return initialValue;
        }
    });

    const setValue = (value) => {
        try {
            setStoredValue(value);
            window.localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    };

    return [storedValue, setValue];
};

// App.jsx - Using imports
import React from 'react';
import Button from './components/Button';
import { formatDate, debounce, validateEmail } from './utils';
import { useLocalStorage } from './hooks';

const App = () => {
    const [user, setUser] = useLocalStorage('user', null);
    
    const handleSearch = debounce((query) => {
        // Search logic
    }, 300);
    
    return (
        <div>
            <h1>Welcome {user?.name}</h1>
            <p>Today is {formatDate(new Date())}</p>
            <Button onClick={() => console.log('Clicked!')}>
                Click me
            </Button>
        </div>
    );
};

export default App;
```

---

## 10. Enhanced Array Methods

### Essential Array Methods for React

```javascript
// map() - Transform array elements
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(num => num * 2); // [2, 4, 6, 8, 10]

// filter() - Select elements based on condition
const evenNumbers = numbers.filter(num => num % 2 === 0); // [2, 4]

// reduce() - Reduce array to single value
const sum = numbers.reduce((acc, num) => acc + num, 0); // 15

// find() - Find first matching element
const users = [
    { id: 1, name: 'John', active: true },
    { id: 2, name: 'Jane', active: false },
    { id: 3, name: 'Bob', active: true }
];

const activeUser = users.find(user => user.active); // { id: 1, name: 'John', active: true }

// some() - Check if any element matches
const hasActiveUser = users.some(user => user.active); // true

// every() - Check if all elements match
const allActive = users.every(user => user.active); // false

// includes() - Check if array contains value
const hasNumber = numbers.includes(3); // true
```

### Advanced Array Techniques

```javascript
// Method chaining
const processedUsers = users
    .filter(user => user.active)           // Get active users
    .map(user => ({ ...user, processed: true }))  // Add processed flag
    .sort((a, b) => a.name.localeCompare(b.name)); // Sort by name

// flatMap() - Map and flatten
const userData = [
    { name: 'John', hobbies: ['reading', 'swimming'] },
    { name: 'Jane', hobbies: ['coding', 'painting'] }
];

const allHobbies = userData.flatMap(user => user.hobbies);
// ['reading', 'swimming', 'coding', 'painting']

// Array.from() - Create arrays
const range = Array.from({ length: 5 }, (_, i) => i + 1); // [1, 2, 3, 4, 5]
const uniqueIds = Array.from(new Set([1, 2, 2, 3, 3, 4])); // [1, 2, 3, 4]
```

### React Array Method Examples

```javascript
// Rendering lists
const TodoList = ({ todos }) => (
    <ul>
        {todos.map(todo => (
            <li key={todo.id} className={todo.completed ? 'completed' : ''}>
                {todo.text}
            </li>
        ))}
    </ul>
);

// Filtering data
const UserList = ({ users, searchTerm }) => {
    const filteredUsers = users.filter(user =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    return (
        <div>
            {filteredUsers.map(user => (
                <UserCard key={user.id} user={user} />
            ))}
        </div>
    );
};

// Computing derived state
const ShoppingCart = ({ items }) => {
    const totalPrice = items.reduce((total, item) => {
        return total + (item.price * item.quantity);
    }, 0);
    
    const itemCount = items.reduce((count, item) => {
        return count + item.quantity;
    }, 0);
    
    return (
        <div>
            <h3>Cart ({itemCount} items)</h3>
            <p>Total: ${totalPrice.toFixed(2)}</p>
            {items.map(item => (
                <CartItem key={item.id} item={item} />
            ))}
        </div>
    );
};

// Complex data transformations
const UserDashboard = ({ users }) => {
    const stats = users.reduce((acc, user) => {
        acc.total++;
        if (user.active) acc.active++;
        if (user.role === 'admin') acc.admins++;
        return acc;
    }, { total: 0, active: 0, admins: 0 });
    
    const recentUsers = users
        .filter(user => {
            const daysSinceJoined = (Date.now() - user.joinedAt) / (1000 * 60 * 60 * 24);
            return daysSinceJoined <= 7;
        })
        .sort((a, b) => b.joinedAt - a.joinedAt)
        .slice(0, 5);
    
    return (
        <div>
            <div>Total Users: {stats.total}</div>
            <div>Active Users: {stats.active}</div>
            <div>Admins: {stats.admins}</div>
            
            <h3>Recent Users</h3>
            {recentUsers.map(user => (
                <UserCard key={user.id} user={user} />
            ))}
        </div>
    );
};
```

---

## 🎯 Practice Exercises

### Exercise 1: Convert ES5 to ES6+
```javascript
// Convert this ES5 code to modern ES6+
function UserManager() {
    var users = [];
    
    function addUser(name, email, role) {
        var user = {
            id: Date.now(),
            name: name,
            email: email,
            role: role || 'user',
            active: true
        };
        users.push(user);
        return user;
    }
    
    function getActiveUsers() {
        var activeUsers = [];
        for (var i = 0; i < users.length; i++) {
            if (users[i].active) {
                activeUsers.push(users[i]);
            }
        }
        return activeUsers;
    }
    
    return {
        addUser: addUser,
        getActiveUsers: getActiveUsers,
        users: users
    };
}
```

### Exercise 2: React Component with Modern JavaScript
Create a React component that:
1. Uses destructuring for props
2. Implements array methods for data processing
3. Uses template literals for dynamic content
4. Applies spread operator for state updates

---

## ✅ Knowledge Check

Test your understanding:

1. **Variable Declarations**: When should you use `const` vs `let`?
2. **Arrow Functions**: What's the difference in `this` binding?
3. **Destructuring**: How do you destructure nested objects?
4. **Spread Operator**: How do you update nested state immutably?
5. **Template Literals**: How do you create multi-line strings?
6. **Array Methods**: What's the difference between `map()` and `forEach()`?

---

## 🚀 Next Steps

You're now ready to dive into React! These ES6+ features will be used constantly in React development. Next up:

**[Module 2: React Fundamentals](../02-React-Fundamentals/README.md)**

Practice these concepts daily, and they'll become second nature as you build React applications! 🎯