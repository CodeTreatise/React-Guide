# Module Federation & Micro-frontends

## Table of Contents
1. [Module Federation Fundamentals](#module-federation-fundamentals)
2. [Micro-frontend Architecture](#micro-frontend-architecture)
3. [Advanced Federation Patterns](#advanced-federation-patterns)
4. [Runtime Integration](#runtime-integration)
5. [Shared Dependencies](#shared-dependencies)
6. [State Management Across Microfrontends](#state-management-across-microfrontends)
7. [Testing Strategies](#testing-strategies)
8. [Production Deployment](#production-deployment)

## Module Federation Fundamentals

### Basic Module Federation Setup
```javascript
// webpack.config.js (Host Application)
const ModuleFederationPlugin = require('@module-federation/webpack');

module.exports = {
  mode: 'development',
  
  entry: './src/index.tsx',
  
  devServer: {
    port: 3000,
    historyApiFallback: true
  },
  
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      
      remotes: {
        // Remote micro-frontends
        shell: 'shell@http://localhost:3001/remoteEntry.js',
        dashboard: 'dashboard@http://localhost:3002/remoteEntry.js',
        profile: 'profile@http://localhost:3003/remoteEntry.js'
      },
      
      shared: {
        react: {
          singleton: true,
          requiredVersion: '^18.0.0'
        },
        'react-dom': {
          singleton: true,
          requiredVersion: '^18.0.0'
        },
        'react-router-dom': {
          singleton: true,
          requiredVersion: '^6.0.0'
        }
      }
    })
  ]
};

// webpack.config.js (Remote Application)
module.exports = {
  mode: 'development',
  
  entry: './src/index.tsx',
  
  devServer: {
    port: 3001,
    historyApiFallback: true,
    headers: {
      'Access-Control-Allow-Origin': '*'
    }
  },
  
  plugins: [
    new ModuleFederationPlugin({
      name: 'shell',
      
      filename: 'remoteEntry.js',
      
      exposes: {
        './App': './src/App',
        './Navigation': './src/components/Navigation',
        './Header': './src/components/Header'
      },
      
      shared: {
        react: {
          singleton: true,
          requiredVersion: '^18.0.0'
        },
        'react-dom': {
          singleton: true,
          requiredVersion: '^18.0.0'
        }
      }
    })
  ]
};
```

### Dynamic Remote Loading
```typescript
{% raw %}
// types/module-federation.d.ts
declare global {
  interface Window {
    __webpack_init_sharing__: (scope: string) => Promise<void>;
    __webpack_share_scopes__: Record<string, any>;
  }
}

// Remote loader utility
class RemoteLoader {
  private cache = new Map<string, any>();
  
  async loadRemote<T = any>(
    remoteName: string,
    exposedModule: string,
    fallback?: () => Promise<T>
  ): Promise<T> {
    const cacheKey = `${remoteName}/${exposedModule}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }
    
    try {
      const container = await this.loadContainer(remoteName);
      const factory = await container.get(exposedModule);
      const module = factory();
      
      this.cache.set(cacheKey, module);
      return module;
    } catch (error) {
      console.error(`Failed to load remote ${remoteName}/${exposedModule}:`, error);
      
      if (fallback) {
        const fallbackModule = await fallback();
        this.cache.set(cacheKey, fallbackModule);
        return fallbackModule;
      }
      
      throw error;
    }
  }
  
  private async loadContainer(remoteName: string) {
    // Get remote configuration
    const remoteConfig = this.getRemoteConfig(remoteName);
    
    if (!remoteConfig) {
      throw new Error(`Remote ${remoteName} not configured`);
    }
    
    // Load remote entry script
    await this.loadScript(remoteConfig.url);
    
    // Initialize sharing
    await window.__webpack_init_sharing__('default');
    
    // Get container
    const container = (window as any)[remoteName];
    
    if (!container) {
      throw new Error(`Remote ${remoteName} not found`);
    }
    
    // Initialize container
    await container.init(window.__webpack_share_scopes__.default);
    
    return container;
  }
  
  private loadScript(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // Check if script already loaded
      const existingScript = document.querySelector(`script[src="${url}"]`);
      if (existingScript) {
        resolve();
        return;
      }
      
      const script = document.createElement('script');
      script.src = url;
      script.type = 'text/javascript';
      script.async = true;
      
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load script: ${url}`));
      
      document.head.appendChild(script);
    });
  }
  
  private getRemoteConfig(remoteName: string) {
    // This could come from environment variables or API
    const remoteConfigs = {
      shell: { url: 'http://localhost:3001/remoteEntry.js' },
      dashboard: { url: 'http://localhost:3002/remoteEntry.js' },
      profile: { url: 'http://localhost:3003/remoteEntry.js' }
    };
    
    return remoteConfigs[remoteName as keyof typeof remoteConfigs];
  }
  
  clearCache() {
    this.cache.clear();
  }
}

export const remoteLoader = new RemoteLoader();
{% endraw %}
```

### Remote Component Wrapper
```typescript
{% raw %}
// components/RemoteComponent.tsx
import React, { Suspense, lazy, ComponentType } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { remoteLoader } from '../utils/remote-loader';

interface RemoteComponentProps {
  remoteName: string;
  exposedModule: string;
  fallback?: ComponentType;
  loading?: ComponentType;
  error?: ComponentType<{ error: Error; retry: () => void }>;
  [key: string]: any;
}

export const RemoteComponent: React.FC<RemoteComponentProps> = ({
  remoteName,
  exposedModule,
  fallback: FallbackComponent,
  loading: LoadingComponent = () => <div>Loading...</div>,
  error: ErrorComponent,
  ...props
}) => {
  const LazyComponent = lazy(async () => {
    try {
      const module = await remoteLoader.loadRemote(
        remoteName,
        exposedModule,
        FallbackComponent ? () => Promise.resolve({ default: FallbackComponent }) : undefined
      );
      
      return { default: module.default || module };
    } catch (error) {
      console.error(`Failed to load remote component ${remoteName}/${exposedModule}:`, error);
      
      if (FallbackComponent) {
        return { default: FallbackComponent };
      }
      
      throw error;
    }
  });
  
  const DefaultErrorComponent = ({ error, retry }: { error: Error; retry: () => void }) => (
    <div className="remote-error">
      <h3>Failed to load remote component</h3>
      <p>{error.message}</p>
      <button onClick={retry}>Retry</button>
    </div>
  );
  
  return (
    <ErrorBoundary
      FallbackComponent={ErrorComponent || DefaultErrorComponent}
      onReset={() => {
        remoteLoader.clearCache();
        window.location.reload();
      }}
    >
      <Suspense fallback={<LoadingComponent />}>
        <LazyComponent {...props} />
      </Suspense>
    </ErrorBoundary>
  );
};

// Usage example
export const DashboardPage = () => {
  return (
    <div>
      <h1>Dashboard</h1>
      <RemoteComponent
        remoteName="dashboard"
        exposedModule="./Dashboard"
        fallback={() => <div>Dashboard not available</div>}
        loading={() => <div>Loading dashboard...</div>}
      />
    </div>
  );
};
{% endraw %}
```

## Micro-frontend Architecture

### Application Shell Pattern
```typescript
// shell/src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { RemoteComponent } from './components/RemoteComponent';
import { AuthProvider } from './providers/AuthProvider';
import { GlobalStateProvider } from './providers/GlobalStateProvider';
import { EventBusProvider } from './providers/EventBusProvider';
import { Layout } from './components/Layout';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <GlobalStateProvider>
          <EventBusProvider>
            <Layout>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                <Route
                  path="/dashboard/*"
                  element={
                    <RemoteComponent
                      remoteName="dashboard"
                      exposedModule="./App"
                      fallback={() => <div>Dashboard unavailable</div>}
                    />
                  }
                />
                
                <Route
                  path="/profile/*"
                  element={
                    <RemoteComponent
                      remoteName="profile"
                      exposedModule="./App"
                      fallback={() => <div>Profile unavailable</div>}
                    />
                  }
                />
                
                <Route
                  path="/analytics/*"
                  element={
                    <RemoteComponent
                      remoteName="analytics"
                      exposedModule="./App"
                      fallback={() => <div>Analytics unavailable</div>}
                    />
                  }
                />
                
                <Route path="*" element={<div>Page not found</div>} />
              </Routes>
            </Layout>
          </EventBusProvider>
        </GlobalStateProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
```

### Micro-frontend Base Configuration
```typescript
{% raw %}
// shared/src/types/microfrontend.ts
export interface MicrofrontendConfig {
  name: string;
  url: string;
  scope: string;
  module: string;
  routes: string[];
  permissions?: string[];
  dependencies?: Record<string, string>;
}

export interface MicrofrontendRegistry {
  [key: string]: MicrofrontendConfig;
}

// shared/src/registry/microfrontends.ts
export const microfrontendRegistry: MicrofrontendRegistry = {
  dashboard: {
    name: 'dashboard',
    url: process.env.REACT_APP_DASHBOARD_URL || 'http://localhost:3002/remoteEntry.js',
    scope: 'dashboard',
    module: './App',
    routes: ['/dashboard'],
    permissions: ['dashboard:read']
  },
  
  profile: {
    name: 'profile',
    url: process.env.REACT_APP_PROFILE_URL || 'http://localhost:3003/remoteEntry.js',
    scope: 'profile',
    module: './App',
    routes: ['/profile'],
    permissions: ['profile:read', 'profile:write']
  },
  
  analytics: {
    name: 'analytics',
    url: process.env.REACT_APP_ANALYTICS_URL || 'http://localhost:3004/remoteEntry.js',
    scope: 'analytics',
    module: './App',
    routes: ['/analytics'],
    permissions: ['analytics:read']
  }
};

// shell/src/services/MicrofrontendService.ts
class MicrofrontendService {
  private loadedMicrofrontends = new Set<string>();
  
  async loadMicrofrontend(config: MicrofrontendConfig): Promise<any> {
    if (this.loadedMicrofrontends.has(config.name)) {
      return this.getMicrofrontend(config.name, config.module);
    }
    
    try {
      await this.loadScript(config.url);
      await this.initializeSharing();
      
      const container = (window as any)[config.scope];
      await container.init(window.__webpack_share_scopes__.default);
      
      this.loadedMicrofrontends.add(config.name);
      
      return this.getMicrofrontend(config.name, config.module);
    } catch (error) {
      console.error(`Failed to load microfrontend ${config.name}:`, error);
      throw error;
    }
  }
  
  private async getMicrofrontend(name: string, module: string) {
    const container = (window as any)[microfrontendRegistry[name].scope];
    const factory = await container.get(module);
    return factory();
  }
  
  private loadScript(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const existingScript = document.querySelector(`script[src="${url}"]`);
      if (existingScript) {
        resolve();
        return;
      }
      
      const script = document.createElement('script');
      script.src = url;
      script.type = 'text/javascript';
      script.async = true;
      
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load: ${url}`));
      
      document.head.appendChild(script);
    });
  }
  
  private async initializeSharing(): Promise<void> {
    if (!window.__webpack_share_scopes__?.default) {
      await window.__webpack_init_sharing__('default');
    }
  }
  
  getMicrofrontendsByRoute(pathname: string): MicrofrontendConfig[] {
    return Object.values(microfrontendRegistry).filter(config =>
      config.routes.some(route => pathname.startsWith(route))
    );
  }
  
  hasPermission(microfrontendName: string, userPermissions: string[]): boolean {
    const config = microfrontendRegistry[microfrontendName];
    if (!config.permissions) return true;
    
    return config.permissions.some(permission =>
      userPermissions.includes(permission)
    );
  }
}

export const microfrontendService = new MicrofrontendService();
{% endraw %}
```

## Advanced Federation Patterns

### Bi-directional Module Federation
```javascript
// Host and Remote configuration
const sharedDependencies = {
  react: {
    singleton: true,
    requiredVersion: '^18.0.0',
    eager: true
  },
  'react-dom': {
    singleton: true,
    requiredVersion: '^18.0.0',
    eager: true
  },
  '@shared/design-system': {
    singleton: true,
    requiredVersion: '^1.0.0'
  },
  '@shared/utils': {
    singleton: true,
    requiredVersion: '^1.0.0'
  }
};

// Host application (can also expose modules)
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      
      // Host can expose modules too
      filename: 'hostEntry.js',
      exposes: {
        './AuthService': './src/services/AuthService',
        './UserContext': './src/contexts/UserContext',
        './ErrorBoundary': './src/components/ErrorBoundary'
      },
      
      remotes: {
        dashboard: 'dashboard@http://localhost:3002/remoteEntry.js',
        profile: 'profile@http://localhost:3003/remoteEntry.js'
      },
      
      shared: sharedDependencies
    })
  ]
};

