# Performance Monitoring & Profiling

## Table of Contents
1. [Introduction to Performance Monitoring](#introduction-to-performance-monitoring)
2. [React DevTools Profiler](#react-devtools-profiler)
3. [Custom Performance Metrics](#custom-performance-metrics)
4. [Real-Time Performance Monitoring](#real-time-performance-monitoring)
5. [Performance Budgets & Alerts](#performance-budgets--alerts)
6. [Browser Performance APIs](#browser-performance-apis)
7. [Automated Performance Testing](#automated-performance-testing)
8. [Performance Analytics & Reporting](#performance-analytics--reporting)

## Introduction to Performance Monitoring

Performance monitoring is crucial for maintaining optimal React application performance in production environments. It helps identify bottlenecks, track performance regressions, and ensure consistent user experience.

### Performance Metrics Overview

```jsx
// Core Web Vitals and React-specific metrics
const PERFORMANCE_METRICS = {
  // Core Web Vitals
  LCP: 'Largest Contentful Paint',      // Loading performance
  FID: 'First Input Delay',             // Interactivity
  CLS: 'Cumulative Layout Shift',       // Visual stability
  
  // React-specific metrics
  componentRenderTime: 'Component render duration',
  reRenderCount: 'Number of re-renders',
  commitTime: 'React commit phase duration',
  mountTime: 'Component mount time',
  
  // Custom metrics
  userFlowDuration: 'Time to complete user flows',
  apiResponseTime: 'API call response times',
  bundleLoadTime: 'JavaScript bundle load time'
};

// Performance thresholds
const PERFORMANCE_THRESHOLDS = {
  LCP: { good: 2500, needsImprovement: 4000 },
  FID: { good: 100, needsImprovement: 300 },
  CLS: { good: 0.1, needsImprovement: 0.25 },
  componentRender: { good: 16, needsImprovement: 50 },
  bundleSize: { good: 250000, needsImprovement: 500000 }
};
```

### Performance Monitoring Architecture

```jsx
{% raw %}
// Central performance monitoring system
class PerformanceMonitor {
  constructor(config = {}) {
    this.config = {
      sampleRate: 1, // 100% sampling
      maxMetrics: 1000,
      reportingInterval: 30000, // 30 seconds
      apiEndpoint: '/api/performance',
      ...config
    };
    
    this.metrics = new Map();
    this.observers = new Map();
    this.isReporting = false;
    
    this.initializeObservers();
    this.startReporting();
  }
  
  initializeObservers() {
    // Web Vitals observer
    if ('PerformanceObserver' in window) {
      this.setupWebVitalsObserver();
      this.setupNavigationObserver();
      this.setupResourceObserver();
    }
    
    // React-specific observers
    this.setupReactObserver();
  }
  
  setupWebVitalsObserver() {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric('webVitals', {
            name: entry.name,
            value: entry.value,
            rating: this.getRating(entry.name, entry.value),
            timestamp: Date.now()
          });
        }
      });
      
      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
      this.observers.set('webVitals', observer);
    } catch (error) {
      console.warn('Web Vitals observer not supported:', error);
    }
  }
  
  setupNavigationObserver() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        this.recordMetric('navigation', {
          domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
          loadComplete: entry.loadEventEnd - entry.loadEventStart,
          domInteractive: entry.domInteractive - entry.fetchStart,
          timestamp: Date.now()
        });
      }
    });
    
    observer.observe({ entryTypes: ['navigation'] });
    this.observers.set('navigation', observer);
  }
  
  setupResourceObserver() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name.includes('.js') || entry.name.includes('.css')) {
          this.recordMetric('resource', {
            name: entry.name,
            size: entry.transferSize,
            duration: entry.duration,
            type: entry.initiatorType,
            timestamp: Date.now()
          });
        }
      }
    });
    
    observer.observe({ entryTypes: ['resource'] });
    this.observers.set('resource', observer);
  }
  
  setupReactObserver() {
    // This would be integrated with React DevTools Profiler
    this.reactMetrics = {
      renders: new Map(),
      commits: new Map(),
      interactions: new Map()
    };
  }
  
  recordMetric(category, data) {
    if (Math.random() > this.config.sampleRate) return;
    
    if (!this.metrics.has(category)) {
      this.metrics.set(category, []);
    }
    
    const categoryMetrics = this.metrics.get(category);
    categoryMetrics.push(data);
    
    // Limit metrics to prevent memory issues
    if (categoryMetrics.length > this.config.maxMetrics) {
      categoryMetrics.shift();
    }
  }
  
  getRating(metricName, value) {
    const thresholds = PERFORMANCE_THRESHOLDS[metricName.replace('-', '')];
    if (!thresholds) return 'unknown';
    
    if (value <= thresholds.good) return 'good';
    if (value <= thresholds.needsImprovement) return 'needs-improvement';
    return 'poor';
  }
  
  async sendReport() {
    const report = {
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      metrics: Object.fromEntries(this.metrics),
      sessionId: this.getSessionId()
    };
    
    try {
      await fetch(this.config.apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report)
      });
      
      this.clearMetrics();
    } catch (error) {
      console.error('Failed to send performance report:', error);
    }
  }
  
  getSessionId() {
    let sessionId = sessionStorage.getItem('performanceSessionId');
    if (!sessionId) {
      sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('performanceSessionId', sessionId);
    }
    return sessionId;
  }
}

// Global performance monitor instance
const performanceMonitor = new PerformanceMonitor();
{% endraw %}
```

## React DevTools Profiler

### Advanced Profiler Integration

```jsx
{% raw %}
import { Profiler } from 'react';

// Enhanced profiler component
function EnhancedProfiler({ 
  id, 
  children, 
  onRender,
  threshold = 16,
  enableLogging = process.env.NODE_ENV === 'development'
}) {
  const renderHistory = useRef([]);
  const slowRenderCount = useRef(0);
  
  const handleRender = useCallback((
    profilerId,
    phase,
    actualDuration,
    baseDuration,
    startTime,
    commitTime,
    interactions
  ) => {
    const renderData = {
      id: profilerId,
      phase,
      actualDuration,
      baseDuration,
      startTime,
      commitTime,
      interactions: Array.from(interactions),
      timestamp: Date.now()
    };
    
    // Store render history
    renderHistory.current.push(renderData);
    if (renderHistory.current.length > 100) {
      renderHistory.current.shift();
    }
    
    // Track slow renders
    if (actualDuration > threshold) {
      slowRenderCount.current++;
      
      if (enableLogging) {
        console.warn(`Slow render detected in ${profilerId}:`, {
          duration: actualDuration,
          phase,
          slowRenderCount: slowRenderCount.current
        });
      }
    }
    
    // Calculate performance metrics
    const efficiency = baseDuration > 0 
      ? ((baseDuration - actualDuration) / baseDuration * 100).toFixed(2)
      : 100;
    
    const metrics = {
      ...renderData,
      efficiency: parseFloat(efficiency),
      isSlow: actualDuration > threshold
    };
    
    // Send to performance monitor
    performanceMonitor.recordMetric('reactRender', metrics);
    
    // Call custom onRender if provided
    onRender?.(metrics);
  }, [threshold, enableLogging, onRender]);
  
  return (
    <Profiler id={id} onRender={handleRender}>
      {children}
    </Profiler>
  );
}

// Component-level performance tracking
function useComponentPerformance(componentName) {
  const renderCount = useRef(0);
  const renderTimes = useRef([]);
  const mountTime = useRef(null);
  
  // Track mount time
  useEffect(() => {
    mountTime.current = performance.now();
    
    return () => {
      const unmountTime = performance.now();
      const lifetime = unmountTime - mountTime.current;
      
      performanceMonitor.recordMetric('componentLifetime', {
        component: componentName,
        lifetime,
        renderCount: renderCount.current,
        averageRenderTime: renderTimes.current.length > 0
          ? renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length
          : 0
      });
    };
  }, [componentName]);
  
  // Track render times
  useLayoutEffect(() => {
    const renderEndTime = performance.now();
    renderCount.current++;
    
    // Calculate render time (approximate)
    const renderTime = renderEndTime - (mountTime.current || renderEndTime);
    renderTimes.current.push(renderTime);
    
    // Keep only last 10 render times
    if (renderTimes.current.length > 10) {
      renderTimes.current.shift();
    }
  });
  
  return {
    renderCount: renderCount.current,
    averageRenderTime: renderTimes.current.length > 0
      ? renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length
      : 0
  };
}
{% endraw %}
```

### Profiler Data Analysis

```jsx
// Performance analysis utilities
class ProfilerAnalyzer {
  constructor() {
    this.data = [];
    this.thresholds = {
      slow: 16,
      critical: 50
    };
  }
  
  addProfilerData(data) {
    this.data.push(data);
    
    // Keep only recent data (last 1000 renders)
    if (this.data.length > 1000) {
      this.data.shift();
    }
  }
  
  getSlowComponents() {
    const slowRenders = this.data.filter(d => d.actualDuration > this.thresholds.slow);
    const componentCounts = new Map();
    
    slowRenders.forEach(render => {
      const count = componentCounts.get(render.id) || 0;
      componentCounts.set(render.id, count + 1);
    });
    
    return Array.from(componentCounts.entries())
      .sort(([, a], [, b]) => b - a)
      .map(([id, count]) => ({
        component: id,
        slowRenderCount: count,
        percentage: (count / this.data.filter(d => d.id === id).length * 100).toFixed(2)
      }));
  }
  
  getRenderStats() {
    if (this.data.length === 0) return {};
    
    const durations = this.data.map(d => d.actualDuration);
    const sorted = durations.sort((a, b) => a - b);
    
    return {
      total: this.data.length,
      average: durations.reduce((a, b) => a + b, 0) / durations.length,
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)],
      slowRenders: durations.filter(d => d > this.thresholds.slow).length,
      criticalRenders: durations.filter(d => d > this.thresholds.critical).length
    };
  }
  
  getPerformanceTrends(timeWindow = 300000) { // 5 minutes
    const now = Date.now();
    const recentData = this.data.filter(d => now - d.timestamp < timeWindow);
    
    // Group by time buckets (1 minute intervals)
    const buckets = new Map();
    recentData.forEach(d => {
      const bucket = Math.floor(d.timestamp / 60000) * 60000;
      if (!buckets.has(bucket)) {
        buckets.set(bucket, []);
      }
      buckets.get(bucket).push(d.actualDuration);
    });
    
    return Array.from(buckets.entries()).map(([timestamp, durations]) => ({
      timestamp,
      averageDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
      renderCount: durations.length,
      slowRenders: durations.filter(d => d > this.thresholds.slow).length
    }));
  }
}

// Hook for using profiler analyzer
function useProfilerAnalyzer() {
  const analyzer = useRef(new ProfilerAnalyzer());
  const [stats, setStats] = useState({});
  
  const addData = useCallback((data) => {
    analyzer.current.addProfilerData(data);
  }, []);
  
  const getAnalysis = useCallback(() => {
    return {
      renderStats: analyzer.current.getRenderStats(),
      slowComponents: analyzer.current.getSlowComponents(),
      phaseBreakdown: analyzer.current.getPhaseBreakdown(),
      trends: analyzer.current.getPerformanceTrends()
    };
  }, []);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(getAnalysis());
    }, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, [getAnalysis]);
  
  return { addData, stats, getAnalysis };
}
```

## Custom Performance Metrics

### User Interaction Metrics

```jsx
{% raw %}
// User interaction performance tracking
function useInteractionTracking() {
  const interactions = useRef([]);
  const currentInteraction = useRef(null);
  
  const startInteraction = useCallback((type, target) => {
    const interaction = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      target,
      startTime: performance.now(),
      endTime: null,
      duration: null,
      events: []
    };
    
    currentInteraction.current = interaction;
    
    // Mark the interaction start
    if ('performance' in window && 'mark' in performance) {
      performance.mark(`interaction-${interaction.id}-start`);
    }
    
    return interaction.id;
  }, []);
  
  const addInteractionEvent = useCallback((event, data = {}) => {
    if (currentInteraction.current) {
      currentInteraction.current.events.push({
        event,
        timestamp: performance.now(),
        data
      });
    }
  }, []);
  
  const endInteraction = useCallback((interactionId) => {
    if (currentInteraction.current?.id === interactionId) {
      const interaction = currentInteraction.current;
      interaction.endTime = performance.now();
      interaction.duration = interaction.endTime - interaction.startTime;
      
      // Mark the interaction end
      if ('performance' in window && 'mark' in performance) {
        performance.mark(`interaction-${interaction.id}-end`);
        performance.measure(
          `interaction-${interaction.id}`,
          `interaction-${interaction.id}-start`,
          `interaction-${interaction.id}-end`
        );
      }
      
      interactions.current.push(interaction);
      currentInteraction.current = null;
      
      // Send to performance monitor
      performanceMonitor.recordMetric('userInteraction', interaction);
      
      // Log slow interactions
      if (interaction.duration > 100) {
        console.warn('Slow interaction detected:', interaction);
      }
    }
  }, []);
  
  const getInteractionStats = useCallback(() => {
    const durations = interactions.current.map(i => i.duration).filter(Boolean);
    
    if (durations.length === 0) return null;
    
    const sorted = durations.sort((a, b) => a - b);
    
    return {
      total: interactions.current.length,
      average: durations.reduce((a, b) => a + b, 0) / durations.length,
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      slowInteractions: durations.filter(d => d > 100).length
    };
  }, []);
  
  return {
    startInteraction,
    addInteractionEvent,
    endInteraction,
    getInteractionStats,
    currentInteraction: currentInteraction.current
  };
}

// Enhanced button with interaction tracking
function TrackedButton({ onClick, children, ...props }) {
  const { startInteraction, endInteraction } = useInteractionTracking();
  
  const handleClick = useCallback(async (e) => {
    const interactionId = startInteraction('click', 'button');
    
    try {
      const result = await onClick?.(e);
      endInteraction(interactionId);
      return result;
    } catch (error) {
      endInteraction(interactionId);
      throw error;
    }
  }, [onClick, startInteraction, endInteraction]);
  
  return (
    <button onClick={handleClick} {...props}>
      {children}
    </button>
  );
}
{% endraw %}
```

## Real-Time Performance Monitoring

### Performance Dashboard Hook

```jsx
{% raw %}
// Real-time performance dashboard
function usePerformanceDashboard() {
  const [metrics, setMetrics] = useState({
    fps: 0,
    memoryUsage: { used: 0, total: 0, limit: 0 },
    renderingStats: { total: 0, slow: 0, average: 0 },
    networkRequests: { pending: 0, completed: 0, failed: 0 },
    userInteractions: { total: 0, slow: 0 }
  });
  
  const frameCount = useRef(0);
  const lastTime = useRef(performance.now());
  
  // FPS monitoring
  useEffect(() => {
    const updateFPS = () => {
      frameCount.current++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime.current >= 1000) {
        const fps = Math.round((frameCount.current * 1000) / (currentTime - lastTime.current));
        
        setMetrics(prev => ({ ...prev, fps }));
        
        frameCount.current = 0;
        lastTime.current = currentTime;
      }
      
      requestAnimationFrame(updateFPS);
    };
    
    const animationId = requestAnimationFrame(updateFPS);
    return () => cancelAnimationFrame(animationId);
  }, []);
  
  // Memory usage monitoring
  useEffect(() => {
    const updateMemoryUsage = () => {
      if (performance.memory) {
        const memoryUsage = {
          used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
          total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
          limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
        };
        
        setMetrics(prev => ({ ...prev, memoryUsage }));
      }
    };
    
    updateMemoryUsage();
    const interval = setInterval(updateMemoryUsage, 2000);
    
    return () => clearInterval(interval);
  }, []);
  
  return metrics;
}

// Performance dashboard component
function PerformanceDashboard() {
  const metrics = usePerformanceDashboard();
  const [isVisible, setIsVisible] = useState(false);
  
  // Toggle with keyboard shortcut
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        setIsVisible(prev => !prev);
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);
  
  if (!isVisible) return null;
  
  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      width: '300px',
      background: 'rgba(0, 0, 0, 0.9)',
      color: 'white',
      padding: '15px',
      borderRadius: '8px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 10000
    }}>
      <h3 style={{ margin: '0 0 10px 0' }}>Performance Monitor</h3>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>FPS:</strong> {metrics.fps}
        <div style={{
          width: '100%',
          height: '4px',
          background: '#333',
          borderRadius: '2px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${Math.min(metrics.fps / 60 * 100, 100)}%`,
            height: '100%',
            background: metrics.fps >= 55 ? '#4caf50' : metrics.fps >= 30 ? '#ff9800' : '#f44336'
          }} />
        </div>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>Memory:</strong> {metrics.memoryUsage.used}MB / {metrics.memoryUsage.limit}MB
        <div style={{
          width: '100%',
          height: '4px',
          background: '#333',
          borderRadius: '2px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${(metrics.memoryUsage.used / metrics.memoryUsage.limit) * 100}%`,
            height: '100%',
            background: '#2196f3'
          }} />
        </div>
      </div>
      
      <div style={{ 
        marginTop: '10px', 
        fontSize: '10px', 
        color: '#ccc' 
      }}>
        Press Ctrl+Shift+P to toggle
      </div>
    </div>
  );
}
{% endraw %}
```

## Performance Budgets & Alerts

### Performance Budget System

```jsx
{% raw %}
// Performance budget configuration
const PERFORMANCE_BUDGETS = {
  // Bundle size budgets (in KB)
  bundleSizes: {
    main: 250,
    vendor: 500,
    total: 1000
  },
  
  // Runtime performance budgets
  runtime: {
    firstContentfulPaint: 1500,
    largestContentfulPaint: 2500,
    firstInputDelay: 100,
    cumulativeLayoutShift: 0.1
  },
  
  // React-specific budgets
  react: {
    averageComponentRenderTime: 16,
    slowRendersPercentage: 5,
    reRendersPerInteraction: 10
  }
};

// Performance budget monitor
class PerformanceBudgetMonitor {
  constructor(budgets = PERFORMANCE_BUDGETS) {
    this.budgets = budgets;
    this.violations = new Map();
    this.alertHandlers = new Set();
    
    this.startMonitoring();
  }
  
  checkBudget(metricPath, value, budget, context = '') {
    if (value > budget) {
      const violation = {
        metric: metricPath,
        value,
        budget,
        overage: value - budget,
        percentage: ((value - budget) / budget * 100).toFixed(2),
        context,
        timestamp: Date.now()
      };
      
      this.violations.set(metricPath, violation);
      this.triggerAlert(violation);
    } else {
      this.violations.delete(metricPath);
    }
  }
  
  triggerAlert(violation) {
    const alert = {
      type: 'performance-budget-violation',
      severity: this.getSeverity(violation.percentage),
      message: `Performance budget exceeded: ${violation.metric}`,
      violation
    };
    
    this.alertHandlers.forEach(handler => {
      try {
        handler(alert);
      } catch (error) {
        console.error('Alert handler error:', error);
      }
    });
  }
  
  getSeverity(overagePercentage) {
    if (overagePercentage > 50) return 'critical';
    if (overagePercentage > 25) return 'high';
    if (overagePercentage > 10) return 'medium';
    return 'low';
  }
}
{% endraw %}
```

## Browser Performance APIs

### Comprehensive Performance API Integration

```jsx
// Browser performance API wrapper
class BrowserPerformanceAPI {
  constructor() {
    this.observers = new Map();
    this.metrics = new Map();
    
    this.initializeAPIs();
  }
  
  initializeAPIs() {
    this.initializePerformanceObserver();
    this.initializeResourceTiming();
    this.initializeNavigationTiming();
    this.initializeLongTaskObserver();
  }
  
  initializePerformanceObserver() {
    if ('PerformanceObserver' in window) {
      // Paint timing
      const paintObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric('paint', {
            name: entry.name,
            value: entry.startTime,
            timestamp: Date.now()
          });
        }
      });
      
      paintObserver.observe({ entryTypes: ['paint'] });
      this.observers.set('paint', paintObserver);
      
      // Layout shift
      const layoutShiftObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            this.recordMetric('layoutShift', {
              value: entry.value,
              timestamp: Date.now()
            });
          }
        }
      });
      
      layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.set('layoutShift', layoutShiftObserver);
    }
  }
  
  recordMetric(category, data) {
    if (!this.metrics.has(category)) {
      this.metrics.set(category, []);
    }
    
    this.metrics.get(category).push(data);
  }
  
  // Get comprehensive performance data
  getPerformanceSnapshot() {
    const navigation = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');
    const resources = performance.getEntriesByType('resource');
    
    return {
      timestamp: Date.now(),
      navigation: navigation ? {
        type: navigation.type,
        redirectCount: navigation.redirectCount,
        timing: {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          domInteractive: navigation.domInteractive - navigation.fetchStart
        }
      } : null,
      paint: paint.reduce((acc, entry) => {
        acc[entry.name] = entry.startTime;
        return acc;
      }, {}),
      resources: resources.map(r => ({
        name: r.name,
        type: r.initiatorType,
        size: r.transferSize,
        duration: r.duration
      })),
      memory: performance.memory ? {
        used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
        total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
        limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
      } : null,
      customMetrics: Object.fromEntries(this.metrics)
    };
  }
}
```

## Automated Performance Testing

### Performance Test Suite

```jsx
{% raw %}
// Performance test framework
class PerformanceTestSuite {
  constructor() {
    this.tests = new Map();
    this.results = new Map();
    this.thresholds = new Map();
  }
  
