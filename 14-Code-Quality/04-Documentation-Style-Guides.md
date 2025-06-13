# Documentation & Style Guides

## Introduction to Technical Documentation

Comprehensive documentation is crucial for React projects to ensure maintainability, onboarding efficiency, and knowledge preservation. Well-structured documentation serves as the single source of truth for project conventions, architecture decisions, and usage guidelines.

### Documentation Philosophy

1. **Documentation as Code**: Keep docs in version control alongside code
2. **Living Documentation**: Update docs with every code change
3. **User-Centric**: Write for your intended audience
4. **Searchable**: Organize for easy discovery
5. **Executable**: Include runnable examples

## Project Documentation Structure

### README.md Template

```markdown
# Project Name

Brief description of what this application does and who it's for.

![Build Status](https://img.shields.io/github/workflow/status/username/repo/CI)
![Coverage](https://img.shields.io/codecov/c/github/username/repo)
![License](https://img.shields.io/github/license/username/repo)

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

### Prerequisites

- Node.js 18+ and npm 8+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/username/repo.git
cd repo

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Environment Setup

```bash
# Copy environment template
cp .env.example .env.local

# Configure required variables
NEXT_PUBLIC_API_URL=http://localhost:8080
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

## Features

### Core Features

- 🔐 **Authentication**: JWT-based auth with refresh tokens
- 👥 **User Management**: CRUD operations with role-based access
- 📊 **Dashboard**: Real-time analytics and reporting
- 📱 **Responsive**: Mobile-first design approach
- 🌐 **Internationalization**: Support for multiple languages
- 🧪 **Testing**: Comprehensive test coverage (>90%)

### Technical Features

- ⚡ **Performance**: Code splitting and lazy loading
- 🔍 **SEO**: Server-side rendering with metadata
- 📦 **Bundle Analysis**: Webpack bundle analyzer integration
- 🚀 **CI/CD**: Automated testing and deployment
- 🔧 **Developer Experience**: Hot reload, TypeScript, ESLint

## Architecture

### Tech Stack

- **Frontend**: React 18, TypeScript, Next.js 13
- **Styling**: Tailwind CSS, Headless UI
- **State Management**: Zustand, React Query
- **Testing**: Jest, React Testing Library, Playwright
- **Build Tools**: Webpack, Babel, PostCSS
- **Deployment**: Vercel, Docker

### Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI elements
│   ├── forms/          # Form-specific components
│   └── layout/         # Layout components
├── features/           # Feature-based modules
│   ├── auth/          # Authentication feature
│   ├── dashboard/     # Dashboard feature
│   └── users/         # User management feature
├── hooks/             # Custom React hooks
├── lib/               # Utility libraries
├── types/             # TypeScript type definitions
└── utils/             # Helper functions
```

### Key Architectural Decisions

#### State Management Strategy
We use a hybrid approach:
- **Local State**: `useState` for component-specific state
- **Server State**: React Query for API data
- **Global State**: Zustand for app-wide state
- **Form State**: React Hook Form for complex forms

#### Styling Approach
- **Utility-First**: Tailwind CSS for rapid development
- **Component Library**: Headless UI for accessible components
- **Custom Components**: Styled with CSS modules when needed

## Development

### Getting Started

1. **Install dependencies**: `npm install`
2. **Start development server**: `npm run dev`
3. **Run tests**: `npm test`
4. **Type checking**: `npm run type-check`
5. **Linting**: `npm run lint`

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Create production build
npm run start        # Start production server
npm test             # Run tests in watch mode
npm run test:ci      # Run tests once with coverage
npm run type-check   # TypeScript type checking
npm run lint         # ESLint linting
npm run lint:fix     # Fix linting issues
npm run analyze      # Bundle size analysis
```

### Development Workflow

1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Make changes**: Follow coding standards and conventions
3. **Run tests**: `npm test` to ensure everything works
4. **Commit changes**: Use conventional commits format
5. **Push and create PR**: Include description and tests
6. **Code review**: Address feedback and make changes
7. **Merge**: Squash merge to main branch

### Coding Standards

- Follow the [Style Guide](./docs/STYLE_GUIDE.md)
- Use TypeScript for all new code
- Write tests for new features and bug fixes
- Update documentation for API changes
- Follow conventional commit format

## Deployment

### Environments

