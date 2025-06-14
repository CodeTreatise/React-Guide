# 🧩 Advanced Component Patterns Implementation Guide

> **Project**: Component Pattern Library & Dashboard  
> **Level**: Intermediate  
> **Estimated Time**: 6-8 hours  
> **Focus**: HOCs, Render Props, Compound Components, Custom Hooks, Advanced Patterns

---

## 🚀 Quick Start (30 minutes)

### Step 1: Setup Project
```bash
npx create-react-app advanced-patterns-app
cd advanced-patterns-app
npm install styled-components react-spring framer-motion lodash
npm start
```

### Step 2: Higher-Order Component (HOC) Pattern
```jsx
// src/hocs/withAuth.js
import React, { useEffect, useState } from 'react';

const withAuth = (WrappedComponent) => {
  return function AuthenticatedComponent(props) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState(null);

    useEffect(() => {
      // Simulate auth check
      const checkAuth = async () => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const token = localStorage.getItem('authToken');
        if (token) {
          setUser({ id: 1, name: 'John Doe', email: 'john@example.com' });
          setIsAuthenticated(true);
        }
        setIsLoading(false);
      };

      checkAuth();
    }, []);

    if (isLoading) {
      return (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
          <div>Loading...</div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <h2>Access Denied</h2>
          <p>Please log in to access this content.</p>
          <button onClick={() => {
            localStorage.setItem('authToken', 'fake-token');
            window.location.reload();
          }}>
            Login
          </button>
        </div>
      );
    }

    return <WrappedComponent {...props} user={user} />;
  };
};

export default withAuth;
```

### Step 3: Render Props Pattern
```jsx
// src/components/RenderProps/DataFetcher.jsx
import { useState, useEffect } from 'react';

const DataFetcher = ({ url, children }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data based on URL
        const mockData = {
          '/api/users': [
            { id: 1, name: 'Alice', role: 'Admin' },
            { id: 2, name: 'Bob', role: 'User' },
            { id: 3, name: 'Charlie', role: 'User' }
          ],
          '/api/posts': [
            { id: 1, title: 'React Patterns', content: 'Advanced patterns...' },
            { id: 2, title: 'Component Design', content: 'Best practices...' }
          ]
        };
        
        setData(mockData[url] || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return children({ data, loading, error });
};

export default DataFetcher;
```

### Step 4: Compound Components Pattern
```jsx
{% raw %}
{% raw %}
// src/components/Compound/Accordion.jsx
import React, { createContext, useContext, useState } from 'react';
import './Accordion.css';

const AccordionContext = createContext();

const Accordion = ({ children, allowMultiple = false }) => {
  const [openItems, setOpenItems] = useState(new Set());

  const toggleItem = (id) => {
    setOpenItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        if (!allowMultiple) {
          newSet.clear();
        }
        newSet.add(id);
      }
      return newSet;
    });
  };

  const isOpen = (id) => openItems.has(id);

  return (
    <AccordionContext.Provider value={{ toggleItem, isOpen }}>
      <div className="accordion">
        {children}
      </div>
    </AccordionContext.Provider>
  );
};

const AccordionItem = ({ children, id }) => {
  return (
    <div className="accordion-item">
      {React.Children.map(children, child =>
        React.cloneElement(child, { id })
      )}
    </div>
  );
};

const AccordionHeader = ({ children, id }) => {
  const { toggleItem, isOpen } = useContext(AccordionContext);
  
  return (
    <button
      className={`accordion-header ${isOpen(id) ? 'open' : ''}`}
      onClick={() => toggleItem(id)}
    >
      {children}
      <span className="accordion-icon">
        {isOpen(id) ? '▼' : '▶'}
      </span>
    </button>
  );
};

const AccordionContent = ({ children, id }) => {
  const { isOpen } = useContext(AccordionContext);
  
  return (
    <div className={`accordion-content ${isOpen(id) ? 'open' : ''}`}>
      <div className="accordion-content-inner">
        {children}
      </div>
    </div>
  );
};

Accordion.Item = AccordionItem;
Accordion.Header = AccordionHeader;
Accordion.Content = AccordionContent;

export default Accordion;
{% endraw %}
{% endraw %}
```

---

## 📚 Complete Implementation

### 1. Advanced HOC Patterns

#### Multiple HOCs Composition
```jsx
// src/hocs/withLoading.js
import React from 'react';

const withLoading = (WrappedComponent) => {
  return function LoadingComponent({ isLoading, loadingComponent, ...props }) {
    if (isLoading) {
      return loadingComponent || (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      );
    }
    
    return <WrappedComponent {...props} />;
  };
};

export default withLoading;
```

