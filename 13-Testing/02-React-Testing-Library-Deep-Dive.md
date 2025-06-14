# React Testing Library Deep Dive

## Introduction to React Testing Library

React Testing Library (RTL) is a testing utility that focuses on testing components from the user's perspective. It encourages testing behavior rather than implementation details, leading to more maintainable and meaningful tests.

### Core Philosophy

1. **Test behavior, not implementation**: Focus on what the user sees and does
2. **Accessibility-first**: Use queries that mirror how users interact with your app
3. **Simple and maintainable**: Write tests that don't break when you refactor
4. **Confidence in user experience**: Ensure your app works as users expect

## Setting Up React Testing Library

```bash
# Install React Testing Library (included with Create React App)
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event

# For custom setup
npm install --save-dev @testing-library/react-hooks
```

### Configuration

```javascript
// src/setupTests.js
import '@testing-library/jest-dom'

// Configure testing library
import { configure } from '@testing-library/react'

configure({
  testIdAttribute: 'data-testid', // Default
  asyncUtilTimeout: 5000, // Default is 1000ms
  getElementError: (message, container) => {
    const error = new Error(message)
    error.name = 'TestingLibraryElementError'
    error.stack = null
    return error
  }
})
```

## Queries and Best Practices

### Query Priority

React Testing Library provides different query methods with a recommended priority:

```javascript
import { render, screen } from '@testing-library/react'

const MyComponent = () => (
  <div>
    <h1>Welcome</h1>
    <button type="submit">Submit</button>
    <input placeholder="Enter name" />
    <img src="logo.png" alt="Company logo" />
    <label htmlFor="email">Email</label>
    <input id="email" />
    <span title="Helper text">Help</span>
    <div data-testid="custom-element">Custom</div>
  </div>
)

describe('Query Priority Examples', () => {
  beforeEach(() => {
    render(<MyComponent />)
  })

  test('1. getByRole - Most preferred', () => {
    // Accessible to everyone
    expect(screen.getByRole('heading', { name: 'Welcome' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Enter name' })).toBeInTheDocument()
    expect(screen.getByRole('img', { name: 'Company logo' })).toBeInTheDocument()
  })

  test('2. getByLabelText - Form elements', () => {
    // Accessible to screen readers
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
  })

  test('3. getByPlaceholderText - When no label exists', () => {
    expect(screen.getByPlaceholderText('Enter name')).toBeInTheDocument()
  })

  test('4. getByText - For non-interactive elements', () => {
    expect(screen.getByText('Welcome')).toBeInTheDocument()
  })

  test('5. getByDisplayValue - For form elements with values', () => {
    const input = screen.getByRole('textbox', { name: 'Email' })
    input.value = 'test@example.com'
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument()
  })

  test('6. getByAltText - For images', () => {
    expect(screen.getByAltText('Company logo')).toBeInTheDocument()
  })

  test('7. getByTitle - For elements with title attribute', () => {
    expect(screen.getByTitle('Helper text')).toBeInTheDocument()
  })

  test('8. getByTestId - Last resort', () => {
    // Use sparingly, prefer semantic queries
    expect(screen.getByTestId('custom-element')).toBeInTheDocument()
  })
})
```

### Query Variants

```javascript
// Query variants and their use cases
describe('Query Variants', () => {
  test('getBy* - Element must exist (throws if not found)', () => {
    render(<button>Click me</button>)
    
    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
    
    // This would throw an error:
    // screen.getByRole('textbox') // Error: Unable to find role="textbox"
  })

  test('queryBy* - Element may not exist (returns null)', () => {
    render(<button>Click me</button>)
    
    const button = screen.queryByRole('button')
    expect(button).toBeInTheDocument()
    
    const textbox = screen.queryByRole('textbox')
    expect(textbox).not.toBeInTheDocument() // null
  })

  test('findBy* - Element will appear (async, returns Promise)', async () => {
    const AsyncComponent = () => {
      const [show, setShow] = useState(false)
      
      useEffect(() => {
        setTimeout(() => setShow(true), 100)
      }, [])
      
      return show ? <div>Loaded</div> : <div>Loading...</div>
    }
    
    render(<AsyncComponent />)
    
    // Initially loading
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    
    // Wait for async content
    const loadedElement = await screen.findByText('Loaded')
    expect(loadedElement).toBeInTheDocument()
  })

  test('getAllBy* - Multiple elements', () => {
    render(
      <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
      </ul>
    )
    
    const items = screen.getAllByRole('listitem')
    expect(items).toHaveLength(3)
  })
})
```

