# Module 14: Code Quality

## 📚 Learning Objectives

By the end of this module, you will:
- Master ESLint configuration and custom rules for React
- Implement Prettier for consistent code formatting
- Integrate TypeScript with React for type safety
- Set up pre-commit hooks and automated code quality checks
- Understand code analysis tools and metrics
- Implement accessibility linting and testing
- Build maintainable code architecture patterns
- Establish team coding standards and guidelines

## 🎯 Prerequisites

- Completed Modules 1-13
- Understanding of JavaScript/TypeScript fundamentals
- Basic knowledge of build tools and npm scripts
- Familiarity with Git and version control

## 📖 Module Content

### 1. ESLint Configuration for React

#### **Basic ESLint Setup**
```json
// .eslintrc.json
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true,
    "jest": true
  },
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "plugin:import/recommended",
    "plugin:import/typescript",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaFeatures": {
      "jsx": true
    },
    "ecmaVersion": "latest",
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "plugins": [
    "react",
    "react-hooks",
    "@typescript-eslint",
    "jsx-a11y",
    "import",
    "testing-library"
  ],
  "rules": {
    // React Rules
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off",
    "react/display-name": "warn",
    "react/no-unused-prop-types": "error",
    "react/no-array-index-key": "warn",
    "react/jsx-key": "error",
    "react/jsx-no-bind": ["error", {
      "allowArrowFunctions": true,
      "allowBind": false,
      "ignoreRefs": true
    }],
    "react/jsx-curly-brace-presence": ["error", "never"],
    
    // React Hooks Rules
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    
    // TypeScript Rules
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/prefer-nullish-coalescing": "error",
    "@typescript-eslint/prefer-optional-chain": "error",
    "@typescript-eslint/no-non-null-assertion": "warn",
    
    // Import Rules
    "import/order": ["error", {
      "groups": [
        "builtin",
        "external",
        "internal",
        "parent",
        "sibling",
        "index"
      ],
      "newlines-between": "always",
      "alphabetize": {
        "order": "asc",
        "caseInsensitive": true
      }
    }],
    "import/no-unused-modules": "error",
    "import/no-default-export": "off",
    
    // General Rules
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "no-debugger": "error",
    "no-alert": "error",
    "prefer-const": "error",
    "no-var": "error",
    "object-shorthand": "error",
    "prefer-template": "error"
  },
  "settings": {
    "react": {
      "version": "detect"
    },
    "import/resolver": {
      "typescript": {
        "alwaysTryTypes": true,
        "project": "./tsconfig.json"
      }
    }
  },
  "overrides": [
    {
      "files": ["**/__tests__/**/*", "**/*.test.*"],
      "extends": ["plugin:testing-library/react"],
      "rules": {
        "testing-library/await-async-query": "error",
        "testing-library/no-await-sync-query": "error",
        "testing-library/no-debug": "warn",
        "testing-library/no-dom-import": "error"
      }
    }
  ]
}
```

#### **Custom ESLint Rules**
```javascript
// eslint-rules/no-hardcoded-colors.js
module.exports = {
  meta: {
    type: "suggestion",
    docs: {
      description: "Disallow hardcoded color values",
      category: "Best Practices",
      recommended: false
    },
    fixable: null,
    schema: []
  },
  
  create(context) {
    const colorRegex = /#[0-9a-fA-F]{3,6}|rgb\(|rgba\(|hsl\(|hsla\(/;
    
    return {
      Literal(node) {
        if (typeof node.value === 'string' && colorRegex.test(node.value)) {
          context.report({
            node,
            message: 'Hardcoded color values should be replaced with design tokens'
          });
        }
      },
      
      TemplateElement(node) {
        if (colorRegex.test(node.value.raw)) {
          context.report({
            node,
            message: 'Hardcoded color values should be replaced with design tokens'
          });
        }
      }
    };
  }
};
```

