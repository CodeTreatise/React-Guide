# Component Testing Strategies

## Introduction to Component Testing

Component testing involves testing individual React components in isolation to ensure they render correctly, handle props appropriately, respond to user interactions, and manage state as expected. This level of testing provides confidence in your component's behavior while being fast and maintainable.

### Testing Philosophy

1. **Test from the user's perspective**: Focus on what users see and do
2. **Test behavior, not implementation**: Avoid testing internal details
3. **Test edge cases and error conditions**: Ensure robust component behavior
4. **Test accessibility**: Ensure components work for all users
5. **Test performance**: Verify components don't cause performance issues

## Component Testing Hierarchy

### 1. Smoke Tests
Basic tests that ensure components render without crashing.

```javascript
// components/Button.jsx
import React from 'react'

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  onClick,
  type = 'button',
  ...props 
}) => {
  const baseClasses = 'btn'
  const variantClass = `btn--${variant}`
  const sizeClass = `btn--${size}`
  
  return (
    <button
      type={type}
      className={`${baseClasses} ${variantClass} ${sizeClass}`}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button

// __tests__/Button.smoke.test.jsx
import React from 'react'
import { render } from '@testing-library/react'
import Button from '../components/Button'

describe('Button Smoke Tests', () => {
  test('renders without crashing', () => {
    render(<Button>Click me</Button>)
  })

  test('renders with all prop variants', () => {
    const variants = ['primary', 'secondary', 'danger']
    const sizes = ['small', 'medium', 'large']

    variants.forEach(variant => {
      sizes.forEach(size => {
        render(
          <Button variant={variant} size={size}>
            {variant} {size}
          </Button>
        )
      })
    })
  })

  test('renders with edge case props', () => {
    render(<Button disabled>Disabled</Button>)
    render(<Button type="submit">Submit</Button>)
    render(<Button onClick={() => {}}>With Handler</Button>)
  })
})
```

### 2. Snapshot Tests
Capture component output to detect unintended changes.

```javascript
// __tests__/Button.snapshot.test.jsx
import React from 'react'
import { render } from '@testing-library/react'
import Button from '../components/Button'

describe('Button Snapshot Tests', () => {
  test('matches snapshot for default props', () => {
    const { container } = render(<Button>Default Button</Button>)
    expect(container.firstChild).toMatchSnapshot()
  })

  test('matches snapshot for different variants', () => {
    const variants = ['primary', 'secondary', 'danger']
    
    variants.forEach(variant => {
      const { container } = render(
        <Button variant={variant}>{variant} Button</Button>
      )
      expect(container.firstChild).toMatchSnapshot(`button-${variant}`)
    })
  })

  test('matches snapshot for disabled state', () => {
    const { container } = render(<Button disabled>Disabled Button</Button>)
    expect(container.firstChild).toMatchSnapshot()
  })
})
```

### 3. Props Testing
Verify components handle props correctly.

```javascript
// __tests__/Button.props.test.jsx
import React from 'react'
import { render, screen } from '@testing-library/react'
import Button from '../components/Button'

describe('Button Props Tests', () => {
  test('renders children correctly', () => {
    render(<Button>Test Button</Button>)
    expect(screen.getByText('Test Button')).toBeInTheDocument()
  })

  test('applies correct CSS classes based on props', () => {
    render(<Button variant="danger" size="large">Danger Button</Button>)
    
    const button = screen.getByRole('button')
    expect(button).toHaveClass('btn', 'btn--danger', 'btn--large')
  })

  test('forwards type prop to button element', () => {
    render(<Button type="submit">Submit</Button>)
    
    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('type', 'submit')
  })

  test('forwards disabled prop correctly', () => {
    render(<Button disabled>Disabled</Button>)
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  test('forwards additional props', () => {
    render(
      <Button 
        data-testid="custom-button" 
        aria-label="Custom button"
        id="my-button"
      >
        Custom
      </Button>
    )
    
    const button = screen.getByTestId('custom-button')
    expect(button).toHaveAttribute('aria-label', 'Custom button')
    expect(button).toHaveAttribute('id', 'my-button')
  })

  test('uses default values when props not provided', () => {
    render(<Button>Default</Button>)
    
    const button = screen.getByRole('button')
    expect(button).toHaveClass('btn--primary', 'btn--medium')
    expect(button).toHaveAttribute('type', 'button')
    expect(button).not.toBeDisabled()
  })
})
```

