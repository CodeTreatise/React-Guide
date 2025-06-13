# Module 16: Deployment & DevOps

## 📚 Learning Objectives

By the end of this module, you will:
- Master various deployment strategies and platforms
- Implement comprehensive CI/CD pipelines for React applications
- Configure monitoring, logging, and analytics
- Set up performance monitoring and error tracking
- Implement security best practices for production
- Understand containerization with Docker and Kubernetes
- Configure CDN and caching strategies
- Build automated testing and deployment workflows

## 🎯 Prerequisites

- Completed Modules 1-15
- Basic understanding of cloud platforms (AWS, Vercel, Netlify)
- Familiarity with Git and version control
- Basic knowledge of Docker and containerization concepts

## 📖 Module Content

### 1. Deployment Platforms Overview

#### **Platform Comparison**

| Platform | Best For | Pricing | Features | Complexity |
|----------|----------|---------|----------|------------|
| **Vercel** | Next.js, JAMstack | Free tier, Pay per use | Instant deploy, CDN, Serverless | Low |
| **Netlify** | Static sites, JAMstack | Free tier, Pay per use | Git integration, Forms, Functions | Low |
| **AWS Amplify** | Full-stack apps | Pay per use | CI/CD, Hosting, Backend services | Medium |
| **AWS S3 + CloudFront** | Static sites | Pay per use | Full control, Scalable | Medium |
| **Heroku** | Full-stack apps | Free tier, Monthly plans | Easy deployment, Add-ons | Low |
| **DigitalOcean** | Full control | Monthly VPS pricing | Droplets, App Platform | Medium |
| **Google Cloud** | Enterprise | Pay per use | Firebase, Cloud Run | Medium-High |
| **Azure** | Enterprise | Pay per use | Static Web Apps, App Service | Medium-High |

#### **Deployment Strategy Selection**
```typescript
// src/utils/deploymentStrategy.ts
interface DeploymentRequirements {
  traffic: 'low' | 'medium' | 'high' | 'enterprise';
  budget: 'minimal' | 'moderate' | 'flexible' | 'enterprise';
  complexity: 'static' | 'spa' | 'ssr' | 'fullstack';
  teamSize: number;
  complianceNeeds: boolean;
  globalAudience: boolean;
}

export const selectDeploymentStrategy = (requirements: DeploymentRequirements): string => {
  if (requirements.complexity === 'static' || requirements.complexity === 'spa') {
    if (requirements.budget === 'minimal') {
      return 'Netlify or Vercel (Free Tier)';
    }
    if (requirements.globalAudience) {
      return 'AWS S3 + CloudFront or Vercel Pro';
    }
    return 'Netlify or Vercel';
  }

  if (requirements.complexity === 'ssr') {
    return 'Vercel (Next.js) or AWS Amplify';
  }

  if (requirements.complexity === 'fullstack') {
    if (requirements.traffic === 'enterprise') {
      return 'AWS ECS/EKS or Google Cloud Run';
    }
    return 'Heroku or DigitalOcean App Platform';
  }

  return 'Vercel'; // Default recommendation
};
```

### 2. Static Site Deployment

#### **Netlify Deployment Configuration**
```toml
# netlify.toml
[build]
  publish = "dist"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"
  NPM_VERSION = "9"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/index.html"
  [headers.values]
    Cache-Control = "public, max-age=0, must-revalidate"
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"

[context.production.environment]
  REACT_APP_API_URL = "https://api.myapp.com"
  REACT_APP_ENVIRONMENT = "production"

[context.deploy-preview.environment]
  REACT_APP_API_URL = "https://staging-api.myapp.com"
  REACT_APP_ENVIRONMENT = "staging"
```

#### **Vercel Deployment Configuration**
```json
{
  "version": 2,
  "name": "react-app",
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "@api-url",
    "REACT_APP_ENVIRONMENT": "production"
  },
  "build": {
    "env": {
      "NODE_ENV": "production"
    }
  }
}
```

### 3. AWS Deployment

#### **AWS S3 + CloudFront Setup**
```bash
#!/bin/bash
# deploy-aws.sh

# Configuration
BUCKET_NAME="my-react-app-bucket"
DISTRIBUTION_ID="E1234567890123"
REGION="us-east-1"

# Build the application
echo "Building application..."
npm run build

# Upload to S3
echo "Uploading to S3..."
aws s3 sync dist/ s3://$BUCKET_NAME --delete \
  --cache-control "max-age=31536000" \
  --exclude "index.html" \
  --exclude "service-worker.js"

# Upload index.html with no cache
aws s3 cp dist/index.html s3://$BUCKET_NAME/index.html \
  --cache-control "max-age=0, no-cache, no-store, must-revalidate"

# Upload service worker with no cache
aws s3 cp dist/service-worker.js s3://$BUCKET_NAME/service-worker.js \
  --cache-control "max-age=0, no-cache, no-store, must-revalidate"

# Invalidate CloudFront cache
echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"

echo "Deployment complete!"
```

