# Module 15: Build Tools

## 📚 Learning Objectives

By the end of this module, you will:
- Master modern build tools (Webpack, Vite, Parcel, esbuild)
- Configure advanced bundling strategies and optimizations
- Implement code splitting and lazy loading techniques
- Set up development and production environments
- Optimize bundle size and loading performance
- Configure module federation for micro-frontends
- Implement progressive web app (PWA) features
- Master asset optimization and caching strategies

## 🎯 Prerequisites

- Completed Modules 1-14
- Understanding of JavaScript modules (ES6+, CommonJS)
- Basic knowledge of Node.js and npm
- Familiarity with command line tools

## 📖 Module Content

### 1. Build Tools Overview

#### **Modern Build Tool Comparison**

| Feature | Webpack | Vite | Parcel | esbuild |
|---------|---------|------|--------|---------|
| **Bundle Speed** | Slow | Fast | Fast | Very Fast |
| **Dev Server** | Good | Excellent | Good | Good |
| **Configuration** | Complex | Simple | Zero-config | Minimal |
| **Ecosystem** | Huge | Growing | Good | Limited |
| **Production** | Excellent | Excellent | Good | Good |
| **HMR** | Good | Excellent | Good | Limited |

#### **Build Tool Selection Guide**
```typescript
// Build tool selection criteria
interface BuildToolCriteria {
  projectSize: 'small' | 'medium' | 'large' | 'enterprise';
  teamSize: number;
  performanceRequirements: 'basic' | 'high' | 'critical';
  configurationComplexity: 'none' | 'minimal' | 'advanced';
  ecosystemNeeds: string[];
}

const selectBuildTool = (criteria: BuildToolCriteria): string => {
  if (criteria.projectSize === 'small' && criteria.configurationComplexity === 'none') {
    return 'Parcel';
  }
  
  if (criteria.performanceRequirements === 'critical') {
    return 'esbuild';
  }
  
  if (criteria.projectSize === 'enterprise' || criteria.configurationComplexity === 'advanced') {
    return 'Webpack';
  }
  
  return 'Vite'; // Default for most modern React projects
};
```

### 2. Webpack Advanced Configuration

#### **Production Webpack Configuration**
```javascript
// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');
const WorkboxPlugin = require('workbox-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';
const isDevelopment = !isProduction;

module.exports = {
  mode: isProduction ? 'production' : 'development',
  
  entry: {
    main: './src/index.tsx',
    vendor: ['react', 'react-dom']
  },
  
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: isProduction 
      ? '[name].[contenthash:8].js' 
      : '[name].js',
    chunkFilename: isProduction 
      ? '[name].[contenthash:8].chunk.js' 
      : '[name].chunk.js',
    publicPath: '/',
    clean: true
  },
  
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@types': path.resolve(__dirname, 'src/types')
    }
  },
  
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              presets: [
                ['@babel/preset-env', { useBuiltIns: 'usage', corejs: 3 }],
                ['@babel/preset-react', { runtime: 'automatic' }],
                '@babel/preset-typescript'
              ],
              plugins: [
                isDevelopment && 'react-refresh/babel'
              ].filter(Boolean)
            }
          }
        ]
      },
      {
        test: /\.css$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: {
                auto: true,
                localIdentName: isProduction 
                  ? '[hash:base64:8]' 
                  : '[name]__[local]--[hash:base64:5]'
              }
            }
          },
          'postcss-loader'
        ]
      },
      {
        test: /\.(scss|sass)$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /\.(png|jpg|jpeg|gif|svg)$/,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8 * 1024 // 8kb
          }
        },
        generator: {
          filename: 'images/[name].[contenthash:8][ext]'
        }
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name].[contenthash:8][ext]'
        }
      }
    ]
  },
  
  optimization: {
    minimize: isProduction,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true
          }
        }
      }),
      new OptimizeCSSAssetsPlugin()
    ],
    
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10
        },
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
          name: 'react',
          chunks: 'all',
          priority: 20
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5,
          reuseExistingChunk: true
        }
      }
    },
    
    runtimeChunk: {
      name: 'runtime'
    }
  },
  
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      minify: isProduction ? {
        removeComments: true,
        collapseWhitespace: true,
        removeRedundantAttributes: true,
        useShortDoctype: true,
        removeEmptyAttributes: true,
        removeStyleLinkTypeAttributes: true,
        keepClosingSlash: true,
        minifyJS: true,
        minifyCSS: true,
        minifyURLs: true
      } : false
    }),
    
    isProduction && new MiniCssExtractPlugin({
      filename: '[name].[contenthash:8].css',
      chunkFilename: '[name].[contenthash:8].chunk.css'
    }),
    
    isProduction && new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8
    }),
    
    isProduction && new WorkboxPlugin.GenerateSW({
      clientsClaim: true,
      skipWaiting: true,
      maximumFileSizeToCacheInBytes: 5 * 1024 * 1024
    }),
    
    process.env.ANALYZE && new BundleAnalyzerPlugin()
  ].filter(Boolean),
  
  devServer: {
    contentBase: path.join(__dirname, 'public'),
    historyApiFallback: true,
    hot: true,
    port: 3000,
    compress: true,
    overlay: {
      warnings: false,
      errors: true
    }
  },
  
  devtool: isProduction ? 'source-map' : 'eval-source-map'
};
```

