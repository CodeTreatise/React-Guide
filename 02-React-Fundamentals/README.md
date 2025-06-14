# ⚛️ Module 2: React Fundamentals

> **Duration**: Week 2 (7 days)  
> **Goal**: Master core React concepts and build your first interactive components  
> **Prerequisites**: JavaScript ES6+ knowledge from Module 1

---

## 🎯 Module Overview

Welcome to React! This module covers the fundamental concepts that make React a powerful library for building user interfaces. You'll learn how React's declarative approach and component-based architecture revolutionize front-end development.

### What You'll Learn

| Concept | Description | React Advantage |
|---------|-------------|-----------------|
| **Virtual DOM** | React's representation of the real DOM | Efficient updates and rendering |
| **JSX** | JavaScript syntax extension | Declarative UI descriptions |
| **Components** | Reusable UI building blocks | Modularity and composition |
| **Props** | Data passing mechanism | Component communication |
| **State** | Component memory | Dynamic, interactive UIs |
| **Events** | User interaction handling | Declarative event management |

---

## 📚 Learning Path

### Day 1: What is React?
- Understanding the Virtual DOM
- React vs Vanilla JavaScript
- Setting up your first React app
- React Developer Tools

### Day 2: JSX - JavaScript XML
- JSX syntax and rules
- Expressions in JSX
- Conditional rendering basics
- Styling in React

### Day 3: Components Deep Dive
- Functional vs Class Components
- Component composition
- Importing and exporting components
- Component best practices

### Day 4: Props - Component Communication
- Passing props to components
- PropTypes for type checking
- Default props
- Props vs attributes

### Day 5: State and useState Hook
- Understanding component state
- useState hook basics
- State updates and re-rendering
- Multiple state variables

### Day 6: Event Handling
- React event system (SyntheticEvents)
- Event handlers and binding
- Form handling basics
- Preventing default behavior

### Day 7: Practice Project
- Build a interactive Todo application
- Combine all learned concepts
- Code review and optimization

---

## 🌟 Why React?

### The Problem React Solves

```javascript
// ❌ Vanilla JavaScript - Imperative (How to do it)
const button = document.createElement('button');
button.textContent = 'Click me';
button.addEventListener('click', function() {
    const counter = document.getElementById('counter');
    const currentValue = parseInt(counter.textContent);
    counter.textContent = currentValue + 1;
});
document.body.appendChild(button);

const counterDiv = document.createElement('div');
counterDiv.id = 'counter';
counterDiv.textContent = '0';
document.body.appendChild(counterDiv);
```

```jsx
// ✅ React - Declarative (What you want)
function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <button onClick={() => setCount(count + 1)}>
                Click me
            </button>
            <div>Count: {count}</div>
        </div>
    );
}
```

### React's Core Principles

1. **Declarative**: Describe what the UI should look like for any given state
2. **Component-Based**: Build encapsulated components that manage their own state
3. **Learn Once, Write Anywhere**: Use React for web, mobile (React Native), desktop, etc.

---

## 🔧 Getting Started

### Creating Your First React App

```bash
# Create a new React app
npx create-react-app my-react-app
cd my-react-app

# Start the development server
npm start
```

### Project Structure Overview

```
my-react-app/
├── public/
│   ├── index.html          # Main HTML file
│   └── favicon.ico         # App icon
├── src/
│   ├── index.js           # Entry point
│   ├── App.js             # Main app component
│   ├── App.css            # App styles
│   └── index.css          # Global styles
├── package.json           # Dependencies and scripts
└── README.md              # Project documentation
```

### Your First Component

```jsx
// src/App.js
import React from 'react';
import './App.css';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Welcome to React!</h1>
                <p>You're now building with React components.</p>
            </header>
        </div>
    );
}

export default App;
```

---

## 📊 The Virtual DOM Explained

### How the Virtual DOM Works

