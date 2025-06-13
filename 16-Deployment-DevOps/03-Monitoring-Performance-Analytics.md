# Monitoring, Performance & Analytics

## Table of Contents
- [Application Performance Monitoring](#application-performance-monitoring)
- [Real User Monitoring (RUM)](#real-user-monitoring-rum)
- [Synthetic Monitoring](#synthetic-monitoring)
- [Error Tracking & Alerting](#error-tracking--alerting)
- [Log Management & Analysis](#log-management--analysis)
- [Infrastructure Monitoring](#infrastructure-monitoring)
- [Business Analytics](#business-analytics)
- [Performance Budgets](#performance-budgets)
- [Monitoring Dashboards](#monitoring-dashboards)
- [Alerting Strategies](#alerting-strategies)

## Application Performance Monitoring

### React Performance Monitoring Setup

```typescript
// utils/performance-monitor.ts
interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
}

class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {};
  private observer: PerformanceObserver | null = null;

  constructor() {
    this.initializeWebVitals();
    this.initializeCustomMetrics();
  }

  private initializeWebVitals() {
    // Observe Core Web Vitals
    this.observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        switch (entry.entryType) {
          case 'paint':
            if (entry.name === 'first-contentful-paint') {
              this.metrics.fcp = entry.startTime;
            }
            break;
          case 'largest-contentful-paint':
            this.metrics.lcp = entry.startTime;
            break;
          case 'first-input':
            this.metrics.fid = entry.processingStart - entry.startTime;
            break;
          case 'layout-shift':
            if (!(entry as any).hadRecentInput) {
              this.metrics.cls = (this.metrics.cls || 0) + (entry as any).value;
            }
            break;
        }
      }
    });

    this.observer.observe({ entryTypes: ['paint', 'largest-contentful-paint', 'first-input', 'layout-shift'] });
  }

  private initializeCustomMetrics() {
    // Time to Interactive
    this.measureTTI();
    
    // Bundle size monitoring
    this.trackBundleSize();
    
    // Route change performance
    this.trackRouteChanges();
  }

  private measureTTI() {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        const tti = performance.now();
        this.sendMetric('tti', tti);
      });
    }
  }

  private trackBundleSize() {
    const entries = performance.getEntriesByType('resource');
    const jsEntries = entries.filter(entry => 
      entry.name.includes('.js') && !entry.name.includes('chunk')
    );
    
    const totalSize = jsEntries.reduce((sum, entry) => 
      sum + (entry.transferSize || 0), 0
    );
    
    this.sendMetric('bundle_size', totalSize);
  }

  private trackRouteChanges() {
    let routeStartTime = performance.now();
    
    // Listen for history changes
    const originalPushState = history.pushState;
    history.pushState = function(...args) {
      const routeEndTime = performance.now();
      const routeChangeTime = routeEndTime - routeStartTime;
      
      performanceMonitor.sendMetric('route_change_time', routeChangeTime);
      routeStartTime = performance.now();
      
      return originalPushState.apply(this, args);
    };
  }

  public trackComponentRender(componentName: string, renderTime: number) {
    this.sendMetric(`component_render_${componentName}`, renderTime);
  }

  public trackUserInteraction(action: string, duration: number) {
    this.sendMetric(`user_interaction_${action}`, duration);
  }

  private sendMetric(name: string, value: number) {
    // Send to analytics service
    if (typeof gtag !== 'undefined') {
      gtag('event', 'performance_metric', {
        custom_parameter_name: name,
        custom_parameter_value: value
      });
    }

    // Send to custom analytics endpoint
    fetch('/api/analytics/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        metric: name,
        value,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href
      })
    }).catch(console.error);
  }

  public getMetrics(): Partial<PerformanceMetrics> {
    return { ...this.metrics };
  }
}

export const performanceMonitor = new PerformanceMonitor();
```

### React Component Performance Profiler

```typescript
// components/PerformanceProfiler.tsx
import React, { Profiler, ProfilerOnRenderCallback } from 'react';

interface PerformanceProfilerProps {
  id: string;
  children: React.ReactNode;
  onRender?: ProfilerOnRenderCallback;
}

const PerformanceProfiler: React.FC<PerformanceProfilerProps> = ({
  id,
  children,
  onRender
}) => {
  const handleRender: ProfilerOnRenderCallback = (
    profilerID,
    phase,
    actualDuration,
    baseDuration,
    startTime,
    commitTime,
    interactions
  ) => {
    // Log performance data
    console.log('Profiler Data:', {
      id: profilerID,
      phase,
      actualDuration,
      baseDuration,
      startTime,
      commitTime,
      interactions: Array.from(interactions)
    });

    // Send to monitoring service
    performanceMonitor.trackComponentRender(profilerID, actualDuration);

    // Custom onRender callback
    if (onRender) {
      onRender(profilerID, phase, actualDuration, baseDuration, startTime, commitTime, interactions);
    }
  };

  return (
    <Profiler id={id} onRender={handleRender}>
      {children}
    </Profiler>
  );
};

export default PerformanceProfiler;
```

### Custom Performance Hooks

```typescript
// hooks/usePerformanceMonitoring.ts
import { useEffect, useRef } from 'react';
import { performanceMonitor } from '../utils/performance-monitor';

export const useRenderTime = (componentName: string) => {
  const renderStartTime = useRef<number>();

  useEffect(() => {
    renderStartTime.current = performance.now();
  });

  useEffect(() => {
    if (renderStartTime.current) {
      const renderTime = performance.now() - renderStartTime.current;
      performanceMonitor.trackComponentRender(componentName, renderTime);
    }
  });
};

export const useInteractionTracking = () => {
  const trackInteraction = (action: string) => {
    const startTime = performance.now();
    
    return () => {
      const duration = performance.now() - startTime;
      performanceMonitor.trackUserInteraction(action, duration);
    };
  };

  return { trackInteraction };
};

export const usePageVisibility = () => {
  useEffect(() => {
    let startTime = Date.now();
    
    const handleVisibilityChange = () => {
      if (document.hidden) {
        const visibilityDuration = Date.now() - startTime;
        performanceMonitor.sendMetric('page_visibility_duration', visibilityDuration);
      } else {
        startTime = Date.now();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);
};
```

## Real User Monitoring (RUM)

### Google Analytics 4 Integration

```typescript
// utils/analytics.ts
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
    dataLayer: any[];
  }
}

class GoogleAnalytics {
  private initialized = false;

  public initialize(measurementId: string) {
    if (this.initialized) return;

    // Load Google Analytics script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(script);

    // Initialize dataLayer and gtag
    window.dataLayer = window.dataLayer || [];
    window.gtag = function() {
      window.dataLayer.push(arguments);
    };

    window.gtag('js', new Date());
    window.gtag('config', measurementId, {
      send_page_view: false, // We'll handle page views manually
      custom_map: {
        custom_parameter_1: 'performance_metric',
        custom_parameter_2: 'user_engagement'
      }
    });

    this.initialized = true;
  }

  public trackPageView(page_title: string, page_location: string) {
    if (!this.initialized) return;

    window.gtag('event', 'page_view', {
      page_title,
      page_location,
      send_to: 'GA_MEASUREMENT_ID'
    });
  }

  public trackEvent(action: string, category: string, label?: string, value?: number) {
    if (!this.initialized) return;

    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value
    });
  }

  public trackUserEngagement(engagement_time_msec: number) {
    if (!this.initialized) return;

    window.gtag('event', 'user_engagement', {
      engagement_time_msec
    });
  }

  public trackConversion(conversion_id: string, value?: number, currency?: string) {
    if (!this.initialized) return;

    window.gtag('event', 'conversion', {
      send_to: conversion_id,
      value,
      currency
    });
  }
}

export const googleAnalytics = new GoogleAnalytics();
```

### Custom RUM Implementation

```typescript
// utils/rum-collector.ts
interface RUMData {
  sessionId: string;
  userId?: string;
  timestamp: number;
  url: string;
  referrer: string;
  userAgent: string;
  viewport: {
    width: number;
    height: number;
  };
  connection?: {
    effectiveType: string;
    downlink: number;
    rtt: number;
  };
  performance: {
    navigationTiming: PerformanceNavigationTiming;
    paintTiming: PerformancePaintTiming[];
    resourceTiming: PerformanceResourceTiming[];
  };
  customMetrics: Record<string, number>;
  errors: Array<{
    message: string;
    stack: string;
    timestamp: number;
  }>;
}

class RUMCollector {
  private sessionId: string;
  private data: Partial<RUMData> = {};
  private batchedEvents: any[] = [];
  private batchTimeout: NodeJS.Timeout | null = null;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.initializeCollection();
  }

  private generateSessionId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  private initializeCollection() {
    this.collectBasicInfo();
    this.collectPerformanceData();
    this.setupErrorTracking();
    this.setupUserInteractionTracking();
  }

  private collectBasicInfo() {
    this.data = {
      sessionId: this.sessionId,
      timestamp: Date.now(),
      url: window.location.href,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    };

    // Network information if available
    if ('connection' in navigator) {
      const conn = (navigator as any).connection;
      this.data.connection = {
        effectiveType: conn.effectiveType,
        downlink: conn.downlink,
        rtt: conn.rtt
      };
    }
  }

  private collectPerformanceData() {
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        const paint = performance.getEntriesByType('paint') as PerformancePaintTiming[];
        const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

        this.data.performance = {
          navigationTiming: navigation,
          paintTiming: paint,
          resourceTiming: resources
        };

        this.sendBatch();
      }, 0);
    });
  }

  private setupErrorTracking() {
    window.addEventListener('error', (event) => {
      this.addError({
        message: event.message,
        stack: event.error?.stack || '',
        timestamp: Date.now()
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.addError({
        message: event.reason?.message || 'Unhandled Promise Rejection',
        stack: event.reason?.stack || '',
        timestamp: Date.now()
      });
    });
  }

  private setupUserInteractionTracking() {
    ['click', 'scroll', 'keydown'].forEach(eventType => {
      document.addEventListener(eventType, (event) => {
        this.trackInteraction(eventType, event);
      }, { passive: true });
    });
  }

  private trackInteraction(type: string, event: Event) {
    const interactionData = {
      type,
      timestamp: Date.now(),
      target: (event.target as Element)?.tagName || 'unknown',
      path: this.getEventPath(event)
    };

    this.batchEvent('interaction', interactionData);
  }

  private getEventPath(event: Event): string {
    let path = '';
    let element = event.target as Element;
    
    while (element && element !== document.body) {
      const id = element.id ? `#${element.id}` : '';
      const classes = element.className ? `.${element.className.split(' ').join('.')}` : '';
      path = `${element.tagName.toLowerCase()}${id}${classes} > ${path}`;
      element = element.parentElement!;
    }
    
    return path.slice(0, -3); // Remove trailing ' > '
  }

  public addCustomMetric(name: string, value: number) {
    if (!this.data.customMetrics) {
      this.data.customMetrics = {};
    }
    this.data.customMetrics[name] = value;
  }

  private addError(error: { message: string; stack: string; timestamp: number }) {
    if (!this.data.errors) {
      this.data.errors = [];
    }
    this.data.errors.push(error);
    this.sendBatch(); // Send errors immediately
  }

  private batchEvent(type: string, data: any) {
    this.batchedEvents.push({ type, data, timestamp: Date.now() });

    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
    }

    this.batchTimeout = setTimeout(() => {
      this.sendBatch();
    }, 5000); // Send batch every 5 seconds
  }

  private async sendBatch() {
    if (this.batchedEvents.length === 0 && !this.data.performance) {
      return;
    }

    const payload = {
      ...this.data,
      events: this.batchedEvents.splice(0), // Clear batched events
      timestamp: Date.now()
    };

    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon('/api/rum', JSON.stringify(payload));
      } else {
        await fetch('/api/rum', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          keepalive: true
        });
      }
    } catch (error) {
      console.error('Failed to send RUM data:', error);
    }
  }

  public destroy() {
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
    }
    this.sendBatch(); // Send any remaining data
  }
}

export const rumCollector = new RUMCollector();

// Send data before page unload
window.addEventListener('beforeunload', () => {
  rumCollector.destroy();
});
```

## Synthetic Monitoring

### Playwright Synthetic Tests

```typescript
// tests/synthetic/core-user-flows.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Core User Flows', () => {
  test('Homepage loads within performance budget', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for key content to load
    await page.waitForSelector('[data-testid="main-content"]');
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(3000); // 3 second budget
    
    // Check Core Web Vitals
    const metrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const webVitals: any = {};
          
          entries.forEach((entry) => {
            if (entry.entryType === 'paint' && entry.name === 'first-contentful-paint') {
              webVitals.fcp = entry.startTime;
            }
            if (entry.entryType === 'largest-contentful-paint') {
              webVitals.lcp = entry.startTime;
            }
          });
          
          resolve(webVitals);
        }).observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
      });
    });
    
    expect(metrics.fcp).toBeLessThan(1800); // FCP < 1.8s
    expect(metrics.lcp).toBeLessThan(2500); // LCP < 2.5s
  });

  test('User registration flow', async ({ page }) => {
    await page.goto('/register');
    
    // Fill registration form
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'securePassword123');
    await page.fill('[data-testid="confirm-password-input"]', 'securePassword123');
    
    // Submit form
    const submitButton = page.locator('[data-testid="submit-button"]');
    await expect(submitButton).toBeEnabled();
    
    const responsePromise = page.waitForResponse('/api/auth/register');
    await submitButton.click();
    const response = await responsePromise;
    
    expect(response.status()).toBe(201);
    
    // Check success state
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('Search functionality', async ({ page }) => {
    await page.goto('/');
    
    const searchInput = page.locator('[data-testid="search-input"]');
    await searchInput.fill('React components');
    await searchInput.press('Enter');
    
    // Wait for search results
    await page.waitForSelector('[data-testid="search-results"]');
    
    const results = page.locator('[data-testid="search-result-item"]');
    await expect(results).toHaveCountGreaterThan(0);
    
    // Check result relevance
    const firstResult = results.first();
    const resultText = await firstResult.textContent();
    expect(resultText?.toLowerCase()).toContain('react');
  });

  test('Mobile responsiveness', async ({ page }) => {
    // Test on mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check mobile navigation
    const mobileMenu = page.locator('[data-testid="mobile-menu-button"]');
    await expect(mobileMenu).toBeVisible();
    
    await mobileMenu.click();
    const navigationMenu = page.locator('[data-testid="navigation-menu"]');
    await expect(navigationMenu).toBeVisible();
    
    // Check responsive layout
    const mainContent = page.locator('[data-testid="main-content"]');
    const contentWidth = await mainContent.boundingBox();
    expect(contentWidth?.width).toBeLessThanOrEqual(375);
  });
});
```

### Lighthouse CI Configuration

```json
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/products',
        'http://localhost:3000/about',
        'http://localhost:3000/contact'
      ],
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--no-sandbox'
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 200 }]
      }
    },
    upload: {
      target: 'lhci',
      serverBaseUrl: 'https://lhci.example.com',
      token: process.env.LHCI_TOKEN
    }
  }
};
```

### WebPageTest Integration

```javascript
// scripts/webpagetest-monitor.js
const WebPageTest = require('webpagetest');
const wpt = new WebPageTest('www.webpagetest.org', process.env.WPT_API_KEY);

