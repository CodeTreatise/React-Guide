# Design Systems & Component Libraries

## Table of Contents
1. [Design System Fundamentals](#design-system-fundamentals)
2. [Building a Component Library](#building-a-component-library)
3. [Design Tokens Implementation](#design-tokens-implementation)
4. [Component API Design](#component-api-design)
5. [Documentation & Storybook](#documentation--storybook)
6. [Testing Component Libraries](#testing-component-libraries)
7. [Distribution & Versioning](#distribution--versioning)
8. [Popular Component Libraries](#popular-component-libraries)

---

## Design System Fundamentals

### Design System Architecture

```javascript
// Design system structure
const designSystem = {
  tokens: {
    colors: {},
    typography: {},
    spacing: {},
    elevation: {},
    motion: {},
  },
  components: {
    primitives: [], // Button, Input, Text
    patterns: [],  // Card, Modal, Navigation
    layouts: [],   // Grid, Stack, Container
  },
  guidelines: {
    accessibility: {},
    usage: {},
    principles: {},
  }
}

// Token-based design system
const tokens = {
  color: {
    primitive: {
      neutral: {
        0: '#ffffff',
        100: '#f8f9fa',
        200: '#e9ecef',
        300: '#dee2e6',
        400: '#ced4da',
        500: '#adb5bd',
        600: '#6c757d',
        700: '#495057',
        800: '#343a40',
        900: '#212529',
      },
      blue: {
        50: '#e3f2fd',
        100: '#bbdefb',
        // ... more shades
        900: '#0d47a1',
      },
    },
    semantic: {
      background: {
        primary: 'neutral.0',
        secondary: 'neutral.100',
        tertiary: 'neutral.200',
      },
      text: {
        primary: 'neutral.900',
        secondary: 'neutral.700',
        tertiary: 'neutral.600',
        inverse: 'neutral.0',
      },
      action: {
        primary: 'blue.600',
        primaryHover: 'blue.700',
        secondary: 'neutral.200',
        disabled: 'neutral.400',
      },
      feedback: {
        success: '#28a745',
        warning: '#ffc107',
        error: '#dc3545',
        info: '#17a2b8',
      },
    },
  },
  typography: {
    fontFamily: {
      primary: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
      secondary: 'Georgia, serif',
      mono: 'Fira Code, Consolas, monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  elevation: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  motion: {
    duration: {
      fast: '150ms',
      normal: '250ms',
      slow: '350ms',
    },
    easing: {
      linear: 'linear',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
}
```

### Theme Provider Implementation

```jsx
import React, { createContext, useContext, useMemo } from 'react'

const ThemeContext = createContext()

export const ThemeProvider = ({ children, theme = tokens }) => {
  const contextValue = useMemo(() => ({
    tokens: theme,
    // Utility functions
    getColor: (path) => getTokenValue(theme.color, path),
    getSpacing: (value) => theme.spacing[value] || value,
    getTypography: (property, value) => theme.typography[property]?.[value],
  }), [theme])

  return (
    <ThemeContext.Provider value={contextValue}>
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

// Utility function to get nested token values
const getTokenValue = (obj, path) => {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

// CSS custom properties integration
export const CSSVariablesProvider = ({ children, theme }) => {
  useEffect(() => {
    const root = document.documentElement
    
    // Flatten tokens to CSS custom properties
    const flattenTokens = (obj, prefix = '') => {
      Object.entries(obj).forEach(([key, value]) => {
        const cssVar = `--${prefix}${key}`
        
        if (typeof value === 'object' && value !== null) {
          flattenTokens(value, `${prefix}${key}-`)
        } else {
          root.style.setProperty(cssVar, value)
        }
      })
    }
    
    flattenTokens(theme)
  }, [theme])
  
  return children
}
```

---

## Building a Component Library

### Base Component Architecture

```jsx
// Base component with forwardRef
import React, { forwardRef } from 'react'
import { useTheme } from '../theme'
import { cn } from '../utils'

// Button component
export const Button = forwardRef(({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  leftIcon,
  rightIcon,
  children,
  className,
  ...props
}, ref) => {
  const { getColor, getSpacing } = useTheme()
  
  const baseStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 500,
    borderRadius: '0.375rem',
    border: 'none',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    transition: 'all 150ms ease',
    outline: 'none',
    position: 'relative',
  }
  
  const variants = {
    primary: {
      backgroundColor: getColor('semantic.action.primary'),
      color: getColor('semantic.text.inverse'),
      '&:hover': !disabled && !loading && {
        backgroundColor: getColor('semantic.action.primaryHover'),
      },
      '&:focus': {
        boxShadow: `0 0 0 2px ${getColor('semantic.action.primary')}40`,
      },
    },
    secondary: {
      backgroundColor: getColor('semantic.action.secondary'),
      color: getColor('semantic.text.primary'),
      '&:hover': !disabled && !loading && {
        backgroundColor: getColor('primitive.neutral.300'),
      },
    },
    outline: {
      backgroundColor: 'transparent',
      color: getColor('semantic.action.primary'),
      border: `1px solid ${getColor('semantic.action.primary')}`,
      '&:hover': !disabled && !loading && {
        backgroundColor: getColor('semantic.action.primary'),
        color: getColor('semantic.text.inverse'),
      },
    },
    ghost: {
      backgroundColor: 'transparent',
      color: getColor('semantic.text.primary'),
      '&:hover': !disabled && !loading && {
        backgroundColor: getColor('primitive.neutral.100'),
      },
    },
  }
  
  const sizes = {
    sm: {
      padding: `${getSpacing('xs')} ${getSpacing('sm')}`,
      fontSize: '0.875rem',
      height: '2rem',
    },
    md: {
      padding: `${getSpacing('sm')} ${getSpacing('md')}`,
      fontSize: '0.875rem',
      height: '2.5rem',
    },
    lg: {
      padding: `${getSpacing('md')} ${getSpacing('lg')}`,
      fontSize: '1rem',
      height: '3rem',
    },
  }
  
  const disabledStyles = disabled && {
    opacity: 0.5,
    cursor: 'not-allowed',
  }
  
  const loadingStyles = loading && {
    color: 'transparent',
  }
  
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn('btn', `btn--${variant}`, `btn--${size}`, className)}
      style={{
        ...baseStyles,
        ...variants[variant],
        ...sizes[size],
        ...disabledStyles,
        ...loadingStyles,
      }}
      {...props}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Spinner size={sizes[size].height === '2rem' ? 'sm' : 'md'} />
        </div>
      )}
      
      {leftIcon && !loading && (
        <span className="mr-2 flex-shrink-0">
          {leftIcon}
        </span>
      )}
      
      {children}
      
      {rightIcon && !loading && (
        <span className="ml-2 flex-shrink-0">
          {rightIcon}
        </span>
      )}
    </button>
  )
})

Button.displayName = 'Button'
```

### Form Components

```jsx
// Input component with comprehensive features
export const Input = forwardRef(({
  label,
  helperText,
  error,
  leftAddon,
  rightAddon,
  leftIcon,
  rightIcon,
  size = 'md',
  variant = 'outline',
  disabled = false,
  required = false,
  className,
  ...props
}, ref) => {
  const { getColor, getSpacing } = useTheme()
  const [focused, setFocused] = useState(false)
  
  const inputId = useId()
  const helperTextId = useId()
  const errorId = useId()
  
  const baseStyles = {
    width: '100%',
    border: '1px solid',
    borderRadius: '0.375rem',
    transition: 'all 150ms ease',
    outline: 'none',
    fontFamily: 'inherit',
  }
  
  const variants = {
    outline: {
      backgroundColor: getColor('semantic.background.primary'),
      borderColor: error 
        ? getColor('semantic.feedback.error')
        : focused 
          ? getColor('semantic.action.primary')
          : getColor('primitive.neutral.300'),
      color: getColor('semantic.text.primary'),
      '&:focus': {
        borderColor: getColor('semantic.action.primary'),
        boxShadow: `0 0 0 1px ${getColor('semantic.action.primary')}`,
      },
    },
    filled: {
      backgroundColor: getColor('primitive.neutral.100'),
      borderColor: 'transparent',
      color: getColor('semantic.text.primary'),
      '&:focus': {
        backgroundColor: getColor('semantic.background.primary'),
        borderColor: getColor('semantic.action.primary'),
      },
    },
  }
  
  const sizes = {
    sm: {
      padding: `${getSpacing('xs')} ${getSpacing('sm')}`,
      fontSize: '0.875rem',
      height: '2rem',
    },
    md: {
      padding: `${getSpacing('sm')} ${getSpacing('md')}`,
      fontSize: '0.875rem',
      height: '2.5rem',
    },
    lg: {
      padding: `${getSpacing('md')} ${getSpacing('lg')}`,
      fontSize: '1rem',
      height: '3rem',
    },
  }
  
  const disabledStyles = disabled && {
    backgroundColor: getColor('primitive.neutral.100'),
    color: getColor('primitive.neutral.500'),
    cursor: 'not-allowed',
  }
  
  return (
    <div className={cn('input-group', className)}>
      {label && (
        <label 
          htmlFor={inputId}
          className={cn('input-label', required && 'required')}
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: 500,
            marginBottom: getSpacing('xs'),
            color: getColor('semantic.text.primary'),
          }}
        >
          {label}
          {required && (
            <span style={{ color: getColor('semantic.feedback.error'), marginLeft: '0.25rem' }}>
              *
            </span>
          )}
        </label>
      )}
      
      <div className="input-wrapper" style={{ position: 'relative' }}>
        {leftAddon && (
          <div className="input-left-addon">
            {leftAddon}
          </div>
        )}
        
        {leftIcon && (
          <div 
            className="input-left-icon"
            style={{
              position: 'absolute',
              left: getSpacing('sm'),
              top: '50%',
              transform: 'translateY(-50%)',
              color: getColor('primitive.neutral.500'),
              pointerEvents: 'none',
            }}
          >
            {leftIcon}
          </div>
        )}
        
        <input
          ref={ref}
          id={inputId}
          disabled={disabled}
          required={required}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          aria-describedby={
            [
              helperText && helperTextId,
              error && errorId,
            ].filter(Boolean).join(' ') || undefined
          }
          aria-invalid={error ? 'true' : undefined}
          className={cn('input', `input--${variant}`, `input--${size}`)}
          style={{
            ...baseStyles,
            ...variants[variant],
            ...sizes[size],
            ...disabledStyles,
            paddingLeft: leftIcon ? `calc(${getSpacing('sm')} + 1.25rem + ${getSpacing('xs')})` : undefined,
            paddingRight: rightIcon ? `calc(${getSpacing('sm')} + 1.25rem + ${getSpacing('xs')})` : undefined,
          }}
          {...props}
        />
        
        {rightIcon && (
          <div 
            className="input-right-icon"
            style={{
              position: 'absolute',
              right: getSpacing('sm'),
              top: '50%',
              transform: 'translateY(-50%)',
              color: getColor('primitive.neutral.500'),
              pointerEvents: 'none',
            }}
          >
            {rightIcon}
          </div>
        )}
        
        {rightAddon && (
          <div className="input-right-addon">
            {rightAddon}
          </div>
        )}
      </div>
      
      {error && (
        <div 
          id={errorId}
          role="alert"
          style={{
            marginTop: getSpacing('xs'),
            fontSize: '0.875rem',
            color: getColor('semantic.feedback.error'),
          }}
        >
          {error}
        </div>
      )}
      
      {helperText && !error && (
        <div 
          id={helperTextId}
          style={{
            marginTop: getSpacing('xs'),
            fontSize: '0.875rem',
            color: getColor('semantic.text.secondary'),
          }}
        >
          {helperText}
        </div>
      )}
    </div>
  )
})

Input.displayName = 'Input'
```

### Layout Components

```jsx
// Flexible layout components
export const Stack = ({ 
  direction = 'column',
  spacing = 'md',
  align = 'stretch',
  justify = 'flex-start',
  wrap = false,
  children,
  className,
  ...props 
}) => {
  const { getSpacing } = useTheme()
  
  const styles = {
    display: 'flex',
    flexDirection: direction,
    alignItems: align,
    justifyContent: justify,
    flexWrap: wrap ? 'wrap' : 'nowrap',
    gap: getSpacing(spacing),
  }
  
  return (
    <div 
      className={cn('stack', `stack--${direction}`, className)}
      style={styles}
      {...props}
    >
      {children}
    </div>
  )
}

export const Grid = ({ 
  columns = 1,
  spacing = 'md',
  minChildWidth,
  templateAreas,
  children,
  className,
  ...props 
}) => {
  const { getSpacing } = useTheme()
  
  const styles = {
    display: 'grid',
    gap: getSpacing(spacing),
    gridTemplateColumns: minChildWidth 
      ? `repeat(auto-fit, minmax(${minChildWidth}, 1fr))`
      : typeof columns === 'number' 
        ? `repeat(${columns}, 1fr)`
        : columns,
    gridTemplateAreas: templateAreas,
  }
  
  return (
    <div 
      className={cn('grid', className)}
      style={styles}
      {...props}
    >
      {children}
    </div>
  )
}

export const Container = ({ 
  size = 'md',
  centerContent = false,
  children,
  className,
  ...props 
}) => {
  const maxWidths = {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
    full: '100%',
  }
  
  const styles = {
    width: '100%',
    maxWidth: maxWidths[size],
    marginLeft: 'auto',
    marginRight: 'auto',
    paddingLeft: '1rem',
    paddingRight: '1rem',
    ...(centerContent && {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
    }),
  }
  
  return (
    <div 
      className={cn('container', `container--${size}`, className)}
      style={styles}
      {...props}
    >
      {children}
    </div>
  )
}
```

---

## Design Tokens Implementation

### Token Generation System

```javascript
// Token transformer
const transformTokens = (tokens, platform = 'web') => {
  const transforms = {
    web: {
      color: (value) => value,
      spacing: (value) => value,
      fontSize: (value) => value,
      shadow: (value) => value,
    },
    ios: {
      color: (value) => convertToUIColor(value),
      spacing: (value) => parseFloat(value.replace('rem', '')) * 16,
      fontSize: (value) => parseFloat(value.replace('rem', '')) * 16,
    },
    android: {
      color: (value) => convertToAndroidColor(value),
      spacing: (value) => `${parseFloat(value.replace('rem', '')) * 16}dp`,
      fontSize: (value) => `${parseFloat(value.replace('rem', '')) * 16}sp`,
    },
  }
  
  const platformTransforms = transforms[platform]
  
  const transformObject = (obj, path = '') => {
    const result = {}
    
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'object' && value !== null) {
        result[key] = transformObject(value, `${path}${key}.`)
      } else {
        const tokenType = getTokenType(path + key)
        const transform = platformTransforms[tokenType]
        result[key] = transform ? transform(value) : value
      }
    }
    
    return result
  }
  
  return transformObject(tokens)
}

// Token validation
const validateTokens = (tokens) => {
  const errors = []
  
  const validateObject = (obj, path = '') => {
    for (const [key, value] of Object.entries(obj)) {
      const currentPath = `${path}${key}`
      
      if (typeof value === 'object' && value !== null) {
        validateObject(value, `${currentPath}.`)
      } else {
        // Validate token format
        if (currentPath.includes('color') && !isValidColor(value)) {
          errors.push(`Invalid color token: ${currentPath} = ${value}`)
        }
        
        if (currentPath.includes('spacing') && !isValidSpacing(value)) {
          errors.push(`Invalid spacing token: ${currentPath} = ${value}`)
        }
        
        if (currentPath.includes('fontSize') && !isValidFontSize(value)) {
          errors.push(`Invalid font size token: ${currentPath} = ${value}`)
        }
      }
    }
  }
  
  validateObject(tokens)
  return errors
}

// Token documentation generator
const generateTokenDocs = (tokens) => {
  const generateMarkdown = (obj, level = 0) => {
    let markdown = ''
    const indent = '  '.repeat(level)
    
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'object' && value !== null) {
        markdown += `${indent}- **${key}**:\n`
        markdown += generateMarkdown(value, level + 1)
      } else {
        markdown += `${indent}- \`${key}\`: ${value}\n`
      }
    }
    
    return markdown
  }
  
  return `# Design Tokens\n\n${generateMarkdown(tokens)}`
}
```

### CSS Custom Properties Integration

```css
/* Auto-generated CSS custom properties */
:root {
  /* Colors */
  --color-primitive-neutral-0: #ffffff;
  --color-primitive-neutral-100: #f8f9fa;
  --color-primitive-neutral-200: #e9ecef;
  --color-primitive-neutral-300: #dee2e6;
  --color-primitive-neutral-400: #ced4da;
  --color-primitive-neutral-500: #adb5bd;
  --color-primitive-neutral-600: #6c757d;
  --color-primitive-neutral-700: #495057;
  --color-primitive-neutral-800: #343a40;
  --color-primitive-neutral-900: #212529;
  
  --color-semantic-background-primary: var(--color-primitive-neutral-0);
  --color-semantic-background-secondary: var(--color-primitive-neutral-100);
  --color-semantic-text-primary: var(--color-primitive-neutral-900);
  --color-semantic-text-secondary: var(--color-primitive-neutral-700);
  
  /* Typography */
  --font-family-primary: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Elevation */
  --elevation-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --elevation-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --elevation-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Dark theme */
[data-theme="dark"] {
  --color-semantic-background-primary: var(--color-primitive-neutral-900);
  --color-semantic-background-secondary: var(--color-primitive-neutral-800);
  --color-semantic-text-primary: var(--color-primitive-neutral-0);
  --color-semantic-text-secondary: var(--color-primitive-neutral-300);
}
```

---

## Component API Design

### Consistent API Patterns

```jsx
// Base props interface
interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
  testId?: string
  'aria-label'?: string
  'aria-labelledby'?: string
  'aria-describedby'?: string
}

// Size system
type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

// Variant system
type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'link'

// Color scheme
type ColorScheme = 'blue' | 'green' | 'red' | 'yellow' | 'purple' | 'gray'

// Component prop patterns
interface ButtonProps extends BaseComponentProps {
  variant?: Variant
  size?: Size
  colorScheme?: ColorScheme
  disabled?: boolean
  loading?: boolean
  leftIcon?: React.ReactElement
  rightIcon?: React.ReactElement
  loadingText?: string
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void
}

interface InputProps extends BaseComponentProps {
  variant?: 'outline' | 'filled' | 'flushed' | 'unstyled'
  size?: Size
  value?: string
  defaultValue?: string
  placeholder?: string
  disabled?: boolean
  readOnly?: boolean
  required?: boolean
  invalid?: boolean
  label?: string
  helperText?: string
  errorMessage?: string
  leftAddon?: React.ReactNode
  rightAddon?: React.ReactNode
  leftIcon?: React.ReactElement
  rightIcon?: React.ReactElement
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
}

// Polymorphic component pattern
interface PolymorphicProps<T extends React.ElementType> {
  as?: T
}

type ComponentProps<T extends React.ElementType> = PolymorphicProps<T> &
  Omit<React.ComponentPropsWithRef<T>, keyof PolymorphicProps<T>>

const PolymorphicComponent = <T extends React.ElementType = 'div'>({
  as,
  children,
  ...props
}: ComponentProps<T>) => {
  const Component = as || 'div'
  return <Component {...props}>{children}</Component>
}

// Compound component pattern
interface CardCompoundProps {
  Card: React.FC<CardProps>
  Header: React.FC<CardHeaderProps>
  Body: React.FC<CardBodyProps>
  Footer: React.FC<CardFooterProps>
}

const Card: React.FC<CardProps> & CardCompoundProps = ({ children, ...props }) => {
  return <div {...props}>{children}</div>
}

Card.Header = CardHeader
Card.Body = CardBody
Card.Footer = CardFooter
```

### Prop Validation & TypeScript

```typescript
// Runtime prop validation
import PropTypes from 'prop-types'

const Button = ({ variant, size, children, ...props }) => {
  // Component implementation
}

Button.propTypes = {
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'ghost']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
}

Button.defaultProps = {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
}

// Advanced TypeScript patterns
type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonStyleProps {
  variant: ButtonVariant
  size: ButtonSize
  colorScheme?: string
}

interface ButtonBehaviorProps {
  disabled?: boolean
  loading?: boolean
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void
}

interface ButtonContentProps {
  children: React.ReactNode
  leftIcon?: React.ReactElement
  rightIcon?: React.ReactElement
  loadingText?: string
}

type ButtonProps = ButtonStyleProps & 
  ButtonBehaviorProps & 
  ButtonContentProps & 
  Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onClick'>

// Generic component with constraints
interface SelectOption<T> {
  value: T
  label: string
  disabled?: boolean
}

interface SelectProps<T> {
  options: SelectOption<T>[]
  value?: T
  defaultValue?: T
  placeholder?: string
  onChange?: (value: T | undefined) => void
  multiple?: boolean
}

function Select<T extends string | number>({
  options,
  value,
  onChange,
  ...props
}: SelectProps<T>) {
  // Implementation
}
```

---

## Documentation & Storybook

### Storybook Configuration

```javascript
// .storybook/main.js
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-controls',
    '@storybook/addon-docs',
    '@storybook/addon-a11y',
    '@storybook/addon-viewport',
    '@storybook/addon-design-tokens',
  ],
  framework: '@storybook/react',
  features: {
    buildStoriesJson: true,
  },
}

// .storybook/preview.js
import { ThemeProvider } from '../src/theme'
import { tokens } from '../src/tokens'

export const decorators = [
  (Story) => (
    <ThemeProvider theme={tokens}>
      <Story />
    </ThemeProvider>
  ),
]

export const parameters = {
  actions: { argTypesRegex: '^on[A-Z].*' },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
  docs: {
    extractComponentDescription: (component, { notes }) => {
      if (notes) {
        return typeof notes === 'string' ? notes : notes.markdown || notes.text
      }
      return null
    },
  },
  viewport: {
    viewports: {
      mobile: {
        name: 'Mobile',
        styles: { width: '375px', height: '667px' },
      },
      tablet: {
        name: 'Tablet',
        styles: { width: '768px', height: '1024px' },
      },
      desktop: {
        name: 'Desktop',
        styles: { width: '1024px', height: '768px' },
      },
    },
  },
}
```

### Component Stories

```jsx
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'
import { Icon } from './Icon'

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants and sizes.',
      },
    },
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'outline', 'ghost'],
      description: 'The visual style variant of the button',
    },
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg'],
      description: 'The size of the button',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the button is disabled',
    },
    loading: {
      control: 'boolean',
      description: 'Whether the button is in a loading state',
    },
    children: {
      control: 'text',
      description: 'The content of the button',
    },
  },
  args: {
    children: 'Button',
  },
}