- **Development**: Auto-deployed from `develop` branch
- **Staging**: Auto-deployed from `staging` branch  
- **Production**: Auto-deployed from `main` branch

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | API base URL | Yes | - |
| `DATABASE_URL` | Database connection string | Yes | - |
| `JWT_SECRET` | JWT signing secret | Yes | - |
| `REDIS_URL` | Redis connection string | No | - |

### Deployment Process

1. **Automatic**: Push to main triggers deployment
2. **Manual**: Use GitHub Actions workflow dispatch
3. **Rollback**: Revert commit or redeploy previous version

## Contributing

Please read our [Contributing Guide](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Bug Reports

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details

### Feature Requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:
- Problem statement
- Proposed solution
- Alternative solutions considered
- Additional context

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### API Documentation

```typescript
// API documentation with TypeScript
/**
 * User API endpoints and types
 * 
 * Base URL: /api/users
 */

/**
 * User object structure
 */
interface User {
  /** Unique user identifier */
  id: string
  /** User's full name */
  name: string
  /** User's email address */
  email: string
  /** User's role in the system */
  role: 'admin' | 'user' | 'moderator'
  /** Profile avatar URL */
  avatar?: string
  /** Account creation timestamp */
  createdAt: string
  /** Last update timestamp */
  updatedAt: string
}

/**
 * Create user request payload
 */
interface CreateUserRequest {
  name: string
  email: string
  password: string
  role?: 'user' | 'moderator'
}

/**
 * Update user request payload
 */
interface UpdateUserRequest {
  name?: string
  email?: string
  role?: 'user' | 'moderator' | 'admin'
  avatar?: string
}

/**
 * User API responses
 */
interface UserResponse {
  data: User
  message: string
}

interface UsersResponse {
  data: User[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
  message: string
}

/**
 * Get all users
 * 
 * @route GET /api/users
 * @access Private (Admin only)
 * @param page - Page number (default: 1)
 * @param limit - Items per page (default: 20, max: 100)
 * @param search - Search term for name/email
 * @param role - Filter by user role
 * @param sortBy - Sort field (name, email, createdAt)
 * @param sortOrder - Sort direction (asc, desc)
 * 
 * @example
 * ```typescript
 * const response = await fetch('/api/users?page=1&limit=20&search=john&role=user')
 * const { data, pagination } = await response.json()
 * ```
 * 
 * @returns Promise<UsersResponse>
 */
export const getUsers = async (params?: {
  page?: number
  limit?: number
  search?: string
  role?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}): Promise<UsersResponse> => {
  const searchParams = new URLSearchParams(params as Record<string, string>)
  const response = await fetch(`/api/users?${searchParams}`)
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Get user by ID
 * 
 * @route GET /api/users/:id
 * @access Private
 * @param id - User ID
 * 
 * @example
 * ```typescript
 * const user = await getUserById('123')
 * console.log(user.data.name)
 * ```
 * 
 * @returns Promise<UserResponse>
 * @throws {Error} User not found (404)
 * @throws {Error} Unauthorized (401)
 */
export const getUserById = async (id: string): Promise<UserResponse> => {
  const response = await fetch(`/api/users/${id}`)
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('User not found')
    }
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Create new user
 * 
 * @route POST /api/users
 * @access Private (Admin only)
 * @param userData - User creation data
 * 
 * @example
 * ```typescript
 * const newUser = await createUser({
 *   name: 'John Doe',
 *   email: 'john@example.com',
 *   password: 'securePassword123',
 *   role: 'user'
 * })
 * ```
 * 
 * @returns Promise<UserResponse>
 * @throws {Error} Validation error (400)
 * @throws {Error} Email already exists (409)
 */
export const createUser = async (userData: CreateUserRequest): Promise<UserResponse> => {
  const response = await fetch('/api/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || `HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}
```

### Component Documentation

```typescript
// Component documentation template
/**
 * Button component with multiple variants and states
 * 
 * @example
 * Basic usage:
 * ```tsx
 * <Button onClick={() => console.log('clicked')}>
 *   Click me
 * </Button>
 * ```
 * 
 * @example
 * With loading state:
 * ```tsx
 * <Button 
 *   variant="primary" 
 *   size="large" 
 *   loading={isSubmitting}
 *   disabled={!isValid}
 *   onClick={handleSubmit}
 * >
 *   Submit Form
 * </Button>
 * ```
 * 
 * @example
 * As a link:
 * ```tsx
 * <Button as="a" href="/dashboard" variant="secondary">
 *   Go to Dashboard
 * </Button>
 * ```
 */

