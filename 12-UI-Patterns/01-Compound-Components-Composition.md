# Compound Components & Composition Patterns

## Introduction to Compound Components

Compound components are a React pattern where components work together to form a complete UI. This pattern provides flexibility and customization while maintaining a clean API. Think of compound components like HTML elements: `<select>` works with `<option>`, `<table>` works with `<tr>` and `<td>`.

### Core Principles

1. **Flexibility**: Each sub-component can be used independently
2. **Implicit State Sharing**: Parent manages state shared across children
3. **Inversion of Control**: Users control the structure and arrangement
4. **Composability**: Components can be nested and combined

## Basic Compound Component Pattern

```jsx
// Basic implementation using React.cloneElement
import React, { useState, Children, cloneElement } from 'react'

const Accordion = ({ children }) => {
  const [openIndex, setOpenIndex] = useState(null)

  return (
    <div className="accordion">
      {Children.map(children, (child, index) =>
        cloneElement(child, {
          isOpen: openIndex === index,
          onToggle: () => setOpenIndex(openIndex === index ? null : index),
          index,
        })
      )}
    </div>
  )
}

const AccordionItem = ({ children, isOpen, onToggle, title }) => (
  <div className="accordion-item">
    <button
      className="accordion-header"
      onClick={onToggle}
      aria-expanded={isOpen}
    >
      {title}
    </button>
    {isOpen && (
      <div className="accordion-content">
        {children}
      </div>
    )}
  </div>
)

// Usage
const App = () => (
  <Accordion>
    <AccordionItem title="Section 1">
      <p>Content for section 1</p>
    </AccordionItem>
    <AccordionItem title="Section 2">
      <p>Content for section 2</p>
    </AccordionItem>
  </Accordion>
)
```

## Context-Based Compound Components

The Context API provides a cleaner approach for complex compound components:

```jsx
{% raw %}
{% raw %}
import React, { createContext, useContext, useState } from 'react'

// Step 1: Create context
const TabsContext = createContext()

// Step 2: Provider component
const Tabs = ({ children, defaultTab = 0, onChange }) => {
  const [activeTab, setActiveTab] = useState(defaultTab)

  const selectTab = (index) => {
    setActiveTab(index)
    onChange?.(index)
  }

  const value = {
    activeTab,
    selectTab,
  }

  return (
    <TabsContext.Provider value={value}>
      <div className="tabs" role="tablist">
        {children}
      </div>
    </TabsContext.Provider>
  )
}

// Step 3: Hook for accessing context
const useTabs = () => {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error('Tab components must be used within a Tabs provider')
  }
  return context
}

// Step 4: Sub-components
const TabList = ({ children }) => (
  <div className="tab-list" role="tablist">
    {children}
  </div>
)

const Tab = ({ children, index, disabled = false }) => {
  const { activeTab, selectTab } = useTabs()
  const isActive = activeTab === index

  return (
    <button
      className={`tab ${isActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
      role="tab"
      aria-selected={isActive}
      aria-disabled={disabled}
      onClick={() => !disabled && selectTab(index)}
      tabIndex={isActive ? 0 : -1}
    >
      {children}
    </button>
  )
}

const TabPanels = ({ children }) => {
  const { activeTab } = useTabs()
  
  return (
    <div className="tab-panels">
      {React.Children.map(children, (child, index) =>
        index === activeTab ? child : null
      )}
    </div>
  )
}

const TabPanel = ({ children, index }) => {
  const { activeTab } = useTabs()
  const isActive = activeTab === index

  return (
    <div
      className={`tab-panel ${isActive ? 'active' : ''}`}
      role="tabpanel"
      aria-hidden={!isActive}
    >
      {children}
    </div>
  )
}

// Attach sub-components as properties
Tabs.List = TabList
Tabs.Tab = Tab
Tabs.Panels = TabPanels
Tabs.Panel = TabPanel