```
Real DOM Operation (Expensive):
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JavaScript    │ => │    Real DOM     │ => │   Re-render     │
│   Manipulation  │    │   Manipulation  │    │   Entire Tree   │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Virtual DOM Operation (Efficient):
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   State Change  │ => │   Virtual DOM   │ => │   Diff Process  │ => │   Minimal       │
│                 │    │   Re-creation   │    │   (Reconcile)   │    │   DOM Updates   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Virtual DOM Benefits

```jsx
// When you write this:
function UserList({ users }) {
    return (
        <ul>
            {users.map(user => (
                <li key={user.id}>{user.name}</li>
            ))}
        </ul>
    );
}

// React creates this virtual representation:
const virtualDOM = {
    type: 'ul',
    props: {
        children: [
            { type: 'li', props: { key: '1', children: 'John' } },
            { type: 'li', props: { key: '2', children: 'Jane' } },
            { type: 'li', props: { key: '3', children: 'Bob' } }
        ]
    }
};

// React efficiently updates only what changed in the real DOM
```

---

## 🎨 JSX - The React Syntax

### JSX Rules and Best Practices

```jsx
// ✅ Correct JSX
function WelcomeMessage({ name, isLoggedIn }) {
    return (
        <div className="welcome-container">
            <h1>Welcome {name}!</h1>
            {isLoggedIn && <p>You are logged in.</p>}
            <img src="/logo.png" alt="Company Logo" />
            <button onClick={() => console.log('Clicked!')}>
                Click me
            </button>
        </div>
    );
}

// ❌ Common JSX mistakes and fixes
function BadExample() {
    return (
        // ❌ Multiple root elements (use Fragment or wrapper)
        <h1>Title</h1>
        <p>Content</p>
        
        // ❌ class instead of className
        <div class="container">
        
        // ❌ Unclosed self-closing tags
        <img src="/image.png">
        
        // ❌ for instead of htmlFor
        <label for="input">
    );
}

// ✅ Fixed version
function GoodExample() {
    return (
        <React.Fragment> {/* or <> </> shorthand */}
            <h1>Title</h1>
            <p>Content</p>
            <div className="container">
                <img src="/image.png" alt="Description" />
                <label htmlFor="input">Label</label>
                <input id="input" type="text" />
            </div>
        </React.Fragment>
    );
}
```

### JSX Expressions and Dynamic Content

```jsx
function DynamicContent() {
    const user = { name: 'John', age: 30 };
    const isAdult = user.age >= 18;
    const hobbies = ['reading', 'coding', 'gaming'];
    
    return (
        <div>
            {/* String interpolation */}
            <h1>Hello, {user.name}!</h1>
            
            {/* Calculations */}
            <p>You are {user.age} years old ({2024 - user.age} birth year)</p>
            
            {/* Conditional rendering */}
            <p>Status: {isAdult ? 'Adult' : 'Minor'}</p>
            
            {/* Conditional display */}
            {isAdult && <button>Vote Now</button>}
            
            {/* Array rendering */}
            <ul>
                {hobbies.map((hobby, index) => (
                    <li key={index}>{hobby}</li>
                ))}
            </ul>
            
            {/* Object property access */}
            <div style={{
                color: isAdult ? 'green' : 'orange',
                fontSize: '16px',
                padding: '10px'
            }}>
                User Info
            </div>
        </div>
    );
}
```

---

## 🧩 Components - Building Blocks

### Functional Components (Modern Approach)

```jsx
{% raw %}
{% raw %}
// Simple functional component
function Greeting() {
    return <h1>Hello, World!</h1>;
}

// Component with props
function UserCard({ name, email, avatar, isOnline }) {
    return (
        <div className={`user-card ${isOnline ? 'online' : 'offline'}`}>
            <img src={avatar} alt={`${name}'s avatar`} />
            <div className="user-info">
                <h3>{name}</h3>
                <p>{email}</p>
                <span className="status">
                    {isOnline ? '🟢 Online' : '⚫ Offline'}
                </span>
            </div>
        </div>
    );
}