#### **Advanced Webpack Plugins**
```javascript
// webpack.plugins.js
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const WebpackPwaManifest = require('webpack-pwa-manifest');

// Environment-specific plugins
const environmentPlugins = {
  development: [
    new webpack.HotModuleReplacementPlugin(),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('development'),
      __DEV__: true
    })
  ],
  
  production: [
    new CleanWebpackPlugin(),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production'),
      __DEV__: false
    }),
    new CopyWebpackPlugin({
      patterns: [
        { from: 'public/robots.txt', to: 'robots.txt' },
        { from: 'public/sitemap.xml', to: 'sitemap.xml' }
      ]
    }),
    new WebpackPwaManifest({
      name: 'My React App',
      short_name: 'ReactApp',
      description: 'My awesome React application',
      background_color: '#ffffff',
      theme_color: '#000000',
      start_url: '/',
      display: 'standalone',
      icons: [
        {
          src: path.resolve('src/assets/icon.png'),
          sizes: [96, 128, 192, 256, 384, 512]
        }
      ]
    })
  ]
};
```

### 3. Vite Configuration

#### **Advanced Vite Configuration**
```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { VitePWA } from 'vite-plugin-pwa';
import legacy from '@vitejs/plugin-legacy';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const isProduction = mode === 'production';
  
  return {
    plugins: [
      react({
        // Enable Fast Refresh
        fastRefresh: true,
        
        // Babel configuration
        babel: {
          plugins: [
            ['@babel/plugin-proposal-decorators', { legacy: true }]
          ]
        }
      }),
      
      // Legacy browser support
      legacy({
        targets: ['defaults', 'not IE 11']
      }),
      
      // PWA configuration
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
          maximumFileSizeToCacheInBytes: 3000000
        },
        includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
        manifest: {
          name: 'React Vite App',
          short_name: 'ReactApp',
          description: 'My Awesome React App',
          theme_color: '#ffffff',
          icons: [
            {
              src: 'pwa-192x192.png',
              sizes: '192x192',
              type: 'image/png'
            },
            {
              src: 'pwa-512x512.png',
              sizes: '512x512',
              type: 'image/png'
            }
          ]
        }
      }),
      
      // Bundle analyzer
      isProduction && visualizer({
        filename: 'dist/stats.html',
        open: true
      })
    ].filter(Boolean),
    
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@hooks': resolve(__dirname, 'src/hooks'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@types': resolve(__dirname, 'src/types'),
        '@assets': resolve(__dirname, 'src/assets')
      }
    },
    
    css: {
      modules: {
        localsConvention: 'camelCase',
        generateScopedName: isProduction 
          ? '[hash:base64:8]' 
          : '[name]__[local]___[hash:base64:5]'
      },
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables.scss";`
        }
      }
    },
    
    build: {
      target: 'es2015',
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: true,
      
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
            ui: ['@mui/material', '@emotion/react', '@emotion/styled']
          }
        }
      },
      
      // Chunk size warnings
      chunkSizeWarningLimit: 1000
    },
    
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom'],
      exclude: ['some-large-dependency']
    },
    
    server: {
      port: 3000,
      open: true,
      cors: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },
    
    preview: {
      port: 4173,
      cors: true
    },
    
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString())
    }
  };
});
```

#### **Vite Plugin Development**
```typescript
// plugins/vite-plugin-react-inspector.ts
import { Plugin } from 'vite';

interface ReactInspectorOptions {
  enabled?: boolean;
  hotkey?: string;
}

