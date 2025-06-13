# CSS-in-JS Solutions & Modern Styling

## Table of Contents
1. [CSS-in-JS Fundamentals](#css-in-js-fundamentals)
2. [Styled Components Mastery](#styled-components-mastery)
3. [Emotion.js Deep Dive](#emotionjs-deep-dive)
4. [JSS (JavaScript Style Sheets)](#jss-javascript-style-sheets)
5. [Stitches Modern Styling](#stitches-modern-styling)
6. [CSS-in-JS Performance](#css-in-js-performance)
7. [Theming and Design Systems](#theming-and-design-systems)
8. [Server-Side Rendering](#server-side-rendering)
9. [Migration Strategies](#migration-strategies)
10. [Best Practices](#best-practices)

## CSS-in-JS Fundamentals

### Understanding CSS-in-JS

CSS-in-JS is a styling technique where CSS is composed using JavaScript instead of being defined in external files.

```typescript
// Traditional CSS approach
// styles.css
.button {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border-radius: 4px;
}

.button:hover {
  background-color: #0056b3;
}

// CSS-in-JS approach
const buttonStyles = {
  backgroundColor: '#007bff',
  color: 'white',
  padding: '10px 20px',
  borderRadius: '4px',
  '&:hover': {
    backgroundColor: '#0056b3'
  }
};

// Or with template literals
const Button = styled.button`
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border-radius: 4px;
  
  &:hover {
    background-color: #0056b3;
  }
`;
```

### Benefits and Trade-offs

```typescript
// Benefits of CSS-in-JS
interface CSSInJSBenefits {
  // 1. Component-scoped styles
  scoping: 'automatic'; // No global namespace pollution
  
  // 2. Dynamic styling based on props
  dynamicStyling: boolean;
  
  // 3. Dead code elimination
  treeshaking: boolean;
  
  // 4. TypeScript support
  typeSafety: boolean;
  
  // 5. Runtime theming
  runtimeTheming: boolean;
}

// Trade-offs to consider
interface CSSInJSTradeoffs {
  // Runtime overhead
  performanceImpact: 'small' | 'medium' | 'large';
  
  // Bundle size increase
  bundleSize: number; // in KB
  
  // Learning curve
  complexity: 'low' | 'medium' | 'high';
  
  // DevTools integration
  debugging: 'excellent' | 'good' | 'limited';
}

// Example: Dynamic styling with props
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'small' | 'medium' | 'large';
  disabled?: boolean;
}

const DynamicButton = styled.button<ButtonProps>`
  // Base styles
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  
  // Size variants
  ${props => {
    switch (props.size) {
      case 'small':
        return css`
          padding: 6px 12px;
          font-size: 14px;
        `;
      case 'large':
        return css`
          padding: 12px 24px;
          font-size: 18px;
        `;
      default:
        return css`
          padding: 8px 16px;
          font-size: 16px;
        `;
    }
  }}
  
  // Color variants
  ${props => {
    switch (props.variant) {
      case 'primary':
        return css`
          background-color: #007bff;
          color: white;
          &:hover:not(:disabled) {
            background-color: #0056b3;
          }
        `;
      case 'secondary':
        return css`
          background-color: #6c757d;
          color: white;
          &:hover:not(:disabled) {
            background-color: #545b62;
          }
        `;
      case 'danger':
        return css`
          background-color: #dc3545;
          color: white;
          &:hover:not(:disabled) {
            background-color: #c82333;
          }
        `;
    }
  }}
  
  // Disabled state
  ${props => props.disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
  `}
`;
```

## Styled Components Mastery

### Advanced Styled Components Patterns

```typescript
// Installation and setup
npm install styled-components
npm install --save-dev @types/styled-components

// Basic usage with TypeScript
import styled, { css, ThemeProvider } from 'styled-components';

// 1. Basic styled component
const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

// 2. Extending styles
const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
`;

const PrimaryButton = styled(Button)`
  background-color: #007bff;
  color: white;
  
  &:hover {
    background-color: #0056b3;
  }
`;

// 3. Styling existing components
interface ExistingButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  className?: string;
}

const ExistingButton: React.FC<ExistingButtonProps> = ({ 
  onClick, 
  children, 
  className 
}) => (
  <button className={className} onClick={onClick}>
    {children}
  </button>
);

const StyledExistingButton = styled(ExistingButton)`
  background-color: #28a745;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
`;

// 4. Complex prop-based styling
interface CardProps {
  elevation?: number;
  variant?: 'outlined' | 'filled';
  interactive?: boolean;
}

const Card = styled.div<CardProps>`
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  
  // Elevation (shadow)
  ${props => {
    const elevation = props.elevation || 1;
    return css`
      box-shadow: 0 ${elevation * 2}px ${elevation * 4}px rgba(0, 0, 0, 0.1);
    `;
  }}
  
  // Variant styles
  ${props => props.variant === 'outlined' && css`
    background-color: transparent;
    border: 1px solid #e0e0e0;
  `}
  
  // Interactive behavior
  ${props => props.interactive && css`
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 ${(props.elevation || 1) * 3}px ${(props.elevation || 1) * 6}px rgba(0, 0, 0, 0.15);
    }
  `}
`;

// 5. Advanced component composition
const FlexContainer = styled.div<{
  direction?: 'row' | 'column';
  justify?: 'flex-start' | 'center' | 'flex-end' | 'space-between' | 'space-around';
  align?: 'flex-start' | 'center' | 'flex-end' | 'stretch';
  gap?: number;
  wrap?: boolean;
}>`
  display: flex;
  flex-direction: ${props => props.direction || 'row'};
  justify-content: ${props => props.justify || 'flex-start'};
  align-items: ${props => props.align || 'stretch'};
  gap: ${props => props.gap || 0}px;
  flex-wrap: ${props => props.wrap ? 'wrap' : 'nowrap'};
`;

// 6. Mixin patterns
const truncateText = css`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const visuallyHidden = css`
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
`;

const Text = styled.p<{ truncate?: boolean; srOnly?: boolean }>`
  margin: 0;
  
  ${props => props.truncate && truncateText}
  ${props => props.srOnly && visuallyHidden}
`;

// 7. Animation utilities
import { keyframes } from 'styled-components';

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const slideIn = keyframes`
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
`;

const AnimatedContainer = styled.div<{ 
  animation?: 'fadeIn' | 'slideIn';
  duration?: number;
  delay?: number;
}>`
  ${props => {
    if (props.animation === 'fadeIn') {
      return css`
        animation: ${fadeIn} ${props.duration || 0.3}s ease-out ${props.delay || 0}s both;
      `;
    }
    if (props.animation === 'slideIn') {
      return css`
        animation: ${slideIn} ${props.duration || 0.3}s ease-out ${props.delay || 0}s both;
      `;
    }
    return '';
  }}
`;
```

### Styled Components Theming

```typescript
// Theme definition
interface Theme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    background: string;
    surface: string;
    text: {
      primary: string;
      secondary: string;
      disabled: string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  typography: {
    fontFamily: string;
    fontSizes: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
    };
    fontWeights: {
      normal: number;
      medium: number;
      bold: number;
    };
  };
  breakpoints: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
  };
}

const lightTheme: Theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    warning: '#ffc107',
    error: '#dc3545',
    background: '#ffffff',
    surface: '#f8f9fa',
    text: {
      primary: '#212529',
      secondary: '#6c757d',
      disabled: '#adb5bd'
    }
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px'
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSizes: {
      xs: '12px',
      sm: '14px',
      md: '16px',
      lg: '18px',
      xl: '24px'
    },
    fontWeights: {
      normal: 400,
      medium: 500,
      bold: 700
    }
  },
  breakpoints: {
    xs: '0px',
    sm: '576px',
    md: '768px',
    lg: '992px',
    xl: '1200px'
  },
  shadows: {
    sm: '0 1px 3px rgba(0, 0, 0, 0.12)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)'
  }
};

const darkTheme: Theme = {
  ...lightTheme,
  colors: {
    ...lightTheme.colors,
    background: '#121212',
    surface: '#1e1e1e',
    text: {
      primary: '#ffffff',
      secondary: '#adb5bd',
      disabled: '#6c757d'
    }
  }
};

// Using theme in components
const ThemedButton = styled.button<{ variant?: keyof Theme['colors'] }>`
  background-color: ${props => 
    props.variant ? props.theme.colors[props.variant] : props.theme.colors.primary
  };
  color: ${props => props.theme.colors.text.primary};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: none;
  border-radius: 4px;
  font-family: ${props => props.theme.typography.fontFamily};
  font-size: ${props => props.theme.typography.fontSizes.md};
  font-weight: ${props => props.theme.typography.fontWeights.medium};
  box-shadow: ${props => props.theme.shadows.sm};
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: ${props => props.theme.shadows.md};
    transform: translateY(-1px);
  }
  
  @media (min-width: ${props => props.theme.breakpoints.md}) {
    padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  }
`;

// Theme provider usage
const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  return (
    <ThemeProvider theme={isDarkMode ? darkTheme : lightTheme}>
      <Container>
        <ThemedButton onClick={() => setIsDarkMode(!isDarkMode)}>
          Switch to {isDarkMode ? 'Light' : 'Dark'} Theme
        </ThemedButton>
        
        <ThemedButton variant="success">
          Success Button
        </ThemedButton>
      </Container>
    </ThemeProvider>
  );
};
```

## Emotion.js Deep Dive

### Emotion Setup and Basic Usage

```typescript
// Installation
npm install @emotion/react @emotion/styled

// Core API imports
import { css, jsx } from '@emotion/react';
import styled from '@emotion/styled';

// 1. CSS prop approach (requires jsx pragma or automatic runtime)
/** @jsx jsx */
const CSSPropExample: React.FC = () => {
  return (
    <div
      css={css`
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 8px;
        
        &:hover {
          background-color: #e0e0e0;
        }
      `}
    >
      CSS prop styling
    </div>
  );
};

// 2. Styled components approach
const EmotionButton = styled.button<{ 
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
}>`
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
  
  // Size styles
  ${props => {
    switch (props.size) {
      case 'small':
        return css`
          padding: 6px 12px;
          font-size: 14px;
        `;
      case 'large':
        return css`
          padding: 12px 24px;
          font-size: 18px;
        `;
      default:
        return css`
          padding: 8px 16px;
          font-size: 16px;
        `;
    }
  }}
  
  // Variant styles
  ${props => props.variant === 'primary' ? css`
    background-color: #007bff;
    color: white;
    
    &:hover {
      background-color: #0056b3;
    }
  ` : css`
    background-color: #f8f9fa;
    color: #212529;
    border: 1px solid #dee2e6;
    
    &:hover {
      background-color: #e9ecef;
    }
  `}
`;

// 3. Object styles
const objectStyles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
    padding: '20px'
  },
  
  header: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#333'
  }
};

const ObjectStylesExample: React.FC = () => (
  <div css={objectStyles.container}>
    <h1 css={objectStyles.header}>Object Styles</h1>
  </div>
);
```

### Advanced Emotion Patterns

```typescript
// 1. Dynamic styles with theme
import { Theme, useTheme } from '@emotion/react';

interface EmotionTheme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
  };
  spacing: (multiplier: number) => string;
  breakpoints: {
    mobile: string;
    tablet: string;
    desktop: string;
  };
}

const emotionTheme: EmotionTheme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    background: '#ffffff',
    text: '#212529'
  },
  spacing: (multiplier) => `${8 * multiplier}px`,
  breakpoints: {
    mobile: '480px',
    tablet: '768px',
    desktop: '1024px'
  }
};