#### **ESLint Scripts**
```json
// package.json
{
  "scripts": {
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint src --ext .js,.jsx,.ts,.tsx --fix",
    "lint:staged": "lint-staged",
    "lint:ci": "eslint src --ext .js,.jsx,.ts,.tsx --format junit --output-file reports/eslint.xml"
  },
  "lint-staged": {
    "src/**/*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

### 2. Prettier Configuration

#### **Prettier Configuration**
```javascript
// .prettierrc.js
module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 80,
  tabWidth: 2,
  useTabs: false,
  quoteProps: 'as-needed',
  jsxSingleQuote: true,
  bracketSpacing: true,
  bracketSameLine: false,
  arrowParens: 'avoid',
  endOfLine: 'lf',
  embeddedLanguageFormatting: 'auto',
  
  // Plugin-specific options
  importOrder: [
    '^react$',
    '^react-dom$',
    '<THIRD_PARTY_MODULES>',
    '^@/(.*)$',
    '^[./]'
  ],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
};
```

```javascript
// .prettierignore
# Dependencies
node_modules/

# Build outputs
build/
dist/
coverage/

# Generated files
*.d.ts

# Config files
.eslintrc.js
.prettierrc.js
```

#### **Editor Integration**
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.suggest.autoImports": true,
  "emmet.includeLanguages": {
    "typescript": "html",
    "typescriptreact": "html"
  }
}
```

### 3. TypeScript Integration

#### **TypeScript Configuration**
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": [
      "dom",
      "dom.iterable",
      "ES6"
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
    "incremental": true,
    "baseUrl": "src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/hooks/*": ["hooks/*"],
      "@/utils/*": ["utils/*"],
      "@/types/*": ["types/*"]
    }
  },
  "include": [
    "src",
    "**/*.ts",
    "**/*.tsx"
  ],
  "exclude": [
    "node_modules",
    "build",
    "coverage"
  ]
}
```

#### **TypeScript Strict Configuration**
```json
// tsconfig.strict.json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

#### **Type Definitions**
```typescript
// src/types/common.ts
export interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface User extends BaseEntity {
  name: string;
  email: string;
  role: UserRole;
  profile?: UserProfile;
}

export interface UserProfile {
  avatar?: string;
  bio?: string;
  location?: string;
  website?: string;
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  MODERATOR = 'moderator'
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  errors?: string[];
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequireAtLeastOne<T> = {
  [K in keyof T]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<keyof T, K>>>;
}[keyof T];
```

#### **Component Type Patterns**
```typescript
// src/components/Button/Button.tsx
import React, { forwardRef } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    variant = 'primary', 
    size = 'md', 
    loading = false, 
    leftIcon, 
    rightIcon, 
    children, 
    disabled,
    className,
    ...props 
  }, ref) => {
    const baseClasses = 'btn';
    const variantClasses = `btn-${variant}`;
    const sizeClasses = `btn-${size}`;
    const loadingClasses = loading ? 'btn-loading' : '';
    
    const classes = [
      baseClasses,
      variantClasses,
      sizeClasses,
      loadingClasses,
      className
    ].filter(Boolean).join(' ');

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <span className="spinner" />
        ) : (
          <>
            {leftIcon && <span className="btn-icon-left">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="btn-icon-right">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export type { ButtonProps };
export default Button;
```

#### **Hook Type Patterns**
```typescript
// src/hooks/useApi.ts
import { useState, useEffect, useCallback } from 'react';

interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: () => Promise<void>;
  reset: () => void;
}

function useApi<T = any>(
  fetcher: () => Promise<T>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetcher();
      setData(result);
      options.onSuccess?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      options.onError?.(error);
    } finally {
      setLoading(false);
    }
  }, [fetcher, options]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (options.immediate) {
      execute();
    }
  }, [execute, options.immediate]);

  return { data, loading, error, execute, reset };
}

export type { UseApiOptions, UseApiReturn };
export default useApi;
```

### 4. Pre-commit Hooks and Automation

#### **Husky Configuration**
```json
// package.json
{
  "scripts": {
    "prepare": "husky install"
  },
  "devDependencies": {
    "husky": "^8.0.0",
    "lint-staged": "^13.0.0"
  }
}
```

