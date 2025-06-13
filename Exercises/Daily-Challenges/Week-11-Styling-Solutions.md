# Week 11: Styling Solutions - Daily Challenges

## Overview
This week focuses on mastering various CSS-in-JS solutions, styled-components, CSS modules, and modern styling approaches in React applications. Each day builds upon the previous, culminating in a complete design system implementation.

---

## 📅 **Day 1 (Monday): CSS-in-JS Fundamentals**

### **Challenge: Styled Components Basics**
**Objective**: Learn the fundamentals of styled-components and CSS-in-JS concepts.

**Tasks**:
1. **Setup Project**
   ```bash
   npx create-react-app styling-week
   cd styling-week
   npm install styled-components
   ```

2. **Create Basic Styled Components**
   - Create a `Button` component with variants (primary, secondary, danger)
   - Implement hover states and transitions
   - Add props-based styling for size variations

3. **Theme Integration**
   - Set up a theme provider with color palette and typography
   - Create themed components that respond to theme changes
   - Implement dark/light theme toggle

**Deliverables**:
- [ ] Working styled-components setup
- [ ] Button component with 3 variants and 3 sizes
- [ ] Theme provider with color switching
- [ ] Demo page showcasing all components

**Learning Goals**:
- Understand CSS-in-JS benefits and trade-offs
- Master styled-components syntax and props
- Learn theme-based design systems

---

## 📅 **Day 2 (Tuesday): Advanced Styled Components**

### **Challenge: Component Composition and Inheritance**
**Objective**: Master advanced styled-components patterns for scalable styling architecture.

**Tasks**:
1. **Component Inheritance**
   - Create base components that can be extended
   - Implement style inheritance hierarchy
   - Build complex components from simpler ones

2. **Dynamic Styling**
   - Create components with conditional styles based on props
   - Implement responsive design using styled-components
   - Add animation and keyframes

3. **Component Variants**
   - Build a card component with multiple layout variants
   - Create form input components with validation states
   - Implement loading and error states

**Practice Exercises**:
```javascript
// Extend base button for specific use cases
const IconButton = styled(BaseButton)`
  /* Add icon-specific styles */
`;

// Conditional styling based on props
const Card = styled.div`
  background: ${props => props.variant === 'outlined' ? 'transparent' : props.theme.colors.surface};
  border: ${props => props.variant === 'outlined' ? `1px solid ${props.theme.colors.border}` : 'none'};
`;
```

**Deliverables**:
- [ ] Component inheritance examples
- [ ] Responsive card component
- [ ] Form components with states
- [ ] Animation showcase

---

## 📅 **Day 3 (Wednesday): CSS Modules and Alternatives**

### **Challenge: CSS Modules Implementation**
**Objective**: Compare and implement CSS Modules alongside styled-components.

**Tasks**:
1. **CSS Modules Setup**
   - Configure CSS Modules in React app
   - Create modular CSS files with local scope
   - Implement naming conventions

2. **Feature Comparison**
   - Build same components using CSS Modules vs styled-components
   - Analyze pros and cons of each approach
   - Test performance implications

3. **Hybrid Approach**
   - Combine CSS Modules with styled-components
   - Use CSS Modules for layout, styled-components for theming
   - Create utility classes and component styles

**Practice Files**:
```css
/* Button.module.css */
.button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.primary {
  background-color: var(--color-primary);
  color: white;
}
```

**Deliverables**:
- [ ] CSS Modules configuration
- [ ] Component comparison chart
- [ ] Hybrid implementation example
- [ ] Performance analysis report

---

## 📅 **Day 4 (Thursday): Tailwind CSS Integration**

### **Challenge: Utility-First CSS with Tailwind**
**Objective**: Implement Tailwind CSS for rapid UI development.

**Tasks**:
1. **Tailwind Setup**
   - Install and configure Tailwind CSS
   - Set up custom configuration and theme
   - Create custom utility classes

2. **Component Building**
   - Build responsive dashboard layout
   - Create form components using Tailwind utilities
   - Implement dark mode with Tailwind

3. **Optimization**
   - Configure PurgeCSS for production
   - Create custom component classes
   - Implement design tokens

**Tailwind Examples**:
```jsx
// Responsive card component
const Card = ({ children, className = "" }) => (
  <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 ${className}`}>
    {children}
  </div>
);

// Custom button with Tailwind
const Button = ({ variant = "primary", size = "md", children, ...props }) => {
  const baseClasses = "font-medium rounded focus:outline-none focus:ring-2";
  const variants = {
    primary: "bg-blue-500 hover:bg-blue-600 text-white",
    secondary: "bg-gray-500 hover:bg-gray-600 text-white"
  };
  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base"
  };
  
  return (
    <button 
      className={`${baseClasses} ${variants[variant]} ${sizes[size]}`}
      {...props}
    >
      {children}
    </button>
  );
};
```

**Deliverables**:
- [ ] Tailwind CSS configuration
- [ ] Responsive dashboard layout
- [ ] Dark mode implementation
- [ ] Custom utility classes

---

## 📅 **Day 5 (Friday): CSS-in-JS Performance and Emotion**

### **Challenge: Emotion Library and Performance Optimization**
**Objective**: Explore Emotion as an alternative to styled-components and optimize CSS-in-JS performance.

**Tasks**:
1. **Emotion Setup**
   - Install and configure Emotion
   - Compare Emotion vs styled-components syntax
   - Implement same components using both libraries

2. **Performance Optimization**
   - Implement CSS-in-JS best practices
   - Use css prop for dynamic styles
   - Optimize bundle size and runtime performance

3. **Advanced Features**
   - Server-side rendering with Emotion
   - CSS custom properties integration
   - Component composition patterns

**Emotion Examples**:
```jsx
import { css, jsx } from '@emotion/react';
import styled from '@emotion/styled';

