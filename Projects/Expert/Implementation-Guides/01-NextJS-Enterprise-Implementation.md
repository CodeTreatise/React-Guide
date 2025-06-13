# 🌟 Next.js Enterprise SaaS Platform Implementation Guide

> **Project**: Enterprise-Grade Multi-Tenant SaaS Platform  
> **Level**: Expert  
> **Estimated Time**: 15-20 hours  
> **Focus**: Next.js mastery, SSR/SSG/ISR, Enterprise architecture, Multi-tenancy

---

## 🚀 Quick Start (45 minutes)

### Step 1: Setup Enterprise Next.js Project
```bash
npx create-next-app@latest enterprise-saas-platform --typescript --tailwind --eslint --app
cd enterprise-saas-platform
npm install @prisma/client prisma next-auth@beta @stripe/stripe-js @vercel/analytics
npm install -D @types/node typescript @typescript-eslint/eslint-plugin
npm run dev
```

### Step 2: Database & Authentication Setup
```bash
# Initialize Prisma
npx prisma init
# Configure your database URL in .env.local
echo "NEXTAUTH_SECRET=your-secret-key-here" >> .env.local
echo "NEXTAUTH_URL=http://localhost:3000" >> .env.local
```

### Step 3: Basic Multi-Tenant Architecture
```typescript
// app/[tenant]/layout.tsx
import { getTenantByDomain } from '@/lib/tenants';
import { notFound } from 'next/navigation';

interface TenantLayoutProps {
  children: React.ReactNode;
  params: { tenant: string };
}

export default async function TenantLayout({ 
  children, 
  params 
}: TenantLayoutProps) {
  const tenant = await getTenantByDomain(params.tenant);
  
  if (!tenant) {
    notFound();
  }

  return (
    <div className="tenant-container" data-tenant={tenant.slug}>
      <header className="tenant-header">
        <h1>{tenant.name}</h1>
      </header>
      <main className="tenant-main">
        {children}
      </main>
    </div>
  );
}
```

### Step 4: Quick Dashboard Page
```typescript
// app/[tenant]/dashboard/page.tsx
import { getCurrentUser } from '@/lib/auth';
import { getAnalytics } from '@/lib/analytics';
import { AnalyticsDashboard } from '@/components/dashboard/AnalyticsDashboard';

export default async function DashboardPage({ 
  params 
}: { 
  params: { tenant: string } 
}) {
  const user = await getCurrentUser();
  const analytics = await getAnalytics(params.tenant);

  return (
    <div className="dashboard-container">
      <h1>Welcome, {user.name}</h1>
      <AnalyticsDashboard data={analytics} tenant={params.tenant} />
    </div>
  );
}
```

---

## 📖 Complete Implementation Guide

### Phase 1: Enterprise Architecture Setup

#### 1.1 Advanced Project Structure
```
enterprise-saas-platform/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx
│   ├── [tenant]/
│   │   ├── dashboard/
│   │   ├── analytics/
│   │   ├── billing/
│   │   ├── settings/
│   │   └── layout.tsx
│   ├── api/
│   │   ├── auth/
│   │   ├── tenants/
│   │   ├── analytics/
│   │   ├── billing/
│   │   └── webhooks/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── dashboard/
│   ├── analytics/
│   ├── billing/
│   ├── ui/
│   └── tenant/
├── lib/
│   ├── auth/
│   ├── database/
│   ├── analytics/
│   ├── billing/
│   ├── cache/
│   └── utils/
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── middleware.ts
├── next.config.js
└── package.json
```

#### 1.2 Database Schema Design
```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Tenant {
  id          String   @id @default(cuid())
  slug        String   @unique
  name        String
  domain      String?  @unique
  customDomain String? @unique
  plan        String   @default("starter")
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  // Relations
  users       User[]
  analytics   AnalyticsData[]
  billing     BillingInfo?
  settings    TenantSettings?
  
  @@map("tenants")
}

model User {
  id          String   @id @default(cuid())
  email       String   @unique
  name        String?
  avatar      String?
  role        UserRole @default(USER)
  isActive    Boolean  @default(true)
  lastLoginAt DateTime?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  // Multi-tenancy
  tenantId    String
  tenant      Tenant   @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  
  // Auth
  accounts    Account[]
  sessions    Session[]
  
  @@map("users")
}

model AnalyticsData {
  id        String   @id @default(cuid())
  metric    String
  value     Float
  timestamp DateTime @default(now())
  metadata  Json?
  
  tenantId  String
  tenant    Tenant   @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  
  @@map("analytics_data")
}

model BillingInfo {
  id                String   @id @default(cuid())
  stripeCustomerId  String?  @unique
  subscriptionId    String?  @unique
  planId            String
  status            String
  currentPeriodEnd  DateTime?
  
  tenantId          String   @unique
  tenant            Tenant   @relation(fields: [tenantId], references: [id], onDelete: Cascade)
  
  @@map("billing_info")
}

enum UserRole {
  ADMIN
  USER
  VIEWER
}

// NextAuth.js required models
model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
  @@map("verification_tokens")
}
```