### 4. Interaction Testing
Test user interactions and event handling.

```javascript
// __tests__/Button.interaction.test.jsx
import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Button from '../components/Button'

describe('Button Interaction Tests', () => {
  test('calls onClick when clicked', async () => {
    const user = userEvent.setup()
    const handleClick = jest.fn()
    
    render(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByRole('button')
    await user.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  test('does not call onClick when disabled', async () => {
    const user = userEvent.setup()
    const handleClick = jest.fn()
    
    render(<Button onClick={handleClick} disabled>Disabled</Button>)
    
    const button = screen.getByRole('button')
    await user.click(button)
    
    expect(handleClick).not.toHaveBeenCalled()
  })

  test('handles keyboard interactions', async () => {
    const user = userEvent.setup()
    const handleClick = jest.fn()
    
    render(<Button onClick={handleClick}>Keyboard</Button>)
    
    const button = screen.getByRole('button')
    button.focus()
    
    await user.keyboard('{Enter}')
    expect(handleClick).toHaveBeenCalledTimes(1)
    
    await user.keyboard(' ')
    expect(handleClick).toHaveBeenCalledTimes(2)
  })

  test('prevents double clicks', async () => {
    const user = userEvent.setup()
    const handleClick = jest.fn()
    
    render(<Button onClick={handleClick}>Double Click</Button>)
    
    const button = screen.getByRole('button')
    
    // Rapid clicks
    await user.dblClick(button)
    
    // Should only be called twice (once per click)
    expect(handleClick).toHaveBeenCalledTimes(2)
  })
})
```

## Testing Complex Components

### Form Components

```javascript
// components/LoginForm.jsx
import React, { useState } from 'react'
import Button from './Button'

const LoginForm = ({ onSubmit, onForgotPassword, loading = false }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  })
  const [errors, setErrors] = useState({})

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validateForm()) {
      onSubmit(formData)
    }
  }

  const handleChange = (field) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div className="form-group">
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={handleChange('email')}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
          disabled={loading}
        />
        {errors.email && (
          <div id="email-error" role="alert" className="error">
            {errors.email}
          </div>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="password">Password *</label>
        <input
          id="password"
          type="password"
          value={formData.password}
          onChange={handleChange('password')}
          aria-invalid={!!errors.password}
          aria-describedby={errors.password ? 'password-error' : undefined}
          disabled={loading}
        />
        {errors.password && (
          <div id="password-error" role="alert" className="error">
            {errors.password}
          </div>
        )}
      </div>

      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={formData.rememberMe}
            onChange={handleChange('rememberMe')}
            disabled={loading}
          />
          Remember me
        </label>
      </div>

      <div className="form-actions">
        <Button type="submit" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </Button>
        
        <button 
          type="button" 
          className="link-button"
          onClick={onForgotPassword}
          disabled={loading}
        >
          Forgot password?
        </button>
      </div>
    </form>
  )
}

export default LoginForm

// __tests__/LoginForm.test.jsx
import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginForm from '../components/LoginForm'

describe('LoginForm', () => {
  const defaultProps = {
    onSubmit: jest.fn(),
    onForgotPassword: jest.fn()
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    test('renders all form fields', () => {
      render(<LoginForm {...defaultProps} />)
      
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/remember me/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /forgot password/i })).toBeInTheDocument()
    })

    test('shows loading state correctly', () => {
      render(<LoginForm {...defaultProps} loading={true} />)
      
      expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeDisabled()
      expect(screen.getByLabelText(/password/i)).toBeDisabled()
      expect(screen.getByLabelText(/remember me/i)).toBeDisabled()
    })
  })

  describe('Form Validation', () => {
    test('shows validation errors for empty fields', async () => {
      const user = userEvent.setup()
      render(<LoginForm {...defaultProps} />)
      
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      await user.click(submitButton)
      
      expect(screen.getByText('Email is required')).toBeInTheDocument()
      expect(screen.getByText('Password is required')).toBeInTheDocument()
      expect(defaultProps.onSubmit).not.toHaveBeenCalled()
    })

    test('validates email format', async () => {
      const user = userEvent.setup()
      render(<LoginForm {...defaultProps} />)
      
      await user.type(screen.getByLabelText(/email/i), 'invalid-email')
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      expect(screen.getByText('Email is invalid')).toBeInTheDocument()
    })

    test('validates password length', async () => {
      const user = userEvent.setup()
      render(<LoginForm {...defaultProps} />)
      
      await user.type(screen.getByLabelText(/password/i), '12345')
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument()
    })

    test('clears errors when user starts typing', async () => {
      const user = userEvent.setup()
      render(<LoginForm {...defaultProps} />)
      
      // Submit to show errors
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      expect(screen.getByText('Email is required')).toBeInTheDocument()
      
      // Start typing
      await user.type(screen.getByLabelText(/email/i), 'a')
      
      // Error should be cleared
      expect(screen.queryByText('Email is required')).not.toBeInTheDocument()
    })
  })

  describe('Form Submission', () => {
    test('submits valid form data', async () => {
      const user = userEvent.setup()
      render(<LoginForm {...defaultProps} />)
      
      await user.type(screen.getByLabelText(/email/i), 'test@example.com')
      await user.type(screen.getByLabelText(/password/i), 'password123')
      await user.click(screen.getByLabelText(/remember me/i))
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      expect(defaultProps.onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        rememberMe: true
      })
    })

    test('handles forgot password click', async () => {
      const user = userEvent.setup()
      render(<LoginForm {...defaultProps} />)
      
      await user.click(screen.getByRole('button', { name: /forgot password/i }))
      
      expect(defaultProps.onForgotPassword).toHaveBeenCalledTimes(1)
    })
  })

  describe('Accessibility', () => {
    test('has proper form labels', () => {
      render(<LoginForm {...defaultProps} />)
      
      expect(screen.getByLabelText(/email/i)).toHaveAttribute('id', 'email')
      expect(screen.getByLabelText(/password/i)).toHaveAttribute('id', 'password')
    })

    test('associates errors with form fields', async () => {
      const user = userEvent.setup()
      render(<LoginForm {...defaultProps} />)
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      const emailInput = screen.getByLabelText(/email/i)
      expect(emailInput).toHaveAttribute('aria-invalid', 'true')
      expect(emailInput).toHaveAttribute('aria-describedby', 'email-error')
      
      const errorElement = screen.getByRole('alert', { name: /email is required/i })
      expect(errorElement).toHaveAttribute('id', 'email-error')
    })
  })
})
```

