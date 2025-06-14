# Code Review & Best Practices

## Introduction to Code Review Culture

Code review is a systematic examination of code changes to ensure quality, maintainability, and adherence to standards. In React development, effective code reviews catch bugs early, share knowledge across teams, and maintain consistent code quality.

### Benefits of Code Review

1. **Quality Assurance**: Catch bugs and issues before production
2. **Knowledge Sharing**: Spread expertise across the team
3. **Consistency**: Maintain coding standards and patterns
4. **Learning**: Continuous improvement for all team members
5. **Documentation**: Create a record of design decisions

## Code Review Process

### Pre-Review Checklist

```markdown
## PR Self-Review Checklist

### Functionality
- [ ] Code does what it's supposed to do
- [ ] All acceptance criteria are met
- [ ] Edge cases are handled
- [ ] Error scenarios are covered
- [ ] No console.log or debugging code left

### Code Quality
- [ ] Code follows team conventions
- [ ] Functions and variables have meaningful names
- [ ] Components are properly split and sized
- [ ] No code duplication
- [ ] Comments explain "why" not "what"

### Performance
- [ ] No unnecessary re-renders
- [ ] Proper use of React.memo, useMemo, useCallback
- [ ] Large lists use virtualization if needed
- [ ] Images are optimized
- [ ] Bundle size impact considered

### Security
- [ ] User inputs are validated and sanitized
- [ ] No sensitive data in client-side code
- [ ] Proper authentication/authorization checks
- [ ] XSS and injection vulnerabilities addressed

### Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests for critical paths
- [ ] Edge cases are tested
- [ ] Tests are readable and maintainable
- [ ] All tests pass

### Accessibility
- [ ] Proper semantic HTML
- [ ] ARIA attributes where needed
- [ ] Keyboard navigation works
- [ ] Screen reader compatibility
- [ ] Color contrast meets standards

### Documentation
- [ ] README updated if needed
- [ ] API changes documented
- [ ] Complex logic explained
- [ ] Breaking changes highlighted
```

### Review Guidelines

```typescript
// Example of good React component structure
interface UserProfileProps {
  userId: string
  onUpdate?: (user: User) => void
  className?: string
}

/**
 * UserProfile component displays and manages user information
 * 
 * @param userId - The ID of the user to display
 * @param onUpdate - Callback fired when user data is updated
 * @param className - Additional CSS classes
 */
const UserProfile: React.FC<UserProfileProps> = ({ 
  userId, 
  onUpdate, 
  className 
}) => {
  // State management
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Custom hooks for complex logic
  const { updateUser } = useUserApi()
  const { showToast } = useToast()

  // Effects
  useEffect(() => {
    const loadUser = async () => {
      try {
        setLoading(true)
        const userData = await fetchUser(userId)
        setUser(userData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load user')
      } finally {
        setLoading(false)
      }
    }

    loadUser()
  }, [userId])

  // Event handlers
  const handleSave = useCallback(async (updatedUser: Partial<User>) => {
    try {
      const updated = await updateUser(userId, updatedUser)
      setUser(updated)
      onUpdate?.(updated)
      showToast('User updated successfully', 'success')
    } catch (err) {
      showToast('Failed to update user', 'error')
    }
  }, [userId, updateUser, onUpdate, showToast])

  // Early returns for loading/error states
  if (loading) {
    return <LoadingSpinner aria-label="Loading user profile" />
  }

  if (error) {
    return (
      <ErrorMessage 
        message={error} 
        onRetry={() => window.location.reload()} 
      />
    )
  }

  if (!user) {
    return <div>User not found</div>
  }

  // Main render
  return (
    <div className={clsx('user-profile', className)}>
      <UserHeader user={user} />
      <UserDetails user={user} onSave={handleSave} />
    </div>
  )
}

export default UserProfile
```

## React-Specific Review Guidelines

### Component Design Patterns

```typescript
{% raw %}
// ✅ Good: Single Responsibility Principle
const UserAvatar: React.FC<{ user: User; size?: 'sm' | 'md' | 'lg' }> = ({ 
  user, 
  size = 'md' 
}) => {
  return (
    <img
      src={user.avatar || '/default-avatar.png'}
      alt={`${user.name}'s avatar`}
      className={`avatar avatar-${size}`}
      loading="lazy"
    />
  )
}

// ❌ Bad: Component doing too many things
const UserSection: React.FC<{ userId: string }> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [comments, setComments] = useState<Comment[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  
  // Too much responsibility in one component
  // Should be split into UserProfile, UserPosts, UserComments, etc.
}