interface ButtonProps {
  /** Button content */
  children: ReactNode
  
  /** 
   * Button visual variant 
   * @default "primary"
   */
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  
  /** 
   * Button size 
   * @default "medium"
   */
  size?: 'small' | 'medium' | 'large'
  
  /** 
   * Disabled state - prevents interaction 
   * @default false
   */
  disabled?: boolean
  
  /** 
   * Loading state - shows spinner and disables interaction 
   * @default false
   */
  loading?: boolean
  
  /** 
   * Full width button 
   * @default false
   */
  fullWidth?: boolean
  
  /** 
   * Element type to render as 
   * @default "button"
   */
  as?: 'button' | 'a' | 'div'
  
  /** 
   * Click handler 
   * Only called when not disabled or loading
   */
  onClick?: (event: MouseEvent<HTMLButtonElement>) => void
  
  /** Additional CSS classes */
  className?: string
  
  /** HTML type attribute (for button element) */
  type?: 'button' | 'submit' | 'reset'
  
  /** 
   * Accessible label for screen readers 
   * Use when button content is not descriptive
   */
  'aria-label'?: string
}

/**
 * Button component implementation
 * 
 * Features:
 * - Multiple visual variants (primary, secondary, danger, ghost)
 * - Size variations (small, medium, large)
 * - Loading and disabled states
 * - Polymorphic (can render as button, link, or div)
 * - Full accessibility support
 * - Keyboard navigation support
 * 
 * Accessibility:
 * - Proper ARIA attributes
 * - Keyboard navigation (Enter/Space)
 * - Focus management
 * - Screen reader support
 * 
 * Performance:
 * - Memoized to prevent unnecessary re-renders
 * - Optimized class name concatenation
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  fullWidth = false,
  as: Component = 'button',
  onClick,
  className,
  type = 'button',
  'aria-label': ariaLabel,
  ...props
}, ref) => {
  const handleClick = useCallback((event: MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) {
      event.preventDefault()
      return
    }
    onClick?.(event)
  }, [disabled, loading, onClick])

  const classNames = useMemo(() => clsx(
    'btn',
    `btn-${variant}`,
    `btn-${size}`,
    {
      'btn-disabled': disabled,
      'btn-loading': loading,
      'btn-full-width': fullWidth,
    },
    className
  ), [variant, size, disabled, loading, fullWidth, className])

  const buttonProps = {
    ref,
    className: classNames,
    onClick: handleClick,
    disabled: disabled || loading,
    type: Component === 'button' ? type : undefined,
    'aria-label': ariaLabel,
    'aria-disabled': disabled || loading,
    ...props,
  }

  return (
    <Component {...buttonProps}>
      {loading && <Spinner size="small" />}
      <span className={loading ? 'btn-content-loading' : 'btn-content'}>
        {children}
      </span>
    </Component>
  )
})

Button.displayName = 'Button'

export default Button

/**
 * Usage guidelines:
 * 
 * 1. Use 'primary' for main actions (submit, save, continue)
 * 2. Use 'secondary' for secondary actions (cancel, back)
 * 3. Use 'danger' for destructive actions (delete, remove)
 * 4. Use 'ghost' for subtle actions (view details, edit)
 * 
 * 5. Always provide meaningful button text
 * 6. Use loading state for async operations
 * 7. Disable buttons when action is not available
 * 8. Use aria-label for icon-only buttons
 */
```

## Style Guide

### Naming Conventions

```typescript
// Naming conventions guide

/**
 * COMPONENTS
 * - Use PascalCase for component names
 * - Use descriptive, noun-based names
 * - Avoid abbreviations unless widely understood
 */

// ✅ Good
const UserProfile = () => {}
const NavigationBar = () => {}
const SearchInput = () => {}
const DataTable = () => {}

// ❌ Bad  
const userprofile = () => {} // Wrong case
const NavBar = () => {}      // Abbreviation
const Tbl = () => {}         // Too abbreviated
const Component1 = () => {}  // Not descriptive

/**
 * PROPS AND VARIABLES
 * - Use camelCase for props and variables
 * - Use descriptive names that explain purpose
 * - Use boolean prefixes (is, has, can, should)
 */

// ✅ Good
interface UserCardProps {
  user: User
  isSelected: boolean
  hasActions: boolean
  canEdit: boolean
  shouldShowAvatar: boolean
  onUserClick: (user: User) => void
  onEditStart: () => void
}

