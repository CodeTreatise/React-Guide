# Vite & Modern Build Tools

## Table of Contents
1. [Vite Fundamentals](#vite-fundamentals)
2. [Advanced Vite Configuration](#advanced-vite-configuration)
3. [Modern Build Tools Comparison](#modern-build-tools-comparison)
4. [ESBuild Integration](#esbuild-integration)
5. [Parcel Configuration](#parcel-configuration)
6. [Rollup for Libraries](#rollup-for-libraries)
7. [Performance Optimization](#performance-optimization)
8. [Migration Strategies](#migration-strategies)

## Vite Fundamentals

### Basic Vite Setup for React
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh
      fastRefresh: true,
      
      // JSX runtime
      jsxRuntime: 'automatic',
      
      // Babel configuration
      babel: {
        plugins: [
          ['@babel/plugin-proposal-decorators', { legacy: true }]
        ]
      }
    })
  ],
  
  // Development server
  server: {
    port: 3000,
    open: true,
    host: true, // Allow external access
    
    // Proxy configuration
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    
    // HTTPS configuration
    https: false,
    
    // Headers
    headers: {
      'Cross-Origin-Embedder-Policy': 'require-corp',
      'Cross-Origin-Opener-Policy': 'same-origin'
    }
  },
  
  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    
    // Source maps
    sourcemap: true,
    
    // Minification
    minify: 'esbuild', // or 'terser'
    
    // Target browsers
    target: 'esnext',
    
    // Rollup options
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      },
      
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    
    // Chunk size warnings
    chunkSizeWarningLimit: 500,
    
    // CSS code splitting
    cssCodeSplit: true
  },
  
  // Module resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@styles': resolve(__dirname, 'src/styles')
    },
    
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json']
  },
  
  // CSS configuration
  css: {
    modules: {
      localsConvention: 'camelCase',
      generateScopedName: '[name]__[local]___[hash:base64:5]'
    },
    
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@styles/variables.scss";`
      }
    },
    
    postcss: {
      plugins: [
        require('autoprefixer'),
        require('cssnano')({
          preset: 'default'
        })
      ]
    }
  },
  
  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  },
  
  // Optimization
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
    exclude: ['@vite/client', '@vite/env']
  }
});
```

### Advanced Vite Configuration
```javascript
{% raw %}
// vite.config.advanced.js
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { createHtmlPlugin } from 'vite-plugin-html';
import legacy from '@vitejs/plugin-legacy';
import { VitePWA } from 'vite-plugin-pwa';
import eslint from 'vite-plugin-eslint';