  addTest(name, testFunction, threshold = {}) {
    this.tests.set(name, testFunction);
    this.thresholds.set(name, threshold);
  }
  
  async runTest(name) {
    const testFunction = this.tests.get(name);
    const threshold = this.thresholds.get(name);
    
    if (!testFunction) {
      throw new Error(`Test "${name}" not found`);
    }
    
    const startTime = performance.now();
    
    try {
      const result = await testFunction();
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      const testResult = {
        name,
        success: true,
        duration,
        result,
        threshold,
        passed: this.evaluateThreshold(duration, threshold),
        timestamp: Date.now()
      };
      
      this.results.set(name, testResult);
      return testResult;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      const testResult = {
        name,
        success: false,
        duration,
        error: error.message,
        threshold,
        passed: false,
        timestamp: Date.now()
      };
      
      this.results.set(name, testResult);
      return testResult;
    }
  }
  
  evaluateThreshold(duration, threshold) {
    if (!threshold.maxDuration) return true;
    return duration <= threshold.maxDuration;
  }
  
  generateReport() {
    const results = this.getResults();
    const passed = results.filter(r => r.passed).length;
    const failed = results.filter(r => !r.passed).length;
    
    return {
      summary: {
        total: results.length,
        passed,
        failed,
        passRate: (passed / results.length * 100).toFixed(2)
      },
      results
    };
  }
  