export default meta
type Story = StoryObj<typeof meta>

// Basic variants
export const Primary: Story = {
  args: {
    variant: 'primary',
  },
}

export const Secondary: Story = {
  args: {
    variant: 'secondary',
  },
}

export const Outline: Story = {
  args: {
    variant: 'outline',
  },
}

export const Ghost: Story = {
  args: {
    variant: 'ghost',
  },
}

// Sizes
export const Sizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
}

// States
export const States: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
      <Button>Normal</Button>
      <Button disabled>Disabled</Button>
      <Button loading>Loading</Button>
    </div>
  ),
}

// With icons
export const WithIcons: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
      <Button leftIcon={<Icon name="plus" />}>
        Add Item
      </Button>
      <Button rightIcon={<Icon name="arrow-right" />}>
        Continue
      </Button>
      <Button 
        leftIcon={<Icon name="download" />}
        rightIcon={<Icon name="external-link" />}
      >
        Download
      </Button>
    </div>
  ),
}

// Interactive example
export const Playground: Story = {
  args: {
    variant: 'primary',
    size: 'md',
    children: 'Interactive Button',
    disabled: false,
    loading: false,
  },
}
```

### Documentation Pages

```mdx
<!-- Button.mdx -->
import { Canvas, Meta, ArgTypes, Story } from '@storybook/blocks'
import * as ButtonStories from './Button.stories'