// ✅ Good: Proper prop drilling vs context
interface ThemeContextType {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | null>(null)

// Use context for truly global state
const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  
  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }, [])

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// ❌ Bad: Passing props through many levels
const App = () => {
  const [user, setUser] = useState<User | null>(null)
  return <Layout user={user} setUser={setUser} />
}

const Layout = ({ user, setUser }: { user: User | null; setUser: (user: User) => void }) => {
  return <Header user={user} setUser={setUser} />
}

const Header = ({ user, setUser }: { user: User | null; setUser: (user: User) => void }) => {
  return <UserMenu user={user} setUser={setUser} />
}
{% endraw %}
```

### State Management Patterns

```typescript
// ✅ Good: Proper state colocation
const TodoItem: React.FC<{ todo: Todo; onUpdate: (todo: Todo) => void }> = ({ 
  todo, 
  onUpdate 
}) => {
  // Local state for UI-only concerns
  const [isEditing, setIsEditing] = useState(false)
  const [localTitle, setLocalTitle] = useState(todo.title)

  const handleSave = () => {
    onUpdate({ ...todo, title: localTitle })
    setIsEditing(false)
  }

  const handleCancel = () => {
    setLocalTitle(todo.title)
    setIsEditing(false)
  }

  return (
    <div className="todo-item">
      {isEditing ? (
        <div>
          <input
            value={localTitle}
            onChange={(e) => setLocalTitle(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSave()}
          />
          <button onClick={handleSave}>Save</button>
          <button onClick={handleCancel}>Cancel</button>
        </div>
      ) : (
        <div>
          <span>{todo.title}</span>
          <button onClick={() => setIsEditing(true)}>Edit</button>
        </div>
      )}
    </div>
  )
}

// ✅ Good: Proper useReducer for complex state
interface FormState {
  values: Record<string, unknown>
  errors: Record<string, string>
  touched: Record<string, boolean>
  isSubmitting: boolean
}

type FormAction =
  | { type: 'SET_VALUE'; field: string; value: unknown }
  | { type: 'SET_ERROR'; field: string; error: string }
  | { type: 'SET_TOUCHED'; field: string }
  | { type: 'SET_SUBMITTING'; isSubmitting: boolean }
  | { type: 'RESET' }

const formReducer = (state: FormState, action: FormAction): FormState => {
  switch (action.type) {
    case 'SET_VALUE':
      return {
        ...state,
        values: { ...state.values, [action.field]: action.value },
        errors: { ...state.errors, [action.field]: '' }, // Clear error on change
      }
    case 'SET_ERROR':
      return {
        ...state,
        errors: { ...state.errors, [action.field]: action.error },
      }
    case 'SET_TOUCHED':
      return {
        ...state,
        touched: { ...state.touched, [action.field]: true },
      }
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.isSubmitting }
    case 'RESET':
      return {
        values: {},
        errors: {},
        touched: {},
        isSubmitting: false,
      }
    default:
      return state
  }
}
```

### Performance Optimization Patterns

```typescript
// ✅ Good: Proper memoization
const ExpensiveList: React.FC<{ items: Item[]; filter: string }> = ({ 
  items, 
  filter 
}) => {
  // Memoize expensive computations
  const filteredItems = useMemo(() => {
    return items.filter(item => 
      item.name.toLowerCase().includes(filter.toLowerCase())
    )
  }, [items, filter])

  // Memoize the rendering function
  const renderItem = useCallback((item: Item) => (
    <ItemComponent key={item.id} item={item} />
  ), [])

  return (
    <div>
      {filteredItems.map(renderItem)}
    </div>
  )
}

// ✅ Good: Memoized child component
const ItemComponent = React.memo<{ item: Item }>(({ item }) => {
  return (
    <div className="item">
      <h3>{item.name}</h3>
      <p>{item.description}</p>
    </div>
  )
})

// ❌ Bad: Unnecessary re-renders
const BadList: React.FC<{ items: Item[] }> = ({ items }) => {
  return (
    <div>
      {items.map(item => (
        // New object created on every render
        <ItemComponent 
          key={item.id} 
          item={item} 
          config={{ showDescription: true }} // ❌ New object every render
          onUpdate={() => console.log('update')} // ❌ New function every render
        />
      ))}
    </div>
  )
}

