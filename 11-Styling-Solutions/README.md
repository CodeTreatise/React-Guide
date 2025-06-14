# Module 11: Styling Solutions

## Learning Objectives
By the end of this module, you will be able to:
- Master modern CSS-in-JS solutions for React applications
- Implement component-based styling architectures
- Build responsive and accessible design systems
- Create dynamic themes and styling patterns
- Optimize styling performance and bundle size
- Handle complex animation and transition scenarios
- Implement design tokens and consistent styling
- Build cross-browser compatible styling solutions

## Overview
This module covers comprehensive styling strategies for modern React applications, from traditional CSS approaches to advanced CSS-in-JS solutions and design system implementation.

## Duration: Week 11 (40 hours)
- **Reading & Research**: 10 hours
- **Hands-on Practice**: 20 hours
- **Projects**: 8 hours
- **Assessment**: 2 hours

---

## Topics Covered

### 1. CSS-in-JS with Styled Components
```javascript
{% raw %}
import styled, { css, createGlobalStyle, ThemeProvider } from 'styled-components'

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    font-family: ${props => props.theme.fonts.body};
    color: ${props => props.theme.colors.text};
    background-color: ${props => props.theme.colors.background};
    transition: background-color 0.3s ease;
  }
`

// Theme configuration
const lightTheme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    text: '#212529',
    background: '#ffffff',
    surface: '#f8f9fa',
    border: '#dee2e6',
  },
  fonts: {
    body: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    heading: '"Poppins", sans-serif',
    mono: '"Fira Code", monospace',
  },
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
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
  breakpoints: {
    sm: '576px',
    md: '768px',
    lg: '992px',
    xl: '1200px',
  },
  shadows: {
    sm: '0 1px 3px rgba(0, 0, 0, 0.12)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px rgba(0, 0, 0, 0.1)',
  },
}

const darkTheme = {
  ...lightTheme,
  colors: {
    ...lightTheme.colors,
    text: '#f8f9fa',
    background: '#212529',
    surface: '#343a40',
    border: '#495057',
  },
}

// Advanced styled components
const Button = styled.button`
  /* Base styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: none;
  border-radius: 0.375rem;
  font-family: ${props => props.theme.fonts.body};
  font-size: ${props => props.theme.fontSizes.md};
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;

  /* Disabled state */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }

  /* Loading state */
  ${props => props.loading && css`
    color: transparent;
    
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  `}

  /* Variants */
  ${props => props.variant === 'primary' && css`
    background-color: ${props.theme.colors.primary};
    color: white;
    
    &:hover:not(:disabled) {
      background-color: ${darken(0.1, props.theme.colors.primary)};
      transform: translateY(-1px);
      box-shadow: ${props.theme.shadows.md};
    }
  `}

  ${props => props.variant === 'secondary' && css`
    background-color: transparent;
    color: ${props.theme.colors.primary};
    border: 1px solid ${props.theme.colors.primary};
    
    &:hover:not(:disabled) {
      background-color: ${props.theme.colors.primary};
      color: white;
    }
  `}

  ${props => props.variant === 'ghost' && css`
    background-color: transparent;
    color: ${props.theme.colors.text};
    
    &:hover:not(:disabled) {
      background-color: ${props.theme.colors.surface};
    }
  `}

  /* Sizes */
  ${props => props.size === 'sm' && css`
    padding: ${props.theme.spacing.xs} ${props.theme.spacing.sm};
    font-size: ${props.theme.fontSizes.sm};
  `}

  ${props => props.size === 'lg' && css`
    padding: ${props.theme.spacing.md} ${props.theme.spacing.lg};
    font-size: ${props.theme.fontSizes.lg};
  `}

  /* Full width */
  ${props => props.fullWidth && css`
    width: 100%;
  `}

  /* Animations */
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`

// Responsive container
const Container = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 ${props => props.theme.spacing.md};

  @media (min-width: ${props => props.theme.breakpoints.sm}) {
    padding: 0 ${props => props.theme.spacing.lg};
  }

  @media (min-width: ${props => props.theme.breakpoints.lg}) {
    padding: 0 ${props => props.theme.spacing.xl};
  }