const testConfig = {
  url: 'https://myapp.example.com',
  location: 'Dulles:Chrome',
  runs: 3,
  firstViewOnly: false,
  video: true,
  lighthouse: true,
  pollResults: 5,
  timeout: 300
};

async function runPerformanceTest() {
  try {
    console.log('Starting WebPageTest...');
    
    const result = await new Promise((resolve, reject) => {
      wpt.runTest(testConfig, (err, data) => {
        if (err) reject(err);
        else resolve(data);
      });
    });

    console.log('Test completed:', result.data.summary);
    
    // Check performance budgets
    const metrics = result.data.median.firstView;
    const budgets = {
      loadTime: 3000,
      firstByte: 500,
      startRender: 1500,
      speedIndex: 2000,
      fcp: 1800,
      lcp: 2500
    };

    const violations = [];
    
    Object.entries(budgets).forEach(([metric, budget]) => {
      if (metrics[metric] > budget) {
        violations.push(`${metric}: ${metrics[metric]}ms (budget: ${budget}ms)`);
      }
    });

    if (violations.length > 0) {
      console.error('Performance budget violations:');
      violations.forEach(violation => console.error(`- ${violation}`));
      process.exit(1);
    }

    console.log('All performance budgets met!');
    
  } catch (error) {
    console.error('WebPageTest failed:', error);
    process.exit(1);
  }
}

