# Module 12: UI Patterns

## Learning Objectives
By the end of this module, you will be able to:
- Master advanced UI component patterns and architectures
- Implement complex accessibility features and ARIA patterns
- Build reusable compound components and composition patterns
- Create efficient virtualization and infinite scroll implementations
- Handle complex form patterns and validation scenarios
- Implement advanced navigation and layout patterns
- Build responsive and adaptive UI components
- Create interactive data visualization components

## Overview
This module covers advanced UI patterns essential for building complex, accessible, and performant React applications. You'll learn industry-standard patterns for component composition, accessibility, and user interaction design.

## Duration: Week 12 (40 hours)
- **Reading & Research**: 10 hours
- **Hands-on Practice**: 20 hours
- **Projects**: 8 hours
- **Assessment**: 2 hours

---

## Topics Covered

### 1. Compound Components Pattern
```javascript
// Advanced compound component implementation
import { createContext, useContext, cloneElement, Children } from 'react'

// Context for sharing state between compound components
const TabsContext = createContext()

function Tabs({ children, defaultActiveTab = 0, onTabChange }) {
  const [activeTab, setActiveTab] = useState(defaultActiveTab)

  const handleTabChange = (index) => {
    setActiveTab(index)
    onTabChange?.(index)
  }

  const contextValue = {
    activeTab,
    onTabChange: handleTabChange,
  }

  return (
    <TabsContext.Provider value={contextValue}>
      <div className="tabs-container" role="tablist">
        {children}
      </div>
    </TabsContext.Provider>
  )
}

function TabList({ children }) {
  return (
    <div className="tab-list" role="tablist">
      {Children.map(children, (child, index) =>
        cloneElement(child, { index })
      )}
    </div>
  )
}

function Tab({ children, index, disabled = false }) {
  const { activeTab, onTabChange } = useContext(TabsContext)
  const isActive = activeTab === index

  const handleClick = () => {
    if (!disabled) {
      onTabChange(index)
    }
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleClick()
    }
  }

  return (
    <button
      role="tab"
      aria-selected={isActive}
      aria-controls={`tabpanel-${index}`}
      id={`tab-${index}`}
      tabIndex={isActive ? 0 : -1}
      disabled={disabled}
      className={`tab ${isActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
    >
      {children}
    </button>
  )
}

function TabPanels({ children }) {
  const { activeTab } = useContext(TabsContext)

  return (
    <div className="tab-panels">
      {Children.map(children, (child, index) =>
        cloneElement(child, { index, isActive: activeTab === index })
      )}
    </div>
  )
}

function TabPanel({ children, index, isActive }) {
  return (
    <div
      role="tabpanel"
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      hidden={!isActive}
      className={`tab-panel ${isActive ? 'active' : ''}`}
    >
      {isActive && children}
    </div>
  )
}

// Compose compound components
Tabs.List = TabList
Tabs.Tab = Tab
Tabs.Panels = TabPanels
Tabs.Panel = TabPanel

// Usage
function App() {
  return (
    <Tabs defaultActiveTab={0} onTabChange={(index) => console.log(`Tab ${index} selected`)}>
      <Tabs.List>
        <Tabs.Tab>Overview</Tabs.Tab>
        <Tabs.Tab>Details</Tabs.Tab>
        <Tabs.Tab disabled>Settings</Tabs.Tab>
      </Tabs.List>
      
      <Tabs.Panels>
        <Tabs.Panel>
          <h2>Overview Content</h2>
          <p>This is the overview panel.</p>
        </Tabs.Panel>
        <Tabs.Panel>
          <h2>Details Content</h2>
          <p>This is the details panel.</p>
        </Tabs.Panel>
        <Tabs.Panel>
          <h2>Settings Content</h2>
          <p>This is the settings panel.</p>
        </Tabs.Panel>
      </Tabs.Panels>
    </Tabs>
  )
}
```

### 2. Render Props and Function as Children
```javascript
// Advanced render props pattern for data fetching
function DataFetcher({ 
  url, 
  children, 
  fallback = null, 
  onError = null,
  transform = (data) => data 
}) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    const fetchData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }))
        
        const response = await fetch(url)
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        const transformedData = transform(data)

        if (!cancelled) {
          setState({
            data: transformedData,
            loading: false,
            error: null,
          })
        }
      } catch (error) {
        if (!cancelled) {
          setState({
            data: null,
            loading: false,
            error,
          })
          onError?.(error)
        }
      }
    }

    fetchData()

    return () => {
      cancelled = true
    }
  }, [url, transform, onError])

  // Render prop pattern
  if (typeof children === 'function') {
    return children(state)
  }

  // Fallback rendering
  if (state.loading) return fallback || <div>Loading...</div>
  if (state.error) return <div>Error: {state.error.message}</div>
  
  return children
}

