# 🚀 Expert React Projects

> **Level**: Expert (Weeks 13-20)  
> **Prerequisites**: Advanced projects completed, production experience  
> **Focus**: Enterprise-scale applications, complex systems architecture, and cutting-edge React features

---

## 📋 Project Overview

These expert-level projects represent real-world, enterprise-scale applications that demonstrate mastery of React and modern web development practices. Each project could serve as a portfolio centerpiece or production application.

### Learning Progression
```
Project 1: Next.js Enterprise Platform → Full-stack framework mastery
Project 2: React Native Cross-Platform → Mobile development expertise
Project 3: GraphQL & Real-time Systems → Advanced data layer architecture
Project 4: AI-Powered React Application → Machine learning integration
Project 5: Open Source Component Library → Community contribution and design systems
```

---

## 🌟 Project 1: Next.js Enterprise SaaS Platform

### Objective
Build a complete enterprise SaaS platform using Next.js with advanced features like SSR, ISR, API routes, and multi-tenancy.

### Skills Practiced
- Next.js advanced patterns (SSR, SSG, ISR)
- Server-side rendering optimization
- API routes and middleware
- Multi-tenant architecture
- SEO optimization
- Performance monitoring

### Requirements
```jsx
// Enterprise SaaS architecture
<SaaSPlatform>
  <TenantResolver />
  <AuthenticationGate>
    <DashboardLayout>
      <Navigation />
      <MainContent>
        <AnalyticsDashboard />
        <UserManagement />
        <BillingSystem />
        <SettingsPanel />
      </MainContent>
    </DashboardLayout>
  </AuthenticationGate>
</SaaSPlatform>
```

### Features to Implement
- [x] Multi-tenant architecture with domain routing
- [x] Server-side authentication with NextAuth.js
- [x] Incremental Static Regeneration for dynamic content
- [x] API routes with middleware and rate limiting
- [x] Advanced SEO with dynamic meta tags
- [x] Billing integration with Stripe
- [x] Real-time notifications with WebSockets
- [x] Advanced analytics and monitoring
- [x] Progressive Web App features
- [x] Advanced caching strategies

### Project Structure
```
nextjs-saas-platform/
├── pages/
│   ├── api/
│   │   ├── auth/
│   │   ├── tenants/
│   │   ├── billing/
│   │   └── analytics/
│   ├── dashboard/
│   │   ├── [tenant]/
│   │   │   ├── index.js
│   │   │   ├── analytics.js
│   │   │   ├── users.js
│   │   │   └── settings.js
│   │   └── index.js
│   ├── _app.js
│   ├── _document.js
│   └── index.js
├── components/
│   ├── Dashboard/
│   ├── Auth/
│   ├── Billing/
│   ├── Analytics/
│   └── Layout/
├── lib/
│   ├── auth.js
│   ├── database.js
│   ├── stripe.js
│   ├── analytics.js
│   └── middleware.js
├── hooks/
│   ├── useAuth.js
│   ├── useTenant.js
│   ├── useAnalytics.js
│   └── useBilling.js
├── utils/
│   ├── seo.js
│   ├── performance.js
│   └── validation.js
├── middleware.js
├── next.config.js
└── package.json
```

### Advanced Next.js Implementation
```jsx
// middleware.js - Tenant resolution and authentication
import { NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';

export async function middleware(request) {
  const { pathname } = request.nextUrl;
  
  // Extract tenant from subdomain or path
  const tenant = extractTenant(request);
  
  // Handle tenant resolution
  if (pathname.startsWith('/dashboard')) {
    if (!tenant) {
      return NextResponse.redirect(new URL('/select-tenant', request.url));
    }
    
    // Verify tenant access
    const token = await getToken({ req: request });
    if (!token || !hasAccessToTenant(token, tenant)) {
      return NextResponse.redirect(new URL('/unauthorized', request.url));
    }
    
    // Add tenant to request headers
    const response = NextResponse.next();
    response.headers.set('x-tenant-id', tenant.id);
    return response;
  }
  
  return NextResponse.next();
}

// pages/dashboard/[tenant]/analytics.js - ISR with dynamic data
import { GetStaticProps, GetStaticPaths } from 'next';
import { AnalyticsDashboard } from '../../../components/Dashboard/AnalyticsDashboard';

export default function TenantAnalytics({ tenant, analyticsData, lastUpdated }) {
  return (
    <AnalyticsDashboard 
      tenant={tenant}
      data={analyticsData}
      lastUpdated={lastUpdated}
    />
  );
}

export const getStaticPaths: GetStaticPaths = async () => {
  // Generate paths for top tenants, others will be generated on-demand
  const topTenants = await getTopTenants(100);
  
  const paths = topTenants.map(tenant => ({
    params: { tenant: tenant.slug }
  }));
  
  return {
    paths,
    fallback: 'blocking' // ISR for other tenants
  };
};

export const getStaticProps: GetStaticProps = async ({ params }) => {
  try {
    const tenant = await getTenantBySlug(params.tenant);
    if (!tenant) {
      return { notFound: true };
    }
    
    const analyticsData = await getAnalyticsData(tenant.id);
    
    return {
      props: {
        tenant,
        analyticsData,
        lastUpdated: new Date().toISOString()
      },
      revalidate: 60 // Regenerate every minute
    };
  } catch (error) {
    return { notFound: true };
  }
};

// lib/analytics.js - Advanced analytics with caching
import { Redis } from 'ioredis';
import { createHash } from 'crypto';

const redis = new Redis(process.env.REDIS_URL);

export class AnalyticsService {
  static async getAnalyticsData(tenantId, dateRange, filters = {}) {
    const cacheKey = this.generateCacheKey(tenantId, dateRange, filters);
    
    // Try cache first
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }
    
    // Compute analytics
    const data = await this.computeAnalytics(tenantId, dateRange, filters);
    
    // Cache for 5 minutes
    await redis.setex(cacheKey, 300, JSON.stringify(data));
    
    return data;
  }
  
  static async computeAnalytics(tenantId, dateRange, filters) {
    // Parallel computation of different metrics
    const [
      userMetrics,
      revenueMetrics,
      engagementMetrics,
      conversionMetrics
    ] = await Promise.all([
      this.getUserMetrics(tenantId, dateRange, filters),
      this.getRevenueMetrics(tenantId, dateRange, filters),
      this.getEngagementMetrics(tenantId, dateRange, filters),
      this.getConversionMetrics(tenantId, dateRange, filters)
    ]);
    
    return {
      user: userMetrics,
      revenue: revenueMetrics,
      engagement: engagementMetrics,
      conversion: conversionMetrics,
      computedAt: new Date().toISOString()
    };
  }
}
```

