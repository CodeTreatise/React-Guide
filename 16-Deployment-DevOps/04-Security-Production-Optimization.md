# Security & Production Optimization

## Table of Contents
- [Application Security](#application-security)
- [Infrastructure Security](#infrastructure-security)
- [Performance Optimization](#performance-optimization)
- [Bundle Optimization](#bundle-optimization)
- [Caching Strategies](#caching-strategies)
- [CDN & Edge Computing](#cdn--edge-computing)
- [Production Hardening](#production-hardening)
- [Security Monitoring](#security-monitoring)
- [Compliance & Auditing](#compliance--auditing)
- [Disaster Recovery](#disaster-recovery)

## Application Security

### Content Security Policy (CSP)

```typescript
// utils/security-headers.ts
export const generateCSPHeader = (nonce?: string): string => {
  const directives = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://connect.facebook.net",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https: blob:",
    "connect-src 'self' https://api.example.com wss://api.example.com",
    "media-src 'self' https://media.example.com",
    "object-src 'none'",
    "base-uri 'self'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "upgrade-insecure-requests"
  ];

  if (nonce) {
    directives[1] = `script-src 'self' 'nonce-${nonce}' https://www.googletagmanager.com`;
  }

  return directives.join('; ');
};

// Express middleware for security headers
export const securityHeadersMiddleware = (req: any, res: any, next: any) => {
  const nonce = crypto.randomBytes(16).toString('base64');
  
  // Content Security Policy
  res.setHeader('Content-Security-Policy', generateCSPHeader(nonce));
  
  // Additional security headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  
  // HSTS (only for HTTPS)
  if (req.secure) {
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
  }

  res.locals.nonce = nonce;
  next();
};
```

### Input Validation & Sanitization

```typescript
// utils/input-validation.ts
import DOMPurify from 'dompurify';
import { z } from 'zod';

// Validation schemas
export const userRegistrationSchema = z.object({
  email: z.string().email().max(254),
  password: z.string().min(8).max(128).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/),
  firstName: z.string().min(1).max(50).regex(/^[a-zA-Z\s-']+$/),
  lastName: z.string().min(1).max(50).regex(/^[a-zA-Z\s-']+$/),
  phoneNumber: z.string().optional().refine(
    (val) => !val || /^\+?[1-9]\d{1,14}$/.test(val),
    'Invalid phone number'
  )
});

export const searchQuerySchema = z.object({
  query: z.string().min(1).max(100),
  category: z.enum(['all', 'products', 'articles', 'users']).default('all'),
  page: z.number().min(1).max(1000).default(1),
  limit: z.number().min(1).max(100).default(20)
});

// Input sanitization
export class InputSanitizer {
  static sanitizeHTML(input: string): string {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
      ALLOWED_ATTR: ['href'],
      ALLOW_DATA_ATTR: false
    });
  }

  static sanitizeText(input: string): string {
    return input
      .replace(/[<>]/g, '') // Remove potential HTML tags
      .replace(/javascript:/gi, '') // Remove javascript: URLs
      .replace(/on\w+=/gi, '') // Remove event handlers
      .trim();
  }

  static sanitizeSQL(input: string): string {
    return input
      .replace(/['";\\]/g, '') // Remove SQL injection characters
      .replace(/(--)|(\/\*)|(\*\/)/g, '') // Remove SQL comments
      .trim();
  }

  static sanitizeFilename(filename: string): string {
    return filename
      .replace(/[^a-zA-Z0-9.-]/g, '_') // Replace special chars with underscore
      .replace(/\.{2,}/g, '.') // Replace multiple dots
      .replace(/^\.+|\.+$/g, '') // Remove leading/trailing dots
      .substring(0, 255); // Limit length
  }
}

// React hook for form validation
export const useFormValidation = <T>(schema: z.ZodSchema<T>) => {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (data: any): data is T => {
    try {
      schema.parse(data);
      setErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        error.errors.forEach((err) => {
          const path = err.path.join('.');
          newErrors[path] = err.message;
        });
        setErrors(newErrors);
      }
      return false;
    }
  };

  return { validate, errors };
};
```

### Authentication & Authorization

```typescript
// utils/auth-security.ts
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { rateLimit } from 'express-rate-limit';

// Password security
export class PasswordSecurity {
  private static readonly SALT_ROUNDS = 12;
  private static readonly MIN_ENTROPY = 30;

  static async hash(password: string): Promise<string> {
    return bcrypt.hash(password, this.SALT_ROUNDS);
  }

  static async verify(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  static calculateEntropy(password: string): number {
    const charset = {
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      numbers: /\d/.test(password),
      symbols: /[^a-zA-Z0-9]/.test(password)
    };

    let charsetSize = 0;
    if (charset.lowercase) charsetSize += 26;
    if (charset.uppercase) charsetSize += 26;
    if (charset.numbers) charsetSize += 10;
    if (charset.symbols) charsetSize += 32;

    return Math.log2(Math.pow(charsetSize, password.length));
  }

  static isPasswordSecure(password: string): boolean {
    return this.calculateEntropy(password) >= this.MIN_ENTROPY;
  }
}

// JWT Security
export class JWTSecurity {
  private static readonly SECRET_KEY = process.env.JWT_SECRET!;
  private static readonly REFRESH_SECRET = process.env.JWT_REFRESH_SECRET!;
  private static readonly ACCESS_TOKEN_EXPIRY = '15m';
  private static readonly REFRESH_TOKEN_EXPIRY = '7d';

  static generateTokens(payload: any) {
    const accessToken = jwt.sign(payload, this.SECRET_KEY, {
      expiresIn: this.ACCESS_TOKEN_EXPIRY,
      algorithm: 'HS256',
      issuer: 'myapp.com',
      audience: 'myapp-users'
    });

    const refreshToken = jwt.sign(payload, this.REFRESH_SECRET, {
      expiresIn: this.REFRESH_TOKEN_EXPIRY,
      algorithm: 'HS256',
      issuer: 'myapp.com',
      audience: 'myapp-users'
    });

    return { accessToken, refreshToken };
  }

  static verifyAccessToken(token: string) {
    return jwt.verify(token, this.SECRET_KEY, {
      algorithms: ['HS256'],
      issuer: 'myapp.com',
      audience: 'myapp-users'
    });
  }

  static verifyRefreshToken(token: string) {
    return jwt.verify(token, this.REFRESH_SECRET, {
      algorithms: ['HS256'],
      issuer: 'myapp.com',
      audience: 'myapp-users'
    });
  }
}

// Rate limiting
export const authRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: 'Too many authentication attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      error: 'Rate limit exceeded',
      retryAfter: Math.round(req.rateLimit.resetTime! / 1000)
    });
  }
});

export const apiRateLimit = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many API requests, please try again later'
});
```

### OWASP Security Implementation

```typescript
// utils/owasp-security.ts
import helmet from 'helmet';
import cors from 'cors';

// OWASP Top 10 protection
export const owaspMiddleware = [
  // A1: Injection
  (req: any, res: any, next: any) => {
    // SQL injection protection (parameterized queries)
    // XSS protection (input validation & output encoding)
    next();
  },

  // A2: Broken Authentication
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    }
  }),

  // A3: Sensitive Data Exposure
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true,
    optionsSuccessStatus: 200
  }),

  // A4: XML External Entities (XXE)
  // Disable XML parsing or use secure XML parsers

  // A5: Broken Access Control
  (req: any, res: any, next: any) => {
    // Implement proper RBAC
    next();
  },

  // A6: Security Misconfiguration
  (req: any, res: any, next: any) => {
    // Remove X-Powered-By header
    res.removeHeader('X-Powered-By');
    next();
  },

  // A7: Cross-Site Scripting (XSS)
  // Handled by CSP and input validation

  // A8: Insecure Deserialization
  (req: any, res: any, next: any) => {
    // Validate serialized data
    next();
  },

  // A9: Using Components with Known Vulnerabilities
  // Use npm audit and Snyk

  // A10: Insufficient Logging & Monitoring
  // Implemented in logging middleware
];