// Arrow function component
const Button = ({ children, variant = 'primary', onClick }) => (
    <button 
        className={`btn btn-${variant}`}
        onClick={onClick}
    >
        {children}
    </button>
);
{% endraw %}
{% endraw %}
```

### Component Composition

```jsx
// Base components
function Header({ title, subtitle }) {
    return (
        <header className="header">
            <h1>{title}</h1>
            {subtitle && <p>{subtitle}</p>}
        </header>
    );
}

function Footer({ copyright }) {
    return (
        <footer className="footer">
            <p>&copy; {copyright}</p>
        </footer>
    );
}

function Sidebar({ children }) {
    return (
        <aside className="sidebar">
            {children}
        </aside>
    );
}

// Composed layout component
function Layout({ title, subtitle, children }) {
    return (
        <div className="layout">
            <Header title={title} subtitle={subtitle} />
            <main className="main-content">
                <div className="content">
                    {children}
                </div>
                <Sidebar>
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="/about">About</a></li>
                        <li><a href="/contact">Contact</a></li>
                    </ul>
                </Sidebar>
            </main>
            <Footer copyright="2024 My Company" />
        </div>
    );
}

// Usage
function App() {
    return (
        <Layout title="My App" subtitle="Welcome to our platform">
            <h2>Dashboard</h2>
            <p>This is the main content area.</p>
        </Layout>
    );
}
```

---

## 📡 Props - Component Communication

### Props Fundamentals

```jsx
// Parent component passing props
function App() {
    const userData = {
        id: 1,
        name: 'Alice Johnson',
        email: 'alice@example.com',
        role: 'Developer',
        isActive: true
    };
    
    return (
        <div>
            <UserProfile 
                user={userData}
                showEmail={true}
                onEdit={(user) => console.log('Edit user:', user)}
            />
        </div>
    );
}

// Child component receiving props
function UserProfile({ user, showEmail, onEdit }) {
    return (
        <div className="user-profile">
            <h2>{user.name}</h2>
            <p>Role: {user.role}</p>
            {showEmail && <p>Email: {user.email}</p>}
            <p>Status: {user.isActive ? 'Active' : 'Inactive'}</p>
            <button onClick={() => onEdit(user)}>
                Edit Profile
            </button>
        </div>
    );
}
```

### Props Destructuring and Default Values

```jsx
{% raw %}
{% raw %}
// With destructuring and defaults
function ProductCard({ 
    title, 
    price, 
    image, 
    description = 'No description available',
    isOnSale = false,
    onAddToCart 
}) {
    return (
        <div className="product-card">
            <img src={image} alt={title} />
            <h3>{title}</h3>
            <p className="description">{description}</p>
            <div className="price">
                <span className={isOnSale ? 'sale-price' : 'regular-price'}>
                    ${price}
                </span>
                {isOnSale && <span className="sale-badge">On Sale!</span>}
            </div>
            <button onClick={() => onAddToCart({ title, price })}>
                Add to Cart
            </button>
        </div>
    );
}

// Rest props pattern
function Button({ variant = 'primary', size = 'medium', children, ...restProps }) {
    return (
        <button 
            className={`btn btn-${variant} btn-${size}`}
            {...restProps}  // Passes through all other props
        >
            {children}
        </button>
    );
}

// Usage with rest props
<Button 
    variant="secondary" 
    onClick={handleClick}
    disabled={isLoading}
    data-testid="submit-button"
>
    Submit
</Button>
{% endraw %}
{% endraw %}
```

### PropTypes for Type Checking

```jsx
import PropTypes from 'prop-types';

function UserCard({ name, age, email, hobbies, onContactUser }) {
    return (
        <div className="user-card">
            <h3>{name}</h3>
            <p>Age: {age}</p>
            <p>Email: {email}</p>
            <ul>
                {hobbies.map((hobby, index) => (
                    <li key={index}>{hobby}</li>
                ))}
            </ul>
            <button onClick={() => onContactUser(email)}>
                Contact
            </button>
        </div>
    );
}

// PropTypes definition
UserCard.propTypes = {
    name: PropTypes.string.isRequired,
    age: PropTypes.number.isRequired,
    email: PropTypes.string.isRequired,
    hobbies: PropTypes.arrayOf(PropTypes.string),
    onContactUser: PropTypes.func.isRequired
};

