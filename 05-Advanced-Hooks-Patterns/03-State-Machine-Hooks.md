# State Machine Hooks and Complex Workflows

## Table of Contents
1. [State Machine Fundamentals](#state-machine-fundamentals)
2. [Custom State Machine Hooks](#custom-state-machine-hooks)
3. [Workflow Management Patterns](#workflow-management-patterns)
4. [Complex Form State Machines](#complex-form-state-machines)
5. [Async State Machine Patterns](#async-state-machine-patterns)
6. [Testing State Machines](#testing-state-machines)
7. [Integration with External Libraries](#integration-with-external-libraries)
8. [Real-World Applications](#real-world-applications)
9. [Performance Considerations](#performance-considerations)
10. [Best Practices](#best-practices)

## State Machine Fundamentals

State machines are powerful patterns for managing complex state transitions and ensuring predictable application behavior.

### Basic State Machine Hook

```jsx
// hooks/useStateMachine.js
import { useReducer, useCallback, useMemo } from 'react';

function createStateMachine(config) {
  const { initial, states } = config;
  
  const reducer = (state, action) => {
    const currentState = states[state.value];
    const transition = currentState.on?.[action.type];
    
    if (!transition) {
      console.warn(`No transition for "${action.type}" from state "${state.value}"`);
      return state;
    }
    
    const nextStateValue = typeof transition === 'string' ? transition : transition.target;
    const nextState = states[nextStateValue];
    
    if (!nextState) {
      console.error(`Invalid target state: "${nextStateValue}"`);
      return state;
    }
    
    // Execute exit actions
    if (currentState.exit) {
      currentState.exit(state.context, action);
    }
    
    // Update context
    let newContext = state.context;
    if (typeof transition === 'object' && transition.actions) {
      newContext = transition.actions.reduce((ctx, actionFn) => {
        return actionFn(ctx, action);
      }, state.context);
    }
    
    // Create new state
    const newState = {
      value: nextStateValue,
      context: newContext,
      matches: (value) => value === nextStateValue,
      can: (eventType) => !!nextState.on?.[eventType]
    };
    
    // Execute entry actions
    if (nextState.entry) {
      nextState.entry(newState.context, action);
    }
    
    return newState;
  };
  
  const initialState = {
    value: initial,
    context: config.context || {},
    matches: (value) => value === initial,
    can: (eventType) => !!states[initial].on?.[eventType]
  };
  
  return { reducer, initialState };
}

export function useStateMachine(config) {
  const machine = useMemo(() => createStateMachine(config), []);
  const [state, dispatch] = useReducer(machine.reducer, machine.initialState);
  
  const send = useCallback((event) => {
    const action = typeof event === 'string' ? { type: event } : event;
    dispatch(action);
  }, []);
  
  return [state, send];
}

// Example: Traffic Light State Machine
function useTrafficLight() {
  const config = {
    initial: 'red',
    context: {
      timer: 0,
      emergencyMode: false
    },
    states: {
      red: {
        entry: (context) => console.log('Red light - Stop!'),
        on: {
          TIMER: 'green',
          EMERGENCY: 'emergency'
        }
      },
      yellow: {
        entry: (context) => console.log('Yellow light - Caution!'),
        on: {
          TIMER: 'red',
          EMERGENCY: 'emergency'
        }
      },
      green: {
        entry: (context) => console.log('Green light - Go!'),
        on: {
          TIMER: 'yellow',
          EMERGENCY: 'emergency'
        }
      },
      emergency: {
        entry: (context) => console.log('Emergency mode - All stop!'),
        on: {
          CLEAR_EMERGENCY: 'red'
        }
      }
    }
  };
  
  const [state, send] = useStateMachine(config);
  
  // Auto-timer effect
  useEffect(() => {
    if (state.value === 'emergency') return;
    
    const duration = {
      red: 5000,
      yellow: 2000,
      green: 8000
    }[state.value];
    
    const timer = setTimeout(() => {
      send('TIMER');
    }, duration);
    
    return () => clearTimeout(timer);
  }, [state.value, send]);
  
  return {
    currentLight: state.value,
    isEmergency: state.value === 'emergency',
    activateEmergency: () => send('EMERGENCY'),
    clearEmergency: () => send('CLEAR_EMERGENCY'),
    canTransition: (event) => state.can(event)
  };
}

// Usage in component
function TrafficLightComponent() {
  const { 
    currentLight, 
    isEmergency, 
    activateEmergency, 
    clearEmergency 
  } = useTrafficLight();
  
  return (
    <div className="traffic-light">
      <div className={`light red ${currentLight === 'red' ? 'active' : ''}`} />
      <div className={`light yellow ${currentLight === 'yellow' ? 'active' : ''}`} />
      <div className={`light green ${currentLight === 'green' ? 'active' : ''}`} />
      
      <div className="controls">
        <button onClick={activateEmergency} disabled={isEmergency}>
          Emergency
        </button>
        <button onClick={clearEmergency} disabled={!isEmergency}>
          Clear Emergency
        </button>
      </div>
    </div>
  );
}
```

## Custom State Machine Hooks

### User Authentication State Machine

```jsx
// hooks/useAuthStateMachine.js
export function useAuthStateMachine() {
  const config = {
    initial: 'idle',
    context: {
      user: null,
      error: null,
      retryCount: 0
    },
    states: {
      idle: {
        on: {
          LOGIN: 'authenticating',
          CHECK_AUTH: 'checking'
        }
      },
      checking: {
        entry: (context, action) => {
          // Auto-check authentication on app start
        },
        on: {
          SUCCESS: {
            target: 'authenticated',
            actions: [(context, action) => ({
              ...context,
              user: action.payload.user,
              error: null
            })]
          },
          FAILURE: {
            target: 'unauthenticated',
            actions: [(context, action) => ({
              ...context,
              user: null,
              error: action.payload.error
            })]
          }
        }
      },
      authenticating: {
        entry: (context) => console.log('Starting authentication...'),
        on: {
          SUCCESS: {
            target: 'authenticated',
            actions: [(context, action) => ({
              ...context,
              user: action.payload.user,
              error: null,
              retryCount: 0
            })]
          },
          FAILURE: {
            target: 'unauthenticated',
            actions: [(context, action) => ({
              ...context,
              user: null,
              error: action.payload.error,
              retryCount: context.retryCount + 1
            })]
          },
          CANCEL: 'idle'
        }
      },
      authenticated: {
        entry: (context) => console.log(`Welcome, ${context.user?.name}!`),
        on: {
          LOGOUT: 'loggingOut',
          REFRESH: 'refreshing',
          SESSION_EXPIRED: 'sessionExpired'
        }
      },
      unauthenticated: {
        on: {
          LOGIN: 'authenticating',
          RETRY: {
            target: 'authenticating',
            cond: (context) => context.retryCount < 3
          }
        }
      },
      loggingOut: {
        entry: (context) => console.log('Logging out...'),
        on: {
          SUCCESS: {
            target: 'unauthenticated',
            actions: [(context) => ({
              ...context,
              user: null,
              error: null,
              retryCount: 0
            })]
          },
          FAILURE: 'authenticated' // Stay authenticated if logout fails
        }
      },
      refreshing: {
        on: {
          SUCCESS: {
            target: 'authenticated',
            actions: [(context, action) => ({
              ...context,
              user: action.payload.user,
              error: null
            })]
          },
          FAILURE: 'sessionExpired'
        }
      },
      sessionExpired: {
        entry: (context) => console.log('Session expired. Please log in again.'),
        on: {
          LOGIN: 'authenticating'
        }
      }
    }
  };
  
  const [state, send] = useStateMachine(config);
  
  // API integration
  const login = useCallback(async (credentials) => {
    send('LOGIN');
    
    try {
      const response = await authAPI.login(credentials);
      send({ type: 'SUCCESS', payload: { user: response.user } });
    } catch (error) {
      send({ type: 'FAILURE', payload: { error: error.message } });
    }
  }, [send]);
  
  const logout = useCallback(async () => {
    send('LOGOUT');
    
    try {
      await authAPI.logout();
      send('SUCCESS');
    } catch (error) {
      send('FAILURE');
    }
  }, [send]);
  
  const checkAuth = useCallback(async () => {
    send('CHECK_AUTH');
    
    try {
      const response = await authAPI.getCurrentUser();
      send({ type: 'SUCCESS', payload: { user: response.user } });
    } catch (error) {
      send({ type: 'FAILURE', payload: { error: error.message } });
    }
  }, [send]);
  
  const refreshAuth = useCallback(async () => {
    send('REFRESH');
    
    try {
      const response = await authAPI.refreshToken();
      send({ type: 'SUCCESS', payload: { user: response.user } });
    } catch (error) {
      send('FAILURE');
    }
  }, [send]);
  
  return {
    state: state.value,
    user: state.context.user,
    error: state.context.error,
    retryCount: state.context.retryCount,
    isIdle: state.matches('idle'),
    isChecking: state.matches('checking'),
    isAuthenticating: state.matches('authenticating'),
    isAuthenticated: state.matches('authenticated'),
    isUnauthenticated: state.matches('unauthenticated'),
    isLoggingOut: state.matches('loggingOut'),
    isRefreshing: state.matches('refreshing'),
    isSessionExpired: state.matches('sessionExpired'),
    canRetry: state.can('RETRY') && state.context.retryCount < 3,
    login,
    logout,
    checkAuth,
    refreshAuth,
    retry: () => send('RETRY')
  };
}

// Usage in App component
function App() {
  const auth = useAuthStateMachine();
  
  useEffect(() => {
    auth.checkAuth(); // Check auth on app start
  }, []);
  
  if (auth.isChecking) {
    return <LoadingScreen message="Checking authentication..." />;
  }
  
  if (auth.isAuthenticated) {
    return (
      <AuthenticatedApp 
        user={auth.user}
        onLogout={auth.logout}
        isLoggingOut={auth.isLoggingOut}
      />
    );
  }
  
  return (
    <LoginScreen
      onLogin={auth.login}
      isAuthenticating={auth.isAuthenticating}
      error={auth.error}
      canRetry={auth.canRetry}
      onRetry={auth.retry}
    />
  );
}
```

## Workflow Management Patterns

### Multi-Step Process State Machine

```jsx
// hooks/useWorkflowStateMachine.js
export function useWorkflowStateMachine(workflowConfig) {
  const createWorkflowMachine = (config) => ({
    initial: config.steps[0].id,
    context: {
      data: {},
      errors: {},
      currentStep: 0,
      completedSteps: [],
      canProceed: false
    },
    states: config.steps.reduce((states, step, index) => {
      const isFirst = index === 0;
      const isLast = index === config.steps.length - 1;
      const nextStep = config.steps[index + 1];
      const prevStep = config.steps[index - 1];
      
      states[step.id] = {
        entry: (context, action) => {
          console.log(`Entering step: ${step.title}`);
          // Validate step requirements
          if (step.validate && !step.validate(context.data)) {
            return; // Stay in current step if validation fails
          }
        },
        on: {
          NEXT: nextStep ? {
            target: nextStep.id,
            cond: (context) => {
              // Check if current step is valid
              if (step.validate) {
                return step.validate(context.data);
              }
              return true;
            },
            actions: [(context, action) => ({
              ...context,
              currentStep: index + 1,
              completedSteps: [...context.completedSteps, step.id],
              data: { ...context.data, ...action.payload }
            })]
          } : undefined,
          PREVIOUS: prevStep ? {
            target: prevStep.id,
            actions: [(context, action) => ({
              ...context,
              currentStep: index - 1,
              completedSteps: context.completedSteps.filter(id => id !== step.id)
            })]
          } : undefined,
          UPDATE_DATA: {
            target: step.id,
            actions: [(context, action) => ({
              ...context,
              data: { ...context.data, ...action.payload },
              errors: { ...context.errors, [step.id]: null }
            })]
          },
          SET_ERROR: {
            target: step.id,
            actions: [(context, action) => ({
              ...context,
              errors: { ...context.errors, [step.id]: action.payload }
            })]
          },
          SUBMIT: isLast ? {
            target: 'submitting',
            actions: [(context, action) => ({
              ...context,
              data: { ...context.data, ...action.payload }
            })]
          } : undefined,
          RESET: {
            target: config.steps[0].id,
            actions: [() => ({
              data: {},
              errors: {},
              currentStep: 0,
              completedSteps: [],
              canProceed: false
            })]
          }
        }
      };
      
      return states;
    }, {
      submitting: {
        entry: (context) => console.log('Submitting workflow...'),
        on: {
          SUCCESS: {
            target: 'completed',
            actions: [(context, action) => ({
              ...context,
              result: action.payload
            })]
          },
          FAILURE: {
            target: config.steps[config.steps.length - 1].id,
            actions: [(context, action) => ({
              ...context,
              errors: { submit: action.payload }
            })]
          }
        }
      },
      completed: {
        entry: (context) => console.log('Workflow completed successfully!'),
        on: {
          RESET: {
            target: config.steps[0].id,
            actions: [() => ({
              data: {},
              errors: {},
              currentStep: 0,
              completedSteps: [],
              canProceed: false
            })]
          }
        }
      }
    })
  });
  
  const machine = useMemo(() => createWorkflowMachine(workflowConfig), [workflowConfig]);
  const [state, send] = useStateMachine(machine);
  
  const currentStepConfig = workflowConfig.steps[state.context.currentStep];
  
  return {
    currentStep: state.value,
    currentStepIndex: state.context.currentStep,
    currentStepConfig,
    data: state.context.data,
    errors: state.context.errors,
    completedSteps: state.context.completedSteps,
    isFirst: state.context.currentStep === 0,
    isLast: state.context.currentStep === workflowConfig.steps.length - 1,
    isSubmitting: state.matches('submitting'),
    isCompleted: state.matches('completed'),
    canGoNext: state.can('NEXT'),
    canGoPrevious: state.can('PREVIOUS'),
    
    // Actions
    next: (data) => send({ type: 'NEXT', payload: data }),
    previous: () => send('PREVIOUS'),
    updateData: (data) => send({ type: 'UPDATE_DATA', payload: data }),
    setError: (error) => send({ type: 'SET_ERROR', payload: error }),
    submit: (data) => send({ type: 'SUBMIT', payload: data }),
    reset: () => send('RESET'),
    
    // Progress helpers
    getProgress: () => (state.context.currentStep / (workflowConfig.steps.length - 1)) * 100,
    isStepCompleted: (stepId) => state.context.completedSteps.includes(stepId),
    isStepAccessible: (stepIndex) => stepIndex <= state.context.currentStep + 1
  };
}

// Example: User Onboarding Workflow
function useUserOnboardingWorkflow() {
  const workflowConfig = {
    steps: [
      {
        id: 'personal-info',
        title: 'Personal Information',
        description: 'Tell us about yourself',
        validate: (data) => data.firstName && data.lastName && data.email,
        fields: ['firstName', 'lastName', 'email', 'phone']
      },
      {
        id: 'preferences',
        title: 'Preferences',
        description: 'Customize your experience',
        validate: (data) => data.notifications !== undefined,
        fields: ['notifications', 'theme', 'language']
      },
      {
        id: 'verification',
        title: 'Email Verification',
        description: 'Verify your email address',
        validate: (data) => data.emailVerified,
        fields: ['verificationCode']
      },
      {
        id: 'profile-setup',
        title: 'Profile Setup',
        description: 'Complete your profile',
        validate: (data) => data.bio && data.avatar,
        fields: ['bio', 'avatar', 'interests']
      }
    ]
  };
  
  const workflow = useWorkflowStateMachine(workflowConfig);
  
  // Auto-save data
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      localStorage.setItem('onboarding-data', JSON.stringify(workflow.data));
    }, 1000);
    
    return () => clearTimeout(timeoutId);
  }, [workflow.data]);
  
  // Handle submission
  const handleSubmit = useCallback(async (finalData) => {
    try {
      const response = await userAPI.completeOnboarding({
        ...workflow.data,
        ...finalData
      });
      workflow.submit(response);
    } catch (error) {
      workflow.setError(error.message);
    }
  }, [workflow]);
  
  return {
    ...workflow,
    handleSubmit
  };
}

// Usage in Onboarding component
function OnboardingWizard() {
  const workflow = useUserOnboardingWorkflow();
  
  const renderStep = () => {
    switch (workflow.currentStep) {
      case 'personal-info':
        return (
          <PersonalInfoStep
            data={workflow.data}
            errors={workflow.errors}
            onUpdate={workflow.updateData}
            onNext={workflow.next}
          />
        );
      case 'preferences':
        return (
          <PreferencesStep
            data={workflow.data}
            onUpdate={workflow.updateData}
            onNext={workflow.next}
            onPrevious={workflow.previous}
          />
        );
      case 'verification':
        return (
          <VerificationStep
            data={workflow.data}
            onUpdate={workflow.updateData}
            onNext={workflow.next}
            onPrevious={workflow.previous}
          />
        );
      case 'profile-setup':
        return (
          <ProfileSetupStep
            data={workflow.data}
            onUpdate={workflow.updateData}
            onSubmit={workflow.handleSubmit}
            onPrevious={workflow.previous}
            isSubmitting={workflow.isSubmitting}
          />
        );
      default:
        return <CompletionStep onReset={workflow.reset} />;
    }
  };
  
  return (
    <div className="onboarding-wizard">
      <ProgressBar progress={workflow.getProgress()} />
      <StepIndicator
        steps={workflow.currentStepConfig.title}
        currentStep={workflow.currentStepIndex}
        completedSteps={workflow.completedSteps}
      />
      
      {renderStep()}
      
      {workflow.errors.submit && (
        <ErrorMessage message={workflow.errors.submit} />
      )}
    </div>
  );
}
```

## Complex Form State Machines

### Dynamic Form State Machine

```jsx
// hooks/useFormStateMachine.js
export function useFormStateMachine(formSchema) {
  const createFormMachine = (schema) => ({
    initial: 'editing',
    context: {
      values: schema.defaultValues || {},
      errors: {},
      touched: {},
      isSubmitting: false,
      submitCount: 0,
      isDirty: false
    },
    states: {
      editing: {
        on: {
          CHANGE: {
            target: 'editing',
            actions: [(context, action) => {
              const { field, value } = action.payload;
              const newValues = { ...context.values, [field]: value };
              
              // Run field validation
              let fieldError = null;
              if (schema.fields[field]?.validate) {
                try {
                  schema.fields[field].validate(value, newValues);
                } catch (error) {
                  fieldError = error.message;
                }
              }
              
              return {
                ...context,
                values: newValues,
                errors: { ...context.errors, [field]: fieldError },
                touched: { ...context.touched, [field]: true },
                isDirty: true
              };
            }]
          },
          BLUR: {
            target: 'editing',
            actions: [(context, action) => {
              const { field } = action.payload;
              return {
                ...context,
                touched: { ...context.touched, [field]: true }
              };
            }]
          },
          SUBMIT: {
            target: 'validating',
            actions: [(context) => ({
              ...context,
              submitCount: context.submitCount + 1
            })]
          },
          RESET: {
            target: 'editing',
            actions: [() => ({
              values: schema.defaultValues || {},
              errors: {},
              touched: {},
              isSubmitting: false,
              submitCount: 0,
              isDirty: false
            })]
          }
        }
      },
      validating: {
        entry: (context) => {
          // Run all validations
          const errors = {};
          Object.keys(schema.fields).forEach(field => {
            if (schema.fields[field].validate) {
              try {
                schema.fields[field].validate(context.values[field], context.values);
              } catch (error) {
                errors[field] = error.message;
              }
            }
          });
          
          // Run form-level validation
          if (schema.validate) {
            try {
              schema.validate(context.values);
            } catch (error) {
              errors._form = error.message;
            }
          }
          
          return { ...context, errors };
        },
        on: {
          VALIDATION_SUCCESS: 'submitting',
          VALIDATION_FAILURE: 'editing'
        }
      },
      submitting: {
        entry: (context) => ({ ...context, isSubmitting: true }),
        exit: (context) => ({ ...context, isSubmitting: false }),
        on: {
          SUBMIT_SUCCESS: {
            target: 'submitted',
            actions: [(context, action) => ({
              ...context,
              result: action.payload
            })]
          },
          SUBMIT_FAILURE: {
            target: 'editing',
            actions: [(context, action) => ({
              ...context,
              errors: { ...context.errors, _submit: action.payload }
            })]
          }
        }
      },
      submitted: {
        on: {
          RESET: {
            target: 'editing',
            actions: [() => ({
              values: schema.defaultValues || {},
              errors: {},
              touched: {},
              isSubmitting: false,
              submitCount: 0,
              isDirty: false
            })]
          },
          EDIT_AGAIN: 'editing'
        }
      }
    }
  });
  
  const machine = useMemo(() => createFormMachine(formSchema), [formSchema]);
  const [state, send] = useStateMachine(machine);
  
  // Auto-validation effect
  useEffect(() => {
    if (state.matches('validating')) {
      const hasErrors = Object.keys(state.context.errors).length > 0;
      if (hasErrors) {
        send('VALIDATION_FAILURE');
      } else {
        send('VALIDATION_SUCCESS');
      }
    }
  }, [state, send]);
  
  // Auto-submission effect
  useEffect(() => {
    if (state.matches('submitting')) {
      const submitForm = async () => {
        try {
          const result = await formSchema.onSubmit(state.context.values);
          send({ type: 'SUBMIT_SUCCESS', payload: result });
        } catch (error) {
          send({ type: 'SUBMIT_FAILURE', payload: error.message });
        }
      };
      
      submitForm();
    }
  }, [state, send, formSchema]);
  
  const getFieldProps = useCallback((fieldName) => ({
    value: state.context.values[fieldName] || '',
    onChange: (e) => {
      const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
      send({ type: 'CHANGE', payload: { field: fieldName, value } });
    },
    onBlur: () => send({ type: 'BLUR', payload: { field: fieldName } }),
    error: state.context.touched[fieldName] ? state.context.errors[fieldName] : undefined,
    touched: state.context.touched[fieldName] || false
  }), [state, send]);
  
  return {
    state: state.value,
    values: state.context.values,
    errors: state.context.errors,
    touched: state.context.touched,
    isSubmitting: state.context.isSubmitting,
    submitCount: state.context.submitCount,
    isDirty: state.context.isDirty,
    isValid: Object.keys(state.context.errors).length === 0,
    isEditing: state.matches('editing'),
    isValidating: state.matches('validating'),
    isSubmitted: state.matches('submitted'),
    
    // Actions
    submit: () => send('SUBMIT'),
    reset: () => send('RESET'),
    editAgain: () => send('EDIT_AGAIN'),
    
    // Field helpers
    getFieldProps,
    setFieldValue: (field, value) => send({ type: 'CHANGE', payload: { field, value } }),
    setFieldError: (field, error) => send({ type: 'SET_ERROR', payload: { field, error } })
  };
}

// Example: Contact Form
function useContactForm() {
  const schema = {
    defaultValues: {
      name: '',
      email: '',
      subject: '',
      message: '',
      priority: 'normal'
    },
    fields: {
      name: {
        validate: (value) => {
          if (!value) throw new Error('Name is required');
          if (value.length < 2) throw new Error('Name must be at least 2 characters');
        }
      },
      email: {
        validate: (value) => {
          if (!value) throw new Error('Email is required');
          if (!/\S+@\S+\.\S+/.test(value)) throw new Error('Email is invalid');
        }
      },
      subject: {
        validate: (value) => {
          if (!value) throw new Error('Subject is required');
        }
      },
      message: {
        validate: (value) => {
          if (!value) throw new Error('Message is required');
          if (value.length < 10) throw new Error('Message must be at least 10 characters');
        }
      }
    },
    validate: (values) => {
      // Form-level validation
      if (values.priority === 'urgent' && !values.phone) {
        throw new Error('Phone number is required for urgent inquiries');
      }
    },
    onSubmit: async (values) => {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });
      
      if (!response.ok) {
        throw new Error('Failed to send message');
      }
      
      return response.json();
    }
  };
  
  return useFormStateMachine(schema);
}

// Usage in component
function ContactForm() {
  const form = useContactForm();
  
  const handleSubmit = (e) => {
    e.preventDefault();
    form.submit();
  };
  
  if (form.isSubmitted) {
    return (
      <div className="success-message">
        <h3>Message Sent!</h3>
        <p>We'll get back to you soon.</p>
        <button onClick={form.reset}>Send Another Message</button>
      </div>
    );
  }
  
  return (
    <form onSubmit={handleSubmit} className="contact-form">
      <div className="form-field">
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          {...form.getFieldProps('name')}
        />
        {form.getFieldProps('name').error && (
          <span className="error">{form.getFieldProps('name').error}</span>
        )}
      </div>
      
      <div className="form-field">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...form.getFieldProps('email')}
        />
        {form.getFieldProps('email').error && (
          <span className="error">{form.getFieldProps('email').error}</span>
        )}
      </div>
      
      <div className="form-field">
        <label htmlFor="subject">Subject</label>
        <input
          id="subject"
          type="text"
          {...form.getFieldProps('subject')}
        />
        {form.getFieldProps('subject').error && (
          <span className="error">{form.getFieldProps('subject').error}</span>
        )}
      </div>
      
      <div className="form-field">
        <label htmlFor="priority">Priority</label>
        <select {...form.getFieldProps('priority')}>
          <option value="normal">Normal</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>
      
      <div className="form-field">
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          rows={4}
          {...form.getFieldProps('message')}
        />
        {form.getFieldProps('message').error && (
          <span className="error">{form.getFieldProps('message').error}</span>
        )}
      </div>
      
      {form.errors._form && (
        <div className="form-error">{form.errors._form}</div>
      )}
      
      {form.errors._submit && (
        <div className="submit-error">{form.errors._submit}</div>
      )}
      
      <button 
        type="submit" 
        disabled={form.isSubmitting || !form.isValid}
        className="submit-button"
      >
        {form.isSubmitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
}
```

## Async State Machine Patterns

### Data Fetching State Machine

```jsx
// hooks/useAsyncStateMachine.js
export function useAsyncStateMachine(asyncConfig) {
  const config = {
    initial: 'idle',
    context: {
      data: null,
      error: null,
      params: null,
      retryCount: 0,
      lastFetchTime: null
    },
    states: {
      idle: {
        on: {
          FETCH: {
            target: 'loading',
            actions: [(context, action) => ({
              ...context,
              params: action.payload,
              error: null
            })]
          }
        }
      },
      loading: {
        entry: (context) => console.log('Loading data...'),
        on: {
          SUCCESS: {
            target: 'success',
            actions: [(context, action) => ({
              ...context,
              data: action.payload,
              error: null,
              retryCount: 0,
              lastFetchTime: Date.now()
            })]
          },
          FAILURE: {
            target: 'error',
            actions: [(context, action) => ({
              ...context,
              error: action.payload,
              retryCount: context.retryCount + 1
            })]
          },
          CANCEL: 'idle'
        }
      },
      success: {
        on: {
          FETCH: {
            target: 'loading',
            actions: [(context, action) => ({
              ...context,
              params: action.payload,
              error: null
            })]
          },
          REFRESH: {
            target: 'refreshing',
            actions: [(context) => ({
              ...context,
              error: null
            })]
          },
          INVALIDATE: 'idle'
        }
      },
      refreshing: {
        on: {
          SUCCESS: {
            target: 'success',
            actions: [(context, action) => ({
              ...context,
              data: action.payload,
              error: null,
              lastFetchTime: Date.now()
            })]
          },
          FAILURE: {
            target: 'success', // Keep existing data
            actions: [(context, action) => ({
              ...context,
              error: action.payload
            })]
          }
        }
      },
      error: {
        on: {
          RETRY: {
            target: 'loading',
            cond: (context) => context.retryCount < (asyncConfig.maxRetries || 3)
          },
          FETCH: {
            target: 'loading',
            actions: [(context, action) => ({
              ...context,
              params: action.payload,
              error: null,
              retryCount: 0
            })]
          },
          RESET: 'idle'
        }
      }
    }
  };
  
  const [state, send] = useStateMachine(config);
  
  // Auto-fetch effect
  useEffect(() => {
    if (state.matches('loading')) {
      const controller = new AbortController();
      
      const fetchData = async () => {
        try {
          const result = await asyncConfig.fetcher(state.context.params, {
            signal: controller.signal
          });
          send({ type: 'SUCCESS', payload: result });
        } catch (error) {
          if (!controller.signal.aborted) {
            send({ type: 'FAILURE', payload: error.message });
          }
        }
      };
      
      fetchData();
      
      return () => controller.abort();
    }
  }, [state, send, asyncConfig]);
  
  // Auto-refresh effect
  useEffect(() => {
    if (state.matches('refreshing')) {
      const controller = new AbortController();
      
      const refreshData = async () => {
        try {
          const result = await asyncConfig.fetcher(state.context.params, {
            signal: controller.signal
          });
          send({ type: 'SUCCESS', payload: result });
        } catch (error) {
          if (!controller.signal.aborted) {
            send({ type: 'FAILURE', payload: error.message });
          }
        }
      };
      
      refreshData();
      
      return () => controller.abort();
    }
  }, [state, send, asyncConfig]);
  
  // Auto-retry effect
  useEffect(() => {
    if (state.matches('error') && asyncConfig.autoRetry) {
      const delay = Math.min(1000 * Math.pow(2, state.context.retryCount), 10000);
      const timer = setTimeout(() => {
        if (state.context.retryCount < (asyncConfig.maxRetries || 3)) {
          send('RETRY');
        }
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [state, send, asyncConfig]);
  
  return {
    state: state.value,
    data: state.context.data,
    error: state.context.error,
    params: state.context.params,
    retryCount: state.context.retryCount,
    lastFetchTime: state.context.lastFetchTime,
    
    // State checkers
    isIdle: state.matches('idle'),
    isLoading: state.matches('loading'),
    isSuccess: state.matches('success'),
    isRefreshing: state.matches('refreshing'),
    isError: state.matches('error'),
    
    // Actions
    fetch: (params) => send({ type: 'FETCH', payload: params }),
    refresh: () => send('REFRESH'),
    retry: () => send('RETRY'),
    cancel: () => send('CANCEL'),
    reset: () => send('RESET'),
    invalidate: () => send('INVALIDATE'),
    
    // Helpers
    canRetry: state.can('RETRY'),
    isStale: (maxAge = 300000) => { // 5 minutes default
      return state.context.lastFetchTime && 
             Date.now() - state.context.lastFetchTime > maxAge;
    }
  };
}

// Example: User Profile Fetcher
function useUserProfile(userId) {
  const asyncConfig = {
    fetcher: async (params, options) => {
      const response = await fetch(`/api/users/${params.userId}`, {
        signal: options.signal
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch user: ${response.statusText}`);
      }
      
      return response.json();
    },
    maxRetries: 3,
    autoRetry: true
  };
  
  const profile = useAsyncStateMachine(asyncConfig);
  
  // Fetch when userId changes
  useEffect(() => {
    if (userId) {
      profile.fetch({ userId });
    }
  }, [userId, profile.fetch]);
  
  // Auto-refresh stale data
  useEffect(() => {
    if (profile.isSuccess && profile.isStale()) {
      profile.refresh();
    }
  }, [profile]);
  
  return profile;
}

// Usage in component
function UserProfileCard({ userId }) {
  const profile = useUserProfile(userId);
  
  if (profile.isLoading) {
    return <div className="loading">Loading profile...</div>;
  }
  
  if (profile.isError) {
    return (
      <div className="error">
        <p>Error: {profile.error}</p>
        {profile.canRetry && (
          <button onClick={profile.retry}>
            Retry ({profile.retryCount}/3)
          </button>
        )}
      </div>
    );
  }
  
  if (!profile.data) {
    return <div>No profile data</div>;
  }
  
  return (
    <div className="profile-card">
      <img src={profile.data.avatar} alt={profile.data.name} />
      <h3>{profile.data.name}</h3>
      <p>{profile.data.email}</p>
      
      <div className="actions">
        <button onClick={profile.refresh} disabled={profile.isRefreshing}>
          {profile.isRefreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      
      {profile.isStale() && (
        <div className="stale-indicator">
          Data may be outdated
        </div>
      )}
    </div>
  );
}
```

## Testing State Machines

### State Machine Testing Utilities

```jsx
// test-utils/stateMachineTestUtils.js
import { renderHook, act } from '@testing-library/react';

export function createStateMachineTestUtils(useStateMachine) {
  return {
    renderStateMachine: (initialProps) => {
      return renderHook((props) => useStateMachine(props || initialProps), {
        initialProps
      });
    },
    
    expectState: (result, expectedState) => {
      expect(result.current.state || result.current.currentStep).toBe(expectedState);
    },
    
    expectContext: (result, expectedContext) => {
      expect(result.current.context || result.current.data).toMatchObject(expectedContext);
    },
    
    sendEvent: (result, event) => {
      act(() => {
        const send = result.current.send || result.current.next || result.current.updateData;
        send(event);
      });
    },
    
    waitForState: async (result, expectedState, timeout = 5000) => {
      const startTime = Date.now();
      
      while (Date.now() - startTime < timeout) {
        if ((result.current.state || result.current.currentStep) === expectedState) {
          return;
        }
        await new Promise(resolve => setTimeout(resolve, 10));
      }
      
      throw new Error(`Timeout waiting for state "${expectedState}"`);
    }
  };
}

// Test example for auth state machine
describe('useAuthStateMachine', () => {
  const { renderStateMachine, expectState, sendEvent, waitForState } = 
    createStateMachineTestUtils(useAuthStateMachine);
  
  test('should start in idle state', () => {
    const { result } = renderStateMachine();
    expectState(result, 'idle');
  });
  
  test('should transition to authenticating on login', () => {
    const { result } = renderStateMachine();
    
    sendEvent(result, 'LOGIN');
    expectState(result, 'authenticating');
  });
  
  test('should handle successful login', async () => {
    // Mock API
    jest.spyOn(authAPI, 'login').mockResolvedValue({
      user: { id: 1, name: 'John Doe' }
    });
    
    const { result } = renderStateMachine();
    
    act(() => {
      result.current.login({ email: 'test@test.com', password: 'password' });
    });
    
    expectState(result, 'authenticating');
    
    await waitForState(result, 'authenticated');
    expect(result.current.user).toEqual({ id: 1, name: 'John Doe' });
  });
  
  test('should handle login failure with retry', async () => {
    jest.spyOn(authAPI, 'login').mockRejectedValue(new Error('Invalid credentials'));
    
    const { result } = renderStateMachine();
    
    act(() => {
      result.current.login({ email: 'wrong@test.com', password: 'wrong' });
    });
    
    await waitForState(result, 'unauthenticated');
    expect(result.current.error).toBe('Invalid credentials');
    expect(result.current.canRetry).toBe(true);
  });
  
  test('should limit retry attempts', async () => {
    jest.spyOn(authAPI, 'login').mockRejectedValue(new Error('Server error'));
    
    const { result } = renderStateMachine();
    
    // Try multiple times
    for (let i = 0; i < 4; i++) {
      act(() => {
        result.current.login({ email: 'test@test.com', password: 'password' });
      });
      await waitForState(result, 'unauthenticated');
    }
    
    expect(result.current.retryCount).toBe(4);
    expect(result.current.canRetry).toBe(false);
  });
});

// Integration test with component
describe('AuthFlow Integration', () => {
  test('should complete full authentication flow', async () => {
    const mockUser = { id: 1, name: 'John Doe', email: 'john@test.com' };
    jest.spyOn(authAPI, 'login').mockResolvedValue({ user: mockUser });
    
    render(<App />);
    
    // Should show login form initially
    expect(screen.getByText('Login')).toBeInTheDocument();
    
    // Fill and submit login form
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'john@test.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // Should show loading state
    expect(screen.getByText('Logging in...')).toBeInTheDocument();
    
    // Should transition to authenticated state
    await waitFor(() => {
      expect(screen.getByText(`Welcome, ${mockUser.name}!`)).toBeInTheDocument();
    });
    
    // Should show authenticated UI
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });
});
```

## Performance Considerations

### Optimizing State Machine Performance

```jsx
// Performance optimization techniques
export function useOptimizedStateMachine(config) {
  // Memoize machine configuration
  const memoizedConfig = useMemo(() => config, [
    JSON.stringify(config) // Only for simple configs
  ]);
  
  // Use ref for actions that don't need to cause re-renders
  const actionsRef = useRef({});
  
  // Memoize selectors
  const selectors = useMemo(() => ({
    isLoading: (state) => ['loading', 'submitting', 'validating'].includes(state.value),
    hasError: (state) => !!state.context.error,
    canProceed: (state) => state.can('NEXT') || state.can('SUBMIT')
  }), []);
  
  const [state, send] = useStateMachine(memoizedConfig);
  
  // Debounce rapid state changes
  const debouncedSend = useMemo(
    () => debounce(send, 100),
    [send]
  );
  
  // Memoize computed values
  const computedValues = useMemo(() => ({
    isLoading: selectors.isLoading(state),
    hasError: selectors.hasError(state),
    canProceed: selectors.canProceed(state)
  }), [state, selectors]);
  
  return {
    state: state.value,
    context: state.context,
    send: debouncedSend,
    ...computedValues
  };
}

// Memory-efficient state machine for large datasets
export function useLazyStateMachine(configFactory) {
  const [config, setConfig] = useState(null);
  
  // Lazy load configuration
  useEffect(() => {
    configFactory().then(setConfig);
  }, [configFactory]);
  
  const [state, send] = useStateMachine(config || { initial: 'loading', states: { loading: {} } });
  
  return { state, send, isConfigLoaded: !!config };
}
```

## Best Practices

### State Machine Design Principles

```jsx
// 1. Keep states explicit and meaningful
const goodStateMachine = {
  initial: 'idle',
  states: {
    idle: { /* clear purpose */ },
    loading: { /* clear purpose */ },
    success: { /* clear purpose */ },
    error: { /* clear purpose */ }
  }
};

// 2. Make transitions predictable
const predictableTransitions = {
  states: {
    idle: {
      on: {
        START: 'loading' // Clear transition
      }
    },
    loading: {
      on: {
        SUCCESS: 'success',
        FAILURE: 'error',
        CANCEL: 'idle'
      }
    }
  }
};

// 3. Use guards for conditional logic
const conditionalMachine = {
  states: {
    form: {
      on: {
        SUBMIT: {
          target: 'submitting',
          cond: (context) => context.isValid // Guard condition
        }
      }
    }
  }
};

// 4. Keep context minimal and normalized
const efficientContext = {
  context: {
    // Only essential data
    userId: null,
    status: 'idle',
    error: null
  }
};

// 5. Use actions for side effects
const actionBasedMachine = {
  states: {
    loading: {
      entry: 'startLoading', // Side effect
      exit: 'cleanup'       // Cleanup
    }
  }
};
```

State machines provide a powerful pattern for managing complex state logic in React applications. They ensure predictable state transitions, make debugging easier, and provide a clear mental model for application behavior.
