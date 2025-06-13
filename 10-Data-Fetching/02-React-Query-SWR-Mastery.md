# React Query & SWR Mastery

## Table of Contents
1. [Introduction](#introduction)
2. [React Query Advanced Patterns](#react-query-advanced-patterns)
3. [SWR Deep Dive](#swr-deep-dive)
4. [Comparison and Selection](#comparison-and-selection)
5. [Advanced Caching Strategies](#advanced-caching-strategies)
6. [Real-time Data Synchronization](#real-time-data-synchronization)
7. [Offline Support](#offline-support)
8. [Performance Optimization](#performance-optimization)
9. [Testing Strategies](#testing-strategies)
10. [Best Practices](#best-practices)

## Introduction

Modern React applications require sophisticated data fetching solutions that handle caching, synchronization, error states, and real-time updates. React Query (TanStack Query) and SWR are the leading libraries that provide these capabilities out of the box.

### Why Use Data Fetching Libraries?

```javascript
// Without data fetching library - Complex manual state management
function UserProfile({ userId }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastFetch, setLastFetch] = useState(null)

  useEffect(() => {
    let cancelled = false
    
    const fetchUser = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const response = await fetch(`/api/users/${userId}`)
        if (!response.ok) throw new Error('Failed to fetch')
        const userData = await response.json()
        
        if (!cancelled) {
          setUser(userData)
          setLastFetch(Date.now())
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchUser()
    
    return () => {
      cancelled = true
    }
  }, [userId])

  // Manual refetch logic, cache invalidation, etc.
  
  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!user) return <div>No user found</div>
  
  return <div>{user.name}</div>
}

// With React Query - Simplified and powerful
function UserProfile({ userId }) {
  const { data: user, isLoading, error, refetch } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!userId
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!user) return <div>No user found</div>
  
  return <div>{user.name}</div>
}
```

## React Query Advanced Patterns

### Query Configuration and Optimization

```javascript
import { useQuery, useQueries, useInfiniteQuery, QueryClient } from '@tanstack/react-query'

// Advanced query configuration
function useUserQuery(userId, options = {}) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      return response.json()
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 30, // 30 minutes
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error.message.includes('HTTP 4')) return false
      return failureCount < 3
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    enabled: !!userId,
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    refetchOnReconnect: 'always',
    select: (data) => ({
      ...data,
      displayName: `${data.firstName} ${data.lastName}`,
      isActive: data.lastLoginAt > Date.now() - 30 * 24 * 60 * 60 * 1000
    }),
    ...options
  })
}

// Parallel queries with useQueries
function useMultipleUsers(userIds) {
  return useQueries({
    queries: userIds.map(id => ({
      queryKey: ['user', id],
      queryFn: () => fetchUser(id),
      staleTime: 1000 * 60 * 5,
      enabled: !!id
    }))
  })
}

// Dependent queries
function useUserWithPosts(userId) {
  const { data: user, isLoading: userLoading } = useUserQuery(userId)
  
  const { data: posts, isLoading: postsLoading } = useQuery({
    queryKey: ['posts', 'user', userId],
    queryFn: () => fetchUserPosts(userId),
    enabled: !!user?.id, // Only fetch posts if user exists
    select: (posts) => posts.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  })

  return {
    user,
    posts,
    isLoading: userLoading || postsLoading
  }
}

// Infinite queries for pagination
function useInfinitePostsList(filters = {}) {
  return useInfiniteQuery({
    queryKey: ['posts', 'infinite', filters],
    queryFn: async ({ pageParam = 0 }) => {
      const searchParams = new URLSearchParams({
        page: pageParam.toString(),
        limit: '20',
        ...filters
      })
      
      const response = await fetch(`/api/posts?${searchParams}`)
      return response.json()
    },
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.posts.length < 20) return undefined
      return pages.length
    },
    getPreviousPageParam: (firstPage, pages) => {
      if (pages.length <= 1) return undefined
      return pages.length - 2
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    select: (data) => ({
      pages: data.pages,
      posts: data.pages.flatMap(page => page.posts),
      totalCount: data.pages[0]?.totalCount || 0
    })
  })
}

// Usage in component
function InfinitePostsList({ filters }) {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error
  } = useInfinitePostsList(filters)

  const { posts = [] } = data || {}

  if (isLoading) return <PostsSkeleton />
  if (error) return <ErrorMessage error={error} />

  return (
    <div>
      <div className="posts-grid">
        {posts.map(post => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
      
      {hasNextPage && (
        <button
          onClick={() => fetchNextPage()}
          disabled={isFetchingNextPage}
          className="load-more-btn"
        >
          {isFetchingNextPage ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  )
}
```

### Mutations and Optimistic Updates

```javascript
import { useMutation, useQueryClient } from '@tanstack/react-query'

// Basic mutation
function useCreatePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (newPost) => {
      const response = await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPost)
      })
      
      if (!response.ok) {
        throw new Error('Failed to create post')
      }
      
      return response.json()
    },
    onSuccess: (data) => {
      // Invalidate and refetch
      queryClient.invalidateQueries(['posts'])
      
      // Or update cache directly
      queryClient.setQueryData(['post', data.id], data)
      
      // Add to posts list cache
      queryClient.setQueryData(['posts'], (oldData) => {
        if (!oldData) return [data]
        return [data, ...oldData]
      })
    },
    onError: (error) => {
      toast.error(`Failed to create post: ${error.message}`)
    }
  })
}

// Optimistic mutations
function useOptimisticUpdatePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, updates }) => {
      const response = await fetch(`/api/posts/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      
      if (!response.ok) {
        throw new Error('Failed to update post')
      }
      
      return response.json()
    },
    onMutate: async ({ id, updates }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries(['post', id])

      // Snapshot previous value
      const previousPost = queryClient.getQueryData(['post', id])

      // Optimistically update
      queryClient.setQueryData(['post', id], (old) => ({
        ...old,
        ...updates,
        updatedAt: new Date().toISOString()
      }))

      // Update in lists too
      queryClient.setQueryData(['posts'], (oldPosts) =>
        oldPosts?.map(post =>
          post.id === id ? { ...post, ...updates } : post
        )
      )

      return { previousPost }
    },
    onError: (error, { id }, context) => {
      // Rollback on error
      if (context?.previousPost) {
        queryClient.setQueryData(['post', id], context.previousPost)
      }
      toast.error(`Failed to update post: ${error.message}`)
    },
    onSettled: (data, error, { id }) => {
      // Always refetch after error or success
      queryClient.invalidateQueries(['post', id])
    }
  })
}

// Complex mutation with multiple cache updates
function useDeletePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (postId) => {
      const response = await fetch(`/api/posts/${postId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete post')
      }
      
      return postId
    },
    onMutate: async (postId) => {
      // Cancel queries
      await queryClient.cancelQueries(['post', postId])
      await queryClient.cancelQueries(['posts'])

      // Get previous data
      const previousPost = queryClient.getQueryData(['post', postId])
      const previousPosts = queryClient.getQueryData(['posts'])

      // Optimistically remove from cache
      queryClient.removeQueries(['post', postId])
      queryClient.setQueryData(['posts'], (oldPosts) =>
        oldPosts?.filter(post => post.id !== postId)
      )

      return { previousPost, previousPosts }
    },
    onError: (error, postId, context) => {
      // Restore on error
      if (context?.previousPost) {
        queryClient.setQueryData(['post', postId], context.previousPost)
      }
      if (context?.previousPosts) {
        queryClient.setQueryData(['posts'], context.previousPosts)
      }
      toast.error(`Failed to delete post: ${error.message}`)
    },
    onSuccess: () => {
      toast.success('Post deleted successfully')
    },
    onSettled: () => {
      queryClient.invalidateQueries(['posts'])
    }
  })
}
```

### Advanced Query Management

```javascript
// Query prefetching
function usePrefetchQueries() {
  const queryClient = useQueryClient()

  const prefetchUser = useCallback(async (userId) => {
    await queryClient.prefetchQuery({
      queryKey: ['user', userId],
      queryFn: () => fetchUser(userId),
      staleTime: 1000 * 60 * 5
    })
  }, [queryClient])

  const prefetchUserPosts = useCallback(async (userId) => {
    await queryClient.prefetchQuery({
      queryKey: ['posts', 'user', userId],
      queryFn: () => fetchUserPosts(userId),
      staleTime: 1000 * 60 * 2
    })
  }, [queryClient])

  return { prefetchUser, prefetchUserPosts }
}

// Query background refetching
function useBackgroundRefetch() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const interval = setInterval(() => {
      // Refetch all active queries in background
      queryClient.refetchQueries({
        type: 'active',
        stale: true
      })
    }, 1000 * 60 * 5) // Every 5 minutes

    return () => clearInterval(interval)
  }, [queryClient])

  // Refetch on window focus
  useEffect(() => {
    const handleFocus = () => {
      queryClient.refetchQueries({
        type: 'active',
        stale: true
      })
    }

    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [queryClient])
}

// Query synchronization across tabs
function useQuerySync() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const channel = new BroadcastChannel('react-query-sync')

    channel.addEventListener('message', (event) => {
      const { type, queryKey, data } = event.data

      switch (type) {
        case 'invalidate':
          queryClient.invalidateQueries(queryKey)
          break
        case 'update':
          queryClient.setQueryData(queryKey, data)
          break
        case 'remove':
          queryClient.removeQueries(queryKey)
          break
      }
    })

    return () => channel.close()
  }, [queryClient])

  const broadcastInvalidation = useCallback((queryKey) => {
    const channel = new BroadcastChannel('react-query-sync')
    channel.postMessage({ type: 'invalidate', queryKey })
    channel.close()
  }, [])

  return { broadcastInvalidation }
}
```

## SWR Deep Dive

### Advanced SWR Configuration

```javascript
import useSWR, { useSWRConfig, SWRConfig } from 'swr'
import useSWRMutation from 'swr/mutation'
import useSWRInfinite from 'swr/infinite'

// Global SWR configuration
const swrConfig = {
  fetcher: async (url) => {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      const error = new Error('An error occurred while fetching the data.')
      error.info = await response.json()
      error.status = response.status
      throw error
    }
    
    return response.json()
  },
  onError: (error, key) => {
    console.error('SWR Error:', error, 'for key:', key)
    if (error.status === 401) {
      // Handle authentication error
      redirectToLogin()
    }
  },
  onLoadingSlow: (key, config) => {
    console.warn('SWR loading slow for key:', key)
  },
  loadingTimeout: 3000,
  errorRetryCount: 3,
  errorRetryInterval: 1000,
  focusThrottleInterval: 5000,
  dedupingInterval: 2000,
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  refreshInterval: 0
}

// App wrapper with SWR config
function App() {
  return (
    <SWRConfig value={swrConfig}>
      <Router>
        <Routes>
          {/* Your routes */}
        </Routes>
      </Router>
    </SWRConfig>
  )
}

// Advanced SWR hooks
function useUser(userId, options = {}) {
  const { data, error, isLoading, mutate } = useSWR(
    userId ? `/api/users/${userId}` : null,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
      ...options
    }
  )

  return {
    user: data,
    isLoading,
    isError: error,
    mutate
  }
}

// SWR with conditional fetching
function useUserWithProfile(userId, includeProfile = false) {
  const userKey = userId ? `/api/users/${userId}` : null
  const profileKey = userId && includeProfile ? `/api/users/${userId}/profile` : null

  const { data: user, error: userError } = useSWR(userKey)
  const { data: profile, error: profileError } = useSWR(profileKey)

  return {
    user,
    profile,
    isLoading: (!user && !userError) || (includeProfile && !profile && !profileError),
    error: userError || profileError
  }
}

// SWR infinite loading
function useInfinitePosts(limit = 20) {
  const { data, error, size, setSize, isValidating } = useSWRInfinite(
    (index, previousPageData) => {
      // Reached the end
      if (previousPageData && !previousPageData.posts.length) return null
      
      // First page
      if (index === 0) return `/api/posts?limit=${limit}`
      
      // Add offset
      return `/api/posts?limit=${limit}&offset=${index * limit}`
    },
    {
      revalidateFirstPage: false,
      revalidateAll: false
    }
  )

  const posts = data ? data.flatMap(page => page.posts) : []
  const isLoadingInitial = !data && !error
  const isLoadingMore = isValidating && data && typeof data[size - 1] !== 'undefined'
  const isEmpty = data?.[0]?.posts?.length === 0
  const isReachingEnd = isEmpty || (data && data[data.length - 1]?.posts?.length < limit)

  return {
    posts,
    error,
    isLoadingInitial,
    isLoadingMore,
    isEmpty,
    isReachingEnd,
    loadMore: () => setSize(size + 1)
  }
}
```

### SWR Mutations and Cache Management

```javascript
// SWR mutations
function useCreatePost() {
  const { mutate } = useSWRConfig()

  return useSWRMutation('/api/posts', async (url, { arg: newPost }) => {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newPost)
    })
    
    if (!response.ok) {
      throw new Error('Failed to create post')
    }
    
    return response.json()
  }, {
    onSuccess: (data) => {
      // Update posts list
      mutate('/api/posts', (currentPosts) => 
        currentPosts ? [data, ...currentPosts] : [data], false
      )
      
      // Set individual post cache
      mutate(`/api/posts/${data.id}`, data, false)
    }
  })
}

// Optimistic updates with SWR
function useOptimisticUpdatePost() {
  const { mutate } = useSWRConfig()

  return useSWRMutation(
    '/api/posts',
    async (url, { arg: { id, updates } }) => {
      const response = await fetch(`${url}/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      
      return response.json()
    },
    {
      optimisticData: ({ id, updates }) => updates,
      rollbackOnError: true,
      populateCache: true,
      revalidate: false
    }
  )
}

// Cache manipulation
function useCacheManager() {
  const { mutate, cache } = useSWRConfig()

  const invalidatePattern = useCallback((pattern) => {
    const keys = Array.from(cache.keys()).filter(key => 
      key.includes(pattern)
    )
    
    keys.forEach(key => mutate(key))
  }, [mutate, cache])

  const clearCache = useCallback(() => {
    cache.clear()
  }, [cache])

  const preload = useCallback(async (key) => {
    await mutate(key)
  }, [mutate])

  return {
    invalidatePattern,
    clearCache,
    preload
  }
}
```

## Comparison and Selection

### React Query vs SWR Feature Comparison

```javascript
// React Query advantages
const reactQueryFeatures = {
  // More granular cache control
  queryClient: {
    setQueryData: (key, data) => {},
    invalidateQueries: (key) => {},
    removeQueries: (key) => {},
    getQueryData: (key) => {},
    prefetchQuery: (options) => {}
  },
  
  // Built-in DevTools
  devtools: '<ReactQueryDevtools initialIsOpen={false} />',
  
  // Advanced retry logic
  retry: (failureCount, error) => {
    if (error.status === 404) return false
    return failureCount < 3
  },
  
  // Dependent queries
  enabled: (previousQueryResult) => !!previousQueryResult?.id,
  
  // Infinite queries with bi-directional support
  infiniteQuery: {
    getNextPageParam: (lastPage, pages) => lastPage.nextCursor,
    getPreviousPageParam: (firstPage, pages) => firstPage.prevCursor
  },
  
  // Optimistic updates with context
  onMutate: async (variables) => {
    const context = { previous: getCurrentData() }
    applyOptimisticUpdate(variables)
    return context
  }
}

// SWR advantages
const swrFeatures = {
  // Simpler API
  basicUsage: 'const { data, error } = useSWR(key, fetcher)',
  
  // Smaller bundle size (~5KB vs ~13KB)
  bundleSize: 'Lighter weight',
  
  // Built-in revalidation strategies
  revalidation: {
    revalidateOnFocus: true,
    revalidateOnReconnect: true,
    refreshInterval: 1000
  },
  
  // Simpler infinite loading
  infinite: 'useSWRInfinite(getKey, fetcher)',
  
  // Built-in request deduplication
  deduplication: { dedupingInterval: 2000 },
  
  // Middleware support
  middleware: (useSWRNext) => (key, fetcher, config) => {
    // Custom logic
    return useSWRNext(key, fetcher, config)
  }
}

// Selection guide
function selectDataFetchingLibrary(requirements) {
  const scores = { reactQuery: 0, swr: 0 }
  
  // Complex cache management needs
  if (requirements.complexCaching) scores.reactQuery += 3
  
  // Bundle size is critical
  if (requirements.bundleSize) scores.swr += 2
  
  // Need advanced DevTools
  if (requirements.devtools) scores.reactQuery += 2
  
  // Simple use cases
  if (requirements.simplicity) scores.swr += 2
  
  // Advanced optimistic updates
  if (requirements.optimisticUpdates) scores.reactQuery += 2
  
  // Real-time features
  if (requirements.realtime) scores.swr += 1
  
  return scores.reactQuery > scores.swr ? 'React Query' : 'SWR'
}
```

## Advanced Caching Strategies

### Multi-level Caching

```javascript
// Browser storage integration
class PersistentQueryCache {
  constructor(storage = localStorage, keyPrefix = 'query-cache:') {
    this.storage = storage
    this.keyPrefix = keyPrefix
  }

  set(key, data, ttl = 3600000) { // 1 hour default
    const item = {
      data,
      timestamp: Date.now(),
      ttl
    }
    
    try {
      this.storage.setItem(
        `${this.keyPrefix}${key}`, 
        JSON.stringify(item)
      )
    } catch (error) {
      console.warn('Failed to persist cache:', error)
    }
  }

  get(key) {
    try {
      const item = this.storage.getItem(`${this.keyPrefix}${key}`)
      if (!item) return null

      const parsed = JSON.parse(item)
      const isExpired = Date.now() - parsed.timestamp > parsed.ttl

      if (isExpired) {
        this.remove(key)
        return null
      }

      return parsed.data
    } catch (error) {
      console.warn('Failed to read from cache:', error)
      return null
    }
  }

  remove(key) {
    try {
      this.storage.removeItem(`${this.keyPrefix}${key}`)
    } catch (error) {
      console.warn('Failed to remove from cache:', error)
    }
  }

  clear() {
    try {
      const keys = Object.keys(this.storage)
        .filter(key => key.startsWith(this.keyPrefix))
      
      keys.forEach(key => this.storage.removeItem(key))
    } catch (error) {
      console.warn('Failed to clear cache:', error)
    }
  }
}

// React Query with persistent cache
const persistentCache = new PersistentQueryCache()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      onSuccess: (data, query) => {
        // Persist successful queries
        persistentCache.set(
          JSON.stringify(query.queryKey), 
          data,
          query.cacheTime
        )
      }
    }
  }
})

// Custom hook with persistent cache fallback
function usePersistentQuery(queryKey, queryFn, options = {}) {
  const queryKeyString = JSON.stringify(queryKey)
  
  const query = useQuery({
    queryKey,
    queryFn,
    initialData: () => {
      // Try to get from persistent cache
      return persistentCache.get(queryKeyString)
    },
    ...options
  })

  return query
}
```

### Cache Invalidation Strategies

```javascript
// Tag-based cache invalidation
class TaggedQueryCache {
  constructor(queryClient) {
    this.queryClient = queryClient
    this.tagMap = new Map() // tag -> Set of query keys
    this.keyTagMap = new Map() // query key -> Set of tags
  }

  setQueryTags(queryKey, tags) {
    const keyString = JSON.stringify(queryKey)
    
    // Remove old mappings
    const oldTags = this.keyTagMap.get(keyString) || new Set()
    oldTags.forEach(tag => {
      const keys = this.tagMap.get(tag)
      if (keys) {
        keys.delete(keyString)
        if (keys.size === 0) {
          this.tagMap.delete(tag)
        }
      }
    })

    // Add new mappings
    this.keyTagMap.set(keyString, new Set(tags))
    tags.forEach(tag => {
      if (!this.tagMap.has(tag)) {
        this.tagMap.set(tag, new Set())
      }
      this.tagMap.get(tag).add(keyString)
    })
  }

  invalidateTag(tag) {
    const queryKeys = this.tagMap.get(tag)
    if (queryKeys) {
      queryKeys.forEach(keyString => {
        const queryKey = JSON.parse(keyString)
        this.queryClient.invalidateQueries(queryKey)
      })
    }
  }

  invalidateTags(tags) {
    tags.forEach(tag => this.invalidateTag(tag))
  }

  getQueriesByTag(tag) {
    return Array.from(this.tagMap.get(tag) || [])
      .map(keyString => JSON.parse(keyString))
  }
}

// Usage with tagged queries
const taggedCache = new TaggedQueryCache(queryClient)

function useTaggedQuery(queryKey, queryFn, tags, options = {}) {
  const query = useQuery({
    queryKey,
    queryFn,
    onSuccess: () => {
      taggedCache.setQueryTags(queryKey, tags)
    },
    ...options
  })

  return query
}

// Example usage
function UserProfile({ userId }) {
  const { data: user } = useTaggedQuery(
    ['user', userId],
    () => fetchUser(userId),
    ['user', `user:${userId}`]
  )

  const { data: posts } = useTaggedQuery(
    ['posts', 'user', userId],
    () => fetchUserPosts(userId),
    ['posts', 'user-posts', `user:${userId}`]
  )

  // When user updates, invalidate all user-related queries
  const updateUserMutation = useMutation({
    mutationFn: updateUser,
    onSuccess: () => {
      taggedCache.invalidateTag(`user:${userId}`)
    }
  })

  return (
    <div>
      {/* User profile UI */}
    </div>
  )
}
```

## Real-time Data Synchronization

### WebSocket Integration

```javascript
// WebSocket hook with React Query
function useWebSocketQuery(queryKey, wsUrl, options = {}) {
  const queryClient = useQueryClient()
  const wsRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        // Update query cache with real-time data
        queryClient.setQueryData(queryKey, (oldData) => {
          if (options.merge && oldData) {
            return options.merge(oldData, data)
          }
          return data
        })
      } catch (error) {
        console.error('WebSocket message parsing error:', error)
      }
    }

    ws.onopen = () => {
      console.log('WebSocket connected')
      if (options.onConnect) {
        options.onConnect(ws)
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      if (options.onDisconnect) {
        options.onDisconnect()
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (options.onError) {
        options.onError(error)
      }
    }

    return () => {
      ws.close()
    }
  }, [wsUrl, queryClient])

  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  return { sendMessage }
}