// ✅ Good: Stable references
const GoodList: React.FC<{ items: Item[] }> = ({ items }) => {
  // Stable config object
  const config = useMemo(() => ({ showDescription: true }), [])
  
  // Stable callback
  const handleUpdate = useCallback(() => {
    console.log('update')
  }, [])

  return (
    <div>
      {items.map(item => (
        <ItemComponent 
          key={item.id} 
          item={item} 
          config={config}
          onUpdate={handleUpdate}
        />
      ))}
    </div>
  )
}
```

## Common Code Review Issues

### Anti-Patterns to Watch For

```typescript
{% raw %}
// ❌ Anti-Pattern: Mutating props
const BadComponent: React.FC<{ user: User }> = ({ user }) => {
  // Never mutate props directly
  user.name = 'Modified' // ❌ Direct mutation
  user.preferences.push('new-preference') // ❌ Mutating nested objects
  
  return <div>{user.name}</div>
}

// ✅ Good: Immutable updates
const GoodComponent: React.FC<{ user: User; onUpdate: (user: User) => void }> = ({ 
  user, 
  onUpdate 
}) => {
  const handleNameChange = (newName: string) => {
    // Create new object with updated values
    onUpdate({
      ...user,
      name: newName,
    })
  }

  const handlePreferenceAdd = (preference: string) => {
    onUpdate({
      ...user,
      preferences: [...user.preferences, preference],
    })
  }

  return (
    <div>
      <input 
        value={user.name} 
        onChange={(e) => handleNameChange(e.target.value)} 
      />
    </div>
  )
}

// ❌ Anti-Pattern: Side effects in render
const BadRenderEffects: React.FC<{ items: Item[] }> = ({ items }) => {
  // Never perform side effects during render
  localStorage.setItem('items', JSON.stringify(items)) // ❌
  console.log('Rendering with items:', items) // ❌ (except for debugging)
  
  return <div>{items.length} items</div>
}

// ✅ Good: Side effects in useEffect
const GoodEffects: React.FC<{ items: Item[] }> = ({ items }) => {
  useEffect(() => {
    // Side effects belong in useEffect
    localStorage.setItem('items', JSON.stringify(items))
  }, [items])

  useEffect(() => {
    // Logging for debugging purposes
    if (process.env.NODE_ENV === 'development') {
      console.log('Items updated:', items)
    }
  }, [items])

  return <div>{items.length} items</div>
}

// ❌ Anti-Pattern: Unnecessary state
const UnnecessaryState: React.FC<{ firstName: string; lastName: string }> = ({ 
  firstName, 
  lastName 
}) => {
  // Don't store derived state
  const [fullName, setFullName] = useState('') // ❌ Derived from props

  useEffect(() => {
    setFullName(`${firstName} ${lastName}`)
  }, [firstName, lastName])

  return <div>{fullName}</div>
}

// ✅ Good: Compute derived values
const ComputedValues: React.FC<{ firstName: string; lastName: string }> = ({ 
  firstName, 
  lastName 
}) => {
  // Compute derived values during render
  const fullName = `${firstName} ${lastName}`

  return <div>{fullName}</div>
}

// For expensive computations, use useMemo
const ExpensiveComputation: React.FC<{ items: Item[] }> = ({ items }) => {
  const expensiveValue = useMemo(() => {
    return items.reduce((sum, item) => sum + item.complexCalculation(), 0)
  }, [items])

  return <div>Total: {expensiveValue}</div>
}
{% endraw %}
```

### Security Review Points

```typescript
{% raw %}
// ✅ Good: Proper input validation and sanitization
const UserForm: React.FC<{ onSubmit: (data: UserData) => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    bio: '',
  })

  const validateAndSubmit = (e: FormEvent) => {
    e.preventDefault()
    
    // Client-side validation (not for security, just UX)
    const errors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required'
    }
    
    if (!isValidEmail(formData.email)) {
      errors.email = 'Valid email is required'
    }
    
    // Sanitize input before sending
    const sanitizedData = {
      name: sanitizeHtml(formData.name.trim()),
      email: formData.email.toLowerCase().trim(),
      bio: sanitizeHtml(formData.bio.trim()),
    }
    
    onSubmit(sanitizedData)
  }

  return (
    <form onSubmit={validateAndSubmit}>
      <input
        type="text"
        value={formData.name}
        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
        maxLength={100} // Prevent excessively long input
      />
      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
        maxLength={255}
      />
      <textarea
        value={formData.bio}
        onChange={(e) => setFormData(prev => ({ ...prev, bio: e.target.value }))}
        maxLength={1000}
      />
      <button type="submit">Submit</button>
    </form>
  )
}

// ❌ Bad: Dangerous HTML rendering
const DangerousComponent: React.FC<{ content: string }> = ({ content }) => {
  // Never render unsanitized user content as HTML
  return <div dangerouslySetInnerHTML={{ __html: content }} /> // ❌
}

