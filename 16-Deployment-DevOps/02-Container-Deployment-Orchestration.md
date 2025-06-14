# Container Deployment & Orchestration

## Table of Contents
- [Docker Fundamentals for React](#docker-fundamentals-for-react)
- [Multi-Stage Docker Builds](#multi-stage-docker-builds)
- [Container Optimization](#container-optimization)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Container Orchestration Patterns](#container-orchestration-patterns)
- [Service Mesh & Networking](#service-mesh--networking)
- [Auto-scaling & Load Balancing](#auto-scaling--load-balancing)
- [Container Security](#container-security)
- [Monitoring & Observability](#monitoring--observability)
- [Production Best Practices](#production-best-practices)

## Docker Fundamentals for React

### Basic Dockerfile Setup

```dockerfile
# Basic React Dockerfile
FROM node:18-alpine AS base

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY yarn.lock* ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=base /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Advanced Dockerfile with Health Checks

```dockerfile
# Advanced React Dockerfile with health checks
FROM node:18-alpine AS builder

# Install security updates
RUN apk update && apk upgrade && apk add --no-cache dumb-init

# Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S reactuser -u 1001

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY yarn.lock* ./

# Install dependencies with exact versions
RUN npm ci --frozen-lockfile --only=production

# Copy source code
COPY --chown=reactuser:nodejs . .

# Build application
RUN npm run build

# Production stage
FROM nginx:1.21-alpine AS production

# Install security updates
RUN apk update && apk upgrade

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY mime.types /etc/nginx/mime.types

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Development Dockerfile

```dockerfile
# Development Dockerfile with hot reload
FROM node:18-alpine

# Install development tools
RUN apk add --no-cache git curl

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY yarn.lock* ./

# Install all dependencies (including dev)
RUN npm install

# Copy source code
COPY . .

# Expose port for development server
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
```

## Multi-Stage Docker Builds

### Optimized Multi-Stage Build

```dockerfile
# Multi-stage build for production optimization
FROM node:18-alpine AS dependencies

WORKDIR /app
COPY package*.json ./
RUN npm ci --frozen-lockfile

FROM node:18-alpine AS build

WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .

# Build with production optimizations
ENV NODE_ENV=production
RUN npm run build

# Analyze bundle size
RUN npm run analyze

FROM nginx:alpine AS production

# Copy built assets
COPY --from=build /app/build /usr/share/nginx/html

# Copy configuration files
COPY nginx.conf /etc/nginx/nginx.conf

# Add security headers
COPY security-headers.conf /etc/nginx/conf.d/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Build with Testing Stage

```dockerfile
# Multi-stage with testing
FROM node:18-alpine AS base

WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM base AS test

COPY . .
RUN npm run lint
RUN npm run test:ci
RUN npm run test:e2e

FROM base AS build

COPY . .
RUN npm run build

FROM nginx:alpine AS production

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Container Optimization

### Image Size Optimization

```dockerfile
# Optimized for minimal image size
FROM node:18-alpine AS builder

# Use specific package manager
RUN npm install -g pnpm

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies with pnpm for smaller node_modules
RUN pnpm install --frozen-lockfile --prod

# Copy source and build
COPY . .
RUN pnpm build

# Minimal production image
FROM nginx:alpine

# Remove unnecessary packages
RUN apk del --purge && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/*

# Copy only built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Use minimal nginx config
COPY nginx.minimal.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Layer Caching Optimization

```dockerfile
# Optimized for Docker layer caching
FROM node:18-alpine

WORKDIR /app

# Copy and install dependencies first (cached layer)
COPY package*.json ./
RUN npm ci --frozen-lockfile

# Copy source files (invalidates cache only when source changes)
COPY public/ ./public/
COPY src/ ./src/
COPY tsconfig.json ./
COPY .env* ./

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Kubernetes Deployment

### Basic Kubernetes Deployment

```yaml
# k8s/deployment.yaml
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
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Configuration

```yaml
# k8s/service.yaml
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
# Load Balancer Service
apiVersion: v1
kind: Service
metadata:
  name: react-app-lb
spec:
  selector:
    app: react-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: react-app-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: react-app-tls
  rules:
  - host: myapp.example.com
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

### ConfigMap and Secrets

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: react-app-config
data:
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        location /api {
            proxy_pass http://api-service:8080;
        }
    }

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: react-app-secrets
type: Opaque
data:
  api-key: <base64-encoded-api-key>
  database-url: <base64-encoded-database-url>
```

## Container Orchestration Patterns

### Helm Chart for React Application

```yaml
# helm/react-app/Chart.yaml
apiVersion: v2
name: react-app
description: A Helm chart for React application
type: application
version: 0.1.0
appVersion: "1.0.0"
```

```yaml
# helm/react-app/values.yaml
replicaCount: 3

image:
  repository: myregistry/react-app
  pullPolicy: IfNotPresent
  tag: ""

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls:
    - secretName: react-app-tls
      hosts:
        - myapp.example.com

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}
```

### Docker Compose for Development

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
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      - api

  api:
    image: node:18-alpine
    working_dir: /app
    command: npm start
    ports:
      - "8080:8080"
    volumes:
      - ./api:/app
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:password@db:5432/myapp

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

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

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  react-app:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.react-app.rule=Host(`myapp.example.com`)"
      - "traefik.http.routers.react-app.tls=true"
      - "traefik.http.routers.react-app.tls.certresolver=letsencrypt"

  traefik:
    image: traefik:v2.5
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./acme.json:/acme.json
    restart: unless-stopped
```

## Service Mesh & Networking

### Istio Service Mesh Configuration

```yaml
# istio/virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: react-app-vs
spec:
  hosts:
  - myapp.example.com
  gateways:
  - react-app-gateway
  http:
  - match:
    - uri:
        prefix: /api
    route:
    - destination:
        host: api-service
        port:
          number: 8080
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: react-app-service
        port:
          number: 80

---
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: react-app-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - myapp.example.com
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: react-app-tls
    hosts:
    - myapp.example.com
```

### Network Policies

```yaml
# k8s/network-policy.yaml
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
          name: istio-system
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 8080
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

## Auto-scaling & Load Balancing

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: react-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: react-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Vertical Pod Autoscaler

```yaml
# k8s/vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: react-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: react-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: react-app
      maxAllowed:
        cpu: 1
        memory: 500Mi
      minAllowed:
        cpu: 100m
        memory: 50Mi
      controlledResources: ["cpu", "memory"]
```

### Load Balancer Configuration

```yaml
# k8s/load-balancer.yaml
apiVersion: v1
kind: Service
metadata:
  name: react-app-lb
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: 'true'
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: http
spec:
  type: LoadBalancer
  selector:
    app: react-app
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
```

## Container Security

### Security-Hardened Dockerfile

```dockerfile
# Security-focused Dockerfile
FROM node:18-alpine AS builder

# Update packages and remove package manager cache
RUN apk update && apk upgrade && \
    apk add --no-cache dumb-init && \
    rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactuser -u 1001 -G nodejs

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --frozen-lockfile --only=production && \
    npm cache clean --force

# Copy source code and set ownership
COPY --chown=reactuser:nodejs . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install security updates
RUN apk update && apk upgrade && \
    rm -rf /var/cache/apk/*

# Remove default nginx user and create custom user
RUN deluser nginx && \
    addgroup -g 1001 -S nginx && \
    adduser -S nginx -u 1001 -G nginx

# Copy built application
COPY --from=builder --chown=nginx:nginx /app/build /usr/share/nginx/html

# Copy secure nginx configuration
COPY --chown=nginx:nginx nginx.conf /etc/nginx/nginx.conf

# Set proper permissions
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 8080

# Use dumb-init to handle signals properly
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["nginx", "-g", "daemon off;"]
```

### Pod Security Context

```yaml
# k8s/deployment-secure.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: react-app-secure
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
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: react-app
        image: myregistry/react-app:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: var-cache
          mountPath: /var/cache/nginx
        - name: var-run
          mountPath: /var/run
      volumes:
      - name: tmp
        emptyDir: {}
      - name: var-cache
        emptyDir: {}
      - name: var-run
        emptyDir: {}
```

### Container Scanning with Trivy

```yaml
{% raw %}
# .github/workflows/security-scan.yml
name: Container Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

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

    - name: Check for critical vulnerabilities
      run: |
        trivy image --severity CRITICAL --exit-code 1 react-app:${{ github.sha }}
{% endraw %}
```

## Monitoring & Observability

### Prometheus Monitoring

```yaml
# k8s/service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: react-app-monitor
  labels:
    app: react-app
spec:
  selector:
    matchLabels:
      app: react-app
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

```yaml
# k8s/deployment-with-metrics.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: react-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: react-app
  template:
    metadata:
      labels:
        app: react-app
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: react-app
        image: myregistry/react-app:latest
        ports:
        - containerPort: 80
          name: http
        - containerPort: 8080
          name: metrics
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Jaeger Tracing Configuration

```yaml
# k8s/jaeger-deployment.yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: react-app-jaeger
spec:
  strategy: production
  storage:
    type: elasticsearch
    elasticsearch:
      nodeCount: 3
      storage:
        storageClassName: fast-ssd
        size: 10Gi
  ingress:
    enabled: true
    annotations:
      kubernetes.io/ingress.class: nginx
    hosts:
      - jaeger.example.com
```

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "React App Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(nginx_http_requests_total[5m])",
            "legendFormat": "{{ instance }}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(nginx_http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(nginx_http_requests_total{status=~\"5..\"}[5m]) / rate(nginx_http_requests_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

## Production Best Practices

### Multi-Environment Configuration

```yaml
# environments/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

images:
- name: react-app
  newTag: v1.0.0

replicas:
- name: react-app
  count: 5

patchesStrategicMerge:
- deployment-patch.yaml
- service-patch.yaml

configMapGenerator:
- name: react-app-config
  files:
  - nginx.conf=nginx.prod.conf

secretGenerator:
- name: react-app-secrets
  env: secrets.env
```

### Blue-Green Deployment

```yaml
# k8s/blue-green-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: react-app-rollout
spec:
  replicas: 5
  strategy:
    blueGreen:
      activeService: react-app-active
      previewService: react-app-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: react-app-preview
      postPromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: react-app-active
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
```

### Canary Deployment

```yaml
# k8s/canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: react-app-canary
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 1m}
      - setWeight: 20
      - pause: {duration: 1m}
      - setWeight: 50
      - pause: {duration: 1m}
      - setWeight: 100
      analysis:
        templates:
        - templateName: error-rate
        args:
        - name: service-name
          value: react-app
        startingStep: 1
        successCondition: result[0] < 0.01
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
```

### Disaster Recovery

```yaml
# k8s/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: react-app-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool:latest
            command:
            - /bin/sh
            - -c
            - |
              # Backup application data
              kubectl get deployment react-app -o yaml > /backup/deployment-$(date +%Y%m%d).yaml
              kubectl get configmap react-app-config -o yaml > /backup/configmap-$(date +%Y%m%d).yaml
              kubectl get secret react-app-secrets -o yaml > /backup/secrets-$(date +%Y%m%d).yaml
              
              # Upload to cloud storage
              aws s3 sync /backup/ s3://my-backup-bucket/react-app/
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
```

This comprehensive guide covers container deployment and orchestration for React applications, from basic Docker setups to advanced Kubernetes patterns with security, monitoring, and production best practices. The examples provide practical implementations for real-world scenarios.