// Real-time chat implementation
function useChatRoom(roomId) {
  const queryKey = ['chat', 'room', roomId]
  
  // Initial chat history
  const { data: messages = [] } = useQuery({
    queryKey,
    queryFn: () => fetchChatHistory(roomId),
    staleTime: Infinity // Don't refetch, rely on WebSocket
  })

  // WebSocket for real-time updates
  const { sendMessage } = useWebSocketQuery(
    queryKey,
    `ws://localhost:8080/chat/${roomId}`,
    {
      merge: (oldMessages, newMessage) => {
        // Handle different message types
        switch (newMessage.type) {
          case 'message':
            return [...oldMessages, newMessage.data]
          case 'delete':
            return oldMessages.filter(msg => msg.id !== newMessage.data.id)
          case 'edit':
            return oldMessages.map(msg =>
              msg.id === newMessage.data.id 
                ? { ...msg, ...newMessage.data }
                : msg
            )
          default:
            return oldMessages
        }
      },
      onConnect: (ws) => {
        // Join room
        ws.send(JSON.stringify({ type: 'join', roomId }))
      }
    }
  )

  const sendChatMessage = useCallback((content) => {
    sendMessage({
      type: 'message',
      content,
      timestamp: Date.now()
    })
  }, [sendMessage])

  return {
    messages,
    sendMessage: sendChatMessage
  }
}
```

### Server-Sent Events (SSE)

```javascript
// SSE hook for real-time updates
function useServerSentEvents(url, options = {}) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const eventSourceRef = useRef(null)

  useEffect(() => {
    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.onopen = () => {
      setIsConnected(true)
      setError(null)
      if (options.onOpen) options.onOpen()
    }

    eventSource.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data)
        setData(prevData => {
          if (options.merge && prevData) {
            return options.merge(prevData, newData)
          }
          return newData
        })
        
        if (options.onMessage) options.onMessage(newData)
      } catch (err) {
        console.error('SSE parsing error:', err)
      }
    }

    eventSource.onerror = (err) => {
      setIsConnected(false)
      setError(err)
      if (options.onError) options.onError(err)
    }

    // Custom event listeners
    if (options.eventListeners) {
      Object.entries(options.eventListeners).forEach(([eventType, handler]) => {
        eventSource.addEventListener(eventType, handler)
      })
    }

    return () => {
      eventSource.close()
      setIsConnected(false)
    }
  }, [url])

  const close = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }
  }, [])

  return { data, error, isConnected, close }
}