// Secure session configuration
export const sessionConfig = {
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 1000 * 60 * 60 * 24, // 24 hours
    sameSite: 'strict' as const
  },
  name: 'sessionId' // Don't use default session name
};
```

## Infrastructure Security

### Kubernetes Security Policies

```yaml
# k8s/security/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: react-app-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  runAsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: react-app-netpol
spec:
  podSelector:
    matchLabels:
      app: react-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-system
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: api-system
    ports:
    - protocol: TCP
      port: 8080
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: react-app-sa
automountServiceAccountToken: false
```

### Secrets Management

```yaml
# k8s/security/sealed-secret.yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: react-app-secrets
  namespace: production
spec:
  encryptedData:
    api-key: AgAh8F7...encrypted-data...
    database-url: AgBx9K2...encrypted-data...
    jwt-secret: AgCy5M8...encrypted-data...
  template:
    metadata:
      name: react-app-secrets
      namespace: production
    type: Opaque

---
# External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "react-app"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: react-app-external-secret
spec:
  refreshInterval: 15s
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: react-app-secrets
    creationPolicy: Owner
  data:
  - secretKey: api-key
    remoteRef:
      key: react-app
      property: api-key
```

### Security Scanning

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0' # Weekly scan

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run npm audit
      run: npm audit --audit-level high
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high

  sast-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run CodeQL Analysis
      uses: github/codeql-action/init@v2
      with:
        languages: javascript
    
    - uses: github/codeql-action/analyze@v2

  container-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t react-app:${{ github.sha }} .
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'react-app:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  license-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Check licenses
      uses: fossa-contrib/fossa-action@v1
      with:
        api-key: ${{ secrets.FOSSA_API_KEY }}
```