export function reactInspector(options: ReactInspectorOptions = {}): Plugin {
  const { enabled = true, hotkey = 'ctrl+shift+i' } = options;
  
  return {
    name: 'react-inspector',
    apply: 'serve',
    
    transform(code, id) {
      if (!enabled || !id.includes('.tsx') || !id.includes('.jsx')) {
        return null;
      }
      
      // Add development-only inspection code
      const inspectorCode = `
        if (process.env.NODE_ENV === 'development') {
          // Add click handler for component inspection
          console.log('Component:', '${id}');
        }
      `;
      
      return {
        code: code + inspectorCode,
        map: null
      };
    },
    
    configureServer(server) {
      server.middlewares.use('/__inspect', (req, res, next) => {
        // Handle inspection requests
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ 
          message: 'React Inspector Active',
          hotkey 
        }));
      });
    }
  };
}
```

### 4. Code Splitting and Lazy Loading

#### **Route-based Code Splitting**
```typescript
// src/router/AppRouter.tsx
import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from '@/components/ErrorBoundary';
import LoadingSpinner from '@/components/LoadingSpinner';

// Lazy load route components
const Home = lazy(() => import('@/pages/Home'));
const About = lazy(() => import('@/pages/About'));
const Dashboard = lazy(() => 
  import('@/pages/Dashboard').then(module => ({ 
    default: module.Dashboard 
  }))
);
const Profile = lazy(() => 
  import('@/pages/Profile').catch(() => ({ 
    default: () => <div>Failed to load Profile</div> 
  }))
);

// Preload components on hover
const preloadComponent = (componentImport: () => Promise<any>) => {
  componentImport();
};

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route 
              path="/about" 
              element={
                <div
                  onMouseEnter={() => preloadComponent(() => import('@/pages/About'))}
                >
                  <About />
                </div>
              } 
            />
            <Route path="/dashboard/*" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </BrowserRouter>
  );
};

export default AppRouter;
```

#### **Component-based Code Splitting**
```typescript
// src/components/LazyComponent.tsx
import React, { Suspense, lazy, ComponentType } from 'react';

interface LazyComponentProps {
  factory: () => Promise<{ default: ComponentType<any> }>;
  fallback?: React.ReactNode;
  onError?: (error: Error) => void;
}

const LazyComponent: React.FC<LazyComponentProps> = ({ 
  factory, 
  fallback = <div>Loading...</div>,
  onError,
  ...props 
}) => {
  const Component = lazy(factory);
  
  return (
    <ErrorBoundary onError={onError}>
      <Suspense fallback={fallback}>
        <Component {...props} />
      </Suspense>
    </ErrorBoundary>
  );
};

// Usage example
const DataVisualization = () => (
  <LazyComponent
    factory={() => import('@/components/Charts/AdvancedChart')}
    fallback={<div>Loading chart...</div>}
    onError={(error) => console.error('Chart failed to load:', error)}
  />
);
```

#### **Dynamic Import Utilities**
```typescript
// src/utils/dynamicImport.ts
interface ImportOptions {
  timeout?: number;
  retries?: number;
  fallback?: () => Promise<any>;
}

export async function dynamicImport<T>(
  importFn: () => Promise<T>,
  options: ImportOptions = {}
): Promise<T> {
  const { timeout = 10000, retries = 3, fallback } = options;
  
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Import timeout')), timeout);
      });
      
      const result = await Promise.race([
        importFn(),
        timeoutPromise
      ]) as T;
      
      return result;
    } catch (error) {
      console.warn(`Import attempt ${attempt} failed:`, error);
      
      if (attempt === retries) {
        if (fallback) {
          console.log('Using fallback import');
          return await fallback();
        }
        throw error;
      }
      
      // Exponential backoff
      await new Promise(resolve => 
        setTimeout(resolve, Math.pow(2, attempt) * 1000)
      );
    }
  }
  
  throw new Error('All import attempts failed');
}

// Preload utilities
export const preloadRoute = (routeImport: () => Promise<any>) => {
  // Only preload on good network connections
  if ('connection' in navigator) {
    const connection = (navigator as any).connection;
    if (connection.effectiveType === 'slow-2g' || connection.saveData) {
      return;
    }
  }
  
  requestIdleCallback(() => {
    routeImport().catch(() => {
      // Silently fail preloading
    });
  });
};

