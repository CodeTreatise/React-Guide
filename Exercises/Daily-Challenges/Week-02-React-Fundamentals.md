# Week 2: React Fundamentals - Daily Challenges

## Overview
This week focuses on building solid React fundamentals including components, JSX, props, state, and event handling. Each day introduces new concepts with progressive difficulty.

---

## Day 1: JSX and Basic Components
**Learning Focus:** Understanding JSX syntax, creating functional components, and basic rendering

### Challenge: Personal Portfolio Component
Create a personal portfolio component that showcases your information using JSX.

#### Requirements:
1. Create a `Portfolio` component that displays:
   - Your name and photo
   - A brief bio (2-3 sentences)
   - A list of your skills
   - Contact information
2. Use proper JSX syntax with:
   - JavaScript expressions in curly braces
   - Proper attribute naming (className, etc.)
   - Fragment or container elements
3. Style using inline styles or CSS classes

#### Starter Code:
```jsx
function Portfolio() {
  const name = "Your Name";
  const skills = ["JavaScript", "React", "CSS", "HTML"];
  
  return (
    // Your JSX here
  );
}

export default Portfolio;
```

#### Success Criteria:
- [ ] Component renders without errors
- [ ] Uses JSX expressions for dynamic content
- [ ] Displays all required information
- [ ] Follows proper JSX naming conventions
- [ ] Clean, readable code structure

#### Bonus Challenges:
- Add conditional rendering for different sections
- Include a dark/light theme toggle
- Add hover effects using CSS

---

## Day 2: Props and Component Composition
**Learning Focus:** Passing data between components using props and creating reusable components

### Challenge: Product Catalog
Build a product catalog with reusable card components.

#### Requirements:
1. Create a `ProductCard` component that accepts props:
   - `name` (string)
   - `price` (number)
   - `image` (string)
   - `description` (string)
   - `inStock` (boolean)
2. Create a `ProductCatalog` component that:
   - Renders multiple `ProductCard` components
   - Passes different product data to each card
3. Implement prop validation using PropTypes or TypeScript

#### Starter Code:
```jsx
const products = [
  {
    id: 1,
    name: "Laptop",
    price: 999.99,
    image: "laptop.jpg",
    description: "High-performance laptop",
    inStock: true
  },
  {
    id: 2,
    name: "Smartphone",
    price: 599.99,
    image: "phone.jpg", 
    description: "Latest smartphone model",
    inStock: false
  }
  // Add more products
];

function ProductCard(props) {
  // Your component here
}

function ProductCatalog() {
  // Your component here
}
```

#### Success Criteria:
- [ ] `ProductCard` receives and displays all props correctly
- [ ] `ProductCatalog` renders multiple product cards
- [ ] Props are passed correctly from parent to child
- [ ] Conditional rendering for stock status
- [ ] Clean component composition

#### Bonus Challenges:
- Add default props for optional fields
- Create a `Badge` component for stock status
- Implement a rating system with star components

---

## Day 3: State Management with useState
**Learning Focus:** Managing component state, handling user interactions, and state updates

### Challenge: Interactive Todo List
Create a todo list application with add, toggle, and delete functionality.

#### Requirements:
1. Create a `TodoApp` component with state for:
   - List of todos (array of objects)
   - Input field value (string)
2. Implement functionality to:
   - Add new todos
   - Toggle todo completion status
   - Delete todos
   - Clear all completed todos
3. Each todo should have: id, text, completed status

#### Starter Code:
```jsx
import { useState } from 'react';

function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');
  
  const addTodo = () => {
    // Your implementation here
  };
  
  const toggleTodo = (id) => {
    // Your implementation here
  };
  
  const deleteTodo = (id) => {
    // Your implementation here
  };
  
  return (
    // Your JSX here
  );
}

export default TodoApp;
```

#### Success Criteria:
- [ ] Can add new todos using input field
- [ ] Can toggle todo completion status
- [ ] Can delete individual todos
- [ ] State updates correctly without mutations
- [ ] Input field clears after adding todo

#### Bonus Challenges:
- Add edit functionality for existing todos
- Implement local storage persistence
- Add todo filtering (all, active, completed)
- Include todo count display

---

## Day 4: Event Handling and Forms
**Learning Focus:** Handling various events, form management, and controlled components

### Challenge: User Registration Form
Build a comprehensive user registration form with validation.

#### Requirements:
1. Create a registration form with fields:
   - Username (text)
   - Email (email)
   - Password (password)
   - Confirm Password (password)
   - Age (number)
   - Terms & Conditions (checkbox)