runPerformanceTest();
```

## Error Tracking & Alerting

### Sentry Integration

```typescript
// utils/error-tracking.ts
import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';

export const initializeErrorTracking = () => {
  Sentry.init({
    dsn: process.env.REACT_APP_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    integrations: [
      new Integrations.BrowserTracing({
        tracingOrigins: ['localhost', 'myapp.example.com', /^\//],
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes
        ),
      }),
    ],
    tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
    release: process.env.REACT_APP_VERSION,
    beforeSend(event, hint) {
      // Filter out noisy errors
      if (event.exception) {
        const error = hint.originalException;
        if (error?.message?.includes('ResizeObserver loop limit exceeded')) {
          return null;
        }
      }
      return event;
    },
    beforeSendTransaction(event) {
      // Filter out unimportant transactions
      if (event.transaction?.includes('heartbeat')) {
        return null;
      }
      return event;
    }
  });
};

// Error Boundary with Sentry
export const SentryErrorBoundary = Sentry.withErrorBoundary(
  ({ children }: { children: React.ReactNode }) => children,
  {
    fallback: ({ error, resetError }) => (
      <div className="error-boundary">
        <h2>Something went wrong</h2>
        <p>{error.message}</p>
        <button onClick={resetError}>Try again</button>
      </div>
    ),
    beforeCapture: (scope, error, errorInfo) => {
      scope.setTag('errorBoundary', true);
      scope.setLevel('error');
      scope.setContext('errorInfo', errorInfo);
    }
  }
);
```

### Custom Error Monitoring

```typescript
// utils/custom-error-monitor.ts
interface ErrorReport {
  message: string;
  stack: string;
  url: string;
  lineNumber: number;
  columnNumber: number;
  timestamp: number;
  userAgent: string;
  userId?: string;
  sessionId: string;
  breadcrumbs: Breadcrumb[];
  tags: Record<string, string>;
  level: 'error' | 'warning' | 'info';
}