### Assessment Criteria
- Multi-tenancy is properly implemented and secure ✅
- SSR/ISR performance is optimized ✅
- SEO implementation is comprehensive ✅
- Billing and payment integration works correctly ✅
- Application scales with increasing tenants ✅

---

## 📱 Project 2: React Native Cross-Platform Ecosystem

### Objective
Build a comprehensive cross-platform mobile application with React Native, sharing business logic with a React web application.

### Skills Practiced
- React Native development
- Code sharing between web and mobile
- Native module integration
- Performance optimization for mobile
- App store deployment

### Requirements
```jsx
// Cross-platform ecosystem
<MobileEcosystem>
  <SharedBusinessLogic>
    <WebApp />
    <MobileApp>
      <Navigation />
      <OfflineSupport />
      <PushNotifications />
      <CameraIntegration />
      <LocationServices />
    </MobileApp>
  </SharedBusinessLogic>
</MobileEcosystem>
```

### Features to Implement
- [x] Shared component library between web and mobile
- [x] Offline-first architecture with sync
- [x] Push notifications system
- [x] Camera and photo management
- [x] Location-based features
- [x] Biometric authentication
- [x] Background sync and tasks
- [x] Deep linking implementation
- [x] Performance monitoring
- [x] App store deployment automation

### Project Structure
```
cross-platform-ecosystem/
├── packages/
│   ├── shared/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── types/
│   ├── web/
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   ├── mobile/
│   │   ├── src/
│   │   ├── android/
│   │   ├── ios/
│   │   └── package.json
│   └── native-modules/
│       ├── biometric-auth/
│       └── background-sync/
├── tools/
│   ├── build-scripts/
│   └── deployment/
├── lerna.json
└── package.json
```