// Usage
const TabsExample = () => (
  <Tabs defaultTab={0} onChange={(index) => console.log('Tab changed:', index)}>
    <Tabs.List>
      <Tabs.Tab index={0}>Tab 1</Tabs.Tab>
      <Tabs.Tab index={1}>Tab 2</Tabs.Tab>
      <Tabs.Tab index={2} disabled>Tab 3</Tabs.Tab>
    </Tabs.List>
    
    <Tabs.Panels>
      <Tabs.Panel index={0}>
        <h3>Panel 1</h3>
        <p>Content for tab 1</p>
      </Tabs.Panel>
      <Tabs.Panel index={1}>
        <h3>Panel 2</h3>
        <p>Content for tab 2</p>
      </Tabs.Panel>
      <Tabs.Panel index={2}>
        <h3>Panel 3</h3>
        <p>Content for tab 3</p>
      </Tabs.Panel>
    </Tabs.Panels>
  </Tabs>
)
{% endraw %}
{% endraw %}
```

## Advanced Modal Compound Component

```jsx
{% raw %}
{% raw %}
import React, { createContext, useContext, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

const ModalContext = createContext()

const Modal = ({ children, isOpen, onClose, className = '' }) => {
  const modalRef = useRef()
  const previousFocusRef = useRef()

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement
      modalRef.current?.focus()
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden'
      
      return () => {
        document.body.style.overflow = 'unset'
        previousFocusRef.current?.focus()
      }
    }
  }, [isOpen])

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const contextValue = {
    onClose,
    modalRef,
  }

  return createPortal(
    <ModalContext.Provider value={contextValue}>
      <div className="modal-overlay" onClick={onClose}>
        <div
          ref={modalRef}
          className={`modal ${className}`}
          role="dialog"
          aria-modal="true"
          tabIndex={-1}
          onClick={(e) => e.stopPropagation()}
        >
          {children}
        </div>
      </div>
    </ModalContext.Provider>,
    document.body
  )
}

const useModal = () => {
  const context = useContext(ModalContext)
  if (!context) {
    throw new Error('Modal components must be used within a Modal')
  }
  return context
}

const ModalHeader = ({ children, showCloseButton = true }) => {
  const { onClose } = useModal()

  return (
    <div className="modal-header">
      <div className="modal-title">{children}</div>
      {showCloseButton && (
        <button
          className="modal-close"
          onClick={onClose}
          aria-label="Close modal"
        >
          ×
        </button>
      )}
    </div>
  )
}

const ModalBody = ({ children }) => (
  <div className="modal-body">
    {children}
  </div>
)

const ModalFooter = ({ children }) => (
  <div className="modal-footer">
    {children}
  </div>
)

Modal.Header = ModalHeader
Modal.Body = ModalBody
Modal.Footer = ModalFooter

// Usage
const ModalExample = () => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>
      
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <Modal.Header>
          Confirm Action
        </Modal.Header>
        
        <Modal.Body>
          <p>Are you sure you want to delete this item?</p>
        </Modal.Body>
        
        <Modal.Footer>
          <button onClick={() => setIsOpen(false)}>Cancel</button>
          <button onClick={() => setIsOpen(false)}>Delete</button>
        </Modal.Footer>
      </Modal>
    </>
  )
}
{% endraw %}
{% endraw %}
```

## Dropdown Compound Component

```jsx
{% raw %}
{% raw %}
const DropdownContext = createContext()

