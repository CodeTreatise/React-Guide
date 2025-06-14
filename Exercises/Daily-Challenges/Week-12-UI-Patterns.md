# Week 12: UI Patterns - Daily Challenges

## Overview
This week focuses on implementing advanced UI patterns, design systems, compound components, and sophisticated user interface components. Each day explores different patterns that are essential for building modern, reusable, and accessible React applications.

---

## 📅 **Day 1 (Monday): Compound Components Pattern**

### **Challenge: Build Flexible Component APIs**
**Objective**: Master the compound components pattern for building flexible and composable UI components.

**Tasks**:
1. **Basic Compound Component**
   - Build a `Tabs` component using compound pattern
   - Create `TabList`, `Tab`, `TabPanels`, and `TabPanel` sub-components
   - Implement context for state sharing between components

2. **Advanced Composition**
   - Add support for controlled and uncontrolled modes
   - Implement keyboard navigation (Arrow keys, Home, End)
   - Add ARIA attributes for accessibility

**Code Structure**:
```jsx
// Compound Tabs Example
<Tabs defaultActiveKey="1">
  <TabList>
    <Tab key="1">Tab 1</Tab>
    <Tab key="2">Tab 2</Tab>
    <Tab key="3">Tab 3</Tab>
  </TabList>
  <TabPanels>
    <TabPanel key="1">Content 1</TabPanel>
    <TabPanel key="2">Content 2</TabPanel>
    <TabPanel key="3">Content 3</TabPanel>
  </TabPanels>
</Tabs>
```

**Implementation Pattern**:
```jsx
const TabsContext = createContext();

export const Tabs = ({ children, defaultActiveKey, onChange }) => {
  const [activeKey, setActiveKey] = useState(defaultActiveKey);
  
  const value = {
    activeKey,
    setActiveKey: (key) => {
      setActiveKey(key);
      onChange?.(key);
    }
  };
  
  return (
    <TabsContext.Provider value={value}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
};
```

**Deliverables**:
- [ ] Working Tabs compound component
- [ ] Keyboard navigation support
- [ ] Accessibility compliance (ARIA)
- [ ] Demo with 3+ tab examples

---

## 📅 **Day 2 (Tuesday): Render Props and Function as Children**

### **Challenge: Data Logic Separation**
**Objective**: Implement render props pattern for separating data logic from presentation.

**Tasks**:
1. **Data Fetcher Component**
   - Create a generic data fetching component using render props
   - Handle loading, error, and success states
   - Support different data sources (REST API, GraphQL, localStorage)

2. **Mouse Tracker Component**
   - Build a component that tracks mouse position
   - Use render props to provide position data
   - Create multiple UI representations using the same logic

3. **Toggle Component**
   - Create a reusable toggle logic component
   - Support different UI representations (switch, checkbox, button)
   - Add animation and transition support

**Render Props Examples**:
```jsx
// Data Fetcher with render props
<DataFetcher url="/api/users">
  {({ data, loading, error }) => {
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return <UserList users={data} />;
  }}
</DataFetcher>

// Mouse tracker
<MouseTracker>
  {({ x, y }) => (
    <div>
      Mouse position: {x}, {y}
      <Cursor x={x} y={y} />
    </div>
  )}
</MouseTracker>

// Toggle logic
<Toggle defaultToggled={false}>
  {({ toggled, toggle }) => (
    <button onClick={toggle}>
      {toggled ? '🌙' : '☀️'} {toggled ? 'Dark' : 'Light'} Mode
    </button>
  )}
</Toggle>
```

**Deliverables**:
- [ ] Generic DataFetcher component
- [ ] MouseTracker with visual feedback
- [ ] Toggle component with 3+ UI variations
- [ ] Performance optimization examples

---

## 📅 **Day 3 (Wednesday): Higher-Order Components (HOCs)**

### **Challenge: Component Enhancement Patterns**
**Objective**: Create reusable component enhancement logic using Higher-Order Components.

