# GraphQL & Apollo Integration

## Table of Contents
1. [Introduction to GraphQL](#introduction-to-graphql)
2. [Apollo Client Setup](#apollo-client-setup)
3. [Query Management](#query-management)
4. [Mutation Patterns](#mutation-patterns)
5. [Subscription Handling](#subscription-handling)
6. [Cache Management](#cache-management)
7. [Error Handling](#error-handling)
8. [Code Generation](#code-generation)
9. [Testing GraphQL](#testing-graphql)
10. [Performance Optimization](#performance-optimization)
11. [Advanced Patterns](#advanced-patterns)

## Introduction to GraphQL

### GraphQL Fundamentals

GraphQL is a query language and runtime for APIs that provides a complete and understandable description of your data.

```typescript
// GraphQL Schema Example
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  createdAt: DateTime!
}

type Query {
  user(id: ID!): User
  users: [User!]!
  post(id: ID!): Post
  posts: [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}

type Subscription {
  userUpdated(id: ID!): User!
  postAdded: Post!
}
```

### Benefits of GraphQL

```typescript
// REST vs GraphQL comparison
// REST - Multiple requests needed
const fetchUserWithPosts = async (userId: string) => {
  const user = await fetch(`/api/users/${userId}`);
  const posts = await fetch(`/api/users/${userId}/posts`);
  const comments = await fetch(`/api/posts/${posts[0].id}/comments`);
  
  return { user, posts, comments };
};

// GraphQL - Single request
const USER_WITH_POSTS = gql`
  query GetUserWithPosts($userId: ID!) {
    user(id: $userId) {
      id
      name
      email
      posts {
        id
        title
        content
        comments {
          id
          content
          author {
            name
          }
        }
      }
    }
  }
`;
```

## Apollo Client Setup

### Installation and Configuration

```bash
npm install @apollo/client graphql
```

```typescript
// apollo-client.ts
import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { RetryLink } from '@apollo/client/link/retry';

// HTTP Link
const httpLink = createHttpLink({
  uri: process.env.REACT_APP_GRAPHQL_ENDPOINT || 'http://localhost:4000/graphql',
});

// Auth Link
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    }
  };
});

// Error Link
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `GraphQL error: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
    });
  }

  if (networkError) {
    console.error(`Network error: ${networkError}`);
    
    // Handle authentication errors
    if (networkError.statusCode === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
  }
});

// Retry Link
const retryLink = new RetryLink({
  delay: {
    initial: 300,
    max: Infinity,
    jitter: true
  },
  attempts: {
    max: 3,
    retryIf: (error, _operation) => !!error
  }
});

// Apollo Client
export const client = new ApolloClient({
  link: from([
    errorLink,
    retryLink,
    authLink.concat(httpLink)
  ]),
  cache: new InMemoryCache({
    typePolicies: {
      User: {
        fields: {
          posts: {
            merge(existing = [], incoming) {
              return [...existing, ...incoming];
            }
          }
        }
      }
    }
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-and-network'
    },
    query: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-first'
    }
  }
});

// Provider Setup
import { ApolloProvider } from '@apollo/client';

function App() {
  return (
    <ApolloProvider client={client}>
      <Router>
        <Routes>
          {/* Your routes */}
        </Routes>
      </Router>
    </ApolloProvider>
  );
}
```

### Apollo Client DevTools Integration

```typescript
// apollo-client.ts (development configuration)
import { ApolloClient, InMemoryCache } from '@apollo/client';

export const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql',
  cache: new InMemoryCache(),
  connectToDevTools: process.env.NODE_ENV === 'development',
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all'
    }
  }
});
```

## Query Management

### Basic Queries

```typescript
// queries/user.ts
import { gql } from '@apollo/client';

export const GET_USERS = gql`
  query GetUsers($limit: Int, $offset: Int) {
    users(limit: $limit, offset: $offset) {
      id
      name
      email
      avatar
      createdAt
    }
  }
`;

export const GET_USER_DETAIL = gql`
  query GetUserDetail($id: ID!) {
    user(id: $id) {
      id
      name
      email
      bio
      avatar
      posts {
        id
        title
        excerpt
        createdAt
      }
      followers {
        id
        name
        avatar
      }
      following {
        id
        name
        avatar
      }
    }
  }
`;

// components/UserList.tsx
import { useQuery } from '@apollo/client';
import { GET_USERS } from '../queries/user';

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  createdAt: string;
}

interface GetUsersData {
  users: User[];
}

interface GetUsersVars {
  limit?: number;
  offset?: number;
}

const UserList: React.FC = () => {
  const { data, loading, error, fetchMore, refetch } = useQuery<GetUsersData, GetUsersVars>(
    GET_USERS,
    {
      variables: { limit: 10, offset: 0 },
      errorPolicy: 'all',
      notifyOnNetworkStatusChange: true
    }
  );

  const loadMore = () => {
    fetchMore({
      variables: {
        offset: data?.users.length || 0
      },
      updateQuery: (prev, { fetchMoreResult }) => {
        if (!fetchMoreResult) return prev;
        return {
          users: [...prev.users, ...fetchMoreResult.users]
        };
      }
    });
  };

  if (loading && !data) return <LoadingSpinner />;
  if (error && !data) return <ErrorMessage error={error} />;

  return (
    <div className="user-list">
      {data?.users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
      
      <button onClick={loadMore} disabled={loading}>
        {loading ? 'Loading...' : 'Load More'}
      </button>
      
      <button onClick={() => refetch()}>
        Refresh
      </button>
    </div>
  );
};
```

### Query with Variables and Fragments

```typescript
// fragments/user.ts
import { gql } from '@apollo/client';

export const USER_FRAGMENT = gql`
  fragment UserInfo on User {
    id
    name
    email
    avatar
    bio
    createdAt
  }
`;

export const POST_FRAGMENT = gql`
  fragment PostInfo on Post {
    id
    title
    content
    excerpt
    createdAt
    author {
      ...UserInfo
    }
  }
  ${USER_FRAGMENT}
`;

// queries/posts.ts
import { gql } from '@apollo/client';
import { POST_FRAGMENT } from '../fragments/user';

export const GET_POSTS = gql`
  query GetPosts($filter: PostFilter, $sort: PostSort, $pagination: Pagination) {
    posts(filter: $filter, sort: $sort, pagination: $pagination) {
      data {
        ...PostInfo
        commentsCount
        likesCount
        isLiked
      }
      pagination {
        total
        page
        limit
        hasNext
        hasPrev
      }
    }
  }
  ${POST_FRAGMENT}
`;

// hooks/usePosts.ts
import { useQuery } from '@apollo/client';
import { GET_POSTS } from '../queries/posts';

interface PostFilter {
  authorId?: string;
  category?: string;
  tag?: string;
  search?: string;
}

interface PostSort {
  field: 'createdAt' | 'updatedAt' | 'title';
  order: 'ASC' | 'DESC';
}

interface Pagination {
  page: number;
  limit: number;
}

export const usePosts = (
  filter?: PostFilter,
  sort: PostSort = { field: 'createdAt', order: 'DESC' },
  pagination: Pagination = { page: 1, limit: 10 }
) => {
  return useQuery(GET_POSTS, {
    variables: { filter, sort, pagination },
    errorPolicy: 'all',
    fetchPolicy: 'cache-and-network'
  });
};

// components/PostList.tsx
const PostList: React.FC = () => {
  const [filter, setFilter] = useState<PostFilter>({});
  const [sort, setSort] = useState<PostSort>({ field: 'createdAt', order: 'DESC' });
  const [page, setPage] = useState(1);

  const { data, loading, error } = usePosts(filter, sort, { page, limit: 10 });

  return (
    <div className="post-list">
      <PostFilters filter={filter} onFilterChange={setFilter} />
      <PostSort sort={sort} onSortChange={setSort} />
      
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage error={error} />}
      
      {data?.posts.data.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
      
      <Pagination
        current={page}
        total={data?.posts.pagination.total || 0}
        pageSize={10}
        onChange={setPage}
      />
    </div>
  );
};
```

### Lazy Queries

```typescript
// hooks/useUserSearch.ts
import { useLazyQuery } from '@apollo/client';
import { SEARCH_USERS } from '../queries/user';

export const useUserSearch = () => {
  const [searchUsers, { data, loading, error }] = useLazyQuery(SEARCH_USERS, {
    errorPolicy: 'all',
    fetchPolicy: 'cache-and-network'
  });

  const search = useCallback((query: string) => {
    if (query.trim()) {
      searchUsers({ variables: { query } });
    }
  }, [searchUsers]);

  return {
    search,
    users: data?.searchUsers || [],
    loading,
    error
  };
};

// components/UserSearch.tsx
const UserSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const { search, users, loading, error } = useUserSearch();
  
  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    if (query) {
      debouncedSearch(query);
    }
  }, [query, debouncedSearch]);

  return (
    <div className="user-search">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search users..."
      />
      
      {loading && <span>Searching...</span>}
      {error && <ErrorMessage error={error} />}
      
      <div className="search-results">
        {users.map(user => (
          <UserSearchResult key={user.id} user={user} />
        ))}
      </div>
    </div>
  );
};
```

## Mutation Patterns

### Basic Mutations

```typescript
// mutations/user.ts
import { gql } from '@apollo/client';
import { USER_FRAGMENT } from '../fragments/user';