// Remote application (can consume from host)
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'dashboard',
      filename: 'remoteEntry.js',
      
      exposes: {
        './App': './src/App',
        './DashboardWidget': './src/components/DashboardWidget'
      },
      
      // Remote can consume from host
      remotes: {
        host: 'host@http://localhost:3000/hostEntry.js'
      },
      
      shared: sharedDependencies
    })
  ]
};
```

### Dynamic Remote Discovery
```typescript
{% raw %}
// services/RemoteDiscoveryService.ts
interface RemoteManifest {
  name: string;
  url: string;
  metadata: {
    version: string;
    buildTime: string;
    dependencies: Record<string, string>;
  };
  exposedModules: Record<string, {
    path: string;
    description: string;
    props?: any;
  }>;
}

class RemoteDiscoveryService {
  private manifestCache = new Map<string, RemoteManifest>();
  
  async discoverRemotes(): Promise<RemoteManifest[]> {
    const discoveryEndpoints = [
      'http://localhost:3001/manifest.json',
      'http://localhost:3002/manifest.json',
      'http://localhost:3003/manifest.json'
    ];
    
    const manifests = await Promise.allSettled(
      discoveryEndpoints.map(endpoint => this.fetchManifest(endpoint))
    );
    
    return manifests
      .filter((result): result is PromiseFulfilledResult<RemoteManifest> => 
        result.status === 'fulfilled'
      )
      .map(result => result.value);
  }
  