**Tasks**:
1. **Authentication HOC**
   - Create `withAuth` HOC for protecting components
   - Handle authentication state and redirects
   - Support different permission levels

2. **Loading HOC**
   - Build `withLoading` HOC for async operations
   - Add customizable loading indicators
   - Handle error boundaries and fallbacks

3. **Theme HOC**
   - Create `withTheme` HOC for theme injection
   - Support multiple theme variants
   - Handle theme switching and persistence

**HOC Implementation Patterns**:
```jsx
// Authentication HOC
const withAuth = (WrappedComponent, requiredRole = 'user') => {
  return function AuthenticatedComponent(props) {
    const { user, loading } = useAuth();
    
    if (loading) return <LoadingSpinner />;
    if (!user) return <Navigate to="/login" />;
    if (requiredRole && !user.roles.includes(requiredRole)) {
      return <UnauthorizedMessage />;
    }
    
    return <WrappedComponent {...props} user={user} />;
  };
};

// Usage
const ProtectedDashboard = withAuth(Dashboard, 'admin');

// Loading HOC
const withLoading = (WrappedComponent) => {
  return function LoadingComponent({ isLoading, ...props }) {
    if (isLoading) return <LoadingOverlay />;
    return <WrappedComponent {...props} />;
  };
};

// Theme HOC
const withTheme = (WrappedComponent) => {
  return function ThemedComponent(props) {
    const theme = useContext(ThemeContext);
    return <WrappedComponent {...props} theme={theme} />;
  };
};
```

**Deliverables**:
- [ ] Authentication HOC with role-based access
- [ ] Loading HOC with customizable indicators
- [ ] Theme HOC with switching capabilities
- [ ] Performance comparison with hooks

---

## 📅 **Day 4 (Thursday): Custom Hook Patterns**

### **Challenge: Advanced Hook Composition**
**Objective**: Create sophisticated custom hooks for complex UI patterns.

**Tasks**:
1. **useInfiniteScroll Hook**
   - Implement infinite scrolling functionality
   - Handle intersection observer and loading states
   - Support both vertical and horizontal scrolling

2. **useForm Hook**
   - Create advanced form management hook
   - Handle validation, dirty state, and submission
   - Support nested objects and array fields

3. **useModal Hook**
   - Build modal management hook
   - Handle focus management and escape key
   - Support multiple modal types and stacking

**Custom Hook Examples**:
```jsx
// Infinite scroll hook
const useInfiniteScroll = (fetchMore, hasNextPage) => {
  const [isFetching, setIsFetching] = useState(false);
  
  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop !== 
          document.documentElement.offsetHeight || isFetching) return;
      if (hasNextPage) setIsFetching(true);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isFetching, hasNextPage]);
  
  useEffect(() => {
    if (!isFetching) return;
    fetchMore().then(() => setIsFetching(false));
  }, [isFetching, fetchMore]);
  
  return [isFetching, setIsFetching];
};

// Form hook
const useForm = (initialValues, validationSchema) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  
  const setValue = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };
  
  const validate = () => {
    const newErrors = validationSchema.validate(values);
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  return {
    values,
    errors,
    touched,
    setValue,
    validate,
    isValid: Object.keys(errors).length === 0
  };
};

// Modal hook
const useModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [modalProps, setModalProps] = useState({});
  
  const openModal = (props = {}) => {
    setModalProps(props);
    setIsOpen(true);
  };
  
  const closeModal = () => {
    setIsOpen(false);
    setModalProps({});
  };
  
  return {
    isOpen,
    modalProps,
    openModal,
    closeModal
  };
};
```

**Deliverables**:
- [ ] useInfiniteScroll with demo list
- [ ] useForm with validation example
- [ ] useModal with different modal types
- [ ] Hook composition examples

---

## 📅 **Day 5 (Friday): Portal and Overlay Patterns**

### **Challenge: Advanced DOM Manipulation**
**Objective**: Master React Portals for overlays, modals, and tooltips.

**Tasks**:
1. **Modal System**
   - Create modal system using React Portals
   - Implement modal stacking and z-index management
   - Add backdrop click and escape key handling