// Using theme in styles
const ThemedContainer = styled.div`
  background-color: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  padding: ${props => props.theme.spacing(3)};
  
  @media (min-width: ${props => props.theme.breakpoints.tablet}) {
    padding: ${props => props.theme.spacing(4)};
  }
`;

// 2. Composition patterns
const baseCardStyles = css`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
`;

const interactiveCardStyles = css`
  ${baseCardStyles}
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const Card: React.FC<{ interactive?: boolean; children: React.ReactNode }> = ({ 
  interactive, 
  children 
}) => (
  <div css={interactive ? interactiveCardStyles : baseCardStyles}>
    {children}
  </div>
);

// 3. Responsive utilities
const mq = {
  mobile: `@media (max-width: 767px)`,
  tablet: `@media (min-width: 768px) and (max-width: 1023px)`,
  desktop: `@media (min-width: 1024px)`
};

const ResponsiveGrid = styled.div`
  display: grid;
  gap: 16px;
  
  ${mq.mobile} {
    grid-template-columns: 1fr;
  }
  
  ${mq.tablet} {
    grid-template-columns: repeat(2, 1fr);
  }
  
  ${mq.desktop} {
    grid-template-columns: repeat(3, 1fr);
  }
`;

// 4. Keyframes and animations
import { keyframes } from '@emotion/react';

const pulse = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
`;