<Meta of={ButtonStories} />

# Button

The Button component is a fundamental interactive element that triggers actions when clicked.

## Usage

```jsx
import { Button } from '@company/design-system'

function App() {
  return <Button onClick={() => alert('Clicked!')}>Click me</Button>
}
```

## Variants

<Canvas of={ButtonStories.Primary} />
<Canvas of={ButtonStories.Secondary} />
<Canvas of={ButtonStories.Outline} />
<Canvas of={ButtonStories.Ghost} />

## Sizes

<Canvas of={ButtonStories.Sizes} />

## States

<Canvas of={ButtonStories.States} />

## With Icons

<Canvas of={ButtonStories.WithIcons} />

## Props

<ArgTypes of={ButtonStories} />

## Design Guidelines

### When to use
- For primary actions in forms and dialogs
- For navigation between pages or sections
- For triggering immediate actions

### When not to use
- For navigation that changes the URL (use Link instead)
- For toggling states (use Toggle or Switch instead)

### Accessibility
- Always provide meaningful text or aria-label
- Ensure sufficient color contrast
- Support keyboard navigation
- Provide loading states for async actions
```

---

## Testing Component Libraries

### Unit Testing Strategy

```jsx
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ThemeProvider } from '../theme'
import { Button } from './Button'

const renderWithTheme = (component) => {
  return render(
    <ThemeProvider>
      {component}
    </ThemeProvider>
  )
}