const Dropdown = ({ children, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const dropdownRef = useRef()

  const toggle = () => setIsOpen(!isOpen)
  const close = () => setIsOpen(false)
  
  const selectItem = (item) => {
    setSelectedItem(item)
    onSelect?.(item)
    close()
  }

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        close()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const contextValue = {
    isOpen,
    selectedItem,
    toggle,
    close,
    selectItem,
  }

  return (
    <DropdownContext.Provider value={contextValue}>
      <div ref={dropdownRef} className="dropdown">
        {children}
      </div>
    </DropdownContext.Provider>
  )
}

const useDropdown = () => {
  const context = useContext(DropdownContext)
  if (!context) {
    throw new Error('Dropdown components must be used within a Dropdown')
  }
  return context
}

const DropdownTrigger = ({ children, as: Component = 'button' }) => {
  const { toggle, isOpen } = useDropdown()

  return (
    <Component
      className="dropdown-trigger"
      onClick={toggle}
      aria-expanded={isOpen}
      aria-haspopup="true"
    >
      {children}
    </Component>
  )
}

const DropdownMenu = ({ children }) => {
  const { isOpen } = useDropdown()

  if (!isOpen) return null

  return (
    <div className="dropdown-menu" role="menu">
      {children}
    </div>
  )
}

const DropdownItem = ({ children, value, disabled = false }) => {
  const { selectItem } = useDropdown()

  const handleClick = () => {
    if (!disabled) {
      selectItem(value)
    }
  }

  return (
    <div
      className={`dropdown-item ${disabled ? 'disabled' : ''}`}
      role="menuitem"
      onClick={handleClick}
      tabIndex={disabled ? -1 : 0}
    >
      {children}
    </div>
  )
}

Dropdown.Trigger = DropdownTrigger
Dropdown.Menu = DropdownMenu
Dropdown.Item = DropdownItem

// Usage
const DropdownExample = () => (
  <Dropdown onSelect={(value) => console.log('Selected:', value)}>
    <Dropdown.Trigger>
      Select Option
    </Dropdown.Trigger>
    
    <Dropdown.Menu>
      <Dropdown.Item value="option1">Option 1</Dropdown.Item>
      <Dropdown.Item value="option2">Option 2</Dropdown.Item>
      <Dropdown.Item value="option3" disabled>Option 3 (Disabled)</Dropdown.Item>
    </Dropdown.Menu>
  </Dropdown>
)
{% endraw %}
{% endraw %}
```

## Form Builder Compound Component

```jsx
{% raw %}
{% raw %}
const FormContext = createContext()

const Form = ({ children, onSubmit, validation = {} }) => {
  const [values, setValues] = useState({})
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})

  const setValue = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }))
    }
  }

  const setFieldTouched = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }))
  }

  const validateField = (name, value) => {
    const fieldValidation = validation[name]
    if (!fieldValidation) return null

    if (typeof fieldValidation === 'function') {
      return fieldValidation(value, values)
    }

    // Built-in validations
    if (fieldValidation.required && (!value || value.trim() === '')) {
      return fieldValidation.message || `${name} is required`
    }

    if (fieldValidation.minLength && value.length < fieldValidation.minLength) {
      return `${name} must be at least ${fieldValidation.minLength} characters`
    }

    if (fieldValidation.pattern && !fieldValidation.pattern.test(value)) {
      return fieldValidation.message || `${name} format is invalid`
    }

    return null
  }

  const validateForm = () => {
    const newErrors = {}
    Object.keys(validation).forEach(name => {
      const error = validateField(name, values[name])
      if (error) {
        newErrors[name] = error
      }
    })
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validateForm()) {
      onSubmit(values)
    }
  }

  const contextValue = {
    values,
    errors,
    touched,
    setValue,
    setFieldTouched,
    validateField,
  }

  return (
    <FormContext.Provider value={contextValue}>
      <form onSubmit={handleSubmit} noValidate>
        {children}
      </form>
    </FormContext.Provider>
  )
}

const useForm = () => {
  const context = useContext(FormContext)
  if (!context) {
    throw new Error('Form components must be used within a Form')
  }
  return context
}

const FormField = ({ children, name, label, required = false }) => {
  const { errors, touched } = useForm()
  const hasError = touched[name] && errors[name]

  return (
    <div className={`form-field ${hasError ? 'error' : ''}`}>
      <label className="form-label">
        {label} {required && <span className="required">*</span>}
      </label>
      {children}
      {hasError && (
        <div className="form-error" role="alert">
          {errors[name]}
        </div>
      )}
    </div>
  )
}