## Testing Component Rendering

```javascript
{% raw %}
{% raw %}
// components/UserCard.jsx
import React from 'react'

const UserCard = ({ user, onEdit, onDelete, isEditing = false }) => {
  if (!user) {
    return <div>No user data available</div>
  }

  return (
    <div className="user-card">
      <img src={user.avatar} alt={`${user.name}'s avatar`} />
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <p>Role: {user.role}</p>
      
      {user.isActive ? (
        <span className="status active">Active</span>
      ) : (
        <span className="status inactive">Inactive</span>
      )}
      
      <div className="actions">
        <button onClick={() => onEdit(user.id)} disabled={isEditing}>
          {isEditing ? 'Editing...' : 'Edit'}
        </button>
        <button 
          onClick={() => onDelete(user.id)} 
          className="delete-button"
        >
          Delete
        </button>
      </div>
    </div>
  )
}

// __tests__/UserCard.test.jsx
import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UserCard from '../components/UserCard'

describe('UserCard', () => {
  const mockUser = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Admin',
    avatar: 'https://example.com/avatar.jpg',
    isActive: true
  }

  const mockProps = {
    user: mockUser,
    onEdit: jest.fn(),
    onDelete: jest.fn()
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders user information correctly', () => {
    render(<UserCard {...mockProps} />)
    
    // Check if all user information is displayed
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('john@example.com')).toBeInTheDocument()
    expect(screen.getByText('Role: Admin')).toBeInTheDocument()
    
    // Check avatar
    const avatar = screen.getByAltText("John Doe's avatar")
    expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.jpg')
    
    // Check status
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('Active')).toHaveClass('status', 'active')
  })

  test('renders inactive status correctly', () => {
    const inactiveUser = { ...mockUser, isActive: false }
    render(<UserCard {...mockProps} user={inactiveUser} />)
    
    expect(screen.getByText('Inactive')).toBeInTheDocument()
    expect(screen.getByText('Inactive')).toHaveClass('status', 'inactive')
  })

  test('handles missing user data', () => {
    render(<UserCard {...mockProps} user={null} />)
    
    expect(screen.getByText('No user data available')).toBeInTheDocument()
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  test('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup()
    render(<UserCard {...mockProps} />)
    
    const editButton = screen.getByRole('button', { name: 'Edit' })
    await user.click(editButton)
    
    expect(mockProps.onEdit).toHaveBeenCalledWith(1)
    expect(mockProps.onEdit).toHaveBeenCalledTimes(1)
  })

  test('calls onDelete when delete button is clicked', async () => {
    const user = userEvent.setup()
    render(<UserCard {...mockProps} />)
    
    const deleteButton = screen.getByRole('button', { name: 'Delete' })
    await user.click(deleteButton)
    
    expect(mockProps.onDelete).toHaveBeenCalledWith(1)
    expect(mockProps.onDelete).toHaveBeenCalledTimes(1)
  })

  test('disables edit button when editing', () => {
    render(<UserCard {...mockProps} isEditing={true} />)
    
    const editButton = screen.getByRole('button', { name: 'Editing...' })
    expect(editButton).toBeDisabled()
  })

  test('has proper accessibility attributes', () => {
    render(<UserCard {...mockProps} />)
    
    // Check that buttons are properly labeled
    expect(screen.getByRole('button', { name: 'Edit' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument()
    
    // Check heading structure
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('John Doe')
  })
})
{% endraw %}
{% endraw %}
```

## Testing User Interactions

```javascript
// components/ContactForm.jsx
import React, { useState } from 'react'

const ContactForm = ({ onSubmit, initialData = {} }) => {
  const [formData, setFormData] = useState({
    name: initialData.name || '',
    email: initialData.email || '',
    message: initialData.message || '',
    subscribe: initialData.subscribe || false
  })
  
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }
    
    if (!formData.message.trim()) {
      newErrors.message = 'Message is required'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } finally {
      setIsSubmitting(false)
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
      <div>
        <label htmlFor="name">Name *</label>
        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={handleChange('name')}
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <div id="name-error" role="alert" className="error">
            {errors.name}
          </div>
        )}
      </div>

      <div>
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={handleChange('email')}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <div id="email-error" role="alert" className="error">
            {errors.email}
          </div>
        )}
      </div>

      <div>
        <label htmlFor="message">Message *</label>
        <textarea
          id="message"
          value={formData.message}
          onChange={handleChange('message')}
          rows={4}
          aria-invalid={!!errors.message}
          aria-describedby={errors.message ? 'message-error' : undefined}
        />
        {errors.message && (
          <div id="message-error" role="alert" className="error">
            {errors.message}
          </div>
        )}
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={formData.subscribe}
            onChange={handleChange('subscribe')}
          />
          Subscribe to newsletter
        </label>
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  )
}

