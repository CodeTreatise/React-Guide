# PWA Implementation & Advanced Optimization

## Table of Contents
1. [Progressive Web App Fundamentals](#progressive-web-app-fundamentals)
2. [Service Worker Implementation](#service-worker-implementation)
3. [Caching Strategies](#caching-strategies)
4. [Offline Functionality](#offline-functionality)
5. [Web App Manifest](#web-app-manifest)
6. [Performance Optimization](#performance-optimization)
7. [Bundle Analysis & Monitoring](#bundle-analysis--monitoring)
8. [Production Optimization](#production-optimization)

## Progressive Web App Fundamentals

### PWA Architecture Overview
```typescript
// types/pwa.ts
export interface PWAConfig {
  name: string;
  shortName: string;
  description: string;
  themeColor: string;
  backgroundColor: string;
  display: 'standalone' | 'fullscreen' | 'minimal-ui' | 'browser';
  orientation: 'portrait' | 'landscape' | 'any';
  scope: string;
  startUrl: string;
  icons: PWAIcon[];
  serviceWorker: {
    enabled: boolean;
    scope: string;
    updateViaCache: 'imports' | 'all' | 'none';
  };
  installPrompt: {
    enabled: boolean;
    deferredDays: number;
  };
  notifications: {
    enabled: boolean;
    vapidKey?: string;
  };
}

export interface PWAIcon {
  src: string;
  sizes: string;
  type: string;
  purpose?: 'any' | 'maskable' | 'monochrome';
}

export interface InstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}
```

### PWA Service Setup
```typescript
{% raw %}
{% raw %}
// services/PWAService.ts
class PWAService {
  private config: PWAConfig;
  private deferredPrompt: InstallPromptEvent | null = null;
  private isInstalled = false;
  private registration: ServiceWorkerRegistration | null = null;
  
  constructor(config: PWAConfig) {
    this.config = config;
    this.init();
  }
  
  private async init(): Promise<void> {
    // Check for PWA support
    if (!this.isPWASupported()) {
      console.warn('PWA features not supported in this browser');
      return;
    }
    
    // Register service worker
    if (this.config.serviceWorker.enabled) {
      await this.registerServiceWorker();
    }
    
    // Setup install prompt
    if (this.config.installPrompt.enabled) {
      this.setupInstallPrompt();
    }
    
    // Setup notification handling
    if (this.config.notifications.enabled) {
      await this.setupNotifications();
    }
    
    // Check if already installed
    this.checkInstallationStatus();
  }
  
  private isPWASupported(): boolean {
    return (
      'serviceWorker' in navigator &&
      'manifest' in document &&
      'PushManager' in window &&
      'Notification' in window
    );
  }
  
  private async registerServiceWorker(): Promise<void> {
    try {
      this.registration = await navigator.serviceWorker.register('/sw.js', {
        scope: this.config.serviceWorker.scope,
        updateViaCache: this.config.serviceWorker.updateViaCache
      });
      
      console.log('Service Worker registered:', this.registration);
      
      // Listen for updates
      this.registration.addEventListener('updatefound', () => {
        const newWorker = this.registration!.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New content available
              this.notifyUpdate();
            }
          });
        }
      });
      
      // Listen for controlling worker changes
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
      });
      
    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  }
  
  private setupInstallPrompt(): void {
    window.addEventListener('beforeinstallprompt', (e) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault();
      
      // Check if enough time has passed since last dismissal
      const lastDismissed = localStorage.getItem('pwa-install-dismissed');
      if (lastDismissed) {
        const daysSinceDismissal = (Date.now() - parseInt(lastDismissed)) / (1000 * 60 * 60 * 24);
        if (daysSinceDismissal < this.config.installPrompt.deferredDays) {
          return;
        }
      }
      
      // Store the event for later use
      this.deferredPrompt = e as InstallPromptEvent;
      
      // Show custom install prompt
      this.showInstallPrompt();
    });
    
    // Listen for successful installation
    window.addEventListener('appinstalled', () => {
      console.log('PWA was installed');
      this.isInstalled = true;
      this.hideInstallPrompt();
      
      // Track installation
      this.trackEvent('pwa_installed');
    });
  }
  
  private async setupNotifications(): Promise<void> {
    if (!('Notification' in window)) {
      console.warn('Notifications not supported');
      return;
    }
    
    // Request permission if not already granted
    if (Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      console.log('Notification permission:', permission);
    }
    
    // Setup push notifications if supported
    if ('PushManager' in window && this.registration && this.config.notifications.vapidKey) {
      try {
        const subscription = await this.registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this.urlBase64ToUint8Array(this.config.notifications.vapidKey)
        });
        
        // Send subscription to server
        await this.sendSubscriptionToServer(subscription);
      } catch (error) {
        console.error('Failed to subscribe for push notifications:', error);
      }
    }
  }
  
  async showInstallPrompt(): Promise<void> {
    if (!this.deferredPrompt) return;
    
    // Create custom install prompt UI
    const installModal = this.createInstallModal();
    document.body.appendChild(installModal);
    
    // Handle install button click
    const installButton = installModal.querySelector('#install-button');
    const dismissButton = installModal.querySelector('#dismiss-button');
    
    installButton?.addEventListener('click', async () => {
      if (this.deferredPrompt) {
        await this.deferredPrompt.prompt();
        const choiceResult = await this.deferredPrompt.userChoice;
        
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted the install prompt');
          this.trackEvent('pwa_install_accepted');
        } else {
          console.log('User dismissed the install prompt');
          localStorage.setItem('pwa-install-dismissed', Date.now().toString());
          this.trackEvent('pwa_install_dismissed');
        }
        
        this.deferredPrompt = null;
        document.body.removeChild(installModal);
      }
    });
    
    dismissButton?.addEventListener('click', () => {
      localStorage.setItem('pwa-install-dismissed', Date.now().toString());
      document.body.removeChild(installModal);
      this.trackEvent('pwa_install_dismissed');
    });
  }
  
  private createInstallModal(): HTMLElement {
    const modal = document.createElement('div');
    modal.className = 'pwa-install-modal';
    modal.innerHTML = `
      <div class="pwa-install-content">
        <div class="pwa-install-header">
          <img src="${this.config.icons[0]?.src}" alt="${this.config.name}" class="pwa-install-icon">
          <div>
            <h3>${this.config.name}</h3>
            <p>Install this app for a better experience</p>
          </div>
        </div>
        <div class="pwa-install-features">
          <ul>
            <li>✓ Works offline</li>
            <li>✓ Fast loading</li>
            <li>✓ Push notifications</li>
            <li>✓ Native app experience</li>
          </ul>
        </div>
        <div class="pwa-install-actions">
          <button id="dismiss-button" class="pwa-button secondary">Not now</button>
          <button id="install-button" class="pwa-button primary">Install</button>
        </div>
      </div>
    `;
    
    return modal;
  }
  
  private hideInstallPrompt(): void {
    const modal = document.querySelector('.pwa-install-modal');
    if (modal) {
      document.body.removeChild(modal);
    }
  }
  
  private notifyUpdate(): void {
    // Show update notification
    const updateBanner = document.createElement('div');
    updateBanner.className = 'pwa-update-banner';
    updateBanner.innerHTML = `
      <div class="pwa-update-content">
        <span>A new version is available!</span>
        <button id="update-button" class="pwa-button primary">Update</button>
        <button id="dismiss-update" class="pwa-button secondary">×</button>
      </div>
    `;
    
    document.body.appendChild(updateBanner);
    
    // Handle update button click
    updateBanner.querySelector('#update-button')?.addEventListener('click', () => {
      if (this.registration?.waiting) {
        this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      }
    });
    
    // Handle dismiss button click
    updateBanner.querySelector('#dismiss-update')?.addEventListener('click', () => {
      document.body.removeChild(updateBanner);
    });
  }
  
  private checkInstallationStatus(): void {
    // Check if running as installed PWA
    this.isInstalled = window.matchMedia('(display-mode: standalone)').matches ||
                     (window.navigator as any).standalone === true;
    
    if (this.isInstalled) {
      document.body.classList.add('pwa-installed');
    }
  }
  
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  }
  
  private async sendSubscriptionToServer(subscription: PushSubscription): Promise<void> {
    try {
      await fetch('/api/push-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(subscription)
      });
    } catch (error) {
      console.error('Failed to send subscription to server:', error);
    }
  }
  
  private trackEvent(event: string): void {
    // Analytics tracking
    if (typeof gtag !== 'undefined') {
      gtag('event', event, {
        event_category: 'PWA',
        event_label: this.config.name
      });
    }
  }
  
  // Public methods
  async updateServiceWorker(): Promise<void> {
    if (this.registration) {
      await this.registration.update();
    }
  }
  
  async unregisterServiceWorker(): Promise<void> {
    if (this.registration) {
      await this.registration.unregister();
    }
  }
  
  getInstallationStatus(): boolean {
    return this.isInstalled;
  }
  
  async showNotification(title: string, options?: NotificationOptions): Promise<void> {
    if (Notification.permission === 'granted' && this.registration) {
      await this.registration.showNotification(title, {
        icon: this.config.icons[0]?.src,
        badge: this.config.icons.find(icon => icon.purpose === 'monochrome')?.src,
        ...options
      });
    }
  }
}
{% endraw %}
{% endraw %}
```

## Service Worker Implementation

### Advanced Service Worker
```javascript
// public/sw.js
const CACHE_NAME = 'app-v1.0.0';
const RUNTIME_CACHE = 'runtime-cache';

// Cache strategies
const CACHE_STRATEGIES = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
  NETWORK_ONLY: 'network-only',
  CACHE_ONLY: 'cache-only'
};

// Assets to cache immediately
const PRECACHE_ASSETS = [
  '/',
  '/static/js/main.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico'
];

// Route configurations
const ROUTE_CONFIG = [
  {
    pattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    cacheName: 'images',
    options: {
      maxEntries: 100,
      maxAgeSeconds: 30 * 24 * 60 * 60 // 30 days
    }
  },
  {
    pattern: /\.(?:js|css)$/,
    strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
    cacheName: 'static-resources',
    options: {
      maxEntries: 50,
      maxAgeSeconds: 24 * 60 * 60 // 1 day
    }
  },
  {
    pattern: /^https:\/\/api\.example\.com\//,
    strategy: CACHE_STRATEGIES.NETWORK_FIRST,
    cacheName: 'api-cache',
    options: {
      maxEntries: 50,
      maxAgeSeconds: 5 * 60, // 5 minutes
      networkTimeoutSeconds: 10
    }
  },
  {
    pattern: /^https:\/\/fonts\.googleapis\.com\//,
    strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
    cacheName: 'google-fonts-stylesheets'
  },
  {
    pattern: /^https:\/\/fonts\.gstatic\.com\//,
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    cacheName: 'google-fonts-webfonts',
    options: {
      maxEntries: 30,
      maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
    }
  }
];

// Install event
self.addEventListener('install', (event) => {
  console.log('Service Worker installing');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caching precache assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => {
        // Force activation
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Precaching failed:', error);
      })
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && !cacheName.startsWith('runtime-')) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Take control of all pages
      self.clients.claim()
    ])
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension requests
  if (url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Find matching route configuration
  const routeConfig = ROUTE_CONFIG.find(config => 
    config.pattern.test(request.url)
  );
  
  if (routeConfig) {
    event.respondWith(
      handleRequest(request, routeConfig)
    );
  } else {
    // Default strategy for unmatched routes
    event.respondWith(
      handleRequest(request, {
        strategy: CACHE_STRATEGIES.NETWORK_FIRST,
        cacheName: RUNTIME_CACHE,
        options: { networkTimeoutSeconds: 3 }
      })
    );
  }
});

// Request handling with different strategies
async function handleRequest(request, config) {
  const { strategy, cacheName = RUNTIME_CACHE, options = {} } = config;
  
  switch (strategy) {
    case CACHE_STRATEGIES.CACHE_FIRST:
      return cacheFirst(request, cacheName, options);
      
    case CACHE_STRATEGIES.NETWORK_FIRST:
      return networkFirst(request, cacheName, options);
      
    case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
      return staleWhileRevalidate(request, cacheName, options);
      
    case CACHE_STRATEGIES.NETWORK_ONLY:
      return fetch(request);
      
    case CACHE_STRATEGIES.CACHE_ONLY:
      return caches.match(request);
      
    default:
      return networkFirst(request, cacheName, options);
  }
}

// Cache first strategy
async function cacheFirst(request, cacheName, options) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
      await enforceMaxEntries(cache, options.maxEntries);
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Cache first strategy failed:', error);
    return new Response('Network error', { status: 408 });
  }
}

// Network first strategy
async function networkFirst(request, cacheName, options) {
  const cache = await caches.open(cacheName);
  
  try {
    const networkResponse = await Promise.race([
      fetch(request),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Network timeout')), 
        (options.networkTimeoutSeconds || 3) * 1000)
      )
    ]);
    
    if (networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
      await enforceMaxEntries(cache, options.maxEntries);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error.message);
    
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response('Offline', { status: 503 });
  }
}

// Stale while revalidate strategy
async function staleWhileRevalidate(request, cacheName, options) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Always try to update in background
  const networkUpdate = fetch(request).then(async (response) => {
    if (response.status === 200) {
      cache.put(request, response.clone());
      await enforceMaxEntries(cache, options.maxEntries);
    }
    return response;
  }).catch(error => {
    console.log('Background update failed:', error.message);
  });
  
  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Wait for network if no cache
  try {
    return await networkUpdate;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

// Cache management
async function enforceMaxEntries(cache, maxEntries) {
  if (!maxEntries) return;
  
  const keys = await cache.keys();
  if (keys.length > maxEntries) {
    // Remove oldest entries
    const entriesToDelete = keys.slice(0, keys.length - maxEntries);
    await Promise.all(entriesToDelete.map(key => cache.delete(key)));
  }
}

// Background sync
self.addEventListener('sync', (event) => {
  console.log('Background sync:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(performBackgroundSync());
  }
});

async function performBackgroundSync() {
  try {
    // Get pending requests from IndexedDB
    const pendingRequests = await getPendingRequests();
    
    for (const request of pendingRequests) {
      try {
        await fetch(request);
        await removePendingRequest(request.id);
      } catch (error) {
        console.error('Background sync failed for request:', error);
      }
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('Push message received');
  
  const options = {
    body: 'You have a new notification',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View',
        icon: '/icon-view.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icon-close.png'
      }
    ]
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.title = data.title || 'Notification';
  }
  
  event.waitUntil(
    self.registration.showNotification('App Notification', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
  console.log('Message received in SW:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      type: 'VERSION',
      version: CACHE_NAME
    });
  }
});

// Utility functions for IndexedDB operations
async function getPendingRequests() {
  // Implementation for getting pending requests from IndexedDB
  return [];
}

async function removePendingRequest(id) {
  // Implementation for removing request from IndexedDB
}

async function addPendingRequest(request) {
  // Implementation for adding request to IndexedDB
}
```

## Caching Strategies

### Advanced Cache Manager
```typescript
{% raw %}
{% raw %}
// utils/CacheManager.ts
interface CacheConfig {
  name: string;
  version: string;
  maxSize: number;
  maxAge: number;
  strategy: 'lru' | 'lfu' | 'fifo';
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  accessCount: number;
  lastAccess: number;
  size: number;
}

class CacheManager<T = any> {
  private cache = new Map<string, CacheEntry<T>>();
  private config: CacheConfig;
  private totalSize = 0;
  
  constructor(config: CacheConfig) {
    this.config = config;
    this.loadFromStorage();
  }
  
  set(key: string, data: T, ttl?: number): void {
    const size = this.calculateSize(data);
    const now = Date.now();
    
    // Remove existing entry
    if (this.cache.has(key)) {
      this.totalSize -= this.cache.get(key)!.size;
    }
    
    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      accessCount: 0,
      lastAccess: now,
      size
    };
    
    // Check if we need to make space
    this.ensureSpace(size);
    
    this.cache.set(key, entry);
    this.totalSize += size;
    
    this.saveToStorage();
  }
  
  get(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }
    
    // Check if expired
    const now = Date.now();
    const age = now - entry.timestamp;
    
    if (age > this.config.maxAge) {
      this.delete(key);
      return null;
    }
    
    // Update access statistics
    entry.accessCount++;
    entry.lastAccess = now;
    
    return entry.data;
  }
  
  delete(key: string): boolean {
    const entry = this.cache.get(key);
    
    if (entry) {
      this.totalSize -= entry.size;
      this.cache.delete(key);
      this.saveToStorage();
      return true;
    }
    
    return false;
  }
  
  has(key: string): boolean {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return false;
    }
    
    // Check if expired
    const age = Date.now() - entry.timestamp;
    
    if (age > this.config.maxAge) {
      this.delete(key);
      return false;
    }
    
    return true;
  }
  
  clear(): void {
    this.cache.clear();
    this.totalSize = 0;
    this.clearStorage();
  }
  
  private ensureSpace(requiredSize: number): void {
    while (this.totalSize + requiredSize > this.config.maxSize && this.cache.size > 0) {
      const keyToRemove = this.selectEvictionKey();
      if (keyToRemove) {
        this.delete(keyToRemove);
      } else {
        break;
      }
    }
  }
  
  private selectEvictionKey(): string | null {
    if (this.cache.size === 0) {
      return null;
    }
    
    const entries = Array.from(this.cache.entries());
    
    switch (this.config.strategy) {
      case 'lru':
        return entries.reduce((oldest, [key, entry]) =>
          entry.lastAccess < this.cache.get(oldest)!.lastAccess ? key : oldest
        , entries[0][0]);
        
      case 'lfu':
        return entries.reduce((least, [key, entry]) =>
          entry.accessCount < this.cache.get(least)!.accessCount ? key : least
        , entries[0][0]);
        
      case 'fifo':
        return entries.reduce((oldest, [key, entry]) =>
          entry.timestamp < this.cache.get(oldest)!.timestamp ? key : oldest
        , entries[0][0]);
        
      default:
        return entries[0][0];
    }
  }
  
  private calculateSize(data: T): number {
    return JSON.stringify(data).length;
  }
  
  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(`cache-${this.config.name}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        this.cache = new Map(parsed.entries);
        this.totalSize = parsed.totalSize;
      }
    } catch (error) {
      console.error('Failed to load cache from storage:', error);
    }
  }
  
  private saveToStorage(): void {
    try {
      const data = {
        entries: Array.from(this.cache.entries()),
        totalSize: this.totalSize
      };
      
      localStorage.setItem(`cache-${this.config.name}`, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save cache to storage:', error);
    }
  }
  
  private clearStorage(): void {
    localStorage.removeItem(`cache-${this.config.name}`);
  }
  
  getStats() {
    return {
      size: this.cache.size,
      totalSize: this.totalSize,
      maxSize: this.config.maxSize,
      utilization: (this.totalSize / this.config.maxSize) * 100,
      strategy: this.config.strategy
    };
  }
}

// HTTP Cache with Service Worker integration
class HTTPCache {
  private static instance: HTTPCache;
  private cacheManager: CacheManager<Response>;
  
  private constructor() {
    this.cacheManager = new CacheManager({
      name: 'http-cache',
      version: '1.0.0',
      maxSize: 50 * 1024 * 1024, // 50MB
      maxAge: 60 * 60 * 1000, // 1 hour
      strategy: 'lru'
    });
  }
  
  static getInstance(): HTTPCache {
    if (!HTTPCache.instance) {
      HTTPCache.instance = new HTTPCache();
    }
    return HTTPCache.instance;
  }
  
  async fetch(url: string, options?: RequestInit): Promise<Response> {
    const cacheKey = this.getCacheKey(url, options);
    
    // Try cache first
    const cachedResponse = this.cacheManager.get(cacheKey);
    if (cachedResponse) {
      return cachedResponse.clone();
    }
    
    try {
      // Fetch from network
      const response = await fetch(url, options);
      
      // Cache successful responses
      if (response.ok) {
        this.cacheManager.set(cacheKey, response.clone());
      }
      
      return response;
    } catch (error) {
      // Return cached version if network fails
      const fallbackResponse = this.cacheManager.get(cacheKey);
      if (fallbackResponse) {
        return fallbackResponse.clone();
      }
      
      throw error;
    }
  }
  
  private getCacheKey(url: string, options?: RequestInit): string {
    const method = options?.method || 'GET';
    const headers = JSON.stringify(options?.headers || {});
    return `${method}:${url}:${headers}`;
  }
  
  invalidate(url: string): void {
    // Remove all cache entries for this URL
    Array.from(this.cacheManager['cache'].keys())
      .filter(key => key.includes(url))
      .forEach(key => this.cacheManager.delete(key));
  }
  
  clear(): void {
    this.cacheManager.clear();
  }
}

export const httpCache = HTTPCache.getInstance();
{% endraw %}
{% endraw %}
```

## Offline Functionality

### Offline Data Synchronization
```typescript
{% raw %}
{% raw %}
// services/OfflineSync.ts
interface SyncOperation {
  id: string;
  type: 'create' | 'update' | 'delete';
  entity: string;
  data: any;
  timestamp: number;
  retryCount: number;
}

class OfflineSync {
  private db: IDBDatabase | null = null;
  private syncQueue: SyncOperation[] = [];
  private isOnline = navigator.onLine;
  private syncInProgress = false;
  
  constructor() {
    this.initDB();
    this.setupEventListeners();
    this.loadSyncQueue();
  }
  
  private async initDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('OfflineDB', 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // Create object stores
        if (!db.objectStoreNames.contains('syncQueue')) {
          const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
          syncStore.createIndex('timestamp', 'timestamp');
          syncStore.createIndex('entity', 'entity');
        }
        
        if (!db.objectStoreNames.contains('entities')) {
          const entityStore = db.createObjectStore('entities', { keyPath: 'id' });
          entityStore.createIndex('type', 'type');
          entityStore.createIndex('lastModified', 'lastModified');
        }
      };
    });
  }
  
  private setupEventListeners(): void {
    window.addEventListener('online', () => {
      console.log('Back online, starting sync...');
      this.isOnline = true;
      this.processSyncQueue();
    });
    
    window.addEventListener('offline', () => {
      console.log('Gone offline');
      this.isOnline = false;
    });
    
    // Periodic sync when online
    setInterval(() => {
      if (this.isOnline && !this.syncInProgress) {
        this.processSyncQueue();
      }
    }, 30000); // 30 seconds
  }
  
  async create(entity: string, data: any): Promise<string> {
    const id = this.generateId();
    const operation: SyncOperation = {
      id,
      type: 'create',
      entity,
      data: { ...data, id },
      timestamp: Date.now(),
      retryCount: 0
    };
    
    // Store locally
    await this.storeEntity(entity, operation.data);
    
    if (this.isOnline) {
      try {
        await this.syncOperation(operation);
        return id;
      } catch (error) {
        // Queue for later sync
        await this.queueOperation(operation);
        return id;
      }
    } else {
      // Queue for later sync
      await this.queueOperation(operation);
      return id;
    }
  }
  
  async update(entity: string, id: string, data: any): Promise<void> {
    const operation: SyncOperation = {
      id: this.generateId(),
      type: 'update',
      entity,
      data: { ...data, id },
      timestamp: Date.now(),
      retryCount: 0
    };
    
    // Update locally
    await this.updateEntity(entity, id, operation.data);
    
    if (this.isOnline) {
      try {
        await this.syncOperation(operation);
      } catch (error) {
        await this.queueOperation(operation);
      }
    } else {
      await this.queueOperation(operation);
    }
  }
  
  async delete(entity: string, id: string): Promise<void> {
    const operation: SyncOperation = {
      id: this.generateId(),
      type: 'delete',
      entity,
      data: { id },
      timestamp: Date.now(),
      retryCount: 0
    };
    
    // Mark as deleted locally
    await this.markEntityDeleted(entity, id);
    
    if (this.isOnline) {
      try {
        await this.syncOperation(operation);
        await this.removeEntity(entity, id);
      } catch (error) {
        await this.queueOperation(operation);
      }
    } else {
      await this.queueOperation(operation);
    }
  }
  
  async read(entity: string, id?: string): Promise<any> {
    if (id) {
      return this.getEntity(entity, id);
    } else {
      return this.getAllEntities(entity);
    }
  }
  
  private async syncOperation(operation: SyncOperation): Promise<void> {
    const url = `/api/${operation.entity}`;
    let method: string;
    let body: string | undefined;
    
    switch (operation.type) {
      case 'create':
        method = 'POST';
        body = JSON.stringify(operation.data);
        break;
      case 'update':
        method = 'PUT';
        body = JSON.stringify(operation.data);
        break;
      case 'delete':
        method = 'DELETE';
        break;
      default:
        throw new Error(`Unknown operation type: ${operation.type}`);
    }
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body
    });
    
    if (!response.ok) {
      throw new Error(`Sync failed: ${response.statusText}`);
    }
    
    // Handle server response
    if (operation.type !== 'delete' && response.headers.get('content-type')?.includes('application/json')) {
      const serverData = await response.json();
      await this.updateEntity(operation.entity, operation.data.id, serverData);
    }
  }
  
  private async processSyncQueue(): Promise<void> {
    if (this.syncInProgress || !this.isOnline) {
      return;
    }
    
    this.syncInProgress = true;
    
    try {
      const operations = [...this.syncQueue];
      
      for (const operation of operations) {
        try {
          await this.syncOperation(operation);
          await this.removeSyncOperation(operation.id);
          this.syncQueue = this.syncQueue.filter(op => op.id !== operation.id);
          
          console.log(`Synced operation: ${operation.type} ${operation.entity}`);
        } catch (error) {
          console.error(`Failed to sync operation ${operation.id}:`, error);
          
          // Increment retry count
          operation.retryCount++;
          
          // Remove from queue if max retries reached
          if (operation.retryCount >= 3) {
            console.error(`Max retries reached for operation ${operation.id}, removing from queue`);
            await this.removeSyncOperation(operation.id);
            this.syncQueue = this.syncQueue.filter(op => op.id !== operation.id);
          } else {
            await this.updateSyncOperation(operation);
          }
        }
      }
    } finally {
      this.syncInProgress = false;
    }
  }
  
  private async queueOperation(operation: SyncOperation): Promise<void> {
    this.syncQueue.push(operation);
    await this.storeSyncOperation(operation);
  }
  
  private async loadSyncQueue(): Promise<void> {
    if (!this.db) return;
    
    const transaction = this.db.transaction(['syncQueue'], 'readonly');
    const store = transaction.objectStore('syncQueue');
    const request = store.getAll();
    
    return new Promise((resolve, reject) => {
      request.onsuccess = () => {
        this.syncQueue = request.result;
        resolve();
      };
      request.onerror = () => reject(request.error);
    });
  }
  
  private async storeSyncOperation(operation: SyncOperation): Promise<void> {
    if (!this.db) return;
    
    const transaction = this.db.transaction(['syncQueue'], 'readwrite');
    const store = transaction.objectStore('syncQueue');
    
    return new Promise((resolve, reject) => {
      const request = store.put(operation);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
  
  private async removeSyncOperation(id: string): Promise<void> {
    if (!this.db) return;
    
    const transaction = this.db.transaction(['syncQueue'], 'readwrite');
    const store = transaction.objectStore('syncQueue');
    
    return new Promise((resolve, reject) => {
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
  
  private async updateSyncOperation(operation: SyncOperation): Promise<void> {
    await this.storeSyncOperation(operation);
  }
  
  private async storeEntity(type: string, data: any): Promise<void> {
    if (!this.db) return;
    
    const entity = {
      ...data,
      type,
      lastModified: Date.now(),
      _deleted: false
    };
    
    const transaction = this.db.transaction(['entities'], 'readwrite');
    const store = transaction.objectStore('entities');
    
    return new Promise((resolve, reject) => {
      const request = store.put(entity);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
  
  private async updateEntity(type: string, id: string, data: any): Promise<void> {
    const existing = await this.getEntity(type, id);
    const updated = {
      ...existing,
      ...data,
      lastModified: Date.now()
    };
    
    await this.storeEntity(type, updated);
  }
  
  private async getEntity(type: string, id: string): Promise<any> {
    if (!this.db) return null;
    
    const transaction = this.db.transaction(['entities'], 'readonly');
    const store = transaction.objectStore('entities');
    
    return new Promise((resolve, reject) => {
      const request = store.get(id);
      request.onsuccess = () => {
        const entity = request.result;
        if (entity && entity.type === type && !entity._deleted) {
          resolve(entity);
        } else {
          resolve(null);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }
  
  private async getAllEntities(type: string): Promise<any[]> {
    if (!this.db) return [];
    
    const transaction = this.db.transaction(['entities'], 'readonly');
    const store = transaction.objectStore('entities');
    const index = store.index('type');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(type);
      request.onsuccess = () => {
        const entities = request.result.filter(entity => !entity._deleted);
        resolve(entities);
      };
      request.onerror = () => reject(request.error);
    });
  }
  
  private async markEntityDeleted(type: string, id: string): Promise<void> {
    const entity = await this.getEntity(type, id);
    if (entity) {
      entity._deleted = true;
      entity.lastModified = Date.now();
      await this.storeEntity(type, entity);
    }
  }
  
  private async removeEntity(type: string, id: string): Promise<void> {
    if (!this.db) return;
    
    const transaction = this.db.transaction(['entities'], 'readwrite');
    const store = transaction.objectStore('entities');
    
    return new Promise((resolve, reject) => {
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
  
  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }
  
  // Public methods
  getQueueStatus() {
    return {
      queueLength: this.syncQueue.length,
      isOnline: this.isOnline,
      syncInProgress: this.syncInProgress
    };
  }
  
  async forceSyncNow(): Promise<void> {
    if (this.isOnline) {
      await this.processSyncQueue();
    }
  }
  
  clearQueue(): void {
    this.syncQueue = [];
    // Clear from IndexedDB as well
    if (this.db) {
      const transaction = this.db.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      store.clear();
    }
  }
}

export const offlineSync = new OfflineSync();
{% endraw %}
{% endraw %}
```

## Web App Manifest

### Dynamic Manifest Generation
```typescript
{% raw %}
{% raw %}
// utils/ManifestGenerator.ts
interface ManifestConfig {
  name: string;
  shortName: string;
  description: string;
  themeColor: string;
  backgroundColor: string;
  display: 'standalone' | 'fullscreen' | 'minimal-ui' | 'browser';
  orientation: 'portrait' | 'landscape' | 'any' | 'natural';
  scope: string;
  startUrl: string;
  icons: Array<{
    src: string;
    sizes: string;
    type: string;
    purpose?: 'any' | 'maskable' | 'monochrome';
  }>;
  shortcuts?: Array<{
    name: string;
    shortName?: string;
    description?: string;
    url: string;
    icons?: Array<{
      src: string;
      sizes: string;
      type?: string;
    }>;
  }>;
  categories?: string[];
  screenshots?: Array<{
    src: string;
    sizes: string;
    type: string;
    platform?: 'wide' | 'narrow';
    label?: string;
  }>;
}

class ManifestGenerator {
  private config: ManifestConfig;
  
  constructor(config: ManifestConfig) {
    this.config = config;
  }
  
  generate(): string {
    const manifest = {
      name: this.config.name,
      short_name: this.config.shortName,
      description: this.config.description,
      start_url: this.config.startUrl,
      scope: this.config.scope,
      display: this.config.display,
      orientation: this.config.orientation,
      theme_color: this.config.themeColor,
      background_color: this.config.backgroundColor,
      icons: this.config.icons,
      
      // Optional features
      ...(this.config.shortcuts && { shortcuts: this.config.shortcuts }),
      ...(this.config.categories && { categories: this.config.categories }),
      ...(this.config.screenshots && { screenshots: this.config.screenshots }),
      
      // PWA enhancements
      lang: 'en',
      dir: 'ltr',
      prefer_related_applications: false,
      
      // Share target (for sharing to your PWA)
      share_target: {
        action: '/share',
        method: 'POST',
        enctype: 'multipart/form-data',
        params: {
          title: 'title',
          text: 'text',
          url: 'url',
          files: [
            {
              name: 'file',
              accept: ['image/*', 'video/*']
            }
          ]
        }
      },
      
      // Protocol handlers
      protocol_handlers: [
        {
          protocol: 'web+myapp',
          url: '/handle-protocol?url=%s'
        }
      ],
      
      // File handlers
      file_handlers: [
        {
          action: '/open-file',
          accept: {
            'text/plain': ['.txt'],
            'application/json': ['.json']
          }
        }
      ]
    };
    
    return JSON.stringify(manifest, null, 2);
  }
  
  generateIconSet(baseIcon: string): Array<{ src: string; sizes: string; type: string; purpose?: string }> {
    const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
    const icons: Array<{ src: string; sizes: string; type: string; purpose?: string }> = [];
    
    // Regular icons
    sizes.forEach(size => {
      icons.push({
        src: `/icons/icon-${size}x${size}.png`,
        sizes: `${size}x${size}`,
        type: 'image/png'
      });
    });
    
    // Maskable icons
    sizes.forEach(size => {
      icons.push({
        src: `/icons/maskable-icon-${size}x${size}.png`,
        sizes: `${size}x${size}`,
        type: 'image/png',
        purpose: 'maskable'
      });
    });
    
    // Monochrome icons
    icons.push({
      src: '/icons/monochrome-icon.svg',
      sizes: 'any',
      type: 'image/svg+xml',
      purpose: 'monochrome'
    });
    
    return icons;
  }
  
  async injectManifest(): Promise<void> {
    const manifestJson = this.generate();
    const blob = new Blob([manifestJson], { type: 'application/json' });
    const manifestUrl = URL.createObjectURL(blob);
    
    // Remove existing manifest link
    const existingLink = document.querySelector('link[rel="manifest"]');
    if (existingLink) {
      existingLink.remove();
    }
    
    // Add new manifest link
    const link = document.createElement('link');
    link.rel = 'manifest';
    link.href = manifestUrl;
    document.head.appendChild(link);
    
    // Add theme color meta tag
    const themeColorMeta = document.createElement('meta');
    themeColorMeta.name = 'theme-color';
    themeColorMeta.content = this.config.themeColor;
    document.head.appendChild(themeColorMeta);
    
    // Add apple-specific meta tags
    this.addAppleMetaTags();
  }
  
  private addAppleMetaTags(): void {
    // Apple-specific meta tags for iOS
    const appleMetas = [
      { name: 'apple-mobile-web-app-capable', content: 'yes' },
      { name: 'apple-mobile-web-app-status-bar-style', content: 'default' },
      { name: 'apple-mobile-web-app-title', content: this.config.shortName }
    ];
    
    appleMetas.forEach(meta => {
      const metaTag = document.createElement('meta');
      metaTag.name = meta.name;
      metaTag.content = meta.content;
      document.head.appendChild(metaTag);
    });
    
    // Apple touch icons
    const appleTouchIconSizes = [57, 60, 72, 76, 114, 120, 144, 152, 180];
    appleTouchIconSizes.forEach(size => {
      const link = document.createElement('link');
      link.rel = 'apple-touch-icon';
      link.sizes = `${size}x${size}`;
      link.href = `/icons/apple-touch-icon-${size}x${size}.png`;
      document.head.appendChild(link);
    });
    
    // Apple splash screens
    const splashScreens = [
      { media: '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)', href: '/splash/iphone5_splash.png' },
      { media: '(device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2)', href: '/splash/iphone6_splash.png' },
      { media: '(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3)', href: '/splash/iphonex_splash.png' },
      { media: '(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 2)', href: '/splash/iphonexr_splash.png' },
      { media: '(device-width: 414px) and (device-height: 896px) and (-webkit-device-pixel-ratio: 3)', href: '/splash/iphonexsmax_splash.png' },
      { media: '(device-width: 768px) and (device-height: 1024px) and (-webkit-device-pixel-ratio: 2)', href: '/splash/ipad_splash.png' },
      { media: '(device-width: 834px) and (device-height: 1194px) and (-webkit-device-pixel-ratio: 2)', href: '/splash/ipadpro1_splash.png' },
      { media: '(device-width: 1024px) and (device-height: 1366px) and (-webkit-device-pixel-ratio: 2)', href: '/splash/ipadpro2_splash.png' }
    ];
    
    splashScreens.forEach(splash => {
      const link = document.createElement('link');
      link.rel = 'apple-touch-startup-image';
      link.media = splash.media;
      link.href = splash.href;
      document.head.appendChild(link);
    });
  }
}

// Usage example
const manifestConfig: ManifestConfig = {
  name: 'My React PWA',
  shortName: 'ReactPWA',
  description: 'A powerful Progressive Web App built with React',
  themeColor: '#000000',
  backgroundColor: '#ffffff',
  display: 'standalone',
  orientation: 'portrait',
  scope: '/',
  startUrl: '/',
  icons: [
    {
      src: '/icons/icon-192x192.png',
      sizes: '192x192',
      type: 'image/png'
    },
    {
      src: '/icons/icon-512x512.png',
      sizes: '512x512',
      type: 'image/png'
    },
    {
      src: '/icons/maskable-icon-512x512.png',
      sizes: '512x512',
      type: 'image/png',
      purpose: 'maskable'
    }
  ],
  shortcuts: [
    {
      name: 'Dashboard',
      shortName: 'Dashboard',
      description: 'View your dashboard',
      url: '/dashboard',
      icons: [
        {
          src: '/icons/dashboard-icon.png',
          sizes: '96x96',
          type: 'image/png'
        }
      ]
    },
    {
      name: 'Profile',
      shortName: 'Profile',
      description: 'Manage your profile',
      url: '/profile',
      icons: [
        {
          src: '/icons/profile-icon.png',
          sizes: '96x96',
          type: 'image/png'
        }
      ]
    }
  ],
  categories: ['business', 'productivity'],
  screenshots: [
    {
      src: '/screenshots/desktop-screenshot.png',
      sizes: '1280x720',
      type: 'image/png',
      platform: 'wide',
      label: 'Desktop view of the application'
    },
    {
      src: '/screenshots/mobile-screenshot.png',
      sizes: '375x667',
      type: 'image/png',
      platform: 'narrow',
      label: 'Mobile view of the application'
    }
  ]
};

export const manifestGenerator = new ManifestGenerator(manifestConfig);
{% endraw %}
{% endraw %}
```

This comprehensive guide covers PWA implementation, advanced service worker patterns, sophisticated caching strategies, offline functionality, and performance optimization techniques. The implementations provide production-ready code for building high-performance Progressive Web Apps with React.