export const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      ...UserInfo
    }
  }
  ${USER_FRAGMENT}
`;

export const UPDATE_USER = gql`
  mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
    updateUser(id: $id, input: $input) {
      ...UserInfo
    }
  }
  ${USER_FRAGMENT}
`;

export const DELETE_USER = gql`
  mutation DeleteUser($id: ID!) {
    deleteUser(id: $id)
  }
`;

// hooks/useUserMutations.ts
import { useMutation } from '@apollo/client';
import { CREATE_USER, UPDATE_USER, DELETE_USER } from '../mutations/user';
import { GET_USERS } from '../queries/user';

export const useUserMutations = () => {
  const [createUser, { loading: creating }] = useMutation(CREATE_USER, {
    update(cache, { data }) {
      const existingUsers = cache.readQuery({ query: GET_USERS });
      if (existingUsers && data?.createUser) {
        cache.writeQuery({
          query: GET_USERS,
          data: {
            users: [data.createUser, ...existingUsers.users]
          }
        });
      }
    },
    onCompleted: (data) => {
      toast.success('User created successfully!');
    },
    onError: (error) => {
      toast.error(`Failed to create user: ${error.message}`);
    }
  });

  const [updateUser, { loading: updating }] = useMutation(UPDATE_USER, {
    onCompleted: (data) => {
      toast.success('User updated successfully!');
    },
    onError: (error) => {
      toast.error(`Failed to update user: ${error.message}`);
    }
  });

  const [deleteUser, { loading: deleting }] = useMutation(DELETE_USER, {
    update(cache, { data }, { variables }) {
      if (data?.deleteUser) {
        cache.modify({
          fields: {
            users(existingUsers = [], { readField }) {
              return existingUsers.filter(
                (userRef: any) => readField('id', userRef) !== variables?.id
              );
            }
          }
        });
      }
    },
    onCompleted: () => {
      toast.success('User deleted successfully!');
    },
    onError: (error) => {
      toast.error(`Failed to delete user: ${error.message}`);
    }
  });

  return {
    createUser,
    updateUser,
    deleteUser,
    loading: creating || updating || deleting
  };
};
```