```bash
#!/usr/bin/env sh
# .husky/pre-commit
. "$(dirname -- "$0")/_/husky.sh"

npm run lint:staged
npm run type-check
npm run test:staged
```

```bash
#!/usr/bin/env sh
# .husky/commit-msg
. "$(dirname -- "$0")/_/husky.sh"

npx commitlint --edit "$1"
```

#### **Lint-staged Configuration**
```javascript
// lint-staged.config.js
module.exports = {
  '*.{js,jsx,ts,tsx}': [
    'eslint --fix',
    'prettier --write',
    'jest --findRelatedTests --passWithNoTests'
  ],
  '*.{json,md,yml,yaml}': [
    'prettier --write'
  ],
  '*.{css,scss,sass}': [
    'stylelint --fix',
    'prettier --write'
  ]
};
```

#### **Commitlint Configuration**
```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation
        'style',    // Formatting
        'refactor', // Code restructuring
        'test',     // Adding tests
        'chore',    // Maintenance
        'perf',     // Performance improvements
        'ci',       // CI/CD changes
        'build',    // Build system changes
        'revert'    // Revert changes
      ]
    ],
    'subject-case': [2, 'always', 'sentence-case'],
    'subject-max-length': [2, 'always', 100],
    'body-max-line-length': [2, 'always', 120]
  }
};
```

### 5. Code Analysis Tools

#### **SonarQube Configuration**
```javascript
// sonar-project.properties
sonar.projectKey=react-app
sonar.projectName=React Application
sonar.projectVersion=1.0.0

# Source code
sonar.sources=src
sonar.exclusions=**/*.test.ts,**/*.test.tsx,**/*.stories.tsx,**/node_modules/**

# Test coverage
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.testExecutionReportPaths=coverage/test-reporter.xml

# Quality gates
sonar.qualitygate.wait=true
```

#### **Bundle Analysis**
```json
// package.json
{
  "scripts": {
    "analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js",
    "analyze:deps": "npx depcheck",
    "analyze:duplicate": "npx jscpd src",
    "analyze:complexity": "npx complexity-report src"
  }
}
```

#### **Performance Monitoring**
```javascript
// src/utils/performance.ts
interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];

  startMeasure(name: string): void {
    performance.mark(`${name}-start`);
  }

  endMeasure(name: string): number {
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    const measure = performance.getEntriesByName(name, 'measure')[0];
    const metric: PerformanceMetric = {
      name,
      value: measure.duration,
      timestamp: Date.now()
    };
    
    this.metrics.push(metric);
    
    // Clean up
    performance.clearMarks(`${name}-start`);
    performance.clearMarks(`${name}-end`);
    performance.clearMeasures(name);
    
    return measure.duration;
  }

  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  clearMetrics(): void {
    this.metrics = [];
  }

  reportToAnalytics(metric: PerformanceMetric): void {
    // Send to analytics service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'timing_complete', {
        name: metric.name,
        value: Math.round(metric.value)
      });
    }
  }
}

export const performanceMonitor = new PerformanceMonitor();
```

### 6. Accessibility Linting

#### **Accessibility ESLint Rules**
```json
// .eslintrc.json (accessibility section)
{
  "extends": [
    "plugin:jsx-a11y/recommended"
  ],
  "rules": {
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/anchor-has-content": "error",
    "jsx-a11y/anchor-is-valid": "error",
    "jsx-a11y/aria-activedescendant-has-tabindex": "error",
    "jsx-a11y/aria-props": "error",
    "jsx-a11y/aria-proptypes": "error",
    "jsx-a11y/aria-role": "error",
    "jsx-a11y/aria-unsupported-elements": "error",
    "jsx-a11y/autocomplete-valid": "error",
    "jsx-a11y/click-events-have-key-events": "error",
    "jsx-a11y/heading-has-content": "error",
    "jsx-a11y/html-has-lang": "error",
    "jsx-a11y/iframe-has-title": "error",
    "jsx-a11y/img-redundant-alt": "error",
    "jsx-a11y/interactive-supports-focus": "error",
    "jsx-a11y/label-has-associated-control": "error",
    "jsx-a11y/media-has-caption": "warn",
    "jsx-a11y/mouse-events-have-key-events": "error",
    "jsx-a11y/no-access-key": "error",
    "jsx-a11y/no-autofocus": "warn",
    "jsx-a11y/no-distracting-elements": "error",
    "jsx-a11y/no-interactive-element-to-noninteractive-role": "error",
    "jsx-a11y/no-noninteractive-element-interactions": "error",
    "jsx-a11y/no-noninteractive-element-to-interactive-role": "error",
    "jsx-a11y/no-noninteractive-tabindex": "error",
    "jsx-a11y/no-redundant-roles": "error",
    "jsx-a11y/no-static-element-interactions": "error",
    "jsx-a11y/role-has-required-aria-props": "error",
    "jsx-a11y/role-supports-aria-props": "error",
    "jsx-a11y/scope": "error",
    "jsx-a11y/tabindex-no-positive": "error"
  }
}
```

