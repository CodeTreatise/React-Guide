# Modern CSS Frameworks & Utility-First Approaches

## Table of Contents
1. [Tailwind CSS Integration](#tailwind-css-integration)
2. [Chakra UI Framework](#chakra-ui-framework)
3. [Mantine React Components](#mantine-react-components)
4. [Utility-First Design Patterns](#utility-first-design-patterns)
5. [Framework Performance Optimization](#framework-performance-optimization)
6. [Custom Framework Development](#custom-framework-development)
7. [Migration Strategies](#migration-strategies)
8. [Best Practices & Patterns](#best-practices--patterns)

---

## Tailwind CSS Integration

### Installation & Setup

```bash
# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install additional plugins
npm install -D @tailwindcss/forms @tailwindcss/typography @tailwindcss/aspect-ratio
```

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class', // or 'media'
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        gray: {
          750: '#374151',
          850: '#1f2937',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui'],
        'serif': ['ui-serif', 'Georgia'],
        'mono': ['Fira Code', 'ui-monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-soft': 'bounceSoft 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceSoft: {
          '0%, 20%, 50%, 80%, 100%': { transform: 'translateY(0)' },
          '40%': { transform: 'translateY(-5px)' },
          '60%': { transform: 'translateY(-3px)' },
        }
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### Advanced Tailwind Patterns

```jsx
// Component-based Tailwind patterns
import React from 'react'
import clsx from 'clsx'

// Variant-based component system
const Button = ({ 
  variant = 'primary', 
  size = 'md', 
  children, 
  disabled = false,
  loading = false,
  className = '',
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2'
  
  const variants = {
    primary: 'bg-brand-600 hover:bg-brand-700 text-white focus:ring-brand-500',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 focus:ring-gray-500',
    outline: 'border border-gray-300 hover:bg-gray-50 text-gray-700 focus:ring-gray-500',
    ghost: 'hover:bg-gray-100 text-gray-700 focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
  }
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
    xl: 'px-8 py-4 text-lg',
  }
  
  const disabledClasses = 'opacity-50 cursor-not-allowed pointer-events-none'
  
  return (
    <button
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        disabled && disabledClasses,
        loading && 'relative text-transparent',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      {children}
    </button>
  )
}

// Form components with Tailwind
const Input = ({ 
  label, 
  error, 
  helperText, 
  className = '', 
  ...props 
}) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <input
        className={clsx(
          'block w-full rounded-md shadow-sm',
          'border-gray-300 focus:border-brand-500 focus:ring-brand-500',
          'dark:border-gray-600 dark:bg-gray-700 dark:text-white',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
      {helperText && !error && (
        <p className="text-sm text-gray-500 dark:text-gray-400">{helperText}</p>
      )}
    </div>
  )
}

// Card component system
const Card = ({ children, className = '', padding = true, shadow = true }) => {
  return (
    <div
      className={clsx(
        'bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700',
        shadow && 'shadow-sm',
        padding && 'p-6',
        className
      )}
    >
      {children}
    </div>
  )
}

const CardHeader = ({ title, subtitle, action, className = '' }) => {
  return (
    <div className={clsx('flex items-center justify-between mb-4', className)}>
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {title}
        </h3>
        {subtitle && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
```

### Responsive Design Patterns

```jsx
{% raw %}
// Advanced responsive utilities
const ResponsiveGrid = ({ children }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
      {children}
    </div>
  )
}

// Responsive typography
const ResponsiveHeading = ({ level = 1, children, className = '' }) => {
  const Tag = `h${level}`
  const sizeClasses = {
    1: 'text-2xl sm:text-3xl lg:text-4xl xl:text-5xl',
    2: 'text-xl sm:text-2xl lg:text-3xl',
    3: 'text-lg sm:text-xl lg:text-2xl',
    4: 'text-base sm:text-lg lg:text-xl',
    5: 'text-sm sm:text-base lg:text-lg',
    6: 'text-xs sm:text-sm lg:text-base',
  }
  
  return (
    <Tag className={clsx(
      'font-bold text-gray-900 dark:text-white',
      sizeClasses[level],
      className
    )}>
      {children}
    </Tag>
  )
}

// Container patterns
const Container = ({ size = 'default', children, className = '' }) => {
  const sizeClasses = {
    sm: 'max-w-2xl',
    default: 'max-w-7xl',
    lg: 'max-w-screen-2xl',
    full: 'max-w-none',
  }
  
  return (
    <div className={clsx(
      'mx-auto px-4 sm:px-6 lg:px-8',
      sizeClasses[size],
      className
    )}>
      {children}
    </div>
  )
}
{% endraw %}
```

---

## Chakra UI Framework

### Setup & Configuration

```bash
# Install Chakra UI
npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion
```

```jsx
{% raw %}
// App.js - Provider setup
import React from 'react'
import { ChakraProvider, extendTheme } from '@chakra-ui/react'

// Custom theme
const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      50: '#e3f2f9',
      100: '#c5e4f3',
      200: '#a2d4ec',
      300: '#7ac1e4',
      400: '#47a9da',
      500: '#0088cc',
      600: '#007ab8',
      700: '#006ba1',
      800: '#005885',
      900: '#003f5e',
    },
  },
  fonts: {
    heading: 'Inter, sans-serif',
    body: 'Inter, sans-serif',
  },
  components: {
    Button: {
      defaultProps: {
        size: 'md',
        variant: 'solid',
      },
      variants: {
        solid: (props) => ({
          bg: `${props.colorScheme}.500`,
          color: 'white',
          _hover: {
            bg: `${props.colorScheme}.600`,
          },
          _active: {
            bg: `${props.colorScheme}.700`,
          },
        }),
        ghost: (props) => ({
          color: `${props.colorScheme}.500`,
          _hover: {
            bg: `${props.colorScheme}.50`,
          },
          _active: {
            bg: `${props.colorScheme}.100`,
          },
        }),
      },
    },
    Card: {
      baseStyle: {
        p: 6,
        borderRadius: 'lg',
        bg: 'white',
        boxShadow: 'sm',
        _dark: {
          bg: 'gray.800',
        },
      },
    },
  },
})

function App() {
  return (
    <ChakraProvider theme={theme}>
      <YourApp />
    </ChakraProvider>
  )
}
{% endraw %}
```

### Advanced Chakra Patterns

```jsx
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  Flex,
  Grid,
  GridItem,
  Heading,
  Stack,
  Text,
  useColorModeValue,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useToast,
  FormControl,
  FormLabel,
  FormErrorMessage,
  Input,
  VStack,
  HStack,
} from '@chakra-ui/react'

// Custom hooks for Chakra
const useCustomColors = () => {
  const bg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  const textColor = useColorModeValue('gray.800', 'white')
  const mutedColor = useColorModeValue('gray.600', 'gray.400')
  
  return { bg, borderColor, textColor, mutedColor }
}

// Reusable components
const CustomCard = ({ title, children, action, ...props }) => {
  const { bg, borderColor } = useCustomColors()
  
  return (
    <Card bg={bg} borderColor={borderColor} {...props}>
      <CardHeader pb={2}>
        <Flex justify="space-between" align="center">
          <Heading size="md">{title}</Heading>
          {action}
        </Flex>
      </CardHeader>
      <CardBody pt={2}>
        {children}
      </CardBody>
    </Card>
  )
}

// Form components
const CustomForm = ({ onSubmit, children }) => {
  const toast = useToast()
  
  const handleSubmit = async (data) => {
    try {
      await onSubmit(data)
      toast({
        title: 'Success',
        description: 'Form submitted successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Something went wrong',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }
  
  return (
    <Box as="form" onSubmit={handleSubmit}>
      <VStack spacing={4}>
        {children}
      </VStack>
    </Box>
  )
}

// Layout components
const DashboardLayout = ({ children }) => {
  const { bg } = useCustomColors()
  
  return (
    <Grid
      templateAreas={`"nav header"
                      "nav main"`}
      gridTemplateRows={'60px 1fr'}
      gridTemplateColumns={'250px 1fr'}
      h="100vh"
      gap="1"
      color="blackAlpha.700"
      fontWeight="bold"
    >
      <GridItem pl="2" bg="blue.300" area={'nav'}>
        Nav
      </GridItem>
      <GridItem pl="2" bg="green.300" area={'header'}>
        Header
      </GridItem>
      <GridItem pl="2" bg={bg} area={'main'}>
        {children}
      </GridItem>
    </Grid>
  )
}
```

### Responsive Breakpoints

```jsx
// Responsive utilities
const ResponsiveBox = ({ children }) => {
  return (
    <Box
      w={{ base: "100%", md: "80%", lg: "60%" }}
      p={{ base: 4, md: 6, lg: 8 }}
      mx="auto"
    >
      {children}
    </Box>
  )
}

// Responsive grid system
const ResponsiveGrid = ({ children }) => {
  return (
    <Grid
      templateColumns={{
        base: "1fr",
        md: "repeat(2, 1fr)",
        lg: "repeat(3, 1fr)",
        xl: "repeat(4, 1fr)"
      }}
      gap={{ base: 4, md: 6 }}
    >
      {children}
    </Grid>
  )
}

// Show/hide components
const ResponsiveNavigation = () => {
  return (
    <>
      {/* Mobile menu */}
      <Box display={{ base: "block", md: "none" }}>
        <MobileMenu />
      </Box>
      
      {/* Desktop navigation */}
      <Box display={{ base: "none", md: "block" }}>
        <DesktopNav />
      </Box>
    </>
  )
}
```

---

## Mantine React Components

### Installation & Setup

```bash
npm install @mantine/core @mantine/hooks @mantine/form @mantine/dates
npm install @tabler/icons-react
```

```jsx
// App.js
import { MantineProvider, createTheme } from '@mantine/core'
import '@mantine/core/styles.css'

const theme = createTheme({
  primaryColor: 'blue',
  fontFamily: 'Inter, sans-serif',
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
  },
  spacing: {
    xs: '0.5rem',
    sm: '0.75rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  radius: {
    xs: '0.125rem',
    sm: '0.25rem',
    md: '0.5rem',
    lg: '1rem',
  },
  components: {
    Button: {
      defaultProps: {
        size: 'md',
        variant: 'filled',
      },
    },
    Input: {
      styles: {
        input: {
          '&:focus': {
            borderColor: 'var(--mantine-color-blue-6)',
          },
        },
      },
    },
  },
})

function App() {
  return (
    <MantineProvider theme={theme}>
      <YourApp />
    </MantineProvider>
  )
}
```

### Advanced Mantine Components

```jsx
import {
  AppShell,
  Button,
  Card,
  Container,
  Grid,
  Group,
  Input,
  Loader,
  Modal,
  Paper,
  Stack,
  Text,
  TextInput,
  Title,
  useMantineTheme,
  rem,
} from '@mantine/core'
import { useForm } from '@mantine/form'
import { useDisclosure } from '@mantine/hooks'
import { notifications } from '@mantine/notifications'

// Custom components
const CustomCard = ({ title, children, loading = false }) => {
  const theme = useMantineTheme()
  
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Card.Section withBorder inheritPadding py="xs">
        <Group justify="space-between">
          <Title order={4}>{title}</Title>
          {loading && <Loader size="sm" />}
        </Group>
      </Card.Section>
      
      <Card.Section inheritPadding mt="sm" pb="md">
        {children}
      </Card.Section>
    </Card>
  )
}

// Form with validation
const UserForm = ({ onSubmit, initialValues = {} }) => {
  const form = useForm({
    initialValues: {
      name: '',
      email: '',
      age: 18,
      ...initialValues,
    },
    validate: {
      name: (value) => (value.length < 2 ? 'Name must have at least 2 letters' : null),
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
      age: (value) => (value < 18 ? 'Age must be at least 18' : null),
    },
  })
  
  const handleSubmit = async (values) => {
    try {
      await onSubmit(values)
      notifications.show({
        title: 'Success',
        message: 'User created successfully',
        color: 'green',
      })
      form.reset()
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: error.message || 'Something went wrong',
        color: 'red',
      })
    }
  }
  
  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <Stack gap="md">
        <TextInput
          withAsterisk
          label="Name"
          placeholder="Enter your name"
          {...form.getInputProps('name')}
        />
        
        <TextInput
          withAsterisk
          label="Email"
          placeholder="your@email.com"
          {...form.getInputProps('email')}
        />
        
        <Button type="submit" loading={form.isSubmitting}>
          Submit
        </Button>
      </Stack>
    </form>
  )
}

// Layout system
const DashboardShell = ({ children }) => {
  const [opened, { toggle }] = useDisclosure()
  
  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Button onClick={toggle} hiddenFrom="sm">
            Toggle
          </Button>
          <Title order={3}>Dashboard</Title>
        </Group>
      </AppShell.Header>
      
      <AppShell.Navbar p="md">
        <Text>Navigation items</Text>
      </AppShell.Navbar>
      
      <AppShell.Main>
        {children}
      </AppShell.Main>
    </AppShell>
  )
}
```

---

## Utility-First Design Patterns

### Composition Patterns

```jsx
{% raw %}
// Spacing utilities
const SpacingSystem = {
  Stack: ({ gap = 'md', children, ...props }) => (
    <div className={`space-y-${gap}`} {...props}>
      {children}
    </div>
  ),
  
  Inline: ({ gap = 'md', children, ...props }) => (
    <div className={`flex items-center space-x-${gap}`} {...props}>
      {children}
    </div>
  ),
  
  Grid: ({ cols = 1, gap = 'md', children, ...props }) => (
    <div className={`grid grid-cols-${cols} gap-${gap}`} {...props}>
      {children}
    </div>
  ),
}

// Typography utilities
const Typography = {
  Heading: ({ level = 1, size, children, ...props }) => {
    const Tag = `h${level}`
    const sizeClass = size || {
      1: 'text-4xl',
      2: 'text-3xl',
      3: 'text-2xl',
      4: 'text-xl',
      5: 'text-lg',
      6: 'text-base',
    }[level]
    
    return (
      <Tag className={`font-bold ${sizeClass}`} {...props}>
        {children}
      </Tag>
    )
  },
  
  Text: ({ size = 'base', weight = 'normal', color = 'gray-900', children, ...props }) => (
    <p className={`text-${size} font-${weight} text-${color}`} {...props}>
      {children}
    </p>
  ),
  
  Code: ({ children, ...props }) => (
    <code className="px-1 py-0.5 bg-gray-100 rounded text-sm font-mono" {...props}>
      {children}
    </code>
  ),
}

// Layout utilities
const Layout = {
  Container: ({ size = 'default', children, ...props }) => {
    const sizeClasses = {
      sm: 'max-w-2xl',
      default: 'max-w-4xl',
      lg: 'max-w-6xl',
      xl: 'max-w-7xl',
      full: 'max-w-none',
    }
    
    return (
      <div className={`mx-auto px-4 ${sizeClasses[size]}`} {...props}>
        {children}
      </div>
    )
  },
  
  Section: ({ padding = 'default', children, ...props }) => {
    const paddingClasses = {
      none: '',
      sm: 'py-8',
      default: 'py-16',
      lg: 'py-24',
    }
    
    return (
      <section className={paddingClasses[padding]} {...props}>
        {children}
      </section>
    )
  },
  
  Flex: ({ direction = 'row', align = 'start', justify = 'start', children, ...props }) => (
    <div 
      className={`flex flex-${direction} items-${align} justify-${justify}`} 
      {...props}
    >
      {children}
    </div>
  ),
}
{% endraw %}
```

### Responsive Utility Patterns

```jsx
{% raw %}
// Responsive visibility
const ResponsiveUtilities = {
  Show: ({ above, below, children }) => {
    let classes = ''
    if (above) classes += ` hidden ${above}:block`
    if (below) classes += ` ${below}:hidden`
    
    return <div className={classes}>{children}</div>
  },
  
  Hide: ({ above, below, children }) => {
    let classes = ''
    if (above) classes += ` ${above}:hidden`
    if (below) classes += ` hidden ${below}:block`
    
    return <div className={classes}>{children}</div>
  },
}

// Responsive spacing
const ResponsiveSpacing = {
  Stack: ({ gap, children }) => {
    const gapClass = typeof gap === 'object' 
      ? Object.entries(gap).map(([breakpoint, value]) => 
          breakpoint === 'base' ? `space-y-${value}` : `${breakpoint}:space-y-${value}`
        ).join(' ')
      : `space-y-${gap}`
    
    return <div className={gapClass}>{children}</div>
  },
  
  Padding: ({ p, children }) => {
    const paddingClass = typeof p === 'object'
      ? Object.entries(p).map(([breakpoint, value]) =>
          breakpoint === 'base' ? `p-${value}` : `${breakpoint}:p-${value}`
        ).join(' ')
      : `p-${p}`
    
    return <div className={paddingClass}>{children}</div>
  },
}
{% endraw %}
```

---

## Framework Performance Optimization

### Bundle Size Optimization

```javascript
// Tailwind CSS purging
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  // Enable tree-shaking
  purge: {
    enabled: true,
    content: [
      './src/**/*.{js,jsx,ts,tsx}',
      './public/index.html',
    ],
    // Safelist important classes
    safelist: [
      'bg-red-500',
      'text-3xl',
      'lg:text-4xl',
    ],
    // Custom extractors
    extractors: [
      {
        extractor: content => content.match(/[A-Za-z0-9-_:/]+/g) || [],
        extensions: ['html', 'js', 'jsx', 'ts', 'tsx'],
      }
    ],
  },
}

// Dynamic imports for large frameworks
const ChakraProvider = React.lazy(() => 
  import('@chakra-ui/react').then(module => ({
    default: module.ChakraProvider
  }))
)

const MantineProvider = React.lazy(() =>
  import('@mantine/core').then(module => ({
    default: module.MantineProvider
  }))
)

// Conditional loading
const App = () => {
  const [uiFramework, setUiFramework] = useState('tailwind')
  
  return (
    <Suspense fallback={<div>Loading...</div>}>
      {uiFramework === 'chakra' && (
        <ChakraProvider>
          <ChakraApp />
        </ChakraProvider>
      )}
      {uiFramework === 'mantine' && (
        <MantineProvider>
          <MantineApp />
        </MantineProvider>
      )}
      {uiFramework === 'tailwind' && <TailwindApp />}
    </Suspense>
  )
}
```

### Runtime Performance

```jsx
// Memoized components for heavy styling
const MemoizedCard = React.memo(({ title, content, theme }) => {
  const computedStyles = useMemo(() => {
    return generateComplexStyles(theme)
  }, [theme])
  
  return (
    <div style={computedStyles}>
      <h3>{title}</h3>
      <p>{content}</p>
    </div>
  )
})

// Virtualized styling for large lists
import { FixedSizeList as List } from 'react-window'

const VirtualizedStyledList = ({ items }) => {
  const Row = React.memo(({ index, style }) => {
    const item = items[index]
    
    return (
      <div
        style={style}
        className="flex items-center p-4 border-b hover:bg-gray-50"
      >
        <div className="flex-1">
          <h4 className="font-medium">{item.title}</h4>
          <p className="text-gray-600">{item.description}</p>
        </div>
      </div>
    )
  })
  
  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={80}
    >
      {Row}
    </List>
  )
}

// CSS-in-JS optimization
const useOptimizedStyles = (theme, dependencies) => {
  return useMemo(() => {
    return {
      container: {
        backgroundColor: theme.colors.background,
        padding: theme.spacing.md,
        borderRadius: theme.radius.md,
      },
      title: {
        fontSize: theme.fontSizes.lg,
        fontWeight: 'bold',
        color: theme.colors.text,
      },
    }
  }, [theme, ...dependencies])
}
```

---

## Custom Framework Development

### Building a Custom Design System

```jsx
{% raw %}
// Design tokens
const tokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      // ... more shades
      900: '#1e3a8a',
    },
    gray: {
      50: '#f9fafb',
      // ... more shades
      900: '#111827',
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  },
}

// Theme provider
const ThemeContext = React.createContext(tokens)

export const ThemeProvider = ({ children, theme = tokens }) => {
  return (
    <ThemeContext.Provider value={theme}>
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

// Component factory
const createComponent = (baseComponent, defaultProps = {}) => {
  return React.forwardRef((props, ref) => {
    const theme = useTheme()
    const mergedProps = { ...defaultProps, ...props, theme }
    
    return React.createElement(baseComponent, { ...mergedProps, ref })
  })
}

// Base components
const Box = createComponent(({ as = 'div', theme, ...props }) => {
  const Component = as
  return <Component {...props} />
})

const Button = createComponent(({ 
  variant = 'primary',
  size = 'md',
  theme,
  children,
  ...props 
}) => {
  const styles = {
    base: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: theme.borderRadius.md,
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.2s',
      border: 'none',
    },
    variants: {
      primary: {
        backgroundColor: theme.colors.primary[600],
        color: 'white',
      },
      secondary: {
        backgroundColor: theme.colors.gray[200],
        color: theme.colors.gray[900],
      },
    },
    sizes: {
      sm: {
        padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
        fontSize: theme.fontSizes.sm,
      },
      md: {
        padding: `${theme.spacing.sm} ${theme.spacing.md}`,
        fontSize: theme.fontSizes.base,
      },
      lg: {
        padding: `${theme.spacing.md} ${theme.spacing.lg}`,
        fontSize: theme.fontSizes.lg,
      },
    },
  }
  
  return (
    <button
      style={{
        ...styles.base,
        ...styles.variants[variant],
        ...styles.sizes[size],
      }}
      {...props}
    >
      {children}
    </button>
  )
})
{% endraw %}
```

### Component Composition System

```jsx
{% raw %}
// Compound component pattern
const Card = ({ children, className, ...props }) => {
  const theme = useTheme()
  
  return (
    <div
      className={clsx('card', className)}
      style={{
        backgroundColor: theme.colors.gray[50],
        borderRadius: theme.borderRadius.lg,
        boxShadow: theme.shadows.md,
        overflow: 'hidden',
      }}
      {...props}
    >
      {children}
    </div>
  )
}

const CardHeader = ({ children, className, ...props }) => {
  const theme = useTheme()
  
  return (
    <div
      className={clsx('card-header', className)}
      style={{
        padding: theme.spacing.lg,
        borderBottom: `1px solid ${theme.colors.gray[200]}`,
      }}
      {...props}
    >
      {children}
    </div>
  )
}

const CardBody = ({ children, className, ...props }) => {
  const theme = useTheme()
  
  return (
    <div
      className={clsx('card-body', className)}
      style={{
        padding: theme.spacing.lg,
      }}
      {...props}
    >
      {children}
    </div>
  )
}

const CardFooter = ({ children, className, ...props }) => {
  const theme = useTheme()
  
  return (
    <div
      className={clsx('card-footer', className)}
      style={{
        padding: theme.spacing.lg,
        borderTop: `1px solid ${theme.colors.gray[200]}`,
        backgroundColor: theme.colors.gray[25],
      }}
      {...props}
    >
      {children}
    </div>
  )
}

// Attach sub-components
Card.Header = CardHeader
Card.Body = CardBody
Card.Footer = CardFooter

// Usage
const ExampleCard = () => (
  <Card>
    <Card.Header>
      <h3>Card Title</h3>
    </Card.Header>
    <Card.Body>
      <p>Card content goes here</p>
    </Card.Body>
    <Card.Footer>
      <Button>Action</Button>
    </Card.Footer>
  </Card>
)
{% endraw %}
```

---

## Migration Strategies

### From CSS to Utility-First

```jsx
{% raw %}
// Before: Traditional CSS
/*
.button {
  padding: 12px 24px;
  background-color: #3b82f6;
  color: white;
  border-radius: 6px;
  font-weight: 500;
}

.button:hover {
  background-color: #2563eb;
}

.button--large {
  padding: 16px 32px;
  font-size: 18px;
}
*/

// After: Tailwind classes
const Button = ({ size = 'default', children, ...props }) => {
  const baseClasses = 'px-6 py-3 bg-blue-500 text-white rounded-md font-medium hover:bg-blue-600'
  const sizeClasses = {
    default: '',
    large: 'px-8 py-4 text-lg',
  }
  
  return (
    <button 
      className={`${baseClasses} ${sizeClasses[size]}`}
      {...props}
    >
      {children}
    </button>
  )
}

// Migration helper
const migrationMap = {
  '.button': 'px-6 py-3 bg-blue-500 text-white rounded-md font-medium hover:bg-blue-600',
  '.card': 'bg-white rounded-lg shadow-md p-6',
  '.container': 'max-w-4xl mx-auto px-4',
}

const convertCSSToTailwind = (cssClass) => {
  return migrationMap[cssClass] || cssClass
}
{% endraw %}
```

### Framework Migration

```jsx
// Migration wrapper component
const FrameworkMigrationWrapper = ({ 
  from, 
  to, 
  component: Component, 
  ...props 
}) => {
  const [migrated, setMigrated] = useState(false)
  
  useEffect(() => {
    // Gradual migration logic
    const timer = setTimeout(() => {
      setMigrated(true)
    }, 1000)
    
    return () => clearTimeout(timer)
  }, [])
  
  if (from === 'styled-components' && to === 'tailwind') {
    return migrated ? (
      <TailwindComponent {...props} />
    ) : (
      <StyledComponent {...props} />
    )
  }
  
  return <Component {...props} />
}

// Progressive migration
const useProgressiveMigration = (oldComponent, newComponent, feature = 'new-ui') => {
  const [shouldUseMigrated, setShouldUseMigrated] = useState(false)
  
  useEffect(() => {
    // Feature flag or A/B testing logic
    const isEnabled = localStorage.getItem(feature) === 'true'
    setShouldUseMigrated(isEnabled)
  }, [feature])
  
  return shouldUseMigrated ? newComponent : oldComponent
}
```

---

## Best Practices & Patterns

### Performance Best Practices

```jsx
{% raw %}
// 1. Conditional styling
const ConditionalStyling = ({ isActive, theme, children }) => {
  // ❌ Bad: Creates new object on every render
  const badStyle = {
    color: isActive ? theme.colors.primary : theme.colors.gray,
    backgroundColor: isActive ? theme.colors.primaryBg : 'transparent',
  }
  
  // ✅ Good: Memoized styles
  const goodStyle = useMemo(() => ({
    color: isActive ? theme.colors.primary : theme.colors.gray,
    backgroundColor: isActive ? theme.colors.primaryBg : 'transparent',
  }), [isActive, theme])
  
  return <div style={goodStyle}>{children}</div>
}

// 2. CSS custom properties for dynamic values
const DynamicTheming = ({ theme }) => {
  useEffect(() => {
    Object.entries(theme.colors).forEach(([key, value]) => {
      document.documentElement.style.setProperty(`--color-${key}`, value)
    })
  }, [theme])
  
  return (
    <div className="bg-[var(--color-primary)] text-[var(--color-text)]">
      Dynamic themed content
    </div>
  )
}

// 3. Lazy loading for large component libraries
const LazyMantineComponents = {
  Button: lazy(() => import('@mantine/core').then(m => ({ default: m.Button }))),
  Modal: lazy(() => import('@mantine/core').then(m => ({ default: m.Modal }))),
  Table: lazy(() => import('@mantine/core').then(m => ({ default: m.Table }))),
}

const ConditionalComponentLoader = ({ component: componentName, ...props }) => {
  const Component = LazyMantineComponents[componentName]
  
  return (
    <Suspense fallback={<div>Loading {componentName}...</div>}>
      <Component {...props} />
    </Suspense>
  )
}
{% endraw %}
```

### Accessibility Patterns

```jsx
{% raw %}
// Focus management
const AccessibleModal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef()
  const previousFocusRef = useRef()
  
  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement
      modalRef.current?.focus()
    } else {
      previousFocusRef.current?.focus()
    }
  }, [isOpen])
  
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }
  
  if (!isOpen) return null
  
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
      onClick={onClose}
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
      >
        {children}
      </div>
    </div>
  )
}

// High contrast mode support
const useHighContrast = () => {
  const [isHighContrast, setIsHighContrast] = useState(false)
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)')
    setIsHighContrast(mediaQuery.matches)
    
    const handler = (e) => setIsHighContrast(e.matches)
    mediaQuery.addEventListener('change', handler)
    
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])
  
  return isHighContrast
}

const AccessibleButton = ({ children, variant = 'primary', ...props }) => {
  const isHighContrast = useHighContrast()
  
  const baseClasses = 'px-4 py-2 rounded font-medium focus:outline-none focus:ring-2 focus:ring-offset-2'
  const variantClasses = {
    primary: isHighContrast 
      ? 'bg-black text-white border-2 border-white focus:ring-white'
      : 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-500',
    secondary: isHighContrast
      ? 'bg-white text-black border-2 border-black focus:ring-black'
      : 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
  }
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]}`}
      {...props}
    >
      {children}
    </button>
  )
}
{% endraw %}
```

### Testing Strategies

```jsx
// Component testing with styling
import { render, screen } from '@testing-library/react'
import { ThemeProvider } from './theme-provider'

const renderWithTheme = (component, theme = defaultTheme) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  )
}

describe('Button Component', () => {
  it('applies correct styles for primary variant', () => {
    renderWithTheme(<Button variant="primary">Click me</Button>)
    
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-blue-500')
    expect(button).toHaveClass('text-white')
  })
  
  it('responds to theme changes', () => {
    const customTheme = {
      ...defaultTheme,
      colors: { primary: '#ff0000' }
    }
    
    renderWithTheme(<Button variant="primary">Click me</Button>, customTheme)
    
    const button = screen.getByRole('button')
    expect(button).toHaveStyle('background-color: #ff0000')
  })
})

// Visual regression testing
import { chromatic } from '@chromatic-com/storybook'

export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    chromatic: { delay: 300 },
  },
}

export const AllVariants = () => (
  <div className="space-y-4">
    <Button variant="primary">Primary</Button>
    <Button variant="secondary">Secondary</Button>
    <Button variant="outline">Outline</Button>
  </div>
)

export const DarkMode = () => (
  <div className="dark bg-gray-900 p-8">
    <Button variant="primary">Dark Mode Button</Button>
  </div>
)
```

This comprehensive guide covers modern CSS frameworks and utility-first approaches for React applications, providing practical examples and best practices for building scalable, performant, and accessible user interfaces.
