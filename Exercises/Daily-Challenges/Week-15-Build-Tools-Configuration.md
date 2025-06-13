# Week 15: Build Tools Configuration

## Learning Goals
- Master modern build tool configurations for React applications
- Understand webpack, Vite, and other bundler configurations
- Implement development and production optimization strategies
- Configure TypeScript, ESLint, and testing tools
- Set up automated CI/CD pipelines
- Optimize bundle size and performance
- Implement advanced development workflows

---

## Day 1: Webpack Configuration Mastery

### Challenge: Custom Webpack Setup for React
Create a custom webpack configuration from scratch for a React application with advanced features.

#### Tasks
1. **Basic Webpack Setup**
```javascript
// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: './src/index.js',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProduction 
        ? '[name].[contenthash].js' 
        : '[name].js',
      publicPath: '/',
    },
    // Configure module rules, plugins, optimization
  };
};
```

2. **Advanced Loaders Configuration**
   - Babel loader with preset configurations
   - CSS/SCSS loaders with PostCSS
   - Image and font loaders
   - TypeScript loader integration

3. **Development vs Production Configs**
   - Hot module replacement setup
   - Source maps configuration
   - Bundle optimization strategies
   - Code splitting implementation

4. **Plugin Configuration**
   - HTML webpack plugin
   - Mini CSS extract plugin
   - Bundle analyzer integration
   - Environment variables handling

#### Expected Outcome
- Fully functional webpack configuration
- Development and production modes
- Hot reloading capability
- Optimized bundle output

---

## Day 2: Vite Configuration & Optimization

### Challenge: Advanced Vite Setup
Configure Vite for maximum development speed and production optimization.

#### Tasks
1. **Vite Configuration**
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@utils': resolve(__dirname, 'src/utils'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@mui/material', '@emotion/react'],
        },
      },
    },
  },
});
```

2. **Plugin Ecosystem**
   - PWA plugin integration
   - Bundle analyzer plugin
   - Environment variable handling
   - Legacy browser support

3. **Performance Optimization**
   - Tree shaking configuration
   - Dynamic imports setup
   - Chunk splitting strategies
   - Asset optimization

4. **Development Features**
   - Hot module replacement
   - Proxy configuration for APIs
   - Mock data integration
   - Testing environment setup

#### Expected Outcome
- Optimized Vite configuration
- Fast development experience
- Production-ready builds
- Advanced plugin integrations

---

## Day 3: Babel & TypeScript Configuration

### Challenge: Advanced Compilation Setup
Configure Babel and TypeScript for modern React development.

#### Tasks
1. **Babel Configuration**
```javascript
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        browsers: ['> 1%', 'last 2 versions']
      },
      useBuiltIns: 'usage',
      corejs: 3
    }],
    ['@babel/preset-react', {
      runtime: 'automatic'
    }],
    '@babel/preset-typescript'
  ],
  plugins: [
    '@babel/plugin-proposal-class-properties',
    '@babel/plugin-proposal-optional-chaining',
    ['babel-plugin-styled-components', {
      displayName: true,
      ssr: false
    }]
  ]
};
```

2. **TypeScript Configuration**
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": "src",
    "paths": {
      "@/*": ["*"],
      "@components/*": ["components/*"]
    }
  }
}
```

3. **Advanced TypeScript Features**
   - Strict mode configuration
   - Path mapping setup
   - Declaration file generation
   - Incremental compilation

4. **Integration Testing**
   - Babel transform testing
   - TypeScript compilation verification
   - Source map validation
   - Performance benchmarking

#### Expected Outcome
- Optimized compilation pipeline
- Type-safe development environment
- Modern JavaScript features support
- Fast compilation times

---

## Day 4: ESLint & Code Quality Tools

### Challenge: Comprehensive Code Quality Setup
Configure ESLint, Prettier, and additional code quality tools.

#### Tasks
1. **ESLint Configuration**
```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:import/recommended',
    'plugin:import/typescript',
    'prettier'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true
    }
  },
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'import/order': ['error', {
      'groups': ['builtin', 'external', 'internal'],
      'newlines-between': 'always'
    }]
  }
};
```

2. **Prettier Configuration**
```javascript
// .prettierrc.js
module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 80,
  tabWidth: 2,
  useTabs: false,
  bracketSpacing: true,
  arrowParens: 'avoid'
};
```

3. **Additional Tools**
   - Husky pre-commit hooks
   - lint-staged configuration
   - Commitlint setup
   - EditorConfig implementation