describe('Button', () => {
  it('renders with correct text', () => {
    renderWithTheme(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = jest.fn()
    renderWithTheme(<Button onClick={handleClick}>Click me</Button>)
    
    await userEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    renderWithTheme(<Button disabled>Click me</Button>)
    const button = screen.getByRole('button')
    
    expect(button).toBeDisabled()
    expect(button).toHaveAttribute('aria-disabled', 'true')
  })

  it('shows loading state', () => {
    renderWithTheme(<Button loading>Click me</Button>)
    const button = screen.getByRole('button')
    
    expect(button).toBeDisabled()
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('applies correct variant styles', () => {
    renderWithTheme(<Button variant="secondary">Click me</Button>)
    const button = screen.getByRole('button')
    
    expect(button).toHaveClass('btn--secondary')
  })

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLButtonElement>()
    renderWithTheme(<Button ref={ref}>Click me</Button>)
    
    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
  })

  it('supports keyboard navigation', async () => {
    const handleClick = jest.fn()
    renderWithTheme(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByRole('button')
    button.focus()
    
    await userEvent.keyboard('{Enter}')
    expect(handleClick).toHaveBeenCalledTimes(1)
    
    await userEvent.keyboard('{Space}')
    expect(handleClick).toHaveBeenCalledTimes(2)
  })
})
```

### Visual Regression Testing

```javascript
// Button.visual.test.js
import { test, expect } from '@playwright/test'

test.describe('Button Visual Tests', () => {
  test('button variants', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--variants')
    await expect(page).toHaveScreenshot('button-variants.png')
  })

  test('button sizes', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--sizes')
    await expect(page).toHaveScreenshot('button-sizes.png')
  })

  test('button states', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--states')
    await expect(page).toHaveScreenshot('button-states.png')
  })

  test('button hover state', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--primary')
    const button = page.getByRole('button')
    await button.hover()
    await expect(page).toHaveScreenshot('button-hover.png')
  })

  test('button focus state', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--primary')
    const button = page.getByRole('button')
    await button.focus()
    await expect(page).toHaveScreenshot('button-focus.png')
  })
})
```

### Accessibility Testing

```jsx
// a11y.test.tsx
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { Button } from './Button'

