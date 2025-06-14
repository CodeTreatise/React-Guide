# Form Performance Optimization and Testing

> **Advanced Performance Techniques, Testing Strategies, and Production-Ready Patterns**

## 🎯 Overview

This comprehensive guide covers advanced performance optimization techniques, comprehensive testing strategies, monitoring solutions, and production-ready patterns for React forms.

## 📋 Table of Contents

1. [Performance Optimization Strategies](#performance-optimization-strategies)
2. [Memory Management](#memory-management)
3. [Rendering Optimization](#rendering-optimization)
4. [Network Optimization](#network-optimization)
5. [Testing Strategies](#testing-strategies)
6. [Performance Monitoring](#performance-monitoring)
7. [Production Patterns](#production-patterns)
8. [Debugging Tools](#debugging-tools)

## ⚡ Performance Optimization Strategies

### Memoization and Optimization Hooks

```jsx
{% raw %}
{% raw %}
import { memo, useMemo, useCallback, useState } from 'react';
import { useForm } from 'react-hook-form';

// Memoized field component
const OptimizedField = memo(({ 
  field, 
  register, 
  errors, 
  onChange,
  value 
}) => {
  const validationRules = useMemo(() => {
    const rules = {};
    if (field.required) rules.required = `${field.label} is required`;
    if (field.minLength) rules.minLength = { 
      value: field.minLength, 
      message: `Minimum ${field.minLength} characters` 
    };
    if (field.maxLength) rules.maxLength = { 
      value: field.maxLength, 
      message: `Maximum ${field.maxLength} characters` 
    };
    if (field.pattern) rules.pattern = { 
      value: field.pattern, 
      message: 'Invalid format' 
    };
    return rules;
  }, [field]);

  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    onChange?.(field.name, newValue);
  }, [field.name, onChange]);

  const fieldClassName = useMemo(() => {
    return `form-field ${errors[field.name] ? 'error' : ''} ${field.className || ''}`;
  }, [errors, field.name, field.className]);

  return (
    <div className={fieldClassName}>
      <label htmlFor={field.name}>{field.label}</label>
      <input
        {...register(field.name, validationRules)}
        id={field.name}
        type={field.type}
        placeholder={field.placeholder}
        onChange={handleChange}
      />
      {errors[field.name] && (
        <span className="error-message">{errors[field.name].message}</span>
      )}
    </div>
  );
});

// Optimized form with virtualization for large forms
const VirtualizedForm = ({ fields, onSubmit }) => {
  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    mode: 'onBlur',
    reValidateMode: 'onChange'
  });

  const [visibleFields, setVisibleFields] = useState(new Set());
  const [fieldChanges, setFieldChanges] = useState({});

  // Virtualization for large forms
  const useVirtualization = fields.length > 50;

  const handleFieldChange = useCallback((fieldName, value) => {
    setFieldChanges(prev => ({ ...prev, [fieldName]: value }));
  }, []);

  // Memoize visible fields calculation
  const renderFields = useMemo(() => {
    const fieldsToRender = useVirtualization 
      ? fields.filter((_, index) => visibleFields.has(index))
      : fields;

    return fieldsToRender.map((field, index) => (
      <OptimizedField
        key={field.name}
        field={field}
        register={register}
        errors={errors}
        onChange={handleFieldChange}
      />
    ));
  }, [fields, visibleFields, useVirtualization, register, errors, handleFieldChange]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="optimized-form">
      {renderFields}
      <button type="submit">Submit</button>
    </form>
  );
};

// Performance monitoring hook
const useFormPerformance = () => {
  const [metrics, setMetrics] = useState({
    renderCount: 0,
    renderTime: 0,
    validationTime: 0,
    memoryUsage: 0
  });

  const markRenderStart = useCallback(() => {
    return performance.now();
  }, []);

  const markRenderEnd = useCallback((startTime) => {
    const renderTime = performance.now() - startTime;
    setMetrics(prev => ({
      ...prev,
      renderCount: prev.renderCount + 1,
      renderTime: (prev.renderTime + renderTime) / 2 // Running average
    }));
  }, []);

  const trackValidation = useCallback((validationTime) => {
    setMetrics(prev => ({
      ...prev,
      validationTime: (prev.validationTime + validationTime) / 2
    }));
  }, []);

  const trackMemoryUsage = useCallback(() => {
    if (performance.memory) {
      setMetrics(prev => ({
        ...prev,
        memoryUsage: performance.memory.usedJSHeapSize
      }));
    }
  }, []);

  return {
    metrics,
    markRenderStart,
    markRenderEnd,
    trackValidation,
    trackMemoryUsage
  };
};
{% endraw %}
{% endraw %}
```

### Debounced Validation and Input Optimization

```jsx
import { useMemo, useCallback, useRef } from 'react';
import { debounce } from 'lodash';

// Optimized debounced input component
const DebouncedInput = memo(({ 
  name, 
  onValidate, 
  validationDelay = 300,
  ...props 
}) => {
  const [value, setValue] = useState('');
  const [error, setError] = useState('');
  const [isValidating, setIsValidating] = useState(false);

  // Memoized debounced validation
  const debouncedValidate = useMemo(
    () => debounce(async (val) => {
      if (!onValidate) return;
      
      setIsValidating(true);
      try {
        const validationError = await onValidate(val);
        setError(validationError || '');
      } catch (err) {
        setError('Validation failed');
      } finally {
        setIsValidating(false);
      }
    }, validationDelay),
    [onValidate, validationDelay]
  );

  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    setValue(newValue);
    debouncedValidate(newValue);
  }, [debouncedValidate]);

  // Cleanup debounced function
  useEffect(() => {
    return () => {
      debouncedValidate.cancel();
    };
  }, [debouncedValidate]);

  return (
    <div className="debounced-input">
      <input
        {...props}
        value={value}
        onChange={handleChange}
        className={error ? 'error' : ''}
      />
      {isValidating && <span className="validating">Validating...</span>}
      {error && <span className="error">{error}</span>}
    </div>
  );
});

// Optimized async validation hook
const useOptimizedAsyncValidation = (validationFn, dependencies = []) => {
  const cache = useRef(new Map());
  const requestQueue = useRef(new Map());

  const validate = useCallback(async (value) => {
    // Check cache first
    if (cache.current.has(value)) {
      return cache.current.get(value);
    }

    // Check if request is already in progress
    if (requestQueue.current.has(value)) {
      return requestQueue.current.get(value);
    }

    // Create new validation promise
    const validationPromise = validationFn(value);
    requestQueue.current.set(value, validationPromise);

    try {
      const result = await validationPromise;
      
      // Cache the result
      cache.current.set(value, result);
      
      // Limit cache size
      if (cache.current.size > 100) {
        const firstKey = cache.current.keys().next().value;
        cache.current.delete(firstKey);
      }
      
      return result;
    } finally {
      requestQueue.current.delete(value);
    }
  }, [...dependencies, validationFn]);

  const clearCache = useCallback(() => {
    cache.current.clear();
    requestQueue.current.clear();
  }, []);

  return { validate, clearCache };
};
```

## 🧠 Memory Management

### Memory Leak Prevention

```jsx
import { useEffect, useRef, useCallback } from 'react';

// Hook to prevent memory leaks in forms
const useMemoryOptimization = () => {
  const subscriptions = useRef(new Set());
  const timeouts = useRef(new Set());
  const intervals = useRef(new Set());
  const abortControllers = useRef(new Set());

  const addSubscription = useCallback((unsubscribe) => {
    subscriptions.current.add(unsubscribe);
    return () => subscriptions.current.delete(unsubscribe);
  }, []);

  const addTimeout = useCallback((id) => {
    timeouts.current.add(id);
    return () => {
      clearTimeout(id);
      timeouts.current.delete(id);
    };
  }, []);

  const addInterval = useCallback((id) => {
    intervals.current.add(id);
    return () => {
      clearInterval(id);
      intervals.current.delete(id);
    };
  }, []);

  const addAbortController = useCallback((controller) => {
    abortControllers.current.add(controller);
    return () => {
      controller.abort();
      abortControllers.current.delete(controller);
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Clear all subscriptions
      subscriptions.current.forEach(unsubscribe => {
        try {
          unsubscribe();
        } catch (error) {
          console.warn('Error during subscription cleanup:', error);
        }
      });

      // Clear all timeouts
      timeouts.current.forEach(id => clearTimeout(id));

      // Clear all intervals
      intervals.current.forEach(id => clearInterval(id));

      // Abort all controllers
      abortControllers.current.forEach(controller => {
        try {
          controller.abort();
        } catch (error) {
          console.warn('Error during abort controller cleanup:', error);
        }
      });
    };
  }, []);

  return {
    addSubscription,
    addTimeout,
    addInterval,
    addAbortController
  };
};

// Optimized form state management
const useOptimizedFormState = (initialValues = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const { addTimeout } = useMemoryOptimization();

  // Batched state updates
  const batchedUpdates = useRef(null);
  const pendingUpdates = useRef({});

  const scheduleUpdate = useCallback(() => {
    if (batchedUpdates.current) return;

    batchedUpdates.current = addTimeout(setTimeout(() => {
      const updates = { ...pendingUpdates.current };
      pendingUpdates.current = {};
      batchedUpdates.current = null;

      if (updates.values) setValues(prev => ({ ...prev, ...updates.values }));
      if (updates.errors) setErrors(prev => ({ ...prev, ...updates.errors }));
      if (updates.touched) setTouched(prev => ({ ...prev, ...updates.touched }));
    }, 16)); // ~60fps
  }, [addTimeout]);

  const updateValue = useCallback((name, value) => {
    pendingUpdates.current.values = {
      ...pendingUpdates.current.values,
      [name]: value
    };
    scheduleUpdate();
  }, [scheduleUpdate]);

  const updateError = useCallback((name, error) => {
    pendingUpdates.current.errors = {
      ...pendingUpdates.current.errors,
      [name]: error
    };
    scheduleUpdate();
  }, [scheduleUpdate]);

  const updateTouched = useCallback((name, isTouched = true) => {
    pendingUpdates.current.touched = {
      ...pendingUpdates.current.touched,
      [name]: isTouched
    };
    scheduleUpdate();
  }, [scheduleUpdate]);

  return {
    values,
    errors,
    touched,
    updateValue,
    updateError,
    updateTouched
  };
};
```

### Resource Pooling and Caching

```jsx
// Form field cache to reuse components
class FieldComponentCache {
  constructor(maxSize = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  get(key) {
    const item = this.cache.get(key);
    if (item) {
      // Move to end (LRU)
      this.cache.delete(key);
      this.cache.set(key, item);
      return item;
    }
    return null;
  }

  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      // Remove oldest item
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }

  clear() {
    this.cache.clear();
  }
}

const fieldCache = new FieldComponentCache();

// Object pool for form validation results
class ValidationResultPool {
  constructor() {
    this.pool = [];
  }

  acquire() {
    if (this.pool.length > 0) {
      return this.pool.pop();
    }
    return {
      isValid: true,
      errors: {},
      warnings: {}
    };
  }

  release(result) {
    // Reset the object
    result.isValid = true;
    result.errors = {};
    result.warnings = {};
    
    // Return to pool if not too large
    if (this.pool.length < 50) {
      this.pool.push(result);
    }
  }
}

const validationPool = new ValidationResultPool();

// Cached validation hook
const useCachedValidation = (validationSchema) => {
  const validationCache = useRef(new Map());

  const validate = useCallback(async (values) => {
    const cacheKey = JSON.stringify(values);
    
    if (validationCache.current.has(cacheKey)) {
      return validationCache.current.get(cacheKey);
    }

    const result = validationPool.acquire();
    
    try {
      const validationResult = await validationSchema.validate(values, { 
        abortEarly: false 
      });
      result.isValid = true;
    } catch (error) {
      result.isValid = false;
      result.errors = error.inner.reduce((acc, err) => {
        acc[err.path] = err.message;
        return acc;
      }, {});
    }

    // Cache the result
    validationCache.current.set(cacheKey, { ...result });
    
    // Limit cache size
    if (validationCache.current.size > 200) {
      const firstKey = validationCache.current.keys().next().value;
      validationCache.current.delete(firstKey);
    }

    return result;
  }, [validationSchema]);

  useEffect(() => {
    return () => {
      // Clear cache on unmount
      validationCache.current.clear();
    };
  }, []);

  return validate;
};
```

## 🎨 Rendering Optimization

### Virtual Scrolling for Large Forms

```jsx
import { FixedSizeList as List } from 'react-window';
import { memo, useMemo } from 'react';

const VirtualizedFormList = memo(({ 
  fields, 
  itemHeight = 80, 
  maxHeight = 400,
  register,
  errors 
}) => {
  const fieldItems = useMemo(() => fields.map((field, index) => ({
    ...field,
    index
  })), [fields]);

  const FieldRow = memo(({ index, style }) => {
    const field = fieldItems[index];
    
    return (
      <div style={style} className="virtual-field-row">
        <OptimizedField
          field={field}
          register={register}
          errors={errors}
        />
      </div>
    );
  });

  return (
    <List
      height={Math.min(maxHeight, fields.length * itemHeight)}
      itemCount={fields.length}
      itemSize={itemHeight}
      className="virtual-form-list"
    >
      {FieldRow}
    </List>
  );
});

// Windowing for large form sections
const WindowedFormSection = ({ fields, windowSize = 20 }) => {
  const [startIndex, setStartIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef();

  // Intersection observer for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Calculate visible fields
  const visibleFields = useMemo(() => {
    if (!isVisible) return [];
    
    const endIndex = Math.min(startIndex + windowSize, fields.length);
    return fields.slice(startIndex, endIndex);
  }, [fields, startIndex, windowSize, isVisible]);

  const handleScroll = useCallback((e) => {
    const { scrollTop, clientHeight, scrollHeight } = e.target;
    const scrollPercentage = scrollTop / (scrollHeight - clientHeight);
    const newStartIndex = Math.floor(scrollPercentage * (fields.length - windowSize));
    setStartIndex(Math.max(0, newStartIndex));
  }, [fields.length, windowSize]);

  return (
    <div 
      ref={sectionRef}
      className="windowed-section"
      onScroll={handleScroll}
    >
      {isVisible && visibleFields.map((field, index) => (
        <OptimizedField key={field.id} field={field} />
      ))}
    </div>
  );
};
```

### Lazy Loading and Code Splitting

```jsx
import { lazy, Suspense } from 'react';

// Lazy load heavy form components
const FileUploadComponent = lazy(() => import('./FileUploadComponent'));
const RichTextEditor = lazy(() => import('./RichTextEditor'));
const DateRangePicker = lazy(() => import('./DateRangePicker'));
const AddressAutoComplete = lazy(() => import('./AddressAutoComplete'));

// Component registry for dynamic loading
const componentRegistry = {
  'file-upload': FileUploadComponent,
  'rich-text': RichTextEditor,
  'date-range': DateRangePicker,
  'address': AddressAutoComplete
};

const LazyFormField = ({ fieldType, ...props }) => {
  const Component = componentRegistry[fieldType];
  
  if (!Component) {
    return <DefaultFormField {...props} />;
  }

  return (
    <Suspense fallback={<FieldSkeleton />}>
      <Component {...props} />
    </Suspense>
  );
};

// Skeleton loader for lazy components
const FieldSkeleton = () => (
  <div className="field-skeleton">
    <div className="skeleton-label"></div>
    <div className="skeleton-input"></div>
  </div>
);

// Progressive form loading
const ProgressiveForm = ({ sections }) => {
  const [loadedSections, setLoadedSections] = useState(new Set([0]));
  const [visibleSections, setVisibleSections] = useState(new Set([0]));

  const loadSection = useCallback((sectionIndex) => {
    if (!loadedSections.has(sectionIndex)) {
      setLoadedSections(prev => new Set([...prev, sectionIndex]));
    }
    setVisibleSections(prev => new Set([...prev, sectionIndex]));
  }, [loadedSections]);

  const IntersectionSection = ({ section, index }) => {
    const sectionRef = useRef();

    useEffect(() => {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            loadSection(index);
          }
        },
        { rootMargin: '100px' }
      );

      if (sectionRef.current) {
        observer.observe(sectionRef.current);
      }

      return () => observer.disconnect();
    }, [index]);

    return (
      <div ref={sectionRef} className="form-section">
        {loadedSections.has(index) && visibleSections.has(index) ? (
          <FormSection section={section} />
        ) : (
          <SectionSkeleton />
        )}
      </div>
    );
  };

  return (
    <div className="progressive-form">
      {sections.map((section, index) => (
        <IntersectionSection
          key={index}
          section={section}
          index={index}
        />
      ))}
    </div>
  );
};
```

## 🌐 Network Optimization

### Request Batching and Caching

```jsx
// Network request batching
class RequestBatcher {
  constructor(batchDelay = 100, maxBatchSize = 10) {
    this.batchDelay = batchDelay;
    this.maxBatchSize = maxBatchSize;
    this.pendingRequests = [];
    this.batchTimeout = null;
  }

  addRequest(request) {
    return new Promise((resolve, reject) => {
      this.pendingRequests.push({ request, resolve, reject });

      if (this.pendingRequests.length >= this.maxBatchSize) {
        this.processBatch();
      } else if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => {
          this.processBatch();
        }, this.batchDelay);
      }
    });
  }

  async processBatch() {
    if (this.pendingRequests.length === 0) return;

    const batch = this.pendingRequests.splice(0);
    this.batchTimeout = null;

    try {
      const requests = batch.map(({ request }) => request);
      const results = await this.executeBatch(requests);

      batch.forEach(({ resolve }, index) => {
        resolve(results[index]);
      });
    } catch (error) {
      batch.forEach(({ reject }) => {
        reject(error);
      });
    }
  }

  async executeBatch(requests) {
    const response = await fetch('/api/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ requests })
    });

    if (!response.ok) {
      throw new Error('Batch request failed');
    }

    return response.json();
  }
}

const validationBatcher = new RequestBatcher();

// Optimized async validation with batching
const useBatchedValidation = () => {
  const validateField = useCallback(async (fieldName, value) => {
    const request = {
      type: 'validate',
      field: fieldName,
      value
    };

    return validationBatcher.addRequest(request);
  }, []);

  return { validateField };
};

// Cache management for form data
class FormDataCache {
  constructor(maxAge = 5 * 60 * 1000) { // 5 minutes
    this.cache = new Map();
    this.maxAge = maxAge;
  }

  set(key, value) {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.maxAge) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  clear() {
    this.cache.clear();
  }

  cleanup() {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > this.maxAge) {
        this.cache.delete(key);
      }
    }
  }
}

const formDataCache = new FormDataCache();

// Periodic cache cleanup
setInterval(() => {
  formDataCache.cleanup();
}, 60000); // Clean every minute
```

### Optimistic Updates and Offline Support

```jsx
{% raw %}
{% raw %}
// Optimistic update hook
const useOptimisticUpdates = () => {
  const [optimisticData, setOptimisticData] = useState({});
  const [pendingUpdates, setPendingUpdates] = useState(new Map());

  const applyOptimisticUpdate = useCallback((key, update) => {
    const updateId = `${key}_${Date.now()}`;
    
    // Apply optimistic update
    setOptimisticData(prev => ({ ...prev, [key]: update }));
    
    // Track pending update
    setPendingUpdates(prev => new Map(prev).set(updateId, { key, update }));

    return updateId;
  }, []);

  const confirmUpdate = useCallback((updateId) => {
    setPendingUpdates(prev => {
      const newMap = new Map(prev);
      newMap.delete(updateId);
      return newMap;
    });
  }, []);

  const revertUpdate = useCallback((updateId) => {
    setPendingUpdates(prev => {
      const newMap = new Map(prev);
      const update = prev.get(updateId);
      
      if (update) {
        setOptimisticData(current => {
          const { [update.key]: removed, ...rest } = current;
          return rest;
        });
        newMap.delete(updateId);
      }
      
      return newMap;
    });
  }, []);

  return {
    optimisticData,
    pendingUpdates,
    applyOptimisticUpdate,
    confirmUpdate,
    revertUpdate
  };
};

// Offline support with queue
const useOfflineForm = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [submissionQueue, setSubmissionQueue] = useState([]);
  const { applyOptimisticUpdate, confirmUpdate, revertUpdate } = useOptimisticUpdates();

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      processQueue();
    };
    
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const submitForm = useCallback(async (formData) => {
    const updateId = applyOptimisticUpdate('formSubmission', formData);

    if (isOnline) {
      try {
        const response = await fetch('/api/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });

        if (response.ok) {
          confirmUpdate(updateId);
          return { success: true };
        } else {
          throw new Error('Submission failed');
        }
      } catch (error) {
        revertUpdate(updateId);
        
        // Queue for retry when back online
        setSubmissionQueue(prev => [...prev, { formData, updateId }]);
        return { success: false, queued: true };
      }
    } else {
      // Queue submission for when back online
      setSubmissionQueue(prev => [...prev, { formData, updateId }]);
      return { success: false, queued: true };
    }
  }, [isOnline, applyOptimisticUpdate, confirmUpdate, revertUpdate]);

  const processQueue = useCallback(async () => {
    const queue = [...submissionQueue];
    setSubmissionQueue([]);

    for (const { formData, updateId } of queue) {
      try {
        const response = await fetch('/api/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });

        if (response.ok) {
          confirmUpdate(updateId);
        } else {
          // Re-queue failed submissions
          setSubmissionQueue(prev => [...prev, { formData, updateId }]);
        }
      } catch (error) {
        // Re-queue failed submissions
        setSubmissionQueue(prev => [...prev, { formData, updateId }]);
      }
    }
  }, [submissionQueue, confirmUpdate]);

  return {
    isOnline,
    submissionQueue,
    submitForm
  };
};
{% endraw %}
{% endraw %}
```

## 🧪 Testing Strategies

### Comprehensive Form Testing

```jsx
{% raw %}
{% raw %}
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

// Testing utilities
export const FormTestUtils = {
  // Fill form fields
  async fillForm(fields) {
    const user = userEvent.setup();
    
    for (const [fieldName, value] of Object.entries(fields)) {
      const field = screen.getByRole('textbox', { name: new RegExp(fieldName, 'i') });
      await user.clear(field);
      await user.type(field, value);
    }
  },

  // Submit form
  async submitForm() {
    const user = userEvent.setup();
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);
  },

  // Check validation errors
  expectValidationError(fieldName, errorMessage) {
    const error = screen.getByText(errorMessage);
    expect(error).toBeInTheDocument();
  },

  // Check form submission
  async expectFormSubmission(mockSubmit, expectedData) {
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expectedData);
    });
  }
};

// Performance testing
describe('Form Performance Tests', () => {
  beforeEach(() => {
    // Mock performance API
    global.performance.mark = vi.fn();
    global.performance.measure = vi.fn();
    global.performance.getEntriesByName = vi.fn().mockReturnValue([
      { duration: 50 }
    ]);
  });

  test('should render large form within performance budget', async () => {
    const startTime = performance.now();
    
    const largeFields = Array.from({ length: 1000 }, (_, i) => ({
      name: `field_${i}`,
      type: 'text',
      label: `Field ${i}`
    }));

    render(<VirtualizedForm fields={largeFields} />);
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render within 100ms
    expect(renderTime).toBeLessThan(100);
  });

  test('should handle rapid input changes without blocking', async () => {
    const user = userEvent.setup();
    const onValidate = vi.fn().mockResolvedValue('');
    
    render(
      <DebouncedInput
        name="test"
        onValidate={onValidate}
        validationDelay={300}
      />
    );

    const input = screen.getByRole('textbox');
    
    // Rapid typing
    await user.type(input, 'rapid typing test');
    
    // Should debounce validation calls
    await waitFor(() => {
      expect(onValidate).toHaveBeenCalledTimes(1);
    });
  });

  test('should not cause memory leaks', () => {
    const { unmount } = render(<OptimizedForm />);
    
    const initialMemory = performance.memory?.usedJSHeapSize || 0;
    
    unmount();
    
    // Force garbage collection in test environment
    if (global.gc) {
      global.gc();
    }
    
    const finalMemory = performance.memory?.usedJSHeapSize || 0;
    
    // Memory should not increase significantly
    expect(finalMemory - initialMemory).toBeLessThan(1024 * 1024); // 1MB
  });
});

// Validation testing
describe('Form Validation Tests', () => {
  test('should validate required fields', async () => {
    const mockSubmit = vi.fn();
    
    render(<TestForm onSubmit={mockSubmit} />);
    
    await FormTestUtils.submitForm();
    
    FormTestUtils.expectValidationError('firstName', 'First name is required');
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  test('should validate email format', async () => {
    render(<TestForm />);
    
    await FormTestUtils.fillForm({
      email: 'invalid-email'
    });
    
    await FormTestUtils.submitForm();
    
    FormTestUtils.expectValidationError('email', 'Invalid email format');
  });

  test('should handle async validation', async () => {
    const mockAsyncValidation = vi.fn().mockResolvedValue('Username taken');
    
    render(<TestForm asyncValidation={mockAsyncValidation} />);
    
    await FormTestUtils.fillForm({
      username: 'taken-username'
    });

    // Wait for async validation
    await waitFor(() => {
      FormTestUtils.expectValidationError('username', 'Username taken');
    });
  });
});

// Accessibility testing
describe('Form Accessibility Tests', () => {
  test('should have proper ARIA labels', () => {
    render(<TestForm />);
    
    const firstNameField = screen.getByLabelText('First Name');
    expect(firstNameField).toHaveAttribute('aria-required', 'true');
    
    const emailField = screen.getByLabelText('Email');
    expect(emailField).toHaveAttribute('aria-describedby');
  });

  test('should announce validation errors to screen readers', async () => {
    render(<TestForm />);
    
    await FormTestUtils.submitForm();
    
    const errorMessage = screen.getByRole('alert');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveAttribute('aria-live', 'polite');
  });

  test('should support keyboard navigation', async () => {
    const user = userEvent.setup();
    
    render(<TestForm />);
    
    // Tab through form fields
    await user.tab();
    expect(screen.getByLabelText('First Name')).toHaveFocus();
    
    await user.tab();
    expect(screen.getByLabelText('Email')).toHaveFocus();
    
    await user.tab();
    expect(screen.getByRole('button', { name: /submit/i })).toHaveFocus();
  });
});

// Integration testing
describe('Form Integration Tests', () => {
  test('should handle full form submission flow', async () => {
    const mockApiCall = vi.fn().mockResolvedValue({ success: true });
    
    // Mock fetch
    global.fetch = mockApiCall;
    
    const formData = {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com'
    };
    
    render(<TestForm />);
    
    await FormTestUtils.fillForm(formData);
    await FormTestUtils.submitForm();
    
    await waitFor(() => {
      expect(mockApiCall).toHaveBeenCalledWith('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
    });
  });

  test('should handle file upload', async () => {
    const user = userEvent.setup();
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    
    render(<FileUploadForm />);
    
    const fileInput = screen.getByLabelText('Upload File');
    await user.upload(fileInput, file);
    
    expect(fileInput.files[0]).toBe(file);
    expect(fileInput.files).toHaveLength(1);
  });
});
{% endraw %}
{% endraw %}
```

### Visual Regression Testing

```jsx
// Visual testing with Playwright
import { test, expect } from '@playwright/test';

test.describe('Form Visual Tests', () => {
  test('should match baseline form appearance', async ({ page }) => {
    await page.goto('/form');
    
    // Wait for form to load
    await page.waitForSelector('.form-container');
    
    // Take screenshot
    await expect(page.locator('.form-container')).toHaveScreenshot('baseline-form.png');
  });

  test('should show validation errors correctly', async ({ page }) => {
    await page.goto('/form');
    
    // Submit empty form
    await page.click('button[type="submit"]');
    
    // Wait for validation errors
    await page.waitForSelector('.error', { state: 'visible' });
    
    // Screenshot with errors
    await expect(page.locator('.form-container')).toHaveScreenshot('form-with-errors.png');
  });

  test('should handle responsive layout', async ({ page }) => {
    // Test mobile layout
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/form');
    
    await expect(page.locator('.form-container')).toHaveScreenshot('form-mobile.png');
    
    // Test tablet layout
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    
    await expect(page.locator('.form-container')).toHaveScreenshot('form-tablet.png');
  });
});
```

## 📊 Performance Monitoring

### Real-Time Performance Tracking

```jsx
{% raw %}
{% raw %}
// Performance monitoring service
class FormPerformanceMonitor {
  constructor() {
    this.metrics = {
      renderTimes: [],
      validationTimes: [],
      submissionTimes: [],
      errorRates: {},
      userInteractions: []
    };
    this.observers = new Set();
  }

  trackRenderTime(componentName, duration) {
    this.metrics.renderTimes.push({
      component: componentName,
      duration,
      timestamp: Date.now()
    });
    
    this.notifyObservers('renderTime', { componentName, duration });
  }

  trackValidationTime(fieldName, duration) {
    this.metrics.validationTimes.push({
      field: fieldName,
      duration,
      timestamp: Date.now()
    });
    
    this.notifyObservers('validationTime', { fieldName, duration });
  }

  trackSubmissionTime(duration, success) {
    this.metrics.submissionTimes.push({
      duration,
      success,
      timestamp: Date.now()
    });
    
    this.notifyObservers('submissionTime', { duration, success });
  }

  trackError(errorType, context) {
    if (!this.metrics.errorRates[errorType]) {
      this.metrics.errorRates[errorType] = 0;
    }
    this.metrics.errorRates[errorType]++;
    
    this.notifyObservers('error', { errorType, context });
  }

  trackUserInteraction(interaction) {
    this.metrics.userInteractions.push({
      ...interaction,
      timestamp: Date.now()
    });
  }

  subscribe(observer) {
    this.observers.add(observer);
    return () => this.observers.delete(observer);
  }

  notifyObservers(eventType, data) {
    this.observers.forEach(observer => {
      try {
        observer(eventType, data);
      } catch (error) {
        console.error('Observer error:', error);
      }
    });
  }

  getReport() {
    return {
      averageRenderTime: this.calculateAverage(this.metrics.renderTimes, 'duration'),
      averageValidationTime: this.calculateAverage(this.metrics.validationTimes, 'duration'),
      averageSubmissionTime: this.calculateAverage(this.metrics.submissionTimes, 'duration'),
      errorRates: { ...this.metrics.errorRates },
      totalInteractions: this.metrics.userInteractions.length
    };
  }

  calculateAverage(array, property) {
    if (array.length === 0) return 0;
    return array.reduce((sum, item) => sum + item[property], 0) / array.length;
  }
}

const performanceMonitor = new FormPerformanceMonitor();

// Performance monitoring hook
const usePerformanceMonitoring = (componentName) => {
  const renderCount = useRef(0);
  const startTime = useRef(performance.now());

  useEffect(() => {
    renderCount.current++;
    const renderTime = performance.now() - startTime.current;
    performanceMonitor.trackRenderTime(componentName, renderTime);
    startTime.current = performance.now();
  });

  const trackValidation = useCallback((fieldName, validationStart) => {
    const duration = performance.now() - validationStart;
    performanceMonitor.trackValidationTime(fieldName, duration);
  }, []);

  const trackSubmission = useCallback((submissionStart, success) => {
    const duration = performance.now() - submissionStart;
    performanceMonitor.trackSubmissionTime(duration, success);
  }, []);

  const trackError = useCallback((errorType, context) => {
    performanceMonitor.trackError(errorType, context);
  }, []);

  const trackInteraction = useCallback((interaction) => {
    performanceMonitor.trackUserInteraction(interaction);
  }, []);

  return {
    trackValidation,
    trackSubmission,
    trackError,
    trackInteraction,
    renderCount: renderCount.current
  };
};

// Performance dashboard component
const PerformanceDashboard = () => {
  const [metrics, setMetrics] = useState(performanceMonitor.getReport());
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const unsubscribe = performanceMonitor.subscribe((eventType, data) => {
      // Update metrics
      setMetrics(performanceMonitor.getReport());
      
      // Check for performance alerts
      if (eventType === 'renderTime' && data.duration > 100) {
        setAlerts(prev => [...prev, {
          type: 'warning',
          message: `Slow render detected: ${data.componentName} (${data.duration}ms)`,
          timestamp: Date.now()
        }]);
      }
      
      if (eventType === 'validationTime' && data.duration > 500) {
        setAlerts(prev => [...prev, {
          type: 'warning',
          message: `Slow validation: ${data.fieldName} (${data.duration}ms)`,
          timestamp: Date.now()
        }]);
      }
    });

    return unsubscribe;
  }, []);

  return (
    <div className="performance-dashboard">
      <h3>Form Performance Metrics</h3>
      
      <div className="metrics-grid">
        <div className="metric">
          <h4>Average Render Time</h4>
          <span className={metrics.averageRenderTime > 50 ? 'warning' : 'good'}>
            {metrics.averageRenderTime.toFixed(2)}ms
          </span>
        </div>
        
        <div className="metric">
          <h4>Average Validation Time</h4>
          <span className={metrics.averageValidationTime > 200 ? 'warning' : 'good'}>
            {metrics.averageValidationTime.toFixed(2)}ms
          </span>
        </div>
        
        <div className="metric">
          <h4>Average Submission Time</h4>
          <span className={metrics.averageSubmissionTime > 1000 ? 'warning' : 'good'}>
            {metrics.averageSubmissionTime.toFixed(2)}ms
          </span>
        </div>
        
        <div className="metric">
          <h4>Total Interactions</h4>
          <span>{metrics.totalInteractions}</span>
        </div>
      </div>
      
      {alerts.length > 0 && (
        <div className="alerts">
          <h4>Performance Alerts</h4>
          {alerts.slice(-5).map((alert, index) => (
            <div key={index} className={`alert ${alert.type}`}>
              {alert.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
{% endraw %}
{% endraw %}
```

## 🛠 Debugging Tools

### Advanced Form Debugging

```jsx
{% raw %}
{% raw %}
// Form debugging context
const FormDebugContext = createContext();

const FormDebugProvider = ({ children, enabled = process.env.NODE_ENV === 'development' }) => {
  const [debugInfo, setDebugInfo] = useState({
    formState: {},
    validationHistory: [],
    renderHistory: [],
    performanceMetrics: {}
  });

  const logFormState = useCallback((state) => {
    if (!enabled) return;
    
    setDebugInfo(prev => ({
      ...prev,
      formState: state,
      renderHistory: [...prev.renderHistory, {
        timestamp: Date.now(),
        state: JSON.stringify(state)
      }].slice(-20) // Keep last 20 renders
    }));
  }, [enabled]);

  const logValidation = useCallback((field, result) => {
    if (!enabled) return;
    
    setDebugInfo(prev => ({
      ...prev,
      validationHistory: [...prev.validationHistory, {
        timestamp: Date.now(),
        field,
        result
      }].slice(-50) // Keep last 50 validations
    }));
  }, [enabled]);

  return (
    <FormDebugContext.Provider value={{
      debugInfo,
      logFormState,
      logValidation,
      enabled
    }}>
      {children}
      {enabled && <FormDebugPanel />}
    </FormDebugContext.Provider>
  );
};

// Debug panel component
const FormDebugPanel = () => {
  const { debugInfo } = useContext(FormDebugContext);
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('state');

  return (
    <div className={`debug-panel ${isOpen ? 'open' : 'closed'}`}>
      <button 
        className="debug-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        🐛
      </button>
      
      {isOpen && (
        <div className="debug-content">
          <div className="debug-tabs">
            <button 
              className={activeTab === 'state' ? 'active' : ''}
              onClick={() => setActiveTab('state')}
            >
              State
            </button>
            <button 
              className={activeTab === 'validation' ? 'active' : ''}
              onClick={() => setActiveTab('validation')}
            >
              Validation
            </button>
            <button 
              className={activeTab === 'performance' ? 'active' : ''}
              onClick={() => setActiveTab('performance')}
            >
              Performance
            </button>
          </div>
          
          <div className="debug-panel-content">
            {activeTab === 'state' && (
              <pre>{JSON.stringify(debugInfo.formState, null, 2)}</pre>
            )}
            
            {activeTab === 'validation' && (
              <div className="validation-history">
                {debugInfo.validationHistory.map((entry, index) => (
                  <div key={index} className="validation-entry">
                    <strong>{entry.field}:</strong> {entry.result}
                    <small>{new Date(entry.timestamp).toLocaleTimeString()}</small>
                  </div>
                ))}
              </div>
            )}
            
            {activeTab === 'performance' && (
              <PerformanceDashboard />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Debug-aware form hook
const useDebugForm = (options) => {
  const { logFormState, logValidation, enabled } = useContext(FormDebugContext) || {};
  const form = useForm(options);

  // Log form state changes
  useEffect(() => {
    if (enabled && logFormState) {
      logFormState({
        values: form.getValues(),
        errors: form.formState.errors,
        isDirty: form.formState.isDirty,
        isValid: form.formState.isValid
      });
    }
  }, [form.formState, enabled, logFormState]);

  return form;
};
{% endraw %}
{% endraw %}
```

## 📈 Best Practices Summary

### Performance Guidelines

1. **Rendering Optimization**
   - Use React.memo for expensive components
   - Implement virtualization for large forms
   - Lazy load heavy components

2. **Memory Management**
   - Clean up subscriptions and timeouts
   - Use object pooling for frequent operations
   - Implement proper caching strategies

3. **Network Optimization**
   - Batch API requests when possible
   - Implement optimistic updates
   - Cache validation results

4. **Testing Strategy**
   - Test performance with realistic data volumes
   - Include accessibility testing
   - Monitor for memory leaks

5. **Production Monitoring**
   - Track real-user performance metrics
   - Set up alerts for performance regressions
   - Monitor error rates and user flows

This comprehensive guide provides the foundation for building high-performance, well-tested React forms that scale to production requirements.