#### **AWS CDK Infrastructure**
```typescript
// infrastructure/react-app-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';

export class ReactAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 bucket for hosting
    const siteBucket = new s3.Bucket(this, 'SiteBucket', {
      bucketName: 'my-react-app-bucket',
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'index.html',
      publicReadAccess: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // CloudFront distribution
    const distribution = new cloudfront.Distribution(this, 'SiteDistribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(siteBucket),
        compress: true,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      additionalBehaviors: {
        '/static/*': {
          origin: new origins.S3Origin(siteBucket),
          compress: true,
          cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED_FOR_UNCOMPRESSED_OBJECTS,
        },
      },
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.minutes(30),
        },
      ],
    });

    // Deploy site contents to S3 bucket
    new s3deploy.BucketDeployment(this, 'DeployWithInvalidation', {
      sources: [s3deploy.Source.asset('./dist')],
      destinationBucket: siteBucket,
      distribution,
      distributionPaths: ['/*'],
    });

    // Outputs
    new cdk.CfnOutput(this, 'DistributionDomainName', {
      value: distribution.domainName,
      description: 'CloudFront Distribution Domain Name',
    });

    new cdk.CfnOutput(this, 'BucketWebsiteURL', {
      value: siteBucket.bucketWebsiteUrl,
      description: 'S3 Bucket Website URL',
    });
  }
}
```

### 4. CI/CD Pipeline Implementation

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/deploy.yml
name: Deploy React App

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  CACHE_PATHS: |
    ~/.npm
    node_modules
    .next/cache

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run type checking
        run: npm run type-check

      - name: Run tests
        run: npm run test:ci
        env:
          CI: true

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build
        env:
          REACT_APP_API_URL: ${{ github.ref == 'refs/heads/main' && secrets.PROD_API_URL || secrets.STAGING_API_URL }}
          REACT_APP_ENVIRONMENT: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-files
          path: dist/

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-files
          path: dist/

      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2.0
        with:
          publish-dir: './dist'
          production-branch: main
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: "Deploy from GitHub Actions"
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_STAGING_SITE_ID }}

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-files
          path: dist/

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Deploy to S3
        run: |
          aws s3 sync dist/ s3://${{ secrets.S3_BUCKET }} --delete \
            --cache-control "max-age=31536000" \
            --exclude "index.html" \
            --exclude "service-worker.js"
          
          aws s3 cp dist/index.html s3://${{ secrets.S3_BUCKET }}/index.html \
            --cache-control "max-age=0, no-cache, no-store, must-revalidate"

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"

  lighthouse:
    needs: deploy-production
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://myapp.com
            https://myapp.com/dashboard
          uploadArtifacts: true
          temporaryPublicStorage: true

  notify:
    needs: [deploy-production, lighthouse]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

#### **Advanced CI/CD Configuration**
```yaml
# .github/workflows/advanced-deploy.yml
name: Advanced Deploy Pipeline

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run security audit
        run: npm audit --audit-level high
      
      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  performance-budget:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build and analyze bundle
        run: |
          npm run build
          npm run analyze:bundle
      
      - name: Check bundle size
        uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

  canary-deployment:
    needs: [security-scan, performance-budget]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to canary environment
        run: |
          # Deploy 5% of traffic to new version
          echo "Deploying canary version..."
      
      - name: Run smoke tests
        run: |
          # Run critical path tests
          npm run test:e2e:smoke
      
      - name: Monitor metrics
        run: |
          # Check error rates and performance
          echo "Monitoring canary metrics..."

  blue-green-deployment:
    needs: canary-deployment
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Deploy to green environment
        run: |
          echo "Deploying to green environment..."
      
      - name: Run full test suite
        run: |
          npm run test:e2e:full
      
      - name: Switch traffic to green
        run: |
          echo "Switching traffic to green environment..."
      
      - name: Monitor and rollback if needed
        run: |
          echo "Monitoring deployment..."
```

### 5. Monitoring and Analytics