`

// Grid system
const Grid = styled.div`
  display: grid;
  gap: ${props => props.gap || props.theme.spacing.md};
  
  ${props => props.columns && css`
    grid-template-columns: repeat(${props.columns}, 1fr);
  `}

  ${props => props.responsive && css`
    grid-template-columns: 1fr;
    
    @media (min-width: ${props.theme.breakpoints.md}) {
      grid-template-columns: repeat(2, 1fr);
    }
    
    @media (min-width: ${props.theme.breakpoints.lg}) {
      grid-template-columns: repeat(${props.responsive.lg || 3}, 1fr);
    }
  `}
`

// Card component with elevation
const Card = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border-radius: 0.5rem;
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
  transition: all 0.3s ease;

  ${props => props.hoverable && css`
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: ${props.theme.shadows.lg};
    }
  `}

  ${props => props.border && css`
    border: 1px solid ${props.theme.colors.border};
    box-shadow: none;
  `}
`
{% endraw %}
```

### 2. Emotion CSS-in-JS
```javascript
{% raw %}
/** @jsxImportSource @emotion/react */
import { css, Global, ThemeProvider } from '@emotion/react'
import styled from '@emotion/styled'
import { keyframes } from '@emotion/react'

// Global styles with Emotion
const globalStyles = css`
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    font-family: Inter, sans-serif;
    line-height: 1.6;
  }
`

// Keyframes animation
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

const slideIn = keyframes`
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
`

// Styled components with Emotion
const AnimatedCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  animation: ${fadeIn} 0.6s ease-out;
  
  &:hover {
    transform: scale(1.02);
    transition: transform 0.2s ease;
  }
`

// CSS prop usage
function Component() {
  return (
    <div
      css={css`
        display: flex;
        flex-direction: column;
        gap: 16px;
        
        ${/* Responsive styles */ ''}
        @media (min-width: 768px) {
          flex-direction: row;
        }
        
        ${/* Nested selectors */ ''}
        .title {
          font-size: 24px;
          font-weight: bold;
          color: #333;
        }
        
        .description {
          color: #666;
          line-height: 1.5;
        }
      `}
    >
      <h2 className="title">Card Title</h2>
      <p className="description">Card description</p>
    </div>
  )
}

// Dynamic styles based on props
const DynamicButton = styled.button`
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${props => {
    const { variant, theme } = props
    
    switch (variant) {
      case 'primary':
        return css`
          background-color: ${theme.colors.primary};
          color: white;
          
          &:hover {
            background-color: ${theme.colors.primaryDark};
          }
        `
      case 'secondary':
        return css`
          background-color: transparent;
          color: ${theme.colors.primary};
          border: 2px solid ${theme.colors.primary};
          
          &:hover {
            background-color: ${theme.colors.primary};
            color: white;
          }
        `
      default:
        return css`
          background-color: #f5f5f5;
          color: #333;
          
          &:hover {
            background-color: #e5e5e5;
          }
        `
    }
  }}
`
{% endraw %}
```

### 3. CSS Modules with Advanced Features
```css
/* Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius);
  font-family: var(--font-body);
  font-size: var(--font-size-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Variants */
.primary {
  background-color: var(--color-primary);
  color: white;
}

.primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.secondary:hover:not(:disabled) {
  background-color: var(--color-primary);
  color: white;
}

/* Sizes */
.small {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.large {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-lg);
}

/* States */
.loading {
  color: transparent;
  position: relative;
}

.loading::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes spin {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .button {
    width: 100%;
  }
}
```

```javascript
// Button.jsx
import styles from './Button.module.css'
import clsx from 'clsx'

function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  loading = false, 
  disabled = false,
  className,
  ...props 
}) {
  const buttonClasses = clsx(
    styles.button,
    styles[variant],
    styles[size],
    {
      [styles.loading]: loading,
    },
    className
  )

  return (
    <button
      className={buttonClasses}
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button
```

### 4. Tailwind CSS Integration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}