### Modal Components

```javascript
// components/Modal.jsx
import React, { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import Button from './Button'

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'medium',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true 
}) => {
  const modalRef = useRef()
  const previousFocusRef = useRef()

  useEffect(() => {
    if (isOpen) {
      // Store previously focused element
      previousFocusRef.current = document.activeElement
      
      // Focus the modal
      modalRef.current?.focus()
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden'
      
      return () => {
        document.body.style.overflow = 'unset'
        // Restore focus to previously focused element
        previousFocusRef.current?.focus()
      }
    }
  }, [isOpen])

  useEffect(() => {
    if (!closeOnEscape) return

    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose, closeOnEscape])

  // Trap focus within modal
  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      
      if (!focusableElements?.length) return
      
      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]
      
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }
  }

  const handleOverlayClick = (e) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose()
    }
  }

  if (!isOpen) return null

  return createPortal(
    <div 
      className="modal-overlay" 
      onClick={handleOverlayClick}
      role="presentation"
    >
      <div
        ref={modalRef}
        className={`modal modal--${size}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
        tabIndex={-1}
        onKeyDown={handleKeyDown}
      >
        {title && (
          <div className="modal-header">
            <h2 id="modal-title" className="modal-title">
              {title}
            </h2>
            {showCloseButton && (
              <Button 
                variant="ghost" 
                size="small"
                onClick={onClose}
                aria-label="Close modal"
              >
                ×
              </Button>
            )}
          </div>
        )}
        
        <div className="modal-content">
          {children}
        </div>
      </div>
    </div>,
    document.body
  )
}

export default Modal

// __tests__/Modal.test.jsx
import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Modal from '../components/Modal'