// Live notifications system
function useNotifications() {
  const queryClient = useQueryClient()
  
  const { data: notifications } = useServerSentEvents('/api/notifications/stream', {
    merge: (existing, newNotification) => [newNotification, ...existing],
    onMessage: (notification) => {
      // Update related queries based on notification type
      switch (notification.type) {
        case 'new_message':
          queryClient.invalidateQueries(['chat', 'room', notification.roomId])
          break
        case 'post_like':
          queryClient.invalidateQueries(['post', notification.postId])
          break
        case 'user_follow':
          queryClient.invalidateQueries(['user', notification.userId, 'followers'])
          break
      }
    },
    eventListeners: {
      'user-event': (event) => {
        const data = JSON.parse(event.data)
        queryClient.invalidateQueries(['user', data.userId])
      },
      'system-event': (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'maintenance') {
          // Show maintenance notification
          showMaintenanceNotification(data)
        }
      }
    }
  })

  return { notifications: notifications || [] }
}
```

## Offline Support

### Offline-First Data Strategy

```javascript
// Service Worker integration for offline caching
class OfflineQueryManager {
  constructor(queryClient) {
    this.queryClient = queryClient
    this.pendingMutations = new Map()
    this.isOnline = navigator.onLine
    
    this.setupEventListeners()
  }

  setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true
      this.syncPendingMutations()
    })

    window.addEventListener('offline', () => {
      this.isOnline = false
    })
  }

  addPendingMutation(key, mutationFn, variables) {
    if (!this.pendingMutations.has(key)) {
      this.pendingMutations.set(key, [])
    }
    
    this.pendingMutations.get(key).push({
      mutationFn,
      variables,
      timestamp: Date.now()
    })

    // Persist to localStorage
    this.persistPendingMutations()
  }

  async syncPendingMutations() {
    for (const [key, mutations] of this.pendingMutations.entries()) {
      for (const mutation of mutations) {
        try {
          await mutation.mutationFn(mutation.variables)
          console.log(`Synced offline mutation: ${key}`)
        } catch (error) {
          console.error(`Failed to sync mutation ${key}:`, error)
        }
      }
    }

    this.pendingMutations.clear()
    this.persistPendingMutations()
  }

  persistPendingMutations() {
    try {
      const mutations = Array.from(this.pendingMutations.entries())
      localStorage.setItem('pendingMutations', JSON.stringify(mutations))
    } catch (error) {
      console.warn('Failed to persist pending mutations:', error)
    }
  }

  loadPendingMutations() {
    try {
      const stored = localStorage.getItem('pendingMutations')
      if (stored) {
        const mutations = JSON.parse(stored)
        this.pendingMutations = new Map(mutations)
      }
    } catch (error) {
      console.warn('Failed to load pending mutations:', error)
    }
  }
}