export default defineConfig(({ command, mode }) => {
  // Load environment variables
  const env = loadEnv(mode, process.cwd(), '');
  
  const isProduction = mode === 'production';
  const isDevelopment = mode === 'development';
  
  return {
    plugins: [
      // React plugin with SWC
      react({
        jsxRuntime: 'automatic',
        
        // Use SWC instead of Babel for better performance
        ...(isProduction && {
          jsxImportSource: '@emotion/react',
          plugins: [
            ['@swc/plugin-emotion', {}]
          ]
        })
      }),
      
      // ESLint integration
      eslint({
        cache: false,
        include: ['src/**/*.{js,jsx,ts,tsx}'],
        exclude: ['node_modules', 'dist']
      }),
      
      // HTML template processing
      createHtmlPlugin({
        minify: isProduction,
        inject: {
          data: {
            title: env.VITE_APP_TITLE || 'React App',
            description: env.VITE_APP_DESCRIPTION || 'Modern React Application',
            keywords: env.VITE_APP_KEYWORDS || 'react,vite,typescript'
          }
        }
      }),
      
      // Legacy browser support
      ...(isProduction ? [
        legacy({
          targets: ['defaults', 'not IE 11']
        })
      ] : []),
      
      // PWA configuration
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,webp}'],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: 'CacheFirst',
              options: {
                cacheName: 'google-fonts-cache',
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
                },
                cacheableResponse: {
                  statuses: [0, 200]
                }
              }
            },
            {
              urlPattern: /^https:\/\/api\.example\.com\/.*/i,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                networkTimeoutSeconds: 10,
                expiration: {
                  maxEntries: 50,
                  maxAgeSeconds: 60 * 60 * 24 // 1 day
                }
              }
            }
          ]
        },
        manifest: {
          name: env.VITE_APP_TITLE || 'React App',
          short_name: env.VITE_APP_SHORT_NAME || 'App',
          description: env.VITE_APP_DESCRIPTION || 'Modern React Application',
          theme_color: '#000000',
          background_color: '#ffffff',
          display: 'standalone',
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
      ...(process.env.ANALYZE === 'true' ? [
        visualizer({
          filename: 'dist/stats.html',
          open: true,
          gzipSize: true,
          brotliSize: true
        })
      ] : [])
    ],
    
    server: {
      port: parseInt(env.VITE_PORT) || 3000,
      host: env.VITE_HOST || 'localhost',
      open: env.VITE_OPEN === 'true',
      
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8080',
          changeOrigin: true,
          secure: env.VITE_API_SECURE === 'true',
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },
    
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: isDevelopment || env.VITE_BUILD_SOURCEMAP === 'true',
      minify: isProduction ? 'esbuild' : false,
      target: 'esnext',
      
      rollupOptions: {
        output: {
          manualChunks: {
            // Separate vendor chunks
            react: ['react', 'react-dom'],
            router: ['react-router-dom'],
            ui: ['@mui/material', '@emotion/react', '@emotion/styled'],
            utils: ['lodash-es', 'date-fns', 'uuid']
          },
          
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId 
              ? chunkInfo.facadeModuleId.split('/').pop() 
              : 'chunk';
            return `js/${facadeModuleId}-[hash].js`;
          },
          
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].[ext]'
        }
      },
      
      // Increase chunk size warning limit
      chunkSizeWarningLimit: 600,
      
      // CSS code splitting
      cssCodeSplit: true,
      
      // Polyfill for dynamic imports
      dynamicImportVarsOptions: {
        warnOnError: true,
        exclude: ['node_modules']
      }
    },
    
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@pages': resolve(__dirname, 'src/pages'),
        '@hooks': resolve(__dirname, 'src/hooks'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@types': resolve(__dirname, 'src/types'),
        '@assets': resolve(__dirname, 'src/assets'),
        '@styles': resolve(__dirname, 'src/styles'),
        '@services': resolve(__dirname, 'src/services'),
        '@store': resolve(__dirname, 'src/store')
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
          additionalData: `
            @import "@styles/variables.scss";
            @import "@styles/mixins.scss";
          `
        }
      },
      
      postcss: {
        plugins: [
          require('autoprefixer'),
          ...(isProduction ? [
            require('cssnano')({
              preset: ['default', {
                discardComments: { removeAll: true }
              }]
            })
          ] : [])
        ]
      }
    },
    
    define: {
      __APP_VERSION__: JSON.stringify(env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      __COMMIT_HASH__: JSON.stringify(env.VITE_COMMIT_HASH || 'dev')
    },
    
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@emotion/react',
        '@emotion/styled',
        'lodash-es'
      ],
      exclude: ['@vite/client', '@vite/env']
    },
    
    // Worker configuration
    worker: {
      format: 'es'
    },
    
    // Experimental features
    experimental: {
      renderBuiltUrl(filename, { hostType }) {
        if (hostType === 'js') {
          return { js: `/${filename}` };
        } else {
          return { relative: true };
        }
      }
    }
  };
});
{% endraw %}
```

## Modern Build Tools Comparison

### Build Tool Feature Matrix
```typescript
interface BuildToolFeatures {
  name: string;
  bundling: 'webpack' | 'rollup' | 'esbuild' | 'parcel' | 'custom';
  devServer: boolean;
  hmr: boolean;
  codesplitting: boolean;
  treeshaking: boolean;
  typescript: boolean;
  configComplexity: 'none' | 'minimal' | 'moderate' | 'complex';
  buildSpeed: 'slow' | 'medium' | 'fast' | 'very-fast';
  ecosystem: 'small' | 'medium' | 'large' | 'huge';
  production: 'good' | 'excellent';
}

const buildTools: BuildToolFeatures[] = [
  {
    name: 'Webpack',
    bundling: 'webpack',
    devServer: true,
    hmr: true,
    codesplitting: true,
    treeshaking: true,
    typescript: true,
    configComplexity: 'complex',
    buildSpeed: 'slow',
    ecosystem: 'huge',
    production: 'excellent'
  },
  {
    name: 'Vite',
    bundling: 'rollup',
    devServer: true,
    hmr: true,
    codesplitting: true,
    treeshaking: true,
    typescript: true,
    configComplexity: 'minimal',
    buildSpeed: 'fast',
    ecosystem: 'large',
    production: 'excellent'
  },
  {
    name: 'Parcel',
    bundling: 'parcel',
    devServer: true,
    hmr: true,
    codesplitting: true,
    treeshaking: true,
    typescript: true,
    configComplexity: 'none',
    buildSpeed: 'fast',
    ecosystem: 'medium',
    production: 'good'
  },
  {
    name: 'esbuild',
    bundling: 'esbuild',
    devServer: false,
    hmr: false,
    codesSplitting: true,
    treeshaking: true,
    typescript: true,
    configComplexity: 'minimal',
    buildSpeed: 'very-fast',
    ecosystem: 'small',
    production: 'good'
  }
];
```

### Performance Benchmarks
```javascript
// Performance comparison script
const { performance } = require('perf_hooks');
const fs = require('fs');

