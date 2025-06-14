# ESLint & Prettier Configuration for React

## Introduction to Code Quality Tools

ESLint and Prettier are essential tools for maintaining consistent, high-quality React code. ESLint focuses on code quality and catching potential bugs, while Prettier handles code formatting. Together, they create a robust foundation for maintainable React applications.

### Why Use ESLint and Prettier?

1. **Consistency**: Enforce uniform code style across teams
2. **Error Prevention**: Catch common bugs and anti-patterns
3. **Productivity**: Reduce time spent on code reviews
4. **Maintainability**: Improve code readability and structure
5. **Team Collaboration**: Eliminate style debates and conflicts

## ESLint Setup and Configuration

### Installation

```bash
# Install ESLint and React-specific plugins
npm install --save-dev eslint @eslint/js
npm install --save-dev eslint-plugin-react eslint-plugin-react-hooks
npm install --save-dev @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install --save-dev eslint-plugin-jsx-a11y eslint-plugin-import

# For React Testing Library
npm install --save-dev eslint-plugin-testing-library eslint-plugin-jest-dom
```

### Basic ESLint Configuration

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
    jest: true,
  },
  extends: [
    'eslint:recommended',
    '@eslint/js/recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:import/errors',
    'plugin:import/warnings',
    'plugin:import/typescript',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: [
    'react',
    'react-hooks',
    '@typescript-eslint',
    'jsx-a11y',
    'import',
    'testing-library',
    'jest-dom',
  ],
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      typescript: {},
      node: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
      },
    },
  },
  rules: {
    // React Rules
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off', // Using TypeScript for prop validation
    'react/jsx-uses-react': 'off',
    'react/jsx-uses-vars': 'error',
    'react/jsx-key': 'error',
    'react/jsx-no-bind': ['error', {
      allowArrowFunctions: true,
      allowBind: false,
      ignoreRefs: true,
    }],
    'react/jsx-pascal-case': 'error',
    'react/jsx-fragments': ['error', 'syntax'],
    'react/jsx-curly-brace-presence': ['error', {
      props: 'never',
      children: 'never',
    }],
    'react/jsx-boolean-value': ['error', 'never'],
    'react/no-array-index-key': 'warn',
    'react/no-unused-prop-types': 'error',
    'react/no-unused-state': 'error',
    'react/prefer-stateless-function': 'error',
    'react/self-closing-comp': 'error',
    'react/sort-comp': 'error',

    // React Hooks Rules
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // JavaScript/TypeScript Rules
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-unused-vars': 'off', // Use TypeScript version
    '@typescript-eslint/no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    'prefer-const': 'error',
    'no-var': 'error',
    'object-shorthand': 'error',
    'prefer-template': 'error',
    'template-curly-spacing': 'error',
    'arrow-spacing': 'error',
    'comma-dangle': ['error', 'always-multiline'],
    'semi': ['error', 'never'],
    'quotes': ['error', 'single'],
    'jsx-quotes': ['error', 'prefer-double'],

    // Import Rules
    'import/order': ['error', {
      groups: [
        'builtin',
        'external',
        'internal',
        'parent',
        'sibling',
        'index',
      ],
      'newlines-between': 'always',
      alphabetize: {
        order: 'asc',
        caseInsensitive: true,
      },
    }],
    'import/no-unresolved': 'error',
    'import/no-duplicates': 'error',
    'import/no-unused-modules': 'warn',
    'import/first': 'error',
    'import/newline-after-import': 'error',

    // Accessibility Rules
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/anchor-has-content': 'error',
    'jsx-a11y/anchor-is-valid': 'error',
    'jsx-a11y/aria-activedescendant-has-tabindex': 'error',
    'jsx-a11y/aria-props': 'error',
    'jsx-a11y/aria-proptypes': 'error',
    'jsx-a11y/aria-role': 'error',
    'jsx-a11y/aria-unsupported-elements': 'error',
    'jsx-a11y/click-events-have-key-events': 'error',
    'jsx-a11y/heading-has-content': 'error',
    'jsx-a11y/iframe-has-title': 'error',
    'jsx-a11y/img-redundant-alt': 'error',
    'jsx-a11y/interactive-supports-focus': 'error',
    'jsx-a11y/label-has-associated-control': 'error',
    'jsx-a11y/no-access-key': 'error',
    'jsx-a11y/no-distracting-elements': 'error',
    'jsx-a11y/no-redundant-roles': 'error',
    'jsx-a11y/role-has-required-aria-props': 'error',
    'jsx-a11y/role-supports-aria-props': 'error',
    'jsx-a11y/scope': 'error',
    'jsx-a11y/tabindex-no-positive': 'error',
  },
  overrides: [
    // TypeScript files
    {
      files: ['**/*.ts', '**/*.tsx'],
      extends: [
        'plugin:@typescript-eslint/recommended',
        'plugin:@typescript-eslint/recommended-requiring-type-checking',
      ],
      parserOptions: {
        project: './tsconfig.json',
      },
      rules: {
        '@typescript-eslint/explicit-function-return-type': 'off',
        '@typescript-eslint/explicit-module-boundary-types': 'off',
        '@typescript-eslint/no-explicit-any': 'warn',
        '@typescript-eslint/no-unused-vars': ['error', {
          argsIgnorePattern: '^_',
        }],
        '@typescript-eslint/prefer-nullish-coalescing': 'error',
        '@typescript-eslint/prefer-optional-chain': 'error',
        '@typescript-eslint/strict-boolean-expressions': 'error',
        '@typescript-eslint/switch-exhaustiveness-check': 'error',
      },
    },
    // Test files
    {
      files: [
        '**/__tests__/**/*',
        '**/*.test.*',
        '**/*.spec.*',
      ],
      extends: [
        'plugin:testing-library/react',
        'plugin:jest-dom/recommended',
      ],
      env: {
        jest: true,
      },
      rules: {
        'testing-library/await-async-query': 'error',
        'testing-library/no-await-sync-query': 'error',
        'testing-library/no-debugging-utils': 'warn',
        'testing-library/no-dom-import': 'error',
        'testing-library/prefer-find-by': 'error',
        'testing-library/prefer-presence-queries': 'error',
        'testing-library/prefer-screen-queries': 'error',
        'testing-library/render-result-naming-convention': 'error',
      },
    },
    // Configuration files
    {
      files: [
        '*.config.js',
        '*.config.ts',
        '.eslintrc.js',
        'vite.config.*',
        'webpack.config.*',
      ],
      env: {
        node: true,
      },
      rules: {
        'no-console': 'off',
        '@typescript-eslint/no-var-requires': 'off',
      },
    },
  ],
}
```

### Advanced ESLint Rules

```javascript
// Custom rules for React projects
const customReactRules = {
  // Performance Rules
  'react/jsx-no-bind': ['error', {
    allowArrowFunctions: false,
    allowBind: false,
    allowFunctions: false,
    ignoreRefs: true,
    ignoreDOMComponents: true,
  }],
  'react/no-multi-comp': ['error', { ignoreStateless: true }],
  'react/prefer-es6-class': ['error', 'always'],
  'react/prefer-stateless-function': 'error',
  
  // Security Rules
  'react/no-danger': 'warn',
  'react/no-danger-with-children': 'error',
  'react/jsx-no-script-url': 'error',
  'react/jsx-no-target-blank': ['error', {
    allowReferrer: false,
    enforceDynamicLinks: 'always',
  }],
  
  // Best Practices
  'react/destructuring-assignment': ['error', 'always'],
  'react/function-component-definition': ['error', {
    namedComponents: 'arrow-function',
    unnamedComponents: 'arrow-function',
  }],
  'react/hook-use-state': 'error',
  'react/jsx-filename-extension': ['error', {
    extensions: ['.jsx', '.tsx'],
  }],
  'react/jsx-handler-names': ['error', {
    eventHandlerPrefix: 'handle',
    eventHandlerPropPrefix: 'on',
  }],
  'react/jsx-max-depth': ['warn', { max: 5 }],
  'react/jsx-max-props-per-line': ['error', {
    maximum: { single: 3, multi: 1 },
  }],
  'react/jsx-no-literals': ['warn', {
    noStrings: true,
    ignoreProps: false,
  }],
  'react/jsx-sort-props': ['error', {
    callbacksLast: true,
    shorthandFirst: true,
    multiline: 'last',
    reservedFirst: true,
  }],
  'react/no-unstable-nested-components': 'error',
  'react/require-default-props': 'off', // Using TypeScript
  'react/state-in-constructor': ['error', 'always'],
  'react/static-property-placement': ['error', 'property assignment'],
}
```

## Prettier Configuration

### Installation

```bash
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
```

### Prettier Configuration

```json
// .prettierrc
{
  "semi": false,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "quoteProps": "as-needed",
  "jsxSingleQuote": false,
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "embeddedLanguageFormatting": "auto",
  "htmlWhitespaceSensitivity": "css",
  "insertPragma": false,
  "proseWrap": "preserve",
  "requirePragma": false,
  "vueIndentScriptAndStyle": false
}
```

### Prettier Ignore File

```bash
# .prettierignore
node_modules
dist
build
.next
.nuxt
.cache
.parcel-cache
coverage
*.min.js
*.min.css
package-lock.json
yarn.lock
.env*
```

### Integration with ESLint

```javascript
// Updated .eslintrc.js to work with Prettier
module.exports = {
  extends: [
    // ... other extends
    'prettier', // This disables ESLint rules that conflict with Prettier
  ],
  plugins: [
    // ... other plugins
    'prettier',
  ],
  rules: {
    // ... other rules
    'prettier/prettier': 'error',
  },
}
```

## Advanced Configuration Patterns

### Project-Specific Rules

```javascript
// .eslintrc.js for different project types
const createConfig = (projectType) => {
  const baseConfig = {
    // ... base configuration
  }

  switch (projectType) {
    case 'next.js':
      return {
        ...baseConfig,
        extends: [
          ...baseConfig.extends,
          '@next/next/core-web-vitals',
        ],
        rules: {
          ...baseConfig.rules,
          '@next/next/no-html-link-for-pages': 'error',
          '@next/next/no-img-element': 'error',
          '@next/next/no-page-custom-font': 'error',
        },
      }

    case 'gatsby':
      return {
        ...baseConfig,
        env: {
          ...baseConfig.env,
          browser: true,
          node: true,
        },
        rules: {
          ...baseConfig.rules,
          'react/prop-types': 'off',
          'react/display-name': 'off',
        },
      }

    case 'react-native':
      return {
        ...baseConfig,
        extends: [
          ...baseConfig.extends,
          '@react-native-community',
        ],
        env: {
          ...baseConfig.env,
          'react-native/react-native': true,
        },
        rules: {
          ...baseConfig.rules,
          'react-native/no-unused-styles': 'error',
          'react-native/split-platform-components': 'error',
          'react-native/no-inline-styles': 'error',
          'react-native/no-color-literals': 'error',
          'react-native/no-raw-text': 'error',
        },
      }

    default:
      return baseConfig
  }
}