// __tests__/ContactForm.test.jsx
import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ContactForm from '../components/ContactForm'

describe('ContactForm', () => {
  const mockOnSubmit = jest.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  test('renders all form fields', () => {
    render(<ContactForm onSubmit={mockOnSubmit} />)
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/subscribe/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument()
  })

  test('fills out and submits form successfully', async () => {
    const user = userEvent.setup()
    mockOnSubmit.mockResolvedValue()

    render(<ContactForm onSubmit={mockOnSubmit} />)
    
    // Fill out the form
    await user.type(screen.getByLabelText(/name/i), 'John Doe')
    await user.type(screen.getByLabelText(/email/i), 'john@example.com')
    await user.type(screen.getByLabelText(/message/i), 'This is a test message')
    await user.click(screen.getByLabelText(/subscribe/i))
    
    // Submit the form
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        message: 'This is a test message',
        subscribe: true
      })
    })
  })

  test('shows validation errors for empty required fields', async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)
    
    // Try to submit empty form
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    // Check for error messages
    expect(screen.getByText('Name is required')).toBeInTheDocument()
    expect(screen.getByText('Email is required')).toBeInTheDocument()
    expect(screen.getByText('Message is required')).toBeInTheDocument()
    
    // Form should not be submitted
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  test('shows email validation error for invalid email', async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)
    
    await user.type(screen.getByLabelText(/email/i), 'invalid-email')
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    expect(screen.getByText('Email is invalid')).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  test('clears error when user starts typing in field', async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)
    
    // Submit to show errors
    await user.click(screen.getByRole('button', { name: /submit/i }))
    expect(screen.getByText('Name is required')).toBeInTheDocument()
    
    // Start typing in name field
    await user.type(screen.getByLabelText(/name/i), 'J')
    
    // Error should be cleared
    expect(screen.queryByText('Name is required')).not.toBeInTheDocument()
  })

  test('disables submit button while submitting', async () => {
    const user = userEvent.setup()
    // Make onSubmit hang to test loading state
    mockOnSubmit.mockImplementation(() => new Promise(() => {}))

    render(<ContactForm onSubmit={mockOnSubmit} />)
    
    // Fill required fields
    await user.type(screen.getByLabelText(/name/i), 'John')
    await user.type(screen.getByLabelText(/email/i), 'john@example.com')
    await user.type(screen.getByLabelText(/message/i), 'Test message')
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    // Button should be disabled and show loading text
    const button = screen.getByRole('button', { name: /submitting/i })
    expect(button).toBeDisabled()
  })

  test('populates form with initial data', () => {
    const initialData = {
      name: 'Jane Doe',
      email: 'jane@example.com',
      message: 'Initial message',
      subscribe: true
    }

    render(<ContactForm onSubmit={mockOnSubmit} initialData={initialData} />)
    
    expect(screen.getByDisplayValue('Jane Doe')).toBeInTheDocument()
    expect(screen.getByDisplayValue('jane@example.com')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Initial message')).toBeInTheDocument()
    expect(screen.getByLabelText(/subscribe/i)).toBeChecked()
  })

  test('has proper accessibility attributes', async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)
    
    // Submit to show errors
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    // Check aria-invalid attributes
    expect(screen.getByLabelText(/name/i)).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByLabelText(/email/i)).toHaveAttribute('aria-invalid', 'true')
    
    // Check error associations
    expect(screen.getByLabelText(/name/i)).toHaveAttribute('aria-describedby', 'name-error')
    
    // Check alert role for errors
    expect(screen.getByRole('alert', { name: /name is required/i })).toBeInTheDocument()
  })
})
```

## Testing Async Behavior

```javascript
{% raw %}
{% raw %}
// components/UserList.jsx
import React, { useState, useEffect } from 'react'