```jsx
// src/hocs/withErrorBoundary.js
import React, { Component } from 'react';

const withErrorBoundary = (WrappedComponent) => {
  return class extends Component {
    constructor(props) {
      super(props);
      this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
      return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
      console.error('Error caught by HOC:', error, errorInfo);
    }

    render() {
      if (this.state.hasError) {
        return (
          <div className="error-boundary">
            <h2>Something went wrong</h2>
            <details>
              <summary>Error details</summary>
              <pre>{this.state.error?.toString()}</pre>
            </details>
            <button onClick={() => this.setState({ hasError: false, error: null })}>
              Try again
            </button>
          </div>
        );
      }

      return <WrappedComponent {...this.props} />;
    }
  };
};

export default withErrorBoundary;
```

```jsx
{% raw %}
{% raw %}
// src/hocs/withTracking.js
import React, { useEffect } from 'react';

const withTracking = (eventName) => (WrappedComponent) => {
  return function TrackedComponent(props) {
    useEffect(() => {
      // Simulate analytics tracking
      console.log(`Component mounted: ${eventName}`, {
        timestamp: new Date().toISOString(),
        props: Object.keys(props)
      });

      return () => {
        console.log(`Component unmounted: ${eventName}`);
      };
    }, []);

    return <WrappedComponent {...props} />;
  };
};

export default withTracking;
{% endraw %}
{% endraw %}
```

```jsx
// src/hocs/compose.js
const compose = (...hocs) => (WrappedComponent) => {
  return hocs.reduceRight((acc, hoc) => hoc(acc), WrappedComponent);
};

export default compose;

// Usage example
// export default compose(
//   withAuth,
//   withLoading,
//   withErrorBoundary,
//   withTracking('UserDashboard')
// )(UserDashboard);
```

### 2. Advanced Render Props Patterns

#### Mouse Tracker Component
```jsx
// src/components/RenderProps/MouseTracker.jsx
import { useState, useEffect } from 'react';

const MouseTracker = ({ children, throttle = 16 }) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isTracking, setIsTracking] = useState(false);

  useEffect(() => {
    let timeoutId;
    
    const handleMouseMove = (e) => {
      if (timeoutId) return;
      
      timeoutId = setTimeout(() => {
        setMousePosition({ x: e.clientX, y: e.clientY });
        timeoutId = null;
      }, throttle);
    };

    const handleMouseEnter = () => setIsTracking(true);
    const handleMouseLeave = () => setIsTracking(false);

    if (isTracking) {
      window.addEventListener('mousemove', handleMouseMove);
    }

    document.addEventListener('mouseenter', handleMouseEnter);
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseenter', handleMouseEnter);
      document.removeEventListener('mouseleave', handleMouseLeave);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [isTracking, throttle]);

  return children({ mousePosition, isTracking });
};

export default MouseTracker;
```

#### Form State Manager
```jsx
// src/components/RenderProps/FormStateManager.jsx
import { useState, useCallback } from 'react';

const FormStateManager = ({ initialValues = {}, validationRules = {}, children }) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = useCallback((fieldName, value) => {
    const rules = validationRules[fieldName];
    if (!rules) return '';

    for (const rule of rules) {
      const error = rule(value, values);
      if (error) return error;
    }
    return '';
  }, [validationRules, values]);

  const handleChange = useCallback((fieldName) => (e) => {
    const value = e.target.value;
    setValues(prev => ({ ...prev, [fieldName]: value }));
    
    if (touched[fieldName]) {
      const error = validate(fieldName, value);
      setErrors(prev => ({ ...prev, [fieldName]: error }));
    }
  }, [touched, validate]);

  const handleBlur = useCallback((fieldName) => () => {
    setTouched(prev => ({ ...prev, [fieldName]: true }));
    const error = validate(fieldName, values[fieldName]);
    setErrors(prev => ({ ...prev, [fieldName]: error }));
  }, [validate, values]);

  const handleSubmit = useCallback((onSubmit) => async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Validate all fields
    const newErrors = {};
    let hasErrors = false;

    Object.keys(validationRules).forEach(fieldName => {
      const error = validate(fieldName, values[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
        hasErrors = true;
      }
    });

    setErrors(newErrors);
    setTouched(Object.keys(validationRules).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {}));

    if (!hasErrors) {
      try {
        await onSubmit(values);
      } catch (error) {
        console.error('Form submission error:', error);
      }
    }

    setIsSubmitting(false);
  }, [validate, values, validationRules]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  return children({
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    reset
  });
};

export default FormStateManager;
```

### 3. Advanced Compound Components