describe('Modal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    title: 'Test Modal',
    children: <div>Modal content</div>
  }

  beforeEach(() => {
    jest.clearAllMocks()
    // Clear any existing modals
    document.body.innerHTML = ''
  })

  describe('Rendering', () => {
    test('renders modal when open', () => {
      render(<Modal {...defaultProps} />)
      
      expect(screen.getByRole('dialog')).toBeInTheDocument()
      expect(screen.getByText('Test Modal')).toBeInTheDocument()
      expect(screen.getByText('Modal content')).toBeInTheDocument()
    })

    test('does not render when closed', () => {
      render(<Modal {...defaultProps} isOpen={false} />)
      
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    test('renders without title', () => {
      render(<Modal {...defaultProps} title={undefined} />)
      
      expect(screen.getByRole('dialog')).toBeInTheDocument()
      expect(screen.queryByText('Test Modal')).not.toBeInTheDocument()
    })

    test('applies size classes correctly', () => {
      render(<Modal {...defaultProps} size="large" />)
      
      const modal = screen.getByRole('dialog')
      expect(modal).toHaveClass('modal--large')
    })

    test('shows close button by default', () => {
      render(<Modal {...defaultProps} />)
      
      expect(screen.getByLabelText('Close modal')).toBeInTheDocument()
    })

    test('hides close button when configured', () => {
      render(<Modal {...defaultProps} showCloseButton={false} />)
      
      expect(screen.queryByLabelText('Close modal')).not.toBeInTheDocument()
    })
  })

  describe('Interaction', () => {
    test('calls onClose when close button clicked', async () => {
      const user = userEvent.setup()
      render(<Modal {...defaultProps} />)
      
      await user.click(screen.getByLabelText('Close modal'))
      
      expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
    })

    test('calls onClose when escape key pressed', async () => {
      const user = userEvent.setup()
      render(<Modal {...defaultProps} />)
      
      await user.keyboard('{Escape}')
      
      expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
    })

    test('does not close on escape when disabled', async () => {
      const user = userEvent.setup()
      render(<Modal {...defaultProps} closeOnEscape={false} />)
      
      await user.keyboard('{Escape}')
      
      expect(defaultProps.onClose).not.toHaveBeenCalled()
    })

    test('calls onClose when overlay clicked', async () => {
      const user = userEvent.setup()
      render(<Modal {...defaultProps} />)
      
      const overlay = screen.getByRole('presentation')
      await user.click(overlay)
      
      expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
    })

    test('does not close when modal content clicked', async () => {
      const user = userEvent.setup()
      render(<Modal {...defaultProps} />)
      
      await user.click(screen.getByRole('dialog'))
      
      expect(defaultProps.onClose).not.toHaveBeenCalled()
    })

    test('does not close on overlay click when disabled', async () => {
      const user = userEvent.setup()
      render(<Modal {...defaultProps} closeOnOverlayClick={false} />)
      
      const overlay = screen.getByRole('presentation')
      await user.click(overlay)
      
      expect(defaultProps.onClose).not.toHaveBeenCalled()
    })
  })

  describe('Focus Management', () => {
    test('focuses modal when opened', () => {
      render(<Modal {...defaultProps} />)
      
      const modal = screen.getByRole('dialog')
      expect(modal).toHaveFocus()
    })

    test('traps focus within modal', async () => {
      const user = userEvent.setup()
      render(
        <Modal {...defaultProps}>
          <button>First</button>
          <button>Second</button>
          <button>Last</button>
        </Modal>
      )
      
      const firstButton = screen.getByText('First')
      const lastButton = screen.getByText('Last')
      
      // Focus first button
      firstButton.focus()
      
      // Shift+Tab should go to last button
      await user.keyboard('{Shift>}{Tab}{/Shift}')
      expect(lastButton).toHaveFocus()
      
      // Tab should go to first button
      await user.keyboard('{Tab}')
      expect(firstButton).toHaveFocus()
    })

    test('restores focus when closed', () => {
      const button = document.createElement('button')
      document.body.appendChild(button)
      button.focus()
      
      const { rerender } = render(<Modal {...defaultProps} />)
      
      // Modal should be focused
      expect(screen.getByRole('dialog')).toHaveFocus()
      
      // Close modal
      rerender(<Modal {...defaultProps} isOpen={false} />)
      
      // Focus should be restored
      expect(button).toHaveFocus()
      
      document.body.removeChild(button)
    })
  })

  describe('Accessibility', () => {
    test('has proper ARIA attributes', () => {
      render(<Modal {...defaultProps} />)
      
      const modal = screen.getByRole('dialog')
      expect(modal).toHaveAttribute('aria-modal', 'true')
      expect(modal).toHaveAttribute('aria-labelledby', 'modal-title')
      expect(modal).toHaveAttribute('tabindex', '-1')
    })

    test('does not have aria-labelledby when no title', () => {
      render(<Modal {...defaultProps} title={undefined} />)
      
      const modal = screen.getByRole('dialog')
      expect(modal).not.toHaveAttribute('aria-labelledby')
    })
  })

  describe('Body Scroll Prevention', () => {
    test('prevents body scroll when open', () => {
      render(<Modal {...defaultProps} />)
      
      expect(document.body.style.overflow).toBe('hidden')
    })

    test('restores body scroll when closed', () => {
      const { rerender } = render(<Modal {...defaultProps} />)
      
      expect(document.body.style.overflow).toBe('hidden')
      
      rerender(<Modal {...defaultProps} isOpen={false} />)
      
      expect(document.body.style.overflow).toBe('unset')
    })
  })
})
```

## Testing Component State Management

```javascript
// components/Counter.jsx
import React, { useState, useCallback } from 'react'
import Button from './Button'