### Optimistic Updates

```typescript
// hooks/usePostMutations.ts
import { useMutation } from '@apollo/client';
import { LIKE_POST, UNLIKE_POST } from '../mutations/post';

export const usePostLike = () => {
  const [likePost] = useMutation(LIKE_POST, {
    optimisticResponse: (variables) => ({
      likePost: {
        __typename: 'Post',
        id: variables.postId,
        isLiked: true,
        likesCount: 0 // Will be updated by the server response
      }
    }),
    update(cache, { data }, { variables }) {
      cache.modify({
        id: cache.identify({ __typename: 'Post', id: variables?.postId }),
        fields: {
          isLiked() {
            return true;
          },
          likesCount(existingCount = 0) {
            return existingCount + 1;
          }
        }
      });
    },
    onError: (error, { variables }) => {
      // Revert optimistic update on error
      cache.modify({
        id: cache.identify({ __typename: 'Post', id: variables?.postId }),
        fields: {
          isLiked() {
            return false;
          },
          likesCount(existingCount = 0) {
            return Math.max(0, existingCount - 1);
          }
        }
      });
      toast.error('Failed to like post');
    }
  });

  const [unlikePost] = useMutation(UNLIKE_POST, {
    optimisticResponse: (variables) => ({
      unlikePost: {
        __typename: 'Post',
        id: variables.postId,
        isLiked: false,
        likesCount: 0
      }
    }),
    update(cache, { data }, { variables }) {
      cache.modify({
        id: cache.identify({ __typename: 'Post', id: variables?.postId }),
        fields: {
          isLiked() {
            return false;
          },
          likesCount(existingCount = 0) {
            return Math.max(0, existingCount - 1);
          }
        }
      });
    }
  });

  return { likePost, unlikePost };
};
```

### File Upload Mutations

```typescript
// mutations/upload.ts
import { gql } from '@apollo/client';

export const UPLOAD_FILE = gql`
  mutation UploadFile($file: Upload!) {
    uploadFile(file: $file) {
      id
      filename
      mimetype
      encoding
      url
    }
  }
`;

export const UPDATE_USER_AVATAR = gql`
  mutation UpdateUserAvatar($userId: ID!, $file: Upload!) {
    updateUserAvatar(userId: $userId, file: $file) {
      id
      avatar
    }
  }