## Performance Optimization

### Advanced Bundle Optimization

```javascript
// webpack.config.prod.js
const path = require('path');
const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  mode: 'production',
  entry: {
    main: './src/index.tsx',
    vendor: ['react', 'react-dom']
  },
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: 'static/js/[name].[contenthash:8].js',
    chunkFilename: 'static/js/[name].[contenthash:8].chunk.js',
    publicPath: '/',
    clean: true
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          parse: { ecma: 8 },
          compress: {
            ecma: 5,
            warnings: false,
            comparisons: false,
            inline: 2,
            drop_console: true,
            drop_debugger: true,
            pure_funcs: ['console.log', 'console.info', 'console.debug']
          },
          mangle: { safari10: true },
          output: { ecma: 5, comments: false, ascii_only: true }
        },
        parallel: true
      })
    ],
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
          reuseExistingChunk: true
        },
        common: {
          name: 'common',
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true
        },
        styles: {
          name: 'styles',
          test: /\.css$/,
          chunks: 'all',
          enforce: true
        }
      }
    },
    runtimeChunk: {
      name: entrypoint => `runtime-${entrypoint.name}`
    }
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    }),
    new CompressionPlugin({
      filename: '[path][base].gz',
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8
    }),
    new CompressionPlugin({
      filename: '[path][base].br',
      algorithm: 'brotliCompress',
      test: /\.(js|css|html|svg)$/,
      compressionOptions: { level: 11 },
      threshold: 8192,
      minRatio: 0.8
    }),
    process.env.ANALYZE === 'true' && new BundleAnalyzerPlugin()
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'react-dom': process.env.NODE_ENV === 'production' ? 'react-dom/profiling' : 'react-dom'
    }
  }
};
```

### Tree Shaking & Dead Code Elimination