#### 1.3 Middleware for Tenant Resolution
```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';

export async function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  const hostname = req.headers.get('host') || '';
  
  // Extract potential tenant from subdomain or path
  const subdomain = hostname.split('.')[0];
  const pathTenant = url.pathname.split('/')[1];
  
  // Custom domain handling
  if (hostname !== 'localhost:3000' && hostname !== 'yourdomain.com') {
    // This is a custom domain, resolve tenant
    const tenant = await resolveTenantByDomain(hostname);
    if (tenant) {
      url.pathname = `/${tenant.slug}${url.pathname}`;
      return NextResponse.rewrite(url);
    }
  }
  
  // Subdomain handling
  if (subdomain && subdomain !== 'www' && subdomain !== 'app') {
    url.pathname = `/${subdomain}${url.pathname}`;
    return NextResponse.rewrite(url);
  }
  
  // Authentication check for protected routes
  if (url.pathname.startsWith('/api/') || url.pathname.includes('/dashboard')) {
    const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET });
    
    if (!token) {
      url.pathname = '/login';
      return NextResponse.redirect(url);
    }
  }
  
  // Rate limiting for API routes
  if (url.pathname.startsWith('/api/')) {
    const rateLimitResult = await checkRateLimit(req);
    if (!rateLimitResult.success) {
      return new NextResponse('Rate limit exceeded', { status: 429 });
    }
  }
  
  return NextResponse.next();
}

async function resolveTenantByDomain(domain: string) {
  // Implementation to resolve tenant by custom domain
  // This would typically query your database
  try {
    const response = await fetch(`${process.env.NEXTAUTH_URL}/api/tenants/resolve?domain=${domain}`);
    return response.ok ? await response.json() : null;
  } catch {
    return null;
  }
}

async function checkRateLimit(req: NextRequest) {
  // Implement rate limiting logic
  // You could use Redis, Upstash, or any other rate limiting service
  return { success: true };
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
};
```

### Phase 2: Advanced Next.js Features

#### 2.1 Server-Side Rendering with Data Fetching
```typescript
// app/[tenant]/analytics/page.tsx
import { Suspense } from 'react';
import { Metadata } from 'next';
import { getTenantBySlug } from '@/lib/tenants';
import { getAnalyticsData } from '@/lib/analytics';
import { AnalyticsCharts } from '@/components/analytics/AnalyticsCharts';
import { AnalyticsSkeleton } from '@/components/analytics/AnalyticsSkeleton';

interface AnalyticsPageProps {
  params: { tenant: string };
  searchParams: { 
    period?: string; 
    metric?: string; 
  };
}

export async function generateMetadata({ 
  params 
}: AnalyticsPageProps): Promise<Metadata> {
  const tenant = await getTenantBySlug(params.tenant);
  
  return {
    title: `Analytics - ${tenant?.name || 'Dashboard'}`,
    description: `Advanced analytics dashboard for ${tenant?.name}`,
    openGraph: {
      title: `${tenant?.name} Analytics`,
      description: 'Real-time business analytics and insights',
      images: [`/api/og?tenant=${params.tenant}&page=analytics`],
    },
  };
}

export default async function AnalyticsPage({ 
  params, 
  searchParams 
}: AnalyticsPageProps) {
  const tenant = await getTenantBySlug(params.tenant);
  
  if (!tenant) {
    return <div>Tenant not found</div>;
  }

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        <p className="text-gray-600">
          Real-time insights for {tenant.name}
        </p>
      </div>
      
      <Suspense fallback={<AnalyticsSkeleton />}>
        <AnalyticsContent 
          tenantId={tenant.id}
          period={searchParams.period || '7d'}
          metric={searchParams.metric}
        />
      </Suspense>
    </div>
  );
}

async function AnalyticsContent({ 
  tenantId, 
  period, 
  metric 
}: {
  tenantId: string;
  period: string;
  metric?: string;
}) {
  const analyticsData = await getAnalyticsData(tenantId, {
    period,
    metric,
  });

  return (
    <div className="analytics-content">
      <AnalyticsCharts 
        data={analyticsData}
        period={period}
        selectedMetric={metric}
      />
    </div>
  );
}
```

#### 2.2 Incremental Static Regeneration (ISR)
```typescript
// app/[tenant]/reports/[reportId]/page.tsx
import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getReport, getReportsList } from '@/lib/reports';
import { ReportViewer } from '@/components/reports/ReportViewer';

interface ReportPageProps {
  params: { 
    tenant: string; 
    reportId: string; 
  };
}

export async function generateStaticParams() {
  // Generate static params for popular reports
  const popularReports = await getReportsList({ popular: true, limit: 100 });
  
  return popularReports.map((report) => ({
    tenant: report.tenantSlug,
    reportId: report.id,
  }));
}

export const revalidate = 3600; // Revalidate every hour

export async function generateMetadata({ 
  params 
}: ReportPageProps): Promise<Metadata> {
  const report = await getReport(params.reportId, params.tenant);
  
  if (!report) {
    return {
      title: 'Report Not Found',
    };
  }

  return {
    title: `${report.title} - ${report.tenant.name}`,
    description: report.description,
    openGraph: {
      title: report.title,
      description: report.description,
      images: [`/api/og/report?id=${report.id}`],
    },
  };
}

export default async function ReportPage({ params }: ReportPageProps) {
  const report = await getReport(params.reportId, params.tenant);
  
  if (!report) {
    notFound();
  }

  return (
    <div className="report-page">
      <div className="report-header">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold">{report.title}</h1>
            <p className="text-gray-600">{report.description}</p>
          </div>
          <div className="report-actions">
            <button className="btn-export">Export PDF</button>
            <button className="btn-share">Share</button>
          </div>
        </div>
      </div>
      
      <ReportViewer 
        report={report}
        tenant={params.tenant}
      />
    </div>
  );
}
```