#### Modal Component System
```jsx
// src/components/Compound/Modal.jsx
import React, { createContext, useContext, useEffect } from 'react';
import { createPortal } from 'react-dom';
import './Modal.css';

const ModalContext = createContext();

const Modal = ({ children, isOpen, onClose, closeOnOverlay = true }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (closeOnOverlay && e.target === e.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <ModalContext.Provider value={{ onClose }}>
      <div className="modal-overlay" onClick={handleOverlayClick}>
        <div className="modal-container">
          {children}
        </div>
      </div>
    </ModalContext.Provider>,
    document.getElementById('modal-root') || document.body
  );
};

const ModalHeader = ({ children, showCloseButton = true }) => {
  const { onClose } = useContext(ModalContext);
  
  return (
    <div className="modal-header">
      <div className="modal-title">{children}</div>
      {showCloseButton && (
        <button className="modal-close-button" onClick={onClose}>
          ✕
        </button>
      )}
    </div>
  );
};

const ModalBody = ({ children }) => (
  <div className="modal-body">
    {children}
  </div>
);

const ModalFooter = ({ children }) => (
  <div className="modal-footer">
    {children}
  </div>
);

Modal.Header = ModalHeader;
Modal.Body = ModalBody;
Modal.Footer = ModalFooter;

export default Modal;
```