interface Breadcrumb {
  timestamp: number;
  message: string;
  category: string;
  level: string;
  data?: any;
}

class ErrorMonitor {
  private breadcrumbs: Breadcrumb[] = [];
  private sessionId: string;
  private maxBreadcrumbs = 50;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.setupGlobalErrorHandling();
    this.setupUnhandledRejectionHandling();
  }

  private generateSessionId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  private setupGlobalErrorHandling() {
    window.addEventListener('error', (event) => {
      this.captureError({
        message: event.message,
        stack: event.error?.stack || '',
        url: event.filename,
        lineNumber: event.lineno,
        columnNumber: event.colno,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        sessionId: this.sessionId,
        breadcrumbs: [...this.breadcrumbs],
        tags: { type: 'javascript' },
        level: 'error'
      });
    });
  }

  private setupUnhandledRejectionHandling() {
    window.addEventListener('unhandledrejection', (event) => {
      this.captureError({
        message: event.reason?.message || 'Unhandled Promise Rejection',
        stack: event.reason?.stack || '',
        url: window.location.href,
        lineNumber: 0,
        columnNumber: 0,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        sessionId: this.sessionId,
        breadcrumbs: [...this.breadcrumbs],
        tags: { type: 'promise' },
        level: 'error'
      });
    });
  }

  public addBreadcrumb(breadcrumb: Omit<Breadcrumb, 'timestamp'>) {
    this.breadcrumbs.push({
      ...breadcrumb,
      timestamp: Date.now()
    });

    if (this.breadcrumbs.length > this.maxBreadcrumbs) {
      this.breadcrumbs.shift();
    }
  }

  public captureError(errorReport: ErrorReport) {
    // Add breadcrumb for this error
    this.addBreadcrumb({
      message: errorReport.message,
      category: 'error',
      level: errorReport.level,
      data: { url: errorReport.url, line: errorReport.lineNumber }
    });

    // Send to error tracking service
    this.sendErrorReport(errorReport);
  }

  public captureException(error: Error, tags: Record<string, string> = {}) {
    this.captureError({
      message: error.message,
      stack: error.stack || '',
      url: window.location.href,
      lineNumber: 0,
      columnNumber: 0,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      sessionId: this.sessionId,
      breadcrumbs: [...this.breadcrumbs],
      tags: { ...tags, type: 'exception' },
      level: 'error'
    });
  }

  private async sendErrorReport(errorReport: ErrorReport) {
    try {
      await fetch('/api/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorReport),
        keepalive: true
      });
    } catch (sendError) {
      console.error('Failed to send error report:', sendError);
    }
  }

  public setUser(userId: string) {
    this.addBreadcrumb({
      message: `User set: ${userId}`,
      category: 'auth',
      level: 'info'
    });
  }

  public logNavigation(from: string, to: string) {
    this.addBreadcrumb({
      message: `Navigation from ${from} to ${to}`,
      category: 'navigation',
      level: 'info',
      data: { from, to }
    });
  }

  public logUserAction(action: string, data?: any) {
    this.addBreadcrumb({
      message: `User action: ${action}`,
      category: 'user',
      level: 'info',
      data
    });
  }
}