#### **Application Performance Monitoring**
```typescript
// src/utils/monitoring.ts
interface PerformanceMetrics {
  fcp: number; // First Contentful Paint
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  ttfb: number; // Time to First Byte
}

class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {};
  
  constructor() {
    this.observeWebVitals();
    this.observeCustomMetrics();
  }

  private observeWebVitals() {
    // Observe Core Web Vitals
    import('web-vitals').then(({ onFCP, onLCP, onFID, onCLS, onTTFB }) => {
      onFCP((metric) => {
        this.metrics.fcp = metric.value;
        this.sendMetric('fcp', metric.value);
      });

      onLCP((metric) => {
        this.metrics.lcp = metric.value;
        this.sendMetric('lcp', metric.value);
      });

      onFID((metric) => {
        this.metrics.fid = metric.value;
        this.sendMetric('fid', metric.value);
      });

      onCLS((metric) => {
        this.metrics.cls = metric.value;
        this.sendMetric('cls', metric.value);
      });

      onTTFB((metric) => {
        this.metrics.ttfb = metric.value;
        this.sendMetric('ttfb', metric.value);
      });
    });
  }

  private observeCustomMetrics() {
    // Custom performance marks
    performance.mark('app-start');
    
    // Observe React component mount times
    this.observeComponentMetrics();
    
    // Observe API response times
    this.observeNetworkMetrics();
  }

  private observeComponentMetrics() {
    // Use React DevTools Profiler API
    if (process.env.NODE_ENV === 'production') {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.name.startsWith('⚛️')) {
            this.sendMetric('react-render', entry.duration);
          }
        });
      });
      
      observer.observe({ entryTypes: ['measure'] });
    }
  }

  private observeNetworkMetrics() {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'navigation') {
          const navEntry = entry as PerformanceNavigationTiming;
          this.sendMetric('page-load', navEntry.loadEventEnd - navEntry.fetchStart);
        }
        
        if (entry.entryType === 'resource') {
          const resourceEntry = entry as PerformanceResourceTiming;
          if (resourceEntry.name.includes('/api/')) {
            this.sendMetric('api-response', resourceEntry.responseEnd - resourceEntry.requestStart);
          }
        }
      });
    });
    
    observer.observe({ entryTypes: ['navigation', 'resource'] });
  }

  private sendMetric(name: string, value: number) {
    // Send to analytics service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'timing_complete', {
        name,
        value: Math.round(value)
      });
    }

    // Send to custom monitoring service
    fetch('/api/metrics', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        metric: name,
        value,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href
      })
    }).catch(() => {
      // Silently fail metrics reporting
    });
  }

  getMetrics(): Partial<PerformanceMetrics> {
    return { ...this.metrics };
  }
}

export const performanceMonitor = new PerformanceMonitor();
```

#### **Error Tracking with Sentry**
```typescript
// src/utils/errorTracking.ts
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

export const initializeErrorTracking = () => {
  Sentry.init({
    dsn: process.env.REACT_APP_SENTRY_DSN,
    integrations: [
      new BrowserTracing({
        routingInstrumentation: Sentry.reactRouterV6Instrumentation(
          React.useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes
        ),
      }),
    ],
    
    // Performance monitoring
    tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
    
    // Release tracking
    release: process.env.REACT_APP_VERSION,
    environment: process.env.REACT_APP_ENVIRONMENT,
    
    // Error filtering
    beforeSend(event, hint) {
      // Filter out non-critical errors
      if (event.exception) {
        const error = hint.originalException;
        if (error && error.message && error.message.includes('Non-Error promise rejection')) {
          return null;
        }
      }
      
      return event;
    },
    
    // Session tracking
    autoSessionTracking: true,
    
    // User context
    initialScope: {
      tags: {
        component: "React App"
      }
    }
  });
};

// Error boundary with Sentry integration
export const SentryErrorBoundary = Sentry.withErrorBoundary(
  ({ children }: { children: React.ReactNode }) => children,
  {
    fallback: ({ error, resetError }) => (
      <div className="error-boundary">
        <h2>Something went wrong</h2>
        <p>{error?.message}</p>
        <button onClick={resetError}>Try again</button>
      </div>
    ),
    beforeCapture: (scope, error, errorInfo) => {
      scope.setTag("errorBoundary", true);
      scope.setContext("errorInfo", errorInfo);
    }
  }
);
```

### 6. Security Configuration