### React Native Implementation
```jsx
// packages/mobile/src/components/OfflineSync.jsx
import React, { useEffect, useRef } from 'react';
import { AppState } from 'react-native';
import NetInfo from '@react-native-async-storage/async-storage';
import { useOfflineSync } from '@shared/hooks/useOfflineSync';
import { SyncService } from '@shared/services/SyncService';

export const OfflineSync = ({ children }) => {
  const appState = useRef(AppState.currentState);
  const { 
    isOnline, 
    pendingSyncs, 
    syncData, 
    queueForSync 
  } = useOfflineSync();

  useEffect(() => {
    const handleAppStateChange = (nextAppState) => {
      if (appState.current.match(/inactive|background/) && 
          nextAppState === 'active') {
        // App came to foreground, attempt sync
        if (isOnline && pendingSyncs.length > 0) {
          syncData();
        }
      }
      appState.current = nextAppState;
    };

    const subscription = AppState.addEventListener(
      'change', 
      handleAppStateChange
    );

    return () => subscription?.remove();
  }, [isOnline, pendingSyncs, syncData]);

  // Background sync when app is backgrounded
  useEffect(() => {
    const handleBackground = async () => {
      if (pendingSyncs.length > 0) {
        // Start background task
        await SyncService.startBackgroundSync();
      }
    };

    const backgroundListener = AppState.addEventListener(
      'background', 
      handleBackground
    );

    return () => backgroundListener?.remove();
  }, [pendingSyncs]);

  return children;
};

// packages/mobile/src/services/LocationService.js
import Geolocation from '@react-native-community/geolocation';
import { PermissionsAndroid, Platform } from 'react-native';

export class LocationService {
  static async requestLocationPermission() {
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION
      );
      return granted === PermissionsAndroid.RESULTS.GRANTED;
    }
    return true; // iOS handles permissions automatically
  }

  static async getCurrentLocation() {
    const hasPermission = await this.requestLocationPermission();
    if (!hasPermission) {
      throw new Error('Location permission denied');
    }

    return new Promise((resolve, reject) => {
      Geolocation.getCurrentPosition(
        resolve,
        reject,
        {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 10000
        }
      );
    });
  }

  static watchLocation(callback, errorCallback) {
    return Geolocation.watchPosition(
      callback,
      errorCallback,
      {
        enableHighAccuracy: true,
        distanceFilter: 10 // Update every 10 meters
      }
    );
  }
}

// packages/shared/hooks/useOfflineSync.js
import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

export const useOfflineSync = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [pendingSyncs, setPendingSyncs] = useState([]);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(state.isConnected);
    });

    loadPendingSyncs();

    return unsubscribe;
  }, []);

  const loadPendingSyncs = async () => {
    try {
      const stored = await AsyncStorage.getItem('pendingSyncs');
      if (stored) {
        setPendingSyncs(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Failed to load pending syncs:', error);
    }
  };

  const queueForSync = useCallback(async (operation) => {
    const newSync = {
      id: Date.now().toString(),
      operation,
      timestamp: new Date().toISOString(),
      retryCount: 0
    };

    const updatedSyncs = [...pendingSyncs, newSync];
    setPendingSyncs(updatedSyncs);
    
    await AsyncStorage.setItem('pendingSyncs', JSON.stringify(updatedSyncs));

    // If online, try to sync immediately
    if (isOnline) {
      syncData();
    }
  }, [pendingSyncs, isOnline]);

  const syncData = useCallback(async () => {
    if (!isOnline || isSyncing || pendingSyncs.length === 0) {
      return;
    }

    setIsSyncing(true);

    const successfulSyncs = [];
    const failedSyncs = [];

    for (const sync of pendingSyncs) {
      try {
        await executeSync(sync.operation);
        successfulSyncs.push(sync.id);
      } catch (error) {
        if (sync.retryCount < 3) {
          failedSyncs.push({
            ...sync,
            retryCount: sync.retryCount + 1
          });
        }
      }
    }

    // Update pending syncs
    const remainingSyncs = failedSyncs;
    setPendingSyncs(remainingSyncs);
    await AsyncStorage.setItem('pendingSyncs', JSON.stringify(remainingSyncs));

    setIsSyncing(false);
  }, [isOnline, isSyncing, pendingSyncs]);

  return {
    isOnline,
    pendingSyncs,
    isSyncing,
    queueForSync,
    syncData
  };
};
```

### Assessment Criteria
- Cross-platform code sharing is effective ✅
- Mobile-specific features work correctly ✅
- Offline functionality is robust ✅
- Performance is optimized for mobile ✅
- App store deployment is successful ✅

---

## 🔄 Project 3: GraphQL Real-time Collaboration Platform

### Objective
Build a sophisticated real-time collaboration platform using GraphQL subscriptions, advanced caching, and optimistic updates.

### Skills Practiced
- GraphQL schema design and implementation
- Real-time subscriptions
- Apollo Client advanced features
- Optimistic updates and cache management
- Scalable real-time architecture

### Requirements
```jsx
// GraphQL-powered collaboration platform
<CollaborationPlatform>
  <ApolloProvider client={apolloClient}>
    <SubscriptionManager>
      <DocumentWorkspace>
        <CollaborativeEditor />
        <RealtimeComments />
        <PresenceIndicators />
        <VersionHistory />
      </DocumentWorkspace>
    </SubscriptionManager>
  </ApolloProvider>
</CollaborationPlatform>
```

### Features to Implement
- [x] GraphQL schema with real-time subscriptions
- [x] Optimistic updates with conflict resolution
- [x] Advanced Apollo Client caching strategies
- [x] Real-time presence and cursors
- [x] Collaborative document editing
- [x] Version control with branching
- [x] Permission-based access control
- [x] Offline support with cache persistence
- [x] Performance monitoring and optimization

### Project Structure
```
graphql-collaboration-platform/
├── client/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Editor/
│   │   │   ├── Comments/
│   │   │   ├── Presence/
│   │   │   └── Versions/
│   │   ├── graphql/
│   │   │   ├── queries/
│   │   │   ├── mutations/
│   │   │   ├── subscriptions/
│   │   │   └── fragments/
│   │   ├── apollo/
│   │   │   ├── client.js
│   │   │   ├── cache.js
│   │   │   ├── links/
│   │   │   └── optimisticUpdates.js
│   │   ├── hooks/
│   │   │   ├── useCollaboration.js
│   │   │   ├── useOptimisticUpdates.js
│   │   │   └── useRealTimeSync.js
│   │   └── utils/
│   │       ├── conflictResolution.js
│   │       └── cacheHelpers.js
│   └── package.json
├── server/
│   ├── src/
│   │   ├── schema/
│   │   │   ├── typeDefs/
│   │   │   └── resolvers/
│   │   ├── services/
│   │   │   ├── DocumentService.js
│   │   │   ├── CollaborationService.js
│   │   │   └── VersionService.js
│   │   ├── subscriptions/
│   │   │   └── pubsub.js
│   │   └── utils/
│   │       └── operationalTransform.js
│   └── package.json
└── shared/
    ├── types/
    └── utils/
```