  private async fetchManifest(url: string): Promise<RemoteManifest> {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch manifest: ${response.statusText}`);
      }
      
      const manifest = await response.json();
      this.manifestCache.set(manifest.name, manifest);
      
      return manifest;
    } catch (error) {
      console.error(`Failed to discover remote at ${url}:`, error);
      throw error;
    }
  }
  
  async loadRemoteModule(remoteName: string, moduleName: string): Promise<any> {
    const manifest = this.manifestCache.get(remoteName);
    
    if (!manifest) {
      throw new Error(`Remote ${remoteName} not discovered`);
    }
    
    const moduleInfo = manifest.exposedModules[moduleName];
    
    if (!moduleInfo) {
      throw new Error(`Module ${moduleName} not exposed by ${remoteName}`);
    }
    
    // Check version compatibility
    await this.checkCompatibility(manifest);
    
    // Load the remote module
    return await remoteLoader.loadRemote(remoteName, moduleInfo.path);
  }
  
  private async checkCompatibility(manifest: RemoteManifest): Promise<void> {
    const incompatibleDeps: string[] = [];
    
    Object.entries(manifest.metadata.dependencies).forEach(([dep, version]) => {
      const currentVersion = this.getCurrentVersion(dep);
      if (currentVersion && !this.isCompatible(currentVersion, version)) {
        incompatibleDeps.push(`${dep}: required ${version}, current ${currentVersion}`);
      }
    });
    
    if (incompatibleDeps.length > 0) {
      console.warn(`Compatibility issues with ${manifest.name}:`, incompatibleDeps);
    }
  }
  
  private getCurrentVersion(dependency: string): string | null {
    // Implementation to get current version from package.json or runtime
    return null;
  }
  
  private isCompatible(current: string, required: string): boolean {
    // Semantic version compatibility check
    return true; // Simplified
  }
}

export const remoteDiscoveryService = new RemoteDiscoveryService();
{% endraw %}
```

### Micro-frontend Orchestration
```typescript
{% raw %}
// orchestration/MicrofrontendOrchestrator.ts
interface MicrofrontendInstance {
  name: string;
  component: React.ComponentType;
  metadata: {
    version: string;
    capabilities: string[];
    dependencies: string[];
  };
  lifecycle: {
    mount: () => Promise<void>;
    unmount: () => Promise<void>;
    update: (props: any) => Promise<void>;
  };
}

class MicrofrontendOrchestrator {
  private instances = new Map<string, MicrofrontendInstance>();
  private dependencyGraph = new Map<string, string[]>();
  
  async registerMicrofrontend(
    name: string, 
    config: MicrofrontendConfig
  ): Promise<void> {
    try {
      // Load the microfrontend
      const module = await microfrontendService.loadMicrofrontend(config);
      
      // Create instance
      const instance: MicrofrontendInstance = {
        name,
        component: module.default,
        metadata: module.metadata || {},
        lifecycle: {
          mount: module.mount || (() => Promise.resolve()),
          unmount: module.unmount || (() => Promise.resolve()),
          update: module.update || (() => Promise.resolve())
        }
      };
      
      // Register dependencies
      this.registerDependencies(name, instance.metadata.dependencies || []);
      
      // Store instance
      this.instances.set(name, instance);
      
      console.log(`Microfrontend ${name} registered successfully`);
    } catch (error) {
      console.error(`Failed to register microfrontend ${name}:`, error);
      throw error;
    }
  }
  
  async mountMicrofrontend(name: string, props?: any): Promise<void> {
    const instance = this.instances.get(name);
    
    if (!instance) {
      throw new Error(`Microfrontend ${name} not registered`);
    }
    
    // Check and mount dependencies first
    await this.mountDependencies(name);
    
    // Mount the microfrontend
    await instance.lifecycle.mount();
    
    console.log(`Microfrontend ${name} mounted`);
  }
  
  async unmountMicrofrontend(name: string): Promise<void> {
    const instance = this.instances.get(name);
    
    if (!instance) {
      return; // Already unmounted or never mounted
    }
    
    // Unmount the microfrontend
    await instance.lifecycle.unmount();
    
    // Check if we can unmount dependencies
    await this.unmountUnusedDependencies(name);
    
    console.log(`Microfrontend ${name} unmounted`);
  }
  
  private registerDependencies(name: string, dependencies: string[]): void {
    this.dependencyGraph.set(name, dependencies);
  }
  
  private async mountDependencies(name: string): Promise<void> {
    const dependencies = this.dependencyGraph.get(name) || [];
    
    for (const dependency of dependencies) {
      if (this.instances.has(dependency)) {
        await this.mountMicrofrontend(dependency);
      }
    }
  }
  
  private async unmountUnusedDependencies(name: string): Promise<void> {
    const dependencies = this.dependencyGraph.get(name) || [];
    
    for (const dependency of dependencies) {
      // Check if any other microfrontend depends on this
      const isUsedByOthers = Array.from(this.dependencyGraph.entries())
        .some(([key, deps]) => key !== name && deps.includes(dependency));
      
      if (!isUsedByOthers) {
        await this.unmountMicrofrontend(dependency);
      }
    }
  }
  
  getMicrofrontendCapabilities(name: string): string[] {
    const instance = this.instances.get(name);
    return instance?.metadata.capabilities || [];
  }
  
  getDependencyGraph(): Map<string, string[]> {
    return new Map(this.dependencyGraph);
  }
}

export const microfrontendOrchestrator = new MicrofrontendOrchestrator();
{% endraw %}
```

## Runtime Integration

### Event Bus Communication
```typescript
{% raw %}
// shared/src/events/EventBus.ts
type EventHandler<T = any> = (data: T) => void;
type UnsubscribeFunction = () => void;

interface EventBusInterface {
  emit<T>(event: string, data?: T): void;
  on<T>(event: string, handler: EventHandler<T>): UnsubscribeFunction;
  off(event: string, handler: EventHandler): void;
  once<T>(event: string, handler: EventHandler<T>): UnsubscribeFunction;
  clear(): void;
}

class EventBus implements EventBusInterface {
  private events = new Map<string, Set<EventHandler>>();
  private onceEvents = new Map<string, Set<EventHandler>>();
  
  emit<T>(event: string, data?: T): void {
    // Emit to regular listeners
    const handlers = this.events.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
    
    // Emit to once listeners and remove them
    const onceHandlers = this.onceEvents.get(event);
    if (onceHandlers) {
      onceHandlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in once event handler for ${event}:`, error);
        }
      });
      this.onceEvents.delete(event);
    }
    
    // Emit to wildcard listeners
    this.emitWildcard(event, data);
  }
  
  on<T>(event: string, handler: EventHandler<T>): UnsubscribeFunction {
    if (!this.events.has(event)) {
      this.events.set(event, new Set());
    }
    
    this.events.get(event)!.add(handler);
    
    return () => this.off(event, handler);
  }
  
  off(event: string, handler: EventHandler): void {
    const handlers = this.events.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.events.delete(event);
      }
    }
  }
  
  once<T>(event: string, handler: EventHandler<T>): UnsubscribeFunction {
    if (!this.onceEvents.has(event)) {
      this.onceEvents.set(event, new Set());
    }
    
    this.onceEvents.get(event)!.add(handler);
    
    return () => {
      const handlers = this.onceEvents.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.onceEvents.delete(event);
        }
      }
    };
  }
  
  private emitWildcard<T>(event: string, data?: T): void {
    const wildcardHandlers = this.events.get('*');
    if (wildcardHandlers) {
      wildcardHandlers.forEach(handler => {
        try {
          handler({ event, data });
        } catch (error) {
          console.error(`Error in wildcard event handler:`, error);
        }
      });
    }
  }
  
  clear(): void {
    this.events.clear();
    this.onceEvents.clear();
  }
  
  getEventNames(): string[] {
    return Array.from(this.events.keys());
  }
  
  getListenerCount(event: string): number {
    const handlers = this.events.get(event);
    const onceHandlers = this.onceEvents.get(event);
    
    return (handlers?.size || 0) + (onceHandlers?.size || 0);
  }
}