// Mouse position tracker with render props
function MouseTracker({ children, throttleMs = 16 }) {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const throttledSetPosition = useCallback(
    throttle(setPosition, throttleMs),
    [throttleMs]
  )

  useEffect(() => {
    const handleMouseMove = (event) => {
      throttledSetPosition({ x: event.clientX, y: event.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [throttledSetPosition])

  return children(position)
}

// Usage examples
function App() {
  return (
    <div>
      {/* Data fetching with render props */}
      <DataFetcher 
        url="/api/users" 
        transform={(data) => data.users}
      >
        {({ data, loading, error }) => (
          <div>
            {loading && <Spinner />}
            {error && <ErrorMessage error={error} />}
            {data && (
              <UserList 
                users={data} 
                onUserSelect={(user) => console.log(user)}
              />
            )}
          </div>
        )}
      </DataFetcher>

      {/* Mouse tracking with render props */}
      <MouseTracker>
        {({ x, y }) => (
          <div>
            <h2>Mouse Position</h2>
            <p>X: {x}, Y: {y}</p>
            <div
              style={{
                position: 'absolute',
                left: x - 10,
                top: y - 10,
                width: 20,
                height: 20,
                backgroundColor: 'red',
                borderRadius: '50%',
                pointerEvents: 'none',
              }}
            />
          </div>
        )}
      </MouseTracker>
    </div>
  )
}
```

### 3. Advanced Accessibility Patterns
```javascript
// Comprehensive accessible modal implementation
import { useEffect, useRef, useCallback } from 'react'
import { createPortal } from 'react-dom'

function AccessibleModal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  closeOnEscape = true,
  closeOnBackdrop = true,
  initialFocus = null,
  restoreFocus = true 
}) {
  const modalRef = useRef()
  const previousActiveElement = useRef()
  const titleId = useId()
  const descriptionId = useId()

  // Focus management
  useEffect(() => {
    if (isOpen) {
      // Store currently focused element
      previousActiveElement.current = document.activeElement

      // Focus the modal
      const focusTarget = initialFocus?.current || modalRef.current
      focusTarget?.focus()

      // Trap focus within modal
      const handleTabKey = (event) => {
        const focusableElements = modalRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        const firstElement = focusableElements[0]
        const lastElement = focusableElements[focusableElements.length - 1]

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault()
            lastElement.focus()
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault()
            firstElement.focus()
          }
        }
      }

      const handleKeyDown = (event) => {
        if (event.key === 'Tab') {
          handleTabKey(event)
        } else if (event.key === 'Escape' && closeOnEscape) {
          onClose()
        }
      }

      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    } else if (restoreFocus && previousActiveElement.current) {
      // Restore focus when modal closes
      previousActiveElement.current.focus()
    }
  }, [isOpen, initialFocus, closeOnEscape, onClose, restoreFocus])

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      const originalStyle = window.getComputedStyle(document.body).overflow
      document.body.style.overflow = 'hidden'
      return () => {
        document.body.style.overflow = originalStyle
      }
    }
  }, [isOpen])

  const handleBackdropClick = useCallback((event) => {
    if (closeOnBackdrop && event.target === event.currentTarget) {
      onClose()
    }
  }, [closeOnBackdrop, onClose])

  if (!isOpen) return null

  return createPortal(
    <div
      className="modal-backdrop"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <div
        ref={modalRef}
        className="modal-content"
        tabIndex={-1}
      >
        <div className="modal-header">
          <h2 id={titleId} className="modal-title">
            {title}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="modal-close"
          >
            ×
          </button>
        </div>
        
        <div id={descriptionId} className="modal-body">
          {children}
        </div>
      </div>
    </div>,
    document.body
  )
}