// Default props
UserCard.defaultProps = {
    hobbies: []
};
```

---

## 🔄 State with useState Hook

### Basic useState Usage

```jsx
import React, { useState } from 'react';

function Counter() {
    // State declaration
    const [count, setCount] = useState(0);
    
    // Event handlers
    const increment = () => setCount(count + 1);
    const decrement = () => setCount(count - 1);
    const reset = () => setCount(0);
    
    return (
        <div className="counter">
            <h2>Counter: {count}</h2>
            <div className="controls">
                <button onClick={decrement}>-</button>
                <button onClick={reset}>Reset</button>
                <button onClick={increment}>+</button>
            </div>
        </div>
    );
}
```

### Multiple State Variables

```jsx
function UserForm() {
    // Multiple state variables
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [age, setAge] = useState('');
    const [isSubscribed, setIsSubscribed] = useState(false);
    const [errors, setErrors] = useState({});
    
    // Validation function
    const validateForm = () => {
        const newErrors = {};
        
        if (!name.trim()) newErrors.name = 'Name is required';
        if (!email.trim()) newErrors.email = 'Email is required';
        else if (!/\S+@\S+\.\S+/.test(email)) newErrors.email = 'Email is invalid';
        if (!age || age < 1) newErrors.age = 'Valid age is required';
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };
    
    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (validateForm()) {
            console.log('Form submitted:', { name, email, age, isSubscribed });
            // Reset form
            setName('');
            setEmail('');
            setAge('');
            setIsSubscribed(false);
            setErrors({});
        }
    };
    
    return (
        <form onSubmit={handleSubmit} className="user-form">
            <div className="form-group">
                <label htmlFor="name">Name:</label>
                <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className={errors.name ? 'error' : ''}
                />
                {errors.name && <span className="error-message">{errors.name}</span>}
            </div>
            
            <div className="form-group">
                <label htmlFor="email">Email:</label>
                <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
            </div>
            
            <div className="form-group">
                <label htmlFor="age">Age:</label>
                <input
                    id="age"
                    type="number"
                    value={age}
                    onChange={(e) => setAge(parseInt(e.target.value) || '')}
                    className={errors.age ? 'error' : ''}
                />
                {errors.age && <span className="error-message">{errors.age}</span>}
            </div>
            
            <div className="form-group">
                <label>
                    <input
                        type="checkbox"
                        checked={isSubscribed}
                        onChange={(e) => setIsSubscribed(e.target.checked)}
                    />
                    Subscribe to newsletter
                </label>
            </div>
            
            <button type="submit">Submit</button>
        </form>
    );
}
```

### Object and Array State

```jsx
{% raw %}
{% raw %}
function TodoApp() {
    const [todos, setTodos] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [filter, setFilter] = useState('all'); // 'all', 'active', 'completed'
    
    // Add new todo
    const addTodo = () => {
        if (inputValue.trim()) {
            const newTodo = {
                id: Date.now(),
                text: inputValue.trim(),
                completed: false,
                createdAt: new Date().toISOString()
            };
            
            setTodos(prev => [...prev, newTodo]);
            setInputValue('');
        }
    };
    
    // Toggle todo completion
    const toggleTodo = (id) => {
        setTodos(prev => 
            prev.map(todo => 
                todo.id === id 
                    ? { ...todo, completed: !todo.completed }
                    : todo
            )
        );
    };
    
    // Delete todo
    const deleteTodo = (id) => {
        setTodos(prev => prev.filter(todo => todo.id !== id));
    };
    
    // Filter todos
    const filteredTodos = todos.filter(todo => {
        if (filter === 'active') return !todo.completed;
        if (filter === 'completed') return todo.completed;
        return true; // 'all'
    });
    
    return (
        <div className="todo-app">
            <h1>Todo App</h1>
            
            <div className="input-section">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addTodo()}
                    placeholder="Add a new todo..."
                />
                <button onClick={addTodo}>Add</button>
            </div>
            
            <div className="filters">
                <button 
                    className={filter === 'all' ? 'active' : ''}
                    onClick={() => setFilter('all')}
                >
                    All ({todos.length})
                </button>
                <button 
                    className={filter === 'active' ? 'active' : ''}
                    onClick={() => setFilter('active')}
                >
                    Active ({todos.filter(t => !t.completed).length})
                </button>
                <button 
                    className={filter === 'completed' ? 'active' : ''}
                    onClick={() => setFilter('completed')}
                >
                    Completed ({todos.filter(t => t.completed).length})
                </button>
            </div>
            
            <ul className="todo-list">
                {filteredTodos.map(todo => (
                    <li key={todo.id} className={todo.completed ? 'completed' : ''}>
                        <input
                            type="checkbox"
                            checked={todo.completed}
                            onChange={() => toggleTodo(todo.id)}
                        />
                        <span className="todo-text">{todo.text}</span>
                        <button 
                            onClick={() => deleteTodo(todo.id)}
                            className="delete-btn"
                        >
                            ×
                        </button>
                    </li>
                ))}
            </ul>
            
            {filteredTodos.length === 0 && (
                <p className="empty-message">
                    {filter === 'all' 
                        ? 'No todos yet. Add one above!' 
                        : `No ${filter} todos.`
                    }
                </p>
            )}
        </div>
    );
}
{% endraw %}
{% endraw %}
```

---

## 🎯 Assessment Criteria

### Knowledge Check ✅

**Conceptual Understanding:**
- [ ] Can explain what the Virtual DOM is and why it's beneficial
- [ ] Understands the difference between declarative and imperative programming
- [ ] Knows the difference between props and state
- [ ] Can explain React's component-based architecture

**Technical Skills:**
- [ ] Can write valid JSX with proper syntax
- [ ] Creates functional components with props
- [ ] Uses useState hook for component state
- [ ] Handles events in React components
- [ ] Implements conditional rendering
- [ ] Renders lists with proper keys

**Practical Application:**
- [ ] Builds interactive components with state
- [ ] Passes data between parent and child components
- [ ] Handles user input and form submission
- [ ] Follows React best practices and conventions

---

## 🚀 Practice Project: Interactive Dashboard

Build a personal dashboard that combines all the concepts you've learned:

### Project Requirements

```jsx
// Dashboard components to build:
function Dashboard() {
    return (
        <div className="dashboard">
            <Header user={currentUser} />
            <StatsCards stats={dashboardStats} />
            <TodoSection todos={todos} onTodoUpdate={handleTodoUpdate} />
            <WeatherWidget location={userLocation} />
            <QuickActions onAction={handleQuickAction} />
        </div>
    );
}