// Offline-aware mutation hook
function useOfflineMutation(mutationFn, options = {}) {
  const offlineManager = useContext(OfflineManagerContext)
  
  return useMutation({
    mutationFn: async (variables) => {
      if (!navigator.onLine) {
        // Queue for later sync
        const mutationKey = options.offlineKey || `mutation-${Date.now()}`
        offlineManager.addPendingMutation(mutationKey, mutationFn, variables)
        
        // Apply optimistic update
        if (options.optimisticUpdate) {
          options.optimisticUpdate(variables)
        }
        
        throw new Error('Offline: Mutation queued for sync')
      }
      
      return mutationFn(variables)
    },
    ...options
  })
}

// Offline indicator component
function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [syncInProgress, setSyncInProgress] = useState(false)
  const offlineManager = useContext(OfflineManagerContext)

  useEffect(() => {
    const handleOnline = async () => {
      setIsOnline(true)
      setSyncInProgress(true)
      
      await offlineManager.syncPendingMutations()
      
      setSyncInProgress(false)
    }

    const handleOffline = () => {
      setIsOnline(false)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [offlineManager])

  if (isOnline && !syncInProgress) return null

  return (
    <div className="offline-indicator">
      {!isOnline && (
        <div className="offline-banner">
          📡 You're offline. Changes will sync when connection is restored.
        </div>
      )}
      {syncInProgress && (
        <div className="sync-banner">
          🔄 Syncing offline changes...
        </div>
      )}
    </div>
  )
}
```

## Performance Optimization

### Request Deduplication and Batching

```javascript
// Request batching utility
class RequestBatcher {
  constructor(batchFn, { delay = 50, maxBatchSize = 10 } = {}) {
    this.batchFn = batchFn
    this.delay = delay
    this.maxBatchSize = maxBatchSize
    this.queue = []
    this.timeoutId = null
  }

  add(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ ...request, resolve, reject })

      if (this.queue.length >= this.maxBatchSize) {
        this.flush()
      } else if (!this.timeoutId) {
        this.timeoutId = setTimeout(() => this.flush(), this.delay)
      }
    })
  }

  async flush() {
    if (this.queue.length === 0) return

    const batch = this.queue.splice(0)
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }

    try {
      const results = await this.batchFn(batch.map(item => item.request))
      
      batch.forEach((item, index) => {
        item.resolve(results[index])
      })
    } catch (error) {
      batch.forEach(item => {
        item.reject(error)
      })
    }
  }
}