`;

// components/FileUpload.tsx
import { useMutation } from '@apollo/client';
import { UPLOAD_FILE } from '../mutations/upload';

const FileUpload: React.FC = () => {
  const [uploadFile, { loading, error }] = useMutation(UPLOAD_FILE, {
    onCompleted: (data) => {
      console.log('File uploaded:', data.uploadFile);
    }
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadFile({
        variables: { file },
        context: {
          hasUpload: true
        }
      });
    }
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        onChange={handleFileChange}
        disabled={loading}
      />
      {loading && <progress />}
      {error && <span>Upload failed: {error.message}</span>}
    </div>
  );
};
```

## Subscription Handling

### Real-time Updates

```typescript
// subscriptions/post.ts
import { gql } from '@apollo/client';
import { POST_FRAGMENT } from '../fragments/user';

export const POST_ADDED = gql`
  subscription PostAdded {
    postAdded {
      ...PostInfo
    }
  }
  ${POST_FRAGMENT}
`;

export const POST_UPDATED = gql`
  subscription PostUpdated($postId: ID!) {
    postUpdated(postId: $postId) {
      ...PostInfo
    }
  }
  ${POST_FRAGMENT}
`;

export const COMMENT_ADDED = gql`
  subscription CommentAdded($postId: ID!) {
    commentAdded(postId: $postId) {
      id
      content
      createdAt
      author {
        id
        name
        avatar
      }
    }
  }
`;

// hooks/useRealtimePosts.ts
import { useSubscription } from '@apollo/client';
import { POST_ADDED } from '../subscriptions/post';
import { GET_POSTS } from '../queries/posts';

export const useRealtimePosts = () => {
  const { data, loading } = useSubscription(POST_ADDED, {
    onSubscriptionData: ({ client, subscriptionData }) => {
      const newPost = subscriptionData.data?.postAdded;
      if (newPost) {
        // Update cache with new post
        const existingPosts = client.readQuery({ query: GET_POSTS });
        if (existingPosts) {
          client.writeQuery({
            query: GET_POSTS,
            data: {
              posts: {
                ...existingPosts.posts,
                data: [newPost, ...existingPosts.posts.data]
              }
            }
          });
        }
        
        // Show notification
        toast.success(`New post by ${newPost.author.name}`);
      }
    }
  });

  return { newPost: data?.postAdded, loading };
};

// components/RealtimePostList.tsx
const RealtimePostList: React.FC = () => {
  const { data: postsData, loading, error } = useQuery(GET_POSTS);
  const { newPost } = useRealtimePosts();

  return (
    <div className="realtime-post-list">
      {newPost && (
        <div className="new-post-notification">
          New post available! <button>Refresh</button>
        </div>
      )}
      
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage error={error} />}
      
      {postsData?.posts.data.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
};
```

### WebSocket Setup

```typescript
// apollo-client.ts (with subscriptions)
import { ApolloClient, InMemoryCache, split, HttpLink } from '@apollo/client';
import { getMainDefinition } from '@apollo/client/utilities';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';

const httpLink = new HttpLink({
  uri: 'http://localhost:4000/graphql'
});

const wsLink = new GraphQLWsLink(createClient({
  url: 'ws://localhost:4000/graphql',
  connectionParams: () => {
    const token = localStorage.getItem('token');
    return {
      authorization: token ? `Bearer ${token}` : ''
    };
  },
  on: {
    connected: () => console.log('WebSocket connected'),
    closed: () => console.log('WebSocket closed'),
    error: (error) => console.error('WebSocket error:', error)
  }
}));

const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink
);

export const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache()
});
```

## Cache Management

### Cache Policies and Type Policies

```typescript
// apollo-client.ts (advanced cache configuration)
import { InMemoryCache, makeVar } from '@apollo/client';

// Reactive variables
export const currentUserVar = makeVar<User | null>(null);
export const themeVar = makeVar<'light' | 'dark'>('light');

export const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        currentUser: {
          read() {
            return currentUserVar();
          }
        },
        theme: {
          read() {
            return themeVar();
          }
        },
        posts: {
          keyArgs: ['filter', 'sort'],
          merge(existing = { data: [], pagination: {} }, incoming) {
            return {
              data: [...existing.data, ...incoming.data],
              pagination: incoming.pagination
            };
          }
        }
      }
    },
    User: {
      keyFields: ['id'],
      fields: {
        posts: {
          merge(existing = [], incoming) {
            return [...existing, ...incoming];
          }
        }
      }
    },
    Post: {
      keyFields: ['id'],
      fields: {
        comments: {
          merge(existing = [], incoming) {
            const existingIds = existing.map((ref: any) => 
              cache.identify(ref)
            );
            return [
              ...existing,
              ...incoming.filter((ref: any) => 
                !existingIds.includes(cache.identify(ref))
              )
            ];
          }
        }
      }
    }
  }
});

// hooks/useReactiveVar.ts
import { useReactiveVar } from '@apollo/client';
import { currentUserVar, themeVar } from '../apollo-client';

export const useCurrentUser = () => {
  const currentUser = useReactiveVar(currentUserVar);
  
  const setCurrentUser = (user: User | null) => {
    currentUserVar(user);
  };

  return { currentUser, setCurrentUser };
};

export const useTheme = () => {
  const theme = useReactiveVar(themeVar);
  
  const toggleTheme = () => {
    themeVar(theme === 'light' ? 'dark' : 'light');
  };

  return { theme, toggleTheme };
};
```