2. Implement form validation:
   - All fields required
   - Email format validation
   - Password minimum length (8 characters)
   - Password confirmation match
   - Age minimum (18 years)
3. Display validation errors and success message

#### Starter Code:
```jsx
import { useState } from 'react';

function RegistrationForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    age: '',
    agreeToTerms: false
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const handleChange = (e) => {
    // Your implementation here
  };
  
  const validateForm = () => {
    // Your implementation here
  };
  
  const handleSubmit = (e) => {
    // Your implementation here
  };
  
  return (
    // Your JSX here
  );
}

export default RegistrationForm;
```

#### Success Criteria:
- [ ] All form fields are controlled components
- [ ] Proper event handling for different input types
- [ ] Form validation works correctly
- [ ] Error messages display appropriately
- [ ] Form submission prevents default behavior

#### Bonus Challenges:
- Add real-time validation as user types
- Implement password strength indicator
- Add file upload for profile picture
- Include form reset functionality

---

## Day 5: Component Communication
**Learning Focus:** Parent-child communication, lifting state up, and callback props

### Challenge: Shopping Cart System
Build a shopping cart with product selection and cart management.

#### Requirements:
1. Create components:
   - `ShoppingApp` (parent)
   - `ProductList` (displays available products)
   - `Product` (individual product item)
   - `Cart` (displays cart items)
   - `CartItem` (individual cart item)
2. Implement functionality:
   - Add products to cart
   - Remove products from cart
   - Update quantity in cart
   - Calculate total price
3. State should be managed in the parent component

#### Starter Code:
```jsx
import { useState } from 'react';

const availableProducts = [
  { id: 1, name: "T-Shirt", price: 19.99 },
  { id: 2, name: "Jeans", price: 49.99 },
  { id: 3, name: "Sneakers", price: 79.99 }
];

function ShoppingApp() {
  const [cartItems, setCartItems] = useState([]);
  
  const addToCart = (product) => {
    // Your implementation here
  };
  
  const removeFromCart = (productId) => {
    // Your implementation here
  };
  
  const updateQuantity = (productId, quantity) => {
    // Your implementation here
  };
  
  return (
    // Your JSX here
  );
}

function ProductList({ products, onAddToCart }) {
  // Your implementation here
}

function Product({ product, onAddToCart }) {
  // Your implementation here
}

function Cart({ items, onRemoveFromCart, onUpdateQuantity }) {
  // Your implementation here
}

function CartItem({ item, onRemove, onUpdateQuantity }) {
  // Your implementation here
}

export default ShoppingApp;
```

#### Success Criteria:
- [ ] Products can be added to cart
- [ ] Cart items can be removed
- [ ] Quantity can be updated
- [ ] Total price calculates correctly
- [ ] Proper state lifting and prop passing

#### Bonus Challenges:
- Add product search/filter functionality
- Implement quantity limits for products
- Add cart persistence using localStorage
- Include discount codes functionality

---

## Day 6: Lists and Keys
**Learning Focus:** Rendering lists efficiently, using keys properly, and dynamic content

### Challenge: Dynamic Dashboard
Create a dashboard that displays various widgets with dynamic data.

#### Requirements:
1. Create a dashboard with widgets:
   - Weather widget (current weather)
   - News widget (news articles)
   - Stats widget (numerical statistics)
   - Activity widget (recent activities)
2. Each widget should:
   - Render lists of items with proper keys
   - Handle empty states
   - Support adding/removing items
3. Implement search/filter functionality for each widget

#### Starter Code:
```jsx
import { useState } from 'react';

const initialData = {
  weather: [
    { id: 1, city: "New York", temp: 72, condition: "Sunny" },
    { id: 2, city: "London", temp: 65, condition: "Cloudy" }
  ],
  news: [
    { id: 1, title: "React 18 Released", summary: "New features..." },
    { id: 2, title: "Web Dev Trends", summary: "Latest trends..." }
  ],
  stats: [
    { id: 1, label: "Users", value: 1250, change: "+5%" },
    { id: 2, label: "Revenue", value: 45000, change: "+12%" }
  ],
  activities: [
    { id: 1, action: "User login", timestamp: "2 mins ago" },
    { id: 2, action: "New order", timestamp: "5 mins ago" }
  ]
};

function Dashboard() {
  const [data, setData] = useState(initialData);
  const [searchTerms, setSearchTerms] = useState({});
  
  const filterItems = (items, searchTerm) => {
    // Your implementation here
  };
  
  return (
    // Your JSX here
  );
}

function Widget({ title, children }) {
  // Your implementation here
}

function WeatherWidget({ items, searchTerm, onSearch }) {
  // Your implementation here
}

// Similar components for other widgets...

export default Dashboard;
```