// Using css prop
const buttonStyle = css`
  background-color: hotpink;
  &:hover {
    color: white;
  }
`;

// Styled component approach
const Button = styled.button`
  background-color: ${props => props.primary ? 'blue' : 'gray'};
`;

// Object styles
const objectStyle = {
  backgroundColor: 'hotpink',
  '&:hover': {
    color: 'white'
  }
};
```

**Deliverables**:
- [ ] Emotion implementation
- [ ] Performance comparison report
- [ ] SSR configuration
- [ ] Bundle size analysis

---

## 📅 **Day 6 (Saturday): Design System Architecture**

### **Challenge: Build a Complete Design System**
**Objective**: Create a comprehensive design system with tokens, components, and documentation.

**Tasks**:
1. **Design Tokens**
   - Define color palettes, typography scales, spacing units
   - Create token-based theme system
   - Implement design token documentation

2. **Component Library**
   - Build foundational components (Button, Input, Card, etc.)
   - Create composite components (Forms, Navigation, etc.)
   - Implement component variants and sizes

3. **Documentation**
   - Set up Storybook for component documentation
   - Create usage guidelines and examples
   - Document design principles and patterns

**Design Token Structure**:
```javascript
const tokens = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      500: '#3b82f6',
      900: '#1e3a8a'
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '3rem'
  },
  typography: {
    fontSizes: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem'
    }
  }
};
```

**Deliverables**:
- [ ] Complete design token system
- [ ] 10+ documented components
- [ ] Storybook setup with examples
- [ ] Design system documentation

---

## 📅 **Day 7 (Sunday): Advanced Styling Patterns**

### **Challenge: Advanced Styling Techniques and Patterns**
**Objective**: Implement advanced CSS patterns, animations, and responsive design techniques.

**Tasks**:
1. **Advanced Animations**
   - Create complex CSS animations and transitions
   - Implement spring animations with Framer Motion
   - Build loading states and micro-interactions

2. **Responsive Design Patterns**
   - Implement container queries (where supported)
   - Create fluid typography and spacing
   - Build responsive component variants

3. **Performance and Accessibility**
   - Optimize CSS delivery and critical path
   - Implement proper focus management
   - Create accessible color schemes and contrast

**Advanced Pattern Examples**:
```jsx
import { motion } from 'framer-motion';

// Spring animation component
const AnimatedCard = motion.div.attrs({
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", damping: 20 }
})`
  background: white;
  border-radius: 8px;
  padding: 1rem;
`;

// Responsive typography
const FluidText = styled.h1`
  font-size: clamp(1.5rem, 4vw, 3rem);
  line-height: 1.2;
`;

// CSS custom properties for theming
const ThemeProvider = ({ theme, children }) => (
  <div style={{
    '--color-primary': theme.colors.primary,
    '--font-size-base': theme.typography.base
  }}>
    {children}
  </div>
);
```

**Deliverables**:
- [ ] Animation showcase with 5+ examples
- [ ] Responsive design patterns demo
- [ ] Accessibility audit checklist
- [ ] Performance optimization report

---

## 🎯 **Weekly Project: Complete Design System**

### **Project Overview**
Build a production-ready design system that can be used across multiple applications.

### **Requirements**:
1. **Token-Based Architecture**
   - Comprehensive design tokens for colors, typography, spacing
   - Theme variants (light/dark mode)
   - Responsive breakpoint system

2. **Component Library**
   - 15+ foundational components
   - Consistent API and prop patterns
   - Accessibility compliance (WCAG 2.1)

3. **Documentation and Testing**
   - Storybook with interactive examples
   - Visual regression testing setup
   - Usage guidelines and best practices

4. **Multi-Library Support**
   - Components available in styled-components
   - Tailwind utility classes
   - CSS Modules variants

### **Evaluation Criteria**:
- **Consistency**: All components follow design patterns (25%)
- **Accessibility**: WCAG 2.1 AA compliance (25%)
- **Documentation**: Complete Storybook setup (25%)
- **Code Quality**: Clean, maintainable, performant code (25%)

---

## 📚 **Additional Resources**

### **Documentation**
- [Styled Components Documentation](https://styled-components.com/)
- [Emotion Documentation](https://emotion.sh/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [CSS Modules Documentation](https://github.com/css-modules/css-modules)

### **Design System Examples**
- [Material-UI Design System](https://mui.com/)
- [Chakra UI Design System](https://chakra-ui.com/)
- [Ant Design System](https://ant.design/)
- [Polaris Design System](https://polaris.shopify.com/)

### **Tools and Testing**
- [Storybook](https://storybook.js.org/)
- [Chromatic Visual Testing](https://www.chromatic.com/)
- [Design Tokens Transformer](https://amzn.github.io/style-dictionary/)

---

**💡 Pro Tips**:
1. **Performance**: Avoid dynamic CSS-in-JS in render functions
2. **Consistency**: Use design tokens instead of hard-coded values
3. **Accessibility**: Always test with screen readers and keyboard navigation
4. **Documentation**: Write clear examples and usage guidelines
5. **Testing**: Implement visual regression testing for UI consistency