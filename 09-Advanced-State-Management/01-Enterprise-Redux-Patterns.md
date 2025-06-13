# Enterprise Redux Patterns and Architecture

> **Advanced Redux Patterns for Large-Scale Applications**

## 🎯 Overview

This comprehensive guide covers enterprise-level Redux patterns, advanced architectures, and scalable solutions for complex React applications. Learn how to structure, organize, and optimize Redux for production-ready applications.

## 📋 Table of Contents

1. [Advanced Redux Toolkit Patterns](#advanced-redux-toolkit-patterns)
2. [RTK Query for Data Fetching](#rtk-query-for-data-fetching)
3. [Advanced Middleware Patterns](#advanced-middleware-patterns)
4. [Normalized State Management](#normalized-state-management)
5. [Complex Selector Strategies](#complex-selector-strategies)
6. [Enterprise Architecture Patterns](#enterprise-architecture-patterns)
7. [State Persistence and Hydration](#state-persistence-and-hydration)
8. [Performance Optimization](#performance-optimization)

## 🏗 Advanced Redux Toolkit Patterns

### Feature-Based Store Organization

```jsx
// store/index.js - Main store configuration
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { 
  persistStore, 
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER
} from 'redux-persist';
import storage from 'redux-persist/lib/storage';

// Feature reducers
import { authSlice } from '../features/auth/authSlice';
import { userSlice } from '../features/user/userSlice';
import { productSlice } from '../features/product/productSlice';
import { cartSlice } from '../features/cart/cartSlice';
import { orderSlice } from '../features/order/orderSlice';
import { notificationSlice } from '../features/notification/notificationSlice';

// API slices
import { apiSlice } from '../api/apiSlice';
import { authApiSlice } from '../features/auth/authApiSlice';
import { productApiSlice } from '../features/product/productApiSlice';

// Root reducer with persistence
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth', 'cart', 'user'], // Only persist specific slices
  blacklist: ['api', 'notifications'] // Don't persist API cache and notifications
};

const rootReducer = {
  // Sync slices
  auth: authSlice.reducer,
  user: userSlice.reducer,
  products: productSlice.reducer,
  cart: cartSlice.reducer,
  orders: orderSlice.reducer,
  notifications: notificationSlice.reducer,
  
  // API slices
  api: apiSlice.reducer,
  authApi: authApiSlice.reducer,
  productApi: productApiSlice.reducer
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    })
    .concat(apiSlice.middleware)
    .concat(authApiSlice.middleware)
    .concat(productApiSlice.middleware),
  devTools: process.env.NODE_ENV !== 'production',
});

// Enable listener behavior for the store
setupListeners(store.dispatch);

export const persistor = persistStore(store);
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Advanced Slice Patterns

```jsx
// features/user/userSlice.js
import { createSlice, createAsyncThunk, createSelector } from '@reduxjs/toolkit';
import { createEntityAdapter } from '@reduxjs/toolkit';

// Entity adapter for normalized state
const usersAdapter = createEntityAdapter({
  selectId: (user) => user.id,
  sortComparer: (a, b) => a.lastName.localeCompare(b.lastName)
});

// Async thunks with enhanced error handling
export const fetchUserProfile = createAsyncThunk(
  'user/fetchProfile',
  async (userId, { getState, rejectWithValue, signal }) => {
    try {
      const { auth } = getState();
      const controller = new AbortController();
      
      // Link the thunk's signal to our controller
      signal.addEventListener('abort', () => controller.abort());
      
      const response = await fetch(`/api/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${auth.token}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });

      if (!response.ok) {
        const errorData = await response.json();
        return rejectWithValue({
          message: errorData.message,
          status: response.status,
          timestamp: Date.now()
        });
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'AbortError') {
        return rejectWithValue({ message: 'Request cancelled', cancelled: true });
      }
      return rejectWithValue({ 
        message: error.message, 
        network: true,
        timestamp: Date.now()
      });
    }
  }
);

export const updateUserProfile = createAsyncThunk(
  'user/updateProfile',
  async ({ userId, updates }, { getState, rejectWithValue, dispatch }) => {
    try {
      const { auth } = getState();
      
      // Optimistic update
      dispatch(userSlice.actions.updateUserOptimistic({ userId, updates }));
      
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${auth.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        // Revert optimistic update
        dispatch(userSlice.actions.revertOptimisticUpdate(userId));
        const errorData = await response.json();
        return rejectWithValue(errorData);
      }

      const updatedUser = await response.json();
      return updatedUser;
    } catch (error) {
      // Revert optimistic update
      dispatch(userSlice.actions.revertOptimisticUpdate(userId));
      return rejectWithValue({ message: error.message });
    }
  }
);

// Complex slice with entity adapter
const userSlice = createSlice({
  name: 'user',
  initialState: usersAdapter.getInitialState({
    currentUser: null,
    loading: false,
    error: null,
    lastUpdated: null,
    optimisticUpdates: {},
    preferences: {
      theme: 'light',
      language: 'en',
      notifications: true
    },
    cache: {
      profiles: {},
      lastFetch: {}
    }
  }),
  reducers: {
    // Synchronous actions
    updatePreferences: (state, action) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },
    
    updateUserOptimistic: (state, action) => {
      const { userId, updates } = action.payload;
      // Store original for potential revert
      if (!state.optimisticUpdates[userId]) {
        const originalUser = state.entities[userId];
        if (originalUser) {
          state.optimisticUpdates[userId] = { ...originalUser };
        }
      }
      // Apply optimistic update
      usersAdapter.updateOne(state, { id: userId, changes: updates });
    },
    
    revertOptimisticUpdate: (state, action) => {
      const userId = action.payload;
      const original = state.optimisticUpdates[userId];
      if (original) {
        usersAdapter.setOne(state, original);
        delete state.optimisticUpdates[userId];
      }
    },
    
    confirmOptimisticUpdate: (state, action) => {
      const userId = action.payload;
      delete state.optimisticUpdates[userId];
    },
    
    cacheUserProfile: (state, action) => {
      const { userId, profile } = action.payload;
      state.cache.profiles[userId] = profile;
      state.cache.lastFetch[userId] = Date.now();
    },
    
    clearUserCache: (state) => {
      state.cache.profiles = {};
      state.cache.lastFetch = {};
    },
    
    setCurrentUser: (state, action) => {
      state.currentUser = action.payload;
    },
    
    clearCurrentUser: (state) => {
      state.currentUser = null;
    }
  },
  
  extraReducers: (builder) => {
    builder
      // Fetch user profile
      .addCase(fetchUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        usersAdapter.setOne(state, action.payload);
        state.lastUpdated = Date.now();
        
        // Cache the profile
        userSlice.caseReducers.cacheUserProfile(state, {
          payload: {
            userId: action.payload.id,
            profile: action.payload
          }
        });
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || action.error.message;
      })
      
      // Update user profile
      .addCase(updateUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        usersAdapter.setOne(state, action.payload);
        state.lastUpdated = Date.now();
        
        // Confirm optimistic update
        userSlice.caseReducers.confirmOptimisticUpdate(state, {
          payload: action.payload.id
        });
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || action.error.message;
      });
  }
});

// Export actions
export const {
  updatePreferences,
  updateUserOptimistic,
  revertOptimisticUpdate,
  cacheUserProfile,
  clearUserCache,
  setCurrentUser,
  clearCurrentUser
} = userSlice.actions;

// Export entity selectors
export const {
  selectAll: selectAllUsers,
  selectById: selectUserById,
  selectIds: selectUserIds,
  selectEntities: selectUserEntities,
  selectTotal: selectTotalUsers
} = usersAdapter.getSelectors((state) => state.user);

// Custom selectors
export const selectCurrentUser = (state) => state.user.currentUser;
export const selectUserLoading = (state) => state.user.loading;
export const selectUserError = (state) => state.user.error;
export const selectUserPreferences = (state) => state.user.preferences;

// Memoized complex selectors
export const selectUsersByRole = createSelector(
  [selectAllUsers, (state, role) => role],
  (users, role) => users.filter(user => user.role === role)
);

export const selectUsersWithProjects = createSelector(
  [selectAllUsers, (state) => state.projects.entities],
  (users, projects) => {
    return users.map(user => ({
      ...user,
      projects: Object.values(projects).filter(project => 
        project.assignedUsers?.includes(user.id)
      )
    }));
  }
);

export default userSlice.reducer;
```

## 🔌 RTK Query for Data Fetching

### Advanced API Slice Configuration

```jsx
// api/apiSlice.js - Base API configuration
import { createApi, fetchBaseQuery, retry } from '@reduxjs/toolkit/query/react';
import { RootState } from '../store';

// Custom base query with retry and error handling
const baseQuery = fetchBaseQuery({
  baseUrl: '/api',
  prepareHeaders: (headers, { getState }) => {
    const state = getState() as RootState;
    const token = state.auth.token;
    
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    
    headers.set('Content-Type', 'application/json');
    return headers;
  },
});

// Base query with retry logic
const baseQueryWithRetry = retry(baseQuery, { maxRetries: 3 });

// Enhanced base query with auth refresh
const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await baseQueryWithRetry(args, api, extraOptions);
  
  if (result.error && result.error.status === 401) {
    // Try to refresh token
    const refreshResult = await baseQueryWithRetry(
      { url: '/auth/refresh', method: 'POST' },
      api,
      extraOptions
    );
    
    if (refreshResult.data) {
      // Store the new token
      api.dispatch(authSlice.actions.setToken(refreshResult.data.token));
      
      // Retry original query
      result = await baseQueryWithRetry(args, api, extraOptions);
    } else {
      // Refresh failed, logout user
      api.dispatch(authSlice.actions.logout());
      window.location.href = '/login';
    }
  }
  
  return result;
};

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: [
    'User', 
    'Product', 
    'Order', 
    'Category', 
    'Review', 
    'Cart',
    'Wishlist',
    'Analytics'
  ],
  endpoints: (builder) => ({
    // Health check endpoint
    getHealth: builder.query({
      query: () => '/health',
      keepUnusedDataFor: 60 // Cache for 1 minute
    })
  })
});

export const { useGetHealthQuery } = apiSlice;
```

### Feature-Specific API Slices

```jsx
// features/product/productApiSlice.js
import { apiSlice } from '../../api/apiSlice';

export const productApiSlice = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    // Get all products with filtering and pagination
    getProducts: builder.query({
      query: ({ 
        page = 1, 
        limit = 20, 
        category, 
        search, 
        sortBy = 'createdAt',
        sortOrder = 'desc',
        minPrice,
        maxPrice
      } = {}) => {
        const params = new URLSearchParams({
          page: page.toString(),
          limit: limit.toString(),
          sortBy,
          sortOrder
        });
        
        if (category) params.append('category', category);
        if (search) params.append('search', search);
        if (minPrice) params.append('minPrice', minPrice.toString());
        if (maxPrice) params.append('maxPrice', maxPrice.toString());
        
        return `/products?${params.toString()}`;
      },
      providesTags: (result, error, arg) => {
        return result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Product', id })),
              { type: 'Product', id: 'LIST' }
            ]
          : [{ type: 'Product', id: 'LIST' }];
      },
      // Transform response
      transformResponse: (response) => {
        return {
          data: response.products,
          pagination: {
            page: response.page,
            totalPages: response.totalPages,
            totalItems: response.totalItems,
            hasNext: response.hasNext,
            hasPrev: response.hasPrev
          }
        };
      },
      // Merge pages for infinite scroll
      serializeQueryArgs: ({ endpointName, queryArgs }) => {
        const { page, ...otherArgs } = queryArgs;
        return endpointName + JSON.stringify(otherArgs);
      },
      merge: (currentCache, newItems, { arg }) => {
        if (arg.page === 1) {
          return newItems;
        }
        return {
          ...newItems,
          data: [...currentCache.data, ...newItems.data]
        };
      },
      forceRefetch({ currentArg, previousArg }) {
        return currentArg?.page !== previousArg?.page;
      }
    }),
    
    // Get single product
    getProduct: builder.query({
      query: (id) => `/products/${id}`,
      providesTags: (result, error, id) => [{ type: 'Product', id }],
      transformResponse: (response) => {
        // Add computed fields
        return {
          ...response,
          averageRating: response.reviews?.length 
            ? response.reviews.reduce((sum, review) => sum + review.rating, 0) / response.reviews.length 
            : 0,
          isInStock: response.inventory > 0,
          discountPercentage: response.originalPrice 
            ? Math.round(((response.originalPrice - response.price) / response.originalPrice) * 100)
            : 0
        };
      }
    }),
    
    // Create product
    createProduct: builder.mutation({
      query: (productData) => ({
        url: '/products',
        method: 'POST',
        body: productData
      }),
      invalidatesTags: [{ type: 'Product', id: 'LIST' }],
      // Optimistic update
      async onQueryStarted(productData, { dispatch, queryFulfilled }) {
        const tempId = `temp-${Date.now()}`;
        const optimisticProduct = {
          id: tempId,
          ...productData,
          createdAt: new Date().toISOString()
        };
        
        // Add optimistic update to cache
        const patchResult = dispatch(
          productApiSlice.util.updateQueryData('getProducts', {}, (draft) => {
            draft.data.unshift(optimisticProduct);
          })
        );
        
        try {
          const { data: newProduct } = await queryFulfilled;
          
          // Replace optimistic product with real one
          dispatch(
            productApiSlice.util.updateQueryData('getProducts', {}, (draft) => {
              const index = draft.data.findIndex(p => p.id === tempId);
              if (index !== -1) {
                draft.data[index] = newProduct;
              }
            })
          );
        } catch {
          // Revert optimistic update
          patchResult.undo();
        }
      }
    }),
    
    // Update product
    updateProduct: builder.mutation({
      query: ({ id, ...updates }) => ({
        url: `/products/${id}`,
        method: 'PUT',
        body: updates
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Product', id },
        { type: 'Product', id: 'LIST' }
      ],
      // Optimistic update
      async onQueryStarted({ id, ...updates }, { dispatch, queryFulfilled }) {
        const patchResults = [];
        
        // Update individual product cache
        patchResults.push(
          dispatch(
            productApiSlice.util.updateQueryData('getProduct', id, (draft) => {
              Object.assign(draft, updates);
            })
          )
        );
        
        // Update products list cache
        patchResults.push(
          dispatch(
            productApiSlice.util.updateQueryData('getProducts', {}, (draft) => {
              const product = draft.data.find(p => p.id === id);
              if (product) {
                Object.assign(product, updates);
              }
            })
          )
        );
        
        try {
          await queryFulfilled;
        } catch {
          // Revert all optimistic updates
          patchResults.forEach(patch => patch.undo());
        }
      }
    }),
    
    // Delete product
    deleteProduct: builder.mutation({
      query: (id) => ({
        url: `/products/${id}`,
        method: 'DELETE'
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Product', id },
        { type: 'Product', id: 'LIST' }
      ]
    }),
    
    // Bulk operations
    bulkUpdateProducts: builder.mutation({
      query: (updates) => ({
        url: '/products/bulk',
        method: 'PUT',
        body: { updates }
      }),
      invalidatesTags: [{ type: 'Product', id: 'LIST' }]
    }),
    
    // Search products with autocomplete
    searchProducts: builder.query({
      query: (searchTerm) => `/products/search?q=${encodeURIComponent(searchTerm)}`,
      transformResponse: (response) => response.suggestions || [],
      keepUnusedDataFor: 300 // Cache autocomplete for 5 minutes
    }),
    
    // Get product recommendations
    getProductRecommendations: builder.query({
      query: ({ productId, userId, limit = 10 }) => {
        const params = new URLSearchParams({ limit: limit.toString() });
        if (userId) params.append('userId', userId);
        return `/products/${productId}/recommendations?${params.toString()}`;
      },
      providesTags: (result, error, { productId }) => [
        { type: 'Product', id: `recommendations-${productId}` }
      ]
    })
  })
});

// Export hooks
export const {
  useGetProductsQuery,
  useGetProductQuery,
  useCreateProductMutation,
  useUpdateProductMutation,
  useDeleteProductMutation,
  useBulkUpdateProductsMutation,
  useSearchProductsQuery,
  useLazySearchProductsQuery,
  useGetProductRecommendationsQuery
} = productApiSlice;

// Export endpoint matchers for middleware
export const {
  getProducts,
  getProduct,
  createProduct,
  updateProduct,
  deleteProduct
} = productApiSlice.endpoints;
```

## 🔧 Advanced Middleware Patterns

### Custom Middleware for Cross-Cutting Concerns

```jsx
// middleware/index.js
import { createListenerMiddleware, isAnyOf } from '@reduxjs/toolkit';
import { authSlice } from '../features/auth/authSlice';
import { notificationSlice } from '../features/notification/notificationSlice';
import { analyticsSlice } from '../features/analytics/analyticsSlice';

// Listener middleware for side effects
export const listenerMiddleware = createListenerMiddleware();

// Authentication event listeners
listenerMiddleware.startListening({
  matcher: isAnyOf(authSlice.actions.loginSuccess, authSlice.actions.logout),
  effect: async (action, listenerApi) => {
    const { type } = action;
    
    if (type === 'auth/loginSuccess') {
      // Initialize user data
      listenerApi.dispatch(userSlice.actions.initializeUser());
      
      // Track login event
      listenerApi.dispatch(analyticsSlice.actions.trackEvent({
        event: 'user_login',
        timestamp: Date.now(),
        userId: action.payload.user.id
      }));
      
      // Show welcome notification
      listenerApi.dispatch(notificationSlice.actions.addNotification({
        id: Date.now(),
        type: 'success',
        message: `Welcome back, ${action.payload.user.name}!`,
        timeout: 5000
      }));
    }
    
    if (type === 'auth/logout') {
      // Clear sensitive data
      listenerApi.dispatch(userSlice.actions.clearUserData());
      listenerApi.dispatch(cartSlice.actions.clearCart());
      
      // Track logout event
      listenerApi.dispatch(analyticsSlice.actions.trackEvent({
        event: 'user_logout',
        timestamp: Date.now()
      }));
    }
  }
});

// Error handling middleware
export const errorHandlingMiddleware = (store) => (next) => (action) => {
  try {
    return next(action);
  } catch (error) {
    console.error('Redux error:', error);
    
    // Dispatch error notification
    store.dispatch(notificationSlice.actions.addNotification({
      id: Date.now(),
      type: 'error',
      message: 'An unexpected error occurred',
      timeout: 10000
    }));
    
    // Track error
    store.dispatch(analyticsSlice.actions.trackEvent({
      event: 'redux_error',
      error: error.message,
      action: action.type,
      timestamp: Date.now()
    }));
    
    throw error;
  }
};

// Performance monitoring middleware
export const performanceMiddleware = (store) => (next) => (action) => {
  const startTime = performance.now();
  const result = next(action);
  const endTime = performance.now();
  
  const duration = endTime - startTime;
  
  // Log slow actions
  if (duration > 16) { // Longer than one frame (60fps)
    console.warn(`Slow action detected: ${action.type} took ${duration.toFixed(2)}ms`);
    
    store.dispatch(analyticsSlice.actions.trackPerformance({
      action: action.type,
      duration,
      timestamp: Date.now()
    }));
  }
  
  return result;
};

// API caching middleware
export const apiCachingMiddleware = (store) => (next) => (action) => {
  const result = next(action);
  
  // Auto-invalidate cache for related data
  if (action.type.endsWith('/fulfilled')) {
    const state = store.getState();
    
    // Example: Invalidate user cache when profile is updated
    if (action.type === 'api/updateUser/fulfilled') {
      setTimeout(() => {
        store.dispatch(apiSlice.util.invalidateTags(['User']));
      }, 1000);
    }
  }
  
  return result;
};

// Optimistic update middleware
export const optimisticUpdateMiddleware = (store) => (next) => (action) => {
  const result = next(action);
  
  // Handle optimistic updates for mutations
  if (action.type.includes('mutation/pending')) {
    const state = store.getState();
    
    // Apply optimistic update based on action type
    // This is handled in individual slice extra reducers
  }
  
  return result;
};
```

### State Synchronization Middleware

```jsx
// middleware/syncMiddleware.js
import { createListenerMiddleware } from '@reduxjs/toolkit';

export const syncMiddleware = createListenerMiddleware();

// Sync cart with server
syncMiddleware.startListening({
  actionCreator: cartSlice.actions.addItem,
  effect: async (action, listenerApi) => {
    const { item } = action.payload;
    const state = listenerApi.getState();
    
    if (state.auth.isAuthenticated) {
      try {
        await fetch('/api/cart/sync', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${state.auth.token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            action: 'add',
            item
          })
        });
      } catch (error) {
        console.error('Failed to sync cart:', error);
        
        // Show offline notification
        listenerApi.dispatch(notificationSlice.actions.addNotification({
          id: Date.now(),
          type: 'warning',
          message: 'Changes saved locally. Will sync when online.',
          timeout: 5000
        }));
      }
    }
  }
});

// Real-time updates via WebSocket
let websocket = null;

syncMiddleware.startListening({
  actionCreator: authSlice.actions.loginSuccess,
  effect: async (action, listenerApi) => {
    const { token, user } = action.payload;
    
    // Establish WebSocket connection
    websocket = new WebSocket(`ws://localhost:8080/ws?token=${token}`);
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'CART_UPDATED':
          listenerApi.dispatch(cartSlice.actions.updateFromServer(data.cart));
          break;
          
        case 'ORDER_STATUS_CHANGED':
          listenerApi.dispatch(orderSlice.actions.updateOrderStatus({
            orderId: data.orderId,
            status: data.status
          }));
          break;
          
        case 'NOTIFICATION':
          listenerApi.dispatch(notificationSlice.actions.addNotification(data.notification));
          break;
          
        default:
          console.log('Unknown WebSocket message:', data);
      }
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
});

syncMiddleware.startListening({
  actionCreator: authSlice.actions.logout,
  effect: async (action, listenerApi) => {
    // Close WebSocket connection
    if (websocket) {
      websocket.close();
      websocket = null;
    }
  }
});
```

## 📊 Normalized State Management

### Entity Relationship Management

```jsx
// utils/entityHelpers.js
import { createEntityAdapter } from '@reduxjs/toolkit';

// Generic entity adapter factory
export const createNormalizedSlice = ({
  name,
  selectId = (entity) => entity.id,
  sortComparer
}) => {
  const adapter = createEntityAdapter({
    selectId,
    sortComparer
  });

  return {
    adapter,
    initialState: adapter.getInitialState({
      loading: false,
      error: null,
      lastUpdated: null
    })
  };
};

// Relationship management utilities
export const relationshipUtils = {
  // Add relationship between entities
  addRelationship: (state, { parentId, childId, relationshipType }) => {
    if (!state.relationships) {
      state.relationships = {};
    }
    if (!state.relationships[relationshipType]) {
      state.relationships[relationshipType] = {};
    }
    if (!state.relationships[relationshipType][parentId]) {
      state.relationships[relationshipType][parentId] = [];
    }
    
    if (!state.relationships[relationshipType][parentId].includes(childId)) {
      state.relationships[relationshipType][parentId].push(childId);
    }
  },
  
  // Remove relationship
  removeRelationship: (state, { parentId, childId, relationshipType }) => {
    if (state.relationships?.[relationshipType]?.[parentId]) {
      state.relationships[relationshipType][parentId] = 
        state.relationships[relationshipType][parentId].filter(id => id !== childId);
    }
  },
  
  // Get related entities
  getRelatedEntities: (state, { parentId, relationshipType }) => {
    return state.relationships?.[relationshipType]?.[parentId] || [];
  }
};

// Complex normalized slice example
// features/blog/blogSlice.js
const postsAdapter = createEntityAdapter({
  selectId: (post) => post.id,
  sortComparer: (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
});

const authorsAdapter = createEntityAdapter();
const categoriesAdapter = createEntityAdapter();
const tagsAdapter = createEntityAdapter();
const commentsAdapter = createEntityAdapter();

const blogSlice = createSlice({
  name: 'blog',
  initialState: {
    posts: postsAdapter.getInitialState(),
    authors: authorsAdapter.getInitialState(),
    categories: categoriesAdapter.getInitialState(),
    tags: tagsAdapter.getInitialState(),
    comments: commentsAdapter.getInitialState(),
    relationships: {
      postAuthors: {}, // postId -> authorId
      postCategories: {}, // postId -> [categoryIds]
      postTags: {}, // postId -> [tagIds]
      postComments: {}, // postId -> [commentIds]
      commentAuthors: {} // commentId -> authorId
    },
    loading: false,
    error: null
  },
  reducers: {
    // Denormalize blog post data
    setBlogData: (state, action) => {
      const { posts, authors, categories, tags, comments } = action.payload;
      
      // Set entities
      postsAdapter.setAll(state.posts, posts);
      authorsAdapter.setAll(state.authors, authors);
      categoriesAdapter.setAll(state.categories, categories);
      tagsAdapter.setAll(state.tags, tags);
      commentsAdapter.setAll(state.comments, comments);
      
      // Build relationships
      posts.forEach(post => {
        // Post author
        if (post.authorId) {
          state.relationships.postAuthors[post.id] = post.authorId;
        }
        
        // Post categories
        if (post.categoryIds?.length) {
          state.relationships.postCategories[post.id] = post.categoryIds;
        }
        
        // Post tags
        if (post.tagIds?.length) {
          state.relationships.postTags[post.id] = post.tagIds;
        }
        
        // Post comments
        const postComments = comments.filter(comment => comment.postId === post.id);
        if (postComments.length) {
          state.relationships.postComments[post.id] = postComments.map(c => c.id);
          
          // Comment authors
          postComments.forEach(comment => {
            if (comment.authorId) {
              state.relationships.commentAuthors[comment.id] = comment.authorId;
            }
          });
        }
      });
    },
    
    addPost: (state, action) => {
      const post = action.payload;
      postsAdapter.addOne(state.posts, post);
      
      // Update relationships
      if (post.authorId) {
        state.relationships.postAuthors[post.id] = post.authorId;
      }
    },
    
    updatePost: (state, action) => {
      const { id, changes } = action.payload;
      postsAdapter.updateOne(state.posts, { id, changes });
      
      // Update relationships if needed
      if (changes.categoryIds) {
        state.relationships.postCategories[id] = changes.categoryIds;
      }
      if (changes.tagIds) {
        state.relationships.postTags[id] = changes.tagIds;
      }
    },
    
    addComment: (state, action) => {
      const comment = action.payload;
      commentsAdapter.addOne(state.comments, comment);
      
      // Update relationships
      if (!state.relationships.postComments[comment.postId]) {
        state.relationships.postComments[comment.postId] = [];
      }
      state.relationships.postComments[comment.postId].push(comment.id);
      
      if (comment.authorId) {
        state.relationships.commentAuthors[comment.id] = comment.authorId;
      }
    }
  }
});

// Denormalized selectors
export const selectPostWithDetails = createSelector(
  [
    (state) => state.blog.posts.entities,
    (state) => state.blog.authors.entities,
    (state) => state.blog.categories.entities,
    (state) => state.blog.tags.entities,
    (state) => state.blog.comments.entities,
    (state) => state.blog.relationships,
    (state, postId) => postId
  ],
  (posts, authors, categories, tags, comments, relationships, postId) => {
    const post = posts[postId];
    if (!post) return null;
    
    return {
      ...post,
      author: authors[relationships.postAuthors[postId]],
      categories: relationships.postCategories[postId]?.map(id => categories[id]) || [],
      tags: relationships.postTags[postId]?.map(id => tags[id]) || [],
      comments: relationships.postComments[postId]?.map(id => ({
        ...comments[id],
        author: authors[relationships.commentAuthors[id]]
      })) || []
    };
  }
);
```

## 🔍 Complex Selector Strategies

### Performance-Optimized Selectors

```jsx
// selectors/index.js
import { createSelector, createDraftSafeSelector } from '@reduxjs/toolkit';
import { memoize } from 'lodash';

// Memoized selector factory
const createMemoizedSelector = (dependencies, resultFunc, options = {}) => {
  const memoizedResultFunc = memoize(resultFunc, options.keySelector);
  return createSelector(dependencies, memoizedResultFunc);
};

// Complex filtering and sorting
export const selectFilteredProducts = createMemoizedSelector(
  [
    (state) => state.products.entities,
    (state, filters) => filters
  ],
  (products, filters) => {
    let filtered = Object.values(products);
    
    // Apply filters
    if (filters.category) {
      filtered = filtered.filter(product => product.category === filters.category);
    }
    
    if (filters.priceRange) {
      const [min, max] = filters.priceRange;
      filtered = filtered.filter(product => 
        product.price >= min && product.price <= max
      );
    }
    
    if (filters.inStock) {
      filtered = filtered.filter(product => product.inventory > 0);
    }
    
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm)
      );
    }
    
    // Apply sorting
    if (filters.sortBy) {
      filtered.sort((a, b) => {
        const aVal = a[filters.sortBy];
        const bVal = b[filters.sortBy];
        
        if (filters.sortOrder === 'desc') {
          return bVal > aVal ? 1 : -1;
        }
        return aVal > bVal ? 1 : -1;
      });
    }
    
    return filtered;
  },
  {
    keySelector: (products, filters) => JSON.stringify(filters)
  }
);

// Aggregation selectors
export const selectProductAnalytics = createSelector(
  [selectAllProducts],
  (products) => {
    const analytics = {
      totalProducts: products.length,
      totalValue: 0,
      averagePrice: 0,
      categoryBreakdown: {},
      priceRanges: {
        under50: 0,
        between50And100: 0,
        between100And200: 0,
        over200: 0
      },
      stockStatus: {
        inStock: 0,
        lowStock: 0,
        outOfStock: 0
      }
    };
    
    products.forEach(product => {
      // Total value
      analytics.totalValue += product.price * product.inventory;
      
      // Category breakdown
      if (!analytics.categoryBreakdown[product.category]) {
        analytics.categoryBreakdown[product.category] = 0;
      }
      analytics.categoryBreakdown[product.category]++;
      
      // Price ranges
      if (product.price < 50) {
        analytics.priceRanges.under50++;
      } else if (product.price < 100) {
        analytics.priceRanges.between50And100++;
      } else if (product.price < 200) {
        analytics.priceRanges.between100And200++;
      } else {
        analytics.priceRanges.over200++;
      }
      
      // Stock status
      if (product.inventory === 0) {
        analytics.stockStatus.outOfStock++;
      } else if (product.inventory < 10) {
        analytics.stockStatus.lowStock++;
      } else {
        analytics.stockStatus.inStock++;
      }
    });
    
    analytics.averagePrice = products.length > 0 
      ? analytics.totalValue / products.length 
      : 0;
    
    return analytics;
  }
);

// Cross-slice selectors
export const selectUserDashboardData = createSelector(
  [
    selectCurrentUser,
    selectUserOrders,
    selectUserWishlist,
    selectUserReviews,
    (state) => state.cart.items
  ],
  (user, orders, wishlist, reviews, cartItems) => {
    if (!user) return null;
    
    const recentOrders = orders
      .filter(order => new Date(order.createdAt) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000))
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, 5);
    
    const totalSpent = orders.reduce((sum, order) => sum + order.total, 0);
    
    return {
      user,
      stats: {
        totalOrders: orders.length,
        totalSpent,
        wishlistItems: wishlist.length,
        reviewsWritten: reviews.length,
        cartItems: cartItems.length
      },
      recentOrders,
      recommendations: [] // Could be populated from another selector
    };
  }
);

// Parameterized selectors with caching
const makeSelectUserById = () => createSelector(
  [(state) => state.users.entities, (state, userId) => userId],
  (users, userId) => users[userId]
);

// Selector factory for different user data views
export const createUserSelector = (transformFn) => createSelector(
  [makeSelectUserById()],
  (user) => user ? transformFn(user) : null
);

export const selectUserDisplayName = createUserSelector(
  (user) => `${user.firstName} ${user.lastName}`
);

export const selectUserPermissions = createUserSelector(
  (user) => user.roles?.flatMap(role => role.permissions) || []
);
```

## 🏢 Enterprise Architecture Patterns

### Micro-Frontend State Management

```jsx
// Shared state management for micro-frontends
// shared/stateManager.js
class MicroFrontendStateManager {
  constructor() {
    this.stores = new Map();
    this.subscribers = new Map();
    this.eventBus = new EventTarget();
  }
  
  // Register a micro-frontend store
  registerStore(name, store) {
    this.stores.set(name, store);
    this.subscribers.set(name, new Set());
    
    // Subscribe to store changes
    store.subscribe(() => {
      this.notifySubscribers(name, store.getState());
    });
    
    this.eventBus.dispatchEvent(new CustomEvent('storeRegistered', {
      detail: { name, store }
    }));
  }
  
  // Unregister store (for cleanup)
  unregisterStore(name) {
    this.stores.delete(name);
    this.subscribers.delete(name);
    
    this.eventBus.dispatchEvent(new CustomEvent('storeUnregistered', {
      detail: { name }
    }));
  }
  
  // Get state from any micro-frontend
  getState(storeName) {
    const store = this.stores.get(storeName);
    return store ? store.getState() : null;
  }
  
  // Dispatch action to specific store
  dispatch(storeName, action) {
    const store = this.stores.get(storeName);
    if (store) {
      return store.dispatch(action);
    }
    console.warn(`Store ${storeName} not found`);
  }
  
  // Subscribe to state changes
  subscribe(storeName, callback) {
    if (!this.subscribers.has(storeName)) {
      this.subscribers.set(storeName, new Set());
    }
    
    this.subscribers.get(storeName).add(callback);
    
    // Return unsubscribe function
    return () => {
      this.subscribers.get(storeName)?.delete(callback);
    };
  }
  
  // Cross micro-frontend communication
  broadcast(event, data) {
    this.eventBus.dispatchEvent(new CustomEvent(event, { detail: data }));
  }
  
  // Listen to broadcast events
  on(event, callback) {
    this.eventBus.addEventListener(event, callback);
    return () => this.eventBus.removeEventListener(event, callback);
  }
  
  private notifySubscribers(storeName, state) {
    const subscribers = this.subscribers.get(storeName);
    if (subscribers) {
      subscribers.forEach(callback => {
        try {
          callback(state);
        } catch (error) {
          console.error('Subscriber error:', error);
        }
      });
    }
  }
}

// Global instance
export const microFrontendStateManager = new MicroFrontendStateManager();

// React hook for micro-frontend state
export const useMicroFrontendState = (storeName) => {
  const [state, setState] = useState(
    microFrontendStateManager.getState(storeName)
  );
  
  useEffect(() => {
    const unsubscribe = microFrontendStateManager.subscribe(
      storeName, 
      setState
    );
    
    return unsubscribe;
  }, [storeName]);
  
  const dispatch = useCallback((action) => {
    return microFrontendStateManager.dispatch(storeName, action);
  }, [storeName]);
  
  return [state, dispatch];
};
```

### Domain-Driven Design with Redux

```jsx
// Domain-driven architecture
// domains/ecommerce/store.js
export const createEcommerceStore = () => {
  return configureStore({
    reducer: {
      // Product domain
      products: combineReducers({
        catalog: productCatalogSlice.reducer,
        inventory: productInventorySlice.reducer,
        pricing: productPricingSlice.reducer,
        reviews: productReviewsSlice.reducer
      }),
      
      // Order domain
      orders: combineReducers({
        management: orderManagementSlice.reducer,
        fulfillment: orderFulfillmentSlice.reducer,
        payments: orderPaymentsSlice.reducer,
        shipping: orderShippingSlice.reducer
      }),
      
      // User domain
      users: combineReducers({
        authentication: authSlice.reducer,
        profiles: userProfileSlice.reducer,
        preferences: userPreferencesSlice.reducer,
        analytics: userAnalyticsSlice.reducer
      }),
      
      // Shared/Infrastructure
      notifications: notificationSlice.reducer,
      cache: cacheSlice.reducer,
      ui: uiSlice.reducer
    },
    
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware()
        .concat(listenerMiddleware.middleware)
        .concat(apiSlice.middleware),
        
    enhancers: (getDefaultEnhancers) =>
      getDefaultEnhancers().concat(
        // Domain-specific enhancers
        productDomainEnhancer,
        orderDomainEnhancer,
        userDomainEnhancer
      )
  });
};

// Domain event handling
// domains/shared/eventBus.js
export class DomainEventBus {
  constructor() {
    this.handlers = new Map();
  }
  
  // Register domain event handler
  registerHandler(eventType, handler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType).add(handler);
  }
  
  // Emit domain event
  emit(eventType, payload) {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(payload);
        } catch (error) {
          console.error(`Error in domain event handler for ${eventType}:`, error);
        }
      });
    }
  }
  
  // Remove handler
  removeHandler(eventType, handler) {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }
}

export const domainEventBus = new DomainEventBus();

// Domain event middleware
export const domainEventMiddleware = (store) => (next) => (action) => {
  const result = next(action);
  
  // Emit domain events based on actions
  switch (action.type) {
    case 'orders/createOrder/fulfilled':
      domainEventBus.emit('ORDER_CREATED', {
        order: action.payload,
        timestamp: Date.now()
      });
      break;
      
    case 'products/updateInventory/fulfilled':
      domainEventBus.emit('INVENTORY_UPDATED', {
        productId: action.meta.arg.productId,
        newQuantity: action.payload.quantity,
        timestamp: Date.now()
      });
      break;
      
    case 'users/updateProfile/fulfilled':
      domainEventBus.emit('USER_PROFILE_UPDATED', {
        userId: action.payload.id,
        changes: action.meta.arg.updates,
        timestamp: Date.now()
      });
      break;
  }
  
  return result;
};
```

This comprehensive guide covers enterprise-level Redux patterns that enable scalable, maintainable state management for complex React applications. The patterns shown here provide the foundation for building robust production applications with advanced state management requirements.