module.exports = createConfig(process.env.PROJECT_TYPE || 'react')
```

### Workspace Configuration

```javascript
// Root .eslintrc.js for monorepo
module.exports = {
  root: true,
  ignorePatterns: [
    'packages/*/dist',
    'packages/*/build',
    'node_modules',
  ],
  overrides: [
    {
      files: ['packages/ui/**/*'],
      extends: ['./packages/ui/.eslintrc.js'],
    },
    {
      files: ['packages/app/**/*'],
      extends: ['./packages/app/.eslintrc.js'],
    },
    {
      files: ['packages/utils/**/*'],
      extends: ['./packages/utils/.eslintrc.js'],
    },
  ],
}
```

## Custom ESLint Rules

### Creating Custom Rules

```javascript
{% raw %}
// eslint-rules/prefer-named-exports.js
module.exports = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'prefer named exports over default exports',
      category: 'Best Practices',
      recommended: false,
    },
    schema: [],
  },
  create(context) {
    return {
      ExportDefaultDeclaration(node) {
        context.report({
          node,
          message: 'Prefer named exports over default exports',
          suggest: [
            {
              desc: 'Convert to named export',
              fix(fixer) {
                const sourceCode = context.getSourceCode()
                const declaration = node.declaration
                
                if (declaration.type === 'Identifier') {
                  return fixer.replaceText(
                    node,
                    `export { ${declaration.name} }`
                  )
                }
                
                return null
              },
            },
          ],
        })
      },
    }
  },
}
{% endraw %}
```

### Component-Specific Rules

```javascript
// eslint-rules/react-component-conventions.js
module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'enforce React component naming conventions',
    },
    schema: [],
  },
  create(context) {
    return {
      FunctionDeclaration(node) {
        if (isReactComponent(node)) {
          const name = node.id.name
          
          if (!isPascalCase(name)) {
            context.report({
              node: node.id,
              message: 'React component names must be PascalCase',
            })
          }
          
          if (name.endsWith('Component')) {
            context.report({
              node: node.id,
              message: 'Avoid "Component" suffix in component names',
            })
          }
        }
      },
      
      VariableDeclarator(node) {
        if (isArrowFunctionComponent(node)) {
          const name = node.id.name
          
          if (!isPascalCase(name)) {
            context.report({
              node: node.id,
              message: 'React component names must be PascalCase',
            })
          }
        }
      },
    }
    
    function isReactComponent(node) {
      return node.id && 
             node.id.name &&
             /^[A-Z]/.test(node.id.name) &&
             hasJSXReturn(node)
    }
    
    function isArrowFunctionComponent(node) {
      return node.init &&
             node.init.type === 'ArrowFunctionExpression' &&
             node.id &&
             /^[A-Z]/.test(node.id.name) &&
             hasJSXReturn(node.init)
    }
    
    function hasJSXReturn(node) {
      // Implementation to check if function returns JSX
      return true // Simplified for example
    }
    
    function isPascalCase(str) {
      return /^[A-Z][a-zA-Z0-9]*$/.test(str)
    }
  },
}
```

## Editor Integration

### VS Code Settings

```json
// .vscode/settings.json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.insertSpaces": true,
  "editor.tabSize": 2,
  "editor.detectIndentation": false,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "eslint.workingDirectories": [
    "packages/ui",
    "packages/app"
  ],
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.suggest.autoImports": true,
  "typescript.updateImportsOnFileMove.enabled": "always",
  "javascript.suggest.autoImports": true,
  "javascript.updateImportsOnFileMove.enabled": "always",
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact",
    "typescript": "typescriptreact"
  },
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