// Create global event bus instance
export const eventBus = new EventBus();

// Event types for type safety
export interface MicrofrontendEvents {
  'user:login': { userId: string; email: string };
  'user:logout': { userId: string };
  'navigation:change': { from: string; to: string };
  'data:updated': { entity: string; id: string; data: any };
  'notification:show': { type: 'info' | 'warning' | 'error'; message: string };
  'modal:open': { modalId: string; props?: any };
  'modal:close': { modalId: string };
}

// Typed event bus wrapper
export class TypedEventBus {
  emit<K extends keyof MicrofrontendEvents>(
    event: K,
    data: MicrofrontendEvents[K]
  ): void {
    eventBus.emit(event, data);
  }
  
  on<K extends keyof MicrofrontendEvents>(
    event: K,
    handler: (data: MicrofrontendEvents[K]) => void
  ): UnsubscribeFunction {
    return eventBus.on(event, handler);
  }
  
  once<K extends keyof MicrofrontendEvents>(
    event: K,
    handler: (data: MicrofrontendEvents[K]) => void
  ): UnsubscribeFunction {
    return eventBus.once(event, handler);
  }
}

export const typedEventBus = new TypedEventBus();
{% endraw %}
```

### React Hook for Event Bus
```typescript
// hooks/useEventBus.ts
import { useEffect, useCallback, useRef } from 'react';
import { eventBus, typedEventBus, MicrofrontendEvents } from '../events/EventBus';