// Accessible dropdown/combobox
function AccessibleCombobox({
  options,
  value,
  onChange,
  placeholder = "Select an option...",
  searchable = true,
  multiSelect = false
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [highlightedIndex, setHighlightedIndex] = useState(-1)
  const [selectedItems, setSelectedItems] = useState(multiSelect ? [] : null)
  
  const comboboxRef = useRef()
  const listboxRef = useRef()
  const inputRef = useRef()
  
  const comboboxId = useId()
  const listboxId = useId()

  // Filter options based on search
  const filteredOptions = useMemo(() => {
    if (!searchTerm) return options
    return options.filter(option =>
      option.label.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [options, searchTerm])

  // Keyboard navigation
  const handleKeyDown = (event) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        if (!isOpen) {
          setIsOpen(true)
        } else {
          setHighlightedIndex(prev => 
            prev < filteredOptions.length - 1 ? prev + 1 : 0
          )
        }
        break
        
      case 'ArrowUp':
        event.preventDefault()
        if (isOpen) {
          setHighlightedIndex(prev => 
            prev > 0 ? prev - 1 : filteredOptions.length - 1
          )
        }
        break
        
      case 'Enter':
        event.preventDefault()
        if (isOpen && highlightedIndex >= 0) {
          handleOptionSelect(filteredOptions[highlightedIndex])
        } else {
          setIsOpen(!isOpen)
        }
        break
        
      case 'Escape':
        setIsOpen(false)
        inputRef.current?.focus()
        break
        
      case 'Tab':
        setIsOpen(false)
        break
    }
  }

  const handleOptionSelect = (option) => {
    if (multiSelect) {
      const isSelected = selectedItems.some(item => item.value === option.value)
      if (isSelected) {
        setSelectedItems(prev => prev.filter(item => item.value !== option.value))
      } else {
        setSelectedItems(prev => [...prev, option])
      }
    } else {
      setSelectedItems(option)
      setIsOpen(false)
      onChange(option)
    }
  }

  return (
    <div ref={comboboxRef} className="combobox-container">
      <div
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-owns={listboxId}
        id={comboboxId}
      >
        <input
          ref={inputRef}
          type="text"
          value={searchable ? searchTerm : (selectedItems?.label || '')}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          aria-autocomplete="list"
          aria-controls={listboxId}
          className="combobox-input"
        />
        
        <button
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle options"
          className="combobox-toggle"
        >
          ▼
        </button>
      </div>

      {isOpen && (
        <ul
          ref={listboxRef}
          role="listbox"
          id={listboxId}
          aria-labelledby={comboboxId}
          className="combobox-listbox"
        >
          {filteredOptions.map((option, index) => (
            <li
              key={option.value}
              role="option"
              aria-selected={
                multiSelect 
                  ? selectedItems.some(item => item.value === option.value)
                  : selectedItems?.value === option.value
              }
              className={`combobox-option ${
                index === highlightedIndex ? 'highlighted' : ''
              } ${
                multiSelect && selectedItems.some(item => item.value === option.value)
                  ? 'selected'
                  : selectedItems?.value === option.value
                  ? 'selected'
                  : ''
              }`}
              onClick={() => handleOptionSelect(option)}
            >
              {option.label}
            </li>
          ))}
          
          {filteredOptions.length === 0 && (
            <li className="combobox-no-options">No options found</li>
          )}
        </ul>
      )}
    </div>
  )
}
```

### 4. Virtual Scrolling and Infinite Lists
```javascript
// Advanced virtual scrolling implementation
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualizedList({ 
  items, 
  renderItem, 
  itemHeight = 50, 
  overscan = 5,
  estimateSize,
  getItemKey,
  onEndReached,
  endReachedThreshold = 0.8 
}) {
  const parentRef = useRef()
  const [endReachedCalled, setEndReachedCalled] = useState(false)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: estimateSize || (() => itemHeight),
    overscan,
    getItemKey: getItemKey || ((index) => items[index]?.id || index),
  })

  // Handle infinite scrolling
  useEffect(() => {
    const lastItem = virtualizer.getVirtualItems().slice(-1)[0]
    
    if (!lastItem) return

    const threshold = items.length * endReachedThreshold
    
    if (lastItem.index >= threshold - 1 && !endReachedCalled) {
      setEndReachedCalled(true)
      onEndReached?.()
    }

    // Reset flag when new items are loaded
    if (endReachedCalled && lastItem.index < threshold - 1) {
      setEndReachedCalled(false)
    }
  }, [virtualizer.getVirtualItems(), items.length, endReachedThreshold, onEndReached, endReachedCalled])

  return (
    <div
      ref={parentRef}
      className="virtual-list-container"
      style={{
        height: '400px',
        overflow: 'auto',
      }}
    >
      <div
        style={{
          height: virtualizer.getTotalSize(),
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: virtualItem.size,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {renderItem(items[virtualItem.index], virtualItem.index)}
          </div>
        ))}
      </div>
    </div>
  )
}