// Batched user fetching
const userBatcher = new RequestBatcher(
  async (userIds) => {
    const response = await fetch('/api/users/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userIds })
    })
    return response.json()
  },
  { delay: 10, maxBatchSize: 50 }
)

function useBatchedUser(userId) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => userBatcher.add({ userId }),
    staleTime: 1000 * 60 * 5
  })
}

// Request deduplication
class RequestDeduplicator {
  constructor() {
    this.pendingRequests = new Map()
  }

  async dedupe(key, requestFn) {
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key)
    }

    const promise = requestFn().finally(() => {
      this.pendingRequests.delete(key)
    })

    this.pendingRequests.set(key, promise)
    return promise
  }
}

const deduplicator = new RequestDeduplicator()

function useDedupedQuery(queryKey, queryFn, options = {}) {
  const dedupedQueryFn = useCallback(() => {
    const key = JSON.stringify(queryKey)
    return deduplicator.dedupe(key, queryFn)
  }, [queryKey, queryFn])

  return useQuery({
    queryKey,
    queryFn: dedupedQueryFn,
    ...options
  })
}
```

### Memory Management and Cleanup

```javascript
// Memory-efficient infinite query
function useMemoryEfficientInfiniteQuery(queryKey, queryFn, options = {}) {
  const { maxPages = 10, ...restOptions } = options
  
  const query = useInfiniteQuery({
    queryKey,
    queryFn,
    ...restOptions,
    onSuccess: (data) => {
      // Limit the number of pages in memory
      if (data.pages.length > maxPages) {
        // Keep only the last maxPages
        data.pages = data.pages.slice(-maxPages)
      }
    }
  })

  return query
}