4. **Custom Rules & Plugins**
   - Custom ESLint rules
   - Plugin development
   - Rule testing
   - Team standards enforcement

#### Expected Outcome
- Consistent code formatting
- Automated code quality checks
- Git hook integration
- Team development standards

---

## Day 5: Testing Tools Configuration

### Challenge: Complete Testing Environment Setup
Configure Jest, React Testing Library, and E2E testing tools.

#### Tasks
1. **Jest Configuration**
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.js'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest'
  }
};
```

2. **Testing Library Setup**
```javascript
// src/setupTests.js
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

configure({ testIdAttribute: 'data-testid' });

// Mock implementations
global.fetch = jest.fn();
global.IntersectionObserver = jest.fn();

beforeEach(() => {
  fetch.mockClear();
});
```

3. **E2E Testing Configuration**
   - Cypress setup and configuration
   - Playwright integration
   - Custom commands development
   - Visual regression testing

4. **Advanced Testing Features**
   - Mock service worker setup
   - Test data factories
   - Coverage reporting
   - Performance testing integration

#### Expected Outcome
- Comprehensive testing environment
- Automated test execution
- Coverage reporting
- E2E testing capability

---

## Day 6: Performance & Bundle Optimization

### Challenge: Advanced Bundle Analysis & Optimization
Implement sophisticated bundle optimization strategies.

#### Tasks
1. **Bundle Analysis Setup**
```javascript
// webpack-analyzer.js
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
      reportFilename: 'bundle-report.html'
    })
  ]
};
```

2. **Code Splitting Strategies**
   - Route-based splitting
   - Component-based splitting
   - Vendor chunk optimization
   - Dynamic import implementation

3. **Performance Optimization**
```javascript
// Performance monitoring setup
const performanceConfig = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
    usedExports: true,
    sideEffects: false,
  },
};
```

4. **Asset Optimization**
   - Image optimization
   - Font loading strategies
   - CSS optimization
   - Tree shaking implementation

#### Expected Outcome
- Optimized bundle sizes
- Performance metrics tracking
- Asset optimization pipeline
- Load time improvements

---

## Day 7: CI/CD Pipeline Configuration

### Challenge: Complete DevOps Pipeline Setup
Create automated CI/CD pipelines for React applications.

#### Tasks
1. **GitHub Actions Workflow**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
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
      
      - name: Run tests
        run: npm run test:ci
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Build application
        run: npm run build
      
      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: npm run deploy:staging
```

2. **Docker Configuration**
```dockerfile
# Multi-stage Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=production /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

3. **Deployment Strategies**
   - Blue-green deployment
   - Rolling updates
   - Canary releases
   - Rollback procedures

4. **Monitoring & Alerting**
   - Performance monitoring setup
   - Error tracking integration
   - Health check implementation
   - Alert configuration

#### Expected Outcome
- Automated CI/CD pipeline
- Containerized deployment
- Monitoring and alerting
- Production-ready infrastructure

---

## Weekly Assessment Project

### Project: Enterprise React Build System
Create a complete enterprise-grade build system for a React application.

#### Requirements
1. **Multi-Environment Configuration**
   - Development, staging, production configs
   - Environment-specific optimizations
   - Feature flag integration
   - Performance monitoring

2. **Advanced Build Features**
   - Micro-frontend support
   - Module federation setup
   - Advanced code splitting
   - Bundle optimization

3. **Quality Assurance**
   - Comprehensive testing setup
   - Code quality gates
   - Security scanning
   - Performance budgets

4. **DevOps Integration**
   - Complete CI/CD pipeline
   - Automated deployment
   - Monitoring and alerting
   - Disaster recovery

#### Evaluation Criteria
- Build system complexity and efficiency
- Configuration quality and maintainability
- Performance optimization effectiveness
- DevOps pipeline completeness
- Documentation quality

#### Bonus Challenges
- Implement custom webpack plugins
- Create reusable build configurations
- Set up advanced monitoring dashboards
- Implement zero-downtime deployments

---

## Resources

### Documentation
- [Webpack Documentation](https://webpack.js.org/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Babel Documentation](https://babeljs.io/docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Tools
- Bundle analyzers and optimization tools
- Performance monitoring solutions
- CI/CD platform documentation
- Docker and containerization guides

### Best Practices
- Build tool performance optimization
- Enterprise configuration patterns
- DevOps pipeline design
- Monitoring and alerting strategies