const UserList = ({ onUserSelect, searchTerm = '' }) => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const response = await fetch(`/api/users?search=${searchTerm}`)
        if (!response.ok) {
          throw new Error('Failed to fetch users')
        }
        const userData = await response.json()
        setUsers(userData)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [searchTerm])

  if (loading) {
    return <div role="status" aria-live="polite">Loading users...</div>
  }

  if (error) {
    return (
      <div role="alert" className="error">
        Error: {error}
      </div>
    )
  }

  if (users.length === 0) {
    return <div>No users found</div>
  }

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          <button onClick={() => onUserSelect(user)}>
            {user.name} ({user.email})
          </button>
        </li>
      ))}
    </ul>
  )
}

// __tests__/UserList.test.jsx
import React from 'react'
import { render, screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UserList from '../components/UserList'

// Mock fetch
global.fetch = jest.fn()

describe('UserList', () => {
  const mockUsers = [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
  ]

  const mockOnUserSelect = jest.fn()

  beforeEach(() => {
    fetch.mockClear()
    mockOnUserSelect.mockClear()
  })

  test('loads and displays users successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUsers
    })

    render(<UserList onUserSelect={mockOnUserSelect} />)
    
    // Initially shows loading
    expect(screen.getByText('Loading users...')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveAttribute('aria-live', 'polite')
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('John Doe (john@example.com)')).toBeInTheDocument()
    })
    
    // Loading should be gone
    expect(screen.queryByText('Loading users...')).not.toBeInTheDocument()
    
    // All users should be displayed
    expect(screen.getByText('Jane Smith (jane@example.com)')).toBeInTheDocument()
  })

  test('displays error message when fetch fails', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))

    render(<UserList onUserSelect={mockOnUserSelect} />)
    
    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText('Error: Network error')).toBeInTheDocument()
    })
    
    // Check error has proper role
    expect(screen.getByRole('alert')).toHaveTextContent('Error: Network error')
  })

  test('displays error for non-ok response', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404
    })

    render(<UserList onUserSelect={mockOnUserSelect} />)
    
    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch users')).toBeInTheDocument()
    })
  })

  test('shows no users message when list is empty', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => []
    })

    render(<UserList onUserSelect={mockOnUserSelect} />)
    
    await waitFor(() => {
      expect(screen.getByText('No users found')).toBeInTheDocument()
    })
  })

  test('calls onUserSelect when user is clicked', async () => {
    const user = userEvent.setup()
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUsers
    })

    render(<UserList onUserSelect={mockOnUserSelect} />)
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('John Doe (john@example.com)')).toBeInTheDocument()
    })
    
    // Click on a user
    await user.click(screen.getByText('John Doe (john@example.com)'))
    
    expect(mockOnUserSelect).toHaveBeenCalledWith(mockUsers[0])
  })

  test('refetches users when searchTerm changes', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: async () => mockUsers
    })

    const { rerender } = render(<UserList onUserSelect={mockOnUserSelect} searchTerm="" />)
    
    // Wait for initial fetch
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/users?search=')
    })
    
    // Change search term
    rerender(<UserList onUserSelect={mockOnUserSelect} searchTerm="john" />)
    
    // Should fetch again with new search term
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/users?search=john')
    })
    
    expect(fetch).toHaveBeenCalledTimes(2)
  })

  test('loading state changes appropriately', async () => {
    // Slow fetch to test loading states
    fetch.mockImplementation(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => mockUsers
        }), 100)
      )
    )

    render(<UserList onUserSelect={mockOnUserSelect} />)
    
    // Should show loading initially
    expect(screen.getByText('Loading users...')).toBeInTheDocument()
    
    // Wait for loading to finish
    await waitForElementToBeRemoved(() => screen.queryByText('Loading users...'))
    
    // Users should now be displayed
    expect(screen.getByText('John Doe (john@example.com)')).toBeInTheDocument()
  })
})
{% endraw %}
{% endraw %}
```

## Testing Custom Hooks

```javascript
{% raw %}
{% raw %}
// hooks/useLocalStorage.js
import { useState, useEffect } from 'react'