```typescript
// utils/performance-optimization.ts

// Selective imports to enable tree shaking
import { debounce } from 'lodash-es/debounce';
import { format } from 'date-fns/format';
import { Button } from '@mui/material/Button';

// Dynamic imports for code splitting
export const LazyComponent = React.lazy(() => 
  import(/* webpackChunkName: "lazy-component" */ './LazyComponent')
);

export const LazyRouteComponent = React.lazy(() => 
  import(/* webpackChunkName: "route-[request]" */ './routes/[request]')
);

// Bundle size monitoring
export const trackBundleSize = () => {
  if (process.env.NODE_ENV === 'production') {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name.includes('.js') && entry.transferSize) {
          console.log(`Bundle: ${entry.name}, Size: ${entry.transferSize} bytes`);
          
          // Send to analytics
          if (typeof gtag !== 'undefined') {
            gtag('event', 'bundle_size', {
              bundle_name: entry.name,
              bundle_size: entry.transferSize
            });
          }
        }
      }
    });
    
    observer.observe({ entryTypes: ['resource'] });
  }
};

// Preload critical resources
export const preloadCriticalResources = () => {
  const criticalResources = [
    '/static/css/main.css',
    '/static/js/vendor.js',
    '/api/user/profile'
  ];

  criticalResources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    
    if (resource.endsWith('.css')) {
      link.as = 'style';
    } else if (resource.endsWith('.js')) {
      link.as = 'script';
    } else {
      link.as = 'fetch';
      link.crossOrigin = 'anonymous';
    }
    
    link.href = resource;
    document.head.appendChild(link);
  });
};
```

### React Performance Optimizations

```typescript
// components/OptimizedComponent.tsx
import React, { memo, useMemo, useCallback, startTransition } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

interface OptimizedListProps {
  items: Array<{ id: string; name: string; value: number }>;
  onItemClick: (id: string) => void;
  filterText: string;
}

const OptimizedList = memo<OptimizedListProps>(({ items, onItemClick, filterText }) => {
  // Memoize filtered items
  const filteredItems = useMemo(() => {
    return items.filter(item => 
      item.name.toLowerCase().includes(filterText.toLowerCase())
    );
  }, [items, filterText]);

  // Memoize expensive calculations
  const stats = useMemo(() => {
    return filteredItems.reduce((acc, item) => ({
      total: acc.total + item.value,
      average: (acc.total + item.value) / (acc.count + 1),
      count: acc.count + 1
    }), { total: 0, average: 0, count: 0 });
  }, [filteredItems]);

  // Memoize callbacks
  const handleItemClick = useCallback((id: string) => {
    startTransition(() => {
      onItemClick(id);
    });
  }, [onItemClick]);

  // Virtual scrolling for large lists
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: filteredItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 10
  });

  return (
    <div>
      <div>
        Total: {stats.total}, Average: {stats.average.toFixed(2)}, Count: {stats.count}
      </div>
      
      <div
        ref={parentRef}
        style={{ height: '400px', overflow: 'auto' }}
      >
        <div
          style={{
            height: `${virtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative'
          }}
        >
          {virtualizer.getVirtualItems().map((virtualItem) => {
            const item = filteredItems[virtualItem.index];
            return (
              <div
                key={item.id}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: `${virtualItem.size}px`,
                  transform: `translateY(${virtualItem.start}px)`
                }}
                onClick={() => handleItemClick(item.id)}
              >
                {item.name} - {item.value}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
});

OptimizedList.displayName = 'OptimizedList';

export default OptimizedList;
```

## Caching Strategies

### Multi-Level Caching Implementation

```typescript
// utils/cache-manager.ts
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  version: string;
}

class CacheManager {
  private memoryCache = new Map<string, CacheEntry<any>>();
  private readonly maxMemoryCacheSize = 100;
  private readonly defaultTTL = 5 * 60 * 1000; // 5 minutes