### Cache Updates and Normalization

```typescript
// utils/cacheUtils.ts
import { ApolloCache, Reference } from '@apollo/client';

export const updateCacheAfterCreate = <T>(
  cache: ApolloCache<any>,
  query: any,
  newItem: T,
  field: string = 'data'
) => {
  try {
    const existingData = cache.readQuery({ query });
    if (existingData && existingData[field]) {
      cache.writeQuery({
        query,
        data: {
          [field]: [newItem, ...existingData[field]]
        }
      });
    }
  } catch (error) {
    console.warn('Failed to update cache after create:', error);
  }
};

export const updateCacheAfterDelete = (
  cache: ApolloCache<any>,
  deletedId: string,
  typename: string
) => {
  cache.modify({
    fields: {
      [typename.toLowerCase() + 's'](existingRefs: Reference[] = [], { readField }) {
        return existingRefs.filter(
          ref => readField('id', ref) !== deletedId
        );
      }
    }
  });
  
  // Remove from cache
  cache.evict({ id: cache.identify({ __typename: typename, id: deletedId }) });
  cache.gc();
};

// Custom cache update hooks
export const useCacheUpdates = () => {
  const updateAfterCreate = useCallback((query: any, newItem: any, field = 'data') => {
    return (cache: ApolloCache<any>) => {
      updateCacheAfterCreate(cache, query, newItem, field);
    };
  }, []);

  const updateAfterDelete = useCallback((deletedId: string, typename: string) => {
    return (cache: ApolloCache<any>) => {
      updateCacheAfterDelete(cache, deletedId, typename);
    };
  }, []);

  return { updateAfterCreate, updateAfterDelete };
};
```

## Error Handling

### GraphQL Error Management

```typescript
// utils/errorUtils.ts
import { ApolloError, GraphQLError } from '@apollo/client';

export interface AppError {
  message: string;
  type: 'NETWORK' | 'GRAPHQL' | 'VALIDATION' | 'AUTHENTICATION' | 'AUTHORIZATION';
  code?: string;
  field?: string;
}

export const parseApolloError = (error: ApolloError): AppError[] => {
  const errors: AppError[] = [];

  // Network errors
  if (error.networkError) {
    errors.push({
      message: 'Network connection failed. Please check your internet connection.',
      type: 'NETWORK'
    });
  }

  // GraphQL errors
  if (error.graphQLErrors) {
    error.graphQLErrors.forEach((gqlError: GraphQLError) => {
      const extensions = gqlError.extensions;
      
      errors.push({
        message: gqlError.message,
        type: getErrorType(extensions?.code as string),
        code: extensions?.code as string,
        field: extensions?.field as string
      });
    });
  }

  return errors;
};

const getErrorType = (code: string): AppError['type'] => {
  switch (code) {
    case 'UNAUTHENTICATED':
      return 'AUTHENTICATION';
    case 'FORBIDDEN':
      return 'AUTHORIZATION';
    case 'BAD_USER_INPUT':
    case 'VALIDATION_ERROR':
      return 'VALIDATION';
    default:
      return 'GRAPHQL';
  }
};

// hooks/useErrorHandler.ts
export const useErrorHandler = () => {
  const handleError = useCallback((error: ApolloError) => {
    const appErrors = parseApolloError(error);
    
    appErrors.forEach(appError => {
      switch (appError.type) {
        case 'AUTHENTICATION':
          // Redirect to login
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 'AUTHORIZATION':
          toast.error('You do not have permission to perform this action');
          break;
        case 'VALIDATION':
          toast.error(`Validation error: ${appError.message}`);
          break;
        case 'NETWORK':
          toast.error(appError.message);
          break;
        default:
          toast.error(`Error: ${appError.message}`);
      }
    });
  }, []);

  return { handleError };
};

// components/ErrorBoundary.tsx
import { ApolloError } from '@apollo/client';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>;
}

const ErrorBoundary: React.FC<ErrorBoundaryProps> = ({ 
  children, 
  fallback: Fallback = DefaultErrorFallback 
}) => {
  const [error, setError] = useState<Error | null>(null);

  const retry = () => setError(null);

  if (error) {
    return <Fallback error={error} retry={retry} />;
  }

  return (
    <React.Suspense fallback={<LoadingSpinner />}>
      {children}
    </React.Suspense>
  );
};

const DefaultErrorFallback: React.FC<{ error: Error; retry: () => void }> = ({ 
  error, 
  retry 
}) => (
  <div className="error-fallback">
    <h2>Something went wrong</h2>
    <p>{error.message}</p>
    <button onClick={retry}>Try again</button>
  </div>
);
```