const Loading = styled.div`
  width: 40px;
  height: 40px;
  background-color: #007bff;
  border-radius: 50%;
  animation: ${pulse} 1.5s ease-in-out infinite;
`;

// 5. Global styles
import { Global } from '@emotion/react';

const globalStyles = css`
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  button {
    font-family: inherit;
  }
`;

const App: React.FC = () => (
  <>
    <Global styles={globalStyles} />
    <div>Your app content</div>
  </>
);
```

## JSS (JavaScript Style Sheets)

### JSS Setup and Usage

```typescript
// Installation
npm install jss jss-preset-default react-jss

// Basic setup
import jss from 'jss';
import preset from 'jss-preset-default';
import { createUseStyles } from 'react-jss';

// Setup JSS
jss.setup(preset());

// 1. Basic styles object
const useStyles = createUseStyles({
  container: {
    display: 'flex',
    flexDirection: 'column',
    padding: '20px',
    backgroundColor: '#f5f5f5'
  },
  
  button: {
    padding: '10px 20px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    backgroundColor: '#007bff',
    color: 'white',
    fontSize: '16px',
    
    '&:hover': {
      backgroundColor: '#0056b3'
    },
    
    '&:disabled': {
      opacity: 0.6,
      cursor: 'not-allowed'
    }
  },
  
  // Media queries
  responsiveText: {
    fontSize: '14px',
    
    '@media (min-width: 768px)': {
      fontSize: '16px'
    },
    
    '@media (min-width: 1024px)': {
      fontSize: '18px'
    }
  }
});

