# Compound Components & Advanced Patterns

## Table of Contents
1. [Compound Components Fundamentals](#compound-components-fundamentals)
2. [Context-Based Compound Components](#context-based-compound-components)
3. [Render Props Pattern](#render-props-pattern)
4. [Higher-Order Components (HOCs)](#higher-order-components-hocs)
5. [Component Composition Patterns](#component-composition-patterns)
6. [Polymorphic Components](#polymorphic-components)
7. [Factory Pattern](#factory-pattern)
8. [Best Practices & Performance](#best-practices--performance)

---

## Compound Components Fundamentals

### Basic Compound Component Implementation

```jsx
{% raw %}
import React, { createContext, useContext, useState, Children, cloneElement } from 'react'

// Context for sharing state between compound components
const AccordionContext = createContext()

// Main Accordion component
const Accordion = ({ children, allowMultiple = false, defaultOpenItems = [] }) => {
  const [openItems, setOpenItems] = useState(new Set(defaultOpenItems))
  
  const toggleItem = (index) => {
    setOpenItems(prev => {
      const newSet = new Set(prev)
      
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        if (!allowMultiple) {
          newSet.clear()
        }
        newSet.add(index)
      }
      
      return newSet
    })
  }
  
  const contextValue = {
    openItems,
    toggleItem,
    allowMultiple,
  }
  
  return (
    <AccordionContext.Provider value={contextValue}>
      <div className="accordion" role="tablist">
        {Children.map(children, (child, index) => 
          cloneElement(child, { index })
        )}
      </div>
    </AccordionContext.Provider>
  )
}

// AccordionItem component
const AccordionItem = ({ children, index, disabled = false }) => {
  const context = useContext(AccordionContext)
  
  if (!context) {
    throw new Error('AccordionItem must be used within Accordion')
  }
  
  const isOpen = context.openItems.has(index)
  
  return (
    <div 
      className={`accordion-item ${isOpen ? 'open' : ''} ${disabled ? 'disabled' : ''}`}
      data-index={index}
    >
      {Children.map(children, child => 
        cloneElement(child, { index, isOpen, disabled })
      )}
    </div>
  )
}

// AccordionTrigger component
const AccordionTrigger = ({ children, index, isOpen, disabled }) => {
  const { toggleItem } = useContext(AccordionContext)
  
  const handleClick = () => {
    if (!disabled) {
      toggleItem(index)
    }
  }
  
  const handleKeyDown = (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
      e.preventDefault()
      toggleItem(index)
    }
  }
  
  return (
    <button
      className="accordion-trigger"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      aria-expanded={isOpen}
      aria-controls={`accordion-content-${index}`}
      id={`accordion-trigger-${index}`}
      disabled={disabled}
      type="button"
      role="tab"
    >
      {children}
      <span className={`accordion-icon ${isOpen ? 'rotated' : ''}`}>
        ▼
      </span>
    </button>
  )
}

// AccordionContent component
const AccordionContent = ({ children, index, isOpen }) => {
  return (
    <div
      className={`accordion-content ${isOpen ? 'open' : ''}`}
      id={`accordion-content-${index}`}
      aria-labelledby={`accordion-trigger-${index}`}
      role="tabpanel"
    >
      <div className="accordion-content-inner">
        {children}
      </div>
    </div>
  )
}

// Attach sub-components to main component
Accordion.Item = AccordionItem
Accordion.Trigger = AccordionTrigger
Accordion.Content = AccordionContent

// Usage Example
const AccordionExample = () => {
  return (
    <Accordion allowMultiple defaultOpenItems={[0]}>
      <Accordion.Item>
        <Accordion.Trigger>
          What is React?
        </Accordion.Trigger>
        <Accordion.Content>
          React is a JavaScript library for building user interfaces.
        </Accordion.Content>
      </Accordion.Item>
      
      <Accordion.Item>
        <Accordion.Trigger>
          How do hooks work?
        </Accordion.Trigger>
        <Accordion.Content>
          Hooks allow you to use state and other React features in functional components.
        </Accordion.Content>
      </Accordion.Item>
      
      <Accordion.Item disabled>
        <Accordion.Trigger>
          What's new in React 18?
        </Accordion.Trigger>
        <Accordion.Content>
          This section is currently disabled.
        </Accordion.Content>
      </Accordion.Item>
    </Accordion>
  )
}
{% endraw %}
```

### Advanced Compound Component with Flexible API

```jsx
{% raw %}
// Flexible Tab component with multiple API patterns
const TabsContext = createContext()

const Tabs = ({ 
  children, 
  defaultValue, 
  value: controlledValue,
  onValueChange,
  orientation = 'horizontal',
  activationMode = 'automatic'
}) => {
  const [internalValue, setInternalValue] = useState(defaultValue)
  const isControlled = controlledValue !== undefined
  const value = isControlled ? controlledValue : internalValue
  
  const setValue = (newValue) => {
    if (!isControlled) {
      setInternalValue(newValue)
    }
    onValueChange?.(newValue)
  }
  
  const contextValue = {
    value,
    setValue,
    orientation,
    activationMode,
  }
  
  return (
    <TabsContext.Provider value={contextValue}>
      <div 
        className={`tabs tabs--${orientation}`}
        data-orientation={orientation}
      >
        {children}
      </div>
    </TabsContext.Provider>
  )
}

const TabsList = ({ children, className = '', ...props }) => {
  const { orientation } = useContext(TabsContext)
  
  return (
    <div
      className={`tabs-list ${className}`}
      role="tablist"
      aria-orientation={orientation}
      {...props}
    >
      {children}
    </div>
  )
}

const TabsTrigger = ({ 
  value: triggerValue, 
  children, 
  disabled = false,
  className = '',
  ...props 
}) => {
  const { value, setValue, activationMode } = useContext(TabsContext)
  const isSelected = value === triggerValue
  
  const handleClick = () => {
    if (!disabled) {
      setValue(triggerValue)
    }
  }
  
  const handleKeyDown = (e) => {
    if (disabled) return
    
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setValue(triggerValue)
    }
  }
  
  const handleFocus = () => {
    if (activationMode === 'automatic' && !disabled) {
      setValue(triggerValue)
    }
  }
  
  return (
    <button
      className={`tabs-trigger ${isSelected ? 'selected' : ''} ${className}`}
      role="tab"
      aria-selected={isSelected}
      aria-controls={`tabs-content-${triggerValue}`}
      id={`tabs-trigger-${triggerValue}`}
      tabIndex={isSelected ? 0 : -1}
      disabled={disabled}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      onFocus={handleFocus}
      {...props}
    >
      {children}
    </button>
  )
}

const TabsContent = ({ 
  value: contentValue, 
  children, 
  forceMount = false,
  className = '',
  ...props 
}) => {
  const { value } = useContext(TabsContext)
  const isSelected = value === contentValue
  
  if (!isSelected && !forceMount) {
    return null
  }
  
  return (
    <div
      className={`tabs-content ${isSelected ? 'selected' : ''} ${className}`}
      role="tabpanel"
      aria-labelledby={`tabs-trigger-${contentValue}`}
      id={`tabs-content-${contentValue}`}
      tabIndex={0}
      hidden={!isSelected}
      {...props}
    >
      {children}
    </div>
  )
}

// Attach sub-components
Tabs.List = TabsList
Tabs.Trigger = TabsTrigger
Tabs.Content = TabsContent

// Usage with controlled and uncontrolled modes
const TabsExample = () => {
  const [activeTab, setActiveTab] = useState('tab1')
  
  return (
    <div>
      {/* Uncontrolled */}
      <Tabs defaultValue="overview">
        <Tabs.List>
          <Tabs.Trigger value="overview">Overview</Tabs.Trigger>
          <Tabs.Trigger value="features">Features</Tabs.Trigger>
          <Tabs.Trigger value="pricing" disabled>Pricing</Tabs.Trigger>
        </Tabs.List>
        
        <Tabs.Content value="overview">
          Overview content here
        </Tabs.Content>
        <Tabs.Content value="features">
          Features content here
        </Tabs.Content>
        <Tabs.Content value="pricing">
          Pricing content here
        </Tabs.Content>
      </Tabs>
      
      {/* Controlled */}
      <Tabs 
        value={activeTab} 
        onValueChange={setActiveTab}
        orientation="vertical"
        activationMode="manual"
      >
        <Tabs.List>
          <Tabs.Trigger value="tab1">Tab 1</Tabs.Trigger>
          <Tabs.Trigger value="tab2">Tab 2</Tabs.Trigger>
        </Tabs.List>
        
        <Tabs.Content value="tab1">Content 1</Tabs.Content>
        <Tabs.Content value="tab2">Content 2</Tabs.Content>
      </Tabs>
    </div>
  )
}
{% endraw %}
```

---

## Context-Based Compound Components

### Provider Pattern with Multiple Contexts

```jsx
{% raw %}
// Multi-level context for complex component hierarchies
const FormContext = createContext()
const FieldContext = createContext()
const ValidationContext = createContext()

const Form = ({ children, onSubmit, initialValues = {}, validationSchema }) => {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const setValue = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }))
    
    // Clear error when value changes
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }
  
  const setError = (name, error) => {
    setErrors(prev => ({ ...prev, [name]: error }))
  }
  
  const setFieldTouched = (name, isTouched = true) => {
    setTouched(prev => ({ ...prev, [name]: isTouched }))
  }
  
  const validateField = async (name, value) => {
    if (!validationSchema) return null
    
    try {
      await validationSchema.validateAt(name, { [name]: value })
      return null
    } catch (error) {
      return error.message
    }
  }
  
  const validateForm = async () => {
    if (!validationSchema) return true
    
    try {
      await validationSchema.validate(values, { abortEarly: false })
      setErrors({})
      return true
    } catch (error) {
      const newErrors = {}
      error.inner.forEach(err => {
        newErrors[err.path] = err.message
      })
      setErrors(newErrors)
      return false
    }
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    const isValid = await validateForm()
    
    if (isValid) {
      try {
        await onSubmit?.(values)
      } catch (error) {
        console.error('Form submission error:', error)
      }
    }
    
    setIsSubmitting(false)
  }
  
  const formContextValue = {
    values,
    errors,
    touched,
    isSubmitting,
    setValue,
    setError,
    setFieldTouched,
    validateField,
    validateForm,
  }
  
  return (
    <FormContext.Provider value={formContextValue}>
      <form onSubmit={handleSubmit} noValidate>
        {children}
      </form>
    </FormContext.Provider>
  )
}

const FormField = ({ name, children }) => {
  const formContext = useContext(FormContext)
  
  if (!formContext) {
    throw new Error('FormField must be used within Form')
  }
  
  const fieldContextValue = {
    name,
    value: formContext.values[name],
    error: formContext.errors[name],
    touched: formContext.touched[name],
    setValue: (value) => formContext.setValue(name, value),
    setTouched: (touched) => formContext.setFieldTouched(name, touched),
    validateField: (value) => formContext.validateField(name, value),
  }
  
  return (
    <FieldContext.Provider value={fieldContextValue}>
      <div className={`form-field ${fieldContextValue.error ? 'error' : ''}`}>
        {children}
      </div>
    </FieldContext.Provider>
  )
}

const FormLabel = ({ children, required = false, ...props }) => {
  const { name } = useContext(FieldContext)
  
  return (
    <label htmlFor={name} className="form-label" {...props}>
      {children}
      {required && <span className="required-indicator">*</span>}
    </label>
  )
}

const FormInput = ({ 
  type = 'text', 
  placeholder,
  required = false,
  validateOnBlur = true,
  validateOnChange = false,
  ...props 
}) => {
  const { name, value, error, setValue, setTouched, validateField } = useContext(FieldContext)
  
  const handleChange = async (e) => {
    const newValue = e.target.value
    setValue(newValue)
    
    if (validateOnChange) {
      const fieldError = await validateField(newValue)
      if (fieldError) {
        // Set error through form context
      }
    }
  }
  
  const handleBlur = async () => {
    setTouched(true)
    
    if (validateOnBlur) {
      const fieldError = await validateField(value)
      if (fieldError) {
        // Set error through form context
      }
    }
  }
  
  return (
    <input
      id={name}
      name={name}
      type={type}
      value={value || ''}
      placeholder={placeholder}
      onChange={handleChange}
      onBlur={handleBlur}
      aria-invalid={error ? 'true' : 'false'}
      aria-describedby={error ? `${name}-error` : undefined}
      required={required}
      className={`form-input ${error ? 'error' : ''}`}
      {...props}
    />
  )
}

const FormError = ({ className = '' }) => {
  const { name, error, touched } = useContext(FieldContext)
  
  if (!error || !touched) return null
  
  return (
    <div 
      id={`${name}-error`}
      className={`form-error ${className}`}
      role="alert"
      aria-live="polite"
    >
      {error}
    </div>
  )
}

const FormSubmit = ({ children, ...props }) => {
  const { isSubmitting } = useContext(FormContext)
  
  return (
    <button
      type="submit"
      disabled={isSubmitting}
      className="form-submit"
      {...props}
    >
      {isSubmitting ? 'Submitting...' : children}
    </button>
  )
}

// Attach sub-components
Form.Field = FormField
Form.Label = FormLabel
Form.Input = FormInput
Form.Error = FormError
Form.Submit = FormSubmit

// Usage example
const FormExample = () => {
  const handleSubmit = async (values) => {
    console.log('Form submitted:', values)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
  
  return (
    <Form 
      onSubmit={handleSubmit}
      initialValues={{ email: '', password: '' }}
    >
      <Form.Field name="email">
        <Form.Label required>Email</Form.Label>
        <Form.Input 
          type="email" 
          placeholder="Enter your email"
          required
          validateOnChange
        />
        <Form.Error />
      </Form.Field>
      
      <Form.Field name="password">
        <Form.Label required>Password</Form.Label>
        <Form.Input 
          type="password" 
          placeholder="Enter your password"
          required
        />
        <Form.Error />
      </Form.Field>
      
      <Form.Submit>
        Sign In
      </Form.Submit>
    </Form>
  )
}
{% endraw %}
```

This comprehensive guide covers advanced compound components and composition patterns essential for building scalable React applications.