#### 2.3 Advanced API Routes with Middleware
```typescript
// app/api/tenants/[tenantId]/analytics/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { getAnalyticsData } from '@/lib/analytics';
import { rateLimit } from '@/lib/rate-limit';
import { validateTenantAccess } from '@/lib/auth/validation';

export async function GET(
  req: NextRequest,
  { params }: { params: { tenantId: string } }
) {
  try {
    // Rate limiting
    const rateLimitResult = await rateLimit(req);
    if (!rateLimitResult.success) {
      return NextResponse.json(
        { error: 'Rate limit exceeded' },
        { status: 429 }
      );
    }

    // Authentication
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Authorization - check tenant access
    const hasAccess = await validateTenantAccess(
      session.user.id,
      params.tenantId
    );
    
    if (!hasAccess) {
      return NextResponse.json(
        { error: 'Forbidden' },
        { status: 403 }
      );
    }

    // Extract query parameters
    const { searchParams } = new URL(req.url);
    const period = searchParams.get('period') || '7d';
    const metrics = searchParams.get('metrics')?.split(',') || [];
    const timezone = searchParams.get('timezone') || 'UTC';

    // Fetch analytics data
    const analyticsData = await getAnalyticsData(params.tenantId, {
      period,
      metrics,
      timezone,
      userId: session.user.id,
    });

    // Set cache headers
    const cacheHeaders = {
      'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
      'CDN-Cache-Control': 'public, s-maxage=300',
      'Vercel-CDN-Cache-Control': 'public, s-maxage=300',
    };

    return NextResponse.json(analyticsData, {
      headers: cacheHeaders,
    });

  } catch (error) {
    console.error('Analytics API error:', error);
    
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

export async function POST(
  req: NextRequest,
  { params }: { params: { tenantId: string } }
) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Validate request body
    const body = await req.json();
    const { metric, value, timestamp, metadata } = body;

    if (!metric || value === undefined) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Record analytics event
    const event = await recordAnalyticsEvent({
      tenantId: params.tenantId,
      metric,
      value,
      timestamp: timestamp || new Date(),
      metadata,
      userId: session.user.id,
    });

    return NextResponse.json(event, { status: 201 });

  } catch (error) {
    console.error('Analytics recording error:', error);
    
    return NextResponse.json(
      { error: 'Failed to record analytics event' },
      { status: 500 }
    );
  }
}
```

### Phase 3: Multi-Tenant Architecture

#### 3.1 Tenant Service Implementation
```typescript
// lib/tenants/service.ts
import { PrismaClient } from '@prisma/client';
import { cache } from 'react';
import { redis } from '@/lib/cache/redis';

const prisma = new PrismaClient();

export const getTenantBySlug = cache(async (slug: string) => {
  // Try cache first
  const cacheKey = `tenant:slug:${slug}`;
  const cached = await redis.get(cacheKey);
  
  if (cached) {
    return JSON.parse(cached);
  }

  // Fetch from database
  const tenant = await prisma.tenant.findUnique({
    where: { slug },
    include: {
      settings: true,
      billing: true,
    },
  });

  if (tenant) {
    // Cache for 5 minutes
    await redis.setex(cacheKey, 300, JSON.stringify(tenant));
  }

  return tenant;
});

export const getTenantByDomain = cache(async (domain: string) => {
  const cacheKey = `tenant:domain:${domain}`;
  const cached = await redis.get(cacheKey);
  
  if (cached) {
    return JSON.parse(cached);
  }

  const tenant = await prisma.tenant.findFirst({
    where: {
      OR: [
        { domain },
        { customDomain: domain },
      ],
    },
    include: {
      settings: true,
      billing: true,
    },
  });

  if (tenant) {
    await redis.setex(cacheKey, 300, JSON.stringify(tenant));
  }

  return tenant;
});

export async function createTenant(data: {
  name: string;
  slug: string;
  domain?: string;
  plan?: string;
  ownerId: string;
}) {
  const tenant = await prisma.$transaction(async (tx) => {
    // Create tenant
    const newTenant = await tx.tenant.create({
      data: {
        name: data.name,
        slug: data.slug,
        domain: data.domain,
        plan: data.plan || 'starter',
      },
    });

    // Create owner user
    await tx.user.create({
      data: {
        id: data.ownerId,
        tenantId: newTenant.id,
        role: 'ADMIN',
      },
    });

    // Initialize tenant settings
    await tx.tenantSettings.create({
      data: {
        tenantId: newTenant.id,
        theme: 'default',
        features: ['analytics', 'billing'],
      },
    });

    return newTenant;
  });

  // Invalidate cache
  await redis.del(`tenant:slug:${data.slug}`);
  
  return tenant;
}

export async function updateTenant(
  tenantId: string,
  data: Partial<{
    name: string;
    domain: string;
    customDomain: string;
    plan: string;
    isActive: boolean;
  }>
) {
  const tenant = await prisma.tenant.update({
    where: { id: tenantId },
    data,
    include: {
      settings: true,
      billing: true,
    },
  });

  // Invalidate relevant caches
  await redis.del(`tenant:slug:${tenant.slug}`);
  if (tenant.domain) {
    await redis.del(`tenant:domain:${tenant.domain}`);
  }
  if (tenant.customDomain) {
    await redis.del(`tenant:domain:${tenant.customDomain}`);
  }

  return tenant;
}
```