#### **Accessibility Testing Utilities**
```typescript
// src/utils/accessibility.ts
export const announceToScreenReader = (message: string): void => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.setAttribute('class', 'sr-only');
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

export const trapFocus = (element: HTMLElement): (() => void) => {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstElement = focusableElements[0] as HTMLElement;
  const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  };

  element.addEventListener('keydown', handleKeyDown);
  firstElement?.focus();

  return () => {
    element.removeEventListener('keydown', handleKeyDown);
  };
};

export const getContrastRatio = (color1: string, color2: string): number => {
  // Implementation of WCAG contrast ratio calculation
  const getLuminance = (color: string): number => {
    // Simplified luminance calculation
    const rgb = color.match(/\d+/g)?.map(Number) || [0, 0, 0];
    const [r, g, b] = rgb.map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const lum1 = getLuminance(color1);
  const lum2 = getLuminance(color2);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  
  return (brightest + 0.05) / (darkest + 0.05);
};
```

### 7. Code Documentation

#### **JSDoc Configuration**
```typescript
// src/components/DataTable/DataTable.tsx
/**
 * A flexible and accessible data table component
 * 
 * @example
 * ```tsx
 * const data = [
 *   { id: 1, name: 'John', email: 'john@example.com' },
 *   { id: 2, name: 'Jane', email: 'jane@example.com' }
 * ];
 * 
 * const columns = [
 *   { key: 'name', title: 'Name', sortable: true },
 *   { key: 'email', title: 'Email', sortable: false }
 * ];
 * 
 * <DataTable data={data} columns={columns} />
 * ```
 */

interface Column<T> {
  /** Unique identifier for the column */
  key: keyof T;
  /** Display title for the column header */
  title: string;
  /** Whether the column can be sorted */
  sortable?: boolean;
  /** Custom render function for the column */
  render?: (value: T[keyof T], row: T) => React.ReactNode;
  /** Column width */
  width?: string | number;
}

interface DataTableProps<T extends Record<string, any>> {
  /** Array of data objects to display */
  data: T[];
  /** Column definitions */
  columns: Column<T>[];
  /** Callback for row selection */
  onRowSelect?: (row: T) => void;
  /** Loading state */
  loading?: boolean;
  /** Empty state message */
  emptyMessage?: string;
  /** Table caption for accessibility */
  caption?: string;
}

/**
 * DataTable component for displaying tabular data
 * 
 * @param props - The component props
 * @returns A rendered data table
 */
function DataTable<T extends Record<string, any>>({
  data,
  columns,
  onRowSelect,
  loading = false,
  emptyMessage = 'No data available',
  caption
}: DataTableProps<T>): JSX.Element {
  // Implementation...
}
```