### Extensions Recommendations

```json
// .vscode/extensions.json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-json",
    "usernamehw.errorlens",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

## Pre-commit Hooks

### Husky and lint-staged Setup

```bash
npm install --save-dev husky lint-staged
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
```

```json
// package.json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "git add"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write",
      "git add"
    ]
  },
  "scripts": {
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint src --ext .js,.jsx,.ts,.tsx --fix",
    "format": "prettier --write src/**/*.{js,jsx,ts,tsx,json,md}",
    "prepare": "husky install"
  }
}
```

### Advanced Pre-commit Workflow

```bash
#!/bin/sh
# .husky/pre-commit

. "$(dirname "$0")/_/husky.sh"

echo "🔍 Running pre-commit checks..."

# Run lint-staged
npx lint-staged

# Type checking
echo "🔎 Type checking..."
npx tsc --noEmit

# Run tests for changed files
echo "🧪 Running tests..."
npm run test:changed

# Check bundle size
echo "📦 Checking bundle size..."
npm run build:analyze

echo "✅ Pre-commit checks passed!"
```

## Continuous Integration

### GitHub Actions ESLint Workflow

```yaml
{% raw %}
# .github/workflows/code-quality.yml
name: Code Quality

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run ESLint
        run: npm run lint
        
      - name: Run Prettier check
        run: npm run format:check
        
      - name: Run type check
        run: npm run type-check
        
      - name: Upload ESLint results
        uses: github/super-linter@v4
        if: always()
        env:
          DEFAULT_BRANCH: main
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          VALIDATE_JAVASCRIPT_ES: true
          VALIDATE_TYPESCRIPT_ES: true
{% endraw %}
```

## Performance Optimization

### ESLint Performance Tips

```javascript
// .eslintrc.js optimized for performance
module.exports = {
  // Cache results to speed up subsequent runs
  cache: true,
  cacheLocation: 'node_modules/.cache/eslint/',
  
  // Ignore files that don't need linting
  ignorePatterns: [
    'dist/',
    'build/',
    'coverage/',
    'node_modules/',
    '*.min.js',
    'public/',
    '.next/',
    '.cache/',
    'storybook-static/',
  ],
  
  // Use specific parser for different file types
  overrides: [
    {
      files: ['*.js', '*.jsx'],
      parser: 'espree', // Faster for JS files
    },
    {
      files: ['*.ts', '*.tsx'],
      parser: '@typescript-eslint/parser',
      parserOptions: {
        project: './tsconfig.json',
        tsconfigRootDir: __dirname,
      },
    },
  ],
}
```

### Parallel Processing

```json
// package.json
{
  "scripts": {
    "lint:parallel": "eslint src --ext .js,.jsx,.ts,.tsx --cache --max-warnings 0",
    "lint:fix:parallel": "eslint src --ext .js,.jsx,.ts,.tsx --fix --cache",
    "format:parallel": "prettier --write src/**/*.{js,jsx,ts,tsx} --cache",
    "quality:check": "npm-run-all --parallel lint:parallel format:check type-check"
  }
}
```

## Troubleshooting Common Issues

### Rule Conflicts

```javascript
// Resolving common ESLint/Prettier conflicts
module.exports = {
  extends: [
    '@typescript-eslint/recommended',
    'prettier', // Must be last to override other configs
  ],
  rules: {
    // Disable rules that conflict with Prettier
    'max-len': 'off',
    'indent': 'off',
    '@typescript-eslint/indent': 'off',
    
    // Configure rules that work well with Prettier
    'prettier/prettier': ['error', {
      endOfLine: 'auto', // Handle different OS line endings
    }],
  },
}
```

### TypeScript Integration Issues

```javascript
// Handling TypeScript project references
module.exports = {
  overrides: [
    {
      files: ['*.ts', '*.tsx'],
      parserOptions: {
        project: ['./tsconfig.json', './packages/*/tsconfig.json'],
        tsconfigRootDir: __dirname,
        createDefaultProgram: true, // Fallback for files not in tsconfig
      },
      rules: {
        '@typescript-eslint/no-floating-promises': 'error',
        '@typescript-eslint/await-thenable': 'error',
        '@typescript-eslint/no-misused-promises': 'error',
      },
    },
  ],
}
```

## Best Practices Summary

### Configuration Management

1. **Start Simple**: Begin with recommended configs and gradually customize
2. **Team Consensus**: Establish rules through team discussion
3. **Documentation**: Document custom rules and their rationale
4. **Regular Updates**: Keep tools and configurations up to date
5. **Performance**: Monitor linting performance and optimize accordingly

### Rule Selection

1. **Error vs Warning**: Use errors for bugs, warnings for style preferences
2. **Gradual Adoption**: Introduce strict rules incrementally
3. **Context-Specific**: Different rules for different file types
4. **Accessibility**: Always include accessibility rules
5. **Security**: Include security-focused rules

### Team Workflow

1. **IDE Integration**: Ensure all team members have proper editor setup
2. **Pre-commit Hooks**: Catch issues before they reach the repository
3. **CI/CD Integration**: Enforce quality checks in automated pipelines
4. **Training**: Educate team members on tool usage and rule rationales
5. **Continuous Improvement**: Regularly review and update configurations

This comprehensive ESLint and Prettier setup provides a solid foundation for maintaining high-quality React code across any project size or team structure.