// ❌ Bad
interface UserCardProps {
  u: User                    // Too short
  selected: boolean          // Missing 'is' prefix
  ShowActions: boolean       // Wrong case
  editCallback: () => void   // Inconsistent naming
}

/**
 * CONSTANTS
 * - Use UPPER_SNAKE_CASE for constants
 * - Group related constants in objects
 */

// ✅ Good
const API_BASE_URL = 'https://api.example.com'
const MAX_RETRY_ATTEMPTS = 3
const DEFAULT_TIMEOUT = 5000

const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  MODERATOR: 'moderator',
} as const

// ❌ Bad
const apiUrl = 'https://api.example.com'  // Wrong case
const maxRetries = 3                      // Wrong case

/**
 * FUNCTIONS AND METHODS
 * - Use camelCase for function names
 * - Use verb-based names that describe action
 * - Use consistent prefixes (handle, on, get, set, is, has)
 */

// ✅ Good
const handleUserClick = (user: User) => {}
const getUserById = (id: string) => {}
const isValidEmail = (email: string) => boolean
const hasPermission = (user: User, permission: string) => boolean
const validateForm = (data: FormData) => ValidationResult

// ❌ Bad
const userClick = (user: User) => {}      // Missing 'handle'
const user = (id: string) => {}           // Not descriptive
const checkEmail = (email: string) => {}  // Inconsistent prefix

/**
 * FILES AND DIRECTORIES
 * - Use kebab-case for file names
 * - Use PascalCase for component files
 * - Use descriptive directory names
 */

// ✅ Good
components/
  user-profile/
    UserProfile.tsx
    UserProfile.test.tsx
    UserProfile.stories.tsx
    user-profile.module.css
  navigation/
    NavigationBar.tsx
    navigation-item.component.tsx

// ❌ Bad
components/
  userProfile.tsx           // Wrong case
  UserProfile.component.tsx // Redundant suffix
  nav.tsx                   // Too abbreviated
```

### Code Organization

```typescript
// File organization template
/**
 * Component file structure
 * 1. Imports (external → internal → relative)
 * 2. Types and interfaces
 * 3. Constants
 * 4. Component implementation
 * 5. Styled components (if using styled-components)
 * 6. Default export
 */

// 1. External imports
import React, { useState, useCallback, useMemo } from 'react'
import { clsx } from 'clsx'
import { motion } from 'framer-motion'

// 2. Internal imports
import { Button } from '@/components/ui'
import { useApi } from '@/hooks/use-api'
import { validateEmail } from '@/utils/validation'

// 3. Relative imports
import { UserAvatar } from './UserAvatar'
import { UserActions } from './UserActions'
import styles from './user-profile.module.css'

// 4. Types and interfaces
interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

interface UserProfileProps {
  user: User
  editable?: boolean
  onUpdate?: (user: User) => void
  className?: string
}

// 5. Constants
const ANIMATION_DURATION = 0.3
const MAX_NAME_LENGTH = 100

const USER_ACTIONS = {
  EDIT: 'edit',
  DELETE: 'delete',
  VIEW: 'view',
} as const

// 6. Component implementation
const UserProfile: React.FC<UserProfileProps> = ({
  user,
  editable = false,
  onUpdate,
  className,
}) => {
  // State declarations
  const [isEditing, setIsEditing] = useState(false)
  const [localUser, setLocalUser] = useState(user)

  // Custom hooks
  const { updateUser, loading } = useApi()

  // Computed values
  const isValid = useMemo(() => {
    return validateEmail(localUser.email) && 
           localUser.name.length > 0 && 
           localUser.name.length <= MAX_NAME_LENGTH
  }, [localUser.email, localUser.name])

  // Event handlers
  const handleEdit = useCallback(() => {
    setIsEditing(true)
  }, [])

  const handleSave = useCallback(async () => {
    if (!isValid) return

    try {
      const updated = await updateUser(user.id, localUser)
      onUpdate?.(updated)
      setIsEditing(false)
    } catch (error) {
      console.error('Failed to update user:', error)
    }
  }, [user.id, localUser, isValid, updateUser, onUpdate])

  const handleCancel = useCallback(() => {
    setLocalUser(user)
    setIsEditing(false)
  }, [user])

  // Render helpers
  const renderEditForm = () => (
    <form onSubmit={(e) => { e.preventDefault(); handleSave() }}>
      <input
        type="text"
        value={localUser.name}
        onChange={(e) => setLocalUser(prev => ({ ...prev, name: e.target.value }))}
        maxLength={MAX_NAME_LENGTH}
      />
      <input
        type="email"
        value={localUser.email}
        onChange={(e) => setLocalUser(prev => ({ ...prev, email: e.target.value }))}
      />
      <div className={styles.actions}>
        <Button type="submit" disabled={!isValid || loading}>
          Save
        </Button>
        <Button variant="secondary" onClick={handleCancel}>
          Cancel
        </Button>
      </div>
    </form>
  )

  const renderDisplayMode = () => (
    <div className={styles.display}>
      <UserAvatar user={user} size="large" />
      <div className={styles.info}>
        <h2>{user.name}</h2>
        <p>{user.email}</p>
      </div>
      {editable && (
        <UserActions onEdit={handleEdit} onDelete={() => {}} />
      )}
    </div>
  )

  // Main render
  return (
    <motion.div
      className={clsx(styles.container, className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: ANIMATION_DURATION }}
    >
      {isEditing ? renderEditForm() : renderDisplayMode()}
    </motion.div>
  )
}