// Using styles in component
const JSComponent: React.FC = () => {
  const classes = useStyles();
  
  return (
    <div className={classes.container}>
      <p className={classes.responsiveText}>Responsive text</p>
      <button className={classes.button}>JSS Button</button>
    </div>
  );
};

// 2. Dynamic styles with props
interface DynamicStylesProps {
  size: 'small' | 'medium' | 'large';
  variant: 'primary' | 'secondary';
}

const useDynamicStyles = createUseStyles({
  dynamicButton: (props: DynamicStylesProps) => ({
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 600,
    transition: 'all 0.2s ease',
    
    // Size-based styles
    ...(props.size === 'small' && {
      padding: '6px 12px',
      fontSize: '14px'
    }),
    
    ...(props.size === 'medium' && {
      padding: '8px 16px',
      fontSize: '16px'
    }),
    
    ...(props.size === 'large' && {
      padding: '12px 24px',
      fontSize: '18px'
    }),
    
    // Variant-based styles
    ...(props.variant === 'primary' && {
      backgroundColor: '#007bff',
      color: 'white',
      
      '&:hover': {
        backgroundColor: '#0056b3'
      }
    }),
    
    ...(props.variant === 'secondary' && {
      backgroundColor: '#6c757d',
      color: 'white',
      
      '&:hover': {
        backgroundColor: '#545b62'
      }
    })
  })
});

