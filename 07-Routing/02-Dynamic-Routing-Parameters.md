# Dynamic Routing & Parameters

## 🎯 Learning Objectives
By the end of this section, you will:
- Master URL parameters and route matching patterns
- Implement dynamic route segments and wildcard routes
- Handle query strings and search parameters
- Build parameterized routes for data-driven applications
- Implement route validation and parameter constraints
- Optimize dynamic routing performance
- Handle route parameter changes and updates

## 📚 Table of Contents
1. [URL Parameters Fundamentals](#url-parameters-fundamentals)
2. [Route Patterns & Matching](#route-patterns--matching)
3. [Query String Parameters](#query-string-parameters)
4. [Optional and Wildcard Parameters](#optional-and-wildcard-parameters)
5. [Parameter Validation](#parameter-validation)
6. [Dynamic Route Generation](#dynamic-route-generation)
7. [Performance Optimization](#performance-optimization)
8. [Best Practices](#best-practices)
9. [Advanced Patterns](#advanced-patterns)

## URL Parameters Fundamentals

### Basic Route Parameters
Route parameters are dynamic segments in URLs that capture values to pass to components.

```jsx
import { Routes, Route } from 'react-router-dom';
import { UserProfile, ProductDetail, BlogPost } from './components';

function App() {
  return (
    <Routes>
      {/* Single parameter */}
      <Route path="/users/:userId" element={<UserProfile />} />
      
      {/* Multiple parameters */}
      <Route path="/products/:category/:productId" element={<ProductDetail />} />
      
      {/* Nested parameters */}
      <Route path="/blog/:year/:month/:slug" element={<BlogPost />} />
      
      {/* Parameter with specific format */}
      <Route path="/orders/:orderId" element={<OrderDetail />} />
    </Routes>
  );
}
```

### Accessing Parameters with useParams
```jsx
{% raw %}
import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

function UserProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        
        if (!response.ok) {
          throw new Error(`User not found: ${response.status}`);
        }
        
        const userData = await response.json();
        setUser(userData);
      } catch (err) {
        setError(err.message);
        // Optionally redirect to 404
        // navigate('/404', { replace: true });
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchUser();
    }
  }, [userId, navigate]);

  if (loading) return <div>Loading user...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-profile">
      <h1>{user.name}</h1>
      <p>User ID: {userId}</p>
      <p>Email: {user.email}</p>
      <p>Joined: {new Date(user.createdAt).toLocaleDateString()}</p>
    </div>
  );
}
{% endraw %}
```

### Multiple Parameters Example
```jsx
{% raw %}
function ProductDetail() {
  const { category, productId } = useParams();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await fetch(`/api/products/${category}/${productId}`);
        const productData = await response.json();
        setProduct(productData);
      } catch (error) {
        console.error('Failed to fetch product:', error);
      }
    };

    fetchProduct();
  }, [category, productId]);

  return (
    <div className="product-detail">
      <nav className="breadcrumb">
        <Link to="/products">Products</Link> &gt;
        <Link to={`/products/${category}`}>{category}</Link> &gt;
        <span>{product?.name}</span>
      </nav>
      
      {product && (
        <div>
          <h1>{product.name}</h1>
          <p>Category: {category}</p>
          <p>Product ID: {productId}</p>
          <p>Price: ${product.price}</p>
          <p>{product.description}</p>
        </div>
      )}
    </div>
  );
}
{% endraw %}
```

## Route Patterns & Matching

### Exact vs Partial Matching
React Router v6 uses exact matching by default for route paths.

```jsx
function App() {
  return (
    <Routes>
      {/* Exact match - only matches "/products" */}
      <Route path="/products" element={<ProductList />} />
      
      {/* Parameter route - matches "/products/123" */}
      <Route path="/products/:id" element={<ProductDetail />} />
      
      {/* Wildcard - matches "/products/anything/else" */}
      <Route path="/products/*" element={<ProductsLayout />} />
      
      {/* Index route - renders when parent matches exactly */}
      <Route path="/dashboard" element={<DashboardLayout />}>
        <Route index element={<DashboardHome />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
```

### Route Priority and Ordering
Routes are matched in the order they appear. More specific routes should come first.

```jsx
function App() {
  return (
    <Routes>
      {/* Most specific routes first */}
      <Route path="/users/new" element={<CreateUser />} />
      <Route path="/users/me" element={<CurrentUser />} />
      <Route path="/users/:userId" element={<UserProfile />} />
      
      {/* Special routes */}
      <Route path="/products/featured" element={<FeaturedProducts />} />
      <Route path="/products/:category" element={<CategoryProducts />} />
      <Route path="/products/:category/:productId" element={<ProductDetail />} />
      
      {/* Catch-all route last */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
```

### Complex Route Patterns
```jsx
// Date-based routes
function BlogRoutes() {
  return (
    <Routes>
      {/* Year archives */}
      <Route path="/blog/:year" element={<YearArchive />} />
      
      {/* Month archives */}
      <Route path="/blog/:year/:month" element={<MonthArchive />} />
      
      {/* Individual posts */}
      <Route path="/blog/:year/:month/:day/:slug" element={<BlogPost />} />
      
      {/* Category archives */}
      <Route path="/blog/category/:category" element={<CategoryArchive />} />
      
      {/* Tag archives */}
      <Route path="/blog/tag/:tag" element={<TagArchive />} />
    </Routes>
  );
}

function BlogPost() {
  const { year, month, day, slug } = useParams();
  
  const postDate = new Date(year, month - 1, day);
  const isValidDate = !isNaN(postDate.getTime());

  if (!isValidDate) {
    return <Navigate to="/404" replace />;
  }

  return (
    <article>
      <h1>Blog Post: {slug}</h1>
      <time>{postDate.toLocaleDateString()}</time>
      {/* Post content */}
    </article>
  );
}
```

## Query String Parameters

### Using useSearchParams Hook
```jsx
{% raw %}
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';

function ProductSearch() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // Extract current parameters
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || 'all';
  const minPrice = searchParams.get('minPrice') || '';
  const maxPrice = searchParams.get('maxPrice') || '';
  const sortBy = searchParams.get('sortBy') || 'name';
  const page = parseInt(searchParams.get('page') || '1');

  const [products, setProducts] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);

  // Update search parameters
  const updateParams = (updates) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      
      Object.entries(updates).forEach(([key, value]) => {
        if (value === null || value === undefined || value === '') {
          newParams.delete(key);
        } else {
          newParams.set(key, value);
        }
      });
      
      return newParams;
    });
  };

  // Search products based on parameters
  useEffect(() => {
    const searchProducts = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          q: query,
          category: category !== 'all' ? category : '',
          minPrice,
          maxPrice,
          sortBy,
          page: page.toString(),
          limit: '20'
        });

        const response = await fetch(`/api/products/search?${params}`);
        const data = await response.json();
        
        setProducts(data.products);
        setTotalPages(data.totalPages);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setLoading(false);
      }
    };

    searchProducts();
  }, [query, category, minPrice, maxPrice, sortBy, page]);

  const handleSearch = (newQuery) => {
    updateParams({ q: newQuery, page: 1 });
  };

  const handleCategoryChange = (newCategory) => {
    updateParams({ category: newCategory, page: 1 });
  };

  const handlePriceFilter = (min, max) => {
    updateParams({ minPrice: min, maxPrice: max, page: 1 });
  };

  const handleSort = (newSortBy) => {
    updateParams({ sortBy: newSortBy, page: 1 });
  };

  const handlePageChange = (newPage) => {
    updateParams({ page: newPage });
  };

  return (
    <div className="product-search">
      <div className="search-filters">
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search products..."
        />
        
        <select 
          value={category}
          onChange={(e) => handleCategoryChange(e.target.value)}
        >
          <option value="all">All Categories</option>
          <option value="electronics">Electronics</option>
          <option value="clothing">Clothing</option>
          <option value="books">Books</option>
        </select>
        
        <div className="price-filter">
          <input
            type="number"
            placeholder="Min Price"
            value={minPrice}
            onChange={(e) => handlePriceFilter(e.target.value, maxPrice)}
          />
          <input
            type="number"
            placeholder="Max Price"
            value={maxPrice}
            onChange={(e) => handlePriceFilter(minPrice, e.target.value)}
          />
        </div>
        
        <select 
          value={sortBy}
          onChange={(e) => handleSort(e.target.value)}
        >
          <option value="name">Name</option>
          <option value="price-asc">Price: Low to High</option>
          <option value="price-desc">Price: High to Low</option>
          <option value="rating">Rating</option>
        </select>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          <div className="search-results">
            {products.map(product => (
              <div key={product.id} className="product-card">
                <h3>{product.name}</h3>
                <p>${product.price}</p>
                <Link to={`/products/${product.category}/${product.id}`}>
                  View Details
                </Link>
              </div>
            ))}
          </div>
          
          <div className="pagination">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNum => (
              <button
                key={pageNum}
                onClick={() => handlePageChange(pageNum)}
                className={page === pageNum ? 'active' : ''}
              >
                {pageNum}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
{% endraw %}
```

### Query Parameter Utilities
```jsx
// hooks/useQueryParams.js
import { useSearchParams } from 'react-router-dom';
import { useMemo } from 'react';

export function useQueryParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  const queryParams = useMemo(() => {
    const params = {};
    for (const [key, value] of searchParams.entries()) {
      params[key] = value;
    }
    return params;
  }, [searchParams]);

  const setQueryParam = (key, value) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      if (value === null || value === undefined || value === '') {
        newParams.delete(key);
      } else {
        newParams.set(key, value);
      }
      return newParams;
    });
  };

  const setQueryParams = (updates) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      Object.entries(updates).forEach(([key, value]) => {
        if (value === null || value === undefined || value === '') {
          newParams.delete(key);
        } else {
          newParams.set(key, value);
        }
      });
      return newParams;
    });
  };

  const clearQueryParams = (keys) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      if (Array.isArray(keys)) {
        keys.forEach(key => newParams.delete(key));
      } else if (typeof keys === 'string') {
        newParams.delete(keys);
      } else {
        // Clear all
        return new URLSearchParams();
      }
      return newParams;
    });
  };

  return {
    queryParams,
    setQueryParam,
    setQueryParams,
    clearQueryParams
  };
}
```

## Optional and Wildcard Parameters

### Optional Parameters
```jsx
{% raw %}
// Using optional segments with conditional logic
function UserRoutes() {
  return (
    <Routes>
      {/* Base user route */}
      <Route path="/users" element={<UserList />} />
      
      {/* User profile with optional tab */}
      <Route path="/users/:userId" element={<UserProfile />}>
        <Route index element={<UserOverview />} />
        <Route path="posts" element={<UserPosts />} />
        <Route path="followers" element={<UserFollowers />} />
        <Route path="following" element={<UserFollowing />} />
      </Route>
    </Routes>
  );
}

function UserProfile() {
  const { userId } = useParams();
  const location = useLocation();
  
  // Determine active tab from pathname
  const activeTab = location.pathname.split('/').pop();
  const isOverview = activeTab === userId; // Base profile route

  return (
    <div className="user-profile">
      <div className="user-header">
        <h1>User Profile</h1>
        <nav className="tabs">
          <NavLink 
            to={`/users/${userId}`} 
            end
            className={({ isActive }) => isActive ? 'tab active' : 'tab'}
          >
            Overview
          </NavLink>
          <NavLink 
            to={`/users/${userId}/posts`}
            className={({ isActive }) => isActive ? 'tab active' : 'tab'}
          >
            Posts
          </NavLink>
          <NavLink 
            to={`/users/${userId}/followers`}
            className={({ isActive }) => isActive ? 'tab active' : 'tab'}
          >
            Followers
          </NavLink>
          <NavLink 
            to={`/users/${userId}/following`}
            className={({ isActive }) => isActive ? 'tab active' : 'tab'}
          >
            Following
          </NavLink>
        </nav>
      </div>
      
      <Outlet />
    </div>
  );
}
{% endraw %}
```

### Wildcard Routes
```jsx
{% raw %}
function FileExplorer() {
  return (
    <Routes>
      {/* Catch all file paths */}
      <Route path="/files/*" element={<FileBrowser />} />
      <Route path="/docs/*" element={<DocumentViewer />} />
    </Routes>
  );
}

function FileBrowser() {
  const location = useLocation();
  
  // Extract the wildcard path
  const filePath = location.pathname.replace('/files/', '') || '/';
  const pathSegments = filePath.split('/').filter(Boolean);

  return (
    <div className="file-browser">
      <div className="breadcrumb">
        <Link to="/files">Root</Link>
        {pathSegments.map((segment, index) => {
          const path = '/' + pathSegments.slice(0, index + 1).join('/');
          return (
            <span key={index}>
              {' > '}
              <Link to={`/files${path}`}>{segment}</Link>
            </span>
          );
        })}
      </div>
      
      <div className="file-content">
        <h2>Files in: /{filePath}</h2>
        {/* File listing component */}
        <FileList path={filePath} />
      </div>
    </div>
  );
}
{% endraw %}
```

### Splat Routes (*)
```jsx
function AppRoutes() {
  return (
    <Routes>
      {/* Admin routes with nested wildcard */}
      <Route path="/admin/*" element={<AdminLayout />} />
      
      {/* Help system with dynamic pages */}
      <Route path="/help/*" element={<HelpSystem />} />
      
      {/* 404 catch-all */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

function AdminLayout() {
  const location = useLocation();
  const adminPath = location.pathname.replace('/admin', '') || '/';

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <nav>
          <Link to="/admin">Dashboard</Link>
          <Link to="/admin/users">Users</Link>
          <Link to="/admin/products">Products</Link>
          <Link to="/admin/orders">Orders</Link>
          <Link to="/admin/settings">Settings</Link>
        </nav>
      </aside>
      
      <main className="admin-content">
        <Routes>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/users/:userId" element={<UserEdit />} />
          <Route path="/products" element={<ProductManagement />} />
          <Route path="/products/:productId" element={<ProductEdit />} />
          <Route path="/orders" element={<OrderManagement />} />
          <Route path="/settings" element={<AdminSettings />} />
          <Route path="*" element={<AdminNotFound />} />
        </Routes>
      </main>
    </div>
  );
}
```

## Parameter Validation

### Client-Side Validation
```jsx
import { useParams, Navigate } from 'react-router-dom';

// Validation utilities
const validators = {
  isNumeric: (value) => /^\d+$/.test(value),
  isUUID: (value) => /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value),
  isSlug: (value) => /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value),
  isDate: (year, month, day) => {
    const date = new Date(year, month - 1, day);
    return date.getFullYear() == year && 
           date.getMonth() == month - 1 && 
           date.getDate() == day;
  }
};

function ValidatedRoute({ children, validation }) {
  const params = useParams();
  
  // Validate all parameters
  const isValid = validation.every(({ param, validator, ...options }) => {
    const value = params[param];
    
    if (!value && !options.optional) {
      return false;
    }
    
    if (value && typeof validator === 'function') {
      return validator(value);
    }
    
    if (value && typeof validator === 'string') {
      return validators[validator]?.(value) ?? false;
    }
    
    return true;
  });

  if (!isValid) {
    return <Navigate to="/404" replace />;
  }

  return children;
}

// Usage
function BlogPost() {
  const { year, month, day, slug } = useParams();

  return (
    <ValidatedRoute
      validation={[
        { param: 'year', validator: 'isNumeric' },
        { param: 'month', validator: 'isNumeric' },
        { param: 'day', validator: 'isNumeric' },
        { param: 'slug', validator: 'isSlug' },
        { 
          param: 'date', 
          validator: () => validators.isDate(year, month, day)
        }
      ]}
    >
      <article>
        <h1>Blog Post: {slug}</h1>
        <time>{new Date(year, month - 1, day).toLocaleDateString()}</time>
      </article>
    </ValidatedRoute>
  );
}

function UserProfile() {
  const { userId } = useParams();

  return (
    <ValidatedRoute
      validation={[
        { param: 'userId', validator: 'isNumeric' }
      ]}
    >
      <div>User Profile for ID: {userId}</div>
    </ValidatedRoute>
  );
}
```

### Parameter Transformation Hook
```jsx
// hooks/useValidatedParams.js
import { useParams, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

export function useValidatedParams(paramConfig) {
  const params = useParams();
  const navigate = useNavigate();

  const validatedParams = {};
  let hasError = false;

  Object.entries(paramConfig).forEach(([key, config]) => {
    const value = params[key];
    
    if (!value && config.required) {
      hasError = true;
      return;
    }

    if (!value) {
      validatedParams[key] = config.default;
      return;
    }

    // Transform value
    if (config.transform) {
      try {
        validatedParams[key] = config.transform(value);
      } catch (error) {
        hasError = true;
        return;
      }
    } else {
      validatedParams[key] = value;
    }

    // Validate transformed value
    if (config.validate && !config.validate(validatedParams[key])) {
      hasError = true;
    }
  });

  useEffect(() => {
    if (hasError) {
      navigate('/404', { replace: true });
    }
  }, [hasError, navigate]);

  return hasError ? null : validatedParams;
}

// Usage
function ProductDetail() {
  const params = useValidatedParams({
    category: {
      required: true,
      validate: (value) => ['electronics', 'clothing', 'books'].includes(value)
    },
    productId: {
      required: true,
      transform: (value) => parseInt(value, 10),
      validate: (value) => Number.isInteger(value) && value > 0
    }
  });

  if (!params) {
    return <div>Invalid route parameters</div>;
  }

  const { category, productId } = params;

  return (
    <div>
      <h1>Product {productId} in {category}</h1>
    </div>
  );
}
```

## Dynamic Route Generation

### Route Configuration System
```jsx
// config/routes.js
export const routeConfig = [
  {
    path: '/users/:userId',
    component: 'UserProfile',
    params: {
      userId: { type: 'number', required: true }
    },
    meta: {
      title: 'User Profile',
      requiresAuth: true
    }
  },
  {
    path: '/products/:category/:productId',
    component: 'ProductDetail',
    params: {
      category: { type: 'string', required: true },
      productId: { type: 'number', required: true }
    },
    meta: {
      title: 'Product Details',
      requiresAuth: false
    }
  }
];

// Route generator
function generateRoutes(config, components) {
  return config.map(route => {
    const Component = components[route.component];
    
    return (
      <Route
        key={route.path}
        path={route.path}
        element={
          route.meta.requiresAuth ? (
            <ProtectedRoute>
              <Component />
            </ProtectedRoute>
          ) : (
            <Component />
          )
        }
      />
    );
  });
}
```

### Dynamic Link Generation
```jsx
{% raw %}
// utils/linkHelpers.js
export function generatePath(template, params) {
  return template.replace(/:([^/]+)/g, (match, param) => {
    if (params[param] === undefined) {
      throw new Error(`Missing parameter: ${param}`);
    }
    return encodeURIComponent(params[param]);
  });
}

export function generateQuery(params) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      searchParams.set(key, value);
    }
  });
  return searchParams.toString();
}

// Link builder component
function SmartLink({ to, params = {}, query = {}, children, ...props }) {
  const path = generatePath(to, params);
  const queryString = generateQuery(query);
  const fullPath = queryString ? `${path}?${queryString}` : path;

  return (
    <Link to={fullPath} {...props}>
      {children}
    </Link>
  );
}

// Usage
function ProductCard({ product }) {
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      
      <SmartLink
        to="/products/:category/:productId"
        params={{
          category: product.category,
          productId: product.id
        }}
        query={{
          ref: 'product-list',
          utm_source: 'internal'
        }}
      >
        View Details
      </SmartLink>
    </div>
  );
}
{% endraw %}
```

## Performance Optimization

### Parameter Change Optimization
```jsx
import { useParams, useLocation } from 'react-router-dom';
import { useCallback, useMemo } from 'react';

function OptimizedComponent() {
  const params = useParams();
  const location = useLocation();

  // Memoize expensive computations based on params
  const processedData = useMemo(() => {
    return expensiveDataProcessing(params);
  }, [params]);

  // Optimize parameter-based effects
  const { userId, category } = params;
  
  useEffect(() => {
    // Only re-run when specific params change
    fetchUserData(userId);
  }, [userId]); // Not dependent on all params

  useEffect(() => {
    // Separate effect for category-related data
    fetchCategoryData(category);
  }, [category]);

  return <div>Optimized content</div>;
}
```

### Route Preloading
```jsx
{% raw %}
// utils/routePreloader.js
const routePreloadCache = new Map();

export function preloadRoute(routePath, params = {}) {
  const cacheKey = `${routePath}-${JSON.stringify(params)}`;
  
  if (routePreloadCache.has(cacheKey)) {
    return routePreloadCache.get(cacheKey);
  }

  const preloadPromise = (async () => {
    // Preload route component
    const componentPromise = import(`../pages/${routePath}`);
    
    // Preload route data
    const dataPromise = fetch(`/api${routePath}/${params.id || ''}`);
    
    const [component, data] = await Promise.all([
      componentPromise,
      dataPromise.then(res => res.json())
    ]);

    return { component, data };
  })();

  routePreloadCache.set(cacheKey, preloadPromise);
  return preloadPromise;
}

// Preload on hover
function PreloadLink({ to, params, children, ...props }) {
  const handleMouseEnter = useCallback(() => {
    preloadRoute(to, params);
  }, [to, params]);

  return (
    <Link 
      to={generatePath(to, params)} 
      onMouseEnter={handleMouseEnter}
      {...props}
    >
      {children}
    </Link>
  );
}
{% endraw %}
```

## Best Practices

### 1. Parameter Naming Conventions
```jsx
// Good: Descriptive parameter names
<Route path="/users/:userId/posts/:postId" />
<Route path="/blog/:year/:month/:slug" />
<Route path="/products/:category/:productId" />

// Avoid: Generic parameter names
<Route path="/items/:id1/:id2" />
<Route path="/data/:param" />
```

### 2. URL Structure Design
```jsx
// Good: Hierarchical and logical structure
/users/123
/users/123/posts
/users/123/posts/456
/products/electronics/laptops/789

// Avoid: Flat or confusing structure
/user-123
/post-456-user-123
/laptop-electronics-789
```

### 3. Error Handling for Invalid Parameters
```jsx
{% raw %}
function RobustComponent() {
  const params = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    const validateAndFetch = async () => {
      try {
        // Validate parameters
        if (!params.userId || isNaN(params.userId)) {
          throw new Error('Invalid user ID');
        }

        // Fetch data
        const response = await fetch(`/api/users/${params.userId}`);
        
        if (response.status === 404) {
          navigate('/404', { replace: true });
          return;
        }

        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }

        const data = await response.json();
        setUser(data);
      } catch (error) {
        setError(error.message);
      }
    };

    validateAndFetch();
  }, [params.userId, navigate]);

  if (error) {
    return <ErrorDisplay error={error} />;
  }

  return <UserContent />;
}
{% endraw %}
```

This comprehensive guide covers dynamic routing and parameters in React Router v6. The next sections will explore nested routes, layout patterns, and protected route implementations.