export function useEventBus() {
  const handlersRef = useRef<Array<() => void>>([]);
  
  useEffect(() => {
    return () => {
      // Cleanup all handlers on unmount
      handlersRef.current.forEach(unsubscribe => unsubscribe());
    };
  }, []);
  
  const emit = useCallback(<K extends keyof MicrofrontendEvents>(
    event: K,
    data: MicrofrontendEvents[K]
  ) => {
    typedEventBus.emit(event, data);
  }, []);
  
  const on = useCallback(<K extends keyof MicrofrontendEvents>(
    event: K,
    handler: (data: MicrofrontendEvents[K]) => void,
    deps?: React.DependencyList
  ) => {
    useEffect(() => {
      const unsubscribe = typedEventBus.on(event, handler);
      handlersRef.current.push(unsubscribe);
      
      return unsubscribe;
    }, deps);
  }, []);
  
  const once = useCallback(<K extends keyof MicrofrontendEvents>(
    event: K,
    handler: (data: MicrofrontendEvents[K]) => void
  ) => {
    useEffect(() => {
      const unsubscribe = typedEventBus.once(event, handler);
      handlersRef.current.push(unsubscribe);
      
      return unsubscribe;
    }, [event, handler]);
  }, []);
  
  return { emit, on, once };
}

// Usage example in microfrontend
export const UserProfile: React.FC = () => {
  const { emit, on } = useEventBus();
  const [user, setUser] = useState(null);
  
  // Listen for user login events
  on('user:login', (userData) => {
    setUser(userData);
  }, []);
  
  // Listen for user logout events
  on('user:logout', () => {
    setUser(null);
  }, []);
  
  const handleSaveProfile = useCallback((profileData) => {
    // Save profile and emit update event
    saveProfile(profileData).then(() => {
      emit('data:updated', {
        entity: 'user',
        id: user.userId,
        data: profileData
      });
      
      emit('notification:show', {
        type: 'info',
        message: 'Profile updated successfully'
      });
    });
  }, [user, emit]);
  
  return (
    <div>
      {/* Profile component JSX */}
    </div>
  );
};
```

### Cross-Microfrontend State Synchronization
```typescript
{% raw %}
// state/CrossMicrofrontendState.ts
interface StateChange<T = any> {
  key: string;
  value: T;
  previousValue: T;
  timestamp: number;
  source: string;
}