// Resource hints
export const addResourceHint = (href: string, rel: 'preload' | 'prefetch') => {
  const link = document.createElement('link');
  link.rel = rel;
  link.href = href;
  link.as = 'script';
  document.head.appendChild(link);
};
```

### 5. Bundle Optimization

#### **Tree Shaking Configuration**
```javascript
// webpack.optimization.js
module.exports = {
  optimization: {
    usedExports: true,
    sideEffects: false, // Or specify in package.json
    
    splitChunks: {
      chunks: 'all',
      minSize: 20000,
      minRemainingSize: 0,
      minChunks: 1,
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      enforceSizeThreshold: 50000,
      
      cacheGroups: {
        defaultVendors: {
          test: /[\\/]node_modules[\\/]/,
          priority: -10,
          reuseExistingChunk: true
        },
        
        // React ecosystem
        react: {
          test: /[\\/]node_modules[\\/](react|react-dom|react-router|react-router-dom)[\\/]/,
          name: 'react-vendors',
          priority: 20
        },
        
        // UI libraries
        ui: {
          test: /[\\/]node_modules[\\/](@mui|@emotion|styled-components)[\\/]/,
          name: 'ui-vendors',
          priority: 15
        },
        
        // Utilities
        utils: {
          test: /[\\/]node_modules[\\/](lodash|moment|date-fns|axios)[\\/]/,
          name: 'utils-vendors',
          priority: 10
        },
        
        default: {
          minChunks: 2,
          priority: -20,
          reuseExistingChunk: true
        }
      }
    }
  }
};
```

#### **Bundle Analysis and Monitoring**
```typescript
// src/utils/bundleAnalysis.ts
interface BundleMetrics {
  totalSize: number;
  gzippedSize: number;
  chunkCount: number;
  duplicateModules: string[];
  unusedExports: string[];
}

export class BundleAnalyzer {
  private metrics: BundleMetrics = {
    totalSize: 0,
    gzippedSize: 0,
    chunkCount: 0,
    duplicateModules: [],
    unusedExports: []
  };

  async analyzeBundles(): Promise<BundleMetrics> {
    // Analyze webpack stats or vite bundle info
    const stats = await this.getWebpackStats();
    
    this.metrics.totalSize = this.calculateTotalSize(stats);
    this.metrics.chunkCount = stats.chunks.length;
    this.metrics.duplicateModules = this.findDuplicateModules(stats);
    
    return this.metrics;
  }

  private getWebpackStats(): Promise<any> {
    // Implementation depends on build tool
    return fetch('/__webpack_stats__').then(res => res.json());
  }

  private calculateTotalSize(stats: any): number {
    return stats.assets.reduce((total: number, asset: any) => {
      return total + asset.size;
    }, 0);
  }

  private findDuplicateModules(stats: any): string[] {
    const moduleMap = new Map<string, number>();
    const duplicates: string[] = [];

    stats.modules.forEach((module: any) => {
      const count = moduleMap.get(module.name) || 0;
      moduleMap.set(module.name, count + 1);
      
      if (count > 0) {
        duplicates.push(module.name);
      }
    });

    return duplicates;
  }

  generateReport(): string {
    return `
Bundle Analysis Report
=====================
Total Size: ${(this.metrics.totalSize / 1024).toFixed(2)} KB
Chunks: ${this.metrics.chunkCount}
Duplicate Modules: ${this.metrics.duplicateModules.length}

Recommendations:
${this.generateRecommendations()}
    `;
  }

  private generateRecommendations(): string {
    const recommendations: string[] = [];

    if (this.metrics.totalSize > 500 * 1024) {
      recommendations.push('- Consider code splitting for large bundles');
    }

    if (this.metrics.duplicateModules.length > 0) {
      recommendations.push('- Remove duplicate dependencies');
    }

    if (this.metrics.chunkCount > 10) {
      recommendations.push('- Optimize chunk splitting strategy');
    }

    return recommendations.join('\n');
  }
}
```

### 6. Module Federation

#### **Module Federation Setup**
```javascript
// webpack.config.js (Host Application)
const ModuleFederationPlugin = require('@module-federation/webpack');

module.exports = {
  mode: 'development',
  
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      
      remotes: {
        mfe1: 'mfe1@http://localhost:3001/remoteEntry.js',
        mfe2: 'mfe2@http://localhost:3002/remoteEntry.js',
        shared_components: 'shared@http://localhost:3003/remoteEntry.js'
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
          singleton: true
        }
      }
    })
  ]
};
```

```javascript
// webpack.config.js (Micro-frontend)
const ModuleFederationPlugin = require('@module-federation/webpack');

