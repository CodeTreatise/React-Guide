# TypeScript Integration & Type Safety

## Introduction to TypeScript in React

TypeScript provides static type checking, enhanced IDE support, and improved code maintainability for React applications. It catches errors at compile time, provides better refactoring capabilities, and serves as living documentation for your codebase.

### Benefits of TypeScript with React

1. **Type Safety**: Catch errors before runtime
2. **Better IDE Support**: Enhanced autocomplete and refactoring
3. **Self-Documenting Code**: Types serve as documentation
4. **Easier Refactoring**: Confident large-scale changes
5. **Team Collaboration**: Clear interfaces and contracts

## TypeScript Configuration

### Installation

```bash
# Install TypeScript and related packages
npm install --save-dev typescript @types/react @types/react-dom
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin

# For testing
npm install --save-dev @types/jest @testing-library/jest-dom

# For additional type definitions
npm install --save-dev @types/node @types/lodash
```

### Basic tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/hooks/*": ["hooks/*"],
      "@/utils/*": ["utils/*"],
      "@/types/*": ["types/*"],
      "@/api/*": ["api/*"],
      "@/constants/*": ["constants/*"]
    },
    "incremental": true,
    "tsBuildInfoFile": "./node_modules/.cache/typescript/tsbuildinfo"
  },
  "include": [
    "src/**/*",
    "**/*.ts",
    "**/*.tsx"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "build",
    "coverage",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.spec.ts",
    "**/*.spec.tsx"
  ]
}
```

### Advanced TypeScript Configuration

```json
{
  "compilerOptions": {
    // Strict Type Checking
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    
    // Additional Checks
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    
    // Advanced Options
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "useDefineForClassFields": true,
    
    // Performance
    "skipLibCheck": true,
    "skipDefaultLibCheck": true,
    
    // Bundler mode
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true
  },
  "ts-node": {
    "esm": true,
    "experimentalSpecifierResolution": "node"
  }
}
```

## React Component Types

### Function Components

```typescript
{% raw %}
import React, { ReactNode, ReactElement } from 'react'

// Basic function component
interface ButtonProps {
  children: ReactNode
  onClick: () => void
  variant?: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
  size?: 'small' | 'medium' | 'large'
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  variant = 'primary',
  disabled = false,
  size = 'medium'
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
      disabled={disabled}
      type="button"
    >
      {children}
    </button>
  )
}

// Generic component
interface ListProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => ReactElement
  keyExtractor: (item: T) => string | number
  emptyComponent?: ReactElement
}

function List<T>({ 
  items, 
  renderItem, 
  keyExtractor, 
  emptyComponent 
}: ListProps<T>) {
  if (items.length === 0) {
    return emptyComponent || <div>No items</div>
  }

  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  )
}

// Forward ref component
interface InputProps {
  label: string
  error?: string
  type?: 'text' | 'email' | 'password' | 'number'
  placeholder?: string
  required?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, type = 'text', placeholder, required = false }, ref) => {
    return (
      <div className="input-group">
        <label className="input-label">
          {label}
          {required && <span className="required">*</span>}
        </label>
        <input
          ref={ref}
          type={type}
          placeholder={placeholder}
          className={`input ${error ? 'input-error' : ''}`}
          required={required}
        />
        {error && <span className="error-message">{error}</span>}
      </div>
    )
  }
)

Input.displayName = 'Input'
{% endraw %}
```

### Advanced Component Patterns

```typescript
{% raw %}
// Higher-Order Component typing
function withLoading<P extends object>(
  Component: React.ComponentType<P>
): React.FC<P & { loading?: boolean }> {
  return ({ loading = false, ...props }) => {
    if (loading) {
      return <div>Loading...</div>
    }
    return <Component {...props as P} />
  }
}

// Render prop pattern
interface DataFetcherProps<T> {
  url: string
  children: (data: T | null, loading: boolean, error: string | null) => ReactElement
}

function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = React.useState<T | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await fetch(url)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const result = await response.json() as T
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [url])

  return children(data, loading, error)
}

