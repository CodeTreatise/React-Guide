# API Performance Monitoring & Optimization

## Table of Contents
1. [Performance Monitoring Fundamentals](#performance-monitoring-fundamentals)
2. [Metrics Collection and Analysis](#metrics-collection-and-analysis)
3. [Request Performance Tracking](#request-performance-tracking)
4. [Error Monitoring and Alerting](#error-monitoring-and-alerting)
5. [Cache Performance Optimization](#cache-performance-optimization)
6. [Network Optimization Strategies](#network-optimization-strategies)
7. [Performance Budgets](#performance-budgets)
8. [Real User Monitoring (RUM)](#real-user-monitoring-rum)
9. [Performance Testing](#performance-testing)
10. [Monitoring Tools Integration](#monitoring-tools-integration)
11. [Performance Debugging](#performance-debugging)

## Performance Monitoring Fundamentals

### Core Performance Metrics

Understanding and tracking the right metrics is crucial for maintaining optimal API performance.

```typescript
// types/performance.ts
export interface APIPerformanceMetrics {
  // Request metrics
  requestCount: number;
  requestRate: number; // requests per second
  responseTime: {
    min: number;
    max: number;
    mean: number;
    median: number;
    p95: number;
    p99: number;
  };
  
  // Error metrics
  errorRate: number;
  errorCount: number;
  errorsByType: Record<string, number>;
  
  // Network metrics
  networkLatency: number;
  dnsTiming: number;
  tcpConnectTime: number;
  tlsHandshakeTime: number;
  
  // Cache metrics
  cacheHitRate: number;
  cacheMissRate: number;
  cacheSize: number;
  
  // Resource usage
  memoryUsage: number;
  cpuUsage: number;
  
  // Business metrics
  successfulTransactions: number;
  failedTransactions: number;
  userSatisfactionScore: number;
}

export interface PerformanceEntry {
  id: string;
  timestamp: number;
  url: string;
  method: string;
  status: number;
  duration: number;
  size: number;
  type: 'fetch' | 'xhr' | 'graphql' | 'websocket';
  userAgent: string;
  sessionId: string;
  userId?: string;
  traceId: string;
}

// Performance thresholds
export const PERFORMANCE_THRESHOLDS = {
  EXCELLENT: {
    responseTime: 100, // ms
    errorRate: 0.1 // %
  },
  GOOD: {
    responseTime: 300,
    errorRate: 1
  },
  FAIR: {
    responseTime: 1000,
    errorRate: 5
  },
  POOR: {
    responseTime: 3000,
    errorRate: 10
  }
} as const;

export type PerformanceGrade = keyof typeof PERFORMANCE_THRESHOLDS;

export const getPerformanceGrade = (
  responseTime: number,
  errorRate: number
): PerformanceGrade => {
  for (const [grade, threshold] of Object.entries(PERFORMANCE_THRESHOLDS)) {
    if (responseTime <= threshold.responseTime && errorRate <= threshold.errorRate) {
      return grade as PerformanceGrade;
    }
  }
  return 'POOR';
};
```

### Performance Monitor Class

```typescript
// utils/performanceMonitor.ts
export class APIPerformanceMonitor {
  private entries: PerformanceEntry[] = [];
  private observers: Map<string, (entry: PerformanceEntry) => void> = new Map();
  private sessionId: string;
  private userId?: string;
  private maxEntries: number;

  constructor(config: {
    maxEntries?: number;
    userId?: string;
    autoFlush?: boolean;
    flushInterval?: number;
  } = {}) {
    this.sessionId = this.generateSessionId();
    this.userId = config.userId;
    this.maxEntries = config.maxEntries || 1000;

    if (config.autoFlush) {
      setInterval(() => {
        this.flushEntries();
      }, config.flushInterval || 60000);
    }

    this.setupGlobalInterceptors();
  }

  recordEntry(entry: Omit<PerformanceEntry, 'id' | 'timestamp' | 'sessionId' | 'userId' | 'traceId' | 'userAgent'>): void {
    const fullEntry: PerformanceEntry = {
      ...entry,
      id: this.generateId(),
      timestamp: Date.now(),
      sessionId: this.sessionId,
      userId: this.userId,
      traceId: this.generateTraceId(),
      userAgent: navigator.userAgent
    };

    this.entries.push(fullEntry);

    // Maintain max entries limit
    if (this.entries.length > this.maxEntries) {
      this.entries.shift();
    }

    // Notify observers
    this.observers.forEach(callback => callback(fullEntry));

    // Auto-report critical performance issues
    this.checkCriticalThresholds(fullEntry);
  }

  getMetrics(timeWindow?: number): APIPerformanceMetrics {
    const now = Date.now();
    const entries = timeWindow 
      ? this.entries.filter(entry => now - entry.timestamp <= timeWindow)
      : this.entries;

    if (entries.length === 0) {
      return this.getEmptyMetrics();
    }

    const responseTimes = entries.map(entry => entry.duration);
    const errors = entries.filter(entry => entry.status >= 400);
    const successful = entries.filter(entry => entry.status < 400);

    return {
      requestCount: entries.length,
      requestRate: this.calculateRequestRate(entries, timeWindow),
      responseTime: this.calculateResponseTimeStats(responseTimes),
      errorRate: (errors.length / entries.length) * 100,
      errorCount: errors.length,
      errorsByType: this.groupErrorsByType(errors),
      networkLatency: this.calculateAverageNetworkLatency(entries),
      dnsTiming: 0, // Would be populated from Navigation Timing API
      tcpConnectTime: 0,
      tlsHandshakeTime: 0,
      cacheHitRate: 0, // Would be calculated from cache-specific metrics
      cacheMissRate: 0,
      cacheSize: 0,
      memoryUsage: this.getMemoryUsage(),
      cpuUsage: 0, // Not directly available in browser
      successfulTransactions: successful.length,
      failedTransactions: errors.length,
      userSatisfactionScore: this.calculateUserSatisfactionScore(entries)
    };
  }

  subscribe(id: string, callback: (entry: PerformanceEntry) => void): () => void {
    this.observers.set(id, callback);
    return () => this.observers.delete(id);
  }

  private setupGlobalInterceptors(): void {
    // Intercept fetch requests
    const originalFetch = window.fetch;
    window.fetch = async (...args: Parameters<typeof fetch>): Promise<Response> => {
      const startTime = performance.now();
      const url = typeof args[0] === 'string' ? args[0] : args[0].url;
      const method = args[1]?.method || 'GET';

      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();

        this.recordEntry({
          url,
          method,
          status: response.status,
          duration: endTime - startTime,
          size: parseInt(response.headers.get('content-length') || '0'),
          type: 'fetch'
        });

        return response;
      } catch (error) {
        const endTime = performance.now();
        
        this.recordEntry({
          url,
          method,
          status: 0, // Network error
          duration: endTime - startTime,
          size: 0,
          type: 'fetch'
        });

        throw error;
      }
    };

    // Intercept XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method: string, url: string | URL) {
      (this as any)._startTime = performance.now();
      (this as any)._method = method;
      (this as any)._url = url.toString();
      return originalXHROpen.apply(this, arguments as any);
    };

    XMLHttpRequest.prototype.send = function() {
      const xhr = this;
      const originalOnReadyStateChange = xhr.onreadystatechange;

      xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
          const endTime = performance.now();
          const startTime = (xhr as any)._startTime;

          if (startTime) {
            APIPerformanceMonitor.getInstance().recordEntry({
              url: (xhr as any)._url,
              method: (xhr as any)._method,
              status: xhr.status,
              duration: endTime - startTime,
              size: xhr.responseText?.length || 0,
              type: 'xhr'
            });
          }
        }

        if (originalOnReadyStateChange) {
          originalOnReadyStateChange.apply(xhr, arguments as any);
        }
      };

      return originalXHRSend.apply(this, arguments as any);
    };
  }

  private calculateResponseTimeStats(times: number[]) {
    if (times.length === 0) {
      return { min: 0, max: 0, mean: 0, median: 0, p95: 0, p99: 0 };
    }

    const sorted = [...times].sort((a, b) => a - b);
    const sum = times.reduce((acc, time) => acc + time, 0);

    return {
      min: Math.min(...times),
      max: Math.max(...times),
      mean: sum / times.length,
      median: this.percentile(sorted, 50),
      p95: this.percentile(sorted, 95),
      p99: this.percentile(sorted, 99)
    };
  }

  private percentile(sortedArray: number[], p: number): number {
    if (sortedArray.length === 0) return 0;
    const index = (p / 100) * (sortedArray.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index % 1;

    if (upper >= sortedArray.length) return sortedArray[sortedArray.length - 1];
    return sortedArray[lower] * (1 - weight) + sortedArray[upper] * weight;
  }

  private calculateRequestRate(entries: PerformanceEntry[], timeWindow?: number): number {
    if (!timeWindow || entries.length === 0) return 0;
    return (entries.length / timeWindow) * 1000; // requests per second
  }

  private groupErrorsByType(errors: PerformanceEntry[]): Record<string, number> {
    return errors.reduce((acc, error) => {
      const type = this.getErrorType(error.status);
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }

  private getErrorType(status: number): string {
    if (status === 0) return 'Network Error';
    if (status >= 400 && status < 500) return 'Client Error';
    if (status >= 500) return 'Server Error';
    return 'Unknown Error';
  }

  private calculateAverageNetworkLatency(entries: PerformanceEntry[]): number {
    // This would use Navigation Timing API for more accurate network timing
    return entries.reduce((acc, entry) => acc + entry.duration, 0) / entries.length;
  }

  private getMemoryUsage(): number {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return 0;
  }

  private calculateUserSatisfactionScore(entries: PerformanceEntry[]): number {
    // Apdex-like score: percentage of requests under acceptable threshold
    const acceptable = entries.filter(entry => entry.duration <= 1000).length;
    return (acceptable / entries.length) * 100;
  }

  private checkCriticalThresholds(entry: PerformanceEntry): void {
    // Alert on critical performance issues
    if (entry.duration > 5000) {
      console.warn('Critical response time detected:', entry);
      this.sendAlert('critical-response-time', entry);
    }

    if (entry.status >= 500) {
      console.error('Server error detected:', entry);
      this.sendAlert('server-error', entry);
    }
  }

  private sendAlert(type: string, entry: PerformanceEntry): void {
    // Implementation would send to monitoring service
    fetch('/api/alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, entry, timestamp: Date.now() })
    }).catch(console.error);
  }

  private flushEntries(): void {
    if (this.entries.length === 0) return;

    // Send entries to monitoring service
    fetch('/api/performance-metrics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: this.sessionId,
        userId: this.userId,
        entries: this.entries
      })
    }).catch(console.error);

    this.entries = [];
  }

  private generateSessionId(): string {
    return crypto.randomUUID();
  }

  private generateId(): string {
    return crypto.randomUUID();
  }

  private generateTraceId(): string {
    return crypto.randomUUID();
  }

  private getEmptyMetrics(): APIPerformanceMetrics {
    return {
      requestCount: 0,
      requestRate: 0,
      responseTime: { min: 0, max: 0, mean: 0, median: 0, p95: 0, p99: 0 },
      errorRate: 0,
      errorCount: 0,
      errorsByType: {},
      networkLatency: 0,
      dnsTiming: 0,
      tcpConnectTime: 0,
      tlsHandshakeTime: 0,
      cacheHitRate: 0,
      cacheMissRate: 0,
      cacheSize: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      successfulTransactions: 0,
      failedTransactions: 0,
      userSatisfactionScore: 0
    };
  }

  // Singleton pattern for global access
  private static instance: APIPerformanceMonitor;

  static getInstance(config?: ConstructorParameters<typeof APIPerformanceMonitor>[0]): APIPerformanceMonitor {
    if (!APIPerformanceMonitor.instance) {
      APIPerformanceMonitor.instance = new APIPerformanceMonitor(config);
    }
    return APIPerformanceMonitor.instance;
  }
}
```

## React Performance Monitoring Hooks

### usePerformanceMonitoring Hook

```typescript
// hooks/usePerformanceMonitoring.ts
import { useEffect, useState, useCallback, useRef } from 'react';
import { APIPerformanceMonitor, APIPerformanceMetrics, PerformanceEntry } from '../utils/performanceMonitor';

interface UsePerformanceMonitoringConfig {
  autoStart?: boolean;
  metricsInterval?: number;
  alertThresholds?: {
    responseTime?: number;
    errorRate?: number;
  };
}

export const usePerformanceMonitoring = (config: UsePerformanceMonitoringConfig = {}) => {
  const [metrics, setMetrics] = useState<APIPerformanceMetrics | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [alerts, setAlerts] = useState<Array<{ type: string; entry: PerformanceEntry; timestamp: number }>>([]);
  
  const monitorRef = useRef<APIPerformanceMonitor>();
  const intervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    monitorRef.current = APIPerformanceMonitor.getInstance();
    
    if (config.autoStart !== false) {
      startMonitoring();
    }

    return () => {
      stopMonitoring();
    };
  }, []);

  const startMonitoring = useCallback(() => {
    if (!monitorRef.current || isMonitoring) return;

    setIsMonitoring(true);

    // Subscribe to performance entries
    const unsubscribe = monitorRef.current.subscribe('react-hook', (entry) => {
      // Check alert thresholds
      if (config.alertThresholds) {
        const shouldAlert = 
          (config.alertThresholds.responseTime && entry.duration > config.alertThresholds.responseTime) ||
          (config.alertThresholds.errorRate && entry.status >= 400);

        if (shouldAlert) {
          setAlerts(prev => [
            ...prev,
            { type: 'threshold-exceeded', entry, timestamp: Date.now() }
          ].slice(-10)); // Keep last 10 alerts
        }
      }
    });

    // Update metrics periodically
    intervalRef.current = setInterval(() => {
      const currentMetrics = monitorRef.current?.getMetrics(config.metricsInterval || 60000);
      setMetrics(currentMetrics || null);
    }, 5000); // Update every 5 seconds

    return unsubscribe;
  }, [isMonitoring, config]);

  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = undefined;
    }
  }, []);

  const getMetrics = useCallback((timeWindow?: number) => {
    return monitorRef.current?.getMetrics(timeWindow) || null;
  }, []);

  const recordCustomMetric = useCallback((entry: Omit<PerformanceEntry, 'id' | 'timestamp' | 'sessionId' | 'userId' | 'traceId' | 'userAgent'>) => {
    monitorRef.current?.recordEntry(entry);
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  return {
    metrics,
    alerts,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    getMetrics,
    recordCustomMetric,
    clearAlerts
  };
};

// Hook for monitoring specific API calls
export const useAPICallMonitoring = () => {
  const { recordCustomMetric } = usePerformanceMonitoring();

  const monitoredFetch = useCallback(async (
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response> => {
    const startTime = performance.now();
    const url = typeof input === 'string' ? input : input.toString();
    const method = init?.method || 'GET';

    try {
      const response = await fetch(input, init);
      const endTime = performance.now();

      recordCustomMetric({
        url,
        method,
        status: response.status,
        duration: endTime - startTime,
        size: parseInt(response.headers.get('content-length') || '0'),
        type: 'fetch'
      });

      return response;
    } catch (error) {
      const endTime = performance.now();
      
      recordCustomMetric({
        url,
        method,
        status: 0,
        duration: endTime - startTime,
        size: 0,
        type: 'fetch'
      });

      throw error;
    }
  }, [recordCustomMetric]);

  return { monitoredFetch };
};
```

### Performance Dashboard Component

```typescript
// components/Performance/PerformanceDashboard.tsx
import React, { useEffect, useState } from 'react';
import { usePerformanceMonitoring } from '../../hooks/usePerformanceMonitoring';
import { PerformanceGrade, getPerformanceGrade, PERFORMANCE_THRESHOLDS } from '../../types/performance';

const PerformanceDashboard: React.FC = () => {
  const { 
    metrics, 
    alerts, 
    isMonitoring, 
    startMonitoring, 
    stopMonitoring, 
    clearAlerts 
  } = usePerformanceMonitoring({
    autoStart: true,
    metricsInterval: 60000, // 1 minute window
    alertThresholds: {
      responseTime: 2000,
      errorRate: 5
    }
  });

  const [selectedTimeWindow, setSelectedTimeWindow] = useState(60000); // 1 minute

  const performanceGrade = metrics 
    ? getPerformanceGrade(metrics.responseTime.mean, metrics.errorRate)
    : 'POOR';

  const getGradeColor = (grade: PerformanceGrade): string => {
    switch (grade) {
      case 'EXCELLENT': return '#22c55e';
      case 'GOOD': return '#84cc16';
      case 'FAIR': return '#f59e0b';
      case 'POOR': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="performance-dashboard">
      <div className="dashboard-header">
        <h2>API Performance Monitoring</h2>
        <div className="controls">
          <select 
            value={selectedTimeWindow} 
            onChange={(e) => setSelectedTimeWindow(Number(e.target.value))}
          >
            <option value={60000}>Last 1 minute</option>
            <option value={300000}>Last 5 minutes</option>
            <option value={900000}>Last 15 minutes</option>
            <option value={3600000}>Last 1 hour</option>
          </select>
          
          <button 
            onClick={isMonitoring ? stopMonitoring : startMonitoring}
            className={`monitor-toggle ${isMonitoring ? 'active' : ''}`}
          >
            {isMonitoring ? 'Stop' : 'Start'} Monitoring
          </button>
        </div>
      </div>

      {metrics && (
        <>
          <div className="performance-overview">
            <div className="grade-card">
              <h3>Overall Grade</h3>
              <div 
                className="grade-indicator"
                style={{ backgroundColor: getGradeColor(performanceGrade) }}
              >
                {performanceGrade}
              </div>
              <div className="grade-details">
                <p>Avg Response: {metrics.responseTime.mean.toFixed(2)}ms</p>
                <p>Error Rate: {metrics.errorRate.toFixed(2)}%</p>
              </div>
            </div>

            <div className="metrics-grid">
              <MetricCard
                title="Request Count"
                value={metrics.requestCount}
                unit="requests"
                trend={metrics.requestRate > 0 ? 'up' : 'stable'}
              />
              
              <MetricCard
                title="Request Rate"
                value={metrics.requestRate}
                unit="req/sec"
                decimals={2}
              />
              
              <MetricCard
                title="P95 Response Time"
                value={metrics.responseTime.p95}
                unit="ms"
                decimals={2}
                threshold={PERFORMANCE_THRESHOLDS.GOOD.responseTime}
              />
              
              <MetricCard
                title="Error Rate"
                value={metrics.errorRate}
                unit="%"
                decimals={2}
                threshold={PERFORMANCE_THRESHOLDS.GOOD.errorRate}
                isError={metrics.errorRate > PERFORMANCE_THRESHOLDS.FAIR.errorRate}
              />
            </div>
          </div>

          <div className="detailed-metrics">
            <div className="metric-section">
              <h3>Response Time Distribution</h3>
              <ResponseTimeChart metrics={metrics} />
            </div>

            <div className="metric-section">
              <h3>Error Breakdown</h3>
              <ErrorBreakdown errors={metrics.errorsByType} />
            </div>

            <div className="metric-section">
              <h3>Network Performance</h3>
              <NetworkMetrics metrics={metrics} />
            </div>
          </div>
        </>
      )}

      {alerts.length > 0 && (
        <div className="alerts-section">
          <div className="alerts-header">
            <h3>Performance Alerts ({alerts.length})</h3>
            <button onClick={clearAlerts}>Clear All</button>
          </div>
          <div className="alerts-list">
            {alerts.map((alert, index) => (
              <AlertItem key={index} alert={alert} />
            ))}
          </div>
        </div>
      )}

      {!isMonitoring && (
        <div className="monitoring-disabled">
          <p>Performance monitoring is disabled</p>
          <button onClick={startMonitoring}>Start Monitoring</button>
        </div>
      )}
    </div>
  );
};

// Supporting components
const MetricCard: React.FC<{
  title: string;
  value: number;
  unit: string;
  decimals?: number;
  threshold?: number;
  trend?: 'up' | 'down' | 'stable';
  isError?: boolean;
}> = ({ title, value, unit, decimals = 0, threshold, trend, isError }) => {
  const displayValue = value.toFixed(decimals);
  const isOverThreshold = threshold !== undefined && value > threshold;

  return (
    <div className={`metric-card ${isError ? 'error' : ''} ${isOverThreshold ? 'warning' : ''}`}>
      <h4>{title}</h4>
      <div className="metric-value">
        <span className="value">{displayValue}</span>
        <span className="unit">{unit}</span>
        {trend && <span className={`trend ${trend}`}>
          {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
        </span>}
      </div>
      {threshold && (
        <div className="threshold">
          Threshold: {threshold}{unit}
        </div>
      )}
    </div>
  );
};

const ResponseTimeChart: React.FC<{ metrics: APIPerformanceMetrics }> = ({ metrics }) => {
  const { responseTime } = metrics;
  
  return (
    <div className="response-time-chart">
      <div className="chart-bar">
        <span className="label">Min</span>
        <div className="bar" style={{ width: '20%' }}>
          {responseTime.min.toFixed(2)}ms
        </div>
      </div>
      <div className="chart-bar">
        <span className="label">Median</span>
        <div className="bar" style={{ width: '60%' }}>
          {responseTime.median.toFixed(2)}ms
        </div>
      </div>
      <div className="chart-bar">
        <span className="label">P95</span>
        <div className="bar" style={{ width: '80%' }}>
          {responseTime.p95.toFixed(2)}ms
        </div>
      </div>
      <div className="chart-bar">
        <span className="label">P99</span>
        <div className="bar" style={{ width: '90%' }}>
          {responseTime.p99.toFixed(2)}ms
        </div>
      </div>
      <div className="chart-bar">
        <span className="label">Max</span>
        <div className="bar" style={{ width: '100%' }}>
          {responseTime.max.toFixed(2)}ms
        </div>
      </div>
    </div>
  );
};

const ErrorBreakdown: React.FC<{ errors: Record<string, number> }> = ({ errors }) => {
  const totalErrors = Object.values(errors).reduce((sum, count) => sum + count, 0);

  if (totalErrors === 0) {
    return <div className="no-errors">No errors recorded</div>;
  }

  return (
    <div className="error-breakdown">
      {Object.entries(errors).map(([type, count]) => {
        const percentage = (count / totalErrors) * 100;
        return (
          <div key={type} className="error-item">
            <span className="error-type">{type}</span>
            <span className="error-count">{count}</span>
            <div className="error-bar">
              <div 
                className="error-fill" 
                style={{ width: `${percentage}%` }}
              />
            </div>
            <span className="error-percentage">{percentage.toFixed(1)}%</span>
          </div>
        );
      })}
    </div>
  );
};

const NetworkMetrics: React.FC<{ metrics: APIPerformanceMetrics }> = ({ metrics }) => {
  return (
    <div className="network-metrics">
      <div className="network-item">
        <span className="label">Average Latency:</span>
        <span className="value">{metrics.networkLatency.toFixed(2)}ms</span>
      </div>
      <div className="network-item">
        <span className="label">Memory Usage:</span>
        <span className="value">{(metrics.memoryUsage / 1024 / 1024).toFixed(2)}MB</span>
      </div>
      <div className="network-item">
        <span className="label">User Satisfaction:</span>
        <span className="value">{metrics.userSatisfactionScore.toFixed(1)}%</span>
      </div>
    </div>
  );
};

const AlertItem: React.FC<{ alert: { type: string; entry: PerformanceEntry; timestamp: number } }> = ({ alert }) => {
  return (
    <div className="alert-item">
      <div className="alert-type">{alert.type}</div>
      <div className="alert-details">
        <span>{alert.entry.method} {alert.entry.url}</span>
        <span>{alert.entry.duration.toFixed(2)}ms</span>
        <span>Status: {alert.entry.status}</span>
      </div>
      <div className="alert-time">
        {new Date(alert.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
};

export default PerformanceDashboard;
```

## Advanced Performance Analysis

### Performance Budget Implementation

```typescript
// utils/performanceBudget.ts
export interface PerformanceBudget {
  id: string;
  name: string;
  rules: PerformanceBudgetRule[];
  alerts: PerformanceBudgetAlert[];
  active: boolean;
}

export interface PerformanceBudgetRule {
  metric: keyof APIPerformanceMetrics | string;
  operator: 'lt' | 'lte' | 'gt' | 'gte' | 'eq' | 'neq';
  threshold: number;
  severity: 'info' | 'warning' | 'error' | 'critical';
  description: string;
}

export interface PerformanceBudgetAlert {
  rule: PerformanceBudgetRule;
  value: number;
  timestamp: number;
  resolved: boolean;
}

export class PerformanceBudgetManager {
  private budgets: Map<string, PerformanceBudget> = new Map();
  private alertCallbacks: Array<(alert: PerformanceBudgetAlert) => void> = [];

  addBudget(budget: PerformanceBudget): void {
    this.budgets.set(budget.id, budget);
  }

  removeBudget(budgetId: string): void {
    this.budgets.delete(budgetId);
  }

  checkBudgets(metrics: APIPerformanceMetrics): PerformanceBudgetAlert[] {
    const alerts: PerformanceBudgetAlert[] = [];

    this.budgets.forEach(budget => {
      if (!budget.active) return;

      budget.rules.forEach(rule => {
        const value = this.getMetricValue(metrics, rule.metric);
        const violation = this.checkRule(rule, value);

        if (violation) {
          const alert: PerformanceBudgetAlert = {
            rule,
            value,
            timestamp: Date.now(),
            resolved: false
          };

          alerts.push(alert);
          this.notifyAlert(alert);
        }
      });
    });

    return alerts;
  }

  private getMetricValue(metrics: APIPerformanceMetrics, metricPath: string): number {
    // Handle nested properties like 'responseTime.mean'
    const path = metricPath.split('.');
    let value: any = metrics;

    for (const key of path) {
      value = value?.[key];
      if (value === undefined) return 0;
    }

    return typeof value === 'number' ? value : 0;
  }

  private checkRule(rule: PerformanceBudgetRule, value: number): boolean {
    switch (rule.operator) {
      case 'lt': return value < rule.threshold;
      case 'lte': return value <= rule.threshold;
      case 'gt': return value > rule.threshold;
      case 'gte': return value >= rule.threshold;
      case 'eq': return value === rule.threshold;
      case 'neq': return value !== rule.threshold;
      default: return false;
    }
  }

  private notifyAlert(alert: PerformanceBudgetAlert): void {
    this.alertCallbacks.forEach(callback => callback(alert));
  }

  onAlert(callback: (alert: PerformanceBudgetAlert) => void): () => void {
    this.alertCallbacks.push(callback);
    return () => {
      const index = this.alertCallbacks.indexOf(callback);
      if (index > -1) {
        this.alertCallbacks.splice(index, 1);
      }
    };
  }

  // Predefined budget templates
  static createWebVitalsBudget(): PerformanceBudget {
    return {
      id: 'web-vitals',
      name: 'Core Web Vitals Budget',
      active: true,
      alerts: [],
      rules: [
        {
          metric: 'responseTime.p95',
          operator: 'lt',
          threshold: 2500, // LCP threshold
          severity: 'warning',
          description: 'P95 response time should be under 2.5s for good LCP'
        },
        {
          metric: 'responseTime.p95',
          operator: 'lt',
          threshold: 4000, // LCP poor threshold
          severity: 'critical',
          description: 'P95 response time exceeds poor LCP threshold'
        },
        {
          metric: 'errorRate',
          operator: 'lt',
          threshold: 5,
          severity: 'warning',
          description: 'Error rate should be below 5%'
        },
        {
          metric: 'errorRate',
          operator: 'lt',
          threshold: 10,
          severity: 'critical',
          description: 'Error rate is critically high'
        }
      ]
    };
  }

  static createAPIPerformanceBudget(): PerformanceBudget {
    return {
      id: 'api-performance',
      name: 'API Performance Budget',
      active: true,
      alerts: [],
      rules: [
        {
          metric: 'responseTime.mean',
          operator: 'lt',
          threshold: 300,
          severity: 'info',
          description: 'Mean response time should be under 300ms'
        },
        {
          metric: 'responseTime.p99',
          operator: 'lt',
          threshold: 1000,
          severity: 'warning',
          description: 'P99 response time should be under 1s'
        },
        {
          metric: 'requestRate',
          operator: 'gt',
          threshold: 100,
          severity: 'info',
          description: 'Request rate indicates high traffic'
        }
      ]
    };
  }
}
```

### Real User Monitoring (RUM)

```typescript
// utils/rumCollector.ts
export interface RUMData {
  sessionId: string;
  userId?: string;
  page: string;
  userAgent: string;
  connectionType: string;
  deviceType: 'mobile' | 'tablet' | 'desktop';
  geolocation?: {
    country: string;
    region: string;
    city: string;
  };
  performanceEntries: PerformanceEntry[];
  vitals: {
    fcp?: number; // First Contentful Paint
    lcp?: number; // Largest Contentful Paint
    fid?: number; // First Input Delay
    cls?: number; // Cumulative Layout Shift
    ttfb?: number; // Time to First Byte
  };
  customMetrics: Record<string, number>;
  errors: Array<{
    message: string;
    stack: string;
    timestamp: number;
    url: string;
  }>;
}

export class RUMCollector {
  private data: Partial<RUMData> = {};
  private observer: PerformanceObserver | null = null;
  private sendInterval: NodeJS.Timeout | null = null;

  constructor(private config: {
    endpoint: string;
    sessionId: string;
    userId?: string;
    sendInterval?: number;
    maxBatchSize?: number;
  }) {
    this.data = {
      sessionId: config.sessionId,
      userId: config.userId,
      page: window.location.pathname,
      userAgent: navigator.userAgent,
      connectionType: this.getConnectionType(),
      deviceType: this.getDeviceType(),
      performanceEntries: [],
      vitals: {},
      customMetrics: {},
      errors: []
    };

    this.setupPerformanceObserver();
    this.collectWebVitals();
    this.setupErrorTracking();
    this.startBatchSending();
  }

  private setupPerformanceObserver(): void {
    if ('PerformanceObserver' in window) {
      this.observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === 'navigation' || entry.entryType === 'resource') {
            this.data.performanceEntries?.push({
              id: crypto.randomUUID(),
              timestamp: entry.startTime,
              url: (entry as any).name || window.location.href,
              method: 'GET',
              status: 200, // Default for successful loads
              duration: entry.duration,
              size: (entry as any).transferSize || 0,
              type: entry.entryType as any,
              userAgent: navigator.userAgent,
              sessionId: this.config.sessionId,
              traceId: crypto.randomUUID()
            });
          }
        });
      });

      this.observer.observe({ entryTypes: ['navigation', 'resource', 'measure'] });
    }
  }

  private collectWebVitals(): void {
    // First Contentful Paint
    if ('PerformanceObserver' in window) {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
        if (fcpEntry) {
          this.data.vitals!.fcp = fcpEntry.startTime;
        }
      }).observe({ entryTypes: ['paint'] });

      // Largest Contentful Paint
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.data.vitals!.lcp = lastEntry.startTime;
      }).observe({ entryTypes: ['largest-contentful-paint'] });

      // First Input Delay
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          this.data.vitals!.fid = (entry as any).processingStart - entry.startTime;
        });
      }).observe({ entryTypes: ['first-input'] });

      // Cumulative Layout Shift
      let clsValue = 0;
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
            this.data.vitals!.cls = clsValue;
          }
        });
      }).observe({ entryTypes: ['layout-shift'] });
    }

    // Time to First Byte
    const navigationEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigationEntry) {
      this.data.vitals!.ttfb = navigationEntry.responseStart - navigationEntry.requestStart;
    }
  }

  private setupErrorTracking(): void {
    window.addEventListener('error', (event) => {
      this.data.errors?.push({
        message: event.error?.message || event.message,
        stack: event.error?.stack || '',
        timestamp: Date.now(),
        url: event.filename || window.location.href
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.data.errors?.push({
        message: event.reason?.message || 'Unhandled Promise Rejection',
        stack: event.reason?.stack || '',
        timestamp: Date.now(),
        url: window.location.href
      });
    });
  }

  private getConnectionType(): string {
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
    return connection?.effectiveType || 'unknown';
  }

  private getDeviceType(): 'mobile' | 'tablet' | 'desktop' {
    const userAgent = navigator.userAgent;
    if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
      return 'tablet';
    }
    if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\sce|palm|smartphone|iemobile/i.test(userAgent)) {
      return 'mobile';
    }
    return 'desktop';
  }

  addCustomMetric(name: string, value: number): void {
    this.data.customMetrics![name] = value;
  }

  private startBatchSending(): void {
    const interval = this.config.sendInterval || 30000; // 30 seconds
    
    this.sendInterval = setInterval(() => {
      this.sendData();
    }, interval);

    // Send data on page unload
    window.addEventListener('beforeunload', () => {
      this.sendData(true);
    });
  }

  private sendData(synchronous = false): void {
    if (!this.data.performanceEntries?.length && !this.data.errors?.length) {
      return;
    }

    const payload = { ...this.data };

    if (synchronous && 'sendBeacon' in navigator) {
      navigator.sendBeacon(this.config.endpoint, JSON.stringify(payload));
    } else {
      fetch(this.config.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: synchronous
      }).catch(console.error);
    }

    // Clear sent data
    this.data.performanceEntries = [];
    this.data.errors = [];
  }

  destroy(): void {
    if (this.observer) {
      this.observer.disconnect();
    }
    if (this.sendInterval) {
      clearInterval(this.sendInterval);
    }
    this.sendData(true); // Send remaining data
  }
}

// React hook for RUM integration
export const useRUM = (config: {
  endpoint: string;
  userId?: string;
  customMetrics?: Record<string, number>;
}) => {
  const rumRef = useRef<RUMCollector>();

  useEffect(() => {
    rumRef.current = new RUMCollector({
      ...config,
      sessionId: crypto.randomUUID()
    });

    // Add custom metrics if provided
    if (config.customMetrics) {
      Object.entries(config.customMetrics).forEach(([name, value]) => {
        rumRef.current?.addCustomMetric(name, value);
      });
    }

    return () => {
      rumRef.current?.destroy();
    };
  }, []);

  const addCustomMetric = useCallback((name: string, value: number) => {
    rumRef.current?.addCustomMetric(name, value);
  }, []);

  return { addCustomMetric };
};
```

## Performance Testing

### Load Testing Utilities

```typescript
// utils/loadTesting.ts
export interface LoadTestConfig {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  concurrent: number;
  duration: number; // milliseconds
  rampUp?: number; // milliseconds to reach full load
}

export interface LoadTestResult {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  minResponseTime: number;
  maxResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  requestsPerSecond: number;
  errorRate: number;
  errors: Array<{ status: number; message: string; count: number }>;
  timeline: Array<{ timestamp: number; responseTime: number; status: number }>;
}

export class LoadTester {
  async runTest(config: LoadTestConfig): Promise<LoadTestResult> {
    const results: Array<{ timestamp: number; responseTime: number; status: number; error?: string }> = [];
    const startTime = Date.now();
    const endTime = startTime + config.duration;

    // Calculate ramp-up
    const rampUpDuration = config.rampUp || 0;
    const rampUpStep = rampUpDuration / config.concurrent;

    const promises: Promise<void>[] = [];

    for (let i = 0; i < config.concurrent; i++) {
      const delay = rampUpDuration > 0 ? i * rampUpStep : 0;
      
      promises.push(
        this.runWorker(config, startTime + delay, endTime, results)
      );
    }

    await Promise.all(promises);

    return this.analyzeResults(results, config.duration);
  }

  private async runWorker(
    config: LoadTestConfig,
    startAfter: number,
    endBefore: number,
    results: Array<{ timestamp: number; responseTime: number; status: number; error?: string }>
  ): Promise<void> {
    // Wait for ramp-up delay
    const now = Date.now();
    if (startAfter > now) {
      await new Promise(resolve => setTimeout(resolve, startAfter - now));
    }

    while (Date.now() < endBefore) {
      const requestStart = Date.now();
      
      try {
        const response = await fetch(config.url, {
          method: config.method,
          headers: config.headers,
          body: config.body ? JSON.stringify(config.body) : undefined
        });

        const requestEnd = Date.now();
        
        results.push({
          timestamp: requestStart,
          responseTime: requestEnd - requestStart,
          status: response.status
        });

      } catch (error) {
        const requestEnd = Date.now();
        
        results.push({
          timestamp: requestStart,
          responseTime: requestEnd - requestStart,
          status: 0,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }

      // Small delay to prevent overwhelming the browser
      await new Promise(resolve => setTimeout(resolve, 1));
    }
  }

  private analyzeResults(
    results: Array<{ timestamp: number; responseTime: number; status: number; error?: string }>,
    duration: number
  ): LoadTestResult {
    const responseTimes = results.map(r => r.responseTime);
    const successful = results.filter(r => r.status >= 200 && r.status < 400);
    const failed = results.filter(r => r.status === 0 || r.status >= 400);

    // Group errors
    const errorGroups = failed.reduce((acc, result) => {
      const key = `${result.status}:${result.error || 'HTTP Error'}`;
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const errors = Object.entries(errorGroups).map(([key, count]) => {
      const [status, message] = key.split(':');
      return { status: parseInt(status), message, count };
    });

    return {
      totalRequests: results.length,
      successfulRequests: successful.length,
      failedRequests: failed.length,
      averageResponseTime: responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length,
      minResponseTime: Math.min(...responseTimes),
      maxResponseTime: Math.max(...responseTimes),
      p95ResponseTime: this.percentile(responseTimes.sort((a, b) => a - b), 95),
      p99ResponseTime: this.percentile(responseTimes.sort((a, b) => a - b), 99),
      requestsPerSecond: (results.length / duration) * 1000,
      errorRate: (failed.length / results.length) * 100,
      errors,
      timeline: results.map(r => ({
        timestamp: r.timestamp,
        responseTime: r.responseTime,
        status: r.status
      }))
    };
  }

  private percentile(sortedArray: number[], p: number): number {
    if (sortedArray.length === 0) return 0;
    const index = (p / 100) * (sortedArray.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index % 1;

    if (upper >= sortedArray.length) return sortedArray[sortedArray.length - 1];
    return sortedArray[lower] * (1 - weight) + sortedArray[upper] * weight;
  }
}

// React component for load testing
export const LoadTestRunner: React.FC = () => {
  const [config, setConfig] = useState<LoadTestConfig>({
    url: '/api/test',
    method: 'GET',
    concurrent: 10,
    duration: 30000,
    rampUp: 5000
  });
  
  const [result, setResult] = useState<LoadTestResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const runTest = async () => {
    setIsRunning(true);
    setResult(null);
    
    try {
      const tester = new LoadTester();
      const testResult = await tester.runTest(config);
      setResult(testResult);
    } catch (error) {
      console.error('Load test failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="load-test-runner">
      <h3>Load Test Configuration</h3>
      
      <div className="config-form">
        <label>
          URL:
          <input
            type="url"
            value={config.url}
            onChange={(e) => setConfig({ ...config, url: e.target.value })}
          />
        </label>
        
        <label>
          Concurrent Users:
          <input
            type="number"
            value={config.concurrent}
            onChange={(e) => setConfig({ ...config, concurrent: parseInt(e.target.value) })}
          />
        </label>
        
        <label>
          Duration (seconds):
          <input
            type="number"
            value={config.duration / 1000}
            onChange={(e) => setConfig({ ...config, duration: parseInt(e.target.value) * 1000 })}
          />
        </label>
        
        <button onClick={runTest} disabled={isRunning}>
          {isRunning ? 'Running Test...' : 'Run Load Test'}
        </button>
      </div>

      {result && (
        <div className="test-results">
          <h3>Test Results</h3>
          
          <div className="results-grid">
            <div className="result-item">
              <span className="label">Total Requests:</span>
              <span className="value">{result.totalRequests}</span>
            </div>
            
            <div className="result-item">
              <span className="label">Success Rate:</span>
              <span className="value">{((result.successfulRequests / result.totalRequests) * 100).toFixed(2)}%</span>
            </div>
            
            <div className="result-item">
              <span className="label">Avg Response Time:</span>
              <span className="value">{result.averageResponseTime.toFixed(2)}ms</span>
            </div>
            
            <div className="result-item">
              <span className="label">P95 Response Time:</span>
              <span className="value">{result.p95ResponseTime.toFixed(2)}ms</span>
            </div>
            
            <div className="result-item">
              <span className="label">Requests/Second:</span>
              <span className="value">{result.requestsPerSecond.toFixed(2)}</span>
            </div>
            
            <div className="result-item">
              <span className="label">Error Rate:</span>
              <span className="value">{result.errorRate.toFixed(2)}%</span>
            </div>
          </div>

          {result.errors.length > 0 && (
            <div className="error-summary">
              <h4>Errors</h4>
              {result.errors.map((error, index) => (
                <div key={index} className="error-item">
                  Status {error.status}: {error.message} ({error.count} times)
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

This comprehensive guide covers API performance monitoring and optimization in React applications, providing tools and techniques for measuring, analyzing, and improving API performance in production environments.