#### 3.2 Tenant Context Provider
```typescript
// components/tenant/TenantProvider.tsx
'use client';

import React, { createContext, useContext, ReactNode } from 'react';

interface Tenant {
  id: string;
  slug: string;
  name: string;
  domain?: string;
  customDomain?: string;
  plan: string;
  isActive: boolean;
  settings?: {
    theme: string;
    features: string[];
  };
  billing?: {
    status: string;
    planId: string;
    currentPeriodEnd?: Date;
  };
}

interface TenantContextType {
  tenant: Tenant;
  isOwner: boolean;
  hasFeature: (feature: string) => boolean;
  canAccess: (resource: string) => boolean;
}

const TenantContext = createContext<TenantContextType | null>(null);

interface TenantProviderProps {
  children: ReactNode;
  tenant: Tenant;
  userRole: string;
  userId: string;
}

export function TenantProvider({ 
  children, 
  tenant, 
  userRole, 
  userId 
}: TenantProviderProps) {
  const isOwner = userRole === 'ADMIN';
  
  const hasFeature = (feature: string): boolean => {
    if (!tenant.settings?.features) return false;
    return tenant.settings.features.includes(feature);
  };

  const canAccess = (resource: string): boolean => {
    // Implement role-based access control
    const permissions = getPermissions(userRole, tenant.plan);
    return permissions.includes(resource);
  };

  const contextValue: TenantContextType = {
    tenant,
    isOwner,
    hasFeature,
    canAccess,
  };

  return (
    <TenantContext.Provider value={contextValue}>
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);
  
  if (!context) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  
  return context;
}

function getPermissions(role: string, plan: string): string[] {
  const basePermissions = ['read:dashboard', 'read:analytics'];
  
  if (role === 'ADMIN') {
    return [
      ...basePermissions,
      'write:settings',
      'manage:users',
      'manage:billing',
      'delete:data',
    ];
  }
  
  if (role === 'USER') {
    return [
      ...basePermissions,
      'write:content',
      'read:reports',
    ];
  }
  
  return basePermissions; // VIEWER role
}
```

### Phase 4: Advanced Analytics Implementation