// Compound component pattern
interface TabsContextType {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const TabsContext = React.createContext<TabsContextType | null>(null)

interface TabsProps {
  children: ReactNode
  defaultTab: string
  onChange?: (tab: string) => void
}

const Tabs: React.FC<TabsProps> & {
  List: typeof TabList
  Tab: typeof Tab
  Panels: typeof TabPanels
  Panel: typeof TabPanel
} = ({ children, defaultTab, onChange }) => {
  const [activeTab, setActiveTab] = React.useState(defaultTab)

  const handleTabChange = (tab: string) => {
    setActiveTab(tab)
    onChange?.(tab)
  }

  const value = { activeTab, setActiveTab: handleTabChange }

  return (
    <TabsContext.Provider value={value}>
      {children}
    </TabsContext.Provider>
  )
}

const useTabs = (): TabsContextType => {
  const context = React.useContext(TabsContext)
  if (!context) {
    throw new Error('Tab components must be used within a Tabs provider')
  }
  return context
}

interface TabListProps {
  children: ReactNode
}

const TabList: React.FC<TabListProps> = ({ children }) => (
  <div role="tablist">{children}</div>
)

interface TabProps {
  value: string
  children: ReactNode
  disabled?: boolean
}

const Tab: React.FC<TabProps> = ({ value, children, disabled = false }) => {
  const { activeTab, setActiveTab } = useTabs()
  const isActive = activeTab === value

  return (
    <button
      role="tab"
      aria-selected={isActive}
      aria-disabled={disabled}
      onClick={() => !disabled && setActiveTab(value)}
      className={`tab ${isActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
    >
      {children}
    </button>
  )
}

const TabPanels: React.FC<{ children: ReactNode }> = ({ children }) => (
  <div className="tab-panels">{children}</div>
)

interface TabPanelProps {
  value: string
  children: ReactNode
}

const TabPanel: React.FC<TabPanelProps> = ({ value, children }) => {
  const { activeTab } = useTabs()
  const isActive = activeTab === value

  if (!isActive) return null

  return (
    <div role="tabpanel" className="tab-panel">
      {children}
    </div>
  )
}

Tabs.List = TabList
Tabs.Tab = Tab
Tabs.Panels = TabPanels
Tabs.Panel = TabPanel
{% endraw %}
```

## Hook Typing

### Custom Hook Types

```typescript
{% raw %}
// Custom hook with return tuple
function useToggle(initialValue = false): [boolean, () => void, () => void, () => void] {
  const [value, setValue] = React.useState(initialValue)

  const toggle = React.useCallback(() => setValue(prev => !prev), [])
  const setTrue = React.useCallback(() => setValue(true), [])
  const setFalse = React.useCallback(() => setValue(false), [])

  return [value, toggle, setTrue, setFalse]
}

// Custom hook with object return
interface UseApiResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

function useApi<T>(url: string): UseApiResult<T> {
  const [data, setData] = React.useState<T | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const fetchData = React.useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json() as T
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }, [url])

  React.useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}

// Generic hook with constraints
interface UseLocalStorageOptions {
  serializer?: {
    parse: (value: string) => unknown
    stringify: (value: unknown) => string
  }
  defaultValue?: unknown
}

function useLocalStorage<T>(
  key: string, 
  options: UseLocalStorageOptions = {}
): [T | undefined, (value: T | ((prev: T | undefined) => T)) => void] {
  const { serializer = JSON, defaultValue } = options

  const [storedValue, setStoredValue] = React.useState<T | undefined>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? serializer.parse(item) as T : defaultValue as T
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
      return defaultValue as T
    }
  })

  const setValue = React.useCallback((value: T | ((prev: T | undefined) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, serializer.stringify(valueToStore))
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }, [key, serializer, storedValue])

  return [storedValue, setValue]
}
{% endraw %}
```

### Complex Hook Patterns

```typescript
// State machine hook
type State = 'idle' | 'loading' | 'success' | 'error'

interface AsyncState<T> {
  status: State
  data: T | null
  error: string | null
}

type AsyncAction<T> = 
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: T }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'RESET' }

function asyncReducer<T>(state: AsyncState<T>, action: AsyncAction<T>): AsyncState<T> {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, status: 'loading', error: null }
    case 'FETCH_SUCCESS':
      return { status: 'success', data: action.payload, error: null }
    case 'FETCH_ERROR':
      return { ...state, status: 'error', error: action.payload }
    case 'RESET':
      return { status: 'idle', data: null, error: null }
    default:
      return state
  }
}

function useAsyncData<T>(
  fetchFn: () => Promise<T>,
  dependencies: React.DependencyList = []
) {
  const [state, dispatch] = React.useReducer(asyncReducer<T>, {
    status: 'idle',
    data: null,
    error: null,
  })

  const execute = React.useCallback(async () => {
    dispatch({ type: 'FETCH_START' })
    try {
      const data = await fetchFn()
      dispatch({ type: 'FETCH_SUCCESS', payload: data })
    } catch (error) {
      dispatch({ 
        type: 'FETCH_ERROR', 
        payload: error instanceof Error ? error.message : 'Unknown error' 
      })
    }
  }, dependencies)

  const reset = React.useCallback(() => {
    dispatch({ type: 'RESET' })
  }, [])

  return {
    ...state,
    execute,
    reset,
    isIdle: state.status === 'idle',
    isLoading: state.status === 'loading',
    isSuccess: state.status === 'success',
    isError: state.status === 'error',
  }
}
```

## Event Handling Types

### Event Types

```typescript
import React, { ChangeEvent, FormEvent, MouseEvent, KeyboardEvent } from 'react'

interface FormProps {
  onSubmit: (data: FormData) => void
}

interface FormData {
  name: string
  email: string
  message: string
}

const ContactForm: React.FC<FormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = React.useState<FormData>({
    name: '',
    email: '',
    message: '',
  })

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault()
      // Submit form
    }
  }

  const handleButtonClick = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    // Handle button click
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder="Name"
        required
      />
      <input
        name="email"
        type="email"
        value={formData.email}
        onChange={handleInputChange}
        placeholder="Email"
        required
      />
      <textarea
        name="message"
        value={formData.message}
        onChange={handleInputChange}
        placeholder="Message"
        required
      />
      <button type="submit" onClick={handleButtonClick}>
        Submit
      </button>
    </form>
  )
}
```

### Custom Event Types

```typescript
{% raw %}
// Custom event interfaces
interface CustomSelectOption {
  value: string
  label: string
  disabled?: boolean
}

interface SelectChangeEvent {
  value: string
  option: CustomSelectOption
}

interface MultiSelectProps {
  options: CustomSelectOption[]
  value: string[]
  onChange: (event: SelectChangeEvent & { values: string[] }) => void
  placeholder?: string
}

const MultiSelect: React.FC<MultiSelectProps> = ({
  options,
  value,
  onChange,
  placeholder = 'Select options...'
}) => {
  const handleOptionToggle = (option: CustomSelectOption) => {
    const isSelected = value.includes(option.value)
    const newValues = isSelected
      ? value.filter(v => v !== option.value)
      : [...value, option.value]
    
    onChange({
      value: option.value,
      option,
      values: newValues,
    })
  }

  return (
    <div className="multi-select">
      <div className="selected-values">
        {value.length === 0 ? placeholder : `${value.length} selected`}
      </div>
      <div className="options">
        {options.map(option => (
          <div
            key={option.value}
            className={`option ${value.includes(option.value) ? 'selected' : ''}`}
            onClick={() => !option.disabled && handleOptionToggle(option)}
          >
            {option.label}
          </div>
        ))}
      </div>
    </div>
  )
}
{% endraw %}
```

## Type Definitions

### Common Type Patterns

```typescript
// Utility types for React props
type OmitChildren<T> = Omit<T, 'children'>
type WithChildren<T = {}> = T & { children: ReactNode }
type ElementProps<T extends keyof JSX.IntrinsicElements> = JSX.IntrinsicElements[T]

// Component prop extraction
type ButtonProps = React.ComponentProps<'button'>
type DivProps = React.ComponentProps<'div'>
type InputProps = React.ComponentProps<'input'>

// Extending HTML element props
interface CustomButtonProps extends Omit<ButtonProps, 'onClick'> {
  onClick: (id: string) => void
  variant: 'primary' | 'secondary'
  loading?: boolean
}

// Discriminated unions for component variants
type AlertVariant = 
  | { type: 'success'; message: string }
  | { type: 'error'; message: string; retryAction?: () => void }
  | { type: 'warning'; message: string; dismissible?: boolean }
  | { type: 'info'; message: string; icon?: ReactElement }

interface AlertProps {
  variant: AlertVariant
  onClose?: () => void
}

const Alert: React.FC<AlertProps> = ({ variant, onClose }) => {
  const renderContent = () => {
    switch (variant.type) {
      case 'success':
        return <div className="alert-success">{variant.message}</div>
      case 'error':
        return (
          <div className="alert-error">
            {variant.message}
            {variant.retryAction && (
              <button onClick={variant.retryAction}>Retry</button>
            )}
          </div>
        )
      case 'warning':
        return (
          <div className="alert-warning">
            {variant.message}
            {variant.dismissible && (
              <button onClick={onClose}>Dismiss</button>
            )}
          </div>
        )
      case 'info':
        return (
          <div className="alert-info">
            {variant.icon}
            {variant.message}
          </div>
        )
    }
  }

  return <div className="alert">{renderContent()}</div>
}
```

### API Response Types

```typescript
{% raw %}
// API response types
interface ApiResponse<T> {
  data: T
  status: number
  message: string
  timestamp: string
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt: string
  updatedAt: string
}

interface Post {
  id: string
  title: string
  content: string
  author: User
  tags: string[]
  publishedAt: string | null
  createdAt: string
  updatedAt: string
}

// API hook with proper typing
function useUsers() {
  return useApi<PaginatedResponse<User>>('/api/users')
}

function useUser(id: string) {
  return useApi<ApiResponse<User>>(`/api/users/${id}`)
}

// Form validation types
interface ValidationRule<T> {
  validate: (value: T) => boolean
  message: string
}

interface FieldValidation<T> {
  required?: boolean
  rules?: ValidationRule<T>[]
}

interface FormValidation<T extends Record<string, unknown>> {
  [K in keyof T]?: FieldValidation<T[K]>
}

// Usage example
interface LoginForm {
  email: string
  password: string
}

const loginValidation: FormValidation<LoginForm> = {
  email: {
    required: true,
    rules: [
      {
        validate: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        message: 'Please enter a valid email address',
      },
    ],
  },
  password: {
    required: true,
    rules: [
      {
        validate: (value) => value.length >= 8,
        message: 'Password must be at least 8 characters long',
      },
    ],
  },
}
{% endraw %}
```

## Advanced Type Patterns

### Conditional Types

```typescript
{% raw %}
// Conditional types for component props
type ConditionalProps<T> = T extends string
  ? { stringProp: string }
  : T extends number
  ? { numberProp: number }
  : { defaultProp: unknown }

// Mapped types for form fields
type FormField<T> = {
  value: T
  error?: string
  touched: boolean
}

type FormFields<T> = {
  [K in keyof T]: FormField<T[K]>
}

// Example usage
interface UserForm {
  name: string
  age: number
  email: string
}

type UserFormFields = FormFields<UserForm>
// Results in:
// {
//   name: FormField<string>
//   age: FormField<number>
//   email: FormField<string>
// }

// Template literal types for styling
type Size = 'sm' | 'md' | 'lg'
type Color = 'primary' | 'secondary' | 'danger'
type ButtonClass = `btn-${Size}-${Color}`

// Recursive types for nested components
interface TreeNode<T> {
  id: string
  data: T
  children?: TreeNode<T>[]
}

interface TreeProps<T> {
  nodes: TreeNode<T>[]
  renderNode: (node: TreeNode<T>) => ReactElement
  onNodeClick?: (node: TreeNode<T>) => void
}

function Tree<T>({ nodes, renderNode, onNodeClick }: TreeProps<T>) {
  return (
    <ul>
      {nodes.map(node => (
        <li key={node.id}>
          <div onClick={() => onNodeClick?.(node)}>
            {renderNode(node)}
          </div>
          {node.children && (
            <Tree
              nodes={node.children}
              renderNode={renderNode}
              onNodeClick={onNodeClick}
            />
          )}
        </li>
      ))}
    </ul>
  )
}
{% endraw %}
```

### Type Guards and Assertions

```typescript
// Type guards
function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    'email' in value
  )
}

// Custom error types
class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

// Error boundary with typed errors
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

class TypedErrorBoundary extends React.Component<
  WithChildren,
  ErrorBoundaryState
> {
  constructor(props: WithChildren) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    
    if (isApiError(error)) {
      // Handle API errors specifically
      console.error('API Error:', error.status, error.code)
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          {this.state.error && isApiError(this.state.error) && (
            <p>API Error: {this.state.error.message}</p>
          )}
        </div>
      )
    }

    return this.props.children
  }
}
```

## Testing with TypeScript

### Component Testing Types

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Mock types
interface MockApiResponse<T> {
  data: T
  status: number
}

const mockApiCall = <T>(data: T): Promise<MockApiResponse<T>> => {
  return Promise.resolve({ data, status: 200 })
}

// Test utilities with types
const renderWithProviders = (
  ui: ReactElement,
  options?: {
    initialState?: Partial<AppState>
    route?: string
  }
) => {
  const { initialState, route = '/' } = options || {}
  
  // Setup providers with proper types
  return render(ui, { wrapper: TestWrapper })
}

// Custom matchers
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeAccessible(): R
      toHaveValidMarkup(): R
    }
  }
}

// Test component props
interface TestComponentProps {
  title: string
  onClick: jest.MockedFunction<() => void>
  items?: string[]
}

const TestComponent: React.FC<TestComponentProps> = ({ title, onClick, items = [] }) => {
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onClick}>Click me</button>
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

// Type-safe test
describe('TestComponent', () => {
  it('renders with correct props', () => {
    const mockClick = jest.fn()
    const props: TestComponentProps = {
      title: 'Test Title',
      onClick: mockClick,
      items: ['item1', 'item2'],
    }

    render(<TestComponent {...props} />)

    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('item1')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Click me'))
    expect(mockClick).toHaveBeenCalledTimes(1)
  })
})
```

## Migration Strategies

### Gradual TypeScript Adoption

```typescript
{% raw %}
// Step 1: Add basic types
// Before (JavaScript)
const Button = ({ children, onClick, variant }) => {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  )
}