### GraphQL Schema and Implementation
```graphql
# server/src/schema/typeDefs/collaboration.graphql
type Document {
  id: ID!
  title: String!
  content: String!
  version: Int!
  collaborators: [User!]!
  comments: [Comment!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Operation {
  id: ID!
  type: OperationType!
  position: Int!
  content: String
  authorId: ID!
  timestamp: DateTime!
  documentId: ID!
}

enum OperationType {
  INSERT
  DELETE
  RETAIN
}

type Presence {
  userId: ID!
  user: User!
  cursor: CursorPosition
  selection: TextSelection
  lastSeen: DateTime!
}

type Subscription {
  documentUpdated(documentId: ID!): Document!
  operationAdded(documentId: ID!): Operation!
  presenceUpdated(documentId: ID!): Presence!
  commentAdded(documentId: ID!): Comment!
}

type Mutation {
  applyOperation(input: OperationInput!): OperationResult!
  updatePresence(input: PresenceInput!): Presence!
  addComment(input: CommentInput!): Comment!
  createDocument(input: DocumentInput!): Document!
}
```

```jsx
{% raw %}
{% raw %}
// client/src/apollo/optimisticUpdates.js
export const optimisticUpdateHandlers = {
  applyOperation: {
    optimisticResponse: ({ input }) => ({
      __typename: 'Mutation',
      applyOperation: {
        __typename: 'OperationResult',
        success: true,
        operation: {
          __typename: 'Operation',
          id: `temp-${Date.now()}`,
          type: input.type,
          position: input.position,
          content: input.content,
          authorId: input.authorId,
          timestamp: new Date().toISOString(),
          documentId: input.documentId
        }
      }
    }),
    
    update: (cache, { data: { applyOperation } }) => {
      if (applyOperation.success) {
        // Update document content optimistically
        const documentQuery = {
          query: GET_DOCUMENT,
          variables: { id: applyOperation.operation.documentId }
        };
        
        const { document } = cache.readQuery(documentQuery);
        const updatedContent = applyOperationToContent(
          document.content,
          applyOperation.operation
        );
        
        cache.writeQuery({
          ...documentQuery,
          data: {
            document: {
              ...document,
              content: updatedContent,
              version: document.version + 1
            }
          }
        });
      }
    }
  }
};

// client/src/hooks/useCollaboration.js
import { useSubscription, useMutation, useQuery } from '@apollo/client';
import { useEffect, useCallback, useRef } from 'react';
import { OperationalTransform } from '../utils/operationalTransform';

export const useCollaboration = (documentId) => {
  const transformQueueRef = useRef([]);
  const localOperationsRef = useRef([]);
  
  const { data: document, loading } = useQuery(GET_DOCUMENT, {
    variables: { id: documentId },
    errorPolicy: 'all'
  });
  
  const [applyOperation] = useMutation(APPLY_OPERATION, {
    ...optimisticUpdateHandlers.applyOperation,
    onCompleted: (data) => {
      // Remove from local operations queue
      localOperationsRef.current = localOperationsRef.current.filter(
        op => op.tempId !== data.applyOperation.operation.id
      );
    },
    onError: (error) => {
      // Handle conflict resolution
      handleOperationConflict(error);
    }
  });
  
  // Subscribe to remote operations
  const { data: operationData } = useSubscription(OPERATION_ADDED, {
    variables: { documentId },
    onSubscriptionData: ({ subscriptionData }) => {
      const remoteOperation = subscriptionData.data.operationAdded;
      handleRemoteOperation(remoteOperation);
    }
  });
  
  // Subscribe to presence updates
  const { data: presenceData } = useSubscription(PRESENCE_UPDATED, {
    variables: { documentId }
  });
  
  const handleRemoteOperation = useCallback((remoteOperation) => {
    // Transform remote operation against pending local operations
    let transformedOperation = remoteOperation;
    const newLocalOperations = [];
    
    for (const localOp of localOperationsRef.current) {
      const [transformedLocal, transformedRemote] = OperationalTransform.transform(
        localOp,
        transformedOperation
      );
      newLocalOperations.push(transformedLocal);
      transformedOperation = transformedRemote;
    }
    
    localOperationsRef.current = newLocalOperations;
    
    // Apply transformed remote operation to document
    applyRemoteOperation(transformedOperation);
  }, []);
  
  const sendOperation = useCallback(async (operation) => {
    const tempId = `temp-${Date.now()}`;
    const operationWithId = { ...operation, tempId };
    
    // Add to local operations queue
    localOperationsRef.current.push(operationWithId);
    
    try {
      await applyOperation({
        variables: {
          input: {
            ...operation,
            documentId
          }
        }
      });
    } catch (error) {
      // Remove from queue on error
      localOperationsRef.current = localOperationsRef.current.filter(
        op => op.tempId !== tempId
      );
      throw error;
    }
  }, [applyOperation, documentId]);
  
  return {
    document,
    loading,
    sendOperation,
    presence: presenceData?.presenceUpdated || [],
    isCollaborating: localOperationsRef.current.length > 0
  };
};
{% endraw %}
{% endraw %}
```