#### 4.1 Real-time Analytics Service
```typescript
// lib/analytics/service.ts
import { PrismaClient } from '@prisma/client';
import { redis } from '@/lib/cache/redis';
import { EventEmitter } from 'events';

const prisma = new PrismaClient();
const analyticsEmitter = new EventEmitter();

export interface AnalyticsEvent {
  tenantId: string;
  metric: string;
  value: number;
  timestamp: Date;
  metadata?: Record<string, any>;
  userId?: string;
}

export interface AnalyticsQuery {
  tenantId: string;
  period: string;
  metrics?: string[];
  timezone?: string;
  groupBy?: string;
  filters?: Record<string, any>;
}

export class AnalyticsService {
  static async recordEvent(event: AnalyticsEvent) {
    try {
      // Store in database
      const record = await prisma.analyticsData.create({
        data: {
          tenantId: event.tenantId,
          metric: event.metric,
          value: event.value,
          timestamp: event.timestamp,
          metadata: event.metadata || {},
        },
      });

      // Update real-time cache
      await this.updateRealtimeMetrics(event);

      // Emit real-time event
      analyticsEmitter.emit('new-event', event);

      return record;
    } catch (error) {
      console.error('Failed to record analytics event:', error);
      throw error;
    }
  }

  static async getAnalyticsData(query: AnalyticsQuery) {
    const { tenantId, period, metrics = [], timezone = 'UTC' } = query;
    
    // Generate cache key
    const cacheKey = `analytics:${tenantId}:${period}:${metrics.join(',')}:${timezone}`;
    
    // Try cache first
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Calculate time range
    const timeRange = this.calculateTimeRange(period, timezone);
    
    // Build query
    const whereClause = {
      tenantId,
      timestamp: {
        gte: timeRange.start,
        lte: timeRange.end,
      },
      ...(metrics.length > 0 && { metric: { in: metrics } }),
    };

    // Fetch data
    const data = await prisma.analyticsData.findMany({
      where: whereClause,
      orderBy: { timestamp: 'asc' },
    });

    // Process and aggregate data
    const processedData = this.processAnalyticsData(data, query);

    // Cache for 5 minutes
    await redis.setex(cacheKey, 300, JSON.stringify(processedData));

    return processedData;
  }

  static async getRealtimeMetrics(tenantId: string) {
    const cacheKey = `realtime:${tenantId}`;
    const cached = await redis.get(cacheKey);
    
    if (cached) {
      return JSON.parse(cached);
    }

    // If no cached data, generate initial metrics
    const initialMetrics = await this.generateInitialMetrics(tenantId);
    await redis.setex(cacheKey, 60, JSON.stringify(initialMetrics));
    
    return initialMetrics;
  }

  private static async updateRealtimeMetrics(event: AnalyticsEvent) {
    const cacheKey = `realtime:${event.tenantId}`;
    const current = await redis.get(cacheKey);
    
    let metrics = current ? JSON.parse(current) : {};
    
    // Update metrics based on event
    if (!metrics[event.metric]) {
      metrics[event.metric] = { count: 0, sum: 0, avg: 0 };
    }
    
    metrics[event.metric].count += 1;
    metrics[event.metric].sum += event.value;
    metrics[event.metric].avg = metrics[event.metric].sum / metrics[event.metric].count;
    metrics[event.metric].lastUpdated = new Date().toISOString();
    
    await redis.setex(cacheKey, 300, JSON.stringify(metrics));
  }

  private static calculateTimeRange(period: string, timezone: string) {
    const now = new Date();
    let start: Date;
    
    switch (period) {
      case '1h':
        start = new Date(now.getTime() - 60 * 60 * 1000);
        break;
      case '24h':
        start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case '7d':
        start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      default:
        start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    }
    
    return { start, end: now };
  }

  private static processAnalyticsData(
    data: any[], 
    query: AnalyticsQuery
  ) {
    // Group data by time intervals
    const grouped = this.groupByTimeInterval(data, query.period);
    
    // Calculate aggregations
    const metrics = this.calculateMetrics(grouped);
    
    // Generate insights
    const insights = this.generateInsights(metrics, query);
    
    return {
      metrics,
      insights,
      timeRange: this.calculateTimeRange(query.period, query.timezone!),
      generatedAt: new Date().toISOString(),
    };
  }

  private static groupByTimeInterval(data: any[], period: string) {
    // Implementation for grouping data by time intervals
    // This would create buckets based on the period (hourly, daily, etc.)
    const buckets = new Map();
    
    data.forEach(item => {
      const bucketKey = this.getBucketKey(item.timestamp, period);
      if (!buckets.has(bucketKey)) {
        buckets.set(bucketKey, []);
      }
      buckets.get(bucketKey).push(item);
    });
    
    return buckets;
  }

  private static getBucketKey(timestamp: Date, period: string): string {
    const date = new Date(timestamp);
    
    switch (period) {
      case '1h':
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
      case '24h':
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}-${date.getHours()}`;
      case '7d':
      case '30d':
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
      default:
        return date.toISOString();
    }
  }

  private static calculateMetrics(grouped: Map<string, any[]>) {
    const metrics: Record<string, any> = {};
    
    grouped.forEach((items, timeKey) => {
      metrics[timeKey] = {
        timestamp: timeKey,
        total: items.length,
        sum: items.reduce((acc, item) => acc + item.value, 0),
        avg: items.reduce((acc, item) => acc + item.value, 0) / items.length,
        min: Math.min(...items.map(item => item.value)),
        max: Math.max(...items.map(item => item.value)),
      };
    });
    
    return metrics;
  }

  private static generateInsights(metrics: Record<string, any>, query: AnalyticsQuery) {
    // Generate AI-powered insights based on the data patterns
    const insights = [];
    
    const values = Object.values(metrics).map((m: any) => m.sum);
    const trend = this.calculateTrend(values);
    
    if (trend > 0.1) {
      insights.push({
        type: 'positive_trend',
        message: `${query.metrics?.[0] || 'Metrics'} showing strong upward trend (+${(trend * 100).toFixed(1)}%)`,
        confidence: 0.85,
      });
    } else if (trend < -0.1) {
      insights.push({
        type: 'negative_trend',
        message: `${query.metrics?.[0] || 'Metrics'} showing downward trend (${(trend * 100).toFixed(1)}%)`,
        confidence: 0.85,
      });
    }
    
    return insights;
  }

  private static calculateTrend(values: number[]): number {
    if (values.length < 2) return 0;
    
    const firstHalf = values.slice(0, Math.floor(values.length / 2));
    const secondHalf = values.slice(Math.floor(values.length / 2));
    
    const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
    
    return (secondAvg - firstAvg) / firstAvg;
  }

  private static async generateInitialMetrics(tenantId: string) {
    // Generate initial real-time metrics for a tenant
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    
    const recentData = await prisma.analyticsData.findMany({
      where: {
        tenantId,
        timestamp: { gte: oneHourAgo },
      },
    });
    
    const metrics = {};
    recentData.forEach(item => {
      if (!metrics[item.metric]) {
        metrics[item.metric] = { count: 0, sum: 0, avg: 0 };
      }
      metrics[item.metric].count += 1;
      metrics[item.metric].sum += item.value;
      metrics[item.metric].avg = metrics[item.metric].sum / metrics[item.metric].count;
    });
    
    return metrics;
  }
}