  // Memory cache
  setMemoryCache<T>(key: string, data: T, ttl = this.defaultTTL): void {
    if (this.memoryCache.size >= this.maxMemoryCacheSize) {
      const firstKey = this.memoryCache.keys().next().value;
      this.memoryCache.delete(firstKey);
    }

    this.memoryCache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
      version: this.getCacheVersion()
    });
  }

  getMemoryCache<T>(key: string): T | null {
    const entry = this.memoryCache.get(key);
    
    if (!entry) return null;
    
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.memoryCache.delete(key);
      return null;
    }

    if (entry.version !== this.getCacheVersion()) {
      this.memoryCache.delete(key);
      return null;
    }

    return entry.data;
  }

  // LocalStorage cache
  setLocalStorageCache<T>(key: string, data: T, ttl = this.defaultTTL): void {
    try {
      const entry: CacheEntry<T> = {
        data,
        timestamp: Date.now(),
        ttl,
        version: this.getCacheVersion()
      };
      
      localStorage.setItem(`cache_${key}`, JSON.stringify(entry));
    } catch (error) {
      console.warn('Failed to set localStorage cache:', error);
    }
  }

  getLocalStorageCache<T>(key: string): T | null {
    try {
      const stored = localStorage.getItem(`cache_${key}`);
      if (!stored) return null;

      const entry: CacheEntry<T> = JSON.parse(stored);
      
      if (Date.now() - entry.timestamp > entry.ttl) {
        localStorage.removeItem(`cache_${key}`);
        return null;
      }

      if (entry.version !== this.getCacheVersion()) {
        localStorage.removeItem(`cache_${key}`);
        return null;
      }

      return entry.data;
    } catch (error) {
      console.warn('Failed to get localStorage cache:', error);
      return null;
    }
  }

  // IndexedDB cache for large data
  async setIndexedDBCache<T>(key: string, data: T, ttl = this.defaultTTL): Promise<void> {
    try {
      const db = await this.openIndexedDB();
      const transaction = db.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
      
      const entry: CacheEntry<T> = {
        data,
        timestamp: Date.now(),
        ttl,
        version: this.getCacheVersion()
      };
      
      await store.put(entry, key);
    } catch (error) {
      console.warn('Failed to set IndexedDB cache:', error);
    }
  }

  async getIndexedDBCache<T>(key: string): Promise<T | null> {
    try {
      const db = await this.openIndexedDB();
      const transaction = db.transaction(['cache'], 'readonly');
      const store = transaction.objectStore('cache');
      
      const entry = await store.get(key) as CacheEntry<T>;
      
      if (!entry) return null;
      
      if (Date.now() - entry.timestamp > entry.ttl) {
        await this.deleteIndexedDBCache(key);
        return null;
      }

      if (entry.version !== this.getCacheVersion()) {
        await this.deleteIndexedDBCache(key);
        return null;
      }

      return entry.data;
    } catch (error) {
      console.warn('Failed to get IndexedDB cache:', error);
      return null;
    }
  }

  private async openIndexedDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('CacheDB', 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
      
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains('cache')) {
          db.createObjectStore('cache');
        }
      };
    });
  }

  private async deleteIndexedDBCache(key: string): Promise<void> {
    try {
      const db = await this.openIndexedDB();
      const transaction = db.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
      await store.delete(key);
    } catch (error) {
      console.warn('Failed to delete IndexedDB cache:', error);
    }
  }

  private getCacheVersion(): string {
    return process.env.REACT_APP_VERSION || '1.0.0';
  }

  // Unified cache interface
  async get<T>(key: string): Promise<T | null> {
    // Try memory cache first
    let data = this.getMemoryCache<T>(key);
    if (data) return data;

    // Try localStorage cache
    data = this.getLocalStorageCache<T>(key);
    if (data) {
      // Promote to memory cache
      this.setMemoryCache(key, data);
      return data;
    }

    // Try IndexedDB cache
    data = await this.getIndexedDBCache<T>(key);
    if (data) {
      // Promote to higher levels
      this.setMemoryCache(key, data);
      this.setLocalStorageCache(key, data);
      return data;
    }

    return null;
  }

  async set<T>(key: string, data: T, ttl = this.defaultTTL): Promise<void> {
    // Set in all cache levels
    this.setMemoryCache(key, data, ttl);
    this.setLocalStorageCache(key, data, ttl);
    await this.setIndexedDBCache(key, data, ttl);
  }

  invalidate(key: string): void {
    this.memoryCache.delete(key);
    localStorage.removeItem(`cache_${key}`);
    this.deleteIndexedDBCache(key);
  }

  clear(): void {
    this.memoryCache.clear();
    
    // Clear localStorage cache entries
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('cache_')) {
        localStorage.removeItem(key);
      }
    });

    // Clear IndexedDB
    this.clearIndexedDB();
  }

  private async clearIndexedDB(): Promise<void> {
    try {
      const db = await this.openIndexedDB();
      const transaction = db.transaction(['cache'], 'readwrite');
      const store = transaction.objectStore('cache');
      await store.clear();
    } catch (error) {
      console.warn('Failed to clear IndexedDB cache:', error);
    }
  }
}

