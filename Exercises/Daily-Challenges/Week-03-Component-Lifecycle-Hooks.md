# Week 03: Component Lifecycle & Hooks - Daily Challenges

## Overview
This week focuses on mastering React hooks, component lifecycle, and building reusable custom hooks. Each day builds upon the previous, culminating in a complex state management system.

---

## Day 15: useState and useEffect Mastery

### 🎯 Challenge: Build a Smart Counter with Side Effects
Create a counter component that demonstrates advanced useState and useEffect patterns.

#### Requirements:
1. **Counter with History**: Track all count changes with timestamps
2. **Persistence**: Save/restore count from localStorage
3. **Auto-increment**: Optional auto-increment every second when enabled
4. **Limits**: Set min/max boundaries with validation
5. **Statistics**: Show total increments, decrements, and time spent

#### Starter Code:
```jsx
function SmartCounter() {
  // Implement your solution here
  return (
    <div className="smart-counter">
      <h2>Smart Counter</h2>
      {/* Your JSX here */}
    </div>
  );
}
```

#### Expected Features:
- Current count display with boundaries
- Increment/Decrement buttons (disabled when at limits)
- Auto-increment toggle with visual indicator
- History list showing timestamp and value changes
- Statistics panel
- Reset functionality that clears history

#### Bonus Points:
- Add sound effects for actions (using Web Audio API)
- Implement undo/redo functionality
- Add keyboard shortcuts (spacebar to increment, etc.)
- Create different counter themes

---

## Day 16: useContext and Global State

### 🎯 Challenge: Multi-Theme Application
Build a theme system that manages multiple UI themes across different components.

#### Requirements:
1. **Theme Context**: Create a context for theme management
2. **Multiple Themes**: Support light, dark, and custom themes
3. **Component Theming**: Different components respond to theme changes
4. **Theme Persistence**: Save selected theme to localStorage
5. **Dynamic Theme Creation**: Allow users to create custom themes

#### Starter Code:
```jsx
// ThemeContext.js
const ThemeContext = createContext();

// App.js
function App() {
  return (
    <div className="app">
      <Header />
      <Sidebar />
      <MainContent />
      <Footer />
    </div>
  );
}
```

#### Expected Features:
- Theme provider wrapping the entire app
- Theme switcher component with live preview
- Multiple components that adapt to theme changes
- Custom theme builder with color pickers
- Export/import theme functionality

#### Bonus Points:
- Add theme transitions/animations
- Implement system theme detection (dark/light mode)
- Create theme scheduling (different themes at different times)
- Add accessibility considerations (high contrast, etc.)

---

## Day 17: useReducer and Complex State

### 🎯 Challenge: Shopping Cart with Complex Logic
Build a shopping cart system using useReducer to manage complex state interactions.

#### Requirements:
1. **Cart State**: Items, quantities, prices, discounts, taxes
2. **Product Management**: Add, remove, update quantities
3. **Discount System**: Coupons, bulk discounts, user-level discounts
4. **Inventory Tracking**: Stock levels, availability checks
5. **Order Processing**: Checkout flow with validation

#### Starter Code:
```jsx
const cartReducer = (state, action) => {
  switch (action.type) {
    // Implement your cases here
    default:
      return state;
  }
};

function ShoppingCart() {
  const [cartState, dispatch] = useReducer(cartReducer, initialState);
  
  return (
    <div className="shopping-cart">
      {/* Your implementation */}
    </div>
  );
}
```

#### Expected Features:
- Product catalog with add to cart functionality
- Cart display with item management
- Coupon code system
- Tax and shipping calculations
- Checkout form with validation
- Order confirmation

#### Bonus Points:
- Add wishlist functionality
- Implement recently viewed items
- Create cart abandonment recovery
- Add product recommendations

---

## Day 18: Custom Hooks Development

### 🎯 Challenge: Utility Hooks Library
Create a collection of reusable custom hooks for common use cases.

#### Requirements:
Build the following custom hooks:
1. **useLocalStorage**: Persistent state with localStorage
2. **useDebounce**: Debounced value updates
3. **useToggle**: Boolean state management with methods
4. **usePrevious**: Track previous values
5. **useOnlineStatus**: Network connectivity status

#### Implementation Template:
```jsx
// useLocalStorage
function useLocalStorage(key, initialValue) {
  // Implementation here
}

// useDebounce
function useDebounce(value, delay) {
  // Implementation here
}

// useToggle
function useToggle(initialValue) {
  // Implementation here
}

// usePrevious
function usePrevious(value) {
  // Implementation here
}

// useOnlineStatus
function useOnlineStatus() {
  // Implementation here
}
```

#### Test Components:
Create test components that demonstrate each hook:
- **LocalStorage Demo**: Settings form with persistence
- **Debounce Demo**: Search input with API calls
- **Toggle Demo**: Modal/sidebar controls
- **Previous Demo**: Value comparison display
- **Online Status Demo**: Network status indicator

#### Bonus Points:
- Add TypeScript definitions
- Create unit tests for each hook
- Add hook composition examples
- Build a hooks documentation site

---

## Day 19: Performance Optimization with Hooks

### 🎯 Challenge: Optimized Data Table
Build a high-performance data table with filtering, sorting, and virtual scrolling.

#### Requirements:
1. **Large Dataset**: Handle 10,000+ rows efficiently
2. **Virtual Scrolling**: Only render visible rows
3. **Advanced Filtering**: Multiple column filters
4. **Sorting**: Multi-column sorting with indicators
5. **Selection**: Row selection with bulk operations