// ✅ Good: Safe content rendering
const SafeComponent: React.FC<{ content: string }> = ({ content }) => {
  // Render as text by default
  return <div>{content}</div>
  
  // Or sanitize if HTML is needed
  const sanitizedContent = DOMPurify.sanitize(content)
  return <div dangerouslySetInnerHTML={{ __html: sanitizedContent }} />
}

// ✅ Good: Secure API calls
const SecureApiComponent: React.FC = () => {
  const { user } = useAuth()
  
  const fetchUserData = async () => {
    try {
      // Always include authentication
      const response = await fetch('/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch user data')
      }
      
      const data = await response.json()
      return data
    } catch (error) {
      // Don't expose sensitive error details
      console.error('Error fetching user data:', error)
      throw new Error('Unable to load user data')
    }
  }

  return <div>User Profile</div>
}
{% endraw %}
```

## Review Feedback Guidelines

### Constructive Feedback Examples

```markdown
## Examples of Good Review Comments

### Suggesting Improvements
❌ "This is wrong"
✅ "Consider using useCallback here to prevent unnecessary re-renders of child components"

❌ "Bad naming"
✅ "Could we use a more descriptive name? Maybe `handleUserSubmission` instead of `handleSubmit`?"

❌ "Performance issue"
✅ "This computation runs on every render. Consider wrapping it with useMemo to optimize performance:
```javascript
const filteredItems = useMemo(() => 
  items.filter(item => item.active), [items]
)
```"

### Asking Questions
✅ "What happens if `user` is null here? Should we add a null check?"
✅ "Could you explain the reasoning behind this approach? I'm curious about the trade-offs."
✅ "Is there a specific reason we're not using the existing `UserCard` component here?"

### Sharing Knowledge
✅ "Nice solution! FYI, React 18 has a new `useId` hook that might be useful for this use case."
✅ "This pattern works well. For future reference, we could also consider using a reducer for this complex state logic."

### Highlighting Positives
✅ "Great use of error boundaries here! This will help with debugging."
✅ "I like how you separated the business logic into a custom hook. Very clean!"
✅ "Excellent test coverage for the edge cases."
```

### Review Response Guidelines

```markdown
## How to Respond to Review Feedback

### Accepting Feedback
✅ "Good catch! I'll fix that."
✅ "You're right, that's a better approach. Updated!"
✅ "Thanks for the suggestion. I've implemented your recommendation."

### Asking for Clarification
✅ "Could you elaborate on what you mean by 'performance concern'?"
✅ "I'm not sure I understand the issue. Could you provide an example?"
✅ "What would you suggest as an alternative approach?"

### Explaining Decisions
✅ "I chose this approach because it handles the edge case where X happens."
✅ "This is required by the design system guidelines we established."
✅ "I considered that option but went with this because of the performance implications."

### Disagreeing Respectfully
✅ "I see your point, but I think this approach is better because..."
✅ "Could we discuss this in person? I'd like to understand your concerns better."
✅ "I'm not convinced this change is necessary. Here's my reasoning..."
```

## Automated Review Tools

### Setup for Automated Checks

```json
// package.json scripts for automated reviews
{
  "scripts": {
    "pre-review": "npm-run-all --parallel lint type-check test:coverage",
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx --max-warnings 0",
    "lint:fix": "eslint src --ext .js,.jsx,.ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "test:coverage": "jest --coverage --watchAll=false",
    "bundle-analyzer": "npm run build && npx bundle-analyzer dist/*.js",
    "audit": "npm audit --audit-level moderate"
  }
}
```

### GitHub Actions for Automated Review

```yaml
{% raw %}
# .github/workflows/pr-review.yml
name: PR Review Automation

on:
  pull_request:
    branches: [main, develop]

jobs:
  automated-review:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run linting
        run: npm run lint
        
      - name: Type checking
        run: npm run type-check
        
      - name: Run tests with coverage
        run: npm run test:coverage
        
      - name: Check bundle size
        uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Security audit
        run: npm audit --audit-level moderate
        
      - name: Comment PR with results
        uses: actions/github-script@v6
        if: failure()
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ Automated checks failed. Please review the errors and fix them before merging.'
            })
{% endraw %}
```

### Code Quality Metrics

```typescript
// Custom metrics collection
interface CodeQualityMetrics {
  cyclomaticComplexity: number
  linesOfCode: number
  testCoverage: number
  duplicatedLines: number
  technicalDebt: number
  maintainabilityIndex: number
}

const collectMetrics = async (filePath: string): Promise<CodeQualityMetrics> => {
  // Implementation would use tools like:
  // - ESLint complexity rules
  // - Jest coverage reports
  // - jscpd for duplication detection
  // - Code climate or similar for technical debt
  
  return {
    cyclomaticComplexity: 5,
    linesOfCode: 150,
    testCoverage: 85,
    duplicatedLines: 0,
    technicalDebt: 2,
    maintainabilityIndex: 75,
  }
}