export const cacheManager = new CacheManager();
```

### Service Worker Caching

```javascript
// public/sw.js
const CACHE_NAME = 'react-app-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-v1.0.0';

const STATIC_ASSETS = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/favicon.ico'
];

const API_CACHE_PATTERNS = [
  /^https:\/\/api\.example\.com\/users\/profile$/,
  /^https:\/\/api\.example\.com\/config$/
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event with different strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Network first for API calls
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
  }
  // Cache first for static assets
  else if (request.destination === 'script' || request.destination === 'style') {
    event.respondWith(cacheFirst(request));
  }
  // Stale while revalidate for images
  else if (request.destination === 'image') {
    event.respondWith(staleWhileRevalidate(request));
  }
  // Network first for HTML
  else if (request.headers.get('accept').includes('text/html')) {
    event.respondWith(networkFirst(request));
  }
  // Default: network first
  else {
    event.respondWith(networkFirst(request));
  }
});

// Caching strategies
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Network request failed:', error);
    return new Response('Network error', { status: 408 });
  }
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response('Network error', { status: 408 });
  }
}

async function staleWhileRevalidate(request) {
  const cachedResponse = await caches.match(request);
  
  const networkResponsePromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      const cache = caches.open(DYNAMIC_CACHE);
      cache.then(c => c.put(request, networkResponse.clone()));
    }
    return networkResponse;
  });

  return cachedResponse || networkResponsePromise;
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Process offline actions
  const offlineActions = await getOfflineActions();
  
  for (const action of offlineActions) {
    try {
      await fetch(action.url, action.options);
      await removeOfflineAction(action.id);
    } catch (error) {
      console.error('Failed to sync action:', error);
    }
  }
}
```

## CDN & Edge Computing

### CloudFlare Configuration

```javascript
// cloudflare-worker.js
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const cache = caches.default;
  
  // Custom caching rules
  if (url.pathname.startsWith('/api/')) {
    return handleAPI(request);
  }
  
  if (url.pathname.startsWith('/static/')) {
    return handleStatic(request, cache);
  }
  
  return handleHTML(request, cache);
}

async function handleStatic(request, cache) {
  // Cache static assets for 1 year
  const cacheKey = new Request(request.url, request);
  let response = await cache.match(cacheKey);
  
  if (!response) {
    response = await fetch(request);
    
    if (response.ok) {
      const headers = new Headers(response.headers);
      headers.set('Cache-Control', 'public, max-age=31536000, immutable');
      headers.set('CDN-Cache-Control', 'max-age=31536000');
      
      response = new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: headers
      });
      
      // Cache at edge
      event.waitUntil(cache.put(cacheKey, response.clone()));
    }
  }
  
  return response;
}