export const useLocalStorage = (key, initialValue) => {
  // Get value from localStorage or use initial value
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
      return initialValue
    }
  })

  // Update localStorage when state changes
  const setValue = (value) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }

  // Remove item from localStorage
  const removeValue = () => {
    try {
      window.localStorage.removeItem(key)
      setStoredValue(initialValue)
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error)
    }
  }

  return [storedValue, setValue, removeValue]
}

// __tests__/useLocalStorage.test.js
import { renderHook, act } from '@testing-library/react'
import { useLocalStorage } from '../hooks/useLocalStorage'

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString()
    }),
    removeItem: jest.fn((key) => {
      delete store[key]
    }),
    clear: jest.fn(() => {
      store = {}
    })
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorageMock.clear()
    jest.clearAllMocks()
  })

  test('returns initial value when no stored value exists', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))
    
    const [value] = result.current
    expect(value).toBe('initial')
  })

  test('returns stored value when it exists', () => {
    localStorageMock.setItem('test-key', JSON.stringify('stored'))
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))
    
    const [value] = result.current
    expect(value).toBe('stored')
  })

  test('updates localStorage when value is set', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))
    
    const [, setValue] = result.current
    
    act(() => {
      setValue('new value')
    })
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'test-key', 
      JSON.stringify('new value')
    )
    
    const [newValue] = result.current
    expect(newValue).toBe('new value')
  })

  test('supports functional updates', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 0))
    
    const [, setValue] = result.current
    
    act(() => {
      setValue(prev => prev + 1)
    })
    
    const [value] = result.current
    expect(value).toBe(1)
  })

  test('removes value from localStorage', () => {
    localStorageMock.setItem('test-key', JSON.stringify('stored'))
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))
    
    const [, , removeValue] = result.current
    
    act(() => {
      removeValue()
    })
    
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('test-key')
    
    const [value] = result.current
    expect(value).toBe('initial') // Should revert to initial value
  })

  test('handles JSON parse errors gracefully', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation()
    localStorageMock.getItem.mockReturnValue('invalid json')
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'fallback'))
    
    const [value] = result.current
    expect(value).toBe('fallback')
    expect(consoleSpy).toHaveBeenCalled()
    
    consoleSpy.mockRestore()
  })

  test('handles localStorage setItem errors', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation()
    localStorageMock.setItem.mockImplementation(() => {
      throw new Error('Storage quota exceeded')
    })
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))
    
    const [, setValue] = result.current
    
    act(() => {
      setValue('new value')
    })
    
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error setting localStorage key "test-key":',
      expect.any(Error)
    )
    
    consoleSpy.mockRestore()
  })

  test('works with complex objects', () => {
    const complexObject = { 
      name: 'John', 
      preferences: { theme: 'dark', language: 'en' } 
    }
    
    const { result } = renderHook(() => useLocalStorage('user', complexObject))
    
    const [, setValue] = result.current
    
    act(() => {
      setValue({ ...complexObject, name: 'Jane' })
    })
    
    const [value] = result.current
    expect(value.name).toBe('Jane')
    expect(value.preferences).toEqual({ theme: 'dark', language: 'en' })
  })
})
{% endraw %}
{% endraw %}
```

## Testing Context and Providers

```javascript
// context/ThemeContext.js
import React, { createContext, useContext, useReducer } from 'react'