#### Starter Code:
```jsx
function DataTable({ data, columns }) {
  // Use useMemo, useCallback, and React.memo strategically
  
  return (
    <div className="data-table">
      <TableControls />
      <VirtualizedTable />
      <TablePagination />
    </div>
  );
}

// Memoized row component
const TableRow = React.memo(function TableRow({ row, columns, isSelected, onSelect }) {
  // Implementation
});
```

#### Expected Features:
- Filter controls for each column type
- Sort indicators and multi-column sorting
- Virtual scrolling for performance
- Row selection with checkboxes
- Bulk actions (delete, export, etc.)
- Search functionality

#### Bonus Points:
- Add column resizing and reordering
- Implement row grouping
- Add export to CSV/Excel
- Create custom cell renderers

---

## Day 20: Advanced Hook Patterns

### 🎯 Challenge: Form Builder with Dynamic Validation
Create a dynamic form builder that uses advanced hook patterns for form management.

#### Requirements:
1. **Dynamic Form Structure**: Add/remove fields dynamically
2. **Validation Engine**: Complex validation rules with dependencies
3. **Field Types**: Text, number, select, checkbox, date, file upload
4. **Conditional Logic**: Show/hide fields based on other field values
5. **Form Persistence**: Save draft forms and resume later

#### Advanced Patterns to Implement:
```jsx
// Compound component pattern
function FormBuilder() {
  return (
    <Form>
      <Form.Section title="Personal Info">
        <Form.Field name="firstName" type="text" required />
        <Form.Field name="lastName" type="text" required />
      </Form.Section>
      <Form.Section title="Contact">
        <Form.Field name="email" type="email" required />
        <Form.Field name="phone" type="tel" />
      </Form.Section>
    </Form>
  );
}

// Custom form hook
function useForm(schema, options) {
  // Advanced form management logic
}

// Validation hook
function useValidation(rules) {
  // Complex validation logic
}
```

#### Expected Features:
- Drag-and-drop form builder interface
- Real-time validation with error messages
- Conditional field rendering
- Form preview mode
- Form submission with API integration
- Form analytics (completion rates, etc.)

#### Bonus Points:
- Add multi-step form wizard
- Implement form versioning
- Create form templates
- Add accessibility features (ARIA, keyboard navigation)

---

## Day 21: Integration Project - Weather Dashboard

### 🎯 Challenge: Weather Dashboard Application
Combine all the hooks concepts into a comprehensive weather dashboard application.

#### Requirements:
1. **Multiple Data Sources**: Current weather, forecast, historical data
2. **Location Management**: Search, save favorite locations
3. **Customizable Dashboard**: Drag-and-drop widgets
4. **Data Visualization**: Charts and graphs for weather trends
5. **Offline Support**: Cache data and work offline

#### Architecture:
```jsx
function WeatherDashboard() {
  // Combine multiple custom hooks
  const { user, preferences } = useAuth();
  const { locations, addLocation } = useLocations();
  const { currentWeather, forecast } = useWeatherData(locations);
  const { isOnline } = useOnlineStatus();
  const [dashboardLayout, setDashboardLayout] = useLocalStorage('dashboard-layout', defaultLayout);
  
  return (
    <DashboardProvider>
      <Dashboard layout={dashboardLayout} onLayoutChange={setDashboardLayout}>
        <WeatherWidget />
        <ForecastWidget />
        <ChartsWidget />
        <LocationsWidget />
      </Dashboard>
    </DashboardProvider>
  );
}
```

#### Expected Features:
- Location search with autocomplete
- Multiple weather widgets (current, forecast, radar, etc.)
- Customizable dashboard layout
- Weather alerts and notifications
- Historical weather charts
- Unit conversion (Celsius/Fahrenheit, mph/kph)
- Dark/light theme switching

#### Technical Requirements:
- Use all hooks learned this week
- Implement proper error boundaries
- Add loading states and error handling
- Optimize for performance
- Make responsive for mobile/desktop

#### Bonus Points:
- Add push notifications for weather alerts
- Implement PWA features (service worker, install prompt)
- Add weather-based background animations
- Create shareable weather reports
- Add voice commands for weather queries

---

## 📋 Week 3 Assessment Checklist

### Technical Skills:
- [ ] Mastered useState for complex state scenarios
- [ ] Effectively used useEffect with cleanup and dependencies
- [ ] Implemented useContext for global state management
- [ ] Built complex state logic with useReducer
- [ ] Created reusable custom hooks
- [ ] Applied performance optimization techniques
- [ ] Used advanced hook patterns (compound components, etc.)

### Best Practices:
- [ ] Proper hook dependency arrays
- [ ] Effective memoization strategies
- [ ] Clean component architecture
- [ ] Error handling and loading states
- [ ] Accessibility considerations
- [ ] Mobile-responsive design

### Problem-Solving:
- [ ] Debugged hook-related issues
- [ ] Optimized component re-renders
- [ ] Handled complex state interactions
- [ ] Implemented real-world features
- [ ] Integrated multiple APIs and data sources

---

## 🚀 Bonus Challenges

### Expert Level Extensions:
1. **Hook Testing**: Write comprehensive tests for all custom hooks
2. **Hook Library**: Publish your hooks as an npm package
3. **Performance Profiling**: Use React DevTools to profile and optimize
4. **Advanced Patterns**: Implement render props pattern with hooks
5. **State Machines**: Use XState with React hooks for complex workflows

### Real-World Applications:
- **E-commerce Cart**: Full shopping cart with complex business logic
- **Task Management**: Project management tool with drag-and-drop
- **Social Media Feed**: Infinite scroll feed with real-time updates
- **Dashboard Builder**: Generic dashboard builder for any data source
- **Game Development**: Simple game using Canvas and hooks

Each challenge should take 2-4 hours to complete. Focus on understanding the concepts deeply rather than rushing through. Document your solutions and create reusable components that you can use in future projects.