#### **Security Headers**
```typescript
// security/headers.ts
export const securityHeaders = {
  // Content Security Policy
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.google-analytics.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https:",
    "connect-src 'self' https://api.myapp.com https://www.google-analytics.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'"
  ].join('; '),
  
  // XSS Protection
  'X-XSS-Protection': '1; mode=block',
  
  // Content Type Options
  'X-Content-Type-Options': 'nosniff',
  
  // Frame Options
  'X-Frame-Options': 'DENY',
  
  // Referrer Policy
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  
  // Permissions Policy
  'Permissions-Policy': [
    'camera=()',
    'microphone=()',
    'geolocation=()',
    'payment=()',
    'usb=()',
    'magnetometer=()',
    'gyroscope=()',
    'accelerometer=()'
  ].join(', '),
  
  // HSTS (for HTTPS)
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
};
```

#### **Environment Variable Management**
```typescript
// src/config/environment.ts
interface EnvironmentConfig {
  apiUrl: string;
  environment: 'development' | 'staging' | 'production';
  version: string;
  sentryDsn?: string;
  googleAnalyticsId?: string;
  features: {
    enableAnalytics: boolean;
    enableErrorTracking: boolean;
    enablePerformanceMonitoring: boolean;
  };
}

const requiredEnvVars = [
  'REACT_APP_API_URL',
  'REACT_APP_ENVIRONMENT'
] as const;

// Validate required environment variables
const validateEnvironment = (): void => {
  const missing = requiredEnvVars.filter(
    envVar => !process.env[envVar]
  );
  
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}`
    );
  }
};

// Environment configuration
export const getEnvironmentConfig = (): EnvironmentConfig => {
  validateEnvironment();
  
  const environment = process.env.REACT_APP_ENVIRONMENT as EnvironmentConfig['environment'];
  const isProduction = environment === 'production';
  
  return {
    apiUrl: process.env.REACT_APP_API_URL!,
    environment,
    version: process.env.REACT_APP_VERSION || '1.0.0',
    sentryDsn: process.env.REACT_APP_SENTRY_DSN,
    googleAnalyticsId: process.env.REACT_APP_GA_ID,
    
    features: {
      enableAnalytics: isProduction && !!process.env.REACT_APP_GA_ID,
      enableErrorTracking: !!process.env.REACT_APP_SENTRY_DSN,
      enablePerformanceMonitoring: isProduction
    }
  };
};

// Environment-specific API client
export const createApiClient = () => {
  const config = getEnvironmentConfig();
  
  return {
    baseURL: config.apiUrl,
    timeout: config.environment === 'development' ? 30000 : 10000,
    headers: {
      'Content-Type': 'application/json',
      'X-Client-Version': config.version,
      'X-Environment': config.environment
    }
  };
};
```

### 7. Containerization with Docker

#### **Production Dockerfile**
```dockerfile
# Dockerfile
# Multi-stage build for React application

# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production --silent

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### **Nginx Configuration**
```nginx
# nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/x-javascript
        application/xml+rss
        application/javascript
        application/json;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # Static assets caching
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Main application
        location / {
            try_files $uri $uri/ /index.html;
            
            # No caching for HTML files
            location ~* \.html$ {
                expires -1;
                add_header Cache-Control "no-cache, no-store, must-revalidate";
            }
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # Error pages
        error_page 404 /index.html;
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
```

#### **Docker Compose for Development**
```yaml
# docker-compose.yml
version: '3.8'

services:
  react-app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - api

  api:
    image: node:18-alpine
    working_dir: /api
    ports:
      - "8000:8000"
    volumes:
      - ./api:/api
      - /api/node_modules
    command: npm run dev
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://user:password@db:5432/myapp

  db:
    image: postgres:14-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.dev.conf:/etc/nginx/nginx.conf
    depends_on:
      - react-app
      - api

volumes:
  postgres_data:
```

### 8. Kubernetes Deployment

#### **Kubernetes Manifests**
```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: react-app
  labels:
    app: react-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: react-app
  template:
    metadata:
      labels:
        app: react-app
    spec:
      containers:
      - name: react-app
        image: myregistry/react-app:latest
        ports:
        - containerPort: 80
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: react-app-service
spec:
  selector:
    app: react-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: react-app-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - myapp.com
    secretName: react-app-tls
  rules:
  - host: myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: react-app-service
            port:
              number: 80
```

### 9. Performance Optimization