class CrossMicrofrontendState {
  private state = new Map<string, any>();
  private subscribers = new Map<string, Set<(change: StateChange) => void>>();
  private source: string;
  
  constructor(microfrontendName: string) {
    this.source = microfrontendName;
    
    // Listen for state changes from other microfrontends
    eventBus.on('state:change', this.handleExternalStateChange.bind(this));
  }
  
  set<T>(key: string, value: T): void {
    const previousValue = this.state.get(key);
    this.state.set(key, value);
    
    const change: StateChange<T> = {
      key,
      value,
      previousValue,
      timestamp: Date.now(),
      source: this.source
    };
    
    // Notify local subscribers
    this.notifySubscribers(key, change);
    
    // Emit to other microfrontends
    eventBus.emit('state:change', change);
  }
  
  get<T>(key: string): T | undefined {
    return this.state.get(key);
  }
  
  subscribe<T>(
    key: string,
    callback: (change: StateChange<T>) => void
  ): () => void {
    if (!this.subscribers.has(key)) {
      this.subscribers.set(key, new Set());
    }
    
    this.subscribers.get(key)!.add(callback);
    
    return () => {
      const keySubscribers = this.subscribers.get(key);
      if (keySubscribers) {
        keySubscribers.delete(callback);
        if (keySubscribers.size === 0) {
          this.subscribers.delete(key);
        }
      }
    };
  }
  