### Assessment Criteria
- GraphQL schema is well-designed and scalable ✅
- Real-time features work without conflicts ✅
- Optimistic updates handle edge cases correctly ✅
- Caching strategy is efficient and consistent ✅
- Performance scales with concurrent users ✅

---

## 🤖 Project 4: AI-Powered React Application

### Objective
Build an intelligent React application that integrates machine learning capabilities, natural language processing, and AI-driven features.

### Skills Practiced
- AI/ML integration in React applications
- Natural language processing
- Computer vision integration
- Real-time AI processing
- Ethical AI implementation

### Requirements
```jsx
// AI-powered application structure
<AIApplication>
  <AIAssistant>
    <NaturalLanguageProcessor />
    <ComputerVisionEngine />
    <RecommendationSystem />
    <PredictiveAnalytics />
  </AIAssistant>
  <UserInterface>
    <SmartSearch />
    <AutoCompletion />
    <ContentGeneration />
    <PersonalizedDashboard />
  </UserInterface>
</AIApplication>
```

### Features to Implement
- [x] Natural language processing for smart search
- [x] Computer vision for image analysis
- [x] AI-powered content generation
- [x] Intelligent recommendations
- [x] Predictive analytics dashboard
- [x] Voice interaction capabilities
- [x] Real-time sentiment analysis
- [x] Automated accessibility improvements
- [x] Ethical AI monitoring and bias detection

### Project Structure
```
ai-powered-react-app/
├── src/
│   ├── components/
│   │   ├── AI/
│   │   │   ├── AIAssistant.jsx
│   │   │   ├── SmartSearch.jsx
│   │   │   ├── ContentGenerator.jsx
│   │   │   └── RecommendationEngine.jsx
│   │   ├── Vision/
│   │   │   ├── ImageAnalysis.jsx
│   │   │   ├── ObjectDetection.jsx
│   │   │   └── FaceRecognition.jsx
│   │   ├── NLP/
│   │   │   ├── TextAnalysis.jsx
│   │   │   ├── SentimentAnalysis.jsx
│   │   │   └── LanguageDetection.jsx
│   │   └── Voice/
│   │       ├── SpeechRecognition.jsx
│   │       └── TextToSpeech.jsx
│   ├── services/
│   │   ├── aiService.js
│   │   ├── nlpService.js
│   │   ├── visionService.js
│   │   ├── recommendationService.js
│   │   └── ethicsService.js
│   ├── hooks/
│   │   ├── useAI.js
│   │   ├── useNLP.js
│   │   ├── useVision.js
│   │   ├── useRecommendations.js
│   │   └── useEthicalAI.js
│   ├── workers/
│   │   ├── aiProcessor.worker.js
│   │   ├── nlpProcessor.worker.js
│   │   └── visionProcessor.worker.js
│   ├── models/
│   │   ├── sentiment.model.json
│   │   ├── classification.model.json
│   │   └── recommendation.model.json
│   └── utils/
│       ├── aiHelpers.js
│       ├── biasDetection.js
│       └── performanceMonitoring.js
├── public/
│   └── models/
└── package.json
```

