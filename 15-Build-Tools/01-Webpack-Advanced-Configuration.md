# Webpack Advanced Configuration

## Table of Contents
1. [Advanced Webpack Setup](#advanced-webpack-setup)
2. [Module Resolution & Optimization](#module-resolution--optimization)
3. [Code Splitting Strategies](#code-splitting-strategies)
4. [Asset Management](#asset-management)
5. [Development vs Production](#development-vs-production)
6. [Performance Optimization](#performance-optimization)
7. [Custom Loaders & Plugins](#custom-loaders--plugins)
8. [Troubleshooting & Debugging](#troubleshooting--debugging)

## Advanced Webpack Setup

### Complete Production Configuration
```javascript
// webpack.config.js
const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');
const WorkboxPlugin = require('workbox-webpack-plugin');
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');
const ForkTsCheckerWebpackPlugin = require('fork-ts-checker-webpack-plugin');

const isProduction = process.env.NODE_ENV === 'production';
const isDevelopment = !isProduction;

module.exports = {
  mode: isProduction ? 'production' : 'development',
  
  target: 'browserslist',
  
  entry: {
    main: './src/index.tsx',
    // Separate vendor bundle for better caching
    vendor: ['react', 'react-dom', 'react-router-dom']
  },
  
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: isProduction 
      ? 'js/[name].[contenthash:8].js' 
      : 'js/[name].js',
    chunkFilename: isProduction 
      ? 'js/[name].[contenthash:8].chunk.js' 
      : 'js/[name].chunk.js',
    assetModuleFilename: 'assets/[name].[contenthash:8][ext]',
    publicPath: process.env.PUBLIC_URL || '/',
    clean: true,
    // Enable modern output for better performance
    environment: {
      arrowFunction: true,
      bigIntLiteral: false,
      const: true,
      destructuring: true,
      dynamicImport: true,
      forOf: true,
      module: true
    }
  },
  
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@types': path.resolve(__dirname, 'src/types'),
      '@assets': path.resolve(__dirname, 'src/assets'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@store': path.resolve(__dirname, 'src/store')
    },
    // Reduce resolve attempts for better performance
    modules: ['node_modules'],
    symlinks: false,
    cacheWithContext: false
  },
  
  module: {
    // Improve build performance
    noParse: /^(vue|lodash|jquery)$/,
    
    rules: [
      // TypeScript/JavaScript processing
      {
        test: /\.(ts|tsx|js|jsx)$/,
        exclude: /node_modules/,
        use: [
          // Use thread-loader for parallel processing
          {
            loader: 'thread-loader',
            options: {
              workers: require('os').cpus().length - 1,
              poolTimeout: isDevelopment ? Infinity : 2000
            }
          },
          {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
              cacheCompression: false,
              compact: isProduction,
              presets: [
                [
                  '@babel/preset-env',
                  {
                    useBuiltIns: 'usage',
                    corejs: { version: 3, proposals: true },
                    modules: false,
                    targets: 'defaults'
                  }
                ],
                [
                  '@babel/preset-react',
                  {
                    runtime: 'automatic',
                    development: isDevelopment
                  }
                ],
                '@babel/preset-typescript'
              ],
              plugins: [
                ['@babel/plugin-proposal-decorators', { legacy: true }],
                ['@babel/plugin-proposal-class-properties', { loose: true }],
                '@babel/plugin-proposal-object-rest-spread',
                '@babel/plugin-syntax-dynamic-import',
                isDevelopment && 'react-refresh/babel'
              ].filter(Boolean)
            }
          }
        ]
      },
      
      // CSS processing
      {
        test: /\.css$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: {
                auto: (resourcePath) => resourcePath.includes('.module.'),
                localIdentName: isProduction 
                  ? '[hash:base64:8]' 
                  : '[name]__[local]--[hash:base64:5]',
                exportLocalsConvention: 'camelCase'
              },
              importLoaders: 1,
              sourceMap: isDevelopment
            }
          },
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  'postcss-flexbugs-fixes',
                  [
                    'postcss-preset-env',
                    {
                      autoprefixer: {
                        flexbox: 'no-2009'
                      },
                      stage: 3
                    }
                  ],
                  'postcss-normalize'
                ]
              },
              sourceMap: isDevelopment
            }
          }
        ]
      },
      
      // SCSS processing
      {
        test: /\.(scss|sass)$/,
        use: [
          isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: {
                auto: (resourcePath) => resourcePath.includes('.module.'),
                localIdentName: isProduction 
                  ? '[hash:base64:8]' 
                  : '[name]__[local]--[hash:base64:5]'
              },
              importLoaders: 3,
              sourceMap: isDevelopment
            }
          },
          'postcss-loader',
          {
            loader: 'sass-loader',
            options: {
              sourceMap: isDevelopment,
              sassOptions: {
                includePaths: [path.resolve(__dirname, 'src/styles')]
              }
            }
          }
        ]
      },
      
      // Asset processing
      {
        test: /\.(png|jpe?g|gif|svg|webp|avif)$/i,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8192 // 8kb
          }
        },
        generator: {
          filename: 'assets/images/[name].[contenthash:8][ext]'
        }
      },
      
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'assets/fonts/[name].[contenthash:8][ext]'
        }
      },
      
      {
        test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'assets/media/[name].[contenthash:8][ext]'
        }
      }
    ]
  },
  
  plugins: [
    // HTML template
    new HtmlWebpackPlugin({
      template: './public/index.html',
      favicon: './public/favicon.ico',
      inject: true,
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
    
    // Environment variables
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
      'process.env.PUBLIC_URL': JSON.stringify(process.env.PUBLIC_URL || ''),
      __DEV__: isDevelopment,
      __PROD__: isProduction
    }),
    
    // TypeScript type checking
    new ForkTsCheckerWebpackPlugin({
      async: isDevelopment,
      typescript: {
        typescriptPath: require.resolve('typescript'),
        configFile: path.resolve(__dirname, 'tsconfig.json'),
        diagnosticOptions: {
          syntactic: true
        },
        mode: 'write-references'
      },
      eslint: {
        files: './src/**/*.{ts,tsx,js,jsx}'
      }
    }),
    
    // ESLint integration
    new ESLintPlugin({
      extensions: ['js', 'jsx', 'ts', 'tsx'],
      formatter: require.resolve('react-dev-utils/eslintFormatter'),
      eslintPath: require.resolve('eslint'),
      failOnError: !isDevelopment,
      context: path.resolve(__dirname, 'src'),
      cache: true,
      cacheLocation: path.resolve(__dirname, 'node_modules/.cache/.eslintcache')
    }),
    
    // Development plugins
    ...(isDevelopment ? [
      new ReactRefreshWebpackPlugin({
        overlay: {
          entry: require.resolve('react-dev-utils/webpackHotDevClient'),
          module: require.resolve('react-dev-utils/refreshOverlayInterop'),
          sockIntegration: 'whm'
        }
      }),
      new webpack.HotModuleReplacementPlugin()
    ] : []),
    
    // Production plugins
    ...(isProduction ? [
      new MiniCssExtractPlugin({
        filename: 'css/[name].[contenthash:8].css',
        chunkFilename: 'css/[name].[contenthash:8].chunk.css'
      }),
      
      new CompressionPlugin({
        algorithm: 'gzip',
        test: /\.(js|css|html|svg)$/,
        threshold: 8192,
        minRatio: 0.8
      }),
      
      new webpack.ids.HashedModuleIdsPlugin({
        hashFunction: 'xxhash64',
        hashDigest: 'base64'
      }),
      
      // Bundle analyzer (optional)
      ...(process.env.ANALYZE === 'true' ? [
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: 'bundle-report.html'
        })
      ] : [])
    ] : [])
  ],
  
  optimization: {
    minimize: isProduction,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          parse: {
            ecma: 8
          },
          compress: {
            ecma: 5,
            warnings: false,
            comparisons: false,
            inline: 2,
            drop_console: true,
            drop_debugger: true,
            pure_funcs: ['console.log', 'console.info', 'console.debug']
          },
          mangle: {
            safari10: true
          },
          output: {
            ecma: 5,
            comments: false,
            ascii_only: true
          }
        },
        parallel: true,
        extractComments: false
      }),
      
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            'default',
            {
              discardComments: { removeAll: true }
            }
          ]
        }
      })
    ],
    
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        default: false,
        vendors: false,
        
        // Vendor bundle
        vendor: {
          name: 'vendor',
          chunks: 'all',
          test: /[\\/]node_modules[\\/]/,
          priority: 20
        },
        
        // Common chunks
        common: {
          name: 'common',
          chunks: 'all',
          minChunks: 2,
          priority: 10,
          reuseExistingChunk: true,
          enforce: true
        },
        
        // React specific
        react: {
          name: 'react',
          chunks: 'all',
          test: /[\\/]node_modules[\\/](react|react-dom|react-router|react-router-dom)[\\/]/,
          priority: 30
        },
        
        // UI libraries
        ui: {
          name: 'ui',
          chunks: 'all',
          test: /[\\/]node_modules[\\/](@mui|@chakra-ui|antd|@ant-design)[\\/]/,
          priority: 25
        }
      }
    },
    
    runtimeChunk: {
      name: 'runtime'
    },
    
    moduleIds: 'deterministic',
    chunkIds: 'deterministic'
  },
  
  devServer: {
    static: {
      directory: path.join(__dirname, 'public')
    },
    compress: true,
    port: 3000,
    open: true,
    hot: true,
    historyApiFallback: true,
    client: {
      overlay: {
        errors: true,
        warnings: false
      }
    }
  },
  
  devtool: isDevelopment ? 'eval-source-map' : 'source-map',
  
  // Performance hints
  performance: {
    hints: isProduction ? 'warning' : false,
    maxEntrypointSize: 250000,
    maxAssetSize: 250000
  },
  
  // Stats configuration
  stats: {
    preset: 'minimal',
    colors: true,
    timings: true,
    chunks: false,
    chunkModules: false,
    modules: false,
    children: false,
    version: false,
    hash: false,
    builtAt: false,
    entrypoints: false
  }
};
```

## Module Resolution & Optimization

### Advanced Resolve Configuration
```javascript
// Advanced module resolution
module.exports = {
  resolve: {
    // Extension priority
    extensions: ['.ts', '.tsx', '.js', '.jsx', '.json', '.wasm'],
    
    // Module directories
    modules: [
      'node_modules',
      path.resolve(__dirname, 'src'),
      path.resolve(__dirname, 'src/shared')
    ],
    
    // Aliases for better imports
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@types': path.resolve(__dirname, 'src/types'),
      '@assets': path.resolve(__dirname, 'src/assets'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@store': path.resolve(__dirname, 'src/store'),
      '@config': path.resolve(__dirname, 'src/config'),
      
      // Performance aliases
      'lodash': 'lodash-es',
      'moment': 'dayjs',
      
      // Development aliases
      ...(isDevelopment && {
        'react-dom': '@hot-loader/react-dom'
      })
    },
    
    // Fallback for Node.js modules
    fallback: {
      crypto: require.resolve('crypto-browserify'),
      stream: require.resolve('stream-browserify'),
      buffer: require.resolve('buffer'),
      util: require.resolve('util'),
      url: require.resolve('url'),
      path: require.resolve('path-browserify'),
      os: require.resolve('os-browserify/browser'),
      https: require.resolve('https-browserify'),
      http: require.resolve('stream-http'),
      fs: false,
      net: false,
      tls: false
    },
    
    // Symlinks handling
    symlinks: false,
    
    // Cache resolution
    cache: true,
    cacheWithContext: false,
    
    // Main fields priority
    mainFields: ['browser', 'module', 'main'],
    
    // Conditionals for exports field
    conditionNames: ['import', 'module', 'browser', 'default']
  }
};
```

### Tree Shaking Optimization
```javascript
// Optimize tree shaking
module.exports = {
  optimization: {
    usedExports: true,
    providedExports: true,
    sideEffects: false, // or array of files with side effects
    
    // Inner graph analysis
    innerGraph: true,
    
    // Mangling for better compression
    mangleExports: 'size'
  },
  
  // Package.json side effects
  module: {
    rules: [
      {
        test: /\.js$/,
        sideEffects: false
      },
      {
        test: /\.css$/,
        sideEffects: true
      }
    ]
  }
};
```

## Code Splitting Strategies

### Route-Based Code Splitting
```javascript
// Route-based splitting with React Router
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import LoadingSpinner from '@components/LoadingSpinner';

// Lazy load route components
const Home = lazy(() => import('@pages/Home'));
const About = lazy(() => import('@pages/About'));
const Dashboard = lazy(() => import('@pages/Dashboard'));
const Profile = lazy(() => import('@pages/Profile'));

// Error boundary for lazy components
const LazyWrapper = ({ children }) => (
  <Suspense fallback={<LoadingSpinner />}>
    {children}
  </Suspense>
);

export const AppRoutes = () => (
  <Routes>
    <Route path="/" element={
      <LazyWrapper>
        <Home />
      </LazyWrapper>
    } />
    <Route path="/about" element={
      <LazyWrapper>
        <About />
      </LazyWrapper>
    } />
    <Route path="/dashboard/*" element={
      <LazyWrapper>
        <Dashboard />
      </LazyWrapper>
    } />
    <Route path="/profile" element={
      <LazyWrapper>
        <Profile />
      </LazyWrapper>
    } />
  </Routes>
);
```

### Component-Based Code Splitting
```javascript
// Component-based splitting
import { lazy, Suspense, useState } from 'react';

// Lazy load heavy components
const Chart = lazy(() => import('@components/Chart'));
const DataTable = lazy(() => import('@components/DataTable'));
const FileUploader = lazy(() => import('@components/FileUploader'));

export const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="dashboard">
      <nav>
        <button onClick={() => setActiveTab('overview')}>Overview</button>
        <button onClick={() => setActiveTab('charts')}>Charts</button>
        <button onClick={() => setActiveTab('data')}>Data</button>
        <button onClick={() => setActiveTab('upload')}>Upload</button>
      </nav>
      
      <div className="dashboard-content">
        {activeTab === 'charts' && (
          <Suspense fallback={<div>Loading charts...</div>}>
            <Chart />
          </Suspense>
        )}
        
        {activeTab === 'data' && (
          <Suspense fallback={<div>Loading data table...</div>}>
            <DataTable />
          </Suspense>
        )}
        
        {activeTab === 'upload' && (
          <Suspense fallback={<div>Loading uploader...</div>}>
            <FileUploader />
          </Suspense>
        )}
      </div>
    </div>
  );
};
```

### Library Code Splitting
```javascript
// Split large libraries
export const loadMoment = () => import('moment');
export const loadLodash = () => import('lodash');
export const loadD3 = () => import('d3');

// Usage with dynamic imports
const DatePicker = () => {
  const [moment, setMoment] = useState(null);

  useEffect(() => {
    loadMoment().then(momentModule => {
      setMoment(momentModule.default);
    });
  }, []);

  if (!moment) return <div>Loading...</div>;

  return (
    <input
      type="date"
      defaultValue={moment().format('YYYY-MM-DD')}
    />
  );
};
```

### Advanced SplitChunks Configuration
```javascript
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      minSize: 20000,
      minRemainingSize: 0,
      minChunks: 1,
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      enforceSizeThreshold: 50000,
      
      cacheGroups: {
        // Disable default groups
        default: false,
        vendors: false,
        
        // React ecosystem
        react: {
          name: 'react',
          test: /[\\/]node_modules[\\/](react|react-dom|react-router)[\\/]/,
          chunks: 'all',
          priority: 40,
          enforce: true
        },
        
        // UI libraries
        ui: {
          name: 'ui',
          test: /[\\/]node_modules[\\/](@mui|@chakra-ui|antd|styled-components)[\\/]/,
          chunks: 'all',
          priority: 35,
          enforce: true
        },
        
        // Utility libraries
        utils: {
          name: 'utils',
          test: /[\\/]node_modules[\\/](lodash|moment|dayjs|uuid|axios)[\\/]/,
          chunks: 'all',
          priority: 30,
          enforce: true
        },
        
        // Polyfills
        polyfills: {
          name: 'polyfills',
          test: /[\\/]node_modules[\\/](core-js|regenerator-runtime)[\\/]/,
          chunks: 'all',
          priority: 25,
          enforce: true
        },
        
        // Large libraries (split individually)
        lodash: {
          name: 'lodash',
          test: /[\\/]node_modules[\\/]lodash[\\/]/,
          chunks: 'all',
          priority: 45,
          enforce: true
        },
        
        // Common application code
        common: {
          name: 'common',
          chunks: 'all',
          minChunks: 2,
          priority: 20,
          reuseExistingChunk: true
        },
        
        // Async chunks
        async: {
          name: 'async',
          chunks: 'async',
          minChunks: 2,
          priority: 15
        }
      }
    }
  }
};
```

## Asset Management

### Image Optimization
```javascript
// Image processing rules
module.exports = {
  module: {
    rules: [
      {
        test: /\.(png|jpe?g|gif|svg|webp|avif)$/i,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8192 // 8kb
          }
        },
        use: [
          {
            loader: 'image-webpack-loader',
            options: {
              mozjpeg: {
                progressive: true,
                quality: 85
              },
              optipng: {
                enabled: false
              },
              pngquant: {
                quality: [0.65, 0.90],
                speed: 4
              },
              gifsicle: {
                interlaced: false
              },
              webp: {
                quality: 85
              }
            }
          }
        ],
        generator: {
          filename: 'assets/images/[name].[contenthash:8][ext]'
        }
      }
    ]
  }
};
```

### Font Loading Strategy
```javascript
// Font optimization
module.exports = {
  module: {
    rules: [
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'assets/fonts/[name].[contenthash:8][ext]'
        }
      }
    ]
  },
  
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      templateParameters: {
        preloadFonts: [
          '/assets/fonts/inter-var.woff2',
          '/assets/fonts/roboto-regular.woff2'
        ]
      }
    })
  ]
};

// HTML template with font preloading
// <% preloadFonts.forEach(font => { %>
//   <link rel="preload" href="<%= font %>" as="font" type="font/woff2" crossorigin>
// <% }); %>
```

### CSS Asset Management
```javascript
// CSS optimization and extraction
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          isProduction ? {
            loader: MiniCssExtractPlugin.loader,
            options: {
              publicPath: '../'
            }
          } : 'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: {
                auto: true,
                localIdentName: isProduction 
                  ? '[hash:base64:8]' 
                  : '[name]__[local]--[hash:base64:5]'
              },
              importLoaders: 1
            }
          },
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  'autoprefixer',
                  'cssnano',
                  'postcss-custom-properties',
                  'postcss-custom-media'
                ]
              }
            }
          }
        ]
      }
    ]
  },
  
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/[name].[contenthash:8].css',
      chunkFilename: 'css/[name].[contenthash:8].chunk.css',
      ignoreOrder: false
    })
  ],
  
  optimization: {
    minimizer: [
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            'default',
            {
              discardComments: { removeAll: true },
              normalizeUnicode: false
            }
          ]
        }
      })
    ]
  }
};
```

## Development vs Production

### Development Configuration
```javascript
// webpack.dev.js
const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');

module.exports = merge(common, {
  mode: 'development',
  
  devtool: 'eval-source-map',
  
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
      publicPath: '/'
    },
    compress: true,
    port: 3000,
    open: true,
    hot: true,
    historyApiFallback: true,
    
    client: {
      overlay: {
        errors: true,
        warnings: false,
        runtimeErrors: true
      },
      progress: true
    },
    
    // Proxy API calls
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      }
    },
    
    // HTTPS for development
    https: process.env.HTTPS === 'true',
    
    // Allow external connections
    allowedHosts: 'all'
  },
  
  plugins: [
    new ReactRefreshWebpackPlugin({
      overlay: {
        entry: require.resolve('react-dev-utils/webpackHotDevClient'),
        module: require.resolve('react-dev-utils/refreshOverlayInterop'),
        sockIntegration: 'whm'
      }
    })
  ],
  
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        default: false,
        vendors: false,
        vendor: {
          name: 'vendor',
          chunks: 'all',
          test: /[\\/]node_modules[\\/]/,
          enforce: true
        }
      }
    }
  },
  
  // Faster builds in development
  cache: {
    type: 'filesystem',
    buildDependencies: {
      config: [__filename]
    }
  }
});
```

### Production Configuration
```javascript
// webpack.prod.js
const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const CompressionPlugin = require('compression-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = merge(common, {
  mode: 'production',
  
  devtool: 'source-map',
  
  plugins: [
    // Gzip compression
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
      filename: '[path][base].gz'
    }),
    
    // Brotli compression
    new CompressionPlugin({
      algorithm: 'brotliCompress',
      test: /\.(js|css|html|svg)$/,
      compressionOptions: {
        level: 11
      },
      threshold: 8192,
      minRatio: 0.8,
      filename: '[path][base].br'
    }),
    
    // Bundle analysis
    ...(process.env.ANALYZE === 'true' ? [
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        openAnalyzer: false,
        reportFilename: '../reports/bundle-report.html'
      })
    ] : [])
  ],
  
  optimization: {
    minimize: true,
    
    // Advanced splitting for production
    splitChunks: {
      chunks: 'all',
      minSize: 20000,
      maxSize: 244000,
      
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
          chunks: 'all'
        },
        
        common: {
          name: 'common',
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
          chunks: 'all'
        }
      }
    },
    
    // Module concatenation
    concatenateModules: true,
    
    // Deterministic module IDs
    moduleIds: 'deterministic',
    chunkIds: 'deterministic'
  },
  
  performance: {
    hints: 'warning',
    maxEntrypointSize: 250000,
    maxAssetSize: 250000,
    assetFilter: function(assetFilename) {
      return !assetFilename.endsWith('.map');
    }
  }
});
```

## Performance Optimization

### Build Performance
```javascript
// Build performance optimization
module.exports = {
  // Parallel processing
  module: {
    rules: [
      {
        test: /\.(ts|tsx|js|jsx)$/,
        use: [
          {
            loader: 'thread-loader',
            options: {
              workers: require('os').cpus().length - 1,
              poolTimeout: isDevelopment ? Infinity : 2000
            }
          },
          'babel-loader'
        ]
      }
    ]
  },
  
  // Caching
  cache: {
    type: 'filesystem',
    version: '1.0',
    cacheDirectory: path.resolve(__dirname, 'node_modules/.cache/webpack'),
    buildDependencies: {
      config: [__filename],
      tsconfig: [path.resolve(__dirname, 'tsconfig.json')]
    },
    managedPaths: [path.resolve(__dirname, 'node_modules')],
    profile: false,
    maxAge: 5184000000 // 60 days
  },
  
  // Resolve optimization
  resolve: {
    symlinks: false,
    cacheWithContext: false,
    modules: ['node_modules']
  },
  
  // Exclude large libraries from parsing
  module: {
    noParse: /^(vue|lodash|jquery)$/
  },
  
  // Lazy compilation (Webpack 5.17+)
  experiments: {
    lazyCompilation: {
      imports: true,
      entries: false
    }
  }
};
```

### Runtime Performance
```javascript
// Runtime performance optimization
module.exports = {
  optimization: {
    // Tree shaking
    usedExports: true,
    sideEffects: false,
    
    // Module concatenation (scope hoisting)
    concatenateModules: true,
    
    // Split chunks for better caching
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all'
        }
      }
    },
    
    // Runtime chunk for better caching
    runtimeChunk: {
      name: 'runtime'
    }
  },
  
  // Output configuration for HTTP/2
  output: {
    chunkFilename: '[name].[contenthash:8].chunk.js',
    filename: '[name].[contenthash:8].js'
  }
};
```

## Custom Loaders & Plugins

### Custom Loader Example
```javascript
{% raw %}
{% raw %}
// loaders/svg-react-loader.js
const { getOptions } = require('loader-utils');
const { validate } = require('schema-utils');

const schema = {
  type: 'object',
  properties: {
    typescript: {
      type: 'boolean'
    },
    template: {
      type: 'string'
    }
  }
};

module.exports = function(source) {
  const options = getOptions(this) || {};
  validate(schema, options, 'SVG React Loader');
  
  const callback = this.async();
  
  // Transform SVG to React component
  const componentName = this.resourcePath
    .split('/')
    .pop()
    .replace('.svg', '')
    .replace(/[^a-zA-Z0-9]/g, '')
    .replace(/^./, str => str.toUpperCase());
  
  const template = options.typescript ? `
import React from 'react';

interface ${componentName}Props {
  className?: string;
  style?: React.CSSProperties;
}

const ${componentName}: React.FC<${componentName}Props> = ({ className, style }) => (
  ${source.replace('<svg', '<svg className={className} style={style}')}
);

export default ${componentName};
` : `
import React from 'react';

const ${componentName} = ({ className, style }) => (
  ${source.replace('<svg', '<svg className={className} style={style}')}
);

export default ${componentName};
`;

  callback(null, template);
};

// Usage in webpack config
module.exports = {
  module: {
    rules: [
      {
        test: /\.svg$/,
        use: [
          {
            loader: path.resolve('./loaders/svg-react-loader.js'),
            options: {
              typescript: true
            }
          }
        ]
      }
    ]
  }
};
{% endraw %}
{% endraw %}
```

### Custom Plugin Example
```javascript
// plugins/bundle-info-plugin.js
class BundleInfoPlugin {
  constructor(options = {}) {
    this.options = {
      filename: 'bundle-info.json',
      includeModules: false,
      ...options
    };
  }
  
  apply(compiler) {
    compiler.hooks.emit.tapAsync('BundleInfoPlugin', (compilation, callback) => {
      const stats = compilation.getStats().toJson({
        all: false,
        assets: true,
        chunks: true,
        modules: this.options.includeModules,
        entrypoints: true
      });
      
      const bundleInfo = {
        timestamp: new Date().toISOString(),
        webpack: compiler.webpack.version,
        hash: stats.hash,
        assets: stats.assets.map(asset => ({
          name: asset.name,
          size: asset.size,
          gzipSize: this.estimateGzipSize(asset.size)
        })),
        chunks: stats.chunks.map(chunk => ({
          id: chunk.id,
          names: chunk.names,
          size: chunk.size,
          files: chunk.files
        })),
        entrypoints: Object.keys(stats.entrypoints).reduce((acc, name) => {
          acc[name] = {
            assets: stats.entrypoints[name].assets,
            size: stats.entrypoints[name].assets.reduce((total, asset) => {
              const assetInfo = stats.assets.find(a => a.name === asset.name);
              return total + (assetInfo ? assetInfo.size : 0);
            }, 0)
          };
          return acc;
        }, {})
      };
      
      if (this.options.includeModules) {
        bundleInfo.modules = stats.modules;
      }
      
      const json = JSON.stringify(bundleInfo, null, 2);
      
      compilation.assets[this.options.filename] = {
        source: () => json,
        size: () => json.length
      };
      
      callback();
    });
  }
  
  estimateGzipSize(size) {
    return Math.round(size * 0.3); // Rough estimate
  }
}

module.exports = BundleInfoPlugin;

// Usage
const BundleInfoPlugin = require('./plugins/bundle-info-plugin');

module.exports = {
  plugins: [
    new BundleInfoPlugin({
      filename: 'build-stats.json',
      includeModules: true
    })
  ]
};
```

### Progressive Web App Plugin
```javascript
// plugins/pwa-plugin.js
const WorkboxPlugin = require('workbox-webpack-plugin');

class PWAPlugin {
  constructor(options = {}) {
    this.options = {
      swDest: 'sw.js',
      clientsClaim: true,
      skipWaiting: true,
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.googleapis\.com/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'google-fonts-stylesheets'
          }
        },
        {
          urlPattern: /^https:\/\/fonts\.gstatic\.com/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'google-fonts-webfonts',
            expiration: {
              maxAgeSeconds: 60 * 60 * 24 * 365,
              maxEntries: 30
            }
          }
        },
        {
          urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
          handler: 'CacheFirst',
          options: {
            cacheName: 'images',
            expiration: {
              maxEntries: 60,
              maxAgeSeconds: 30 * 24 * 60 * 60 // 30 Days
            }
          }
        }
      ],
      ...options
    };
  }
  
  apply(compiler) {
    new WorkboxPlugin.GenerateSW(this.options).apply(compiler);
  }
}

module.exports = PWAPlugin;
```

## Troubleshooting & Debugging

### Common Issues and Solutions

#### Memory Issues
```javascript
{% raw %}
{% raw %}
// Increase Node.js memory limit
// package.json
{
  "scripts": {
    "build": "node --max-old-space-size=8192 node_modules/.bin/webpack --mode=production"
  }
}

// Monitor memory usage
const webpack = require('webpack');
const config = require('./webpack.config');

const compiler = webpack(config);

compiler.hooks.done.tap('MemoryUsage', (stats) => {
  const memUsage = process.memoryUsage();
  console.log(`Memory usage: ${Math.round(memUsage.heapUsed / 1024 / 1024 * 100) / 100} MB`);
});
{% endraw %}
{% endraw %}
```

#### Build Performance Analysis
```javascript
// Speed measure plugin
const SpeedMeasurePlugin = require('speed-measure-webpack-plugin');
const smp = new SpeedMeasurePlugin();

module.exports = smp.wrap({
  // webpack config
});

// Bundle analysis
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'server',
      openAnalyzer: true
    })
  ]
};
```

#### Debugging Webpack Configuration
```javascript
// Debug webpack config
const util = require('util');

const debugConfig = (config) => {
  console.log(util.inspect(config, {
    colors: true,
    depth: null,
    maxArrayLength: null
  }));
};

// Validate configuration
const webpack = require('webpack');
const config = require('./webpack.config');

webpack.validate(config);
```

#### Source Map Debugging
```javascript
// Different source map options for debugging
module.exports = {
  devtool: process.env.NODE_ENV === 'development' 
    ? 'eval-source-map'  // Fast rebuild, readable
    : 'source-map',      // Production quality
    
  // Alternative options:
  // 'cheap-module-source-map' - Faster build
  // 'inline-source-map' - Inline maps
  // 'eval-cheap-module-source-map' - Development balance
};
```

#### Hot Module Replacement Issues
```javascript
// HMR debugging
module.exports = {
  devServer: {
    hot: true,
    liveReload: false, // Disable if using HMR
    
    client: {
      logging: 'verbose',
      overlay: {
        errors: true,
        warnings: false
      }
    }
  },
  
  plugins: [
    new webpack.HotModuleReplacementPlugin()
  ]
};

// Component HMR acceptance
if (module.hot) {
  module.hot.accept('./App', () => {
    const NextApp = require('./App').default;
    ReactDOM.render(<NextApp />, document.getElementById('root'));
  });
}
```

### Performance Monitoring
```javascript
{% raw %}
{% raw %}
// Build time monitoring
const start = Date.now();

compiler.hooks.done.tap('BuildTime', () => {
  const buildTime = Date.now() - start;
  console.log(`Build completed in ${buildTime}ms`);
  
  if (buildTime > 30000) {
    console.warn('⚠️ Build time exceeded 30 seconds');
  }
});

// File size monitoring
compiler.hooks.afterEmit.tap('FileSizeMonitor', (compilation) => {
  const assets = compilation.getAssets();
  const largeAssets = assets.filter(asset => asset.info.size > 250000);
  
  if (largeAssets.length > 0) {
    console.warn('⚠️ Large assets detected:');
    largeAssets.forEach(asset => {
      console.warn(`  ${asset.name}: ${Math.round(asset.info.size / 1024)}kb`);
    });
  }
});
{% endraw %}
{% endraw %}
```

### Error Handling
```javascript
// Comprehensive error handling
compiler.run((err, stats) => {
  if (err) {
    console.error('❌ Webpack compilation error:', err);
    process.exit(1);
  }
  
  const info = stats.toJson();
  
  if (stats.hasErrors()) {
    console.error('❌ Compilation errors:');
    info.errors.forEach(error => console.error(error));
    process.exit(1);
  }
  
  if (stats.hasWarnings()) {
    console.warn('⚠️ Compilation warnings:');
    info.warnings.forEach(warning => console.warn(warning));
  }
  
  console.log('✅ Build completed successfully');
});
```

This comprehensive guide covers advanced Webpack configuration patterns, optimization strategies, and troubleshooting techniques. Each section provides production-ready code examples that can be adapted to specific project requirements while maintaining performance and maintainability.