const Counter = ({ 
  initialValue = 0, 
  min = -Infinity, 
  max = Infinity, 
  step = 1,
  onValueChange 
}) => {
  const [count, setCount] = useState(initialValue)

  const increment = useCallback(() => {
    setCount(prev => {
      const newValue = Math.min(prev + step, max)
      onValueChange?.(newValue)
      return newValue
    })
  }, [step, max, onValueChange])

  const decrement = useCallback(() => {
    setCount(prev => {
      const newValue = Math.max(prev - step, min)
      onValueChange?.(newValue)
      return newValue
    })
  }, [step, min, onValueChange])

  const reset = useCallback(() => {
    setCount(initialValue)
    onValueChange?.(initialValue)
  }, [initialValue, onValueChange])

  const handleInputChange = (e) => {
    const value = parseInt(e.target.value, 10)
    if (!isNaN(value)) {
      const clampedValue = Math.min(Math.max(value, min), max)
      setCount(clampedValue)
      onValueChange?.(clampedValue)
    }
  }

  const canIncrement = count < max
  const canDecrement = count > min

  return (
    <div className="counter">
      <div className="counter-display">
        <Button 
          onClick={decrement} 
          disabled={!canDecrement}
          aria-label="Decrease count"
        >
          -
        </Button>
        
        <input
          type="number"
          value={count}
          onChange={handleInputChange}
          min={min}
          max={max}
          aria-label="Counter value"
        />
        
        <Button 
          onClick={increment} 
          disabled={!canIncrement}
          aria-label="Increase count"
        >
          +
        </Button>
      </div>
      
      <Button onClick={reset} variant="secondary" size="small">
        Reset
      </Button>
      
      <div className="counter-info">
        <span>Min: {min === -Infinity ? 'None' : min}</span>
        <span>Max: {max === Infinity ? 'None' : max}</span>
        <span>Step: {step}</span>
      </div>
    </div>
  )
}

export default Counter

// __tests__/Counter.test.jsx
import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Counter from '../components/Counter'