class BuildBenchmark {
  constructor(tool, projectSize) {
    this.tool = tool;
    this.projectSize = projectSize;
    this.results = {};
  }
  
  async measureColdBuild() {
    const start = performance.now();
    await this.runBuild({ clean: true });
    const end = performance.now();
    
    this.results.coldBuild = end - start;
    return this.results.coldBuild;
  }
  
  async measureIncrementalBuild() {
    // Make a small change
    await this.makeChange();
    
    const start = performance.now();
    await this.runBuild({ incremental: true });
    const end = performance.now();
    
    this.results.incrementalBuild = end - start;
    return this.results.incrementalBuild;
  }
  
  async measureDevServerStart() {
    const start = performance.now();
    await this.startDevServer();
    const end = performance.now();
    
    this.results.devServerStart = end - start;
    return this.results.devServerStart;
  }
  
  async measureHMRUpdate() {
    await this.makeChange();
    
    const start = performance.now();
    await this.waitForHMRUpdate();
    const end = performance.now();
    
    this.results.hmrUpdate = end - start;
    return this.results.hmrUpdate;
  }
  
  generateReport() {
    return {
      tool: this.tool,
      projectSize: this.projectSize,
      metrics: this.results,
      score: this.calculateScore()
    };
  }
  
  calculateScore() {
    const weights = {
      coldBuild: 0.3,
      incrementalBuild: 0.3,
      devServerStart: 0.2,
      hmrUpdate: 0.2
    };
    
    // Lower times = higher score
    const normalizedScores = Object.entries(this.results).map(([key, time]) => {
      const baseTime = this.getBaselineTime(key);
      const score = Math.max(0, 100 - (time / baseTime) * 100);
      return score * weights[key];
    });
    
    return normalizedScores.reduce((sum, score) => sum + score, 0);
  }
}

// Usage example
const runBenchmarks = async () => {
  const tools = ['webpack', 'vite', 'parcel', 'esbuild'];
  const results = [];
  
  for (const tool of tools) {
    const benchmark = new BuildBenchmark(tool, 'medium');
    
    await benchmark.measureColdBuild();
    await benchmark.measureIncrementalBuild();
    await benchmark.measureDevServerStart();
    await benchmark.measureHMRUpdate();
    
    results.push(benchmark.generateReport());
  }
  
  console.table(results);
};
```

## ESBuild Integration

### Standalone ESBuild Configuration
```javascript
{% raw %}
// esbuild.config.js
const esbuild = require('esbuild');
const { sassPlugin } = require('esbuild-sass-plugin');
const { htmlPlugin } = require('@chialab/esbuild-plugin-html');
const { clean } = require('esbuild-plugin-clean');

const isProduction = process.env.NODE_ENV === 'production';

const buildOptions = {
  entryPoints: ['src/index.tsx'],
  bundle: true,
  outdir: 'dist',
  format: 'esm',
  target: 'esnext',
  platform: 'browser',
  
  // Source maps
  sourcemap: !isProduction,
  
  // Minification
  minify: isProduction,
  
  // Tree shaking
  treeShaking: true,
  
  // Code splitting
  splitting: true,
  
  // Asset handling
  loader: {
    '.png': 'file',
    '.jpg': 'file',
    '.jpeg': 'file',
    '.gif': 'file',
    '.svg': 'file',
    '.woff': 'file',
    '.woff2': 'file',
    '.eot': 'file',
    '.ttf': 'file'
  },
  
  // External dependencies
  external: isProduction ? [] : ['react', 'react-dom'],
  
  // Define environment variables
  define: {
    'process.env.NODE_ENV': `"${process.env.NODE_ENV}"`,
    __DEV__: !isProduction
  },
  
  plugins: [
    // Clean dist folder
    clean({
      patterns: ['./dist/*']
    }),
    
    // SASS support
    sassPlugin({
      type: 'style'
    }),
    
    // HTML processing
    htmlPlugin({
      files: [
        {
          entryPoints: ['src/index.tsx'],
          filename: 'index.html',
          htmlTemplate: 'public/index.html'
        }
      ]
    }),
    
    // Custom plugin for environment handling
    {
      name: 'env',
      setup(build) {
        build.onResolve({ filter: /^env$/ }, args => ({
          path: args.path,
          namespace: 'env-ns'
        }));
        
        build.onLoad({ filter: /.*/, namespace: 'env-ns' }, () => ({
          contents: JSON.stringify(process.env),
          loader: 'json'
        }));
      }
    }
  ],
  
  // Watch mode for development
  ...(process.env.WATCH === 'true' && {
    watch: {
      onRebuild(error, result) {
        if (error) console.error('Watch build failed:', error);
        else console.log('Watch build succeeded:', result);
      }
    }
  })
};