// Custom utility components
function Card({ children, className, hoverable = false, ...props }) {
  return (
    <div
      className={clsx(
        'bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700',
        hoverable && 'hover:shadow-md transition-shadow duration-200 cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false,
  disabled = false,
  className,
  ...props 
}) {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white focus:ring-primary-500',
    secondary: 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 focus:ring-primary-500',
    ghost: 'hover:bg-gray-100 text-gray-700 focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
  }
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  return (
    <button
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        loading && 'relative text-transparent',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg
          className="absolute inset-0 m-auto h-5 w-5 animate-spin text-current"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  )
}

// Dark mode toggle hook
function useDarkMode() {
  const [isDark, setIsDark] = useState(() => {
    // Check for saved preference or system preference
    const saved = localStorage.getItem('darkMode')
    if (saved !== null) {
      return JSON.parse(saved)
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDark))
    
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  return [isDark, setIsDark]
}
```

### 5. Design System Implementation
```javascript
{% raw %}
// Design tokens
export const tokens = {
  colors: {
    brand: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
    },
    gray: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
    semantic: {
      success: '#059669',
      warning: '#d97706',
      error: '#dc2626',
      info: '#2563eb',
    }
  },
  typography: {
    fontFamilies: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'Consolas', 'monospace'],
    },
    fontSizes: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
    },
    fontWeights: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeights: {
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    }
  },
  spacing: {
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    8: '2rem',
    10: '2.5rem',
    12: '3rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    base: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    full: '9999px',
  }
}

// Component system
const componentVariants = {
  button: {
    base: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: tokens.borderRadius.md,
      fontWeight: tokens.typography.fontWeights.medium,
      transition: 'all 0.2s ease',
      cursor: 'pointer',
      border: 'none',
      textDecoration: 'none',
    },
    variants: {
      primary: {
        backgroundColor: tokens.colors.brand[600],
        color: 'white',
        '&:hover': {
          backgroundColor: tokens.colors.brand[700],
        },
        '&:focus': {
          outline: 'none',
          boxShadow: `0 0 0 3px ${tokens.colors.brand[200]}`,
        }
      },
      secondary: {
        backgroundColor: 'transparent',
        color: tokens.colors.brand[600],
        border: `1px solid ${tokens.colors.brand[600]}`,
        '&:hover': {
          backgroundColor: tokens.colors.brand[50],
        }
      },
      ghost: {
        backgroundColor: 'transparent',
        color: tokens.colors.gray[700],
        '&:hover': {
          backgroundColor: tokens.colors.gray[100],
        }
      }
    },
    sizes: {
      sm: {
        padding: `${tokens.spacing[2]} ${tokens.spacing[3]}`,
        fontSize: tokens.typography.fontSizes.sm,
      },
      md: {
        padding: `${tokens.spacing[3]} ${tokens.spacing[4]}`,
        fontSize: tokens.typography.fontSizes.base,
      },
      lg: {
        padding: `${tokens.spacing[4]} ${tokens.spacing[6]}`,
        fontSize: tokens.typography.fontSizes.lg,
      }
    }
  }
}

// Style system hook
function useStyleSystem() {
  const getButtonStyles = (variant = 'primary', size = 'md', customStyles = {}) => {
    return {
      ...componentVariants.button.base,
      ...componentVariants.button.variants[variant],
      ...componentVariants.button.sizes[size],
      ...customStyles,
    }
  }

  const getSpacing = (space) => tokens.spacing[space]
  const getColor = (path) => path.split('.').reduce((obj, key) => obj[key], tokens.colors)
  const getFontSize = (size) => tokens.typography.fontSizes[size]

  return {
    tokens,
    getButtonStyles,
    getSpacing,
    getColor,
    getFontSize,
  }
}
{% endraw %}
```

### 6. Animation and Transitions
```javascript
// Advanced animation hooks and components
import { useSpring, animated, useTransition, useTrail } from '@react-spring/web'
import { useDrag } from '@use-gesture/react'

// Smooth entrance animations
function FadeInWhenVisible({ children, delay = 0 }) {
  const [ref, inView] = useInView({
    threshold: 0.1,
    triggerOnce: true,
  })

  const styles = useSpring({
    opacity: inView ? 1 : 0,
    transform: inView ? 'translateY(0px)' : 'translateY(50px)',
    delay: delay,
    config: { tension: 280, friction: 60 },
  })

  return (
    <animated.div ref={ref} style={styles}>
      {children}
    </animated.div>
  )
}