// Event emitter for real-time updates
export const onAnalyticsEvent = (callback: (event: AnalyticsEvent) => void) => {
  analyticsEmitter.on('new-event', callback);
  
  return () => {
    analyticsEmitter.off('new-event', callback);
  };
};
```

#### 4.2 Analytics Dashboard Components
```typescript
// components/analytics/AnalyticsDashboard.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useTenant } from '@/components/tenant/TenantProvider';
import { MetricsGrid } from './MetricsGrid';
import { AnalyticsChart } from './AnalyticsChart';
import { InsightsList } from './InsightsList';
import { RealtimeMetrics } from './RealtimeMetrics';
import { FilterPanel } from './FilterPanel';

interface AnalyticsDashboardProps {
  data: any;
  tenant: string;
}

export function AnalyticsDashboard({ data, tenant }: AnalyticsDashboardProps) {
  const { hasFeature } = useTenant();
  const [filters, setFilters] = useState({
    period: '7d',
    metrics: ['users', 'revenue', 'sessions'],
    timezone: 'UTC',
  });
  
  const [realtimeData, setRealtimeData] = useState(null);
  const [insights, setInsights] = useState(data.insights);

  // Real-time updates
  useEffect(() => {
    if (!hasFeature('realtime-analytics')) return;

    const fetchRealtimeData = async () => {
      try {
        const response = await fetch(`/api/tenants/${tenant}/analytics/realtime`);
        const data = await response.json();
        setRealtimeData(data);
      } catch (error) {
        console.error('Failed to fetch realtime data:', error);
      }
    };

    fetchRealtimeData();
    const interval = setInterval(fetchRealtimeData, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [tenant, hasFeature]);

  const handleFilterChange = async (newFilters: any) => {
    setFilters(newFilters);
    
    // Fetch new data with updated filters
    try {
      const params = new URLSearchParams(newFilters);
      const response = await fetch(`/api/tenants/${tenant}/analytics?${params}`);
      const updatedData = await response.json();
      setInsights(updatedData.insights);
    } catch (error) {
      console.error('Failed to update analytics data:', error);
    }
  };

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        
        <FilterPanel 
          filters={filters}
          onChange={handleFilterChange}
        />
      </div>

      {hasFeature('realtime-analytics') && realtimeData && (
        <div className="realtime-section">
          <h3 className="text-lg font-semibold mb-4">Real-time Metrics</h3>
          <RealtimeMetrics data={realtimeData} />
        </div>
      )}

      <div className="metrics-section">
        <MetricsGrid metrics={data.metrics} />
      </div>

      <div className="charts-section">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AnalyticsChart 
            data={data.metrics}
            type="line"
            title="Trend Analysis"
            metric={filters.metrics[0]}
          />
          
          <AnalyticsChart 
            data={data.metrics}
            type="bar"
            title="Comparison"
            metric={filters.metrics[1]}
          />
        </div>
      </div>

      {hasFeature('ai-insights') && (
        <div className="insights-section">
          <h3 className="text-lg font-semibold mb-4">AI-Powered Insights</h3>
          <InsightsList insights={insights} />
        </div>
      )}
    </div>
  );
}
```

### Phase 5: Billing Integration with Stripe

#### 5.1 Stripe Integration Service
```typescript
// lib/billing/stripe.ts
import Stripe from 'stripe';
import { PrismaClient } from '@prisma/client';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

const prisma = new PrismaClient();

export class BillingService {
  static async createCustomer(tenantId: string, email: string, name: string) {
    try {
      const customer = await stripe.customers.create({
        email,
        name,
        metadata: {
          tenantId,
        },
      });

      // Update tenant with Stripe customer ID
      await prisma.billingInfo.upsert({
        where: { tenantId },
        create: {
          tenantId,
          stripeCustomerId: customer.id,
          planId: 'starter',
          status: 'inactive',
        },
        update: {
          stripeCustomerId: customer.id,
        },
      });

      return customer;
    } catch (error) {
      console.error('Failed to create Stripe customer:', error);
      throw error;
    }
  }

  static async createSubscription(
    tenantId: string,
    priceId: string,
    customerId?: string
  ) {
    try {
      const billing = await prisma.billingInfo.findUnique({
        where: { tenantId },
      });

      if (!billing?.stripeCustomerId && !customerId) {
        throw new Error('No Stripe customer found for tenant');
      }

      const subscription = await stripe.subscriptions.create({
        customer: customerId || billing!.stripeCustomerId!,
        items: [{ price: priceId }],
        payment_behavior: 'default_incomplete',
        payment_settings: { save_default_payment_method: 'on_subscription' },
        expand: ['latest_invoice.payment_intent'],
      });

      // Update billing info
      await prisma.billingInfo.update({
        where: { tenantId },
        data: {
          subscriptionId: subscription.id,
          planId: priceId,
          status: subscription.status,
          currentPeriodEnd: new Date(subscription.current_period_end * 1000),
        },
      });

      return subscription;
    } catch (error) {
      console.error('Failed to create subscription:', error);
      throw error;
    }
  }

  static async updateSubscription(tenantId: string, newPriceId: string) {
    try {
      const billing = await prisma.billingInfo.findUnique({
        where: { tenantId },
      });

      if (!billing?.subscriptionId) {
        throw new Error('No subscription found for tenant');
      }

      const subscription = await stripe.subscriptions.retrieve(billing.subscriptionId);
      
      const updatedSubscription = await stripe.subscriptions.update(billing.subscriptionId, {
        items: [{
          id: subscription.items.data[0].id,
          price: newPriceId,
        }],
        proration_behavior: 'create_prorations',
      });

      // Update billing info
      await prisma.billingInfo.update({
        where: { tenantId },
        data: {
          planId: newPriceId,
          status: updatedSubscription.status,
          currentPeriodEnd: new Date(updatedSubscription.current_period_end * 1000),
        },
      });

      return updatedSubscription;
    } catch (error) {
      console.error('Failed to update subscription:', error);
      throw error;
    }
  }

  static async cancelSubscription(tenantId: string, immediately = false) {
    try {
      const billing = await prisma.billingInfo.findUnique({
        where: { tenantId },
      });

      if (!billing?.subscriptionId) {
        throw new Error('No subscription found for tenant');
      }

      const subscription = immediately
        ? await stripe.subscriptions.cancel(billing.subscriptionId)
        : await stripe.subscriptions.update(billing.subscriptionId, {
            cancel_at_period_end: true,
          });

      // Update billing info
      await prisma.billingInfo.update({
        where: { tenantId },
        data: {
          status: subscription.status,
        },
      });

      return subscription;
    } catch (error) {
      console.error('Failed to cancel subscription:', error);
      throw error;
    }
  }

  static async handleWebhook(event: Stripe.Event) {
    try {
      switch (event.type) {
        case 'customer.subscription.created':
        case 'customer.subscription.updated':
          await this.handleSubscriptionUpdate(event.data.object as Stripe.Subscription);
          break;
        
        case 'customer.subscription.deleted':
          await this.handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
          break;
        
        case 'invoice.payment_succeeded':
          await this.handlePaymentSucceeded(event.data.object as Stripe.Invoice);
          break;
        
        case 'invoice.payment_failed':
          await this.handlePaymentFailed(event.data.object as Stripe.Invoice);
          break;
      }
    } catch (error) {
      console.error('Webhook handling error:', error);
      throw error;
    }
  }

  private static async handleSubscriptionUpdate(subscription: Stripe.Subscription) {
    const customerId = subscription.customer as string;
    
    // Find tenant by customer ID
    const billing = await prisma.billingInfo.findFirst({
      where: { stripeCustomerId: customerId },
    });

    if (!billing) {
      console.error('No billing info found for customer:', customerId);
      return;
    }

    await prisma.billingInfo.update({
      where: { id: billing.id },
      data: {
        subscriptionId: subscription.id,
        status: subscription.status,
        currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      },
    });

    // Update tenant status based on subscription
    await prisma.tenant.update({
      where: { id: billing.tenantId },
      data: {
        isActive: subscription.status === 'active',
      },
    });
  }

  private static async handleSubscriptionDeleted(subscription: Stripe.Subscription) {
    const customerId = subscription.customer as string;
    
    const billing = await prisma.billingInfo.findFirst({
      where: { stripeCustomerId: customerId },
    });

    if (!billing) return;

    await prisma.billingInfo.update({
      where: { id: billing.id },
      data: {
        status: 'canceled',
        subscriptionId: null,
      },
    });

    // Deactivate tenant
    await prisma.tenant.update({
      where: { id: billing.tenantId },
      data: { isActive: false },
    });
  }

  private static async handlePaymentSucceeded(invoice: Stripe.Invoice) {
    // Handle successful payment - maybe send confirmation email
    console.log(`Payment succeeded for invoice ${invoice.id}`);
  }

  private static async handlePaymentFailed(invoice: Stripe.Invoice) {
    // Handle failed payment - maybe send dunning email
    console.error(`Payment failed for invoice ${invoice.id}`);
  }

  static async getUsageStats(tenantId: string) {
    // Get current usage statistics for billing purposes
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);

    const usage = await prisma.analyticsData.groupBy({
      by: ['metric'],
      where: {
        tenantId,
        timestamp: { gte: oneMonthAgo },
      },
      _count: { metric: true },
      _sum: { value: true },
    });

    return usage.reduce((acc, item) => {
      acc[item.metric] = {
        count: item._count.metric,
        total: item._sum.value || 0,
      };
      return acc;
    }, {} as Record<string, { count: number; total: number }>);
  }
}
```

#### 5.2 Billing API Routes
```typescript
// app/api/billing/create-subscription/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { BillingService } from '@/lib/billing/stripe';
import { validateTenantAccess } from '@/lib/auth/validation';

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { tenantId, priceId } = await req.json();

    // Validate access
    const hasAccess = await validateTenantAccess(session.user.id, tenantId);
    if (!hasAccess) {
      return NextResponse.json(
        { error: 'Forbidden' },
        { status: 403 }
      );
    }

    // Create subscription
    const subscription = await BillingService.createSubscription(
      tenantId,
      priceId
    );

    return NextResponse.json({
      subscriptionId: subscription.id,
      clientSecret: subscription.latest_invoice?.payment_intent?.client_secret,
    });
  } catch (error) {
    console.error('Subscription creation error:', error);
    return NextResponse.json(
      { error: 'Failed to create subscription' },
      { status: 500 }
    );
  }
}
```

```typescript
// app/api/billing/webhook/route.ts
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { BillingService } from '@/lib/billing/stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export async function POST(req: NextRequest) {
  const sig = req.headers.get('stripe-signature')!;
  const body = await req.text();

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return NextResponse.json(
      { error: 'Invalid signature' },
      { status: 400 }
    );
  }

  try {
    await BillingService.handleWebhook(event);
    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Webhook handling error:', error);
    return NextResponse.json(
      { error: 'Webhook handling failed' },
      { status: 500 }
    );
  }
}
```

---

## 🧪 Testing Your Implementation

### Testing Checklist

#### Next.js Features ✅
- [ ] SSR pages load correctly with proper SEO metadata
- [ ] ISR pages regenerate and cache appropriately
- [ ] API routes handle authentication and rate limiting
- [ ] Middleware performs tenant resolution correctly

#### Multi-Tenancy ✅  
- [ ] Tenant isolation is properly enforced
- [ ] Custom domains resolve to correct tenants
- [ ] Subdomain routing works correctly
- [ ] Data segregation is maintained across tenants

#### Authentication & Authorization ✅
- [ ] NextAuth.js authentication flows work properly
- [ ] Role-based access control is enforced
- [ ] Tenant-level permissions function correctly
- [ ] Session management is secure

#### Analytics & Performance ✅
- [ ] Real-time analytics update correctly
- [ ] Caching strategies improve performance
- [ ] Database queries are optimized
- [ ] Error handling is comprehensive

#### Billing Integration ✅
- [ ] Stripe integration handles all subscription flows
- [ ] Webhooks process events correctly
- [ ] Usage tracking is accurate
- [ ] Payment failures are handled gracefully

---

## 🎯 Learning Objectives

### After completing this project, you should understand:

1. **Next.js Mastery**
   - Advanced routing with App Router
   - SSR, SSG, and ISR implementation
   - API routes with middleware
   - Performance optimization techniques

2. **Enterprise Architecture**
   - Multi-tenant application design
   - Scalable database architecture
   - Caching strategies
   - Security best practices

3. **Advanced React Patterns**
   - Server Components vs Client Components
   - Context providers for global state
   - Error boundaries and suspense
   - Performance optimization with React

4. **Production Deployment**
   - Environment configuration
   - Database migrations
   - Monitoring and analytics
   - CI/CD pipeline setup

5. **Business Logic Integration**
   - Payment processing with Stripe
   - Real-time analytics
   - User management systems
   - Feature flag implementation

---

## 🚀 Next Steps

### Recommended Enhancements

1. **Add Monitoring & Observability**
   ```bash
   npm install @vercel/analytics @sentry/nextjs
   ```

2. **Implement Advanced Caching**
   ```bash
   npm install ioredis @upstash/redis
   ```

3. **Add Real-time Features**
   ```bash
   npm install pusher-js @pusher/pusher-http-node
   ```

4. **Enhanced Security**
   ```bash
   npm install helmet rate-limiter-flexible
   ```

5. **Performance Monitoring**
   ```bash
   npm install @vercel/speed-insights web-vitals
   ```

### Production Deployment

1. **Environment Setup**
   - Configure production database
   - Set up Redis for caching
   - Configure Stripe webhook endpoints
   - Set up monitoring and logging

2. **Performance Optimization**
   - Implement CDN for static assets
   - Optimize database indexes
   - Set up proper caching headers
   - Implement image optimization

3. **Security Hardening**
   - Enable HTTPS everywhere
   - Implement proper CORS policies
   - Set up rate limiting
   - Configure security headers

### Continue Learning

- **Expert Project 2**: React Native Cross-Platform Ecosystem
- **Expert Project 3**: GraphQL Real-time Collaboration Platform
- **Expert Project 4**: AI-Powered React Application
- **Expert Project 5**: Open Source Component Library

---

## 📚 Additional Resources

### Next.js Advanced
- [Next.js Documentation](https://nextjs.org/docs)
- [React Server Components](https://react.dev/blog/2020/12/21/data-fetching-with-react-server-components)
- [Next.js Performance](https://nextjs.org/docs/advanced-features/measuring-performance)

### Enterprise Architecture
- [Multi-tenant SaaS Architecture](https://docs.aws.amazon.com/whitepapers/latest/saas-architecture-fundamentals/multi-tenant-saas-architecture.html)
- [Database Design Patterns](https://microservices.io/patterns/data/)
- [Caching Strategies](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/welcome.html)

### Billing & Payments
- [Stripe Documentation](https://stripe.com/docs)
- [SaaS Metrics Guide](https://stripe.com/guides/saas-metrics)
- [Subscription Billing Best Practices](https://stripe.com/guides/billing)

---

**Continue to**: [Expert Project 2: React Native Cross-Platform](./02-React-Native-Cross-Platform-Implementation.md)