// After (TypeScript)
interface ButtonProps {
  children: ReactNode
  onClick: () => void
  variant: 'primary' | 'secondary'
}

const Button: React.FC<ButtonProps> = ({ children, onClick, variant }) => {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  )
}

// Step 2: Add strict types
interface StrictButtonProps {
  children: ReactNode
  onClick: (event: MouseEvent<HTMLButtonElement>) => void
  variant: 'primary' | 'secondary' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  'aria-label'?: string
}

const StrictButton = React.forwardRef<HTMLButtonElement, StrictButtonProps>(
  ({ children, onClick, variant, size = 'medium', disabled = false, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={`btn btn-${variant} btn-${size}`}
        onClick={onClick}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    )
  }
)
{% endraw %}
```

### Legacy Code Integration

```typescript
// Declaring types for untyped libraries
declare module 'untyped-library' {
  export interface LibraryConfig {
    apiKey: string
    timeout?: number
  }

  export function initialize(config: LibraryConfig): void
  export function getData<T>(endpoint: string): Promise<T>
}

// Gradual typing with any escape hatch
interface PartiallyTypedComponent {
  knownProp: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  legacyProps: any
}

// Type assertions for migration
const legacyData = getLegacyData() as unknown as User[]
```

This comprehensive TypeScript integration guide provides the foundation for building type-safe, maintainable React applications with excellent developer experience and reduced runtime errors.