describe('Counter', () => {
  const defaultProps = {
    onValueChange: jest.fn()
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Initial State', () => {
    test('renders with default initial value', () => {
      render(<Counter {...defaultProps} />)
      
      expect(screen.getByDisplayValue('0')).toBeInTheDocument()
    })

    test('renders with custom initial value', () => {
      render(<Counter {...defaultProps} initialValue={5} />)
      
      expect(screen.getByDisplayValue('5')).toBeInTheDocument()
    })

    test('displays constraint information', () => {
      render(<Counter {...defaultProps} min={0} max={10} step={2} />)
      
      expect(screen.getByText('Min: 0')).toBeInTheDocument()
      expect(screen.getByText('Max: 10')).toBeInTheDocument()
      expect(screen.getByText('Step: 2')).toBeInTheDocument()
    })
  })

  describe('Increment/Decrement', () => {
    test('increments value when plus button clicked', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} />)
      
      const incrementButton = screen.getByLabelText('Increase count')
      await user.click(incrementButton)
      
      expect(screen.getByDisplayValue('1')).toBeInTheDocument()
      expect(defaultProps.onValueChange).toHaveBeenCalledWith(1)
    })

    test('decrements value when minus button clicked', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} initialValue={1} />)
      
      const decrementButton = screen.getByLabelText('Decrease count')
      await user.click(decrementButton)
      
      expect(screen.getByDisplayValue('0')).toBeInTheDocument()
      expect(defaultProps.onValueChange).toHaveBeenCalledWith(0)
    })

    test('respects custom step value', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} step={5} />)
      
      const incrementButton = screen.getByLabelText('Increase count')
      await user.click(incrementButton)
      
      expect(screen.getByDisplayValue('5')).toBeInTheDocument()
    })

    test('respects maximum constraint', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} initialValue={9} max={10} />)
      
      const incrementButton = screen.getByLabelText('Increase count')
      await user.click(incrementButton)
      
      expect(screen.getByDisplayValue('10')).toBeInTheDocument()
      
      // Button should be disabled at max
      expect(incrementButton).toBeDisabled()
      
      // Try to increment beyond max
      await user.click(incrementButton)
      expect(screen.getByDisplayValue('10')).toBeInTheDocument()
    })

    test('respects minimum constraint', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} initialValue={1} min={0} />)
      
      const decrementButton = screen.getByLabelText('Decrease count')
      await user.click(decrementButton)
      
      expect(screen.getByDisplayValue('0')).toBeInTheDocument()
      
      // Button should be disabled at min
      expect(decrementButton).toBeDisabled()
      
      // Try to decrement beyond min
      await user.click(decrementButton)
      expect(screen.getByDisplayValue('0')).toBeInTheDocument()
    })
  })

  describe('Direct Input', () => {
    test('updates value when input changed', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} />)
      
      const input = screen.getByLabelText('Counter value')
      await user.clear(input)
      await user.type(input, '42')
      
      expect(screen.getByDisplayValue('42')).toBeInTheDocument()
      expect(defaultProps.onValueChange).toHaveBeenCalledWith(42)
    })

    test('clamps input value to constraints', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} min={0} max={10} />)
      
      const input = screen.getByLabelText('Counter value')
      
      // Test value above max
      await user.clear(input)
      await user.type(input, '15')
      expect(screen.getByDisplayValue('10')).toBeInTheDocument()
      
      // Test value below min
      await user.clear(input)
      await user.type(input, '-5')
      expect(screen.getByDisplayValue('0')).toBeInTheDocument()
    })

    test('ignores invalid input', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} initialValue={5} />)
      
      const input = screen.getByLabelText('Counter value')
      await user.clear(input)
      await user.type(input, 'abc')
      
      // Should keep previous value
      expect(screen.getByDisplayValue('5')).toBeInTheDocument()
    })
  })

  describe('Reset Functionality', () => {
    test('resets to initial value', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} initialValue={0} />)
      
      // Change the value
      const incrementButton = screen.getByLabelText('Increase count')
      await user.click(incrementButton)
      await user.click(incrementButton)
      expect(screen.getByDisplayValue('2')).toBeInTheDocument()
      
      // Reset
      const resetButton = screen.getByText('Reset')
      await user.click(resetButton)
      
      expect(screen.getByDisplayValue('0')).toBeInTheDocument()
      expect(defaultProps.onValueChange).toHaveBeenCalledWith(0)
    })
  })

  describe('Callback Behavior', () => {
    test('does not crash when onValueChange not provided', async () => {
      const user = userEvent.setup()
      render(<Counter />)
      
      const incrementButton = screen.getByLabelText('Increase count')
      await user.click(incrementButton)
      
      expect(screen.getByDisplayValue('1')).toBeInTheDocument()
    })

    test('calls onValueChange for all value changes', async () => {
      const user = userEvent.setup()
      render(<Counter {...defaultProps} />)
      
      // Test increment
      await user.click(screen.getByLabelText('Increase count'))
      expect(defaultProps.onValueChange).toHaveBeenCalledWith(1)
      
      // Test decrement
      await user.click(screen.getByLabelText('Decrease count'))
      expect(defaultProps.onValueChange).toHaveBeenCalledWith(0)
      
      // Test reset
      await user.click(screen.getByText('Reset'))
      expect(defaultProps.onValueChange).toHaveBeenCalledWith(0)
      
      expect(defaultProps.onValueChange).toHaveBeenCalledTimes(3)
    })
  })
})
```

## Testing Error Boundaries

```javascript
// components/ErrorBoundary.jsx
import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null 
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    
    // Log error to monitoring service
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.state.errorInfo)
      }
      
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          {this.props.showDetails && (
            <details>
              <summary>Error details</summary>
              <pre>{this.state.error?.toString()}</pre>
              <pre>{this.state.errorInfo?.componentStack}</pre>
            </details>
          )}
          {this.props.onRetry && (
            <button onClick={() => {
              this.setState({ hasError: false, error: null, errorInfo: null })
              this.props.onRetry()
            }}>
              Try again
            </button>
          )}
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary

// __tests__/ErrorBoundary.test.jsx
import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ErrorBoundary from '../components/ErrorBoundary'

// Component that throws an error
const ThrowError = ({ shouldThrow, message = 'Test error' }) => {
  if (shouldThrow) {
    throw new Error(message)
  }
  return <div>No error here</div>
}

describe('ErrorBoundary', () => {
  // Suppress console.error for clean test output
  const originalError = console.error
  beforeAll(() => {
    console.error = jest.fn()
  })

  afterAll(() => {
    console.error = originalError
  })

  beforeEach(() => {
    console.error.mockClear()
  })

  test('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    )

    expect(screen.getByText('No error here')).toBeInTheDocument()
  })

  test('catches and displays error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(console.error).toHaveBeenCalled()
  })

  test('shows error details when enabled', () => {
    render(
      <ErrorBoundary showDetails={true}>
        <ThrowError shouldThrow={true} message="Custom error" />
      </ErrorBoundary>
    )

    expect(screen.getByText('Error details')).toBeInTheDocument()
    expect(screen.getByText(/Custom error/)).toBeInTheDocument()
  })

  test('calls onError callback', () => {
    const onError = jest.fn()
    
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String)
      })
    )
  })

  test('renders custom fallback', () => {
    const fallback = (error) => (
      <div>Custom error: {error.message}</div>
    )
    
    render(
      <ErrorBoundary fallback={fallback}>
        <ThrowError shouldThrow={true} message="Fallback test" />
      </ErrorBoundary>
    )

    expect(screen.getByText('Custom error: Fallback test')).toBeInTheDocument()
  })

  test('retries when retry button clicked', async () => {
    const user = userEvent.setup()
    const onRetry = jest.fn()
    
    const TestComponent = () => {
      const [shouldThrow, setShouldThrow] = React.useState(true)
      
      React.useEffect(() => {
        if (onRetry.mock.calls.length > 0) {
          setShouldThrow(false)
        }
      }, [onRetry.mock.calls.length])
      
      return <ThrowError shouldThrow={shouldThrow} />
    }
    
    render(
      <ErrorBoundary onRetry={onRetry}>
        <TestComponent />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    
    const retryButton = screen.getByText('Try again')
    await user.click(retryButton)
    
    expect(onRetry).toHaveBeenCalledTimes(1)
    expect(screen.getByText('No error here')).toBeInTheDocument()
  })
})
```

## Performance Testing Strategies

```javascript
// __tests__/performance.test.jsx
import React from 'react'
import { render, screen } from '@testing-library/react'
import { performance } from 'perf_hooks'

// Mock component with performance concerns
const ExpensiveList = ({ items, renderItem }) => {
  // Simulate expensive computation
  const processedItems = items.map(item => ({
    ...item,
    processed: true,
    timestamp: Date.now()
  }))

  return (
    <ul>
      {processedItems.map(renderItem)}
    </ul>
  )
}

const OptimizedList = React.memo(({ items, renderItem }) => {
  const processedItems = React.useMemo(() => 
    items.map(item => ({
      ...item,
      processed: true,
      timestamp: Date.now()
    })), [items]
  )

  return (
    <ul>
      {processedItems.map(renderItem)}
    </ul>
  )
})