  private handleExternalStateChange(change: StateChange): void {
    // Don't process changes from this microfrontend
    if (change.source === this.source) {
      return;
    }
    
    // Update local state
    this.state.set(change.key, change.value);
    
    // Notify local subscribers
    this.notifySubscribers(change.key, change);
  }
  
  private notifySubscribers(key: string, change: StateChange): void {
    const keySubscribers = this.subscribers.get(key);
    if (keySubscribers) {
      keySubscribers.forEach(callback => {
        try {
          callback(change);
        } catch (error) {
          console.error(`Error in state subscriber for key ${key}:`, error);
        }
      });
    }
  }
  
  getSnapshot(): Record<string, any> {
    return Object.fromEntries(this.state);
  }
  
  clear(): void {
    this.state.clear();
    this.subscribers.clear();
  }
}

// React hook for cross-microfrontend state
export function useCrossMicrofrontendState<T>(
  key: string,
  initialValue?: T,
  microfrontendName: string = 'unknown'
): [T | undefined, (value: T) => void] {
  const stateManager = useRef(new CrossMicrofrontendState(microfrontendName));
  const [value, setValue] = useState<T | undefined>(
    stateManager.current.get(key) ?? initialValue
  );
  
  useEffect(() => {
    const unsubscribe = stateManager.current.subscribe(key, (change) => {
      setValue(change.value);
    });
    
    return unsubscribe;
  }, [key]);
  
  const updateValue = useCallback((newValue: T) => {
    stateManager.current.set(key, newValue);
  }, [key]);
  
  return [value, updateValue];
}
{% endraw %}
```

## Shared Dependencies

### Shared Library Configuration
```javascript
// webpack.shared.js
const sharedConfig = {
  // React ecosystem
  react: {
    singleton: true,
    requiredVersion: '^18.0.0',
    eager: true,
    strictVersion: true
  },
  
  'react-dom': {
    singleton: true,
    requiredVersion: '^18.0.0',
    eager: true,
    strictVersion: true
  },
  
  'react-router-dom': {
    singleton: true,
    requiredVersion: '^6.0.0',
    eager: false
  },
  
  // State management
  'react-query': {
    singleton: true,
    requiredVersion: '^3.39.0',
    eager: false
  },
  
  zustand: {
    singleton: true,
    requiredVersion: '^4.0.0',
    eager: false
  },
  
  // UI libraries
  '@mui/material': {
    singleton: true,
    requiredVersion: '^5.0.0',
    eager: false
  },
  
  '@emotion/react': {
    singleton: true,
    requiredVersion: '^11.0.0',
    eager: false
  },
  
  // Utilities
  'lodash-es': {
    singleton: true,
    requiredVersion: '^4.17.0',
    eager: false
  },
  
  'date-fns': {
    singleton: true,
    requiredVersion: '^2.28.0',
    eager: false
  },
  
  // Custom shared libraries
  '@company/design-system': {
    singleton: true,
    requiredVersion: '^2.0.0',
    eager: false,
    import: '@company/design-system'
  },
  
  '@company/shared-utils': {
    singleton: true,
    requiredVersion: '^1.5.0',
    eager: false,
    import: '@company/shared-utils'
  }
};

module.exports = { sharedConfig };
```

### Version Compatibility Manager
```typescript
{% raw %}
// shared/src/version/VersionManager.ts
interface VersionRequirement {
  name: string;
  version: string;
  requiredBy: string[];
  conflicts?: string[];
}

class VersionManager {
  private requirements = new Map<string, VersionRequirement>();
  private resolvedVersions = new Map<string, string>();
  
  addRequirement(
    packageName: string,
    version: string,
    requiredBy: string
  ): void {
    const existing = this.requirements.get(packageName);
    
    if (existing) {
      // Add to required by list
      if (!existing.requiredBy.includes(requiredBy)) {
        existing.requiredBy.push(requiredBy);
      }
      
      // Check for version conflicts
      if (existing.version !== version) {
        console.warn(
          `Version conflict for ${packageName}: ` +
          `${existing.version} (required by ${existing.requiredBy.join(', ')}) ` +
          `vs ${version} (required by ${requiredBy})`
        );
        
        // Use semantic versioning to resolve
        const resolvedVersion = this.resolveVersionConflict(
          existing.version,
          version
        );
        
        existing.version = resolvedVersion;
      }
    } else {
      this.requirements.set(packageName, {
        name: packageName,
        version,
        requiredBy: [requiredBy]
      });
    }
  }
  