## Code Generation

### GraphQL Code Generation Setup

```bash
npm install --save-dev @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations @graphql-codegen/typescript-react-apollo
```

```yaml
# codegen.yml
overwrite: true
schema: "http://localhost:4000/graphql"
documents: "src/**/*.{ts,tsx}"
generates:
  src/types/generated.ts:
    plugins:
      - "typescript"
      - "typescript-operations"
      - "typescript-react-apollo"
    config:
      withHooks: true
      withComponent: false
      withHOC: false
      apolloReactHooksImportFrom: "@apollo/client"
      scalars:
        DateTime: string
        Upload: File
```

```typescript
// Generated types usage
import { 
  useGetUsersQuery, 
  useCreateUserMutation,
  GetUsersDocument,
  User,
  CreateUserInput
} from '../types/generated';

const UserList: React.FC = () => {
  const { data, loading, error } = useGetUsersQuery({
    variables: { limit: 10 },
    errorPolicy: 'all'
  });

  const [createUser] = useCreateUserMutation({
    update(cache, { data }) {
      if (data?.createUser) {
        cache.updateQuery(
          { query: GetUsersDocument },
          (prev) => ({
            users: [data.createUser, ...(prev?.users || [])]
          })
        );
      }
    }
  });

  const handleCreateUser = async (input: CreateUserInput) => {
    try {
      await createUser({ variables: { input } });
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  return (
    <div>
      {/* Component implementation */}
    </div>
  );
};
```

## Testing GraphQL

### Mocking Apollo Client

```typescript
// __tests__/utils/apollo-mock.ts
import { MockedProvider } from '@apollo/client/testing';
import { InMemoryCache } from '@apollo/client';

export const createMockApolloProvider = (mocks: any[] = []) => {
  return ({ children }: { children: React.ReactNode }) => (
    <MockedProvider 
      mocks={mocks} 
      cache={new InMemoryCache()}
      addTypename={false}
    >
      {children}
    </MockedProvider>
  );
};

// Test mocks
export const userMocks = {
  getUserQuery: {
    request: {
      query: GET_USER_DETAIL,
      variables: { id: '1' }
    },
    result: {
      data: {
        user: {
          id: '1',
          name: 'John Doe',
          email: 'john@example.com',
          bio: 'Test user',
          avatar: 'avatar.jpg',
          posts: [],
          followers: [],
          following: []
        }
      }
    }
  },
  
  createUserMutation: {
    request: {
      query: CREATE_USER,
      variables: {
        input: {
          name: 'Jane Doe',
          email: 'jane@example.com'
        }
      }
    },
    result: {
      data: {
        createUser: {
          id: '2',
          name: 'Jane Doe',
          email: 'jane@example.com',
          bio: null,
          avatar: null,
          createdAt: '2023-01-01T00:00:00Z'
        }
      }
    }
  }
};
```

### Component Testing

```typescript
// __tests__/components/UserList.test.tsx
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { UserList } from '../components/UserList';
import { createMockApolloProvider, userMocks } from './utils/apollo-mock';

describe('UserList', () => {
  it('renders users successfully', async () => {
    const MockProvider = createMockApolloProvider([userMocks.getUsersQuery]);
    
    render(
      <MockProvider>
        <UserList />
      </MockProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('handles create user mutation', async () => {
    const MockProvider = createMockApolloProvider([
      userMocks.getUsersQuery,
      userMocks.createUserMutation
    ]);
    
    render(
      <MockProvider>
        <UserList />
      </MockProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Add User'));
    
    await waitFor(() => {
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    });
  });

  it('handles errors gracefully', async () => {
    const errorMock = {
      ...userMocks.getUsersQuery,
      error: new Error('Network error')
    };
    
    const MockProvider = createMockApolloProvider([errorMock]);
    
    render(
      <MockProvider>
        <UserList />
      </MockProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

### Integration Testing

```typescript
// __tests__/integration/user-flow.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../App';
import { server } from './mocks/server';