expect.extend(toHaveNoViolations)

describe('Button Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Accessible button</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('has correct ARIA attributes when loading', async () => {
    const { container } = render(<Button loading>Loading button</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('maintains accessibility with icons', async () => {
    const { container } = render(
      <Button leftIcon={<span aria-hidden="true">+</span>}>
        Add item
      </Button>
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

---

## Distribution & Versioning

### Build Configuration

```javascript
// rollup.config.js
import resolve from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'
import typescript from '@rollup/plugin-typescript'
import peerDepsExternal from 'rollup-plugin-peer-deps-external'
import { terser } from 'rollup-plugin-terser'

export default {
  input: 'src/index.ts',
  output: [
    {
      file: 'dist/index.js',
      format: 'cjs',
      sourcemap: true,
    },
    {
      file: 'dist/index.esm.js',
      format: 'esm',
      sourcemap: true,
    },
  ],
  plugins: [
    peerDepsExternal(),
    resolve(),
    commonjs(),
    typescript({ tsconfig: './tsconfig.json' }),
    terser(),
  ],
  external: ['react', 'react-dom'],
}

// package.json
{
  "name": "@company/design-system",
  "version": "1.0.0",
  "description": "A comprehensive React design system",
  "main": "dist/index.js",
  "module": "dist/index.esm.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist",
    "README.md"
  ],
  "peerDependencies": {
    "react": ">=16.8.0",
    "react-dom": ">=16.8.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^4.9.0"
  },
  "scripts": {
    "build": "rollup -c",
    "test": "jest",
    "test:visual": "playwright test",
    "storybook": "start-storybook -p 6006",
    "build-storybook": "build-storybook",
    "release": "semantic-release"
  }
}
```

### Semantic Versioning

```javascript
// .releaserc.json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github"
  ]
}

// Conventional commit types
// feat: A new feature
// fix: A bug fix
// docs: Documentation only changes
// style: Changes that do not affect the meaning of the code
// refactor: A code change that neither fixes a bug nor adds a feature
// perf: A code change that improves performance
// test: Adding missing tests or correcting existing tests
// chore: Changes to the build process or auxiliary tools

// Example commits:
// feat(button): add loading state support
// fix(input): resolve focus ring styling issue
// docs(readme): update installation instructions
// BREAKING CHANGE: remove deprecated size prop
```

---

## Popular Component Libraries

### Material-UI (MUI) Integration

```jsx
// Custom MUI theme
import { createTheme, ThemeProvider } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Inter, Roboto, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
        },
      },
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <YourApp />
    </ThemeProvider>
  )
}
```

### Ant Design Integration

```jsx
// Custom Ant Design theme
import { ConfigProvider, theme } from 'antd'

const customTheme = {
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorInfo: '#1890ff',
    colorTextBase: '#000000d9',
    colorBgBase: '#ffffff',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    fontSize: 14,
    borderRadius: 6,
  },
  components: {
    Button: {
      colorPrimary: '#1890ff',
      algorithm: theme.darkAlgorithm, // Enable dark algorithm
    },
    Input: {
      colorPrimary: '#1890ff',
    },
  },
}

function App() {
  return (
    <ConfigProvider theme={customTheme}>
      <YourApp />
    </ConfigProvider>
  )
}
```

### Creating Design System Adapters

```jsx
// Adapter pattern for multiple design systems
const createDesignSystemAdapter = (library) => {
  const adapters = {
    mui: {
      Button: ({ variant, size, children, ...props }) => (
        <MuiButton
          variant={variant === 'primary' ? 'contained' : 'outlined'}
          size={size}
          {...props}
        >
          {children}
        </MuiButton>
      ),
      Input: ({ label, error, ...props }) => (
        <TextField
          label={label}
          error={!!error}
          helperText={error}
          {...props}
        />
      ),
    },
    antd: {
      Button: ({ variant, size, children, ...props }) => (
        <AntButton
          type={variant === 'primary' ? 'primary' : 'default'}
          size={size}
          {...props}
        >
          {children}
        </AntButton>
      ),
      Input: ({ label, error, ...props }) => (
        <div>
          {label && <label>{label}</label>}
          <AntInput {...props} />
          {error && <div style={{ color: 'red' }}>{error}</div>}
        </div>
      ),
    },
  }
  
  return adapters[library]
}

// Usage
const DesignSystem = createDesignSystemAdapter('mui')

function App() {
  return (
    <div>
      <DesignSystem.Button variant="primary">
        Adapted Button
      </DesignSystem.Button>
      <DesignSystem.Input
        label="Email"
        error="Invalid email"
      />
    </div>
  )
}
```

This comprehensive guide covers design systems and component libraries, providing practical frameworks for building scalable, maintainable, and consistent user interfaces in React applications.