// Quality gates
const qualityGates = {
  maxComplexity: 10,
  minTestCoverage: 80,
  maxDuplication: 5,
  minMaintainability: 60,
}

const passesQualityGates = (metrics: CodeQualityMetrics): boolean => {
  return (
    metrics.cyclomaticComplexity <= qualityGates.maxComplexity &&
    metrics.testCoverage >= qualityGates.minTestCoverage &&
    metrics.duplicatedLines <= qualityGates.maxDuplication &&
    metrics.maintainabilityIndex >= qualityGates.minMaintainability
  )
}
```

## Team Standards and Guidelines

### Establishing Team Conventions

```typescript
// Team coding standards document
export const TEAM_STANDARDS = {
  // Component naming
  componentNaming: {
    // Use PascalCase for components
    components: 'PascalCase', // UserProfile, NavBar, SearchInput
    // Use camelCase for props
    props: 'camelCase', // onClick, isVisible, userData
    // Use UPPER_SNAKE_CASE for constants
    constants: 'UPPER_SNAKE_CASE', // MAX_RETRIES, API_BASE_URL
  },

  // File organization
  fileStructure: {
    // Group by feature, not by file type
    structure: 'feature-based', // /features/user-profile/components/
    // Index files for clean imports
    indexFiles: true, // export { UserProfile } from './UserProfile'
    // Consistent file naming
    fileNaming: 'kebab-case', // user-profile.component.tsx
  },

  // Component structure
  componentStructure: {
    // Order of component elements
    order: [
      'imports',
      'types/interfaces',
      'constants',
      'component-definition',
      'styled-components', // if using styled-components
      'export',
    ],
    // Hooks order within component
    hooksOrder: [
      'useState',
      'useReducer',
      'useContext',
      'useEffect',
      'useLayoutEffect',
      'custom-hooks',
      'useCallback',
      'useMemo',
    ],
  },

  // Error handling
  errorHandling: {
    // Always use Error Boundaries for components
    errorBoundaries: true,
    // Consistent error message format
    errorFormat: 'user-friendly', // Don't expose technical details
    // Logging standards
    logging: 'structured', // Use structured logging with context
  },
} as const
```

### Documentation Standards

```typescript
/**
 * Complex component example with proper documentation
 */

/**
 * DataTable displays tabular data with sorting, filtering, and pagination
 * 
 * @example
 * ```tsx
 * <DataTable
 *   data={users}
 *   columns={userColumns}
 *   onSort={(column, direction) => handleSort(column, direction)}
 *   onFilter={(filters) => handleFilter(filters)}
 *   pagination={{ page: 1, limit: 20, total: 100 }}
 * />
 * ```
 */
interface DataTableProps<T> {
  /** Array of data objects to display */
  data: T[]
  
  /** Column configuration defining how to render each column */
  columns: ColumnConfig<T>[]
  
  /** Callback fired when a column header is clicked for sorting */
  onSort?: (column: keyof T, direction: 'asc' | 'desc') => void
  
  /** Callback fired when filter values change */
  onFilter?: (filters: Record<string, unknown>) => void
  
  /** Pagination configuration */
  pagination?: {
    /** Current page number (1-based) */
    page: number
    /** Number of items per page */
    limit: number
    /** Total number of items across all pages */
    total: number
  }
  
  /** Loading state - shows skeleton when true */
  loading?: boolean
  
  /** Empty state content when no data */
  emptyContent?: ReactNode
  
  /** Additional CSS classes */
  className?: string
}

/**
 * Column configuration for DataTable
 */
interface ColumnConfig<T> {
  /** Unique identifier for the column */
  key: keyof T
  
  /** Display title for the column header */
  title: string
  
  /** Custom render function for cell content */
  render?: (value: T[keyof T], row: T, index: number) => ReactNode
  
  /** Whether this column is sortable */
  sortable?: boolean
  
  /** Whether this column is filterable */
  filterable?: boolean
  
  /** Column width (CSS value) */
  width?: string
  
  /** Text alignment for the column */
  align?: 'left' | 'center' | 'right'
}

const DataTable = <T extends Record<string, unknown>>({
  data,
  columns,
  onSort,
  onFilter,
  pagination,
  loading = false,
  emptyContent = 'No data available',
  className,
}: DataTableProps<T>) => {
  // Component implementation...
}
```

This comprehensive code review and best practices guide establishes the foundation for maintaining high-quality React codebases through systematic review processes, clear standards, and automated quality checks.