// MSW setup for integration tests
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const graphqlHandler = rest.post('/graphql', (req, res, ctx) => {
  const { query, variables } = req.body as any;
  
  if (query.includes('GetUsers')) {
    return res(
      ctx.json({
        data: {
          users: [
            { id: '1', name: 'John Doe', email: 'john@example.com' }
          ]
        }
      })
    );
  }
  
  if (query.includes('CreateUser')) {
    return res(
      ctx.json({
        data: {
          createUser: {
            id: '2',
            name: variables.input.name,
            email: variables.input.email
          }
        }
      })
    );
  }
});

const server = setupServer(graphqlHandler);

describe('User Management Flow', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('completes full user creation flow', async () => {
    const user = userEvent.setup();
    
    render(<App />);

    // Navigate to users page
    await user.click(screen.getByText('Users'));

    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Open create user form
    await user.click(screen.getByText('Add User'));

    // Fill form
    await user.type(screen.getByLabelText(/name/i), 'Jane Doe');
    await user.type(screen.getByLabelText(/email/i), 'jane@example.com');

    // Submit form
    await user.click(screen.getByText('Create User'));

    // Verify success
    await waitFor(() => {
      expect(screen.getByText('User created successfully')).toBeInTheDocument();
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    });
  });
});
```

## Performance Optimization

### Query Optimization

```typescript
// hooks/useOptimizedQueries.ts
import { useQuery, useMemo } from '@apollo/client';

// Field selection optimization
const USER_FIELDS = {
  minimal: `
    id
    name
    avatar
  `,
  standard: `
    id
    name
    email
    avatar
    bio
  `,
  detailed: `
    id
    name
    email
    avatar
    bio
    createdAt
    updatedAt
    posts {
      id
      title
      createdAt
    }
  `
};

export const useOptimizedUserQuery = (
  userId: string, 
  level: keyof typeof USER_FIELDS = 'standard'
) => {
  const query = useMemo(() => gql`
    query GetUser($id: ID!) {
      user(id: $id) {
        ${USER_FIELDS[level]}
      }
    }
  `, [level]);

  return useQuery(query, {
    variables: { id: userId },
    skip: !userId
  });
};

// Pagination optimization
export const useInfiniteScroll = <T>(
  query: any,
  variables: any = {},
  options: {
    pageSize?: number;
    getKey?: (item: T) => string;
  } = {}
) => {
  const { pageSize = 20, getKey = (item: any) => item.id } = options;
  const [hasMore, setHasMore] = useState(true);

  const { data, loading, error, fetchMore } = useQuery(query, {
    variables: { ...variables, limit: pageSize, offset: 0 },
    notifyOnNetworkStatusChange: true
  });

  const loadMore = useCallback(() => {
    if (!loading && hasMore && data) {
      fetchMore({
        variables: {
          offset: data.items?.length || 0
        },
        updateQuery: (prev, { fetchMoreResult }) => {
          if (!fetchMoreResult || fetchMoreResult.items.length === 0) {
            setHasMore(false);
            return prev;
          }

          return {
            ...prev,
            items: [...(prev.items || []), ...fetchMoreResult.items]
          };
        }
      });
    }
  }, [loading, hasMore, data, fetchMore]);

  return {
    items: data?.items || [],
    loading,
    error,
    loadMore,
    hasMore
  };
};
```

### Cache Optimization

```typescript
// utils/cacheOptimization.ts
export const createOptimizedCache = () => {
  return new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          posts: {
            keyArgs: ['filter'],
            merge(existing = [], incoming, { args }) {
              // Implement smart merging based on pagination strategy
              if (args?.offset === 0) {
                return incoming; // Fresh fetch
              }
              return [...existing, ...incoming]; // Append for pagination
            }
          }
        }
      },
      User: {
        fields: {
          posts: relayStylePagination() // Use Relay-style pagination
        }
      }
    },
    possibleTypes: {
      // Define possible types for union/interface types
      Node: ['User', 'Post', 'Comment']
    }
  });
};

// Cache warming strategies
export const warmCache = async (client: ApolloClient<any>) => {
  // Prefetch critical data
  await Promise.all([
    client.query({ query: GET_CURRENT_USER }),
    client.query({ query: GET_APP_CONFIG }),
    client.query({ query: GET_POPULAR_POSTS, variables: { limit: 5 } })
  ]);
};