async function handleHTML(request, cache) {
  const cacheKey = new Request(request.url, request);
  let response = await cache.match(cacheKey);
  
  if (!response || shouldRevalidate(response)) {
    response = await fetch(request);
    
    if (response.ok) {
      const headers = new Headers(response.headers);
      headers.set('Cache-Control', 'public, max-age=300, s-maxage=3600');
      headers.set('CDN-Cache-Control', 'max-age=3600');
      
      // Add security headers
      headers.set('X-Frame-Options', 'DENY');
      headers.set('X-Content-Type-Options', 'nosniff');
      headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
      
      response = new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: headers
      });
      
      event.waitUntil(cache.put(cacheKey, response.clone()));
    }
  }
  
  return response;
}

async function handleAPI(request) {
  // Add rate limiting
  const clientIP = request.headers.get('CF-Connecting-IP');
  const rateLimitKey = `rate_limit_${clientIP}`;
  
  // Check rate limit (implement with KV storage)
  const rateLimitCheck = await checkRateLimit(rateLimitKey);
  
  if (!rateLimitCheck.allowed) {
    return new Response('Rate limit exceeded', { status: 429 });
  }
  
  // Forward to origin with additional headers
  const modifiedHeaders = new Headers(request.headers);
  modifiedHeaders.set('X-Forwarded-For', clientIP);
  modifiedHeaders.set('X-Real-IP', clientIP);
  
  const modifiedRequest = new Request(request.url, {
    method: request.method,
    headers: modifiedHeaders,
    body: request.body
  });
  
  return fetch(modifiedRequest);
}

function shouldRevalidate(response) {
  const cacheControl = response.headers.get('Cache-Control');
  if (!cacheControl) return true;
  
  const maxAge = cacheControl.match(/max-age=(\d+)/);
  if (!maxAge) return true;
  
  const age = response.headers.get('Age') || '0';
  return parseInt(age) > parseInt(maxAge[1]);
}
```

### AWS CloudFront Configuration

```json
{
  "Comment": "React App Distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "react-app-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true,
    "CachePolicyId": "react-app-cache-policy",
    "OriginRequestPolicyId": "react-app-origin-policy",
    "ResponseHeadersPolicyId": "react-app-response-headers"
  },
  "CacheBehaviors": [
    {
      "PathPattern": "/static/*",
      "TargetOriginId": "react-app-origin",
      "ViewerProtocolPolicy": "redirect-to-https",
      "Compress": true,
      "CachePolicyId": "static-assets-cache-policy",
      "TTL": {
        "DefaultTTL": 31536000,
        "MaxTTL": 31536000
      }
    },
    {
      "PathPattern": "/api/*",
      "TargetOriginId": "api-origin",
      "ViewerProtocolPolicy": "redirect-to-https",
      "CachePolicyId": "api-cache-policy",
      "AllowedMethods": ["GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"],
      "TTL": {
        "DefaultTTL": 0,
        "MaxTTL": 300
      }
    }
  ],
  "Origins": [
    {
      "Id": "react-app-origin",
      "DomainName": "react-app.s3.amazonaws.com",
      "S3OriginConfig": {
        "OriginAccessIdentity": "origin-access-identity/cloudfront/ABCDEFG1234567"
      }
    },
    {
      "Id": "api-origin",
      "DomainName": "api.example.com",
      "CustomOriginConfig": {
        "HTTPPort": 443,
        "OriginProtocolPolicy": "https-only",
        "OriginSSLProtocols": ["TLSv1.2"]
      }
    }
  ],
  "CustomErrorResponses": [
    {
      "ErrorCode": 404,
      "ResponseCode": 200,
      "ResponsePagePath": "/index.html",
      "ErrorCachingMinTTL": 300
    }
  ]
}
```

This comprehensive security and production optimization guide provides enterprise-level practices for deploying React applications with maximum security, performance, and reliability.