// Features to implement:
// 1. User profile display
// 2. Statistics cards with counts
// 3. Interactive todo list
// 4. Weather information (mock data)
// 5. Quick action buttons
// 6. Dark/light theme toggle
// 7. Real-time clock
```

### Bonus Challenges
- Add local storage persistence
- Implement search functionality
- Add animations and transitions
- Make it responsive for mobile

---

## 📚 Additional Resources

### Official Documentation
- [React.dev](https://react.dev) - Official React documentation
- [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools) - Browser extension

### Practice Platforms
- [React Challenges](https://react-challenges.vercel.app/) - Interactive exercises
- [Scrimba React Course](https://scrimba.com/learn/learnreact) - Interactive tutorials

### Community Resources
- [React Community](https://reactjs.org/community/support.html) - Get help
- [Awesome React](https://github.com/enaqx/awesome-react) - Curated resources

---

## 🎯 Moving Forward

Congratulations! You now understand React fundamentals. You're ready to move on to more advanced topics:

**Next Module**: [Component Lifecycle & Hooks](../03-Component-Lifecycle-Hooks/README.md)

You'll learn about:
- useEffect hook for side effects
- Component lifecycle methods
- Advanced hook patterns
- Performance optimization basics

Keep practicing these fundamentals - they're the foundation for everything else in React! 🚀