#### Tab System Component
```jsx
{% raw %}
{% raw %}
// src/components/Compound/Tabs.jsx
import React, { createContext, useContext, useState } from 'react';
import './Tabs.css';

const TabsContext = createContext();

const Tabs = ({ children, defaultTab, onChange }) => {
  const [activeTab, setActiveTab] = useState(defaultTab);

  const selectTab = (tabId) => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  return (
    <TabsContext.Provider value={{ activeTab, selectTab }}>
      <div className="tabs-container">
        {children}
      </div>
    </TabsContext.Provider>
  );
};

const TabList = ({ children }) => (
  <div className="tab-list" role="tablist">
    {children}
  </div>
);

const Tab = ({ children, tabId, disabled = false }) => {
  const { activeTab, selectTab } = useContext(TabsContext);
  const isActive = activeTab === tabId;

  return (
    <button
      className={`tab ${isActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={() => !disabled && selectTab(tabId)}
      role="tab"
      aria-selected={isActive}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

const TabPanels = ({ children }) => (
  <div className="tab-panels">
    {children}
  </div>
);

const TabPanel = ({ children, tabId }) => {
  const { activeTab } = useContext(TabsContext);
  const isActive = activeTab === tabId;

  return (
    <div
      className={`tab-panel ${isActive ? 'active' : ''}`}
      role="tabpanel"
      hidden={!isActive}
    >
      {children}
    </div>
  );
};

Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panels = TabPanels;
Tabs.Panel = TabPanel;

export default Tabs;
{% endraw %}
{% endraw %}
```

### 4. Custom Hook Patterns

#### Advanced State Management Hooks
```jsx
// src/hooks/useAdvancedState.js
import { useState, useCallback, useRef } from 'react';

export const useAdvancedState = (initialState) => {
  const [state, setState] = useState(initialState);
  const stateRef = useRef(state);
  
  // Keep ref in sync
  stateRef.current = state;

  const setStateWithCallback = useCallback((newState, callback) => {
    setState(prev => {
      const nextState = typeof newState === 'function' ? newState(prev) : newState;
      stateRef.current = nextState;
      
      if (callback) {
        // Execute callback after state update
        setTimeout(() => callback(nextState), 0);
      }
      
      return nextState;
    });
  }, []);

  const getCurrentState = useCallback(() => stateRef.current, []);

  const resetState = useCallback(() => {
    setState(initialState);
  }, [initialState]);

  return [state, setStateWithCallback, getCurrentState, resetState];
};
```

```jsx
// src/hooks/useUndo.js
import { useState, useCallback } from 'react';

export const useUndo = (initialState, maxHistorySize = 10) => {
  const [history, setHistory] = useState([initialState]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const currentState = history[currentIndex];

  const setState = useCallback((newState) => {
    setHistory(prev => {
      const newHistory = prev.slice(0, currentIndex + 1);
      newHistory.push(typeof newState === 'function' ? newState(currentState) : newState);
      
      // Limit history size
      if (newHistory.length > maxHistorySize) {
        newHistory.shift();
        setCurrentIndex(prev => prev);
      } else {
        setCurrentIndex(newHistory.length - 1);
      }
      
      return newHistory;
    });
  }, [currentIndex, currentState, maxHistorySize]);

  const undo = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [currentIndex]);

  const redo = useCallback(() => {
    if (currentIndex < history.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  }, [currentIndex, history.length]);

  const canUndo = currentIndex > 0;
  const canRedo = currentIndex < history.length - 1;

  const reset = useCallback(() => {
    setHistory([initialState]);
    setCurrentIndex(0);
  }, [initialState]);

  return {
    state: currentState,
    setState,
    undo,
    redo,
    canUndo,
    canRedo,
    reset,
    history: history.slice(0, currentIndex + 1)
  };
};
```

```jsx
// src/hooks/useAsyncOperation.js
import { useState, useCallback, useRef, useEffect } from 'react';

export const useAsyncOperation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const cancelRef = useRef(false);

  useEffect(() => {
    return () => {
      cancelRef.current = true;
    };
  }, []);

  const execute = useCallback(async (asyncFunction, ...args) => {
    try {
      setLoading(true);
      setError(null);
      cancelRef.current = false;

      const result = await asyncFunction(...args);
      
      if (!cancelRef.current) {
        setData(result);
      }
      
      return result;
    } catch (err) {
      if (!cancelRef.current) {
        setError(err);
      }
      throw err;
    } finally {
      if (!cancelRef.current) {
        setLoading(false);
      }
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);

  return { loading, error, data, execute, reset };
};
```

### 5. Provider Pattern with Context
```jsx
// src/contexts/ComponentPatternsContext.jsx
import React, { createContext, useContext, useReducer } from 'react';

const ComponentPatternsContext = createContext();

const initialState = {
  examples: [],
  favorites: [],
  filters: {
    category: 'all',
    difficulty: 'all'
  },
  settings: {
    showCode: true,
    theme: 'light'
  }
};

function patternsReducer(state, action) {
  switch (action.type) {
    case 'SET_EXAMPLES':
      return { ...state, examples: action.payload };
    
    case 'ADD_TO_FAVORITES':
      return {
        ...state,
        favorites: [...state.favorites, action.payload]
      };
    
    case 'REMOVE_FROM_FAVORITES':
      return {
        ...state,
        favorites: state.favorites.filter(id => id !== action.payload)
      };
    
    case 'UPDATE_FILTERS':
      return {
        ...state,
        filters: { ...state.filters, ...action.payload }
      };
    
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      };
    
    default:
      return state;
  }
}

export const ComponentPatternsProvider = ({ children }) => {
  const [state, dispatch] = useReducer(patternsReducer, initialState);

  const addToFavorites = (id) => {
    dispatch({ type: 'ADD_TO_FAVORITES', payload: id });
  };

  const removeFromFavorites = (id) => {
    dispatch({ type: 'REMOVE_FROM_FAVORITES', payload: id });
  };

  const updateFilters = (filters) => {
    dispatch({ type: 'UPDATE_FILTERS', payload: filters });
  };

  const updateSettings = (settings) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
  };

  return (
    <ComponentPatternsContext.Provider value={{
      ...state,
      addToFavorites,
      removeFromFavorites,
      updateFilters,
      updateSettings
    }}>
      {children}
    </ComponentPatternsContext.Provider>
  );
};

export const useComponentPatterns = () => {
  const context = useContext(ComponentPatternsContext);
  if (!context) {
    throw new Error('useComponentPatterns must be used within ComponentPatternsProvider');
  }
  return context;
};
```

### 6. Main Application Components

#### Pattern Examples Dashboard
```jsx
{% raw %}
{% raw %}
// src/components/PatternsDashboard.jsx
import React, { useState } from 'react';
import withAuth from '../hocs/withAuth';
import withLoading from '../hocs/withLoading';
import withErrorBoundary from '../hocs/withErrorBoundary';
import compose from '../hocs/compose';
import Tabs from './Compound/Tabs';
import Modal from './Compound/Modal';
import Accordion from './Compound/Accordion';
import DataFetcher from './RenderProps/DataFetcher';
import MouseTracker from './RenderProps/MouseTracker';
import FormStateManager from './RenderProps/FormStateManager';
import { useUndo } from '../hooks/useUndo';
import { useAsyncOperation } from '../hooks/useAsyncOperation';
import './PatternsDashboard.css';

const PatternsDashboard = ({ user }) => {
  const [activePattern, setActivePattern] = useState('hoc');
  const [showModal, setShowModal] = useState(false);
  const { state: counterState, setState: setCounter, undo, redo, canUndo, canRedo } = useUndo(0);
  const { loading, error, execute } = useAsyncOperation();

  const validationRules = {
    email: [
      (value) => !value ? 'Email is required' : '',
      (value) => !/\S+@\S+\.\S+/.test(value) ? 'Email is invalid' : ''
    ],
    password: [
      (value) => !value ? 'Password is required' : '',
      (value) => value.length < 6 ? 'Password must be at least 6 characters' : ''
    ]
  };

  const handleAsyncAction = async () => {
    await execute(async () => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      return 'Async operation completed!';
    });
  };

  return (
    <div className="patterns-dashboard">
      <header className="dashboard-header">
        <h1>🧩 Advanced Component Patterns</h1>
        <p>Welcome, {user.name}! Explore advanced React patterns.</p>
      </header>

      <Tabs defaultTab="hoc" onChange={setActivePattern}>
        <Tabs.List>
          <Tabs.Tab tabId="hoc">Higher-Order Components</Tabs.Tab>
          <Tabs.Tab tabId="renderProps">Render Props</Tabs.Tab>
          <Tabs.Tab tabId="compound">Compound Components</Tabs.Tab>
          <Tabs.Tab tabId="hooks">Custom Hooks</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panels>
          <Tabs.Panel tabId="hoc">
            <div className="pattern-section">
              <h2>Higher-Order Components (HOCs)</h2>
              <p>This component is wrapped with multiple HOCs: withAuth, withLoading, and withErrorBoundary.</p>
              
              <div className="hoc-example">
                <h3>Authentication Status</h3>
                <div className="user-card">
                  <img src={user.avatar || `https://ui-avatars.com/api/?name=${user.name}`} alt={user.name} />
                  <div>
                    <strong>{user.name}</strong>
                    <p>{user.email}</p>
                  </div>
                </div>
              </div>

              <div className="async-example">
                <h3>Async Operation with HOC</h3>
                <button onClick={handleAsyncAction} disabled={loading}>
                  {loading ? 'Loading...' : 'Start Async Operation'}
                </button>
                {error && <p className="error">Error: {error.message}</p>}
              </div>
            </div>
          </Tabs.Panel>

          <Tabs.Panel tabId="renderProps">
            <div className="pattern-section">
              <h2>Render Props Pattern</h2>
              
              <div className="render-props-example">
                <h3>Data Fetcher</h3>
                <DataFetcher url="/api/users">
                  {({ data, loading, error }) => (
                    <div>
                      {loading && <p>Loading users...</p>}
                      {error && <p className="error">Error: {error}</p>}
                      {data && (
                        <ul className="user-list">
                          {data.map(user => (
                            <li key={user.id}>{user.name} - {user.role}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </DataFetcher>
              </div>

              <div className="mouse-tracker-example">
                <h3>Mouse Tracker</h3>
                <MouseTracker>
                  {({ mousePosition, isTracking }) => (
                    <div className="mouse-display">
                      <p>Mouse Position: {mousePosition.x}, {mousePosition.y}</p>
                      <p>Tracking: {isTracking ? 'Yes' : 'No'}</p>
                      <div 
                        className="mouse-follower"
                        style={{
                          left: mousePosition.x - 10,
                          top: mousePosition.y - 10,
                          opacity: isTracking ? 1 : 0
                        }}
                      />
                    </div>
                  )}
                </MouseTracker>
              </div>

              <div className="form-example">
                <h3>Form State Manager</h3>
                <FormStateManager
                  initialValues={{ email: '', password: '' }}
                  validationRules={validationRules}
                >
                  {({ values, errors, handleChange, handleBlur, handleSubmit, isSubmitting }) => (
                    <form onSubmit={handleSubmit(async (data) => {
                      console.log('Form submitted:', data);
                      await new Promise(resolve => setTimeout(resolve, 1000));
                    })}>
                      <div className="form-group">
                        <input
                          type="email"
                          placeholder="Email"
                          value={values.email || ''}
                          onChange={handleChange('email')}
                          onBlur={handleBlur('email')}
                        />
                        {errors.email && <span className="error">{errors.email}</span>}
                      </div>
                      
                      <div className="form-group">
                        <input
                          type="password"
                          placeholder="Password"
                          value={values.password || ''}
                          onChange={handleChange('password')}
                          onBlur={handleBlur('password')}
                        />
                        {errors.password && <span className="error">{errors.password}</span>}
                      </div>
                      
                      <button type="submit" disabled={isSubmitting}>
                        {isSubmitting ? 'Submitting...' : 'Submit'}
                      </button>
                    </form>
                  )}
                </FormStateManager>
              </div>
            </div>
          </Tabs.Panel>

          <Tabs.Panel tabId="compound">
            <div className="pattern-section">
              <h2>Compound Components</h2>
              
              <div className="compound-example">
                <h3>Modal System</h3>
                <button onClick={() => setShowModal(true)}>Open Modal</button>
                
                <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
                  <Modal.Header>
                    Example Modal
                  </Modal.Header>
                  <Modal.Body>
                    <p>This is a compound component modal. It demonstrates how multiple components work together to create a cohesive interface.</p>
                    <p>You can press Escape or click the overlay to close it.</p>
                  </Modal.Body>
                  <Modal.Footer>
                    <button onClick={() => setShowModal(false)}>Close</button>
                    <button className="primary">Save</button>
                  </Modal.Footer>
                </Modal>
              </div>

              <div className="accordion-example">
                <h3>Accordion System</h3>
                <Accordion allowMultiple={true}>
                  <Accordion.Item id="item1">
                    <Accordion.Header>What are Compound Components?</Accordion.Header>
                    <Accordion.Content>
                      Compound components are a pattern where multiple components work together to form a complete UI. They share state through React Context and provide a flexible, composable API.
                    </Accordion.Content>
                  </Accordion.Item>
                  
                  <Accordion.Item id="item2">
                    <Accordion.Header>Benefits of This Pattern</Accordion.Header>
                    <Accordion.Content>
                      <ul>
                        <li>Flexible and composable API</li>
                        <li>Clear separation of concerns</li>
                        <li>Easy to understand and maintain</li>
                        <li>Customizable styling and behavior</li>
                      </ul>
                    </Accordion.Content>
                  </Accordion.Item>
                  
                  <Accordion.Item id="item3">
                    <Accordion.Header>Real-world Examples</Accordion.Header>
                    <Accordion.Content>
                      Many popular UI libraries use compound components: React Router's Route components, Reach UI's disclosure components, and many others.
                    </Accordion.Content>
                  </Accordion.Item>
                </Accordion>
              </div>
            </div>
          </Tabs.Panel>

          <Tabs.Panel tabId="hooks">
            <div className="pattern-section">
              <h2>Custom Hooks</h2>
              
              <div className="hooks-example">
                <h3>Undo/Redo Hook</h3>
                <div className="counter-example">
                  <p>Counter: {counterState}</p>
                  <div className="counter-controls">
                    <button onClick={() => setCounter(prev => prev - 1)}>-</button>
                    <button onClick={() => setCounter(prev => prev + 1)}>+</button>
                    <button onClick={undo} disabled={!canUndo}>Undo</button>
                    <button onClick={redo} disabled={!canRedo}>Redo</button>
                  </div>
                </div>
              </div>
            </div>
          </Tabs.Panel>
        </Tabs.Panels>
      </Tabs>
    </div>
  );
};

// Apply multiple HOCs using composition
export default compose(
  withAuth,
  withLoading,
  withErrorBoundary
)(PatternsDashboard);
{% endraw %}
{% endraw %}
```

### 7. Styling

#### Main Dashboard Styles
```css
/* src/components/PatternsDashboard.css */
.patterns-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.dashboard-header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
}

.pattern-section {
  padding: 20px 0;
}

.pattern-section h2 {
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.pattern-section h3 {
  color: #555;
  margin: 25px 0 15px 0;
}

/* HOC Examples */
.hoc-example, .async-example {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 15px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-card img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

/* Render Props Examples */
.render-props-example {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.user-list {
  list-style: none;
  padding: 0;
}

.user-list li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.mouse-display {
  position: relative;
  background: #f0f0f0;
  padding: 20px;
  border-radius: 8px;
  min-height: 200px;
  overflow: hidden;
}

.mouse-follower {
  position: fixed;
  width: 20px;
  height: 20px;
  background: #007bff;
  border-radius: 50%;
  pointer-events: none;
  transition: opacity 0.2s ease;
  z-index: 1000;
}

.form-example form {
  max-width: 300px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
}

.form-group .error {
  color: #dc3545;
  font-size: 12px;
  margin-top: 5px;
  display: block;
}

/* Compound Components Examples */
.compound-example {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.accordion-example {
  margin: 20px 0;
}

/* Custom Hooks Examples */
.hooks-example {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.counter-example {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.counter-example p {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 20px;
}

.counter-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.counter-controls button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.counter-controls button:not(:disabled):hover {
  transform: translateY(-1px);
}

.counter-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* General button styles */
button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

button.primary {
  background: #28a745;
}

button.primary:hover {
  background: #1e7e34;
}

.error {
  color: #dc3545;
  font-weight: 500;
}

/* Loading and error states */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  flex-direction: column;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-boundary {
  padding: 2rem;
  text-align: center;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  color: #721c24;
}

.error-boundary details {
  margin: 1rem 0;
  text-align: left;
}

.error-boundary pre {
  background: #fff;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

/* Responsive design */
@media (max-width: 768px) {
  .patterns-dashboard {
    padding: 10px;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .counter-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .counter-controls button {
    width: 120px;
  }
}
```

#### Tabs Component Styles
```css
/* src/components/Compound/Tabs.css */
.tabs-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
}

.tab-list {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  overflow-x: auto;
}

.tab {
  background: none;
  border: none;
  padding: 15px 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: 150px;
}

.tab:hover:not(.disabled) {
  background: #e9ecef;
  color: #495057;
}

.tab.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background: white;
}

.tab.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tab-panels {
  background: white;
}

.tab-panel {
  padding: 25px;
  min-height: 300px;
}

.tab-panel:not(.active) {
  display: none;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .tab-list {
    flex-direction: column;
  }
  
  .tab {
    min-width: auto;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
    border-right: 3px solid transparent;
  }
  
  .tab.active {
    border-bottom-color: #dee2e6;
    border-right-color: #007bff;
  }
  
  .tab-panel {
    padding: 20px;
  }
}
```

#### Modal Component Styles
```css
/* src/components/Compound/Modal.css */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: scale(0.8) translateY(-50px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 25px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
}

.modal-close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close-button:hover {
  background: #e9ecef;
  color: #495057;
}

.modal-body {
  padding: 25px;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px 25px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .modal-container {
    max-width: 95vw;
    margin: 20px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 15px 20px;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-footer button {
    width: 100%;
  }
}
```

#### Accordion Component Styles
```css
/* src/components/Compound/Accordion.css */
.accordion {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.accordion-item {
  border-bottom: 1px solid #dee2e6;
}

.accordion-item:last-child {
  border-bottom: none;
}

.accordion-header {
  width: 100%;
  background: #f8f9fa;
  border: none;
  padding: 15px 20px;
  text-align: left;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s ease;
}

.accordion-header:hover {
  background: #e9ecef;
}

.accordion-header.open {
  background: #007bff;
  color: white;
}

.accordion-icon {
  transition: transform 0.2s ease;
  font-size: 12px;
}

.accordion-header.open .accordion-icon {
  transform: rotate(90deg);
}

.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
  background: white;
}

.accordion-content.open {
  max-height: 500px; /* Adjust based on content */
}

.accordion-content-inner {
  padding: 20px;
  color: #666;
  line-height: 1.6;
}

.accordion-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.accordion-content li {
  margin: 5px 0;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .accordion-header {
    padding: 12px 15px;
    font-size: 14px;
  }
  
  .accordion-content-inner {
    padding: 15px;
  }
}
```

---

## 🧪 Testing the Implementation

### Test Checklist
- [ ] **HOC Composition**: Multiple HOCs work together correctly
- [ ] **Authentication HOC**: Protects components and shows login when needed
- [ ] **Loading HOC**: Shows loading states appropriately
- [ ] **Error Boundary HOC**: Catches and displays errors gracefully
- [ ] **Render Props**: Data fetcher and mouse tracker work correctly
- [ ] **Form State Manager**: Validation and state management functions
- [ ] **Compound Components**: Modal and accordion systems work independently
- [ ] **Custom Hooks**: Undo/redo and async operations function properly
- [ ] **Context Integration**: All patterns work together seamlessly
- [ ] **Performance**: No unnecessary re-renders or memory leaks
- [ ] **Accessibility**: Keyboard navigation and screen reader support
- [ ] **Responsive Design**: Works on mobile and desktop

### Component Testing Examples
```jsx
// src/tests/PatternTests.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PatternsDashboard from '../components/PatternsDashboard';
import Modal from '../components/Compound/Modal';
import { useUndo } from '../hooks/useUndo';

// Test HOC composition
describe('HOC Patterns', () => {
  test('withAuth redirects when not authenticated', () => {
    localStorage.removeItem('authToken');
    render(<PatternsDashboard />);
    expect(screen.getByText('Access Denied')).toBeInTheDocument();
  });

  test('withAuth renders component when authenticated', async () => {
    localStorage.setItem('authToken', 'fake-token');
    render(<PatternsDashboard />);
    await waitFor(() => {
      expect(screen.getByText(/Welcome/)).toBeInTheDocument();
    });
  });
});

// Test Compound Components
describe('Modal Component', () => {
  test('opens and closes correctly', () => {
    const onClose = jest.fn();
    const { rerender } = render(
      <Modal isOpen={false} onClose={onClose}>
        <Modal.Header>Test</Modal.Header>
      </Modal>
    );
    
    expect(screen.queryByText('Test')).not.toBeInTheDocument();
    
    rerender(
      <Modal isOpen={true} onClose={onClose}>
        <Modal.Header>Test</Modal.Header>
      </Modal>
    );
    
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});

// Test Custom Hooks
describe('useUndo Hook', () => {
  const TestComponent = () => {
    const { state, setState, undo, redo, canUndo, canRedo } = useUndo(0);
    
    return (
      <div>
        <span data-testid="value">{state}</span>
        <button onClick={() => setState(prev => prev + 1)}>Increment</button>
        <button onClick={undo} disabled={!canUndo}>Undo</button>
        <button onClick={redo} disabled={!canRedo}>Redo</button>
      </div>
    );
  };

  test('manages undo/redo state correctly', () => {
    render(<TestComponent />);
    
    expect(screen.getByTestId('value')).toHaveTextContent('0');
    
    fireEvent.click(screen.getByText('Increment'));
    expect(screen.getByTestId('value')).toHaveTextContent('1');
    
    fireEvent.click(screen.getByText('Undo'));
    expect(screen.getByTestId('value')).toHaveTextContent('0');
    
    fireEvent.click(screen.getByText('Redo'));
    expect(screen.getByTestId('value')).toHaveTextContent('1');
  });
});
```

---

## 🔧 Troubleshooting

### Common Issues

**1. HOC Props Not Passing Through**
```jsx
// ❌ Wrong - props not forwarded
const withExample = (WrappedComponent) => {
  return function EnhancedComponent() {
    return <WrappedComponent />;
  };
};

// ✅ Correct - forward all props
const withExample = (WrappedComponent) => {
  return function EnhancedComponent(props) {
    return <WrappedComponent {...props} />;
  };
};
```

**2. Render Props Performance Issues**
```jsx
// ❌ Wrong - creates new function on every render
<DataFetcher>
  {(data) => <SomeComponent data={data} />}
</DataFetcher>

// ✅ Better - memoize the render function
const renderData = useCallback((data) => 
  <SomeComponent data={data} />, []
);

<DataFetcher>
  {renderData}
</DataFetcher>
```

**3. Compound Components Context Issues**
```jsx
// ❌ Wrong - context not provided
const useAccordion = () => {
  const context = useContext(AccordionContext);
  return context; // might be undefined
};

// ✅ Correct - validate context exists
const useAccordion = () => {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error('useAccordion must be used within Accordion');
  }
  return context;
};
```

**4. Custom Hook Dependencies**
```jsx
// ❌ Wrong - missing dependencies
const useEffect(() => {
  fetchData();
}, []); // eslint warning

// ✅ Correct - include all dependencies
const useEffect(() => {
  fetchData();
}, [fetchData]); // or wrap fetchData in useCallback
```

---

## 🎓 Learning Objectives

### Higher-Order Components (HOCs)
- ✅ **HOC Creation**: Building reusable component enhancers
- ✅ **Props Forwarding**: Properly passing props through HOCs
- ✅ **HOC Composition**: Combining multiple HOCs effectively
- ✅ **Static Methods**: Copying static methods and display names

### Render Props Pattern
- ✅ **State Sharing**: Sharing stateful logic between components
- ✅ **Flexibility**: Creating highly flexible and reusable components
- ✅ **Performance**: Optimizing render prop components
- ✅ **Use Cases**: Understanding when to use render props

### Compound Components
- ✅ **Component Composition**: Building component systems that work together
- ✅ **Context Communication**: Using context for component coordination
- ✅ **API Design**: Creating intuitive and flexible APIs
- ✅ **State Management**: Managing shared state between compound components

### Custom Hooks
- ✅ **Logic Extraction**: Moving component logic into reusable hooks
- ✅ **State Management**: Advanced state patterns with hooks
- ✅ **Side Effects**: Managing complex side effects
- ✅ **Performance**: Optimizing custom hooks for performance

### Advanced Patterns
- ✅ **Provider Pattern**: Using context providers effectively
- ✅ **Component Communication**: Patterns for component interaction
- ✅ **Code Reusability**: Maximizing code reuse across patterns
- ✅ **Performance Optimization**: Preventing unnecessary re-renders

---

## 🚀 Next Steps

1. **Testing Integration**: Add comprehensive unit and integration tests
2. **TypeScript Conversion**: Add full TypeScript support for type safety
3. **Animation Patterns**: Integrate advanced animations with Framer Motion
4. **State Management**: Combine with Redux or Zustand for complex state
5. **Micro-frontends**: Explore patterns for micro-frontend architecture
6. **Performance Monitoring**: Add React DevTools and performance monitoring
7. **Accessibility**: Enhance accessibility features and ARIA support
8. **Documentation**: Create interactive documentation with Storybook

This implementation demonstrates mastery of advanced React patterns and provides a solid foundation for building complex, maintainable React applications with sophisticated component architectures.
