# CSS Modules & Traditional Approaches

## Table of Contents
1. [CSS Modules Fundamentals](#css-modules-fundamentals)
2. [Advanced CSS Modules Patterns](#advanced-css-modules-patterns)
3. [CSS Preprocessing with Sass/SCSS](#css-preprocessing-with-sassscss)
4. [PostCSS Integration](#postcss-integration)
5. [CSS Architecture Methodologies](#css-architecture-methodologies)
6. [Component-Based CSS Organization](#component-based-css-organization)
7. [CSS Custom Properties](#css-custom-properties)
8. [Performance Optimization](#performance-optimization)
9. [Migration Strategies](#migration-strategies)
10. [Tooling and Build Integration](#tooling-and-build-integration)

## CSS Modules Fundamentals

### Understanding CSS Modules

CSS Modules provide local scope for CSS by automatically generating unique class names, preventing style conflicts.

```css
/* Button.module.css */
.button {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.button:hover {
  background-color: #0056b3;
}

.button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

/* Size variants */
.small {
  padding: 6px 12px;
  font-size: 14px;
}

.medium {
  padding: 8px 16px;
  font-size: 16px;
}

.large {
  padding: 12px 24px;
  font-size: 18px;
}

/* Color variants */
.primary {
  background-color: #007bff;
}

.primary:hover {
  background-color: #0056b3;
}

.secondary {
  background-color: #6c757d;
}

.secondary:hover {
  background-color: #545b62;
}

.success {
  background-color: #28a745;
}

.success:hover {
  background-color: #218838;
}

.danger {
  background-color: #dc3545;
}

.danger:hover {
  background-color: #c82333;
}
```

```typescript
// Button.tsx
import React from 'react';
import styles from './Button.module.css';
import classNames from 'classnames';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  fullWidth?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  fullWidth = false,
  onClick,
  children,
  type = 'button',
  className
}) => {
  const buttonClasses = classNames(
    styles.button,
    styles[variant],
    styles[size],
    {
      [styles.fullWidth]: fullWidth,
      [styles.disabled]: disabled
    },
    className
  );

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

// Usage
const App: React.FC = () => (
  <div>
    <Button variant="primary" size="large">
      Primary Button
    </Button>
    
    <Button variant="secondary" size="medium">
      Secondary Button
    </Button>
    
    <Button variant="danger" size="small" disabled>
      Disabled Button
    </Button>
  </div>
);
```

### TypeScript Integration with CSS Modules

```typescript
// cssModules.d.ts
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// For better type safety, you can generate types
// Using typescript-plugin-css-modules or css-modules-typescript-loader

// Example generated types (Button.module.css.d.ts)
export declare const button: string;
export declare const small: string;
export declare const medium: string;
export declare const large: string;
export declare const primary: string;
export declare const secondary: string;
export declare const success: string;
export declare const danger: string;
export declare const fullWidth: string;
export declare const disabled: string;

// Type-safe usage
import styles from './Button.module.css';

// TypeScript will now provide autocomplete and type checking
const buttonClass = styles.button; // ✅ Type-safe
const invalidClass = styles.invalid; // ❌ TypeScript error
```

## Advanced CSS Modules Patterns

### Composition and Inheritance

```css
/* styles/base.module.css */
.button {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-weight: 600;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s ease;
  user-select: none;
  vertical-align: middle;
  white-space: nowrap;
}

.input {
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: inherit;
  font-size: 16px;
  padding: 8px 12px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  width: 100%;
}

.input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  outline: 0;
}

.card {
  background-color: #fff;
  border: 1px solid rgba(0, 0, 0, 0.125);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}
```

```css
/* Button.module.css */
.button {
  composes: button from './styles/base.module.css';
  padding: 8px 16px;
  font-size: 16px;
}

.primary {
  composes: button;
  background-color: #007bff;
  color: white;
}

.primary:hover {
  background-color: #0056b3;
}

.secondary {
  composes: button;
  background-color: #6c757d;
  color: white;
}

.secondary:hover {
  background-color: #545b62;
}

.outline {
  composes: button;
  background-color: transparent;
  border: 1px solid #007bff;
  color: #007bff;
}

.outline:hover {
  background-color: #007bff;
  color: white;
}

/* Size modifiers */
.small {
  padding: 6px 12px;
  font-size: 14px;
}

.large {
  padding: 12px 24px;
  font-size: 18px;
}

/* State modifiers */
.loading {
  position: relative;
  color: transparent;
}

.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 16px;
  height: 16px;
  margin: -8px 0 0 -8px;
  border: 2px solid #ffffff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

### Complex Component Patterns

```css
/* Card.module.css */
.card {
  composes: card from './styles/base.module.css';
  position: relative;
}

.header {
  background-color: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  padding: 16px 20px;
}

.body {
  padding: 20px;
}

.footer {
  background-color: rgba(0, 0, 0, 0.03);
  border-top: 1px solid rgba(0, 0, 0, 0.125);
  padding: 12px 20px;
}

.title {
  color: #212529;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  color: #6c757d;
  font-size: 14px;
  margin: 4px 0 0 0;
}

.text {
  color: #212529;
  font-size: 16px;
  line-height: 1.5;
  margin: 0;
}

/* Variants */
.elevated {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.interactive {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

/* Responsive design */
@media (max-width: 767px) {
  .header,
  .body,
  .footer {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .title {
    font-size: 18px;
  }
}
```

```typescript
// Card.tsx
import React from 'react';
import styles from './Card.module.css';
import classNames from 'classnames';

interface CardProps {
  variant?: 'default' | 'elevated';
  interactive?: boolean;
  className?: string;
  children: React.ReactNode;
}

interface CardHeaderProps {
  className?: string;
  children: React.ReactNode;
}

interface CardBodyProps {
  className?: string;
  children: React.ReactNode;
}

interface CardFooterProps {
  className?: string;
  children: React.ReactNode;
}

interface CardTitleProps {
  className?: string;
  children: React.ReactNode;
}

interface CardSubtitleProps {
  className?: string;
  children: React.ReactNode;
}

interface CardTextProps {
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  interactive = false,
  className,
  children
}) => {
  const cardClasses = classNames(
    styles.card,
    {
      [styles.elevated]: variant === 'elevated',
      [styles.interactive]: interactive
    },
    className
  );

  return (
    <div className={cardClasses}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardHeaderProps> = ({ className, children }) => (
  <div className={classNames(styles.header, className)}>
    {children}
  </div>
);

export const CardBody: React.FC<CardBodyProps> = ({ className, children }) => (
  <div className={classNames(styles.body, className)}>
    {children}
  </div>
);

export const CardFooter: React.FC<CardFooterProps> = ({ className, children }) => (
  <div className={classNames(styles.footer, className)}>
    {children}
  </div>
);

export const CardTitle: React.FC<CardTitleProps> = ({ className, children }) => (
  <h3 className={classNames(styles.title, className)}>
    {children}
  </h3>
);

export const CardSubtitle: React.FC<CardSubtitleProps> = ({ className, children }) => (
  <p className={classNames(styles.subtitle, className)}>
    {children}
  </p>
);

export const CardText: React.FC<CardTextProps> = ({ className, children }) => (
  <p className={classNames(styles.text, className)}>
    {children}
  </p>
);

// Usage
const App: React.FC = () => (
  <Card variant="elevated" interactive>
    <CardHeader>
      <CardTitle>Card Title</CardTitle>
      <CardSubtitle>Card Subtitle</CardSubtitle>
    </CardHeader>
    
    <CardBody>
      <CardText>
        This is the card content with some descriptive text
        that explains what this card is about.
      </CardText>
    </CardBody>
    
    <CardFooter>
      <Button variant="primary" size="small">
        Action
      </Button>
    </CardFooter>
  </Card>
);
```

## CSS Preprocessing with Sass/SCSS

### Advanced SCSS Features

```scss
// variables.scss
// Colors
$primary: #007bff;
$secondary: #6c757d;
$success: #28a745;
$warning: #ffc107;
$danger: #dc3545;
$info: #17a2b8;
$light: #f8f9fa;
$dark: #343a40;

// Grays
$white: #fff;
$gray-100: #f8f9fa;
$gray-200: #e9ecef;
$gray-300: #dee2e6;
$gray-400: #ced4da;
$gray-500: #adb5bd;
$gray-600: #6c757d;
$gray-700: #495057;
$gray-800: #343a40;
$gray-900: #212529;
$black: #000;

// Spacing
$spacer: 1rem;
$spacers: (
  0: 0,
  1: $spacer * 0.25,
  2: $spacer * 0.5,
  3: $spacer,
  4: $spacer * 1.5,
  5: $spacer * 3,
);

// Typography
$font-family-sans-serif: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
$font-family-monospace: SFMono-Regular, Menlo, Monaco, Consolas, monospace;

$font-size-base: 1rem;
$font-size-lg: $font-size-base * 1.25;
$font-size-sm: $font-size-base * 0.875;

$font-weight-lighter: lighter;
$font-weight-light: 300;
$font-weight-normal: 400;
$font-weight-bold: 700;
$font-weight-bolder: bolder;

$line-height-base: 1.5;
$line-height-sm: 1.25;
$line-height-lg: 2;

// Borders
$border-width: 1px;
$border-color: $gray-300;
$border-radius: 0.25rem;
$border-radius-lg: 0.3rem;
$border-radius-sm: 0.2rem;

// Shadows
$box-shadow-sm: 0 0.125rem 0.25rem rgba($black, 0.075);
$box-shadow: 0 0.5rem 1rem rgba($black, 0.15);
$box-shadow-lg: 0 1rem 3rem rgba($black, 0.175);

// Breakpoints
$grid-breakpoints: (
  xs: 0,
  sm: 576px,
  md: 768px,
  lg: 992px,
  xl: 1200px,
  xxl: 1400px
);
```

```scss
// mixins.scss
@import 'variables';

// Media query mixins
@mixin media-breakpoint-up($name, $breakpoints: $grid-breakpoints) {
  $min: map-get($breakpoints, $name);
  @if $min {
    @media (min-width: $min) {
      @content;
    }
  } @else {
    @content;
  }
}

@mixin media-breakpoint-down($name, $breakpoints: $grid-breakpoints) {
  $max: map-get($breakpoints, $name);
  @if $max {
    @media (max-width: $max - 0.02) {
      @content;
    }
  } @else {
    @content;
  }
}

@mixin media-breakpoint-between($lower, $upper, $breakpoints: $grid-breakpoints) {
  $min: map-get($breakpoints, $lower);
  $max: map-get($breakpoints, $upper);

  @if $min != null and $max != null {
    @media (min-width: $min) and (max-width: $max - 0.02) {
      @content;
    }
  } @else if $max == null {
    @include media-breakpoint-up($lower, $breakpoints) {
      @content;
    }
  } @else if $min == null {
    @include media-breakpoint-down($upper, $breakpoints) {
      @content;
    }
  }
}

// Button mixins
@mixin button-variant($background, $border, $hover-background: darken($background, 7.5%), $hover-border: darken($border, 10%)) {
  color: color-contrast($background);
  background-color: $background;
  border-color: $border;

  &:hover {
    color: color-contrast($hover-background);
    background-color: $hover-background;
    border-color: $hover-border;
  }

  &:focus,
  &.focus {
    color: color-contrast($hover-background);
    background-color: $hover-background;
    border-color: $hover-border;
    box-shadow: 0 0 0 0.2rem rgba($border, 0.5);
  }

  &:disabled,
  &.disabled {
    color: color-contrast($background);
    background-color: $background;
    border-color: $border;
    opacity: 0.65;
  }
}

@mixin button-outline-variant($color, $color-hover: color-contrast($color), $active-background: $color, $active-border: $color) {
  color: $color;
  border-color: $color;

  &:hover {
    color: $color-hover;
    background-color: $active-background;
    border-color: $active-border;
  }

  &:focus,
  &.focus {
    box-shadow: 0 0 0 0.2rem rgba($color, 0.5);
  }

  &:disabled,
  &.disabled {
    color: $color;
    background-color: transparent;
  }
}

@mixin button-size($padding-y, $padding-x, $font-size, $border-radius) {
  padding: $padding-y $padding-x;
  font-size: $font-size;
  border-radius: $border-radius;
}

// Form mixins
@mixin form-control-focus($ignore-warning: false) {
  &:focus {
    color: $input-focus-color;
    background-color: $input-focus-bg;
    border-color: $input-focus-border-color;
    outline: 0;
    box-shadow: $input-focus-box-shadow;
  }
}

@mixin form-validation-state($state, $color, $icon) {
  .#{$state}-feedback {
    display: none;
    width: 100%;
    margin-top: 0.25rem;
    font-size: 0.875em;
    color: $color;
  }

  .#{$state}-tooltip {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 5;
    display: none;
    max-width: 100%;
    padding: 0.25rem 0.5rem;
    margin-top: 0.1rem;
    font-size: 0.875rem;
    line-height: 1.5;
    color: #fff;
    background-color: rgba($color, 0.9);
    border-radius: 0.25rem;
  }

  .form-control {
    .was-validated &:#{$state},
    &.is-#{$state} {
      border-color: $color;

      &:focus {
        border-color: $color;
        box-shadow: 0 0 0 0.2rem rgba($color, 0.25);
      }

      ~ .#{$state}-feedback,
      ~ .#{$state}-tooltip {
        display: block;
      }
    }
  }
}

// Utility mixins
@mixin clearfix() {
  &::after {
    display: block;
    clear: both;
    content: "";
  }
}

@mixin sr-only() {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

@mixin text-truncate() {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// Animation mixins
@mixin transition($transition...) {
  @if length($transition) == 0 {
    $transition: all 0.15s ease-in-out;
  }

  @if length($transition) > 1 {
    $transitions: ();
    @each $value in $transition {
      $transitions: append($transitions, $value, comma);
    }
    transition: $transitions;
  } @else {
    transition: $transition;
  }
}

@mixin animation($animation...) {
  animation: $animation;
}
```

```scss
// Button.module.scss
@import 'variables';
@import 'mixins';

.button {
  display: inline-block;
  font-family: $font-family-sans-serif;
  font-weight: $font-weight-normal;
  line-height: $line-height-base;
  color: $body-color;
  text-align: center;
  text-decoration: none;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  background-color: transparent;
  border: $border-width solid transparent;
  @include button-size($btn-padding-y, $btn-padding-x, $btn-font-size, $border-radius);
  @include transition($btn-transition);

  &:hover {
    color: $body-color;
    text-decoration: none;
  }

  &:focus,
  &.focus {
    outline: 0;
    box-shadow: $btn-focus-box-shadow;
  }

  &:disabled,
  &.disabled {
    opacity: $btn-disabled-opacity;
    pointer-events: none;
  }
}

// Variant mixins
.primary {
  @include button-variant($primary, $primary);
}

.secondary {
  @include button-variant($secondary, $secondary);
}

.success {
  @include button-variant($success, $success);
}

.danger {
  @include button-variant($danger, $danger);
}

.warning {
  @include button-variant($warning, $warning);
}

.info {
  @include button-variant($info, $info);
}

.light {
  @include button-variant($light, $light);
}

.dark {
  @include button-variant($dark, $dark);
}

// Outline variants
.outlinePrimary {
  @include button-outline-variant($primary);
}

.outlineSecondary {
  @include button-outline-variant($secondary);
}

// Size variants
.sm {
  @include button-size($btn-padding-y-sm, $btn-padding-x-sm, $btn-font-size-sm, $border-radius-sm);
}

.lg {
  @include button-size($btn-padding-y-lg, $btn-padding-x-lg, $btn-font-size-lg, $border-radius-lg);
}

// Block variant
.block {
  display: block;
  width: 100%;

  + .block {
    margin-top: 0.5rem;
  }
}

// Responsive utilities
@include media-breakpoint-down(sm) {
  .responsiveStack {
    display: block;
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
```

## PostCSS Integration

### PostCSS Configuration

```javascript
// postcss.config.js
module.exports = {
  plugins: [
    require('postcss-import'),
    require('postcss-mixins'),
    require('postcss-nested'),
    require('postcss-custom-properties'),
    require('postcss-custom-media'),
    require('postcss-calc'),
    require('autoprefixer'),
    require('postcss-preset-env')({
      stage: 1,
      features: {
        'custom-properties': false,
        'nesting-rules': true
      }
    }),
    ...(process.env.NODE_ENV === 'production' ? [require('cssnano')] : [])
  ]
};
```

```css
/* Using PostCSS features */
/* variables.css */
:root {
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-danger: #dc3545;
  
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 3rem;
  
  --border-radius: 0.25rem;
  --border-radius-lg: 0.5rem;
  
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
  
  --line-height-tight: 1.25;
  --line-height-base: 1.5;
  --line-height-loose: 1.75;
  
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  --transition-fast: 150ms ease;
  --transition-base: 250ms ease;
  --transition-slow: 350ms ease;
}

/* Custom media queries */
@custom-media --screen-sm (min-width: 576px);
@custom-media --screen-md (min-width: 768px);
@custom-media --screen-lg (min-width: 992px);
@custom-media --screen-xl (min-width: 1200px);

/* Mixins */
@define-mixin button-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-family: inherit;
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-tight);
  text-align: center;
  text-decoration: none;
  transition: all var(--transition-fast);
  user-select: none;
  vertical-align: middle;
  white-space: nowrap;
  
  &:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

@define-mixin button-size $padding-y, $padding-x, $font-size {
  padding: $(padding-y) $(padding-x);
  font-size: $(font-size);
}

@define-mixin button-variant $bg-color, $text-color: white {
  background-color: $(bg-color);
  color: $(text-color);
  
  &:hover:not(:disabled) {
    background-color: color-mod($(bg-color) shade(10%));
  }
  
  &:active:not(:disabled) {
    background-color: color-mod($(bg-color) shade(15%));
  }
}
```

```css
/* Button.module.css using PostCSS */
@import 'variables.css';

.button {
  @mixin button-base;
  @mixin button-size var(--spacing-sm), var(--spacing-md), var(--font-size-base);
}

/* Size variants */
.small {
  @mixin button-size calc(var(--spacing-sm) * 0.75), var(--spacing-sm), var(--font-size-sm);
}

.large {
  @mixin button-size var(--spacing-md), var(--spacing-lg), var(--font-size-lg);
}

/* Color variants */
.primary {
  @mixin button-variant var(--color-primary);
}

.secondary {
  @mixin button-variant var(--color-secondary);
}

.success {
  @mixin button-variant var(--color-success);
}

.danger {
  @mixin button-variant var(--color-danger);
}

/* Outline variants */
.outlinePrimary {
  background-color: transparent;
  border: 1px solid var(--color-primary);
  color: var(--color-primary);
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary);
    color: white;
  }
}

/* Responsive design */
.responsiveStack {
  @media (--screen-sm) {
    display: block;
    width: 100%;
    margin-bottom: var(--spacing-sm);
  }
}

/* Full width variant */
.fullWidth {
  width: 100%;
}

/* Loading state */
.loading {
  position: relative;
  color: transparent;
  
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 1rem;
    height: 1rem;
    margin: -0.5rem 0 0 -0.5rem;
    border: 2px solid currentColor;
    border-radius: 50%;
    border-top-color: transparent;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .button {
    --color-primary: #4a90e2;
    --color-secondary: #8a939b;
    --color-success: #4caf50;
    --color-warning: #ff9800;
    --color-danger: #f44336;
  }
}
```

## CSS Architecture Methodologies

### BEM (Block Element Modifier)

```css
/* BEM Methodology Example */
/* Block */
.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Elements */
.card__header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  padding: 16px 20px;
}

.card__title {
  color: #212529;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.card__subtitle {
  color: #6c757d;
  font-size: 14px;
  margin: 4px 0 0 0;
}

.card__body {
  padding: 20px;
}

.card__text {
  color: #212529;
  font-size: 16px;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.card__footer {
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
  padding: 12px 20px;
}

.card__actions {
  display: flex;
  gap: 8px;
}

/* Modifiers */
.card--elevated {
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.card--interactive {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card--interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.2);
}

.card--compact .card__header,
.card--compact .card__body,
.card--compact .card__footer {
  padding: 12px 16px;
}

.card--borderless {
  border: none;
  box-shadow: none;
}

/* Size modifiers */
.card--small {
  max-width: 300px;
}

.card--medium {
  max-width: 500px;
}

.card--large {
  max-width: 700px;
}

/* State modifiers */
.card--loading {
  position: relative;
  overflow: hidden;
}

.card--loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.6),
    transparent
  );
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.card--disabled {
  opacity: 0.6;
  pointer-events: none;
}

/* Context-specific modifiers */
.card--primary .card__header {
  background-color: #007bff;
  color: white;
}

.card--success .card__header {
  background-color: #28a745;
  color: white;
}

.card--warning .card__header {
  background-color: #ffc107;
  color: #212529;
}

.card--danger .card__header {
  background-color: #dc3545;
  color: white;
}
```

### Atomic CSS / Utility-First Approach

```css
/* Utility Classes */
/* Spacing */
.m-0 { margin: 0; }
.m-1 { margin: 0.25rem; }
.m-2 { margin: 0.5rem; }
.m-3 { margin: 1rem; }
.m-4 { margin: 1.5rem; }
.m-5 { margin: 3rem; }

.mt-0 { margin-top: 0; }
.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.mt-5 { margin-top: 3rem; }

.mb-0 { margin-bottom: 0; }
.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 1rem; }
.mb-4 { margin-bottom: 1.5rem; }
.mb-5 { margin-bottom: 3rem; }

.ml-0 { margin-left: 0; }
.ml-1 { margin-left: 0.25rem; }
.ml-2 { margin-left: 0.5rem; }
.ml-3 { margin-left: 1rem; }
.ml-4 { margin-left: 1.5rem; }
.ml-5 { margin-left: 3rem; }

.mr-0 { margin-right: 0; }
.mr-1 { margin-right: 0.25rem; }
.mr-2 { margin-right: 0.5rem; }
.mr-3 { margin-right: 1rem; }
.mr-4 { margin-right: 1.5rem; }
.mr-5 { margin-right: 3rem; }

.mx-0 { margin-left: 0; margin-right: 0; }
.mx-1 { margin-left: 0.25rem; margin-right: 0.25rem; }
.mx-2 { margin-left: 0.5rem; margin-right: 0.5rem; }
.mx-3 { margin-left: 1rem; margin-right: 1rem; }
.mx-4 { margin-left: 1.5rem; margin-right: 1.5rem; }
.mx-5 { margin-left: 3rem; margin-right: 3rem; }

.my-0 { margin-top: 0; margin-bottom: 0; }
.my-1 { margin-top: 0.25rem; margin-bottom: 0.25rem; }
.my-2 { margin-top: 0.5rem; margin-bottom: 0.5rem; }
.my-3 { margin-top: 1rem; margin-bottom: 1rem; }
.my-4 { margin-top: 1.5rem; margin-bottom: 1.5rem; }
.my-5 { margin-top: 3rem; margin-bottom: 3rem; }

/* Padding (similar pattern as margin) */
.p-0 { padding: 0; }
.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 1rem; }
.p-4 { padding: 1.5rem; }
.p-5 { padding: 3rem; }

/* Display */
.d-none { display: none; }
.d-inline { display: inline; }
.d-inline-block { display: inline-block; }
.d-block { display: block; }
.d-flex { display: flex; }
.d-inline-flex { display: inline-flex; }
.d-grid { display: grid; }

/* Flexbox */
.flex-row { flex-direction: row; }
.flex-column { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.flex-nowrap { flex-wrap: nowrap; }

.justify-start { justify-content: flex-start; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }
.justify-between { justify-content: space-between; }
.justify-around { justify-content: space-around; }
.justify-evenly { justify-content: space-evenly; }

.items-start { align-items: flex-start; }
.items-center { align-items: center; }
.items-end { align-items: flex-end; }
.items-stretch { align-items: stretch; }
.items-baseline { align-items: baseline; }

/* Text */
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-justify { text-align: justify; }

.text-lowercase { text-transform: lowercase; }
.text-uppercase { text-transform: uppercase; }
.text-capitalize { text-transform: capitalize; }

.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-bold { font-weight: 700; }

.text-xs { font-size: 0.75rem; }
.text-sm { font-size: 0.875rem; }
.text-base { font-size: 1rem; }
.text-lg { font-size: 1.125rem; }
.text-xl { font-size: 1.25rem; }
.text-2xl { font-size: 1.5rem; }

/* Colors */
.text-primary { color: #007bff; }
.text-secondary { color: #6c757d; }
.text-success { color: #28a745; }
.text-warning { color: #ffc107; }
.text-danger { color: #dc3545; }

.bg-primary { background-color: #007bff; }
.bg-secondary { background-color: #6c757d; }
.bg-success { background-color: #28a745; }
.bg-warning { background-color: #ffc107; }
.bg-danger { background-color: #dc3545; }

/* Borders */
.border { border: 1px solid #dee2e6; }
.border-0 { border: 0; }
.border-t { border-top: 1px solid #dee2e6; }
.border-r { border-right: 1px solid #dee2e6; }
.border-b { border-bottom: 1px solid #dee2e6; }
.border-l { border-left: 1px solid #dee2e6; }

.rounded { border-radius: 0.25rem; }
.rounded-none { border-radius: 0; }
.rounded-sm { border-radius: 0.125rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-full { border-radius: 9999px; }

/* Shadows */
.shadow-none { box-shadow: none; }
.shadow-sm { box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
.shadow { box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); }
.shadow-md { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }

/* Position */
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; }

.top-0 { top: 0; }
.right-0 { right: 0; }
.bottom-0 { bottom: 0; }
.left-0 { left: 0; }

/* Width & Height */
.w-auto { width: auto; }
.w-full { width: 100%; }
.w-1\/2 { width: 50%; }
.w-1\/3 { width: 33.333333%; }
.w-2\/3 { width: 66.666667%; }
.w-1\/4 { width: 25%; }
.w-3\/4 { width: 75%; }

.h-auto { height: auto; }
.h-full { height: 100%; }
.h-screen { height: 100vh; }

/* Responsive variants */
@media (min-width: 640px) {
  .sm\:d-block { display: block; }
  .sm\:d-flex { display: flex; }
  .sm\:flex-row { flex-direction: row; }
  .sm\:text-left { text-align: left; }
  .sm\:text-center { text-align: center; }
  .sm\:w-1\/2 { width: 50%; }
  .sm\:w-1\/3 { width: 33.333333%; }
}

@media (min-width: 768px) {
  .md\:d-block { display: block; }
  .md\:d-flex { display: flex; }
  .md\:flex-row { flex-direction: row; }
  .md\:text-left { text-align: left; }
  .md\:text-center { text-align: center; }
  .md\:w-1\/2 { width: 50%; }
  .md\:w-1\/3 { width: 33.333333%; }
}

@media (min-width: 1024px) {
  .lg\:d-block { display: block; }
  .lg\:d-flex { display: flex; }
  .lg\:flex-row { flex-direction: row; }
  .lg\:text-left { text-align: left; }
  .lg\:text-center { text-align: center; }
  .lg\:w-1\/2 { width: 50%; }
  .lg\:w-1\/3 { width: 33.333333%; }
}
```

This comprehensive guide covers CSS Modules and traditional CSS approaches, including advanced patterns, SCSS preprocessing, PostCSS integration, and architectural methodologies like BEM and utility-first CSS for building scalable and maintainable styling systems in React applications.