export const errorMonitor = new ErrorMonitor();
```

## Log Management & Analysis

### Structured Logging Setup

```typescript
// utils/logger.ts
enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  context?: Record<string, any>;
  userId?: string;
  sessionId?: string;
  requestId?: string;
  url: string;
  userAgent: string;
}

class Logger {
  private level: LogLevel;
  private sessionId: string;
  private userId?: string;
  private context: Record<string, any> = {};

  constructor(level: LogLevel = LogLevel.INFO) {
    this.level = level;
    this.sessionId = this.generateSessionId();
  }

  private generateSessionId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  public setUserId(userId: string) {
    this.userId = userId;
  }

  public setContext(context: Record<string, any>) {
    this.context = { ...this.context, ...context };
  }

  private createLogEntry(level: string, message: string, context?: Record<string, any>): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: { ...this.context, ...context },
      userId: this.userId,
      sessionId: this.sessionId,
      url: window.location.href,
      userAgent: navigator.userAgent
    };
  }

  private async sendLog(entry: LogEntry) {
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon('/api/logs', JSON.stringify(entry));
      } else {
        await fetch('/api/logs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(entry),
          keepalive: true
        });
      }
    } catch (error) {
      console.error('Failed to send log:', error);
    }
  }

  public debug(message: string, context?: Record<string, any>) {
    if (this.level <= LogLevel.DEBUG) {
      const entry = this.createLogEntry('DEBUG', message, context);
      console.debug(message, context);
      this.sendLog(entry);
    }
  }

  public info(message: string, context?: Record<string, any>) {
    if (this.level <= LogLevel.INFO) {
      const entry = this.createLogEntry('INFO', message, context);
      console.info(message, context);
      this.sendLog(entry);
    }
  }

  public warn(message: string, context?: Record<string, any>) {
    if (this.level <= LogLevel.WARN) {
      const entry = this.createLogEntry('WARN', message, context);
      console.warn(message, context);
      this.sendLog(entry);
    }
  }

  public error(message: string, context?: Record<string, any>) {
    if (this.level <= LogLevel.ERROR) {
      const entry = this.createLogEntry('ERROR', message, context);
      console.error(message, context);
      this.sendLog(entry);
    }
  }

  public logUserAction(action: string, details?: Record<string, any>) {
    this.info(`User action: ${action}`, {
      category: 'user_action',
      action,
      details
    });
  }

  public logPerformance(metric: string, value: number, context?: Record<string, any>) {
    this.info(`Performance metric: ${metric}`, {
      category: 'performance',
      metric,
      value,
      ...context
    });
  }

  public logError(error: Error, context?: Record<string, any>) {
    this.error(error.message, {
      category: 'error',
      stack: error.stack,
      ...context
    });
  }
}