const DynamicJSSButton: React.FC<DynamicStylesProps> = (props) => {
  const classes = useDynamicStyles(props);
  
  return (
    <button className={classes.dynamicButton}>
      Dynamic JSS Button
    </button>
  );
};

// 3. Theme support
interface JSTheme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
  };
  spacing: {
    small: string;
    medium: string;
    large: string;
  };
}

const jssTheme: JSTheme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    background: '#ffffff',
    text: '#212529'
  },
  spacing: {
    small: '8px',
    medium: '16px',
    large: '24px'
  }
};

const useThemedStyles = createUseStyles((theme: JSTheme) => ({
  themedContainer: {
    backgroundColor: theme.colors.background,
    color: theme.colors.text,
    padding: theme.spacing.large,
    borderRadius: '8px'
  },
  
  themedButton: {
    backgroundColor: theme.colors.primary,
    color: 'white',
    padding: `${theme.spacing.small} ${theme.spacing.medium}`,
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  }
}));

// Using with ThemeProvider
import { ThemeProvider } from 'react-jss';

const ThemedJSSComponent: React.FC = () => {
  const classes = useThemedStyles();
  
  return (
    <div className={classes.themedContainer}>
      <button className={classes.themedButton}>
        Themed JSS Button
      </button>
    </div>
  );
};

const App: React.FC = () => (
  <ThemeProvider theme={jssTheme}>
    <ThemedJSSComponent />
  </ThemeProvider>
);
```

## Stitches Modern Styling

### Stitches Setup and Configuration

```typescript
// Installation
npm install @stitches/react

// stitches.config.ts
import { createStitches } from '@stitches/react';

export const {
  styled,
  css,
  globalCss,
  keyframes,
  getCssText,
  theme,
  createTheme,
  config,
} = createStitches({
  theme: {
    colors: {
      primary: '#007bff',
      secondary: '#6c757d',
      success: '#28a745',
      warning: '#ffc107',
      error: '#dc3545',
      
      gray100: '#f8f9fa',
      gray200: '#e9ecef',
      gray300: '#dee2e6',
      gray400: '#ced4da',
      gray500: '#adb5bd',
      gray600: '#6c757d',
      gray700: '#495057',
      gray800: '#343a40',
      gray900: '#212529',
      
      background: '#ffffff',
      text: '#212529'
    },
    
    space: {
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      5: '20px',
      6: '24px',
      7: '28px',
      8: '32px',
    },
    
    fontSizes: {
      1: '12px',
      2: '14px',
      3: '16px',
      4: '18px',
      5: '20px',
      6: '24px',
    },
    
    fonts: {
      system: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: 'Menlo, Monaco, "Lucida Console", monospace',
    },
    
    fontWeights: {
      normal: 400,
      medium: 500,
      bold: 700,
    },
    
    lineHeights: {
      1: '1',
      2: '1.25',
      3: '1.5',
      4: '1.75',
    },
    
    letterSpacings: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
    },
    
    sizes: {
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      5: '20px',
      6: '24px',
      7: '28px',
      8: '32px',
    },
    
    borderWidths: {
      1: '1px',
      2: '2px',
      3: '4px',
    },
    
    borderStyles: {},
    
    radii: {
      1: '2px',
      2: '4px',
      3: '8px',
      4: '12px',
      round: '50%',
      pill: '9999px',
    },
    
    shadows: {
      1: '0 1px 3px rgba(0, 0, 0, 0.12)',
      2: '0 4px 6px rgba(0, 0, 0, 0.1)',
      3: '0 10px 15px rgba(0, 0, 0, 0.1)',
    },
    
    zIndices: {
      1: '100',
      2: '200',
      3: '300',
      4: '400',
      max: '999',
    },
    
    transitions: {
      1: 'all 0.125s ease',
      2: 'all 0.25s ease',
      3: 'all 0.375s ease',
    },
  },
  
  media: {
    bp1: '(min-width: 480px)',
    bp2: '(min-width: 768px)',
    bp3: '(min-width: 1024px)',
    bp4: '(min-width: 1200px)',
  },
  
  utils: {
    // Margin utilities
    m: (value: any) => ({
      margin: value,
    }),
    mt: (value: any) => ({
      marginTop: value,
    }),
    mr: (value: any) => ({
      marginRight: value,
    }),
    mb: (value: any) => ({
      marginBottom: value,
    }),
    ml: (value: any) => ({
      marginLeft: value,
    }),
    mx: (value: any) => ({
      marginLeft: value,
      marginRight: value,
    }),
    my: (value: any) => ({
      marginTop: value,
      marginBottom: value,
    }),
    
    // Padding utilities
    p: (value: any) => ({
      padding: value,
    }),
    pt: (value: any) => ({
      paddingTop: value,
    }),
    pr: (value: any) => ({
      paddingRight: value,
    }),
    pb: (value: any) => ({
      paddingBottom: value,
    }),
    pl: (value: any) => ({
      paddingLeft: value,
    }),
    px: (value: any) => ({
      paddingLeft: value,
      paddingRight: value,
    }),
    py: (value: any) => ({
      paddingTop: value,
      paddingBottom: value,
    }),
    
    // Size utilities
    size: (value: any) => ({
      width: value,
      height: value,
    }),
  },
});