module.exports = {
  mode: 'development',
  
  plugins: [
    new ModuleFederationPlugin({
      name: 'mfe1',
      filename: 'remoteEntry.js',
      
      exposes: {
        './UserProfile': './src/components/UserProfile',
        './Dashboard': './src/pages/Dashboard',
        './hooks': './src/hooks/index'
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

#### **Dynamic Module Loading**
```typescript
// src/utils/moduleLoader.ts
interface RemoteModule {
  name: string;
  url: string;
  scope: string;
  module: string;
}

export class ModuleFederationLoader {
  private loadedModules = new Map<string, any>();
  
  async loadRemoteModule(config: RemoteModule): Promise<any> {
    const key = `${config.name}/${config.module}`;
    
    if (this.loadedModules.has(key)) {
      return this.loadedModules.get(key);
    }
    
    try {
      // Load the remote entry
      await this.loadScript(config.url);
      
      // Get the container
      const container = (window as any)[config.scope];
      
      if (!container) {
        throw new Error(`Container ${config.scope} not found`);
      }
      
      // Initialize the container
      await container.init(__webpack_share_scopes__.default);
      
      // Get the module factory
      const factory = await container.get(config.module);
      const module = factory();
      
      this.loadedModules.set(key, module);
      return module;
      
    } catch (error) {
      console.error(`Failed to load remote module ${key}:`, error);
      throw error;
    }
  }
  
  private loadScript(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.async = true;
      script.src = url;
      
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load script: ${url}`));
      
      document.head.appendChild(script);
    });
  }
}

// React component for remote module loading
interface RemoteComponentProps {
  config: RemoteModule;
  fallback?: React.ComponentType;
  onError?: (error: Error) => void;
}

export const RemoteComponent: React.FC<RemoteComponentProps> = ({
  config,
  fallback: Fallback = () => <div>Loading...</div>,
  onError,
  ...props
}) => {
  const [Component, setComponent] = useState<React.ComponentType | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const loader = useMemo(() => new ModuleFederationLoader(), []);
  
  useEffect(() => {
    loader.loadRemoteModule(config)
      .then(module => {
        setComponent(() => module.default || module);
      })
      .catch(err => {
        setError(err);
        onError?.(err);
      });
  }, [config, loader, onError]);
  
  if (error) {
    return <div>Error loading remote component: {error.message}</div>;
  }
  
  if (!Component) {
    return <Fallback />;
  }
  
  return <Component {...props} />;
};
```

### 7. Progressive Web App (PWA) Features

#### **Service Worker Implementation**
```javascript
// public/sw.js
const CACHE_NAME = 'react-app-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});

// Update event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

#### **PWA React Integration**
```typescript
// src/hooks/usePWA.ts
import { useState, useEffect } from 'react';

interface PWAInstallPrompt {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export const usePWA = () => {
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<PWAInstallPrompt | null>(null);

  useEffect(() => {
    // Check if already installed
    const isInStandaloneMode = window.matchMedia('(display-mode: standalone)').matches;
    setIsInstalled(isInStandaloneMode);

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as any);
      setIsInstallable(true);
    };

    // Listen for app installed
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setInstallPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const installApp = async () => {
    if (!installPrompt) return;

    try {
      await installPrompt.prompt();
      const choiceResult = await installPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        console.log('App installation accepted');
      } else {
        console.log('App installation dismissed');
      }
    } catch (error) {
      console.error('Installation failed:', error);
    }
    
    setInstallPrompt(null);
    setIsInstallable(false);
  };

  return {
    isInstallable,
    isInstalled,
    installApp
  };
};
```

### 8. Asset Optimization

#### **Image Optimization Pipeline**
```javascript
// webpack.config.js - Image optimization
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [
      new ImageMinimizerPlugin({
        minimizer: {
          implementation: ImageMinimizerPlugin.imageminMinify,
          options: {
            plugins: [
              ['imagemin-mozjpeg', { quality: 80 }],
              ['imagemin-pngquant', { quality: [0.6, 0.8] }],
              ['imagemin-svgo', {
                plugins: [
                  {
                    name: 'preset-default',
                    params: {
                      overrides: {
                        removeViewBox: false,
                      },
                    },
                  },
                ],
              }],
            ],
          },
        },
        generator: [
          {
            type: 'asset',
            preset: 'webp-custom-name',
            implementation: ImageMinimizerPlugin.imageminGenerate,
            options: {
              plugins: ['imagemin-webp'],
            },
          },
        ],
      }),
    ],
  },
};
```