#### Success Criteria:
- [ ] All lists render with proper keys
- [ ] Search/filter functionality works
- [ ] Empty states are handled gracefully
- [ ] Items can be added/removed dynamically
- [ ] No console warnings about keys

#### Bonus Challenges:
- Add sorting functionality for each widget
- Implement drag-and-drop reordering
- Add data refresh functionality
- Include widget customization options

---

## Day 7: Integration Project - Weather App
**Learning Focus:** Combining all concepts learned during the week

### Challenge: Complete Weather Application
Build a full-featured weather application that demonstrates all React fundamentals.

#### Requirements:
1. **Components Structure:**
   - `WeatherApp` (main component)
   - `SearchBar` (city search)
   - `CurrentWeather` (current conditions)
   - `Forecast` (5-day forecast)
   - `WeatherCard` (reusable weather display)
   - `FavoritesList` (saved cities)

2. **Functionality:**
   - Search for weather by city name
   - Display current weather conditions
   - Show 5-day forecast
   - Save/remove favorite cities
   - Toggle between Celsius and Fahrenheit
   - Handle loading and error states

3. **State Management:**
   - Weather data
   - Search input
   - Favorite cities
   - Temperature unit preference
   - Loading and error states

#### Starter Code:
```jsx
import { useState } from 'react';

// Mock weather data (replace with API in bonus)
const mockWeatherData = {
  "New York": {
    current: { temp: 72, condition: "Sunny", humidity: 45, wind: 8 },
    forecast: [
      { day: "Mon", high: 75, low: 65, condition: "Sunny" },
      { day: "Tue", high: 73, low: 63, condition: "Cloudy" },
      // Add more days...
    ]
  },
  // Add more cities...
};

function WeatherApp() {
  const [currentCity, setCurrentCity] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [tempUnit, setTempUnit] = useState('F'); // F or C
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const searchWeather = (city) => {
    // Your implementation here
  };
  
  const addToFavorites = (city) => {
    // Your implementation here
  };
  
  const removeFromFavorites = (city) => {
    // Your implementation here
  };
  
  const toggleTempUnit = () => {
    // Your implementation here
  };
  
  return (
    // Your JSX here
  );
}

function SearchBar({ onSearch, loading }) {
  // Your implementation here
}

function CurrentWeather({ data, unit, onAddToFavorites }) {
  // Your implementation here
}

function Forecast({ data, unit }) {
  // Your implementation here
}

function WeatherCard({ data, unit, showAddButton, onAddToFavorites }) {
  // Your implementation here
}

function FavoritesList({ favorites, onRemove, onSelect }) {
  // Your implementation here
}

export default WeatherApp;
```

#### Success Criteria:
- [ ] All components work together seamlessly
- [ ] Proper state management and prop passing
- [ ] Event handling for all user interactions
- [ ] List rendering with proper keys
- [ ] Error handling and loading states
- [ ] Temperature unit conversion
- [ ] Favorites functionality works correctly

#### Bonus Challenges:
- Integrate with a real weather API (OpenWeatherMap)
- Add geolocation support for current location
- Implement data caching to avoid repeated API calls
- Add weather charts/graphs
- Include weather alerts and notifications
- Add dark/light theme toggle
- Implement local storage for favorites persistence

---

## Week Wrap-up Assessment

### Knowledge Check Questions:
1. What is JSX and how does it differ from HTML?
2. How do props flow in React applications?
3. When should you use state vs props?
4. What are controlled vs uncontrolled components?
5. Why are keys important when rendering lists?

### Practical Assessment:
Build a mini social media feed component that includes:
- Post creation form
- List of posts with likes/comments
- User profile information
- Real-time post filtering

### Code Review Checklist:
- [ ] Proper component naming and structure
- [ ] Correct use of props and state
- [ ] Event handlers implemented properly
- [ ] Lists rendered with appropriate keys
- [ ] No direct state mutations
- [ ] Clean, readable code with good practices

---

## Resources for Further Learning:
- React Official Documentation: Components and Props
- JavaScript ES6+ features review
- CSS Modules or Styled Components
- React DevTools browser extension

**Estimated Completion Time:** 7-10 hours  
**Difficulty:** Beginner to Intermediate