#### **CDN Configuration**
```javascript
// cdn-config.js
const CDN_CONFIG = {
  // CloudFront behaviors
  behaviors: [
    {
      pathPattern: '/static/*',
      targetOrigin: 's3-origin',
      cachePolicyId: 'CachingOptimized',
      compress: true,
      viewerProtocolPolicy: 'redirect-to-https',
      allowedMethods: ['GET', 'HEAD'],
      cachedMethods: ['GET', 'HEAD'],
      smoothStreaming: false,
      fieldLevelEncryptionId: '',
      forwardedValues: {
        queryString: false,
        cookies: { forward: 'none' }
      }
    },
    {
      pathPattern: '/api/*',
      targetOrigin: 'api-origin',
      cachePolicyId: 'CachingDisabled',
      compress: true,
      viewerProtocolPolicy: 'https-only',
      allowedMethods: ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
      cachedMethods: ['GET', 'HEAD'],
      originRequestPolicyId: 'CORS-S3Origin'
    }
  ],
  
  // Cache policies
  cachePolicies: {
    static: {
      name: 'StaticAssets',
      defaultTTL: 86400, // 1 day
      maxTTL: 31536000,  // 1 year
      minTTL: 0,
      parametersInCacheKeyAndForwardedToOrigin: {
        enableAcceptEncodingBrotli: true,
        enableAcceptEncodingGzip: true,
        queryStringsConfig: {
          queryStringBehavior: 'none'
        },
        headersConfig: {
          headerBehavior: 'none'
        },
        cookiesConfig: {
          cookieBehavior: 'none'
        }
      }
    }
  }
};
```

## 🎯 Practical Exercises

### Exercise 1: Multi-Platform Deployment
Deploy the same React app to Netlify, Vercel, and AWS with different configurations.

### Exercise 2: CI/CD Pipeline Setup
Create a comprehensive CI/CD pipeline with testing, security scanning, and automated deployment.

### Exercise 3: Monitoring Implementation
Set up comprehensive monitoring with performance tracking, error reporting, and analytics.

### Exercise 4: Kubernetes Deployment
Deploy a React application to a Kubernetes cluster with proper scaling and monitoring.

## 📊 Assessment Criteria

### Deployment Mastery
- [ ] Deploy to multiple platforms successfully
- [ ] Configure proper environment management
- [ ] Implement security best practices
- [ ] Set up SSL/TLS and domain configuration

### CI/CD Implementation
- [ ] Create automated testing pipelines
- [ ] Implement proper deployment strategies
- [ ] Configure environment-specific deployments
- [ ] Set up monitoring and alerting

### Production Readiness
- [ ] Implement comprehensive monitoring
- [ ] Configure error tracking and logging
- [ ] Optimize performance and caching
- [ ] Ensure security compliance

## 🚀 Final Project: Production-Ready Deployment

Deploy a complete React application with:

**Infrastructure Requirements:**
- Multi-environment setup (dev, staging, production)
- CDN configuration with proper caching
- SSL/TLS with automatic renewal
- Load balancing and auto-scaling
- Database and API integration

**Monitoring & Analytics:**
- Performance monitoring (Core Web Vitals)
- Error tracking and alerting
- User analytics and behavior tracking
- Security monitoring
- Cost optimization tracking

**DevOps Pipeline:**
- Automated testing and quality gates
- Security scanning and compliance checks
- Blue-green or canary deployment strategy
- Automated rollback capabilities
- Infrastructure as Code (IaC)

**Performance Targets:**
- 99.9% uptime
- < 2s page load time
- < 100ms API response time
- 90+ Lighthouse scores
- Zero critical security vulnerabilities

## 📚 Additional Resources

### Platforms
- Vercel
- Netlify
- AWS Amplify
- Heroku
- DigitalOcean

### Monitoring Tools
- Google Analytics
- Sentry
- LogRocket
- New Relic
- Datadog

### Documentation
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions](https://docs.github.com/en/actions)

## ✅ Course Completion

Congratulations! You have completed the comprehensive React learning journey:

### What You've Accomplished:
- Mastered React fundamentals and advanced patterns
- Learned state management with Context, Redux, and Zustand
- Implemented performance optimization techniques
- Built comprehensive testing strategies
- Established code quality and development workflows
- Configured modern build tools and bundling
- Deployed production-ready applications

### Next Steps:
- Build production applications using learned concepts
- Contribute to open-source React projects
- Stay updated with React ecosystem developments
- Explore advanced topics like React Server Components
- Learn complementary technologies (GraphQL, TypeScript, etc.)

### Continuous Learning:
- Follow React team updates and RFC proposals
- Join React community discussions and conferences
- Practice building real-world applications
- Mentor other developers learning React

---

**Total Course Duration:** 16-20 weeks  
**Final Assessment:** Production deployment with all modules integrated  
**Certification:** Complete all modules with practical projects

**🎉 Welcome to the React Expert Community! 🎉**