// Automatic query cleanup
function useQueryCleanup() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now()
      const maxAge = 1000 * 60 * 10 // 10 minutes

      // Remove old, unused queries
      queryClient.getQueryCache().getAll().forEach(query => {
        const lastUpdated = query.state.dataUpdatedAt
        const isStale = now - lastUpdated > maxAge
        const hasObservers = query.getObserversCount() > 0

        if (isStale && !hasObservers) {
          queryClient.removeQueries(query.queryKey)
        }
      })
    }, 1000 * 60 * 5) // Run every 5 minutes

    return () => clearInterval(interval)
  }, [queryClient])
}

// Component-level cleanup
function DataFetchingComponent() {
  const queryClient = useQueryClient()

  useEffect(() => {
    return () => {
      // Cleanup component-specific queries
      queryClient.removeQueries({
        predicate: (query) => {
          return query.queryKey[0] === 'component-specific'
        }
      })
    }
  }, [queryClient])

  // Component implementation
}
```

## Testing Strategies

### Mocking and Testing Data Fetching

```javascript
// Mock query client for testing
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0
      },
      mutations: {
        retry: false
      }
    },
    logger: {
      log: console.log,
      warn: console.warn,
      error: () => {} // Silence errors in tests
    }
  })
}

// Test wrapper
function TestWrapper({ children }) {
  const queryClient = createTestQueryClient()
  
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

// Mock server responses
const mockApi = {
  getUser: jest.fn(),
  getPosts: jest.fn(),
  createPost: jest.fn()
}

// Test examples
describe('useUser hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should fetch user data successfully', async () => {
    const mockUser = { id: '1', name: 'John Doe' }
    mockApi.getUser.mockResolvedValue(mockUser)

    const { result } = renderHook(
      () => useUser('1'),
      { wrapper: TestWrapper }
    )

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockUser)
    expect(mockApi.getUser).toHaveBeenCalledWith('1')
  })

  it('should handle error states', async () => {
    const mockError = new Error('User not found')
    mockApi.getUser.mockRejectedValue(mockError)

    const { result } = renderHook(
      () => useUser('999'),
      { wrapper: TestWrapper }
    )

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toEqual(mockError)
  })
})