#### **API Documentation**
```typescript
// src/api/users.ts
/**
 * User API client
 * 
 * Provides methods for managing user data including CRUD operations,
 * authentication, and profile management.
 * 
 * @module UserAPI
 */

import { ApiResponse, PaginatedResponse, User } from '../types';

/**
 * Fetches a paginated list of users
 * 
 * @param page - Page number (1-based)
 * @param limit - Number of users per page
 * @param search - Optional search query
 * @returns Promise resolving to paginated user data
 * 
 * @throws {Error} When the API request fails
 * 
 * @example
 * ```typescript
 * try {
 *   const users = await getUsers(1, 10, 'john');
 *   console.log(users.data); // Array of users
 * } catch (error) {
 *   console.error('Failed to fetch users:', error);
 * }
 * ```
 */
export async function getUsers(
  page: number = 1,
  limit: number = 10,
  search?: string
): Promise<PaginatedResponse<User>> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
    ...(search && { search })
  });

  const response = await fetch(`/api/users?${params}`);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}
```

### 8. Team Coding Standards

#### **Style Guide Documentation**
```markdown
<!-- STYLE_GUIDE.md -->
# React Code Style Guide

## General Principles

1. **Consistency**: Follow established patterns
2. **Readability**: Write self-documenting code
3. **Maintainability**: Consider future developers
4. **Performance**: Write efficient code
5. **Accessibility**: Include all users

## Component Structure

### File Organization
```
src/
├── components/
│   └── Button/
│       ├── Button.tsx
│       ├── Button.test.tsx
│       ├── Button.stories.tsx
│       ├── Button.module.css
│       └── index.ts
```

### Component Template
```tsx
// Component imports
import React from 'react';
import classNames from 'classnames';

// Type imports
import type { ButtonProps } from './Button.types';

// Style imports
import styles from './Button.module.css';

/**
 * Button component description
 */
const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary',
  size = 'medium',
  disabled = false,
  className,
  ...props 
}) => {
  const buttonClasses = classNames(
    styles.button,
    styles[variant],
    styles[size],
    {
      [styles.disabled]: disabled
    },
    className
  );

  return (
    <button
      className={buttonClasses}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
```

## Naming Conventions

### Files and Directories
- **Components**: PascalCase (`Button.tsx`)
- **Hooks**: camelCase starting with 'use' (`useAuth.ts`)
- **Utils**: camelCase (`formatDate.ts`)
- **Constants**: UPPER_SNAKE_CASE (`API_ENDPOINTS.ts`)

### Variables and Functions
- **Variables**: camelCase (`isLoading`)
- **Functions**: camelCase (`handleClick`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- **Types/Interfaces**: PascalCase (`UserProfile`)

## Component Patterns

### Props Interface
```tsx
interface ComponentProps {
  // Required props first
  title: string;
  content: string;
  
  // Optional props with defaults
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  
  // Event handlers
  onClick?: (event: MouseEvent) => void;
  
  // Children and className last
  children?: React.ReactNode;
  className?: string;
}
```

### Default Props
```tsx
const Component: React.FC<ComponentProps> = ({
  variant = 'primary',
  size = 'medium',
  ...props
}) => {
  // Component implementation
};
```

## State Management

### useState
```tsx
// Good: Descriptive names
const [isLoading, setIsLoading] = useState(false);
const [userData, setUserData] = useState<User | null>(null);

// Bad: Generic names
const [data, setData] = useState(null);
const [flag, setFlag] = useState(false);
```

### useEffect
```tsx
// Good: Clear dependencies and cleanup
useEffect(() => {
  const controller = new AbortController();
  
  const fetchData = async () => {
    try {
      const data = await api.getUsers({ signal: controller.signal });
      setUsers(data);
    } catch (error) {
      if (!controller.signal.aborted) {
        setError(error);
      }
    }
  };
  
  fetchData();
  
  return () => {
    controller.abort();
  };
}, []);
```

## Error Handling

### Component Error Boundaries
```tsx
class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong.</div>;
    }

    return this.props.children;
  }
}
```

## Performance Guidelines

### Memoization
```tsx
// Memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  // Expensive rendering logic
}, (prevProps, nextProps) => {
  return prevProps.data === nextProps.data;
});

// useMemo for expensive calculations
const expensiveValue = useMemo(() => {
  return data.reduce((acc, item) => acc + item.value, 0);
}, [data]);