const build = async () => {
  try {
    const result = await esbuild.build(buildOptions);
    
    if (result.warnings.length > 0) {
      console.warn('Build warnings:', result.warnings);
    }
    
    console.log('Build completed successfully');
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
};

if (require.main === module) {
  build();
}

module.exports = { buildOptions, build };
{% endraw %}
```

### ESBuild with React Fast Refresh
```javascript
{% raw %}
// esbuild-dev-server.js
const esbuild = require('esbuild');
const { createServer } = require('http');
const { WebSocketServer } = require('ws');
const chokidar = require('chokidar');

class ESBuildDevServer {
  constructor(options = {}) {
    this.options = {
      port: 3000,
      host: 'localhost',
      ...options
    };
    
    this.clients = new Set();
    this.buildContext = null;
  }
  
  async start() {
    // Create build context
    this.buildContext = await esbuild.context({
      entryPoints: ['src/index.tsx'],
      bundle: true,
      outdir: 'dist',
      format: 'esm',
      platform: 'browser',
      target: 'esnext',
      sourcemap: true,
      
      plugins: [
        {
          name: 'rebuild-notify',
          setup(build) {
            build.onEnd(() => {
              this.broadcast({ type: 'reload' });
            });
          }
        }
      ]
    });
    
    // Initial build
    await this.buildContext.rebuild();
    
    // Start file watcher
    this.startWatcher();
    
    // Start HTTP server
    this.startHttpServer();
    
    // Start WebSocket server
    this.startWebSocketServer();
    
    console.log(`Dev server running on http://${this.options.host}:${this.options.port}`);
  }
  
  startWatcher() {
    const watcher = chokidar.watch('src/**/*', {
      ignored: /node_modules/,
      persistent: true
    });
    
    watcher.on('change', async (path) => {
      console.log(`File changed: ${path}`);
      try {
        await this.buildContext.rebuild();
      } catch (error) {
        console.error('Build error:', error);
        this.broadcast({ 
          type: 'error', 
          error: error.message 
        });
      }
    });
  }
  
  startHttpServer() {
    const server = createServer((req, res) => {
      // Serve static files
      this.serveStatic(req, res);
    });
    
    server.listen(this.options.port, this.options.host);
  }
  
  startWebSocketServer() {
    const wss = new WebSocketServer({ port: this.options.port + 1 });
    
    wss.on('connection', (ws) => {
      this.clients.add(ws);
      
      ws.on('close', () => {
        this.clients.delete(ws);
      });
    });
  }
  
  broadcast(message) {
    const data = JSON.stringify(message);
    this.clients.forEach(client => {
      if (client.readyState === 1) { // OPEN
        client.send(data);
      }
    });
  }
  
  async stop() {
    if (this.buildContext) {
      await this.buildContext.dispose();
    }
  }
}

// Usage
const devServer = new ESBuildDevServer({
  port: 3000,
  host: 'localhost'
});

devServer.start().catch(console.error);

// Graceful shutdown
process.on('SIGINT', async () => {
  await devServer.stop();
  process.exit(0);
});
{% endraw %}
```

## Parcel Configuration

### Parcel 2 Configuration
```json
// .parcelrc
{
  "extends": "@parcel/config-default",
  "transformers": {
    "*.{ts,tsx}": ["@parcel/transformer-typescript-tsc"],
    "*.{js,jsx}": ["@parcel/transformer-babel"],
    "*.{css,scss,sass}": ["@parcel/transformer-sass", "@parcel/transformer-css"],
    "*.svg": ["@parcel/transformer-svg-react"]
  },
  "resolvers": ["@parcel/resolver-default"],
  "bundler": "@parcel/bundler-default",
  "namers": ["@parcel/namer-default"],
  "runtimes": ["@parcel/runtime-js", "@parcel/runtime-browser-hmr"],
  "optimizers": {
    "*.{js,mjs,jsm,jsx,ts,tsx}": ["@parcel/optimizer-terser"],
    "*.{css,scss,sass}": ["@parcel/optimizer-css"],
    "*.{png,jpg,jpeg,webp}": ["@parcel/optimizer-imagemin"]
  },
  "packagers": {
    "*.html": "@parcel/packager-html",
    "*.{js,mjs,jsm,jsx,ts,tsx}": "@parcel/packager-js",
    "*.{css,scss,sass}": "@parcel/packager-css",
    "*.{png,jpg,jpeg,gif,svg,webp}": "@parcel/packager-raw-url"
  },
  "compressors": {
    "*.{html,css,js,svg,map}": ["@parcel/compressor-gzip"]
  }
}
```

```javascript
// package.json scripts for Parcel
{
  "scripts": {
    "dev": "parcel src/index.html --port 3000",
    "build": "parcel build src/index.html --dist-dir dist --public-url ./",
    "preview": "parcel serve dist --port 4000"
  }
}
```

### Advanced Parcel Setup
```javascript
{% raw %}
// parcel.config.js (if using programmatic API)
const { Parcel } = require('@parcel/core');
const path = require('path');

const bundler = new Parcel({
  entries: 'src/index.html',
  defaultConfig: '@parcel/config-default',
  
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  
  targets: {
    main: {
      distDir: 'dist',
      publicUrl: './',
      engines: {
        browsers: ['last 2 versions']
      }
    }
  },
  
  env: {
    NODE_ENV: process.env.NODE_ENV || 'development'
  },
  
  serveOptions: {
    port: 3000,
    host: 'localhost'
  },
  
  hmrOptions: {
    port: 3001
  }
});

// Development server
const runDev = async () => {
  try {
    await bundler.watch((err, event) => {
      if (err) {
        console.error('Build error:', err);
        return;
      }
      
      if (event.type === 'buildSuccess') {
        console.log('Build succeeded');
      }
    });
  } catch (error) {
    console.error('Failed to start dev server:', error);
  }
};

// Production build
const runBuild = async () => {
  try {
    const { bundleGraph, buildTime } = await bundler.run();
    console.log(`Build completed in ${buildTime}ms`);
    
    // Bundle information
    bundleGraph.getBundles().forEach(bundle => {
      console.log(`Bundle: ${bundle.filePath} (${bundle.stats.size} bytes)`);
    });
  } catch (error) {
    console.error('Build failed:', error);
  }
};

module.exports = { runDev, runBuild };
{% endraw %}
```

## Rollup for Libraries

### Library Build Configuration
```javascript
// rollup.config.js
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import typescript from '@rollup/plugin-typescript';
import { terser } from 'rollup-plugin-terser';
import babel from '@rollup/plugin-babel';
import postcss from 'rollup-plugin-postcss';
import { visualizer } from 'rollup-plugin-visualizer';
import dts from 'rollup-plugin-dts';

const isProduction = process.env.NODE_ENV === 'production';

// Common external dependencies
const external = [
  'react',
  'react-dom',
  'react/jsx-runtime',
  'styled-components',
  '@emotion/react',
  '@emotion/styled'
];

const commonPlugins = [
  resolve({
    browser: true,
    preferBuiltins: false
  }),
  commonjs(),
  postcss({
    extract: true,
    minimize: isProduction,
    sourceMap: !isProduction
  })
];

export default [
  // ES Modules build
  {
    input: 'src/index.ts',
    external,
    output: {
      file: 'dist/index.esm.js',
      format: 'esm',
      sourcemap: !isProduction
    },
    plugins: [
      ...commonPlugins,
      typescript({
        tsconfig: './tsconfig.json',
        declaration: false,
        declarationMap: false
      }),
      babel({
        babelHelpers: 'bundled',
        exclude: 'node_modules/**',
        presets: [
          ['@babel/preset-env', { modules: false }],
          ['@babel/preset-react', { runtime: 'automatic' }],
          '@babel/preset-typescript'
        ]
      }),
      isProduction && terser({
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      }),
      isProduction && visualizer({
        filename: 'dist/bundle-analysis.html',
        open: false
      })
    ].filter(Boolean)
  },
  
  // CommonJS build
  {
    input: 'src/index.ts',
    external,
    output: {
      file: 'dist/index.cjs.js',
      format: 'cjs',
      sourcemap: !isProduction,
      exports: 'named'
    },
    plugins: [
      ...commonPlugins,
      typescript({
        tsconfig: './tsconfig.json',
        declaration: false,
        declarationMap: false
      }),
      babel({
        babelHelpers: 'bundled',
        exclude: 'node_modules/**',
        presets: [
          ['@babel/preset-env', { modules: 'cjs' }],
          ['@babel/preset-react', { runtime: 'automatic' }],
          '@babel/preset-typescript'
        ]
      }),
      isProduction && terser()
    ].filter(Boolean)
  },
  
  // UMD build for browsers
  {
    input: 'src/index.ts',
    external: ['react', 'react-dom'],
    output: {
      file: 'dist/index.umd.js',
      format: 'umd',
      name: 'MyLibrary',
      globals: {
        react: 'React',
        'react-dom': 'ReactDOM'
      },
      sourcemap: !isProduction
    },
    plugins: [
      ...commonPlugins,
      typescript({
        tsconfig: './tsconfig.json',
        declaration: false,
        declarationMap: false
      }),
      babel({
        babelHelpers: 'bundled',
        exclude: 'node_modules/**',
        presets: [
          ['@babel/preset-env', { modules: false }],
          ['@babel/preset-react', { runtime: 'automatic' }],
          '@babel/preset-typescript'
        ]
      }),
      isProduction && terser()
    ].filter(Boolean)
  },
  
  // Type definitions
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/index.d.ts',
      format: 'esm'
    },
    plugins: [dts()],
    external: /\.css$/
  }
];
```

### Package.json for Library
```json
{
  "name": "my-react-library",
  "version": "1.0.0",
  "description": "A React component library",
  "main": "dist/index.cjs.js",
  "module": "dist/index.esm.js",
  "browser": "dist/index.umd.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist"
  ],
  "exports": {
    ".": {
      "import": "./dist/index.esm.js",
      "require": "./dist/index.cjs.js",
      "types": "./dist/index.d.ts"
    },
    "./package.json": "./package.json"
  },
  "sideEffects": [
    "*.css"
  ],
  "scripts": {
    "build": "rollup -c",
    "build:watch": "rollup -c --watch",
    "build:analyze": "ANALYZE=true rollup -c"
  },
  "peerDependencies": {
    "react": ">=16.8.0",
    "react-dom": ">=16.8.0"
  },
  "devDependencies": {
    "@rollup/plugin-babel": "^6.0.0",
    "@rollup/plugin-commonjs": "^22.0.0",
    "@rollup/plugin-node-resolve": "^13.0.0",
    "@rollup/plugin-typescript": "^8.0.0",
    "rollup": "^2.75.0",
    "rollup-plugin-dts": "^4.2.0",
    "rollup-plugin-postcss": "^4.0.0",
    "rollup-plugin-terser": "^7.0.0",
    "rollup-plugin-visualizer": "^5.6.0"
  }
}
```

## Performance Optimization

### Build Performance Analysis
```javascript
// performance-analyzer.js
const webpack = require('webpack');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const SpeedMeasurePlugin = require('speed-measure-webpack-plugin');