// Dynamic height virtual list
function DynamicVirtualList({ items, renderItem }) {
  const parentRef = useRef()
  const measurements = useRef(new Map())

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: (index) => measurements.current.get(index) || 100,
    overscan: 3,
  })

  const measureElement = useCallback((element, index) => {
    if (element) {
      const height = element.getBoundingClientRect().height
      if (measurements.current.get(index) !== height) {
        measurements.current.set(index, height)
        virtualizer.measure()
      }
    }
  }, [virtualizer])

  return (
    <div
      ref={parentRef}
      style={{
        height: '500px',
        overflow: 'auto',
      }}
    >
      <div
        style={{
          height: virtualizer.getTotalSize(),
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            data-index={virtualItem.index}
            ref={(el) => measureElement(el, virtualItem.index)}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {renderItem(items[virtualItem.index], virtualItem.index)}
          </div>
        ))}
      </div>
    </div>
  )
}

// Infinite scroll with intersection observer
function useInfiniteScroll(fetchMore, hasNextPage, threshold = 1.0) {
  const [isFetching, setIsFetching] = useState(false)
  const loadMoreRef = useRef()

  useEffect(() => {
    if (!hasNextPage || isFetching) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsFetching(true)
          fetchMore().finally(() => setIsFetching(false))
        }
      },
      { threshold }
    )

    const currentRef = loadMoreRef.current
    if (currentRef) observer.observe(currentRef)

    return () => {
      if (currentRef) observer.unobserve(currentRef)
    }
  }, [fetchMore, hasNextPage, isFetching, threshold])

  return { loadMoreRef, isFetching }
}
```

### 5. Advanced Form Patterns
```javascript
// Multi-step form with validation
function MultiStepForm({ steps, onSubmit, validationSchema }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState({})
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})

  const currentStepData = steps[currentStep]
  const isLastStep = currentStep === steps.length - 1
  const isFirstStep = currentStep === 0

  const validateStep = async (stepIndex = currentStep) => {
    try {
      const stepSchema = validationSchema[stepIndex]
      if (stepSchema) {
        await stepSchema.validate(formData, { abortEarly: false })
        setErrors(prev => ({ ...prev, [stepIndex]: {} }))
        return true
      }
      return true
    } catch (validationErrors) {
      const stepErrors = {}
      validationErrors.inner.forEach(error => {
        stepErrors[error.path] = error.message
      })
      setErrors(prev => ({ ...prev, [stepIndex]: stepErrors }))
      return false
    }
  }

  const handleNext = async () => {
    const isValid = await validateStep()
    if (isValid && !isLastStep) {
      setCurrentStep(prev => prev + 1)
    } else if (isValid && isLastStep) {
      onSubmit(formData)
    }
  }

  const handlePrevious = () => {
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleFieldChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setTouched(prev => ({ ...prev, [field]: true }))
    
    // Clear field error when user starts typing
    if (errors[currentStep]?.[field]) {
      setErrors(prev => ({
        ...prev,
        [currentStep]: {
          ...prev[currentStep],
          [field]: undefined
        }
      }))
    }
  }

  const handleStepClick = async (stepIndex) => {
    // Validate all previous steps before allowing jump
    let canNavigate = true
    for (let i = 0; i < stepIndex; i++) {
      const isStepValid = await validateStep(i)
      if (!isStepValid) {
        canNavigate = false
        break
      }
    }
    
    if (canNavigate) {
      setCurrentStep(stepIndex)
    }
  }

  return (
    <div className="multi-step-form">
      {/* Step indicator */}
      <div className="step-indicator">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`step ${index <= currentStep ? 'completed' : ''} ${
              index === currentStep ? 'active' : ''
            }`}
            onClick={() => handleStepClick(index)}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-title">{step.title}</div>
          </div>
        ))}
      </div>

      {/* Step content */}
      <div className="step-content">
        <h2>{currentStepData.title}</h2>
        {currentStepData.description && (
          <p className="step-description">{currentStepData.description}</p>
        )}

        <FormStep
          fields={currentStepData.fields}
          data={formData}
          errors={errors[currentStep] || {}}
          touched={touched}
          onChange={handleFieldChange}
        />
      </div>

      {/* Navigation */}
      <div className="step-navigation">
        <button
          type="button"
          onClick={handlePrevious}
          disabled={isFirstStep}
          className="btn-secondary"
        >
          Previous
        </button>
        
        <button
          type="button"
          onClick={handleNext}
          className="btn-primary"
        >
          {isLastStep ? 'Submit' : 'Next'}
        </button>
      </div>

      {/* Progress bar */}
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{
            width: `${((currentStep + 1) / steps.length) * 100}%`
          }}
        />
      </div>
    </div>
  )
}