// Staggered list animations
function AnimatedList({ items, renderItem }) {
  const trail = useTrail(items.length, {
    from: { opacity: 0, transform: 'translate3d(0,40px,0)' },
    to: { opacity: 1, transform: 'translate3d(0,0px,0)' },
    config: { tension: 280, friction: 60 },
  })

  return (
    <div>
      {trail.map((style, index) => (
        <animated.div key={items[index].id} style={style}>
          {renderItem(items[index])}
        </animated.div>
      ))}
    </div>
  )
}

// Page transitions
function PageTransition({ children, location }) {
  const transitions = useTransition(location, {
    from: { opacity: 0, transform: 'translate3d(100%,0,0)' },
    enter: { opacity: 1, transform: 'translate3d(0%,0,0)' },
    leave: { opacity: 0, transform: 'translate3d(-50%,0,0)' },
    config: { tension: 280, friction: 60 },
  })

  return transitions((style, item) => (
    <animated.div style={{ ...style, position: 'absolute', width: '100%' }}>
      {children}
    </animated.div>
  ))
}

// Draggable components
function DraggableCard({ children, onDragEnd }) {
  const [{ x, y }, api] = useSpring(() => ({ x: 0, y: 0 }))

  const bind = useDrag(({ active, movement: [mx, my], memo = [x.get(), y.get()] }) => {
    api.start({
      x: active ? memo[0] + mx : 0,
      y: active ? memo[1] + my : 0,
      immediate: active,
      config: { tension: 500, friction: 50 },
    })

    if (!active && onDragEnd) {
      onDragEnd({ x: memo[0] + mx, y: memo[1] + my })
    }

    return memo
  })

  return (
    <animated.div
      {...bind()}
      style={{
        x,
        y,
        touchAction: 'none',
        cursor: 'grab',
      }}
    >
      {children}
    </animated.div>
  )
}