class BuildPerformanceAnalyzer {
  constructor(config) {
    this.config = config;
    this.metrics = {};
  }
  
  async analyzeBuildSpeed() {
    const smp = new SpeedMeasurePlugin();
    const config = smp.wrap(this.config);
    
    return new Promise((resolve, reject) => {
      const start = Date.now();
      
      webpack(config, (err, stats) => {
        if (err) {
          reject(err);
          return;
        }
        
        const buildTime = Date.now() - start;
        const info = stats.toJson();
        
        this.metrics.buildSpeed = {
          totalTime: buildTime,
          warnings: info.warnings?.length || 0,
          errors: info.errors?.length || 0,
          chunks: info.chunks?.length || 0,
          modules: info.modules?.length || 0
        };
        
        resolve(this.metrics.buildSpeed);
      });
    });
  }
  
  async analyzeBundleSize() {
    const config = {
      ...this.config,
      plugins: [
        ...this.config.plugins,
        new BundleAnalyzerPlugin({
          analyzerMode: 'json',
          reportFilename: 'bundle-report.json',
          openAnalyzer: false
        })
      ]
    };
    
    return new Promise((resolve, reject) => {
      webpack(config, (err, stats) => {
        if (err) {
          reject(err);
          return;
        }
        
        const info = stats.toJson({
          assets: true,
          chunks: true,
          modules: true
        });
        
        this.metrics.bundleSize = {
          totalSize: info.assets.reduce((sum, asset) => sum + asset.size, 0),
          gzipEstimate: info.assets.reduce((sum, asset) => sum + (asset.size * 0.3), 0),
          largestAssets: info.assets
            .sort((a, b) => b.size - a.size)
            .slice(0, 10)
            .map(asset => ({
              name: asset.name,
              size: asset.size,
              sizeFormatted: this.formatBytes(asset.size)
            }))
        };
        
        resolve(this.metrics.bundleSize);
      });
    });
  }
  
  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  generateReport() {
    return {
      timestamp: new Date().toISOString(),
      metrics: this.metrics,
      recommendations: this.generateRecommendations()
    };
  }
  