### AI Integration Implementation
```jsx
{% raw %}
{% raw %}
// src/services/aiService.js
import * as tf from '@tensorflow/tfjs';
import { loadLayersModel } from '@tensorflow/tfjs-layers';

export class AIService {
  static models = new Map();
  
  static async loadModel(modelName, modelPath) {
    if (this.models.has(modelName)) {
      return this.models.get(modelName);
    }
    
    const model = await loadLayersModel(modelPath);
    this.models.set(modelName, model);
    return model;
  }
  
  static async predictSentiment(text) {
    const model = await this.loadModel('sentiment', '/models/sentiment.json');
    
    // Preprocess text
    const preprocessed = this.preprocessText(text);
    const tensor = tf.tensor2d([preprocessed]);
    
    // Make prediction
    const prediction = model.predict(tensor);
    const result = await prediction.data();
    
    // Cleanup
    tensor.dispose();
    prediction.dispose();
    
    return {
      positive: result[0],
      negative: result[1],
      neutral: result[2],
      confidence: Math.max(...result)
    };
  }
  
  static async generateRecommendations(userProfile, contentItems) {
    const model = await this.loadModel('recommendation', '/models/recommendation.json');
    
    // Create feature vectors
    const userVector = this.createUserVector(userProfile);
    const itemVectors = contentItems.map(item => this.createItemVector(item));
    
    const recommendations = [];
    
    for (const itemVector of itemVectors) {
      const combinedFeatures = tf.concat([userVector, itemVector]);
      const score = model.predict(combinedFeatures.expandDims(0));
      const scoreValue = await score.data();
      
      recommendations.push({
        item: itemVector.item,
        score: scoreValue[0],
        reasoning: this.explainRecommendation(userVector, itemVector)
      });
      
      // Cleanup
      combinedFeatures.dispose();
      score.dispose();
    }
    
    return recommendations
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);
  }
  
  static async analyzeImage(imageElement) {
    const model = await this.loadModel('vision', '/models/mobilenet.json');
    
    // Preprocess image
    const tensor = tf.browser.fromPixels(imageElement)
      .resizeNearestNeighbor([224, 224])
      .toFloat()
      .div(255.0)
      .expandDims(0);
    
    // Make prediction
    const predictions = await model.predict(tensor).data();
    
    // Get top predictions
    const topPredictions = this.getTopPredictions(predictions, 5);
    
    // Cleanup
    tensor.dispose();
    
    return topPredictions;
  }
}

// src/hooks/useAI.js
import { useState, useEffect, useCallback } from 'react';
import { AIService } from '../services/aiService';
import { EthicsService } from '../services/ethicsService';

export const useAI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [biasMetrics, setBiasMetrics] = useState(null);
  
  const predictSentiment = useCallback(async (text) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Check for bias before processing
      const biasCheck = await EthicsService.checkTextBias(text);
      setBiasMetrics(biasCheck);
      
      if (biasCheck.severity > 0.8) {
        throw new Error('Content contains potential bias');
      }
      
      const result = await AIService.predictSentiment(text);
      
      // Log AI decision for audit trail
      EthicsService.logAIDecision({
        type: 'sentiment_analysis',
        input: text,
        output: result,
        biasMetrics: biasCheck,
        timestamp: new Date().toISOString()
      });
      
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  const generateRecommendations = useCallback(async (userProfile, items) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Check for demographic bias in recommendations
      const fairnessCheck = await EthicsService.checkRecommendationFairness(
        userProfile, 
        items
      );
      
      const recommendations = await AIService.generateRecommendations(
        userProfile, 
        items
      );
      
      // Apply fairness adjustments if needed
      const fairRecommendations = EthicsService.adjustForFairness(
        recommendations,
        fairnessCheck
      );
      
      return fairRecommendations;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  return {
    isLoading,
    error,
    biasMetrics,
    predictSentiment,
    generateRecommendations,
    analyzeImage: AIService.analyzeImage
  };
};

// src/components/AI/SmartSearch.jsx
import React, { useState, useEffect, useMemo } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { useAI } from '../hooks/useAI';
import { NLPService } from '../services/nlpService';

export const SmartSearch = ({ onResults, data }) => {
  const [query, setQuery] = useState('');
  const [intent, setIntent] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  
  const debouncedQuery = useDebounce(query, 300);
  const { predictSentiment, isLoading } = useAI();
  
  // Analyze user intent
  useEffect(() => {
    if (debouncedQuery) {
      analyzeSearchIntent(debouncedQuery);
    }
  }, [debouncedQuery]);
  
  const analyzeSearchIntent = async (searchQuery) => {
    try {
      const analysis = await NLPService.analyzeIntent(searchQuery);
      setIntent(analysis);
      
      // Generate smart suggestions based on intent
      const smartSuggestions = await generateSmartSuggestions(
        searchQuery, 
        analysis
      );
      setSuggestions(smartSuggestions);
    } catch (error) {
      console.error('Intent analysis failed:', error);
    }
  };
  
  const generateSmartSuggestions = async (query, intentAnalysis) => {
    // Use AI to generate contextual suggestions
    const suggestions = [];
    
    if (intentAnalysis.type === 'product_search') {
      // Add product-specific suggestions
      suggestions.push(
        `${query} reviews`,
        `${query} price comparison`,
        `${query} alternatives`
      );
    } else if (intentAnalysis.type === 'information_seeking') {
      // Add information-specific suggestions
      suggestions.push(
        `how to ${query}`,
        `${query} tutorial`,
        `${query} best practices`
      );
    }
    
    return suggestions;
  };
  
  const performSmartSearch = async (searchQuery) => {
    const results = [];
    
    // Traditional text matching
    const textMatches = data.filter(item => 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    // Semantic search using embeddings
    const semanticMatches = await NLPService.semanticSearch(searchQuery, data);
    
    // Combine and rank results
    const combinedResults = [...textMatches, ...semanticMatches]
      .reduce((acc, item) => {
        const existing = acc.find(r => r.id === item.id);
        if (existing) {
          existing.score += item.score || 1;
        } else {
          acc.push({ ...item, score: item.score || 1 });
        }
        return acc;
      }, [])
      .sort((a, b) => b.score - a.score);
    
    onResults(combinedResults);
  };
  
  return (
    <div className="smart-search">
      <div className="search-input-container">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search with AI assistance..."
          className="search-input"
        />
        {isLoading && <div className="loading-indicator">🤖</div>}
      </div>
      
      {intent && (
        <div className="search-intent">
          <span>Detected intent: {intent.type}</span>
          <span>Confidence: {Math.round(intent.confidence * 100)}%</span>
        </div>
      )}
      
      {suggestions.length > 0 && (
        <div className="search-suggestions">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => setQuery(suggestion)}
              className="suggestion-button"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
{% endraw %}
{% endraw %}
```

### Assessment Criteria
- AI integration is practical and adds real value ✅
- Ethical AI practices are implemented ✅
- Performance is optimized for AI workloads ✅
- User experience is enhanced by AI features ✅
- Bias detection and mitigation work correctly ✅

---

## 🔧 Project 5: Open Source Component Library

### Objective
Create and maintain a production-ready, open-source React component library with comprehensive documentation, testing, and community features.