// useCallback for stable function references
const handleClick = useCallback((id: string) => {
  onItemClick(id);
}, [onItemClick]);
```

## Accessibility Guidelines

### Semantic HTML
```tsx
// Good: Semantic elements
<main>
  <section>
    <h1>Page Title</h1>
    <article>
      <h2>Article Title</h2>
      <p>Content...</p>
    </article>
  </section>
</main>

// Bad: Generic divs
<div>
  <div>
    <div>Page Title</div>
    <div>
      <div>Article Title</div>
      <div>Content...</div>
    </div>
  </div>
</div>
```

### ARIA Labels
```tsx
<button
  aria-label="Close dialog"
  aria-describedby="close-description"
  onClick={onClose}
>
  ×
</button>
<div id="close-description" className="sr-only">
  Closes the dialog and returns to the main page
</div>
```
```

#### **Code Review Checklist**
```markdown
<!-- CODE_REVIEW_CHECKLIST.md -->
# Code Review Checklist

## Functionality
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error states are managed properly
- [ ] Loading states are implemented

## Code Quality
- [ ] Code is readable and self-documenting
- [ ] Functions are small and focused
- [ ] No code duplication
- [ ] Proper abstractions are used

## Performance
- [ ] No unnecessary re-renders
- [ ] Expensive operations are memoized
- [ ] Images are optimized
- [ ] Bundle size impact is minimal

## Security
- [ ] No sensitive data in client code
- [ ] Input validation is implemented
- [ ] XSS vulnerabilities are prevented
- [ ] CSRF protection is in place

## Accessibility
- [ ] Proper semantic HTML is used
- [ ] ARIA labels are appropriate
- [ ] Keyboard navigation works
- [ ] Screen reader compatibility

## Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests are updated
- [ ] Tests are meaningful and maintainable
- [ ] Edge cases are tested

## Documentation
- [ ] README is updated if needed
- [ ] API documentation is current
- [ ] Comments explain complex logic
- [ ] Examples are provided
```

## 🎯 Practical Exercises

### Exercise 1: ESLint Custom Rules
Create custom ESLint rules for your team's specific coding standards.

### Exercise 2: TypeScript Migration
Convert a JavaScript React project to TypeScript with strict type checking.

### Exercise 3: Code Quality Pipeline
Set up a complete CI/CD pipeline with automated code quality checks.

### Exercise 4: Accessibility Audit
Perform a comprehensive accessibility audit and fix all violations.

## 📊 Assessment Criteria

### Configuration Mastery
- [ ] Properly configure ESLint for React projects
- [ ] Set up Prettier with team standards
- [ ] Implement TypeScript with strict types
- [ ] Configure pre-commit hooks effectively

### Code Quality Standards
- [ ] Write maintainable and readable code
- [ ] Follow consistent naming conventions
- [ ] Implement proper error handling
- [ ] Apply performance best practices

### Team Collaboration
- [ ] Establish coding standards documentation
- [ ] Create effective code review processes
- [ ] Implement automated quality gates
- [ ] Maintain consistent style across team

## 🚀 Project: Code Quality Dashboard

Build a comprehensive code quality monitoring system:

**Features to Implement:**
- Real-time code quality metrics
- ESLint/Prettier violation tracking
- TypeScript error monitoring
- Test coverage visualization
- Performance metric tracking
- Accessibility compliance scores

**Quality Gates:**
- 90%+ ESLint compliance
- 100% TypeScript type coverage
- 80%+ test coverage
- Zero accessibility violations
- Performance budget compliance

## 📚 Additional Resources

### Tools
- ESLint
- Prettier
- TypeScript
- Husky
- Lint-staged
- SonarQube
- Webpack Bundle Analyzer

### Documentation
- [ESLint Rules](https://eslint.org/docs/rules/)
- [Prettier Configuration](https://prettier.io/docs/en/configuration.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## ⏭️ Next Steps

After mastering this module, you'll be ready for:
- **Module 15**: Build Tools and Optimization
- Advanced tooling and automation
- Production deployment strategies
- Continuous integration/deployment

---

**Estimated Time:** 2-3 weeks  
**Difficulty:** Advanced  
**Prerequisites:** Modules 1-13 completed