  generateRecommendations() {
    const recommendations = [];
    
    if (this.metrics.buildSpeed?.totalTime > 30000) {
      recommendations.push({
        type: 'performance',
        severity: 'warning',
        message: 'Build time exceeds 30 seconds. Consider using thread-loader or caching.'
      });
    }
    
    if (this.metrics.bundleSize?.totalSize > 500000) {
      recommendations.push({
        type: 'size',
        severity: 'warning',
        message: 'Bundle size exceeds 500KB. Consider code splitting and tree shaking.'
      });
    }
    
    return recommendations;
  }
}

// Usage
const analyzer = new BuildPerformanceAnalyzer(webpackConfig);

const runAnalysis = async () => {
  try {
    await analyzer.analyzeBuildSpeed();
    await analyzer.analyzeBundleSize();
    
    const report = analyzer.generateReport();
    console.log(JSON.stringify(report, null, 2));
  } catch (error) {
    console.error('Analysis failed:', error);
  }
};
```

### Cache Optimization Strategies
```javascript
{% raw %}
// cache-optimization.js
const path = require('path');

// Webpack persistent caching
const webpackCacheConfig = {
  cache: {
    type: 'filesystem',
    version: '1.0',
    cacheDirectory: path.resolve(__dirname, 'node_modules/.cache/webpack'),
    
    buildDependencies: {
      config: [__filename],
      tsconfig: [path.resolve(__dirname, 'tsconfig.json')],
      package: [path.resolve(__dirname, 'package.json')]
    },
    
    managedPaths: [
      path.resolve(__dirname, 'node_modules')
    ],
    
    profile: false,
    maxAge: 5184000000, // 60 days
    
    name: `${process.env.NODE_ENV}-${process.env.BROWSERSLIST_ENV || 'development'}`
  }
};