const FormInput = ({ name, type = 'text', placeholder, ...props }) => {
  const { values, setValue, setFieldTouched, validateField } = useForm()

  const handleChange = (e) => {
    setValue(name, e.target.value)
  }

  const handleBlur = () => {
    setFieldTouched(name)
    validateField(name, values[name])
  }

  return (
    <input
      type={type}
      name={name}
      value={values[name] || ''}
      placeholder={placeholder}
      onChange={handleChange}
      onBlur={handleBlur}
      className="form-input"
      {...props}
    />
  )
}

const FormTextarea = ({ name, placeholder, rows = 4, ...props }) => {
  const { values, setValue, setFieldTouched } = useForm()

  return (
    <textarea
      name={name}
      value={values[name] || ''}
      placeholder={placeholder}
      rows={rows}
      onChange={(e) => setValue(name, e.target.value)}
      onBlur={() => setFieldTouched(name)}
      className="form-textarea"
      {...props}
    />
  )
}

const FormSelect = ({ name, children, placeholder, ...props }) => {
  const { values, setValue, setFieldTouched } = useForm()

  return (
    <select
      name={name}
      value={values[name] || ''}
      onChange={(e) => setValue(name, e.target.value)}
      onBlur={() => setFieldTouched(name)}
      className="form-select"
      {...props}
    >
      {placeholder && <option value="">{placeholder}</option>}
      {children}
    </select>
  )
}

const FormButton = ({ children, type = 'submit', variant = 'primary', ...props }) => (
  <button
    type={type}
    className={`form-button ${variant}`}
    {...props}
  >
    {children}
  </button>
)

Form.Field = FormField
Form.Input = FormInput
Form.Textarea = FormTextarea
Form.Select = FormSelect
Form.Button = FormButton

// Usage
const FormExample = () => (
  <Form
    onSubmit={(values) => console.log('Form submitted:', values)}
    validation={{
      email: {
        required: true,
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        message: 'Please enter a valid email address'
      },
      password: {
        required: true,
        minLength: 8
      },
      confirmPassword: (value, values) => {
        if (value !== values.password) {
          return 'Passwords do not match'
        }
        return null
      }
    }}
  >
    <Form.Field name="email" label="Email" required>
      <Form.Input
        name="email"
        type="email"
        placeholder="Enter your email"
      />
    </Form.Field>

    <Form.Field name="password" label="Password" required>
      <Form.Input
        name="password"
        type="password"
        placeholder="Enter your password"
      />
    </Form.Field>

    <Form.Field name="confirmPassword" label="Confirm Password" required>
      <Form.Input
        name="confirmPassword"
        type="password"
        placeholder="Confirm your password"
      />
    </Form.Field>

    <Form.Field name="country" label="Country">
      <Form.Select name="country" placeholder="Select country">
        <option value="us">United States</option>
        <option value="ca">Canada</option>
        <option value="uk">United Kingdom</option>
      </Form.Select>
    </Form.Field>

    <Form.Button type="submit">
      Create Account
    </Form.Button>
  </Form>
)
{% endraw %}
{% endraw %}
```

## Advanced Patterns

### Render Props Integration

```jsx
const DataProvider = ({ children, render }) => {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  const contextValue = {
    data,
    loading,
    setData,
    setLoading,
  }

  return (
    <DataContext.Provider value={contextValue}>
      {render ? render(contextValue) : children}
    </DataContext.Provider>
  )
}

// Usage with render prop
<DataProvider
  render={({ data, loading }) => (
    <div>
      {loading ? 'Loading...' : data.map(item => <div key={item.id}>{item.name}</div>)}
    </div>
  )}
/>
```

### Higher-Order Component Integration

```jsx
const withCollapsible = (WrappedComponent) => {
  return (props) => {
    const [isCollapsed, setIsCollapsed] = useState(false)

    return (
      <WrappedComponent
        {...props}
        isCollapsed={isCollapsed}
        onToggle={() => setIsCollapsed(!isCollapsed)}
      />
    )
  }
}