// Dark theme
export const darkTheme = createTheme({
  colors: {
    background: '#121212',
    text: '#ffffff',
    gray100: '#1e1e1e',
    gray200: '#2d2d2d',
    gray300: '#3c3c3c',
    gray400: '#4b4b4b',
    gray500: '#5a5a5a',
    gray600: '#696969',
    gray700: '#787878',
    gray800: '#878787',
    gray900: '#969696',
  },
});
```

### Advanced Stitches Components

```typescript
// Basic styled components
const Box = styled('div', {
  // Base styles
});

const Button = styled('button', {
  // Reset styles
  all: 'unset',
  alignItems: 'center',
  boxSizing: 'border-box',
  userSelect: 'none',
  
  // Base styles
  display: 'inline-flex',
  justifyContent: 'center',
  borderRadius: '$2',
  fontSize: '$3',
  fontWeight: '$medium',
  fontFamily: '$system',
  cursor: 'pointer',
  transition: '$2',
  
  // Default variant
  backgroundColor: '$primary',
  color: 'white',
  px: '$4',
  py: '$2',
  
  '&:hover': {
    backgroundColor: '$gray700',
  },
  
  '&:disabled': {
    backgroundColor: '$gray300',
    color: '$gray500',
    cursor: 'not-allowed',
  },
  
  variants: {
    variant: {
      primary: {
        backgroundColor: '$primary',
        color: 'white',
        
        '&:hover': {
          backgroundColor: '$gray700',
        },
      },
      
      secondary: {
        backgroundColor: '$gray200',
        color: '$text',
        
        '&:hover': {
          backgroundColor: '$gray300',
        },
      },
      
      ghost: {
        backgroundColor: 'transparent',
        color: '$primary',
        
        '&:hover': {
          backgroundColor: '$gray100',
        },
      },
      
      danger: {
        backgroundColor: '$error',
        color: 'white',
        
        '&:hover': {
          backgroundColor: '#c82333',
        },
      },
    },
    
    size: {
      small: {
        px: '$2',
        py: '$1',
        fontSize: '$2',
      },
      
      medium: {
        px: '$4',
        py: '$2',
        fontSize: '$3',
      },
      
      large: {
        px: '$6',
        py: '$3',
        fontSize: '$4',
      },
    },
    
    fullWidth: {
      true: {
        width: '100%',
      },
    },
  },
  
  compoundVariants: [
    {
      variant: 'ghost',
      size: 'small',
      css: {
        px: '$2',
        py: '$1',
      },
    },
  ],
  
  defaultVariants: {
    variant: 'primary',
    size: 'medium',
  },
});