2. **Tooltip Component**
   - Build smart tooltip system with positioning
   - Handle boundary detection and auto-positioning
   - Support different trigger events (hover, click, focus)

3. **Notification System**
   - Create global notification system
   - Support different notification types and positions
   - Implement auto-dismiss and manual close

**Portal Implementation Examples**:
```jsx
{% raw %}
// Modal Portal
const Modal = ({ isOpen, onClose, children }) => {
  const modalRoot = document.getElementById('modal-root');
  
  if (!isOpen) return null;
  
  return createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        {children}
      </div>
    </div>,
    modalRoot
  );
};

// Tooltip with positioning
const Tooltip = ({ children, content, position = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipStyle, setTooltipStyle] = useState({});
  const targetRef = useRef();
  
  const calculatePosition = () => {
    if (!targetRef.current) return;
    
    const rect = targetRef.current.getBoundingClientRect();
    const positions = {
      top: { top: rect.top - 8, left: rect.left + rect.width / 2 },
      bottom: { top: rect.bottom + 8, left: rect.left + rect.width / 2 },
      left: { top: rect.top + rect.height / 2, left: rect.left - 8 },
      right: { top: rect.top + rect.height / 2, left: rect.right + 8 }
    };
    
    setTooltipStyle(positions[position]);
  };
  
  return (
    <>
      <div
        ref={targetRef}
        onMouseEnter={() => {
          setIsVisible(true);
          calculatePosition();
        }}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {isVisible && createPortal(
        <div className={`tooltip tooltip-${position}`} style={tooltipStyle}>
          {content}
        </div>,
        document.body
      )}
    </>
  );
};
{% endraw %}
```

**Deliverables**:
- [ ] Modal system with stacking
- [ ] Smart tooltip with positioning
- [ ] Notification system with types
- [ ] Accessibility compliance check

---

## 📅 **Day 6 (Saturday): Virtualization and Performance**

### **Challenge: Large Dataset Rendering**
**Objective**: Implement virtual scrolling and performance optimization patterns.

**Tasks**:
1. **Virtual List Component**
   - Create virtual scrolling for large lists
   - Support dynamic item heights
   - Implement smooth scrolling experience

2. **Virtual Grid Component**
   - Build 2D virtualization for grids
   - Handle variable column widths and row heights
   - Add sticky headers and footers

3. **Performance Monitoring**
   - Implement performance monitoring hooks
   - Track render times and re-render counts
   - Create performance debugging tools

**Virtualization Examples**:
```jsx
{% raw %}
// Virtual List Implementation
const VirtualList = ({ items, itemHeight, containerHeight }) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );
  
  const visibleItems = items.slice(startIndex, endIndex);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;
  
  return (
    <div
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.target.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div key={startIndex + index} style={{ height: itemHeight }}>
              {item.content}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Performance monitoring hook
const useRenderCount = (componentName) => {
  const renderCount = useRef(0);
  
  useEffect(() => {
    renderCount.current += 1;
    console.log(`${componentName} rendered ${renderCount.current} times`);
  });
  
  return renderCount.current;
};

// Performance timing hook
const usePerformanceTimer = (label) => {
  useEffect(() => {
    performance.mark(`${label}-start`);
    return () => {
      performance.mark(`${label}-end`);
      performance.measure(label, `${label}-start`, `${label}-end`);
    };
  });
};
{% endraw %}
```

**Deliverables**:
- [ ] Virtual list with 10,000+ items
- [ ] Virtual grid with variable sizes
- [ ] Performance monitoring dashboard
- [ ] Optimization before/after comparison

---

## 📅 **Day 7 (Sunday): Accessibility and Inclusive Design**

### **Challenge: WCAG 2.1 Compliance Patterns**
**Objective**: Implement comprehensive accessibility patterns and inclusive design principles.

**Tasks**:
1. **Focus Management**
   - Create focus trap for modals and dialogs
   - Implement skip links and focus indicators
   - Handle programmatic focus management