// Modal with backdrop animation
function AnimatedModal({ isOpen, onClose, children }) {
  const backdropTransition = useTransition(isOpen, {
    from: { opacity: 0 },
    enter: { opacity: 1 },
    leave: { opacity: 0 },
    config: { duration: 200 },
  })

  const modalTransition = useTransition(isOpen, {
    from: { opacity: 0, transform: 'scale(0.95)' },
    enter: { opacity: 1, transform: 'scale(1)' },
    leave: { opacity: 0, transform: 'scale(0.95)' },
    config: { tension: 300, friction: 30 },
  })

  return backdropTransition((backdropStyle, item) =>
    item ? (
      <animated.div
        style={{
          ...backdropStyle,
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}
        onClick={onClose}
      >
        {modalTransition((modalStyle, modalItem) =>
          modalItem ? (
            <animated.div
              style={{
                ...modalStyle,
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '24px',
                maxWidth: '500px',
                width: '90%',
                maxHeight: '80vh',
                overflow: 'auto',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {children}
            </animated.div>
          ) : null
        )}
      </animated.div>
    ) : null
  )
}
```

### 7. Performance Optimization
```javascript
{% raw %}
// CSS-in-JS performance optimization
import { memo, useMemo } from 'react'
import { css, cx } from '@emotion/css'

// Memoized style generation
const useOptimizedStyles = (theme, props) => {
  return useMemo(() => {
    const baseStyles = css`
      padding: ${theme.spacing.md};
      border-radius: ${theme.borderRadius.md};
      transition: all 0.2s ease;
    `

    const variantStyles = css`
      background-color: ${props.variant === 'primary' ? theme.colors.primary : theme.colors.secondary};
      color: ${props.variant === 'primary' ? 'white' : theme.colors.text};
    `

    const sizeStyles = css`
      font-size: ${theme.fontSizes[props.size || 'md']};
    `

    return cx(baseStyles, variantStyles, sizeStyles)
  }, [theme, props.variant, props.size])
}

// Optimized component with memo
const OptimizedButton = memo(({ children, ...props }) => {
  const theme = useTheme()
  const className = useOptimizedStyles(theme, props)

  return (
    <button className={className} {...props}>
      {children}
    </button>
  )
})

// CSS extraction for production
const extractCriticalCSS = (html) => {
  // Extract only the CSS that's actually used
  const usedSelectors = []
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  
  // Find all class names in use
  const elements = doc.querySelectorAll('*')
  elements.forEach(el => {
    if (el.className) {
      usedSelectors.push(...el.className.split(' '))
    }
  })

  // Filter CSS to only include used selectors
  return filterCSS(usedSelectors)
}

// Bundle size optimization
const lazyLoadStyles = (styleName) => {
  return import(`./styles/${styleName}.css`)
}

// Runtime style injection
const injectStyles = (css) => {
  const style = document.createElement('style')
  style.textContent = css
  document.head.appendChild(style)
  return () => document.head.removeChild(style)
}
{% endraw %}
```

---

## Best Practices

### 1. Styling Architecture
- Choose appropriate styling solution for project needs
- Maintain consistent design tokens and theme structure
- Implement proper component composition patterns
- Use CSS custom properties for dynamic theming
- Optimize for both development experience and runtime performance

### 2. Performance Guidelines
- Minimize CSS bundle size and runtime overhead
- Use CSS-in-JS efficiently with proper memoization
- Implement critical CSS extraction for SSR
- Optimize animation performance with transforms
- Use proper CSS containment and will-change properties

### 3. Responsive Design
- Design mobile-first with progressive enhancement
- Use flexible grid systems and container queries
- Implement proper breakpoint strategies
- Handle touch interactions and accessibility
- Test across different devices and screen sizes

### 4. Accessibility
- Ensure proper color contrast ratios
- Implement focus management and keyboard navigation
- Use semantic HTML and ARIA attributes
- Handle reduced motion preferences
- Test with screen readers and assistive technologies

---

## Projects

### Project 1: Design System Library
Build a comprehensive design system with:
- Component library with Storybook
- Design tokens and theming system
- Documentation and usage guidelines
- Accessibility compliance
- Multiple styling solutions support

### Project 2: Responsive Dashboard
Create a complex dashboard featuring:
- Multi-layout responsive design
- Dark/light theme switching
- Advanced data visualizations
- Interactive animations
- Performance optimizations

### Project 3: E-commerce Product Showcase
Develop a product showcase with:
- Image galleries with smooth transitions
- Filter animations and micro-interactions
- Mobile-optimized touch interactions
- Progressive loading and skeleton states
- Accessibility compliance

---

## Assessment Criteria

### Knowledge Check (40 points)
- Modern CSS-in-JS patterns and performance
- Design system architecture and implementation
- Responsive design principles and techniques
- Animation and transition best practices
- Accessibility and cross-browser compatibility

### Practical Skills (40 points)
- Implement efficient styling architectures
- Build responsive and accessible interfaces
- Create smooth animations and interactions
- Optimize styling performance
- Integrate design systems effectively

### Project Quality (20 points)
- Design consistency and visual appeal
- Code organization and maintainability
- Performance benchmarks
- Accessibility compliance
- Cross-browser compatibility

---

## Resources

### Essential Reading
- [Styled Components Documentation](https://styled-components.com/)
- [Emotion Documentation](https://emotion.sh/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [CSS Modules Guide](https://github.com/css-modules/css-modules)

### Advanced Resources
- [Design Systems Guide](https://www.designsystems.com/)
- [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)
- [CSS Containment](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Containment)
- [Responsive Design Patterns](https://web.dev/responsive-web-design-basics/)

### Tools and Libraries
- Styled Components
- Emotion
- Tailwind CSS
- React Spring
- Framer Motion
- Storybook
- PostCSS

---

## Next Steps
After completing this module, you'll be ready for Module 12: UI Patterns, where you'll learn advanced UI component patterns, accessibility implementation, and complex interaction designs.

The combination of modern styling solutions with proper UI patterns creates the foundation for building beautiful, accessible, and performant user interfaces.