// 7. Default export
export default UserProfile

// Named exports for testing
export { USER_ACTIONS }
export type { UserProfileProps }
```

### CSS/Styling Guidelines

```css
/* CSS organization and naming conventions */

/* 1. CSS Custom Properties (CSS Variables) */
:root {
  /* Color system */
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-900: #1e3a8a;
  
  /* Typography scale */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  
  /* Spacing scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-8: 2rem;
  
  /* Animation */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

/* 2. Component styles with BEM naming */
.user-profile {
  /* Component root styles */
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-4);
  border-radius: 0.5rem;
  box-shadow: var(--shadow-md);
  background-color: white;
}

.user-profile--editable {
  /* Modifier for editable state */
  border: 2px solid var(--color-primary-200);
}

.user-profile__header {
  /* Element styles */
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.user-profile__avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  object-fit: cover;
}

.user-profile__info {
  flex: 1;
}

.user-profile__name {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-gray-900);
}

.user-profile__email {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-gray-600);
}

.user-profile__actions {
  display: flex;
  gap: var(--space-2);
}

/* 3. State variations */
.user-profile[data-loading="true"] {
  opacity: 0.6;
  pointer-events: none;
}

.user-profile[data-error="true"] {
  border-color: var(--color-red-300);
  background-color: var(--color-red-50);
}

/* 4. Responsive design */
@media (max-width: 768px) {
  .user-profile {
    padding: var(--space-2);
  }
  
  .user-profile__header {
    flex-direction: column;
    text-align: center;
  }
  
  .user-profile__actions {
    justify-content: center;
  }
}

/* 5. Dark mode support */
@media (prefers-color-scheme: dark) {
  .user-profile {
    background-color: var(--color-gray-800);
    color: var(--color-gray-100);
  }
  
  .user-profile__name {
    color: var(--color-gray-100);
  }
  
  .user-profile__email {
    color: var(--color-gray-300);
  }
}

/* 6. Animation and transitions */
.user-profile {
  transition: all var(--duration-normal) ease;
}

.user-profile:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.user-profile__avatar {
  transition: transform var(--duration-fast) ease;
}

.user-profile__avatar:hover {
  transform: scale(1.05);
}
```

### Tailwind CSS Guidelines

```typescript
// Tailwind CSS class organization
const buttonVariants = {
  // Base styles - always applied
  base: [
    'inline-flex items-center justify-center',
    'px-4 py-2',
    'text-sm font-medium',
    'border border-transparent',
    'rounded-md',
    'transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
  ],
  
  // Variant styles
  variants: {
    primary: [
      'text-white bg-blue-600',
      'hover:bg-blue-700',
      'focus:ring-blue-500',
    ],
    secondary: [
      'text-blue-700 bg-blue-100',
      'hover:bg-blue-200',
      'focus:ring-blue-500',
    ],
    danger: [
      'text-white bg-red-600',
      'hover:bg-red-700',
      'focus:ring-red-500',
    ],
  },
  
  // Size variations
  sizes: {
    sm: ['px-3 py-1.5', 'text-xs'],
    md: ['px-4 py-2', 'text-sm'],
    lg: ['px-6 py-3', 'text-base'],
  },
}