  private resolveVersionConflict(version1: string, version2: string): string {
    // Simple semantic version comparison
    const v1Parts = version1.replace(/[^\d.]/g, '').split('.').map(Number);
    const v2Parts = version2.replace(/[^\d.]/g, '').split('.').map(Number);
    
    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
      const v1Part = v1Parts[i] || 0;
      const v2Part = v2Parts[i] || 0;
      
      if (v1Part > v2Part) return version1;
      if (v2Part > v1Part) return version2;
    }
    
    return version1; // Equal versions, return first
  }
  
  validateCompatibility(): { isCompatible: boolean; issues: string[] } {
    const issues: string[] = [];
    
    this.requirements.forEach((requirement, packageName) => {
      if (requirement.conflicts) {
        requirement.conflicts.forEach(conflictingPackage => {
          if (this.requirements.has(conflictingPackage)) {
            issues.push(
              `${packageName} conflicts with ${conflictingPackage}`
            );
          }
        });
      }
    });
    
    return {
      isCompatible: issues.length === 0,
      issues
    };
  }
  
  getResolvedVersions(): Record<string, string> {
    return Object.fromEntries(this.resolvedVersions);
  }
  
  generateSharedConfig(): Record<string, any> {
    const config: Record<string, any> = {};
    
    this.requirements.forEach((requirement, packageName) => {
      config[packageName] = {
        singleton: true,
        requiredVersion: requirement.version,
        eager: packageName.includes('react'),
        strictVersion: packageName.includes('react')
      };
    });
    
    return config;
  }
}

export const versionManager = new VersionManager();
{% endraw %}
```

### Shared Library Factory
```typescript
{% raw %}
// shared/src/factory/SharedLibraryFactory.ts
interface SharedLibraryConfig {
  name: string;
  version: string;
  factory: () => Promise<any>;
  dependencies?: string[];
}

class SharedLibraryFactory {
  private libraries = new Map<string, SharedLibraryConfig>();
  private instances = new Map<string, any>();
  private loading = new Map<string, Promise<any>>();
  
  register(config: SharedLibraryConfig): void {
    this.libraries.set(config.name, config);
  }
  
  async get<T = any>(libraryName: string): Promise<T> {
    // Return cached instance if available
    if (this.instances.has(libraryName)) {
      return this.instances.get(libraryName);
    }
    
    // Return loading promise if already loading
    if (this.loading.has(libraryName)) {
      return this.loading.get(libraryName);
    }
    
    const config = this.libraries.get(libraryName);
    if (!config) {
      throw new Error(`Shared library ${libraryName} not registered`);
    }
    
    // Load dependencies first
    if (config.dependencies) {
      await Promise.all(
        config.dependencies.map(dep => this.get(dep))
      );
    }
    
    // Create loading promise
    const loadingPromise = this.loadLibrary(config);
    this.loading.set(libraryName, loadingPromise);
    
    try {
      const instance = await loadingPromise;
      this.instances.set(libraryName, instance);
      this.loading.delete(libraryName);
      
      return instance;
    } catch (error) {
      this.loading.delete(libraryName);
      throw error;
    }
  }
  
  private async loadLibrary(config: SharedLibraryConfig): Promise<any> {
    try {
      console.log(`Loading shared library: ${config.name}@${config.version}`);
      
      const startTime = performance.now();
      const instance = await config.factory();
      const loadTime = performance.now() - startTime;
      
      console.log(
        `Loaded ${config.name} in ${Math.round(loadTime)}ms`
      );
      
      return instance;
    } catch (error) {
      console.error(`Failed to load shared library ${config.name}:`, error);
      throw error;
    }
  }
  
  isLoaded(libraryName: string): boolean {
    return this.instances.has(libraryName);
  }
  
  unload(libraryName: string): void {
    this.instances.delete(libraryName);
    this.loading.delete(libraryName);
  }
  
  getLoadedLibraries(): string[] {
    return Array.from(this.instances.keys());
  }
  
  clear(): void {
    this.instances.clear();
    this.loading.clear();
  }
}

export const sharedLibraryFactory = new SharedLibraryFactory();

// Register common shared libraries
sharedLibraryFactory.register({
  name: 'react',
  version: '18.2.0',
  factory: () => import('react')
});

sharedLibraryFactory.register({
  name: 'react-dom',
  version: '18.2.0',
  factory: () => import('react-dom'),
  dependencies: ['react']
});

sharedLibraryFactory.register({
  name: 'react-router-dom',
  version: '6.8.0',
  factory: () => import('react-router-dom'),
  dependencies: ['react']
});
{% endraw %}
```

This comprehensive guide covers Module Federation and micro-frontend architecture patterns, providing production-ready examples for building scalable, distributed React applications. The patterns shown enable teams to work independently while maintaining consistency and performance across the entire application ecosystem.