2. **Screen Reader Support**
   - Add comprehensive ARIA labels and descriptions
   - Implement live regions for dynamic content
   - Create accessible data tables and forms

3. **Keyboard Navigation**
   - Implement full keyboard navigation patterns
   - Support arrow key navigation for complex widgets
   - Add keyboard shortcuts and accelerators

**Accessibility Implementation Examples**:
```jsx
// Focus trap hook
const useFocusTrap = (isActive) => {
  const trapRef = useRef();
  
  useEffect(() => {
    if (!isActive) return;
    
    const trap = trapRef.current;
    const focusableElements = trap.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;
      
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };
    
    trap.addEventListener('keydown', handleTabKey);
    firstElement.focus();
    
    return () => trap.removeEventListener('keydown', handleTabKey);
  }, [isActive]);
  
  return trapRef;
};

// Accessible button component
const AccessibleButton = ({ 
  children, 
  onClick, 
  disabled, 
  ariaLabel, 
  ariaDescribedBy,
  ...props 
}) => {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.(e);
    }
  };
  
  return (
    <button
      {...props}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-disabled={disabled}
      role="button"
      tabIndex={disabled ? -1 : 0}
    >
      {children}
    </button>
  );
};

// Live region for announcements
const LiveRegion = ({ message, politeness = 'polite' }) => {
  return (
    <div
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
};
```

**Deliverables**:
- [ ] Focus management system
- [ ] Screen reader compatible components
- [ ] Keyboard navigation demo
- [ ] WCAG 2.1 AA compliance audit

---

## 🎯 **Weekly Project: Advanced Component Library**

### **Project Overview**
Build a production-ready component library with advanced UI patterns, full accessibility support, and comprehensive documentation.

### **Requirements**:
1. **Component Patterns**
   - 5+ compound components (Tabs, Accordion, Dropdown, etc.)
   - 3+ render prop components
   - 2+ HOCs for common functionality
   - 5+ custom hooks for UI logic

2. **Accessibility Features**
   - WCAG 2.1 AA compliance across all components
   - Full keyboard navigation support
   - Screen reader compatibility
   - Focus management and skip links

3. **Performance Optimization**
   - Virtual scrolling for large datasets
   - Memoization and optimization strategies
   - Bundle size optimization
   - Performance monitoring tools

4. **Documentation and Testing**
   - Storybook with accessibility addon
   - Jest and React Testing Library tests
   - Visual regression testing
   - API documentation with examples

### **Evaluation Criteria**:
- **Pattern Implementation**: Correct use of React patterns (30%)
- **Accessibility**: Full WCAG 2.1 compliance (25%)
- **Performance**: Optimized rendering and interactions (25%)
- **Documentation**: Complete examples and API docs (20%)

---

## 📚 **Additional Resources**

### **React Patterns**
- [React Patterns Documentation](https://reactpatterns.com/)
- [Kent C. Dodds - Advanced React Patterns](https://kentcdodds.com/workshops/advanced-react-patterns)
- [React Hook Patterns](https://react-hook-patterns.vercel.app/)

### **Accessibility Resources**
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [React Accessibility Documentation](https://reactjs.org/docs/accessibility.html)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [axe-core Testing Tools](https://github.com/dequelabs/axe-core)

### **Performance Resources**
- [React Profiler API](https://reactjs.org/docs/profiler.html)
- [React Window (Virtualization)](https://react-window.vercel.app/)
- [Web Vitals](https://web.dev/vitals/)

### **Tools and Libraries**
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Storybook Accessibility Addon](https://storybook.js.org/addons/@storybook/addon-a11y)
- [React Hook Form](https://react-hook-form.com/)
- [Framer Motion](https://www.framer.com/motion/)

---

**💡 Pro Tips**:
1. **Accessibility First**: Design with accessibility in mind from the start
2. **Performance**: Measure before optimizing, profile your components
3. **Patterns**: Choose the right pattern for the use case, avoid over-engineering
4. **Testing**: Test accessibility with real assistive technology
5. **Documentation**: Include accessibility notes in all component documentation