const ThemeContext = createContext()

const themeReducer = (state, action) => {
  switch (action.type) {
    case 'SET_THEME':
      return { ...state, theme: action.payload }
    case 'TOGGLE_THEME':
      return { ...state, theme: state.theme === 'light' ? 'dark' : 'light' }
    case 'SET_FONT_SIZE':
      return { ...state, fontSize: action.payload }
    default:
      return state
  }
}

export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, {
    theme: 'light',
    fontSize: 'medium'
  })

  const setTheme = (theme) => dispatch({ type: 'SET_THEME', payload: theme })
  const toggleTheme = () => dispatch({ type: 'TOGGLE_THEME' })
  const setFontSize = (size) => dispatch({ type: 'SET_FONT_SIZE', payload: size })

  return (
    <ThemeContext.Provider value={{ 
      ...state, 
      setTheme, 
      toggleTheme, 
      setFontSize 
    }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

// components/ThemeToggle.jsx
import React from 'react'
import { useTheme } from '../context/ThemeContext'

const ThemeToggle = () => {
  const { theme, toggleTheme, setFontSize, fontSize } = useTheme()

  return (
    <div>
      <p>Current theme: {theme}</p>
      <button onClick={toggleTheme}>
        Switch to {theme === 'light' ? 'dark' : 'light'} theme
      </button>
      
      <div>
        <label>
          Font size:
          <select 
            value={fontSize} 
            onChange={(e) => setFontSize(e.target.value)}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </label>
      </div>
    </div>
  )
}

// __tests__/ThemeContext.test.jsx
import React from 'react'
import { render, screen, renderHook } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ThemeProvider, useTheme } from '../context/ThemeContext'
import ThemeToggle from '../components/ThemeToggle'

describe('ThemeContext', () => {
  test('provides default theme values', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider
    })

    expect(result.current.theme).toBe('light')
    expect(result.current.fontSize).toBe('medium')
  })

  test('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation()
    
    expect(() => {
      renderHook(() => useTheme())
    }).toThrow('useTheme must be used within a ThemeProvider')
    
    consoleSpy.mockRestore()
  })

  test('toggles theme correctly', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider
    })

    expect(result.current.theme).toBe('light')
    
    act(() => {
      result.current.toggleTheme()
    })
    
    expect(result.current.theme).toBe('dark')
    
    act(() => {
      result.current.toggleTheme()
    })
    
    expect(result.current.theme).toBe('light')
  })

  test('sets theme directly', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider
    })

    act(() => {
      result.current.setTheme('dark')
    })
    
    expect(result.current.theme).toBe('dark')
  })

  test('sets font size', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider
    })

    act(() => {
      result.current.setFontSize('large')
    })
    
    expect(result.current.fontSize).toBe('large')
  })
})

describe('ThemeToggle Component', () => {
  const renderWithProvider = (ui) => {
    return render(
      <ThemeProvider>
        {ui}
      </ThemeProvider>
    )
  }

  test('displays current theme', () => {
    renderWithProvider(<ThemeToggle />)
    
    expect(screen.getByText('Current theme: light')).toBeInTheDocument()
  })

  test('toggles theme when button is clicked', async () => {
    const user = userEvent.setup()
    renderWithProvider(<ThemeToggle />)
    
    const toggleButton = screen.getByText('Switch to dark theme')
    await user.click(toggleButton)
    
    expect(screen.getByText('Current theme: dark')).toBeInTheDocument()
    expect(screen.getByText('Switch to light theme')).toBeInTheDocument()
  })

  test('changes font size when select is changed', async () => {
    const user = userEvent.setup()
    renderWithProvider(<ThemeToggle />)
    
    const select = screen.getByDisplayValue('Medium')
    await user.selectOptions(select, 'Large')
    
    expect(screen.getByDisplayValue('Large')).toBeInTheDocument()
  })
})
```

## Accessibility Testing

```javascript
// __tests__/accessibility.test.jsx
import React from 'react'
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import ContactForm from '../components/ContactForm'
import UserCard from '../components/UserCard'