  getResults() {
    return Array.from(this.results.values());
  }
}
{% endraw %}
```

## Performance Analytics & Reporting

### Analytics Integration

```jsx
{% raw %}
// Performance analytics service
class PerformanceAnalytics {
  constructor(config = {}) {
    this.config = {
      apiEndpoint: '/api/analytics/performance',
      batchSize: 50,
      flushInterval: 30000,
      ...config
    };
    
    this.eventQueue = [];
    this.isFlushInProgress = false;
    
    this.startBatchProcessing();
  }
  
  track(event, data = {}) {
    const analyticsEvent = {
      event,
      data,
      timestamp: Date.now(),
      sessionId: this.getSessionId(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };
    
    this.eventQueue.push(analyticsEvent);
    
    // Flush immediately for critical events
    if (this.isCriticalEvent(event)) {
      this.flush();
    }
  }
  
  isCriticalEvent(event) {
    const criticalEvents = [
      'performance_budget_violation',
      'critical_render_time',
      'memory_leak_detected'
    ];
    
    return criticalEvents.includes(event);
  }
  
  async flush() {
    if (this.isFlushInProgress || this.eventQueue.length === 0) {
      return;
    }
    
    this.isFlushInProgress = true;
    const batch = this.eventQueue.splice(0, this.config.batchSize);
    
    try {
      await fetch(this.config.apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events: batch })
      });
    } catch (error) {
      console.error('Analytics flush failed:', error);
      this.eventQueue.unshift(...batch);
    } finally {
      this.isFlushInProgress = false;
    }
  }
  
  getSessionId() {
    let sessionId = sessionStorage.getItem('analyticsSessionId');
    if (!sessionId) {
      sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('analyticsSessionId', sessionId);
    }
    return sessionId;
  }
}