// Complex component with multiple variants
const Card = styled('div', {
  backgroundColor: '$background',
  borderRadius: '$3',
  overflow: 'hidden',
  
  variants: {
    variant: {
      elevated: {
        boxShadow: '$2',
      },
      
      outlined: {
        border: '1px solid $gray300',
      },
      
      ghost: {
        backgroundColor: 'transparent',
      },
    },
    
    padding: {
      none: {},
      small: { p: '$3' },
      medium: { p: '$4' },
      large: { p: '$6' },
    },
    
    interactive: {
      true: {
        cursor: 'pointer',
        transition: '$2',
        
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '$3',
        },
      },
    },
  },
  
  defaultVariants: {
    variant: 'elevated',
    padding: 'medium',
  },
});

// Layout components
const Container = styled('div', {
  width: '100%',
  maxWidth: '1200px',
  mx: 'auto',
  px: '$4',
  
  '@bp2': {
    px: '$6',
  },
  
  '@bp3': {
    px: '$8',
  },
});

const Grid = styled('div', {
  display: 'grid',
  gap: '$4',
  
  variants: {
    columns: {
      1: { gridTemplateColumns: '1fr' },
      2: { gridTemplateColumns: 'repeat(2, 1fr)' },
      3: { gridTemplateColumns: 'repeat(3, 1fr)' },
      4: { gridTemplateColumns: 'repeat(4, 1fr)' },
    },
    
    responsive: {
      true: {
        gridTemplateColumns: '1fr',
        
        '@bp1': {
          gridTemplateColumns: 'repeat(2, 1fr)',
        },
        
        '@bp2': {
          gridTemplateColumns: 'repeat(3, 1fr)',
        },
        
        '@bp3': {
          gridTemplateColumns: 'repeat(4, 1fr)',
        },
      },
    },
  },
});

// Text components
const Text = styled('span', {
  fontFamily: '$system',
  color: '$text',
  
  variants: {
    size: {
      1: { fontSize: '$1' },
      2: { fontSize: '$2' },
      3: { fontSize: '$3' },
      4: { fontSize: '$4' },
      5: { fontSize: '$5' },
      6: { fontSize: '$6' },
    },
    
    weight: {
      normal: { fontWeight: '$normal' },
      medium: { fontWeight: '$medium' },
      bold: { fontWeight: '$bold' },
    },
    
    color: {
      primary: { color: '$primary' },
      secondary: { color: '$gray600' },
      success: { color: '$success' },
      warning: { color: '$warning' },
      error: { color: '$error' },
    },
    
    truncate: {
      true: {
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
      },
    },
  },
  
  defaultVariants: {
    size: '3',
    weight: 'normal',
  },
});

// Usage example
const StitchesExample: React.FC = () => {
  const [isDark, setIsDark] = useState(false);
  
  return (
    <div className={isDark ? darkTheme : ''}>
      <Container>
        <Card interactive>
          <Text size="5" weight="bold" css={{ mb: '$3' }}>
            Stitches Components
          </Text>
          
          <Text css={{ mb: '$4' }}>
            These components are built with Stitches and demonstrate
            advanced variant patterns.
          </Text>
          
          <Grid columns="2" css={{ gap: '$3' }}>
            <Button variant="primary" size="medium">
              Primary Button
            </Button>
            
            <Button variant="secondary" size="medium">
              Secondary Button
            </Button>
            
            <Button variant="ghost" size="small">
              Ghost Button
            </Button>
            
            <Button 
              variant="danger" 
              size="large"
              onClick={() => setIsDark(!isDark)}
            >
              Toggle Theme
            </Button>
          </Grid>
        </Card>
      </Container>
    </div>
  );
};
```

This comprehensive guide covers modern CSS-in-JS solutions including Styled Components, Emotion, JSS, and Stitches, providing practical examples and advanced patterns for building scalable, maintainable styling systems in React applications.