### Skills Practiced
- Open source project management
- Component library architecture
- API design and documentation
- Community building and maintenance
- Continuous integration and deployment

### Requirements
```jsx
// Component library ecosystem
<ComponentLibraryEcosystem>
  <DocumentationSite>
    <ComponentShowcase />
    <APIReference />
    <DesignTokens />
    <UsageExamples />
  </DocumentationSite>
  <ComponentLibrary>
    <DesignSystem />
    <ComponentCollection />
    <ThemeProvider />
    <AccessibilityFramework />
  </ComponentLibrary>
  <DeveloperTools>
    <Storybook />
    <TestSuite />
    <BuildPipeline />
    <PublishingWorkflow />
  </DeveloperTools>
</ComponentLibraryEcosystem>
```

### Features to Implement
- [x] Comprehensive component library with 50+ components
- [x] Design system with tokens and themes
- [x] Comprehensive Storybook documentation
- [x] Full accessibility compliance (WCAG 2.1 AA)
- [x] TypeScript definitions and IntelliSense
- [x] Multiple framework adapters (React, Vue, Angular)
- [x] Automated testing and visual regression
- [x] NPM publishing and versioning
- [x] Community contribution guidelines
- [x] Performance monitoring and optimization

### Project Structure
```
react-ui-library/
├── packages/
│   ├── core/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Button/
│   │   │   │   ├── Input/
│   │   │   │   ├── Modal/
│   │   │   │   └── DataTable/
│   │   │   ├── tokens/
│   │   │   │   ├── colors.ts
│   │   │   │   ├── typography.ts
│   │   │   │   └── spacing.ts
│   │   │   ├── themes/
│   │   │   └── utils/
│   │   ├── tests/
│   │   └── package.json
│   ├── icons/
│   │   ├── src/
│   │   └── package.json
│   ├── tokens/
│   │   ├── src/
│   │   └── package.json
│   └── adapters/
│       ├── vue/
│       └── angular/
├── apps/
│   ├── storybook/
│   ├── documentation/
│   └── playground/
├── tools/
│   ├── build/
│   ├── testing/
│   └── publishing/
├── docs/
│   ├── contributing.md
│   ├── design-principles.md
│   └── api-guidelines.md
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
└── lerna.json
```

### Component Library Implementation
```typescript
// packages/core/src/components/Button/Button.tsx
import React, { forwardRef } from 'react';
import { styled } from '@stitches/react';
import { VariantProps } from '@stitches/react';
import { theme } from '../../tokens';

const StyledButton = styled('button', {
  // Base styles
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  borderRadius: '$md',
  fontFamily: '$sans',
  fontWeight: '$medium',
  lineHeight: 1,
  textDecoration: 'none',
  border: 'none',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  
  // Focus styles for accessibility
  '&:focus-visible': {
    outline: '2px solid $blue600',
    outlineOffset: '2px',
  },
  
  // Disabled styles
  '&:disabled': {
    opacity: 0.5,
    cursor: 'not-allowed',
    pointerEvents: 'none',
  },
  
  variants: {
    variant: {
      primary: {
        backgroundColor: '$blue600',
        color: '$white',
        '&:hover': {
          backgroundColor: '$blue700',
        },
        '&:active': {
          backgroundColor: '$blue800',
        },
      },
      secondary: {
        backgroundColor: '$gray100',
        color: '$gray900',
        '&:hover': {
          backgroundColor: '$gray200',
        },
        '&:active': {
          backgroundColor: '$gray300',
        },
      },
      outline: {
        backgroundColor: 'transparent',
        color: '$blue600',
        border: '1px solid $blue600',
        '&:hover': {
          backgroundColor: '$blue50',
        },
        '&:active': {
          backgroundColor: '$blue100',
        },
      },
      ghost: {
        backgroundColor: 'transparent',
        color: '$gray700',
        '&:hover': {
          backgroundColor: '$gray100',
        },
        '&:active': {
          backgroundColor: '$gray200',
        },
      },
    },
    size: {
      sm: {
        height: '$8',
        paddingX: '$3',
        fontSize: '$sm',
      },
      md: {
        height: '$10',
        paddingX: '$4',
        fontSize: '$base',
      },
      lg: {
        height: '$12',
        paddingX: '$6',
        fontSize: '$lg',
      },
    },
    fullWidth: {
      true: {
        width: '100%',
      },
    },
  },
  
  defaultVariants: {
    variant: 'primary',
    size: 'md',
  },
});

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof StyledButton> {
  /**
   * The content to display inside the button
   */
  children: React.ReactNode;
  /**
   * Whether the button is in a loading state
   */
  loading?: boolean;
  /**
   * Icon to display before the button text
   */
  startIcon?: React.ReactNode;
  /**
   * Icon to display after the button text
   */
  endIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      loading = false,
      startIcon,
      endIcon,
      disabled,
      variant,
      size,
      fullWidth,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <StyledButton
        ref={ref}
        disabled={isDisabled}
        variant={variant}
        size={size}
        fullWidth={fullWidth}
        aria-disabled={isDisabled}
        {...props}
      >
        {loading && <Spinner size="sm" />}
        {!loading && startIcon && <span className="start-icon">{startIcon}</span>}
        <span className="button-text">{children}</span>
        {!loading && endIcon && <span className="end-icon">{endIcon}</span>}
      </StyledButton>
    );
  }
);

Button.displayName = 'Button';

// packages/core/src/components/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';
import { PlusIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants and states.',
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline', 'ghost'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    loading: {
      control: 'boolean',
    },
    disabled: {
      control: 'boolean',
    },
    fullWidth: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
    </div>
  ),
};

export const WithIcons: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexDirection: 'column', alignItems: 'flex-start' }}>
      <Button startIcon={<PlusIcon width={16} height={16} />}>
        Add Item
      </Button>
      <Button endIcon={<ArrowRightIcon width={16} height={16} />}>
        Continue
      </Button>
      <Button 
        startIcon={<PlusIcon width={16} height={16} />}
        endIcon={<ArrowRightIcon width={16} height={16} />}
      >
        Create and Continue
      </Button>
    </div>
  ),
};

// packages/core/src/components/Button/Button.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Test Button</Button>);
    expect(screen.getByText('Test Button')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('respects disabled state', () => {
    const handleClick = jest.fn();
    render(
      <Button disabled onClick={handleClick}>
        Disabled Button
      </Button>
    );
    
    const button = screen.getByText('Disabled Button');
    expect(button).toBeDisabled();
    
    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('shows loading state correctly', () => {
    render(<Button loading>Loading Button</Button>);
    
    const button = screen.getByText('Loading Button');
    expect(button).toBeDisabled();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('applies correct variant classes', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByText('Primary')).toHaveClass('variant-primary');
    
    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByText('Secondary')).toHaveClass('variant-secondary');
  });

  it('meets accessibility requirements', () => {
    render(<Button>Accessible Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'button');
    expect(button).not.toHaveAttribute('aria-disabled');
    
    // Test keyboard navigation
    button.focus();
    expect(button).toHaveFocus();
  });
});
```