export const logger = new Logger(
  process.env.NODE_ENV === 'development' ? LogLevel.DEBUG : LogLevel.INFO
);
```

### ELK Stack Integration

```typescript
// utils/elasticsearch-logger.ts
interface ElasticsearchConfig {
  endpoint: string;
  index: string;
  apiKey?: string;
}

class ElasticsearchLogger {
  private config: ElasticsearchConfig;
  private buffer: LogEntry[] = [];
  private flushInterval: NodeJS.Timeout;

  constructor(config: ElasticsearchConfig) {
    this.config = config;
    this.flushInterval = setInterval(() => this.flush(), 10000); // Flush every 10 seconds
  }

  public log(entry: LogEntry) {
    this.buffer.push({
      ...entry,
      '@timestamp': entry.timestamp,
      index: this.config.index
    });

    if (this.buffer.length >= 100) {
      this.flush();
    }
  }

  private async flush() {
    if (this.buffer.length === 0) return;

    const bulk = this.buffer.splice(0).map(entry => [
      { index: { _index: this.config.index } },
      entry
    ]).flat();

    try {
      const response = await fetch(`${this.config.endpoint}/_bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-ndjson',
          ...(this.config.apiKey && { 'Authorization': `ApiKey ${this.config.apiKey}` })
        },
        body: bulk.map(item => JSON.stringify(item)).join('\n') + '\n'
      });

      if (!response.ok) {
        console.error('Failed to send logs to Elasticsearch:', response.statusText);
      }
    } catch (error) {
      console.error('Error sending logs to Elasticsearch:', error);
    }
  }

  public destroy() {
    clearInterval(this.flushInterval);
    this.flush();
  }
}

// Initialize if configuration is available
const esConfig = process.env.REACT_APP_ELASTICSEARCH_ENDPOINT ? {
  endpoint: process.env.REACT_APP_ELASTICSEARCH_ENDPOINT,
  index: process.env.REACT_APP_ELASTICSEARCH_INDEX || 'react-app-logs',
  apiKey: process.env.REACT_APP_ELASTICSEARCH_API_KEY
} : null;

export const elasticsearchLogger = esConfig ? new ElasticsearchLogger(esConfig) : null;
```

## Infrastructure Monitoring

### Kubernetes Monitoring Setup

```yaml
# k8s/monitoring/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    rule_files:
      - "react_app_rules.yml"

    scrape_configs:
      - job_name: 'react-app'
        kubernetes_sd_configs:
        - role: pod
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
          action: replace
          target_label: __metrics_path__
          regex: (.+)

      - job_name: 'nginx-ingress'
        kubernetes_sd_configs:
        - role: pod
          namespaces:
            names:
            - ingress-nginx
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
          action: keep
          regex: ingress-nginx

  react_app_rules.yml: |
    groups:
    - name: react_app
      rules:
      - alert: HighErrorRate
        expr: rate(nginx_http_requests_total{status=~"5.."}[5m]) / rate(nginx_http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected
          description: Error rate is {{ $value | humanizePercentage }}

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(nginx_http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High response time detected
          description: 95th percentile response time is {{ $value }}s

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: Pod is crash looping
          description: Pod {{ $labels.pod }} is restarting frequently
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "React App Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(nginx_http_requests_total[5m]))",
            "legendFormat": "Requests/sec"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": { "mode": "thresholds" },
            "thresholds": {
              "steps": [
                { "color": "green", "value": null },
                { "color": "yellow", "value": 80 },
                { "color": "red", "value": 90 }
              ]
            }
          }
        }
      },
      {
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(nginx_http_requests_total{status=~\"5..\"}[5m])) / sum(rate(nginx_http_requests_total[5m]))",
            "legendFormat": "Error Rate"
          }
        ]
      },
      {
        "title": "Response Time Distribution",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(nginx_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(nginx_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.99, rate(nginx_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "99th percentile"
          }
        ]
      },
      {
        "title": "Pod Resource Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(container_memory_usage_bytes{pod=~\"react-app-.*\"}) by (pod)",
            "legendFormat": "Memory Usage - {{ pod }}"
          },
          {
            "expr": "sum(rate(container_cpu_usage_seconds_total{pod=~\"react-app-.*\"}[5m])) by (pod)",
            "legendFormat": "CPU Usage - {{ pod }}"
          }
        ]
      }
    ]
  }
}
```

## Business Analytics

### Custom Analytics Dashboard

```typescript
// components/AnalyticsDashboard.tsx
import React, { useEffect, useState } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';

interface AnalyticsData {
  pageViews: { date: string; views: number }[];
  userEngagement: { metric: string; value: number }[];
  performanceMetrics: { metric: string; value: number; threshold: number }[];
  errorRates: { date: string; rate: number }[];
  conversionFunnel: { step: string; users: number; dropoff: number }[];
}

const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    fetchAnalyticsData(timeRange);
  }, [timeRange]);

  const fetchAnalyticsData = async (range: string) => {
    try {
      const response = await fetch(`/api/analytics?range=${range}`);
      const analyticsData = await response.json();
      setData(analyticsData);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    }
  };

  if (!data) return <div>Loading analytics...</div>;

  const pageViewsChart = {
    labels: data.pageViews.map(d => d.date),
    datasets: [{
      label: 'Page Views',
      data: data.pageViews.map(d => d.views),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };

  const performanceChart = {
    labels: data.performanceMetrics.map(d => d.metric),
    datasets: [
      {
        label: 'Current Value',
        data: data.performanceMetrics.map(d => d.value),
        backgroundColor: 'rgba(54, 162, 235, 0.5)'
      },
      {
        label: 'Threshold',
        data: data.performanceMetrics.map(d => d.threshold),
        backgroundColor: 'rgba(255, 99, 132, 0.5)'
      }
    ]
  };

  const conversionChart = {
    labels: data.conversionFunnel.map(d => d.step),
    datasets: [{
      label: 'Users',
      data: data.conversionFunnel.map(d => d.users),
      backgroundColor: [
        'rgba(255, 99, 132, 0.5)',
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 205, 86, 0.5)',
        'rgba(75, 192, 192, 0.5)'
      ]
    }]
  };

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h1>Analytics Dashboard</h1>
        <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
          <option value="1d">Last 24 hours</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      <div className="dashboard-grid">
        <div className="chart-container">
          <h3>Page Views Over Time</h3>
          <Line data={pageViewsChart} />
        </div>

        <div className="chart-container">
          <h3>Performance Metrics vs Thresholds</h3>
          <Bar data={performanceChart} />
        </div>

        <div className="chart-container">
          <h3>Conversion Funnel</h3>
          <Pie data={conversionChart} />
        </div>

        <div className="metrics-grid">
          {data.userEngagement.map((metric, index) => (
            <div key={index} className="metric-card">
              <h4>{metric.metric}</h4>
              <div className="metric-value">{metric.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
```

### Advanced Event Tracking

```typescript
// utils/advanced-analytics.ts
interface AnalyticsEvent {
  eventName: string;
  properties: Record<string, any>;
  timestamp: number;
  userId?: string;
  sessionId: string;
  pageUrl: string;
  referrer: string;
}

class AdvancedAnalytics {
  private sessionId: string;
  private userId?: string;
  private properties: Record<string, any> = {};

  constructor() {
    this.sessionId = this.generateSessionId();
    this.setupAutoTracking();
  }

  private generateSessionId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  private setupAutoTracking() {
    // Track page views
    this.trackPageView();

    // Track form submissions
    document.addEventListener('submit', (event) => {
      const form = event.target as HTMLFormElement;
      this.track('Form Submitted', {
        formId: form.id,
        formAction: form.action,
        formMethod: form.method
      });
    });

    // Track button clicks
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      if (target.tagName === 'BUTTON' || target.role === 'button') {
        this.track('Button Clicked', {
          buttonText: target.textContent,
          buttonId: target.id,
          buttonClass: target.className
        });
      }
    });

    // Track scroll depth
    this.trackScrollDepth();

    // Track time on page
    this.trackTimeOnPage();
  }

  private trackPageView() {
    this.track('Page Viewed', {
      title: document.title,
      path: window.location.pathname,
      search: window.location.search,
      hash: window.location.hash
    });
  }

  private trackScrollDepth() {
    let maxScrollDepth = 0;
    const intervals = [25, 50, 75, 90, 100];
    const triggered = new Set<number>();

    const handleScroll = () => {
      const scrollTop = window.pageYOffset;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = Math.round((scrollTop / docHeight) * 100);

      if (scrollPercent > maxScrollDepth) {
        maxScrollDepth = scrollPercent;
      }

      intervals.forEach(interval => {
        if (scrollPercent >= interval && !triggered.has(interval)) {
          triggered.add(interval);
          this.track('Scroll Depth', {
            depth: interval,
            maxDepth: maxScrollDepth
          });
        }
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
  }

  private trackTimeOnPage() {
    const startTime = Date.now();
    let lastActiveTime = startTime;

    const updateActiveTime = () => {
      lastActiveTime = Date.now();
    };

    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
      document.addEventListener(event, updateActiveTime, { passive: true });
    });

    const sendTimeOnPage = () => {
      const totalTime = Date.now() - startTime;
      const activeTime = lastActiveTime - startTime;

      this.track('Time on Page', {
        totalTime: Math.round(totalTime / 1000),
        activeTime: Math.round(activeTime / 1000),
        engagementRate: Math.round((activeTime / totalTime) * 100)
      });
    };

    window.addEventListener('beforeunload', sendTimeOnPage);
    
    // Also send periodically for long sessions
    setInterval(sendTimeOnPage, 60000); // Every minute
  }

  public identify(userId: string, properties: Record<string, any> = {}) {
    this.userId = userId;
    this.properties = { ...this.properties, ...properties };

    this.track('User Identified', {
      userId,
      ...properties
    });
  }

  public track(eventName: string, properties: Record<string, any> = {}) {
    const event: AnalyticsEvent = {
      eventName,
      properties: { ...this.properties, ...properties },
      timestamp: Date.now(),
      userId: this.userId,
      sessionId: this.sessionId,
      pageUrl: window.location.href,
      referrer: document.referrer
    };

    this.sendEvent(event);
  }

  public trackConversion(goalName: string, value?: number, currency?: string) {
    this.track('Conversion', {
      goal: goalName,
      value,
      currency: currency || 'USD'
    });
  }

  public trackError(error: Error, context: Record<string, any> = {}) {
    this.track('Error Occurred', {
      errorMessage: error.message,
      errorStack: error.stack,
      ...context
    });
  }

  private async sendEvent(event: AnalyticsEvent) {
    try {
      // Send to multiple analytics services
      await Promise.all([
        this.sendToCustomService(event),
        this.sendToGoogleAnalytics(event),
        this.sendToMixpanel(event)
      ]);
    } catch (error) {
      console.error('Failed to send analytics event:', error);
    }
  }

  private async sendToCustomService(event: AnalyticsEvent) {
    await fetch('/api/analytics/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event),
      keepalive: true
    });
  }

  private sendToGoogleAnalytics(event: AnalyticsEvent) {
    if (typeof gtag !== 'undefined') {
      gtag('event', event.eventName, {
        ...event.properties,
        custom_parameter_user_id: event.userId,
        custom_parameter_session_id: event.sessionId
      });
    }
  }

  private sendToMixpanel(event: AnalyticsEvent) {
    if (typeof mixpanel !== 'undefined') {
      mixpanel.track(event.eventName, {
        ...event.properties,
        $user_id: event.userId,
        $session_id: event.sessionId,
        time: event.timestamp
      });
    }
  }
}

export const analytics = new AdvancedAnalytics();
```

This comprehensive monitoring and analytics setup provides detailed insights into application performance, user behavior, and system health, enabling data-driven optimization and proactive issue resolution.