// Vite cache configuration
const viteCacheConfig = {
  cacheDir: 'node_modules/.vite',
  
  optimizeDeps: {
    force: false, // Don't force re-optimization
    
    include: [
      'react',
      'react-dom',
      'react-router-dom'
    ],
    
    exclude: [
      '@vite/client',
      '@vite/env'
    ]
  }
};

// ESLint caching
const eslintCacheConfig = {
  cache: true,
  cacheLocation: path.resolve(__dirname, 'node_modules/.cache/.eslintcache'),
  cacheStrategy: 'content' // or 'metadata'
};

// TypeScript incremental compilation
const typescriptCacheConfig = {
  compilerOptions: {
    incremental: true,
    tsBuildInfoFile: path.resolve(__dirname, 'node_modules/.cache/typescript/tsbuildinfo')
  }
};
{% endraw %}
```

## Migration Strategies

### Webpack to Vite Migration
```javascript
{% raw %}
// migration-webpack-to-vite.js
const fs = require('fs');
const path = require('path');

class WebpackToViteMigrator {
  constructor(webpackConfigPath) {
    this.webpackConfig = require(webpackConfigPath);
    this.viteConfig = {
      plugins: [],
      resolve: { alias: {} },
      define: {},
      server: {},
      build: {}
    };
  }
  
  migrate() {
    this.migrateEntry();
    this.migrateResolve();
    this.migratePlugins();
    this.migrateDevServer();
    this.migrateBuild();
    this.migrateEnvironment();
    
    return this.generateViteConfig();
  }
  
  migrateEntry() {
    // Vite uses index.html as entry point instead of JS entry
    if (this.webpackConfig.entry) {
      console.warn('Vite uses index.html as entry point. Update your HTML file to include the script tag.');
    }
  }
  
  migrateResolve() {
    if (this.webpackConfig.resolve?.alias) {
      this.viteConfig.resolve.alias = this.webpackConfig.resolve.alias;
    }
    
    if (this.webpackConfig.resolve?.extensions) {
      // Vite has default extensions, only add if custom
      const customExtensions = this.webpackConfig.resolve.extensions
        .filter(ext => !['.js', '.jsx', '.ts', '.tsx', '.json'].includes(ext));
      
      if (customExtensions.length > 0) {
        this.viteConfig.resolve.extensions = this.webpackConfig.resolve.extensions;
      }
    }
  }
  
  migratePlugins() {
    const plugins = this.webpackConfig.plugins || [];
    
    plugins.forEach(plugin => {
      const pluginName = plugin.constructor.name;
      
      switch (pluginName) {
        case 'HtmlWebpackPlugin':
          // Vite handles HTML automatically
          console.info('HtmlWebpackPlugin: Handled automatically by Vite');
          break;
          
        case 'DefinePlugin':
          this.viteConfig.define = {
            ...this.viteConfig.define,
            ...plugin.definitions
          };
          break;
          
        case 'MiniCssExtractPlugin':
          // Vite handles CSS extraction automatically
          console.info('MiniCssExtractPlugin: Handled automatically by Vite');
          break;
          
        case 'ESLintPlugin':
          this.viteConfig.plugins.push("import eslint from 'vite-plugin-eslint';");
          break;
          
        default:
          console.warn(`Plugin ${pluginName} needs manual migration`);
      }
    });
  }
  