// Integration testing with MSW
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params
    
    if (id === '1') {
      return res(ctx.json({ id: '1', name: 'John Doe' }))
    }
    
    return res(ctx.status(404), ctx.json({ error: 'User not found' }))
  }),
  
  rest.post('/api/posts', (req, res, ctx) => {
    const post = req.body
    return res(ctx.json({ ...post, id: '123' }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('Post creation', () => {
  it('should create post optimistically', async () => {
    render(<CreatePostForm />, { wrapper: TestWrapper })
    
    const titleInput = screen.getByLabelText('Title')
    const submitButton = screen.getByText('Create Post')
    
    fireEvent.change(titleInput, { target: { value: 'Test Post' } })
    fireEvent.click(submitButton)
    
    // Should show optimistic update immediately
    expect(screen.getByText('Test Post')).toBeInTheDocument()
    
    // Wait for server response
    await waitFor(() => {
      expect(screen.getByText('Post created successfully')).toBeInTheDocument()
    })
  })
})
```

## Best Practices

### 1. Query Key Design
- Use hierarchical keys: `['posts', 'user', userId]`
- Include all variables that affect the query
- Keep keys consistent across the application
- Use object syntax for complex parameters

### 2. Error Handling
- Implement global error boundaries
- Provide user-friendly error messages
- Use retry strategies appropriately
- Log errors for monitoring

### 3. Performance
- Use stale-while-revalidate appropriately
- Implement proper cache invalidation
- Consider memory usage for large datasets
- Use background refetching for better UX

### 4. Real-time Updates
- Combine polling with WebSocket for reliability
- Handle connection states gracefully
- Implement exponential backoff for reconnection
- Use optimistic updates for immediate feedback

### 5. Offline Support
- Queue mutations when offline
- Provide clear offline indicators
- Sync data when coming back online
- Use service workers for advanced caching

## Conclusion

React Query and SWR provide powerful abstractions for data fetching that solve many common problems in modern React applications. By mastering these tools and implementing proper patterns for caching, real-time updates, and offline support, you can build robust, performant applications that provide excellent user experiences even in challenging network conditions.

Key takeaways:
- Choose the right tool based on your specific needs
- Implement proper error handling and loading states
- Use optimistic updates for better perceived performance
- Design cache invalidation strategies carefully
- Test your data fetching logic thoroughly
- Consider offline scenarios in your design