// Dynamic form builder
function DynamicForm({ schema, onSubmit, initialValues = {} }) {
  const [formData, setFormData] = useState(initialValues)
  const [errors, setErrors] = useState({})

  const handleSubmit = async (event) => {
    event.preventDefault()
    
    try {
      // Validate entire form
      await schema.validation.validate(formData, { abortEarly: false })
      setErrors({})
      onSubmit(formData)
    } catch (validationErrors) {
      const formErrors = {}
      validationErrors.inner.forEach(error => {
        formErrors[error.path] = error.message
      })
      setErrors(formErrors)
    }
  }

  const renderField = (field) => {
    switch (field.type) {
      case 'text':
      case 'email':
      case 'password':
        return (
          <input
            type={field.type}
            id={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              [field.name]: e.target.value
            }))}
            placeholder={field.placeholder}
            required={field.required}
            aria-describedby={errors[field.name] ? `${field.name}-error` : undefined}
            className={errors[field.name] ? 'error' : ''}
          />
        )

      case 'select':
        return (
          <select
            id={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              [field.name]: e.target.value
            }))}
            required={field.required}
          >
            <option value="">Select {field.label}</option>
            {field.options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        )

      case 'checkbox':
        return (
          <input
            type="checkbox"
            id={field.name}
            checked={formData[field.name] || false}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              [field.name]: e.target.checked
            }))}
          />
        )

      case 'radio':
        return (
          <div className="radio-group">
            {field.options.map(option => (
              <label key={option.value} className="radio-option">
                <input
                  type="radio"
                  name={field.name}
                  value={option.value}
                  checked={formData[field.name] === option.value}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    [field.name]: e.target.value
                  }))}
                />
                {option.label}
              </label>
            ))}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <form onSubmit={handleSubmit} className="dynamic-form">
      {schema.fields.map(field => (
        <div key={field.name} className="form-field">
          <label htmlFor={field.name}>
            {field.label}
            {field.required && <span className="required">*</span>}
          </label>
          
          {renderField(field)}
          
          {field.help && (
            <div className="field-help">{field.help}</div>
          )}
          
          {errors[field.name] && (
            <div id={`${field.name}-error`} className="field-error">
              {errors[field.name]}
            </div>
          )}
        </div>
      ))}

      <button type="submit" className="submit-button">
        {schema.submitText || 'Submit'}
      </button>
    </form>
  )
}
```

### 6. Complex Navigation Patterns
```javascript
// Breadcrumb navigation with dynamic routing
function Breadcrumbs({ routes, separator = ">" }) {
  const location = useLocation()
  const navigate = useNavigate()
  
  const breadcrumbs = useMemo(() => {
    const pathSegments = location.pathname.split('/').filter(Boolean)
    const crumbs = []
    
    pathSegments.reduce((path, segment) => {
      const currentPath = `${path}/${segment}`
      const route = routes.find(r => r.path === currentPath)
      
      if (route) {
        crumbs.push({
          path: currentPath,
          label: route.breadcrumb || route.title || segment,
          isClickable: route.breadcrumbClickable !== false,
        })
      }
      
      return currentPath
    }, '')
    
    return crumbs
  }, [location.pathname, routes])

  if (breadcrumbs.length <= 1) return null

  return (
    <nav aria-label="Breadcrumb" className="breadcrumbs">
      <ol>
        <li>
          <button
            onClick={() => navigate('/')}
            className="breadcrumb-link"
          >
            Home
          </button>
        </li>
        
        {breadcrumbs.map((crumb, index) => (
          <li key={crumb.path}>
            <span className="breadcrumb-separator" aria-hidden="true">
              {separator}
            </span>
            
            {crumb.isClickable && index < breadcrumbs.length - 1 ? (
              <button
                onClick={() => navigate(crumb.path)}
                className="breadcrumb-link"
              >
                {crumb.label}
              </button>
            ) : (
              <span 
                className="breadcrumb-current"
                aria-current={index === breadcrumbs.length - 1 ? "page" : undefined}
              >
                {crumb.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}

// Mega menu with keyboard navigation
function MegaMenu({ menuItems }) {
  const [activeMenu, setActiveMenu] = useState(null)
  const [focusedItem, setFocusedItem] = useState(null)
  const menuRef = useRef()

  const handleKeyDown = (event, menuId, itemIndex) => {
    switch (event.key) {
      case 'ArrowRight':
        event.preventDefault()
        const currentIndex = menuItems.findIndex(item => item.id === menuId)
        const nextIndex = (currentIndex + 1) % menuItems.length
        setActiveMenu(menuItems[nextIndex].id)
        setFocusedItem(null)
        break

      case 'ArrowLeft':
        event.preventDefault()
        const currentIdx = menuItems.findIndex(item => item.id === menuId)
        const prevIndex = currentIdx === 0 ? menuItems.length - 1 : currentIdx - 1
        setActiveMenu(menuItems[prevIndex].id)
        setFocusedItem(null)
        break

      case 'ArrowDown':
        event.preventDefault()
        if (activeMenu) {
          const menuItems = document.querySelectorAll(`[data-menu="${activeMenu}"] .menu-item`)
          const nextIndex = itemIndex !== null ? (itemIndex + 1) % menuItems.length : 0
          setFocusedItem(nextIndex)
          menuItems[nextIndex]?.focus()
        }
        break

      case 'ArrowUp':
        event.preventDefault()
        if (activeMenu) {
          const menuItems = document.querySelectorAll(`[data-menu="${activeMenu}"] .menu-item`)
          const prevIndex = itemIndex !== null 
            ? (itemIndex === 0 ? menuItems.length - 1 : itemIndex - 1)
            : menuItems.length - 1
          setFocusedItem(prevIndex)
          menuItems[prevIndex]?.focus()
        }
        break

      case 'Escape':
        setActiveMenu(null)
        setFocusedItem(null)
        break
    }
  }

  return (
    <nav ref={menuRef} className="mega-menu" role="menubar">
      {menuItems.map((menu) => (
        <div key={menu.id} className="menu-section">
          <button
            role="menuitem"
            aria-haspopup="true"
            aria-expanded={activeMenu === menu.id}
            onMouseEnter={() => setActiveMenu(menu.id)}
            onFocus={() => setActiveMenu(menu.id)}
            onKeyDown={(e) => handleKeyDown(e, menu.id)}
            className={`menu-trigger ${activeMenu === menu.id ? 'active' : ''}`}
          >
            {menu.title}
          </button>

          {activeMenu === menu.id && (
            <div
              data-menu={menu.id}
              className="mega-menu-panel"
              role="menu"
              onMouseLeave={() => setActiveMenu(null)}
            >
              {menu.sections.map((section, sectionIndex) => (
                <div key={sectionIndex} className="menu-section">
                  <h3 className="menu-section-title">{section.title}</h3>
                  <ul role="none">
                    {section.items.map((item, itemIndex) => (
                      <li key={item.id} role="none">
                        <a
                          href={item.href}
                          role="menuitem"
                          className="menu-item"
                          tabIndex={focusedItem === itemIndex ? 0 : -1}
                          onKeyDown={(e) => handleKeyDown(e, menu.id, itemIndex)}
                          onFocus={() => setFocusedItem(itemIndex)}
                        >
                          {item.title}
                          {item.description && (
                            <span className="menu-item-description">
                              {item.description}
                            </span>
                          )}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </nav>
  )
}
```

---

## Best Practices

### 1. Component Composition
- Use compound components for related UI elements
- Implement proper prop drilling alternatives
- Create flexible component APIs with render props
- Design components for maximum reusability
- Maintain consistent naming conventions

### 2. Accessibility First
- Implement proper ARIA attributes and roles
- Ensure keyboard navigation support
- Provide screen reader compatibility
- Handle focus management correctly
- Test with assistive technologies

### 3. Performance Considerations
- Use virtualization for large lists
- Implement proper memoization strategies
- Optimize component re-renders
- Handle async operations efficiently
- Monitor bundle size and runtime performance

### 4. User Experience
- Provide clear visual feedback
- Implement smooth transitions and animations
- Handle loading and error states gracefully
- Design for mobile and touch interactions
- Ensure consistent behavior across browsers

---

## Projects

### Project 1: Component Library
Build a comprehensive component library with:
- Accessible form components
- Navigation and layout components
- Data display components
- Interactive elements
- Documentation with Storybook

### Project 2: Admin Dashboard
Create a complex admin dashboard featuring:
- Advanced data tables with virtualization
- Multi-step form wizards
- Complex navigation patterns
- Real-time data updates
- Responsive design

### Project 3: E-learning Platform
Develop an e-learning platform with:
- Interactive course navigation
- Accessible media players
- Progress tracking components
- Assessment and quiz interfaces
- Mobile-optimized design

---

## Assessment Criteria

### Knowledge Check (40 points)
- Advanced component patterns and composition
- Accessibility implementation and ARIA usage
- Performance optimization techniques
- User interaction design principles
- Cross-browser compatibility considerations

### Practical Skills (40 points)
- Build complex, accessible UI components
- Implement efficient data visualization
- Create smooth user interactions
- Handle complex form scenarios
- Optimize component performance

### Project Quality (20 points)
- Component architecture and reusability
- Accessibility compliance and testing
- Performance benchmarks
- Code organization and documentation
- User experience quality

---

## Resources

### Essential Reading
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [React Patterns](https://reactpatterns.com/)
- [Inclusive Components](https://inclusive-components.design/)
- [A11y Project](https://a11yproject.com/)

### Advanced Resources
- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)
- [NVDA Screen Reader](https://www.nvaccess.org/download/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [React Virtual](https://github.com/tannerlinsley/react-virtual)

### Tools and Libraries
- React Hook Form
- React Virtual
- React Spring
- Reach UI
- React Aria
- Testing Library
- Storybook

---

## Next Steps
After completing this module, you'll be ready for Module 13: Testing, where you'll learn comprehensive testing strategies for React applications including unit testing, integration testing, and end-to-end testing.

The combination of advanced UI patterns with proper testing creates the foundation for building reliable, accessible, and maintainable React applications.