// Usage in component
const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  size = 'md', 
  className, 
  ...props 
}) => {
  const classes = clsx(
    buttonVariants.base,
    buttonVariants.variants[variant],
    buttonVariants.sizes[size],
    className
  )
  
  return <button className={classes} {...props} />
}

// Custom Tailwind configuration
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      // Custom color palette
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      
      // Custom spacing
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      
      // Custom fonts
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      
      // Custom animations
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

## Documentation Tools

### Storybook Configuration

```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/react-webpack5'

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
    '@storybook/addon-docs',
  ],
  framework: {
    name: '@storybook/react-webpack5',
    options: {},
  },
  docs: {
    autodocs: 'tag',
  },
  typescript: {
    check: false,
    reactDocgen: 'react-docgen-typescript',
    reactDocgenTypescriptOptions: {
      shouldExtractLiteralValuesFromEnum: true,
      propFilter: (prop) => (prop.parent ? !/node_modules/.test(prop.parent.fileName) : true),
    },
  },
}

export default config

// Component story example
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants and states.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'danger', 'ghost'],
      description: 'Visual style variant',
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large'],
      description: 'Button size',
    },
    loading: {
      control: { type: 'boolean' },
      description: 'Show loading spinner',
    },
    disabled: {
      control: { type: 'boolean' },
      description: 'Disable button interaction',
    },
  },
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
}

export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
  },
}

export const Loading: Story = {
  args: {
    children: 'Loading Button',
    variant: 'primary',
    loading: true,
  },
}

export const Disabled: Story = {
  args: {
    children: 'Disabled Button',
    variant: 'primary',
    disabled: true,
  },
}

// Interactive story with controls
export const Interactive: Story = {
  args: {
    children: 'Interactive Button',
    variant: 'primary',
    size: 'medium',
  },
  render: (args) => (
    <Button {...args} onClick={() => alert('Button clicked!')}>
      {args.children}
    </Button>
  ),
}
```

### JSDoc Standards

```typescript
// JSDoc documentation standards
/**
 * Calculates the total price including tax and discounts
 * 
 * @param basePrice - The base price before tax and discounts
 * @param taxRate - Tax rate as a decimal (e.g., 0.08 for 8%)
 * @param discount - Discount configuration
 * @param discount.type - Type of discount ('percentage' | 'fixed')
 * @param discount.value - Discount value (percentage as decimal or fixed amount)
 * @returns The final price after tax and discounts
 * 
 * @example
 * Calculate price with percentage discount:
 * ```typescript
 * const price = calculateTotalPrice(100, 0.08, { type: 'percentage', value: 0.1 })
 * console.log(price) // 97.2 (100 - 10% discount + 8% tax)
 * ```
 * 
 * @example
 * Calculate price with fixed discount:
 * ```typescript
 * const price = calculateTotalPrice(100, 0.08, { type: 'fixed', value: 15 })
 * console.log(price) // 91.8 (100 - 15 + 8% tax)
 * ```
 * 
 * @throws {Error} When basePrice is negative
 * @throws {Error} When taxRate is not between 0 and 1
 * @throws {Error} When discount value is invalid for its type
 * 
 * @since 1.2.0
 * @see {@link https://example.com/pricing-docs} for pricing documentation
 */
function calculateTotalPrice(
  basePrice: number,
  taxRate: number,
  discount: { type: 'percentage' | 'fixed'; value: number }
): number {
  // Validation
  if (basePrice < 0) {
    throw new Error('Base price cannot be negative')
  }
  
  if (taxRate < 0 || taxRate > 1) {
    throw new Error('Tax rate must be between 0 and 1')
  }
  
  // Calculate discount
  let discountAmount = 0
  if (discount.type === 'percentage') {
    if (discount.value < 0 || discount.value > 1) {
      throw new Error('Percentage discount must be between 0 and 1')
    }
    discountAmount = basePrice * discount.value
  } else {
    if (discount.value < 0) {
      throw new Error('Fixed discount cannot be negative')
    }
    discountAmount = Math.min(discount.value, basePrice)
  }
  
  // Calculate final price
  const priceAfterDiscount = basePrice - discountAmount
  const finalPrice = priceAfterDiscount * (1 + taxRate)
  
  return Math.round(finalPrice * 100) / 100 // Round to 2 decimal places
}
```

This comprehensive documentation and style guide provides the foundation for creating maintainable, well-documented React projects with consistent coding standards and clear communication patterns.