#### **Smart Image Component**
```typescript
// src/components/OptimizedImage.tsx
import React, { useState, useRef, useEffect } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  lazy?: boolean;
  placeholder?: string;
  sizes?: string;
  className?: string;
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  lazy = true,
  placeholder,
  sizes,
  className
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(!lazy);
  const imgRef = useRef<HTMLImageElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!lazy || isInView) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [lazy, isInView]);

  // Generate srcSet for responsive images
  const generateSrcSet = (baseSrc: string) => {
    const sizes = [320, 640, 960, 1280, 1920];
    return sizes
      .map(size => {
        const webpSrc = baseSrc.replace(/\.(jpg|jpeg|png)$/, `.${size}w.webp`);
        const fallbackSrc = baseSrc.replace(/\.(jpg|jpeg|png)$/, `.${size}w.$1`);
        return `${webpSrc} ${size}w, ${fallbackSrc} ${size}w`;
      })
      .join(', ');
  };

  const handleLoad = () => {
    setIsLoaded(true);
  };

  return (
    <div className={`optimized-image ${className || ''}`}>
      {!isLoaded && placeholder && (
        <img
          src={placeholder}
          alt=""
          className="placeholder"
          style={{ filter: 'blur(5px)' }}
        />
      )}
      
      {isInView && (
        <picture>
          <source
            srcSet={generateSrcSet(src)}
            sizes={sizes || '(max-width: 768px) 100vw, 50vw'}
            type="image/webp"
          />
          <img
            ref={imgRef}
            src={src}
            alt={alt}
            width={width}
            height={height}
            onLoad={handleLoad}
            loading={lazy ? 'lazy' : 'eager'}
            style={{
              opacity: isLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease'
            }}
          />
        </picture>
      )}
    </div>
  );
};

export default OptimizedImage;
```

## 🎯 Practical Exercises

### Exercise 1: Webpack Optimization
Configure a production-ready Webpack setup with advanced optimizations.

### Exercise 2: Vite Plugin Development
Create a custom Vite plugin for your specific development needs.

### Exercise 3: Module Federation Implementation
Set up a micro-frontend architecture using Module Federation.

### Exercise 4: PWA Implementation
Convert a React app into a full-featured Progressive Web App.

## 📊 Assessment Criteria

### Build Tool Mastery
- [ ] Configure advanced build tools (Webpack, Vite)
- [ ] Implement code splitting strategies
- [ ] Optimize bundle size and performance
- [ ] Set up development and production environments

### Performance Optimization
- [ ] Achieve optimal loading times
- [ ] Implement efficient caching strategies
- [ ] Optimize asset delivery
- [ ] Monitor and analyze bundle metrics

### Advanced Features
- [ ] Configure Module Federation
- [ ] Implement PWA features
- [ ] Set up automated optimization pipelines
- [ ] Create custom build tools and plugins

## 🚀 Project: Advanced Build System

Create a comprehensive build system for a large-scale React application:

**Requirements:**
- Multi-environment configuration
- Advanced code splitting
- Module Federation setup
- PWA implementation
- Comprehensive optimization pipeline
- Performance monitoring
- Automated deployment

**Performance Targets:**
- First Contentful Paint < 1.5s
- Largest Contentful Paint < 2.5s
- Cumulative Layout Shift < 0.1
- Bundle size < 250KB (gzipped)

## 📚 Additional Resources

### Tools
- Webpack
- Vite
- Parcel
- esbuild
- Rollup
- SWC

### Documentation
- [Webpack Documentation](https://webpack.js.org/concepts/)
- [Vite Documentation](https://vitejs.dev/guide/)
- [Module Federation](https://webpack.js.org/concepts/module-federation/)
- [PWA Documentation](https://web.dev/progressive-web-apps/)

## ⏭️ Next Steps

After mastering this module, you'll be ready for:
- **Module 16**: Deployment & DevOps
- Production deployment strategies
- CI/CD pipeline implementation
- Monitoring and analytics

---

**Estimated Time:** 2-3 weeks  
**Difficulty:** Advanced  
**Prerequisites:** Modules 1-14 completed