// Extend Jest matchers
expect.extend(toHaveNoViolations)

describe('Accessibility Tests', () => {
  test('ContactForm should not have accessibility violations', async () => {
    const { container } = render(
      <ContactForm onSubmit={jest.fn()} />
    )
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  test('UserCard should not have accessibility violations', async () => {
    const mockUser = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      role: 'Admin',
      avatar: 'https://example.com/avatar.jpg',
      isActive: true
    }

    const { container } = render(
      <UserCard 
        user={mockUser} 
        onEdit={jest.fn()} 
        onDelete={jest.fn()} 
      />
    )
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  test('form with errors should maintain accessibility', async () => {
    const { container } = render(
      <ContactForm onSubmit={jest.fn()} />
    )
    
    // Submit empty form to trigger errors
    const submitButton = screen.getByRole('button', { name: /submit/i })
    await userEvent.click(submitButton)
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

## Test Utilities and Custom Render

```javascript
// test-utils/index.js
import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ThemeProvider } from '../context/ThemeContext'

// Create a custom render function that includes providers
const AllTheProviders = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  })

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </QueryClientProvider>
    </BrowserRouter>
  )
}

const customRender = (ui, options) =>
  render(ui, { wrapper: AllTheProviders, ...options })

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }

// Common test data factories
export const createMockUser = (overrides = {}) => ({
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  role: 'user',
  isActive: true,
  avatar: 'https://example.com/avatar.jpg',
  ...overrides
})

export const createMockPost = (overrides = {}) => ({
  id: 1,
  title: 'Test Post',
  content: 'This is test content',
  author: createMockUser(),
  createdAt: new Date().toISOString(),
  ...overrides
})

// Wait for async operations to complete
export const waitForLoadingToFinish = () =>
  waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
  })
```

## Performance Testing

```javascript
{% raw %}
{% raw %}
// __tests__/performance.test.jsx
import React from 'react'
import { render } from '@testing-library/react'
import { performance } from 'perf_hooks'
import VirtualList from '../components/VirtualList'

describe('Performance Tests', () => {
  test('VirtualList renders large dataset efficiently', () => {
    const largeDataset = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      value: Math.random()
    }))

    const start = performance.now()
    
    render(
      <VirtualList
        items={largeDataset}
        itemHeight={50}
        containerHeight={400}
        renderItem={(item) => <div>{item.name}</div>}
      />
    )
    
    const end = performance.now()
    const renderTime = end - start
    
    // Should render in less than 100ms
    expect(renderTime).toBeLessThan(100)
  })

  test('Component re-renders are minimized', () => {
    let renderCount = 0
    
    const TestComponent = React.memo(({ value }) => {
      renderCount++
      return <div>{value}</div>
    })

    const { rerender } = render(<TestComponent value="test" />)
    
    expect(renderCount).toBe(1)
    
    // Re-render with same props
    rerender(<TestComponent value="test" />)
    expect(renderCount).toBe(1) // Should not re-render
    
    // Re-render with different props
    rerender(<TestComponent value="different" />)
    expect(renderCount).toBe(2) // Should re-render
  })
})
{% endraw %}
{% endraw %}
```

## Conclusion

React Testing Library provides powerful tools for testing React components with a focus on:

**Key Principles:**
- Test behavior, not implementation details
- Use accessible queries that mirror user interactions
- Avoid testing internal component state directly
- Focus on user experience and accessibility

**Best Practices:**
- Use the query priority hierarchy (getByRole > getByLabelText > etc.)
- Test user workflows, not isolated functions
- Mock external dependencies appropriately
- Write descriptive test names that explain expected behavior
- Group related tests using describe blocks
- Use custom render functions for providers

**Advanced Features:**
- Async testing with waitFor and findBy queries
- Custom hook testing with renderHook
- Context and provider testing
- Accessibility testing with jest-axe
- Performance testing for optimization verification

React Testing Library encourages writing tests that give you confidence in your application's behavior while remaining maintainable as your codebase evolves.
