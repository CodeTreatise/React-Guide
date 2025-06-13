# State Machines with XState

## Table of Contents
1. [Introduction to State Machines](#introduction-to-state-machines)
2. [XState Fundamentals](#xstate-fundamentals)
3. [Hierarchical State Machines](#hierarchical-state-machines)
4. [Parallel States](#parallel-states)
5. [State Machine Services](#state-machine-services)
6. [React Integration](#react-integration)
7. [Advanced Patterns](#advanced-patterns)
8. [Testing State Machines](#testing-state-machines)
9. [Performance Optimization](#performance-optimization)
10. [Real-world Examples](#real-world-examples)

## Introduction to State Machines

State machines provide a mathematical model for describing the behavior of systems. They are particularly useful for managing complex state logic in React applications, offering predictable state transitions and clear separation of concerns.

### Benefits of State Machines

```javascript
// Traditional state management challenges
const [isLoading, setIsLoading] = useState(false)
const [data, setData] = useState(null)
const [error, setError] = useState(null)
const [isRetrying, setIsRetrying] = useState(false)

// Problems:
// 1. Invalid states (loading=true, data=present, error=present)
// 2. Missing transitions (how to go from error to loading?)
// 3. Complex logic scattered across components
// 4. Difficult to test and reason about

// State machine approach
const fetchMachine = createMachine({
  id: 'fetch',
  initial: 'idle',
  states: {
    idle: { on: { FETCH: 'loading' } },
    loading: {
      on: {
        SUCCESS: 'success',
        ERROR: 'error',
        CANCEL: 'idle'
      }
    },
    success: { on: { FETCH: 'loading', INVALIDATE: 'idle' } },
    error: { on: { RETRY: 'loading', FETCH: 'loading' } }
  }
})

// Benefits:
// 1. Impossible states are impossible
// 2. Clear, explicit state transitions
// 3. Self-documenting behavior
// 4. Easy to test and visualize
```

## XState Fundamentals

### Basic Machine Definition

```javascript
import { createMachine, assign, interpret } from 'xstate'

// Simple toggle machine
const toggleMachine = createMachine({
  id: 'toggle',
  initial: 'inactive',
  states: {
    inactive: {
      on: {
        TOGGLE: 'active'
      }
    },
    active: {
      on: {
        TOGGLE: 'inactive'
      }
    }
  }
})

// Machine with context (extended state)
const counterMachine = createMachine({
  id: 'counter',
  initial: 'active',
  context: {
    count: 0,
    step: 1
  },
  states: {
    active: {
      on: {
        INCREMENT: {
          actions: assign({
            count: (context) => context.count + context.step
          })
        },
        DECREMENT: {
          actions: assign({
            count: (context) => context.count - context.step
          })
        },
        SET_STEP: {
          actions: assign({
            step: (context, event) => event.value
          })
        },
        RESET: {
          actions: assign({
            count: 0
          })
        }
      }
    }
  }
})
```

### Actions and Guards

```javascript
// Machine with actions and guards
const userMachine = createMachine({
  id: 'user',
  initial: 'loggedOut',
  context: {
    user: null,
    error: null,
    attempts: 0
  },
  states: {
    loggedOut: {
      on: {
        LOGIN: {
          target: 'loggingIn',
          actions: assign({
            error: null
          })
        }
      }
    },
    loggingIn: {
      invoke: {
        id: 'login',
        src: 'loginUser',
        onDone: {
          target: 'loggedIn',
          actions: assign({
            user: (context, event) => event.data,
            attempts: 0
          })
        },
        onError: [
          {
            target: 'loggedOut',
            cond: 'maxAttemptsReached',
            actions: assign({
              error: (context, event) => event.data,
              attempts: (context) => context.attempts + 1
            })
          },
          {
            target: 'loggedOut',
            actions: assign({
              error: (context, event) => event.data,
              attempts: (context) => context.attempts + 1
            })
          }
        ]
      }
    },
    loggedIn: {
      on: {
        LOGOUT: {
          target: 'loggedOut',
          actions: assign({
            user: null
          })
        }
      }
    }
  }
}, {
  services: {
    loginUser: async (context, event) => {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event.credentials)
      })
      
      if (!response.ok) {
        throw new Error('Login failed')
      }
      
      return response.json()
    }
  },
  guards: {
    maxAttemptsReached: (context) => context.attempts >= 3
  }
})
```

## Hierarchical State Machines

### Nested States

```javascript
// Complex form state machine with nested states
const formMachine = createMachine({
  id: 'form',
  initial: 'editing',
  context: {
    formData: {},
    errors: {},
    touched: {}
  },
  states: {
    editing: {
      initial: 'idle',
      states: {
        idle: {
          on: {
            CHANGE: {
              actions: assign({
                formData: (context, event) => ({
                  ...context.formData,
                  [event.field]: event.value
                }),
                touched: (context, event) => ({
                  ...context.touched,
                  [event.field]: true
                })
              })
            },
            BLUR: {
              target: 'validating'
            }
          }
        },
        validating: {
          invoke: {
            id: 'validateField',
            src: 'validateField',
            onDone: {
              target: 'idle',
              actions: assign({
                errors: (context, event) => ({
                  ...context.errors,
                  ...event.data
                })
              })
            }
          }
        }
      },
      on: {
        SUBMIT: {
          target: 'submitting',
          cond: 'isFormValid'
        }
      }
    },
    submitting: {
      invoke: {
        id: 'submitForm',
        src: 'submitForm',
        onDone: {
          target: 'success'
        },
        onError: {
          target: 'editing',
          actions: assign({
            errors: (context, event) => ({
              _form: event.data.message
            })
          })
        }
      }
    },
    success: {
      type: 'final'
    }
  }
}, {
  services: {
    validateField: async (context, event) => {
      // Field validation logic
      const errors = {}
      const { field, value } = event
      
      if (field === 'email' && !value.includes('@')) {
        errors.email = 'Invalid email format'
      }
      
      return errors
    },
    submitForm: async (context) => {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context.formData)
      })
      
      if (!response.ok) {
        throw new Error('Submission failed')
      }
      
      return response.json()
    }
  },
  guards: {
    isFormValid: (context) => Object.keys(context.errors).length === 0
  }
})
```

### History States

```javascript
// Machine with history states
const mediaPlayerMachine = createMachine({
  id: 'mediaPlayer',
  initial: 'stopped',
  states: {
    stopped: {
      on: {
        PLAY: 'playing'
      }
    },
    playing: {
      initial: 'normal',
      states: {
        normal: {
          on: {
            FAST_FORWARD: 'fastForward',
            REWIND: 'rewind'
          }
        },
        fastForward: {
          on: {
            NORMAL: 'normal',
            REWIND: 'rewind'
          }
        },
        rewind: {
          on: {
            NORMAL: 'normal',
            FAST_FORWARD: 'fastForward'
          }
        },
        // History state - remembers the last child state
        hist: {
          type: 'history',
          history: 'shallow'
        }
      },
      on: {
        PAUSE: 'paused',
        STOP: 'stopped'
      }
    },
    paused: {
      on: {
        PLAY: 'playing.hist', // Resume at last playing state
        STOP: 'stopped'
      }
    }
  }
})
```

## Parallel States

### Concurrent State Management

```javascript
// Machine with parallel regions
const appMachine = createMachine({
  id: 'app',
  type: 'parallel',
  states: {
    // Authentication state
    auth: {
      initial: 'checkingAuth',
      states: {
        checkingAuth: {
          invoke: {
            id: 'checkAuth',
            src: 'checkAuthentication',
            onDone: [
              {
                target: 'authenticated',
                cond: 'isAuthenticated'
              },
              {
                target: 'unauthenticated'
              }
            ]
          }
        },
        authenticated: {
          on: {
            LOGOUT: 'unauthenticated'
          }
        },
        unauthenticated: {
          on: {
            LOGIN: 'checkingAuth'
          }
        }
      }
    },
    
    // Theme state
    theme: {
      initial: 'light',
      states: {
        light: {
          on: {
            TOGGLE_THEME: 'dark'
          }
        },
        dark: {
          on: {
            TOGGLE_THEME: 'light'
          }
        }
      }
    },
    
    // Network state
    network: {
      initial: 'checking',
      states: {
        checking: {
          invoke: {
            id: 'checkNetwork',
            src: 'checkNetworkStatus',
            onDone: [
              {
                target: 'online',
                cond: (context, event) => event.data.online
              },
              {
                target: 'offline'
              }
            ]
          }
        },
        online: {
          after: {
            30000: 'checking' // Recheck every 30 seconds
          }
        },
        offline: {
          after: {
            5000: 'checking' // Recheck every 5 seconds when offline
          }
        }
      }
    }
  }
}, {
  services: {
    checkAuthentication: async () => {
      const token = localStorage.getItem('authToken')
      if (!token) return { authenticated: false }
      
      const response = await fetch('/api/verify-token', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      return { authenticated: response.ok }
    },
    checkNetworkStatus: async () => {
      try {
        await fetch('/api/ping')
        return { online: true }
      } catch {
        return { online: false }
      }
    }
  },
  guards: {
    isAuthenticated: (context, event) => event.data.authenticated
  }
})
```

## State Machine Services

### Invoking Services

```javascript
// Data fetching machine with services
const dataFetchMachine = createMachine({
  id: 'dataFetch',
  initial: 'idle',
  context: {
    data: null,
    error: null,
    retryCount: 0
  },
  states: {
    idle: {
      on: {
        FETCH: 'loading'
      }
    },
    loading: {
      invoke: {
        id: 'fetchData',
        src: 'fetchDataService',
        onDone: {
          target: 'success',
          actions: assign({
            data: (context, event) => event.data,
            error: null,
            retryCount: 0
          })
        },
        onError: [
          {
            target: 'retrying',
            cond: 'shouldRetry',
            actions: assign({
              error: (context, event) => event.data,
              retryCount: (context) => context.retryCount + 1
            })
          },
          {
            target: 'failure',
            actions: assign({
              error: (context, event) => event.data
            })
          }
        ]
      },
      on: {
        CANCEL: 'idle'
      }
    },
    success: {
      on: {
        FETCH: 'loading',
        INVALIDATE: 'idle'
      }
    },
    failure: {
      on: {
        RETRY: 'loading',
        FETCH: 'loading'
      }
    },
    retrying: {
      after: {
        2000: 'loading' // Retry after 2 seconds
      },
      on: {
        CANCEL: 'idle'
      }
    }
  }
}, {
  services: {
    fetchDataService: async (context, event) => {
      const controller = new AbortController()
      
      // Store controller for potential cancellation
      context.abortController = controller
      
      const response = await fetch(event.url, {
        signal: controller.signal
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      return response.json()
    }
  },
  guards: {
    shouldRetry: (context) => context.retryCount < 3
  }
})
```

### Actor Communication

```javascript
// Parent machine that spawns child actors
const chatMachine = createMachine({
  id: 'chat',
  initial: 'connecting',
  context: {
    rooms: {},
    currentRoom: null
  },
  states: {
    connecting: {
      invoke: {
        id: 'websocket',
        src: 'websocketService'
      },
      on: {
        CONNECTED: 'connected'
      }
    },
    connected: {
      on: {
        JOIN_ROOM: {
          actions: assign({
            rooms: (context, event) => ({
              ...context.rooms,
              [event.roomId]: spawn(roomMachine.withContext({
                roomId: event.roomId,
                messages: []
              }))
            }),
            currentRoom: (context, event) => event.roomId
          })
        },
        LEAVE_ROOM: {
          actions: assign({
            rooms: (context, event) => {
              const { [event.roomId]: removed, ...rest } = context.rooms
              return rest
            },
            currentRoom: null
          })
        },
        MESSAGE_RECEIVED: {
          actions: (context, event) => {
            const room = context.rooms[event.roomId]
            if (room) {
              room.send({
                type: 'ADD_MESSAGE',
                message: event.message
              })
            }
          }
        }
      }
    }
  }
})

// Child room machine
const roomMachine = createMachine({
  id: 'room',
  initial: 'active',
  context: {
    roomId: null,
    messages: [],
    typing: []
  },
  states: {
    active: {
      on: {
        ADD_MESSAGE: {
          actions: assign({
            messages: (context, event) => [
              ...context.messages,
              event.message
            ]
          })
        },
        USER_TYPING: {
          actions: assign({
            typing: (context, event) => [
              ...context.typing.filter(user => user !== event.user),
              event.user
            ]
          })
        },
        USER_STOPPED_TYPING: {
          actions: assign({
            typing: (context, event) => 
              context.typing.filter(user => user !== event.user)
          })
        }
      }
    }
  }
})
```

## React Integration

### Using XState with React

```javascript
import { useMachine, useActor } from '@xstate/react'

// Basic machine usage in React
function ToggleButton() {
  const [state, send] = useMachine(toggleMachine)

  return (
    <button
      onClick={() => send('TOGGLE')}
      className={state.matches('active') ? 'active' : 'inactive'}
    >
      {state.matches('active') ? 'On' : 'Off'}
    </button>
  )
}

// Complex form component
function UserForm() {
  const [state, send] = useMachine(formMachine)
  
  const { formData, errors, touched } = state.context
  const isSubmitting = state.matches('submitting')
  const isSuccess = state.matches('success')

  const handleChange = (field, value) => {
    send({ type: 'CHANGE', field, value })
  }

  const handleBlur = (field) => {
    send({ type: 'BLUR', field })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    send('SUBMIT')
  }

  if (isSuccess) {
    return <div>Form submitted successfully!</div>
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          type="email"
          value={formData.email || ''}
          onChange={(e) => handleChange('email', e.target.value)}
          onBlur={() => handleBlur('email')}
          placeholder="Email"
        />
        {touched.email && errors.email && (
          <span className="error">{errors.email}</span>
        )}
      </div>

      <div>
        <input
          type="text"
          value={formData.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          onBlur={() => handleBlur('name')}
          placeholder="Name"
        />
        {touched.name && errors.name && (
          <span className="error">{errors.name}</span>
        )}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>

      {errors._form && (
        <div className="error">{errors._form}</div>
      )}
    </form>
  )
}

// Data fetching component
function DataList({ url }) {
  const [state, send] = useMachine(dataFetchMachine)
  
  const { data, error, retryCount } = state.context
  const isLoading = state.matches('loading')
  const isRetrying = state.matches('retrying')

  useEffect(() => {
    send({ type: 'FETCH', url })
  }, [url, send])

  const handleRetry = () => {
    send('RETRY')
  }

  const handleCancel = () => {
    send('CANCEL')
  }

  if (isLoading || isRetrying) {
    return (
      <div>
        {isRetrying ? `Retrying... (${retryCount}/3)` : 'Loading...'}
        <button onClick={handleCancel}>Cancel</button>
      </div>
    )
  }

  if (state.matches('failure')) {
    return (
      <div>
        <p>Error: {error.message}</p>
        <button onClick={handleRetry}>Retry</button>
      </div>
    )
  }

  if (state.matches('success') && data) {
    return (
      <ul>
        {data.map(item => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    )
  }

  return <div>No data</div>
}
```

### Custom Hooks with State Machines

```javascript
// Custom hook for authentication
function useAuth() {
  const [state, send] = useMachine(userMachine)
  
  const login = useCallback((credentials) => {
    send({ type: 'LOGIN', credentials })
  }, [send])

  const logout = useCallback(() => {
    send('LOGOUT')
  }, [send])

  return {
    user: state.context.user,
    isAuthenticated: state.matches('loggedIn'),
    isLoggingIn: state.matches('loggingIn'),
    error: state.context.error,
    attempts: state.context.attempts,
    login,
    logout
  }
}

// Custom hook for paginated data
function usePaginatedData(fetchFn, pageSize = 10) {
  const paginationMachine = useMemo(() => createMachine({
    id: 'pagination',
    initial: 'idle',
    context: {
      items: [],
      page: 1,
      pageSize,
      totalCount: 0,
      hasMore: true
    },
    states: {
      idle: {
        on: {
          LOAD_FIRST_PAGE: 'loadingFirstPage',
          LOAD_MORE: 'loadingMore'
        }
      },
      loadingFirstPage: {
        invoke: {
          id: 'loadFirstPage',
          src: 'loadPage',
          onDone: {
            target: 'loaded',
            actions: assign({
              items: (context, event) => event.data.items,
              totalCount: (context, event) => event.data.totalCount,
              hasMore: (context, event) => 
                event.data.items.length === context.pageSize
            })
          },
          onError: {
            target: 'error',
            actions: assign({
              error: (context, event) => event.data
            })
          }
        }
      },
      loadingMore: {
        invoke: {
          id: 'loadMore',
          src: 'loadPage',
          onDone: {
            target: 'loaded',
            actions: assign({
              items: (context, event) => [...context.items, ...event.data.items],
              page: (context) => context.page + 1,
              hasMore: (context, event) => 
                event.data.items.length === context.pageSize
            })
          },
          onError: {
            target: 'error',
            actions: assign({
              error: (context, event) => event.data
            })
          }
        }
      },
      loaded: {
        on: {
          LOAD_MORE: {
            target: 'loadingMore',
            cond: 'hasMore'
          },
          REFRESH: 'loadingFirstPage'
        }
      },
      error: {
        on: {
          RETRY: 'loadingFirstPage'
        }
      }
    }
  }, {
    services: {
      loadPage: async (context) => {
        return fetchFn(context.page, context.pageSize)
      }
    },
    guards: {
      hasMore: (context) => context.hasMore
    }
  }), [fetchFn, pageSize])

  const [state, send] = useMachine(paginationMachine)

  const loadFirstPage = useCallback(() => {
    send('LOAD_FIRST_PAGE')
  }, [send])

  const loadMore = useCallback(() => {
    send('LOAD_MORE')
  }, [send])

  const refresh = useCallback(() => {
    send('REFRESH')
  }, [send])

  return {
    items: state.context.items,
    isLoading: state.matches('loadingFirstPage'),
    isLoadingMore: state.matches('loadingMore'),
    hasMore: state.context.hasMore,
    error: state.context.error,
    loadFirstPage,
    loadMore,
    refresh
  }
}
```

## Advanced Patterns

### State Machine Composition

```javascript
// Composable machines
const createCRUDMachine = (entityName, apiService) => {
  return createMachine({
    id: `${entityName}CRUD`,
    initial: 'idle',
    context: {
      items: [],
      selectedItem: null,
      error: null
    },
    states: {
      idle: {
        on: {
          LOAD: 'loading',
          CREATE: 'creating',
          EDIT: {
            target: 'editing',
            actions: assign({
              selectedItem: (context, event) => event.item
            })
          },
          DELETE: {
            target: 'deleting',
            actions: assign({
              selectedItem: (context, event) => event.item
            })
          }
        }
      },
      loading: {
        invoke: {
          id: 'loadItems',
          src: 'loadItems',
          onDone: {
            target: 'idle',
            actions: assign({
              items: (context, event) => event.data
            })
          },
          onError: {
            target: 'idle',
            actions: assign({
              error: (context, event) => event.data
            })
          }
        }
      },
      creating: {
        invoke: {
          id: 'createItem',
          src: 'createItem',
          onDone: {
            target: 'idle',
            actions: assign({
              items: (context, event) => [...context.items, event.data]
            })
          },
          onError: {
            target: 'idle',
            actions: assign({
              error: (context, event) => event.data
            })
          }
        }
      },
      editing: {
        invoke: {
          id: 'updateItem',
          src: 'updateItem',
          onDone: {
            target: 'idle',
            actions: assign({
              items: (context, event) => 
                context.items.map(item =>
                  item.id === event.data.id ? event.data : item
                ),
              selectedItem: null
            })
          },
          onError: {
            target: 'idle',
            actions: assign({
              error: (context, event) => event.data,
              selectedItem: null
            })
          }
        }
      },
      deleting: {
        invoke: {
          id: 'deleteItem',
          src: 'deleteItem',
          onDone: {
            target: 'idle',
            actions: assign({
              items: (context, event) => 
                context.items.filter(item => item.id !== context.selectedItem.id),
              selectedItem: null
            })
          },
          onError: {
            target: 'idle',
            actions: assign({
              error: (context, event) => event.data,
              selectedItem: null
            })
          }
        }
      }
    }
  }, {
    services: {
      loadItems: apiService.getAll,
      createItem: (context, event) => apiService.create(event.data),
      updateItem: (context, event) => apiService.update(context.selectedItem.id, event.data),
      deleteItem: (context) => apiService.delete(context.selectedItem.id)
    }
  })
}

// Usage
const userCRUDMachine = createCRUDMachine('user', userApiService)
const postCRUDMachine = createCRUDMachine('post', postApiService)
```

### State Chart Patterns

```javascript
// Complex workflow state machine
const approvalWorkflowMachine = createMachine({
  id: 'approvalWorkflow',
  initial: 'draft',
  context: {
    document: null,
    reviewers: [],
    comments: [],
    currentReviewer: 0
  },
  states: {
    draft: {
      on: {
        SUBMIT_FOR_REVIEW: {
          target: 'pendingReview',
          cond: 'hasReviewers',
          actions: assign({
            currentReviewer: 0
          })
        }
      }
    },
    pendingReview: {
      initial: 'awaitingReview',
      states: {
        awaitingReview: {
          after: {
            // Auto-escalate after 7 days
            604800000: 'escalated'
          },
          on: {
            APPROVE: {
              target: 'processing',
              actions: 'recordApproval'
            },
            REJECT: {
              target: '#approvalWorkflow.draft',
              actions: 'recordRejection'
            },
            REQUEST_CHANGES: {
              target: '#approvalWorkflow.changesRequested',
              actions: 'recordChangeRequest'
            }
          }
        },
        escalated: {
          on: {
            ASSIGN_NEW_REVIEWER: {
              target: 'awaitingReview',
              actions: assign({
                currentReviewer: (context, event) => event.reviewerIndex
              })
            }
          }
        },
        processing: {
          always: [
            {
              target: '#approvalWorkflow.approved',
              cond: 'allReviewersApproved'
            },
            {
              target: 'awaitingReview',
              actions: assign({
                currentReviewer: (context) => context.currentReviewer + 1
              })
            }
          ]
        }
      }
    },
    changesRequested: {
      on: {
        MAKE_CHANGES: {
          target: 'draft',
          actions: 'resetReviewProcess'
        }
      }
    },
    approved: {
      type: 'final',
      entry: 'notifyApproval'
    }
  }
}, {
  actions: {
    recordApproval: assign({
      comments: (context, event) => [
        ...context.comments,
        {
          type: 'approval',
          reviewer: context.reviewers[context.currentReviewer],
          timestamp: Date.now(),
          comment: event.comment
        }
      ]
    }),
    recordRejection: assign({
      comments: (context, event) => [
        ...context.comments,
        {
          type: 'rejection',
          reviewer: context.reviewers[context.currentReviewer],
          timestamp: Date.now(),
          comment: event.comment
        }
      ]
    }),
    recordChangeRequest: assign({
      comments: (context, event) => [
        ...context.comments,
        {
          type: 'changeRequest',
          reviewer: context.reviewers[context.currentReviewer],
          timestamp: Date.now(),
          comment: event.comment
        }
      ]
    }),
    resetReviewProcess: assign({
      currentReviewer: 0,
      comments: []
    }),
    notifyApproval: (context) => {
      // Send notifications
      console.log('Document approved:', context.document.id)
    }
  },
  guards: {
    hasReviewers: (context) => context.reviewers.length > 0,
    allReviewersApproved: (context) => {
      const approvals = context.comments.filter(c => c.type === 'approval')
      return approvals.length === context.reviewers.length
    }
  }
})
```

## Testing State Machines

### Unit Testing

```javascript
import { createMachine, interpret } from 'xstate'

describe('Toggle Machine', () => {
  let toggleService

  beforeEach(() => {
    toggleService = interpret(toggleMachine)
    toggleService.start()
  })

  afterEach(() => {
    toggleService.stop()
  })

  it('should start in inactive state', () => {
    expect(toggleService.state.value).toBe('inactive')
  })

  it('should transition to active when toggled', () => {
    toggleService.send('TOGGLE')
    expect(toggleService.state.value).toBe('active')
  })

  it('should toggle back to inactive', () => {
    toggleService.send('TOGGLE')
    toggleService.send('TOGGLE')
    expect(toggleService.state.value).toBe('inactive')
  })
})

// Testing with context
describe('Counter Machine', () => {
  it('should increment count', () => {
    const counterService = interpret(counterMachine)
    counterService.start()

    expect(counterService.state.context.count).toBe(0)

    counterService.send('INCREMENT')
    expect(counterService.state.context.count).toBe(1)

    counterService.send('INCREMENT')
    expect(counterService.state.context.count).toBe(2)

    counterService.stop()
  })

  it('should set custom step', () => {
    const counterService = interpret(counterMachine)
    counterService.start()

    counterService.send({ type: 'SET_STEP', value: 5 })
    counterService.send('INCREMENT')

    expect(counterService.state.context.count).toBe(5)
    counterService.stop()
  })
})

// Testing async machines
describe('Data Fetch Machine', () => {
  const mockFetch = jest.fn()

  const testMachine = dataFetchMachine.withConfig({
    services: {
      fetchDataService: mockFetch
    }
  })

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should handle successful fetch', async () => {
    const mockData = { id: 1, name: 'Test' }
    mockFetch.mockResolvedValue(mockData)

    const service = interpret(testMachine)
    service.start()

    service.send({ type: 'FETCH', url: '/api/test' })

    // Wait for async operation
    await new Promise(resolve => {
      service.onTransition(state => {
        if (state.matches('success')) {
          expect(state.context.data).toEqual(mockData)
          expect(mockFetch).toHaveBeenCalledWith(
            expect.objectContaining({ url: '/api/test' }),
            expect.any(Object)
          )
          resolve()
        }
      })
    })

    service.stop()
  })

  it('should handle fetch error with retry', async () => {
    const mockError = new Error('Network error')
    mockFetch.mockRejectedValue(mockError)

    const service = interpret(testMachine)
    service.start()

    service.send({ type: 'FETCH', url: '/api/test' })

    await new Promise(resolve => {
      service.onTransition(state => {
        if (state.matches('retrying')) {
          expect(state.context.error).toEqual(mockError)
          expect(state.context.retryCount).toBe(1)
          resolve()
        }
      })
    })

    service.stop()
  })
})
```

### Integration Testing with React

```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { interpret } from 'xstate'

// Test component
function TestFormComponent() {
  const [state, send] = useMachine(formMachine)
  
  return (
    <form onSubmit={(e) => { e.preventDefault(); send('SUBMIT') }}>
      <input
        data-testid="email-input"
        type="email"
        onChange={(e) => send({ type: 'CHANGE', field: 'email', value: e.target.value })}
      />
      <button type="submit" data-testid="submit-button">
        Submit
      </button>
      {state.matches('success') && (
        <div data-testid="success-message">Success!</div>
      )}
    </form>
  )
}

describe('Form Component', () => {
  it('should submit form successfully', async () => {
    render(<TestFormComponent />)
    
    const emailInput = screen.getByTestId('email-input')
    const submitButton = screen.getByTestId('submit-button')
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByTestId('success-message')).toBeInTheDocument()
    })
  })
})
```

## Performance Optimization

### Memoization and State Selection

```javascript
// Optimized React component with state selection
function OptimizedComponent() {
  const [state, send] = useMachine(complexMachine)
  
  // Select only needed state slices
  const isLoading = useMemo(() => state.matches('loading'), [state])
  const data = useMemo(() => state.context.data, [state.context.data])
  const error = useMemo(() => state.context.error, [state.context.error])
  
  // Memoize event handlers
  const handleRefresh = useCallback(() => {
    send('REFRESH')
  }, [send])
  
  return (
    <div>
      {isLoading && <Spinner />}
      {error && <ErrorMessage error={error} />}
      {data && <DataDisplay data={data} />}
      <button onClick={handleRefresh}>Refresh</button>
    </div>
  )
}

// Custom hook for state selection
function useSelector(machine, selector) {
  const [state] = useMachine(machine)
  return useMemo(() => selector(state), [state, selector])
}

// Usage
function ComponentWithSelector() {
  const isLoading = useSelector(dataMachine, state => state.matches('loading'))
  const data = useSelector(dataMachine, state => state.context.data)
  
  return (
    <div>
      {isLoading ? 'Loading...' : JSON.stringify(data)}
    </div>
  )
}
```

### Machine Optimization

```javascript
// Optimized machine with lazy loading
const optimizedMachine = createMachine({
  id: 'optimized',
  initial: 'idle',
  states: {
    idle: {
      on: {
        LOAD: 'loading'
      }
    },
    loading: {
      invoke: {
        id: 'loadData',
        src: 'loadData',
        // Use machine refs for better performance
        onDone: {
          target: 'success',
          actions: assign({
            data: (context, event) => event.data
          })
        }
      }
    },
    success: {
      // Lazy load related data
      invoke: {
        id: 'preloadRelated',
        src: 'preloadRelatedData'
      }
    }
  }
}, {
  services: {
    loadData: async () => {
      // Use dynamic imports for code splitting
      const { heavyDataProcessor } = await import('./heavyDataProcessor')
      return heavyDataProcessor()
    },
    preloadRelatedData: async (context) => {
      // Background preloading
      if (context.data?.relatedIds) {
        return preloadData(context.data.relatedIds)
      }
    }
  }
})
```

## Real-world Examples

### E-commerce Shopping Cart

```javascript
const shoppingCartMachine = createMachine({
  id: 'shoppingCart',
  initial: 'empty',
  context: {
    items: [],
    total: 0,
    discount: 0,
    shippingInfo: null,
    paymentInfo: null
  },
  states: {
    empty: {
      on: {
        ADD_ITEM: {
          target: 'hasItems',
          actions: 'addItem'
        }
      }
    },
    hasItems: {
      on: {
        ADD_ITEM: {
          actions: 'addItem'
        },
        REMOVE_ITEM: [
          {
            target: 'empty',
            cond: 'isLastItem',
            actions: 'removeItem'
          },
          {
            actions: 'removeItem'
          }
        ],
        UPDATE_QUANTITY: {
          actions: 'updateQuantity'
        },
        APPLY_DISCOUNT: {
          actions: 'applyDiscount'
        },
        PROCEED_TO_CHECKOUT: 'checkout'
      }
    },
    checkout: {
      initial: 'shipping',
      states: {
        shipping: {
          on: {
            SET_SHIPPING: {
              target: 'payment',
              actions: assign({
                shippingInfo: (context, event) => event.shippingInfo
              })
            }
          }
        },
        payment: {
          on: {
            SET_PAYMENT: {
              target: 'review',
              actions: assign({
                paymentInfo: (context, event) => event.paymentInfo
              })
            },
            BACK_TO_SHIPPING: 'shipping'
          }
        },
        review: {
          on: {
            CONFIRM_ORDER: 'processing',
            BACK_TO_PAYMENT: 'payment'
          }
        },
        processing: {
          invoke: {
            id: 'processOrder',
            src: 'processOrder',
            onDone: {
              target: '#shoppingCart.completed'
            },
            onError: {
              target: 'review',
              actions: assign({
                error: (context, event) => event.data
              })
            }
          }
        }
      },
      on: {
        BACK_TO_CART: 'hasItems'
      }
    },
    completed: {
      type: 'final'
    }
  }
}, {
  actions: {
    addItem: assign({
      items: (context, event) => {
        const existingItem = context.items.find(item => item.id === event.item.id)
        if (existingItem) {
          return context.items.map(item =>
            item.id === event.item.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          )
        }
        return [...context.items, { ...event.item, quantity: 1 }]
      },
      total: (context, event) => calculateTotal(context.items, context.discount)
    }),
    removeItem: assign({
      items: (context, event) => 
        context.items.filter(item => item.id !== event.itemId),
      total: (context) => calculateTotal(context.items, context.discount)
    }),
    updateQuantity: assign({
      items: (context, event) =>
        context.items.map(item =>
          item.id === event.itemId
            ? { ...item, quantity: event.quantity }
            : item
        ),
      total: (context) => calculateTotal(context.items, context.discount)
    }),
    applyDiscount: assign({
      discount: (context, event) => event.discount,
      total: (context, event) => calculateTotal(context.items, event.discount)
    })
  },
  guards: {
    isLastItem: (context) => context.items.length === 1
  },
  services: {
    processOrder: async (context) => {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: context.items,
          total: context.total,
          shipping: context.shippingInfo,
          payment: context.paymentInfo
        })
      })
      
      if (!response.ok) {
        throw new Error('Order processing failed')
      }
      
      return response.json()
    }
  }
})

function calculateTotal(items, discount) {
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  return subtotal - (subtotal * discount / 100)
}
```

### Media Player

```javascript
const mediaPlayerMachine = createMachine({
  id: 'mediaPlayer',
  initial: 'loading',
  context: {
    currentTime: 0,
    duration: 0,
    volume: 1,
    playbackRate: 1,
    playlist: [],
    currentTrack: 0,
    error: null
  },
  states: {
    loading: {
      invoke: {
        id: 'loadMedia',
        src: 'loadMediaSource',
        onDone: {
          target: 'ready',
          actions: assign({
            duration: (context, event) => event.data.duration
          })
        },
        onError: {
          target: 'error',
          actions: assign({
            error: (context, event) => event.data
          })
        }
      }
    },
    ready: {
      on: {
        PLAY: 'playing',
        SEEK: {
          actions: assign({
            currentTime: (context, event) => event.time
          })
        }
      }
    },
    playing: {
      invoke: {
        id: 'trackProgress',
        src: 'trackPlaybackProgress'
      },
      on: {
        PAUSE: 'paused',
        SEEK: {
          actions: assign({
            currentTime: (context, event) => event.time
          })
        },
        ENDED: {
          target: 'ready',
          actions: 'handleTrackEnd'
        },
        SET_VOLUME: {
          actions: assign({
            volume: (context, event) => Math.max(0, Math.min(1, event.volume))
          })
        },
        SET_PLAYBACK_RATE: {
          actions: assign({
            playbackRate: (context, event) => event.rate
          })
        }
      }
    },
    paused: {
      on: {
        PLAY: 'playing',
        SEEK: {
          actions: assign({
            currentTime: (context, event) => event.time
          })
        }
      }
    },
    error: {
      on: {
        RETRY: 'loading'
      }
    }
  },
  on: {
    NEXT_TRACK: {
      target: 'loading',
      actions: 'nextTrack'
    },
    PREVIOUS_TRACK: {
      target: 'loading',
      actions: 'previousTrack'
    },
    LOAD_PLAYLIST: {
      actions: assign({
        playlist: (context, event) => event.playlist,
        currentTrack: 0
      })
    }
  }
}, {
  actions: {
    handleTrackEnd: (context) => {
      // Auto-advance to next track
      if (context.currentTrack < context.playlist.length - 1) {
        return { type: 'NEXT_TRACK' }
      }
    },
    nextTrack: assign({
      currentTrack: (context) => 
        Math.min(context.currentTrack + 1, context.playlist.length - 1),
      currentTime: 0
    }),
    previousTrack: assign({
      currentTrack: (context) => Math.max(context.currentTrack - 1, 0),
      currentTime: 0
    })
  },
  services: {
    loadMediaSource: async (context) => {
      const track = context.playlist[context.currentTrack]
      const audio = new Audio(track.url)
      
      return new Promise((resolve, reject) => {
        audio.addEventListener('loadedmetadata', () => {
          resolve({ duration: audio.duration })
        })
        audio.addEventListener('error', reject)
        audio.load()
      })
    },
    trackPlaybackProgress: (context) => (callback) => {
      const interval = setInterval(() => {
        callback({
          type: 'UPDATE_PROGRESS',
          currentTime: /* get from audio element */
        })
      }, 1000)
      
      return () => clearInterval(interval)
    }
  }
})
```

## Best Practices

### 1. Machine Design
- Keep states atomic and mutually exclusive
- Use hierarchical states for complex workflows
- Implement proper error handling states
- Design for testability from the start

### 2. Context Management
- Keep context minimal and normalized
- Use actions for all context updates
- Avoid side effects in context updates
- Consider immutability patterns

### 3. Service Integration
- Use services for all async operations
- Implement proper cancellation
- Handle edge cases and timeouts
- Provide meaningful error information

### 4. React Integration
- Use custom hooks for reusable logic
- Minimize re-renders with proper selectors
- Handle cleanup in useEffect
- Consider state persistence needs

### 5. Testing Strategy
- Test state transitions independently
- Mock external services
- Test edge cases and error conditions
- Use integration tests for complex flows

## Conclusion

XState provides a powerful way to manage complex state logic in React applications. By modeling application behavior as state machines, you can create more predictable, testable, and maintainable code.

Key benefits include:
- Elimination of impossible states
- Clear documentation of behavior
- Excellent debugging and visualization tools
- Strong TypeScript support
- Comprehensive testing capabilities

The patterns shown in this guide provide a foundation for building robust state management solutions that scale with your application's complexity.