describe('Performance Tests', () => {
  const generateItems = (count) => 
    Array.from({ length: count }, (_, i) => ({
      id: i,
      name: `Item ${i}`
    }))

  const renderItem = (item) => (
    <li key={item.id}>{item.name}</li>
  )

  test('measures render performance', () => {
    const items = generateItems(1000)
    
    const start = performance.now()
    render(<ExpensiveList items={items} renderItem={renderItem} />)
    const end = performance.now()
    
    const renderTime = end - start
    console.log(`Render time: ${renderTime}ms`)
    
    // Performance threshold (adjust based on requirements)
    expect(renderTime).toBeLessThan(100)
  })

  test('optimized component performs better', () => {
    const items = generateItems(1000)
    
    // Test unoptimized component
    const start1 = performance.now()
    const { rerender } = render(
      <ExpensiveList items={items} renderItem={renderItem} />
    )
    const end1 = performance.now()
    
    // Re-render with same props
    const start2 = performance.now()
    rerender(<ExpensiveList items={items} renderItem={renderItem} />)
    const end2 = performance.now()
    
    const unoptimizedRerender = end2 - start2
    
    // Test optimized component
    const start3 = performance.now()
    const { rerender: rerender2 } = render(
      <OptimizedList items={items} renderItem={renderItem} />
    )
    const end3 = performance.now()
    
    // Re-render with same props
    const start4 = performance.now()
    rerender2(<OptimizedList items={items} renderItem={renderItem} />)
    const end4 = performance.now()
    
    const optimizedRerender = end4 - start4
    
    // Optimized should be faster (or at least not significantly slower)
    expect(optimizedRerender).toBeLessThanOrEqual(unoptimizedRerender * 1.1)
  })

  test('tracks render count for memo components', () => {
    let renderCount = 0
    
    const TrackedComponent = React.memo(({ value }) => {
      renderCount++
      return <div>{value}</div>
    })

    const { rerender } = render(<TrackedComponent value="test" />)
    expect(renderCount).toBe(1)
    
    // Re-render with same props - should not re-render
    rerender(<TrackedComponent value="test" />)
    expect(renderCount).toBe(1)
    
    // Re-render with different props - should re-render
    rerender(<TrackedComponent value="different" />)
    expect(renderCount).toBe(2)
  })
})
```

## Test Organization Best Practices

```javascript
// Example of well-organized test structure
describe('UserProfile Component', () => {
  // Setup and utilities
  const mockUser = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    avatar: 'avatar.jpg'
  }

  const defaultProps = {
    user: mockUser,
    onEdit: jest.fn(),
    onDelete: jest.fn()
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  // Group tests by functionality
  describe('Rendering', () => {
    test('renders user information', () => {})
    test('renders avatar when provided', () => {})
    test('renders placeholder when no avatar', () => {})
  })

  describe('User Interactions', () => {
    test('calls onEdit when edit button clicked', () => {})
    test('calls onDelete when delete button clicked', () => {})
    test('shows confirmation before delete', () => {})
  })

  describe('Loading States', () => {
    test('shows loading spinner while saving', () => {})
    test('disables buttons during save', () => {})
  })

  describe('Error Handling', () => {
    test('displays error message on save failure', () => {})
    test('handles missing user data gracefully', () => {})
  })

  describe('Accessibility', () => {
    test('has proper ARIA labels', () => {})
    test('supports keyboard navigation', () => {})
    test('passes accessibility audit', () => {})
  })

  describe('Edge Cases', () => {
    test('handles very long names', () => {})
    test('handles special characters in email', () => {})
  })
})
```

## Conclusion

Effective component testing strategies involve:

**Testing Pyramid:**
- Smoke tests for basic rendering
- Props testing for configuration
- Interaction testing for user behavior
- State testing for internal logic
- Error boundary testing for resilience

**Best Practices:**
- Test behavior, not implementation
- Use descriptive test names
- Group related tests logically
- Mock external dependencies
- Test accessibility compliance
- Measure and optimize performance
- Handle edge cases and error conditions

**Key Benefits:**
- Confidence in component reliability
- Prevention of regressions
- Documentation of expected behavior
- Improved code quality
- Faster debugging and maintenance

Component testing is essential for building robust, maintainable React applications that provide excellent user experiences across all scenarios.