  migrateDevServer() {
    if (this.webpackConfig.devServer) {
      const devServer = this.webpackConfig.devServer;
      
      this.viteConfig.server = {
        port: devServer.port || 3000,
        host: devServer.host || 'localhost',
        open: devServer.open || false,
        https: devServer.https || false
      };
      
      if (devServer.proxy) {
        this.viteConfig.server.proxy = devServer.proxy;
      }
    }
  }
  
  migrateBuild() {
    if (this.webpackConfig.output) {
      const output = this.webpackConfig.output;
      
      this.viteConfig.build = {
        outDir: output.path ? path.basename(output.path) : 'dist',
        assetsDir: 'assets',
        sourcemap: this.webpackConfig.devtool !== false
      };
    }
    
    if (this.webpackConfig.optimization?.splitChunks) {
      this.viteConfig.build.rollupOptions = {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            // Add other chunks based on splitChunks config
          }
        }
      };
    }
  }
  
  migrateEnvironment() {
    // Convert webpack DefinePlugin to Vite define
    const definePlugin = this.webpackConfig.plugins?.find(
      plugin => plugin.constructor.name === 'DefinePlugin'
    );
    
    if (definePlugin) {
      Object.entries(definePlugin.definitions).forEach(([key, value]) => {
        if (key.startsWith('process.env.')) {
          // Convert to Vite env variable format
          const envKey = key.replace('process.env.', 'VITE_');
          console.info(`Convert ${key} to ${envKey} in your .env file`);
        }
      });
    }
  }
  
  generateViteConfig() {
    const configString = `
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
${this.viteConfig.plugins.join('\n')}

export default defineConfig({
  plugins: [
    react(),
    ${this.viteConfig.plugins.filter(p => p.includes('(')).join(',\n    ')}
  ],
  
  resolve: ${JSON.stringify(this.viteConfig.resolve, null, 2)},
  
  define: ${JSON.stringify(this.viteConfig.define, null, 2)},
  
  server: ${JSON.stringify(this.viteConfig.server, null, 2)},
  
  build: ${JSON.stringify(this.viteConfig.build, null, 2)}
});
`;
    
    return configString;
  }
  
  generateMigrationReport() {
    return {
      automaticallyMigrated: [
        'Entry point (use index.html)',
        'CSS extraction',
        'HTML template processing',
        'Basic development server'
      ],
      
      manualMigration: [
        'Custom webpack plugins',
        'Complex loader configurations',
        'Advanced optimization settings',
        'Environment variables (add VITE_ prefix)'
      ],
      
      recommendations: [
        'Update package.json scripts',
        'Move environment variables to .env files with VITE_ prefix',
        'Update import statements for assets',
        'Test hot module replacement functionality'
      ]
    };
  }
}

// Usage
const migrator = new WebpackToViteMigrator('./webpack.config.js');
const viteConfig = migrator.migrate();
const report = migrator.generateMigrationReport();

console.log('Generated Vite Config:');
console.log(viteConfig);
console.log('\nMigration Report:');
console.log(JSON.stringify(report, null, 2));
{% endraw %}
```

### Create React App to Vite Migration
```bash
#!/bin/bash
# migrate-cra-to-vite.sh

echo "Migrating Create React App to Vite..."

# 1. Install Vite and plugins
npm uninstall react-scripts
npm install -D vite @vitejs/plugin-react

# 2. Update package.json scripts
cat > temp_package.json << 'EOF'
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
EOF

# Merge with existing package.json
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const temp = JSON.parse(fs.readFileSync('temp_package.json', 'utf8'));
pkg.scripts = { ...pkg.scripts, ...temp.scripts };
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
"

rm temp_package.json

# 3. Move index.html to root
mv public/index.html index.html

# 4. Update index.html
sed -i 's|%PUBLIC_URL%||g' index.html
sed -i '/<\/body>/i <script type="module" src="/src/index.tsx"></script>' index.html

# 5. Create vite.config.js
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  
  server: {
    port: 3000,
    open: true
  },
  
  build: {
    outDir: 'build', // Keep CRA's build directory
    sourcemap: true
  }
});
EOF

echo "Migration completed! Run 'npm run dev' to start the development server."
```

This comprehensive guide covers modern build tools with practical configurations and migration strategies. Each tool has its strengths, and the choice depends on project requirements, team expertise, and performance needs.
