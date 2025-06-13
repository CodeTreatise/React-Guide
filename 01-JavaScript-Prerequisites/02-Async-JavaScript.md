# ⚡ Asynchronous JavaScript for React

> **Focus**: Master async programming patterns essential for React data fetching  
> **Time**: 3-4 hours reading + 3-4 hours practice  
> **Difficulty**: Intermediate

---

## 📋 Table of Contents

1. [Understanding Asynchronous JavaScript](#1-understanding-asynchronous-javascript)
2. [Callbacks and Callback Hell](#2-callbacks-and-callback-hell)
3. [Promises](#3-promises)
4. [Async/Await](#4-asyncawait)
5. [Error Handling](#5-error-handling)
6. [React-Specific Async Patterns](#6-react-specific-async-patterns)
7. [Real-World Examples](#7-real-world-examples)

---

## 1. Understanding Asynchronous JavaScript

### The JavaScript Event Loop

JavaScript is **single-threaded** but **non-blocking**. Understanding this is crucial for React development.

```javascript
// Synchronous code (blocking)
console.log('1. First');
console.log('2. Second');
console.log('3. Third');
// Output: 1, 2, 3 (in order)

// Asynchronous code (non-blocking)
console.log('1. First');
setTimeout(() => console.log('2. Second'), 0);
console.log('3. Third');
// Output: 1, 3, 2 (Third runs before Second!)
```

### Call Stack, Web APIs, and Event Loop

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Call Stack    │    │    Web APIs     │    │  Callback Queue │
│                 │    │                 │    │                 │
│  main()         │    │  setTimeout()   │    │  callback()     │
│  console.log()  │    │  fetch()        │    │  promise.then() │
│                 │    │  DOM events     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       │                       │
         │                       ▼                       │
         └───────────────── Event Loop ──────────────────┘
```

### Why Async Matters in React

```javascript
// ❌ This would freeze the UI
const BadComponent = () => {
    const [data, setData] = useState(null);
    
    // This blocks the main thread!
    const heavyComputation = () => {
        let result = 0;
        for (let i = 0; i < 1000000000; i++) {
            result += i;
        }
        return result;
    };
    
    return (
        <div>
            <button onClick={() => setData(heavyComputation())}>
                Calculate (Freezes UI!)
            </button>
            <p>{data}</p>
        </div>
    );
};

// ✅ Better approach with async
const GoodComponent = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const heavyComputationAsync = async () => {
        setLoading(true);
        
        // Use setTimeout to break up the work
        const result = await new Promise(resolve => {
            setTimeout(() => {
                let sum = 0;
                for (let i = 0; i < 1000000000; i++) {
                    sum += i;
                }
                resolve(sum);
            }, 0);
        });
        
        setData(result);
        setLoading(false);
    };
    
    return (
        <div>
            <button onClick={heavyComputationAsync} disabled={loading}>
                {loading ? 'Calculating...' : 'Calculate'}
            </button>
            <p>{data}</p>
        </div>
    );
};
```

---

## 2. Callbacks and Callback Hell

### Understanding Callbacks

```javascript
// Basic callback pattern
function fetchUserData(userId, callback) {
    // Simulate API call
    setTimeout(() => {
        const userData = { id: userId, name: 'John Doe' };
        callback(null, userData); // null for error, userData for success
    }, 1000);
}

// Using the callback
fetchUserData(123, (error, user) => {
    if (error) {
        console.error('Error:', error);
    } else {
        console.log('User:', user);
    }
});
```

### The Callback Hell Problem

```javascript
// ❌ Callback Hell (Pyramid of Doom)
function getUserWithPostsAndComments(userId, callback) {
    fetchUser(userId, (userError, user) => {
        if (userError) {
            callback(userError, null);
            return;
        }
        
        fetchPosts(user.id, (postsError, posts) => {
            if (postsError) {
                callback(postsError, null);
                return;
            }
            
            fetchComments(posts[0].id, (commentsError, comments) => {
                if (commentsError) {
                    callback(commentsError, null);
                    return;
                }
                
                // Finally have all data
                callback(null, { user, posts, comments });
            });
        });
    });
}
```

### Why Callbacks Are Problematic

1. **Nested Structure**: Hard to read and maintain
2. **Error Handling**: Must check errors at every level
3. **No Return Values**: Can't use normal return statements
4. **Difficult Testing**: Hard to unit test nested callbacks

---

## 3. Promises

### Promise Basics

A Promise represents a value that may be available now, in the future, or never.

```javascript
// Creating a Promise
const myPromise = new Promise((resolve, reject) => {
    const success = Math.random() > 0.5;
    
    setTimeout(() => {
        if (success) {
            resolve('Operation succeeded!');
        } else {
            reject(new Error('Operation failed!'));
        }
    }, 1000);
});

// Using a Promise
myPromise
    .then(result => {
        console.log('Success:', result);
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
```

### Promise States

```javascript
// Promise states visualization
const promise = new Promise((resolve, reject) => {
    // Initially: PENDING
    
    setTimeout(() => {
        if (Math.random() > 0.5) {
            resolve('success'); // State becomes: FULFILLED
        } else {
            reject('error');    // State becomes: REJECTED
        }
    }, 1000);
});

console.log(promise); // Promise { <pending> }

promise
    .then(value => console.log('Fulfilled:', value))
    .catch(error => console.log('Rejected:', error));
```

### Chaining Promises

```javascript
// ✅ Solving Callback Hell with Promises
function fetchUser(userId) {
    return fetch(`/api/users/${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function fetchPosts(userId) {
    return fetch(`/api/users/${userId}/posts`)
        .then(response => response.json());
}

function fetchComments(postId) {
    return fetch(`/api/posts/${postId}/comments`)
        .then(response => response.json());
}

// Clean chaining (much better than callback hell)
fetchUser(123)
    .then(user => {
        console.log('User:', user);
        return fetchPosts(user.id);
    })
    .then(posts => {
        console.log('Posts:', posts);
        if (posts.length > 0) {
            return fetchComments(posts[0].id);
        }
        return [];
    })
    .then(comments => {
        console.log('Comments:', comments);
    })
    .catch(error => {
        console.error('Something went wrong:', error);
    });
```

### Promise Utility Methods

```javascript
// Promise.all() - Wait for all promises to resolve
const promise1 = fetch('/api/users');
const promise2 = fetch('/api/posts');
const promise3 = fetch('/api/comments');

Promise.all([promise1, promise2, promise3])
    .then(responses => {
        console.log('All requests completed');
        return Promise.all(responses.map(r => r.json()));
    })
    .then(data => {
        const [users, posts, comments] = data;
        console.log({ users, posts, comments });
    })
    .catch(error => {
        console.error('One or more requests failed:', error);
    });

// Promise.allSettled() - Wait for all promises to settle (ES2020)
Promise.allSettled([promise1, promise2, promise3])
    .then(results => {
        results.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                console.log(`Promise ${index} succeeded:`, result.value);
            } else {
                console.log(`Promise ${index} failed:`, result.reason);
            }
        });
    });

// Promise.race() - First promise to resolve/reject wins
const timeout = new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Timeout')), 5000)
);

Promise.race([fetch('/api/data'), timeout])
    .then(response => response.json())
    .then(data => console.log('Data received in time:', data))
    .catch(error => console.error('Request timed out or failed:', error));
```

---

## 4. Async/Await

### Basic Async/Await Syntax

```javascript
// Promise version
function fetchUserData() {
    return fetch('/api/user')
        .then(response => response.json())
        .then(user => {
            console.log('User:', user);
            return user;
        })
        .catch(error => {
            console.error('Error:', error);
            throw error;
        });
}

// Async/await version (much cleaner!)
async function fetchUserData() {
    try {
        const response = await fetch('/api/user');
        const user = await response.json();
        console.log('User:', user);
        return user;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

### Sequential vs Parallel Execution

```javascript
// Sequential execution (one after another)
async function fetchDataSequentially() {
    console.time('Sequential');
    
    const user = await fetchUser(1);        // Wait 1 second
    const posts = await fetchPosts(1);      // Wait another 1 second
    const comments = await fetchComments(1); // Wait another 1 second
    
    console.timeEnd('Sequential'); // ~3 seconds total
    return { user, posts, comments };
}

// Parallel execution (all at once)
async function fetchDataParallel() {
    console.time('Parallel');
    
    const [user, posts, comments] = await Promise.all([
        fetchUser(1),        // All start at the same time
        fetchPosts(1),
        fetchComments(1)
    ]);
    
    console.timeEnd('Parallel'); // ~1 second total
    return { user, posts, comments };
}

// Mixed approach (when you need data from previous calls)
async function fetchDataMixed() {
    const user = await fetchUser(1);
    
    // These can run in parallel since they both only need user.id
    const [posts, profile] = await Promise.all([
        fetchPosts(user.id),
        fetchUserProfile(user.id)
    ]);
    
    return { user, posts, profile };
}
```

### Advanced Async Patterns

```javascript
// Async loops
async function processUsersSequentially(userIds) {
    const results = [];
    
    for (const id of userIds) {
        const user = await fetchUser(id);
        results.push(user);
    }
    
    return results;
}

async function processUsersParallel(userIds) {
    const promises = userIds.map(id => fetchUser(id));
    return await Promise.all(promises);
}

// Async retry logic
async function fetchWithRetry(url, maxRetries = 3) {
    let lastError;
    
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                return await response.json();
            }
            throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            lastError = error;
            console.log(`Attempt ${i + 1} failed:`, error.message);
            
            if (i < maxRetries - 1) {
                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
            }
        }
    }
    
    throw lastError;
}

// Async timeout
async function fetchWithTimeout(url, timeoutMs = 5000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    
    try {
        const response = await fetch(url, { 
            signal: controller.signal 
        });
        return await response.json();
    } finally {
        clearTimeout(timeoutId);
    }
}
```

---

## 5. Error Handling

### Try-Catch with Async/Await

```javascript
// Basic error handling
async function fetchUserSafely(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        
        if (!response.ok) {
            throw new Error(`User not found: ${response.status}`);
        }
        
        const user = await response.json();
        return user;
    } catch (error) {
        if (error.name === 'TypeError') {
            // Network error
            console.error('Network error:', error.message);
            throw new Error('Unable to connect to server');
        } else {
            // Other errors
            console.error('API error:', error.message);
            throw error;
        }
    }
}

// Multiple error types
async function complexAPICall() {
    try {
        const response = await fetch('/api/complex-operation');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error.message);
        }
        
        return data;
    } catch (error) {
        if (error instanceof TypeError) {
            // Network/fetch errors
            throw new Error('Network connection failed');
        } else if (error.message.includes('401')) {
            // Authentication errors
            throw new Error('Please log in again');
        } else if (error.message.includes('403')) {
            // Permission errors
            throw new Error('You do not have permission');
        } else {
            // Generic errors
            throw new Error(`Operation failed: ${error.message}`);
        }
    }
}
```

### Error Boundaries for Async Operations

```javascript
// Custom hook for safe async operations
function useAsyncOperation() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);
    
    const execute = async (asyncFunction) => {
        try {
            setLoading(true);
            setError(null);
            const result = await asyncFunction();
            setData(result);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };
    
    const reset = () => {
        setLoading(false);
        setError(null);
        setData(null);
    };
    
    return { loading, error, data, execute, reset };
}

// Usage in component
const UserProfile = ({ userId }) => {
    const { loading, error, data: user, execute } = useAsyncOperation();
    
    useEffect(() => {
        execute(() => fetchUser(userId));
    }, [userId]);
    
    if (loading) return <div>Loading user...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!user) return <div>No user found</div>;
    
    return (
        <div>
            <h1>{user.name}</h1>
            <p>{user.email}</p>
        </div>
    );
};
```

---

## 6. React-Specific Async Patterns

### Data Fetching with useEffect

```javascript
// Basic data fetching
const UserComponent = ({ userId }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        let isMounted = true; // Cleanup flag
        
        const fetchUser = async () => {
            try {
                setLoading(true);
                setError(null);
                
                const response = await fetch(`/api/users/${userId}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch user');
                }
                
                const userData = await response.json();
                
                // Only update state if component is still mounted
                if (isMounted) {
                    setUser(userData);
                }
            } catch (err) {
                if (isMounted) {
                    setError(err.message);
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };
        
        fetchUser();
        
        // Cleanup function
        return () => {
            isMounted = false;
        };
    }, [userId]); // Re-fetch when userId changes
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!user) return <div>No user found</div>;
    
    return (
        <div>
            <h1>{user.name}</h1>
            <p>{user.email}</p>
        </div>
    );
};
```

### AbortController for Cleanup

```javascript
const SearchComponent = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    
    useEffect(() => {
        if (!query.trim()) {
            setResults([]);
            return;
        }
        
        const controller = new AbortController();
        
        const searchUsers = async () => {
            try {
                setLoading(true);
                
                const response = await fetch(`/api/search?q=${query}`, {
                    signal: controller.signal
                });
                
                if (!response.ok) {
                    throw new Error('Search failed');
                }
                
                const data = await response.json();
                setResults(data.users);
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error('Search error:', error);
                }
            } finally {
                setLoading(false);
            }
        };
        
        // Debounce search
        const timeoutId = setTimeout(searchUsers, 300);
        
        return () => {
            clearTimeout(timeoutId);
            controller.abort(); // Cancel ongoing request
        };
    }, [query]);
    
    return (
        <div>
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search users..."
            />
            
            {loading && <div>Searching...</div>}
            
            <ul>
                {results.map(user => (
                    <li key={user.id}>{user.name}</li>
                ))}
            </ul>
        </div>
    );
};
```

### Custom Hooks for Async Operations

```javascript
// Generic fetch hook
function useFetch(url, options = {}) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [url, JSON.stringify(options)]);
    
    useEffect(() => {
        fetchData();
    }, [fetchData]);
    
    const refetch = () => fetchData();
    
    return { data, loading, error, refetch };
}

// User-specific hook
function useUser(userId) {
    return useFetch(`/api/users/${userId}`);
}

// Usage in component
const UserProfile = ({ userId }) => {
    const { data: user, loading, error, refetch } = useUser(userId);
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div>
            <h1>{user?.name}</h1>
            <button onClick={refetch}>Refresh</button>
        </div>
    );
};
```

---

## 7. Real-World Examples

### Complete User Management Component

```javascript
const UserManagement = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedUser, setSelectedUser] = useState(null);
    
    // Fetch all users
    const fetchUsers = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await fetch('/api/users');
            if (!response.ok) throw new Error('Failed to fetch users');
            
            const data = await response.json();
            setUsers(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };
    
    // Create new user
    const createUser = async (userData) => {
        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
            
            if (!response.ok) throw new Error('Failed to create user');
            
            const newUser = await response.json();
            setUsers(prev => [...prev, newUser]);
            return newUser;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };
    
    // Update user
    const updateUser = async (userId, updates) => {
        try {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });
            
            if (!response.ok) throw new Error('Failed to update user');
            
            const updatedUser = await response.json();
            setUsers(prev => 
                prev.map(user => 
                    user.id === userId ? updatedUser : user
                )
            );
            return updatedUser;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };
    
    // Delete user
    const deleteUser = async (userId) => {
        if (!confirm('Are you sure you want to delete this user?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete user');
            
            setUsers(prev => prev.filter(user => user.id !== userId));
            if (selectedUser?.id === userId) {
                setSelectedUser(null);
            }
        } catch (err) {
            setError(err.message);
        }
    };
    
    // Load users on component mount
    useEffect(() => {
        fetchUsers();
    }, []);
    
    return (
        <div className="user-management">
            <h1>User Management</h1>
            
            {error && (
                <div className="error">
                    Error: {error}
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}
            
            <div className="actions">
                <button onClick={fetchUsers} disabled={loading}>
                    {loading ? 'Loading...' : 'Refresh Users'}
                </button>
                <button onClick={() => setSelectedUser({})}>
                    Add New User
                </button>
            </div>
            
            <div className="user-list">
                {users.map(user => (
                    <UserCard
                        key={user.id}
                        user={user}
                        onEdit={setSelectedUser}
                        onDelete={deleteUser}
                    />
                ))}
            </div>
            
            {selectedUser && (
                <UserForm
                    user={selectedUser}
                    onSave={selectedUser.id ? updateUser : createUser}
                    onCancel={() => setSelectedUser(null)}
                />
            )}
        </div>
    );
};

// Supporting components
const UserCard = ({ user, onEdit, onDelete }) => (
    <div className="user-card">
        <h3>{user.name}</h3>
        <p>{user.email}</p>
        <div className="actions">
            <button onClick={() => onEdit(user)}>Edit</button>
            <button onClick={() => onDelete(user.id)}>Delete</button>
        </div>
    </div>
);

const UserForm = ({ user, onSave, onCancel }) => {
    const [formData, setFormData] = useState({
        name: user.name || '',
        email: user.email || ''
    });
    const [saving, setSaving] = useState(false);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            setSaving(true);
            
            if (user.id) {
                await onSave(user.id, formData);
            } else {
                await onSave(formData);
            }
            
            onCancel(); // Close form on success
        } catch (err) {
            // Error is handled by parent component
        } finally {
            setSaving(false);
        }
    };
    
    return (
        <form onSubmit={handleSubmit} className="user-form">
            <h2>{user.id ? 'Edit User' : 'Create User'}</h2>
            
            <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="Name"
                required
            />
            
            <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="Email"
                required
            />
            
            <div className="form-actions">
                <button type="submit" disabled={saving}>
                    {saving ? 'Saving...' : 'Save'}
                </button>
                <button type="button" onClick={onCancel}>
                    Cancel
                </button>
            </div>
        </form>
    );
};
```

### Advanced Error Handling with Context

```javascript
// Error context for global error handling
const ErrorContext = createContext();

export const ErrorProvider = ({ children }) => {
    const [errors, setErrors] = useState([]);
    
    const addError = (error) => {
        const errorObj = {
            id: Date.now(),
            message: error.message || error,
            timestamp: new Date().toISOString()
        };
        setErrors(prev => [...prev, errorObj]);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            setErrors(prev => prev.filter(e => e.id !== errorObj.id));
        }, 5000);
    };
    
    const removeError = (id) => {
        setErrors(prev => prev.filter(e => e.id !== id));
    };
    
    return (
        <ErrorContext.Provider value={{ errors, addError, removeError }}>
            {children}
            <ErrorDisplay />
        </ErrorContext.Provider>
    );
};

const ErrorDisplay = () => {
    const { errors, removeError } = useContext(ErrorContext);
    
    return (
        <div className="error-container">
            {errors.map(error => (
                <div key={error.id} className="error-toast">
                    {error.message}
                    <button onClick={() => removeError(error.id)}>×</button>
                </div>
            ))}
        </div>
    );
};

// Custom hook for error handling
export const useErrorHandler = () => {
    const { addError } = useContext(ErrorContext);
    
    const handleAsync = async (asyncFunction) => {
        try {
            return await asyncFunction();
        } catch (error) {
            addError(error);
            throw error;
        }
    };
    
    return { handleAsync };
};

// Usage in components
const MyComponent = () => {
    const { handleAsync } = useErrorHandler();
    const [data, setData] = useState(null);
    
    const fetchData = () => {
        handleAsync(async () => {
            const response = await fetch('/api/data');
            if (!response.ok) throw new Error('Failed to fetch');
            const result = await response.json();
            setData(result);
        });
    };
    
    return (
        <div>
            <button onClick={fetchData}>Fetch Data</button>
            {data && <div>{JSON.stringify(data)}</div>}
        </div>
    );
};
```

---

## 🎯 Practice Exercises

### Exercise 1: Convert Callback to Async/Await
```javascript
// Convert this callback-based code to async/await
function processUserData(userId, callback) {
    fetchUser(userId, (userError, user) => {
        if (userError) {
            callback(userError, null);
            return;
        }
        
        fetchUserPosts(user.id, (postsError, posts) => {
            if (postsError) {
                callback(postsError, null);
                return;
            }
            
            const processedData = {
                user: user,
                postsCount: posts.length,
                latestPost: posts[0] || null
            };
            
            callback(null, processedData);
        });
    });
}
```

### Exercise 2: Build a Search Component
Create a React component that:
1. Debounces search input
2. Cancels previous requests
3. Handles loading and error states
4. Displays search results

### Exercise 3: Implement Retry Logic
Create a function that retries failed API calls with exponential backoff.

---

## ✅ Knowledge Check

Test your understanding:

1. **Event Loop**: Explain why `setTimeout(() => console.log('A'), 0)` runs after synchronous code
2. **Promises vs Callbacks**: What advantages do Promises have over callbacks?
3. **Async/Await**: When would you use `Promise.all()` vs sequential await calls?
4. **Error Handling**: How do you handle errors in async/await vs Promise chains?
5. **React Integration**: Why is cleanup important in useEffect with async operations?

---

## 🚀 Next Steps

You now understand async JavaScript patterns essential for React development. These concepts will be crucial when you start:

- Fetching data in React components
- Handling user interactions
- Managing loading states
- Implementing real-time features

**Next Module**: [React Fundamentals](../02-React-Fundamentals/README.md)

Master these async patterns, and you'll build more robust React applications! 🎯