### Assessment Criteria
- Component library is comprehensive and well-designed ✅
- Documentation is thorough and user-friendly ✅
- Accessibility compliance is complete ✅
- Community adoption and contribution guidelines are clear ✅
- Automated testing and deployment work correctly ✅

---

## 🏆 Portfolio Showcase

### Combined Portfolio Project
Create a comprehensive portfolio website that demonstrates all expert-level skills by integrating elements from all five projects.

### Features to Include
- [x] Next.js-powered personal website with SSG/SSR
- [x] React Native mobile companion app
- [x] GraphQL-powered blog and project showcase
- [x] AI-powered content recommendations and search
- [x] Custom component library used throughout
- [x] Advanced performance optimizations
- [x] Comprehensive testing and documentation
- [x] Open source contributions and case studies

---

## 📚 Resources for Expert Projects

### Next.js Advanced Features
- [Next.js Documentation](https://nextjs.org/docs)
- [React Server Components](https://react.dev/blog/2020/12/21/data-fetching-with-react-server-components)
- [Next.js Patterns](https://nextjs.org/docs/advanced-features/compiler)

### React Native Development
- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [Expo Framework](https://docs.expo.dev/)
- [React Native Performance](https://reactnative.dev/docs/performance)

### GraphQL and Apollo
- [Apollo Client Documentation](https://www.apollographql.com/docs/react/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [Real-time GraphQL](https://www.apollographql.com/docs/react/data/subscriptions/)

### AI/ML Integration
- [TensorFlow.js](https://www.tensorflow.org/js)
- [Hugging Face Transformers.js](https://huggingface.co/docs/transformers.js)
- [Ethical AI Guidelines](https://ai.google/principles/)

### Open Source Best Practices
- [Open Source Guide](https://opensource.guide/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🚀 Career Advancement

After completing these expert projects, you'll be qualified for:

### Senior Roles
- **Senior React Developer**: Lead complex React projects
- **Frontend Architect**: Design scalable frontend systems
- **Technical Lead**: Guide development teams and make architectural decisions

### Specialized Roles
- **Performance Engineer**: Optimize application performance
- **DevOps Engineer**: Handle deployment and infrastructure
- **AI/ML Engineer**: Integrate machine learning capabilities

### Leadership Opportunities
- **Engineering Manager**: Lead development teams
- **Product Engineer**: Bridge product and engineering
- **Open Source Maintainer**: Contribute to and maintain projects

### Entrepreneurial Paths
- **Technical Co-founder**: Start your own tech company
- **Consultant**: Provide React expertise to organizations
- **Educator**: Teach React and modern web development

---

## 🎯 Final Assessment

Your expert-level competency will be demonstrated through:

### Technical Excellence ✅
- Complex problem-solving abilities
- Architecture and design decisions
- Performance optimization skills
- Security and accessibility awareness

### Leadership Capabilities ✅
- Code review and mentoring
- Technical documentation
- Team collaboration
- Project management

### Innovation and Growth ✅
- Cutting-edge technology adoption
- Open source contributions
- Community involvement
- Continuous learning mindset

### Industry Impact ✅
- Production application deployment
- User feedback and metrics
- Business value creation
- Professional recognition

**Congratulations on reaching React Expert level! 🚀**