// Performance analytics hook
function usePerformanceAnalytics() {
  const analytics = useRef(null);
  
  useEffect(() => {
    analytics.current = new PerformanceAnalytics();
    
    return () => {
      analytics.current?.destroy();
    };
  }, []);
  
  const trackEvent = useCallback((event, data) => {
    analytics.current?.track(event, data);
  }, []);
  
  const trackComponentRender = useCallback((componentName, duration, phase) => {
    trackEvent('component_render', {
      component: componentName,
      duration,
      phase,
      isSlow: duration > 16
    });
  }, [trackEvent]);
  
  return {
    trackEvent,
    trackComponentRender
  };
}
{% endraw %}
```

## Summary

Performance monitoring and profiling are essential for maintaining optimal React application performance. Key takeaways:

### Monitoring Strategy:
1. **Implement comprehensive monitoring** covering React metrics, Core Web Vitals, and user interactions
2. **Set up performance budgets** with automated alerts
3. **Use real-time dashboards** for immediate insights
4. **Track performance trends** over time

### Key Metrics:
- **React Performance**: Component render times, re-render counts
- **Core Web Vitals**: LCP, FID, CLS scores
- **User Experience**: Interaction responsiveness, API response times
- **Resource Usage**: Bundle sizes, memory consumption

### Best Practices:
1. **Start monitoring early** in development
2. **Set realistic budgets** based on user needs
3. **Implement automated testing** for regressions
4. **Use analytics** for real-world insights
5. **Create actionable reports** for stakeholders

Performance monitoring ensures consistent, high-quality user experiences and helps identify optimization opportunities before they impact users.