const CollapsiblePanel = withCollapsible(({ children, isCollapsed, onToggle, title }) => (
  <div className="collapsible-panel">
    <button onClick={onToggle}>
      {title} {isCollapsed ? '▼' : '▲'}
    </button>
    {!isCollapsed && (
      <div className="panel-content">
        {children}
      </div>
    )}
  </div>
))
```

### TypeScript Integration

```tsx
interface TabsContextType {
  activeTab: number
  selectTab: (index: number) => void
}

const TabsContext = createContext<TabsContextType | null>(null)

interface TabsProps {
  children: React.ReactNode
  defaultTab?: number
  onChange?: (index: number) => void
}

const Tabs: React.FC<TabsProps> & {
  List: React.FC<TabListProps>
  Tab: React.FC<TabProps>
  Panels: React.FC<TabPanelsProps>
  Panel: React.FC<TabPanelProps>
} = ({ children, defaultTab = 0, onChange }) => {
  // Implementation...
}

interface TabProps {
  children: React.ReactNode
  index: number
  disabled?: boolean
}

const Tab: React.FC<TabProps> = ({ children, index, disabled = false }) => {
  // Implementation...
}
```

## Best Practices

### 1. Context Performance

```jsx
// Separate contexts for different concerns
const TabsStateContext = createContext()
const TabsActionsContext = createContext()

const Tabs = ({ children }) => {
  const [state, setState] = useState({ activeTab: 0 })
  
  // Memoize actions to prevent re-renders
  const actions = useMemo(() => ({
    selectTab: (index) => setState(prev => ({ ...prev, activeTab: index }))
  }), [])

  return (
    <TabsStateContext.Provider value={state}>
      <TabsActionsContext.Provider value={actions}>
        {children}
      </TabsActionsContext.Provider>
    </TabsStateContext.Provider>
  )
}
```

### 2. Error Boundaries

```jsx
class CompoundComponentErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Compound component error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong with the component.</div>
    }

    return this.props.children
  }
}
```

### 3. Testing Compound Components

```jsx
import { render, screen, fireEvent } from '@testing-library/react'

describe('Tabs Compound Component', () => {
  test('switches tabs correctly', () => {
    render(
      <Tabs defaultTab={0}>
        <Tabs.List>
          <Tabs.Tab index={0}>Tab 1</Tabs.Tab>
          <Tabs.Tab index={1}>Tab 2</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panels>
          <Tabs.Panel index={0}>Panel 1</Tabs.Panel>
          <Tabs.Panel index={1}>Panel 2</Tabs.Panel>
        </Tabs.Panels>
      </Tabs>
    )

    const tab2 = screen.getByText('Tab 2')
    fireEvent.click(tab2)

    expect(screen.getByText('Panel 2')).toBeVisible()
    expect(screen.queryByText('Panel 1')).not.toBeInTheDocument()
  })

  test('maintains accessibility attributes', () => {
    render(
      <Tabs>
        <Tabs.List>
          <Tabs.Tab index={0}>Tab 1</Tabs.Tab>
        </Tabs.List>
      </Tabs>
    )

    const tab = screen.getByRole('tab')
    expect(tab).toHaveAttribute('aria-selected', 'true')
  })
})
```

## Conclusion

Compound components provide a powerful pattern for building flexible, reusable UI components. They offer:

- **API Flexibility**: Users control structure and composition
- **Separation of Concerns**: Each component has a specific responsibility
- **Implicit State Management**: Parent manages shared state transparently
- **Composability**: Components can be nested and combined in various ways

When implementing compound components, focus on:
- Clear component APIs and naming conventions
- Proper error handling and validation
- Accessibility and semantic HTML
- Performance optimization through context design
- Comprehensive testing coverage

This pattern is particularly useful for complex UI components like forms, navigation, data displays, and interactive widgets where users need control over the structure while maintaining consistent behavior.