// Cache persistence
export const createPersistedCache = () => {
  const cache = createOptimizedCache();

  // Save cache to localStorage periodically
  setInterval(() => {
    try {
      const cacheData = cache.extract();
      localStorage.setItem('apollo-cache', JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Failed to persist cache:', error);
    }
  }, 30000); // Every 30 seconds

  // Restore cache on initialization
  try {
    const cachedData = localStorage.getItem('apollo-cache');
    if (cachedData) {
      cache.restore(JSON.parse(cachedData));
    }
  } catch (error) {
    console.warn('Failed to restore cache:', error);
  }

  return cache;
};
```

## Advanced Patterns

### GraphQL with TypeScript

```typescript
// types/schema.ts
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  bio?: string;
  posts: Post[];
  followers: User[];
  following: User[];
  createdAt: string;
  updatedAt: string;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  excerpt: string;
  author: User;
  comments: Comment[];
  likes: Like[];
  tags: Tag[];
  createdAt: string;
  updatedAt: string;
}

export interface QueryResult<T> {
  data: T;
  loading: boolean;
  error?: ApolloError;
  refetch: () => void;
}

// Typed hooks
export const useTypedQuery = <T, V = {}>(
  query: DocumentNode,
  options?: QueryHookOptions<T, V>
): QueryResult<T> => {
  const { data, loading, error, refetch } = useQuery<T, V>(query, options);
  
  return {
    data: data as T,
    loading,
    error,
    refetch
  };
};

export const useTypedMutation = <T, V = {}>(
  mutation: DocumentNode,
  options?: MutationHookOptions<T, V>
) => {
  return useMutation<T, V>(mutation, options);
};
```

### Composite Components with GraphQL

```typescript
// components/UserProfile/UserProfile.tsx
interface UserProfileProps {
  userId: string;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  return (
    <div className="user-profile">
      <UserInfo userId={userId} />
      <UserStats userId={userId} />
      <UserPosts userId={userId} />
    </div>
  );
};

// components/UserProfile/UserInfo.tsx
const UserInfo: React.FC<{ userId: string }> = ({ userId }) => {
  const { data, loading, error } = useQuery(GET_USER_INFO, {
    variables: { id: userId }
  });

  if (loading) return <UserInfoSkeleton />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="user-info">
      <img src={data.user.avatar} alt={data.user.name} />
      <h1>{data.user.name}</h1>
      <p>{data.user.bio}</p>
    </div>
  );
};

// components/UserProfile/UserStats.tsx
const UserStats: React.FC<{ userId: string }> = ({ userId }) => {
  const { data } = useQuery(GET_USER_STATS, {
    variables: { id: userId }
  });

  return (
    <div className="user-stats">
      <StatItem label="Posts" count={data?.user.postsCount || 0} />
      <StatItem label="Followers" count={data?.user.followersCount || 0} />
      <StatItem label="Following" count={data?.user.followingCount || 0} />
    </div>
  );
};

// Export composed component
export { UserProfile };
```

### Error Recovery and Retry Logic

```typescript
// utils/errorRecovery.ts
import { ApolloLink, Observable } from '@apollo/client';

export const createRetryLink = () => {
  return new ApolloLink((operation, forward) => {
    return new Observable(observer => {
      let retryCount = 0;
      const maxRetries = 3;
      
      const handleRetry = () => {
        retryCount++;
        
        const subscription = forward(operation).subscribe({
          next: observer.next.bind(observer),
          error: (error) => {
            if (retryCount < maxRetries && isRetryableError(error)) {
              setTimeout(handleRetry, Math.pow(2, retryCount) * 1000);
            } else {
              observer.error(error);
            }
          },
          complete: observer.complete.bind(observer)
        });
        
        return () => subscription.unsubscribe();
      };
      
      return handleRetry();
    });
  });
};

const isRetryableError = (error: any): boolean => {
  // Network errors
  if (error.networkError) {
    const statusCode = error.networkError.statusCode;
    return statusCode >= 500 || statusCode === 408 || statusCode === 429;
  }
  
  // GraphQL errors that might be transient
  if (error.graphQLErrors) {
    return error.graphQLErrors.some((gqlError: any) => 
      gqlError.extensions?.code === 'INTERNAL_SERVER_ERROR'
    );
  }
  
  return false;
};

// Circuit breaker pattern
export class GraphQLCircuitBreaker {
  private failureCount = 0;
  private isOpen = false;
  private lastFailureTime = 0;
  
  constructor(
    private threshold = 5,
    private timeout = 60000 // 1 minute
  ) {}
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.isOpen) {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.isOpen = false;
        this.failureCount = 0;
      } else {
        throw new Error('Circuit breaker is open');
      }
    }
    
    try {
      const result = await operation();
      this.failureCount = 0;
      return result;
    } catch (error) {
      this.failureCount++;
      this.lastFailureTime = Date.now();
      
      if (this.failureCount >= this.threshold) {
        this.isOpen = true;
      }
      
      throw error;
    }
  }
}
```

This comprehensive guide covers GraphQL and Apollo Client integration in React applications, from basic setup through advanced patterns. Each section includes practical examples and real-world patterns that can be applied in production applications.
