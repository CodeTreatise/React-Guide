# Advanced Forms and Validation Deep Dive

> **Advanced Implementation Patterns and Real-World Solutions**

## 🎯 Overview

This guide covers advanced form patterns, performance optimization techniques, complex validation scenarios, and real-world implementation strategies for React forms.

## 📋 Table of Contents

1. [Advanced Form Architecture](#advanced-form-architecture)
2. [Custom Form Hook Patterns](#custom-form-hook-patterns)
3. [Complex Validation Scenarios](#complex-validation-scenarios)
4. [Form Performance Optimization](#form-performance-optimization)
5. [Multi-Step Form Implementation](#multi-step-form-implementation)
6. [Form State Synchronization](#form-state-synchronization)
7. [Advanced File Upload Patterns](#advanced-file-upload-patterns)
8. [Form Testing Strategies](#form-testing-strategies)
9. [Real-World Case Studies](#real-world-case-studies)

## 🏗 Advanced Form Architecture

### Form Context Pattern

```jsx
import React, { createContext, useContext, useReducer, useCallback } from 'react';

// Form Context
const FormContext = createContext();

// Form Actions
const FORM_ACTIONS = {
  SET_FIELD: 'SET_FIELD',
  SET_ERROR: 'SET_ERROR',
  SET_TOUCHED: 'SET_TOUCHED',
  SET_SUBMITTING: 'SET_SUBMITTING',
  RESET_FORM: 'RESET_FORM',
  SET_FIELD_ARRAY: 'SET_FIELD_ARRAY'
};

// Form Reducer
function formReducer(state, action) {
  switch (action.type) {
    case FORM_ACTIONS.SET_FIELD:
      return {
        ...state,
        values: {
          ...state.values,
          [action.field]: action.value
        }
      };
      
    case FORM_ACTIONS.SET_ERROR:
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.field]: action.error
        }
      };
      
    case FORM_ACTIONS.SET_TOUCHED:
      return {
        ...state,
        touched: {
          ...state.touched,
          [action.field]: action.touched
        }
      };
      
    case FORM_ACTIONS.SET_SUBMITTING:
      return {
        ...state,
        isSubmitting: action.isSubmitting
      };
      
    case FORM_ACTIONS.RESET_FORM:
      return {
        ...state,
        values: action.initialValues || state.initialValues,
        errors: {},
        touched: {},
        isSubmitting: false
      };
      
    case FORM_ACTIONS.SET_FIELD_ARRAY:
      return {
        ...state,
        values: {
          ...state.values,
          [action.field]: action.array
        }
      };
      
    default:
      return state;
  }
}

// Form Provider Component
export function FormProvider({ 
  children, 
  initialValues = {}, 
  validationSchema,
  onSubmit 
}) {
  const [state, dispatch] = useReducer(formReducer, {
    values: initialValues,
    initialValues,
    errors: {},
    touched: {},
    isSubmitting: false
  });

  const setFieldValue = useCallback((field, value) => {
    dispatch({ type: FORM_ACTIONS.SET_FIELD, field, value });
    
    // Validate field if validation schema exists and field is touched
    if (validationSchema && state.touched[field]) {
      validateField(field, value);
    }
  }, [state.touched, validationSchema]);

  const setFieldError = useCallback((field, error) => {
    dispatch({ type: FORM_ACTIONS.SET_ERROR, field, error });
  }, []);

  const setFieldTouched = useCallback((field, touched = true) => {
    dispatch({ type: FORM_ACTIONS.SET_TOUCHED, field, touched });
  }, []);

  const validateField = useCallback(async (field, value) => {
    if (!validationSchema) return;
    
    try {
      await validationSchema.validateAt(field, { [field]: value });
      setFieldError(field, '');
    } catch (error) {
      setFieldError(field, error.message);
    }
  }, [validationSchema, setFieldError]);

  const validateForm = useCallback(async () => {
    if (!validationSchema) return true;
    
    try {
      await validationSchema.validate(state.values, { abortEarly: false });
      dispatch({ type: FORM_ACTIONS.SET_ERROR, field: '', error: {} });
      return true;
    } catch (error) {
      const errors = {};
      error.inner.forEach(err => {
        errors[err.path] = err.message;
      });
      
      Object.keys(errors).forEach(field => {
        setFieldError(field, errors[field]);
      });
      
      return false;
    }
  }, [state.values, validationSchema, setFieldError]);

  const handleSubmit = useCallback(async (e) => {
    if (e) e.preventDefault();
    
    dispatch({ type: FORM_ACTIONS.SET_SUBMITTING, isSubmitting: true });
    
    // Mark all fields as touched
    Object.keys(state.values).forEach(field => {
      setFieldTouched(field, true);
    });
    
    const isValid = await validateForm();
    
    if (isValid && onSubmit) {
      try {
        await onSubmit(state.values);
      } catch (error) {
        console.error('Form submission error:', error);
      }
    }
    
    dispatch({ type: FORM_ACTIONS.SET_SUBMITTING, isSubmitting: false });
  }, [state.values, validateForm, onSubmit, setFieldTouched]);

  const resetForm = useCallback((newInitialValues) => {
    dispatch({ 
      type: FORM_ACTIONS.RESET_FORM, 
      initialValues: newInitialValues 
    });
  }, []);

  const value = {
    ...state,
    setFieldValue,
    setFieldError,
    setFieldTouched,
    validateField,
    validateForm,
    handleSubmit,
    resetForm
  };

  return (
    <FormContext.Provider value={value}>
      {children}
    </FormContext.Provider>
  );
}

// Custom hook to use form context
export function useForm() {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useForm must be used within a FormProvider');
  }
  return context;
}

// Field Component
export function Field({ name, validate, children, ...props }) {
  const { values, errors, touched, setFieldValue, setFieldTouched, validateField } = useForm();
  
  const value = values[name] || '';
  const error = errors[name];
  const isTouched = touched[name];

  const handleChange = useCallback(async (e) => {
    const newValue = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFieldValue(name, newValue);
    
    if (validate) {
      const fieldError = await validate(newValue, values);
      if (fieldError) {
        setFieldError(name, fieldError);
      }
    }
  }, [name, setFieldValue, validate, values]);

  const handleBlur = useCallback(() => {
    setFieldTouched(name, true);
    validateField(name, value);
  }, [name, setFieldTouched, validateField, value]);

  if (typeof children === 'function') {
    return children({
      field: { name, value, onChange: handleChange, onBlur: handleBlur },
      meta: { error, touched: isTouched }
    });
  }

  return React.cloneElement(children, {
    name,
    value,
    onChange: handleChange,
    onBlur: handleBlur,
    ...props
  });
}
```

### Usage Example

```jsx
import * as yup from 'yup';

const validationSchema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  age: yup.number().positive().integer().required('Age is required')
});

function MyForm() {
  const handleSubmit = async (values) => {
    console.log('Form submitted:', values);
    // API call here
  };

  return (
    <FormProvider 
      initialValues={{ name: '', email: '', age: '' }}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      <FormContent />
    </FormProvider>
  );
}

function FormContent() {
  const { handleSubmit, isSubmitting } = useForm();

  return (
    <form onSubmit={handleSubmit}>
      <Field name="name">
        {({ field, meta }) => (
          <div>
            <input {...field} type="text" placeholder="Name" />
            {meta.touched && meta.error && (
              <span className="error">{meta.error}</span>
            )}
          </div>
        )}
      </Field>
      
      <Field name="email">
        {({ field, meta }) => (
          <div>
            <input {...field} type="email" placeholder="Email" />
            {meta.touched && meta.error && (
              <span className="error">{meta.error}</span>
            )}
          </div>
        )}
      </Field>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

## 🎣 Custom Form Hook Patterns

### Advanced useForm Hook

```jsx
import { useState, useCallback, useRef, useMemo } from 'react';

export function useAdvancedForm({
  initialValues = {},
  validationSchema,
  validateOnChange = true,
  validateOnBlur = true,
  onSubmit
}) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitCount, setSubmitCount] = useState(0);
  
  const fieldsRef = useRef({});
  const validationTimeouts = useRef({});

  // Memoized computed values
  const computedValues = useMemo(() => {
    const hasErrors = Object.keys(errors).some(key => errors[key]);
    const isDirty = JSON.stringify(values) !== JSON.stringify(initialValues);
    const touchedFields = Object.keys(touched).filter(key => touched[key]);
    const isValid = !hasErrors && touchedFields.length > 0;
    
    return {
      hasErrors,
      isDirty,
      isValid,
      touchedFields
    };
  }, [values, errors, touched, initialValues]);

  // Debounced validation
  const debouncedValidate = useCallback((fieldName, value, delay = 300) => {
    if (validationTimeouts.current[fieldName]) {
      clearTimeout(validationTimeouts.current[fieldName]);
    }
    
    validationTimeouts.current[fieldName] = setTimeout(() => {
      validateSingleField(fieldName, value);
    }, delay);
  }, []);

  const validateSingleField = useCallback(async (fieldName, value) => {
    if (!validationSchema) return;
    
    try {
      await validationSchema.validateAt(fieldName, { [fieldName]: value });
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        [fieldName]: error.message
      }));
    }
  }, [validationSchema]);

  const validateForm = useCallback(async () => {
    if (!validationSchema) return {};
    
    try {
      await validationSchema.validate(values, { abortEarly: false });
      setErrors({});
      return {};
    } catch (error) {
      const newErrors = {};
      error.inner.forEach(err => {
        newErrors[err.path] = err.message;
      });
      setErrors(newErrors);
      return newErrors;
    }
  }, [values, validationSchema]);

  const setFieldValue = useCallback((fieldName, value, shouldValidate = validateOnChange) => {
    setValues(prev => ({
      ...prev,
      [fieldName]: value
    }));
    
    if (shouldValidate && touched[fieldName]) {
      debouncedValidate(fieldName, value);
    }
  }, [touched, validateOnChange, debouncedValidate]);

  const setFieldTouched = useCallback((fieldName, isTouched = true, shouldValidate = validateOnBlur) => {
    setTouched(prev => ({
      ...prev,
      [fieldName]: isTouched
    }));
    
    if (isTouched && shouldValidate) {
      validateSingleField(fieldName, values[fieldName]);
    }
  }, [values, validateOnBlur, validateSingleField]);

  const setFieldError = useCallback((fieldName, error) => {
    setErrors(prev => ({
      ...prev,
      [fieldName]: error
    }));
  }, []);

  const resetForm = useCallback((newInitialValues = initialValues) => {
    setValues(newInitialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
    setSubmitCount(0);
    
    // Clear validation timeouts
    Object.values(validationTimeouts.current).forEach(timeout => {
      clearTimeout(timeout);
    });
    validationTimeouts.current = {};
  }, [initialValues]);

  const submitForm = useCallback(async () => {
    setIsSubmitting(true);
    setSubmitCount(prev => prev + 1);
    
    // Mark all fields as touched
    const allTouched = Object.keys(values).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setTouched(allTouched);
    
    // Validate form
    const validationErrors = await validateForm();
    
    if (Object.keys(validationErrors).length === 0) {
      try {
        if (onSubmit) {
          await onSubmit(values);
        }
      } catch (error) {
        console.error('Form submission error:', error);
      }
    }
    
    setIsSubmitting(false);
  }, [values, validateForm, onSubmit]);

  const getFieldProps = useCallback((fieldName) => {
    return {
      name: fieldName,
      value: values[fieldName] || '',
      onChange: (e) => {
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        setFieldValue(fieldName, value);
      },
      onBlur: () => setFieldTouched(fieldName, true),
      ref: (el) => {
        if (el) {
          fieldsRef.current[fieldName] = el;
        }
      }
    };
  }, [values, setFieldValue, setFieldTouched]);

  const getFieldMeta = useCallback((fieldName) => {
    return {
      value: values[fieldName],
      error: errors[fieldName],
      touched: touched[fieldName],
      dirty: values[fieldName] !== initialValues[fieldName]
    };
  }, [values, errors, touched, initialValues]);

  const focusField = useCallback((fieldName) => {
    const field = fieldsRef.current[fieldName];
    if (field && field.focus) {
      field.focus();
    }
  }, []);

  return {
    // Values and state
    values,
    errors,
    touched,
    isSubmitting,
    submitCount,
    
    // Computed values
    ...computedValues,
    
    // Actions
    setFieldValue,
    setFieldTouched,
    setFieldError,
    resetForm,
    submitForm,
    validateForm,
    
    // Helpers
    getFieldProps,
    getFieldMeta,
    focusField
  };
}
```

## 🔍 Complex Validation Scenarios

### Cross-Field Validation

```jsx
import * as yup from 'yup';

// Custom validation schema with cross-field validation
const registrationSchema = yup.object().shape({
  password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain uppercase, lowercase, and number'
    )
    .required('Password is required'),
    
  confirmPassword: yup
    .string()
    .oneOf([yup.ref('password')], 'Passwords must match')
    .required('Please confirm your password'),
    
  startDate: yup.date().required('Start date is required'),
  
  endDate: yup
    .date()
    .min(yup.ref('startDate'), 'End date must be after start date')
    .required('End date is required'),
    
  email: yup
    .string()
    .email('Invalid email format')
    .required('Email is required')
    .test('email-availability', 'Email is already taken', async function(value) {
      if (!value) return true;
      
      // Simulate API call
      const isAvailable = await checkEmailAvailability(value);
      return isAvailable;
    })
});

// Async field validation hook
function useAsyncValidation(validationFn, dependencies = []) {
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  
  const validate = useCallback(async (...args) => {
    setIsValidating(true);
    try {
      const result = await validationFn(...args);
      setValidationResult(result);
      return result;
    } catch (error) {
      setValidationResult({ error: error.message });
      return { error: error.message };
    } finally {
      setIsValidating(false);
    }
  }, dependencies);
  
  return { validate, isValidating, validationResult };
}

// Component with complex validation
function ComplexValidationForm() {
  const {
    values,
    errors,
    touched,
    getFieldProps,
    getFieldMeta,
    submitForm,
    isSubmitting
  } = useAdvancedForm({
    initialValues: {
      email: '',
      password: '',
      confirmPassword: '',
      startDate: '',
      endDate: ''
    },
    validationSchema: registrationSchema,
    onSubmit: async (values) => {
      console.log('Form submitted:', values);
    }
  });

  // Custom async validation for email
  const { validate: validateEmail, isValidating: isEmailValidating } = useAsyncValidation(
    async (email) => {
      const response = await fetch(`/api/validate-email?email=${email}`);
      const result = await response.json();
      return result;
    }
  );

  const handleEmailBlur = async () => {
    if (values.email && !errors.email) {
      await validateEmail(values.email);
    }
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); submitForm(); }}>
      <div className="form-field">
        <label>Email</label>
        <input
          {...getFieldProps('email')}
          type="email"
          onBlur={handleEmailBlur}
        />
        {isEmailValidating && <span>Checking email availability...</span>}
        {getFieldMeta('email').touched && getFieldMeta('email').error && (
          <span className="error">{getFieldMeta('email').error}</span>
        )}
      </div>
      
      <div className="form-field">
        <label>Password</label>
        <input {...getFieldProps('password')} type="password" />
        {getFieldMeta('password').touched && getFieldMeta('password').error && (
          <span className="error">{getFieldMeta('password').error}</span>
        )}
      </div>
      
      <div className="form-field">
        <label>Confirm Password</label>
        <input {...getFieldProps('confirmPassword')} type="password" />
        {getFieldMeta('confirmPassword').touched && getFieldMeta('confirmPassword').error && (
          <span className="error">{getFieldMeta('confirmPassword').error}</span>
        )}
      </div>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

### Conditional Validation

```jsx
// Dynamic validation based on form state
function createConditionalSchema(values) {
  let schema = yup.object().shape({
    userType: yup.string().required('User type is required'),
    name: yup.string().required('Name is required')
  });

  // Add conditional fields based on user type
  if (values.userType === 'business') {
    schema = schema.shape({
      companyName: yup.string().required('Company name is required'),
      taxId: yup.string().required('Tax ID is required'),
      businessAddress: yup.object().shape({
        street: yup.string().required('Street is required'),
        city: yup.string().required('City is required'),
        zipCode: yup.string().required('Zip code is required')
      })
    });
  } else if (values.userType === 'individual') {
    schema = schema.shape({
      dateOfBirth: yup.date().required('Date of birth is required'),
      ssn: yup.string().required('SSN is required')
    });
  }

  return schema;
}

function ConditionalForm() {
  const [currentSchema, setCurrentSchema] = useState(null);
  
  const form = useAdvancedForm({
    initialValues: {
      userType: '',
      name: '',
      companyName: '',
      taxId: '',
      dateOfBirth: '',
      ssn: ''
    },
    validationSchema: currentSchema,
    onSubmit: async (values) => {
      console.log('Form submitted:', values);
    }
  });

  // Update schema when user type changes
  useEffect(() => {
    const newSchema = createConditionalSchema(form.values);
    setCurrentSchema(newSchema);
  }, [form.values.userType]);

  return (
    <form onSubmit={(e) => { e.preventDefault(); form.submitForm(); }}>
      <div>
        <label>User Type</label>
        <select {...form.getFieldProps('userType')}>
          <option value="">Select type</option>
          <option value="individual">Individual</option>
          <option value="business">Business</option>
        </select>
      </div>
      
      <div>
        <label>Name</label>
        <input {...form.getFieldProps('name')} type="text" />
      </div>
      
      {form.values.userType === 'business' && (
        <>
          <div>
            <label>Company Name</label>
            <input {...form.getFieldProps('companyName')} type="text" />
          </div>
          <div>
            <label>Tax ID</label>
            <input {...form.getFieldProps('taxId')} type="text" />
          </div>
        </>
      )}
      
      {form.values.userType === 'individual' && (
        <>
          <div>
            <label>Date of Birth</label>
            <input {...form.getFieldProps('dateOfBirth')} type="date" />
          </div>
          <div>
            <label>SSN</label>
            <input {...form.getFieldProps('ssn')} type="text" />
          </div>
        </>
      )}
      
      <button type="submit" disabled={form.isSubmitting}>
        Submit
      </button>
    </form>
  );
}
```

## ⚡ Form Performance Optimization

### Memoized Form Components

```jsx
import React, { memo, useCallback, useMemo } from 'react';

// Memoized field component
const FormField = memo(({ 
  name, 
  type = 'text', 
  label, 
  value, 
  error, 
  touched, 
  onChange, 
  onBlur,
  ...props 
}) => {
  const fieldId = useMemo(() => `field-${name}`, [name]);
  
  const handleChange = useCallback((e) => {
    const newValue = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    onChange(name, newValue);
  }, [name, onChange]);

  const handleBlur = useCallback(() => {
    onBlur(name);
  }, [name, onBlur]);

  return (
    <div className="form-field">
      <label htmlFor={fieldId}>{label}</label>
      <input
        id={fieldId}
        name={name}
        type={type}
        value={value || ''}
        onChange={handleChange}
        onBlur={handleBlur}
        aria-invalid={touched && error ? 'true' : 'false'}
        aria-describedby={touched && error ? `${fieldId}-error` : undefined}
        {...props}
      />
      {touched && error && (
        <span id={`${fieldId}-error`} className="error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
});

// Optimized form with field memoization
function OptimizedForm() {
  const {
    values,
    errors,
    touched,
    setFieldValue,
    setFieldTouched,
    handleSubmit,
    isSubmitting
  } = useForm({
    initialValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      zipCode: ''
    }
  });

  // Memoized change handler to prevent re-renders
  const handleFieldChange = useCallback((fieldName, value) => {
    setFieldValue(fieldName, value);
  }, [setFieldValue]);

  const handleFieldBlur = useCallback((fieldName) => {
    setFieldTouched(fieldName, true);
  }, [setFieldTouched]);

  // Memoized field configurations
  const fieldConfigs = useMemo(() => [
    { name: 'firstName', label: 'First Name', type: 'text' },
    { name: 'lastName', label: 'Last Name', type: 'text' },
    { name: 'email', label: 'Email', type: 'email' },
    { name: 'phone', label: 'Phone', type: 'tel' },
    { name: 'address', label: 'Address', type: 'text' },
    { name: 'city', label: 'City', type: 'text' },
    { name: 'zipCode', label: 'Zip Code', type: 'text' }
  ], []);

  return (
    <form onSubmit={handleSubmit}>
      {fieldConfigs.map(({ name, label, type }) => (
        <FormField
          key={name}
          name={name}
          label={label}
          type={type}
          value={values[name]}
          error={errors[name]}
          touched={touched[name]}
          onChange={handleFieldChange}
          onBlur={handleFieldBlur}
        />
      ))}
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

## 📝 Multi-Step Form Implementation

```jsx
import React, { useState, useMemo } from 'react';

// Multi-step form hook
function useMultiStepForm(steps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  
  const currentStep = useMemo(() => steps[currentStepIndex], [steps, currentStepIndex]);
  
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === steps.length - 1;
  
  const goToNext = () => {
    if (!isLastStep) {
      setCurrentStepIndex(prev => prev + 1);
    }
  };
  
  const goToPrevious = () => {
    if (!isFirstStep) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };
  
  const goToStep = (stepIndex) => {
    if (stepIndex >= 0 && stepIndex < steps.length) {
      setCurrentStepIndex(stepIndex);
    }
  };
  
  return {
    currentStep,
    currentStepIndex,
    steps,
    isFirstStep,
    isLastStep,
    goToNext,
    goToPrevious,
    goToStep
  };
}

// Step components
const PersonalInfoStep = ({ values, errors, touched, onChange, onBlur }) => (
  <div className="step-content">
    <h2>Personal Information</h2>
    <FormField
      name="firstName"
      label="First Name"
      value={values.firstName}
      error={errors.firstName}
      touched={touched.firstName}
      onChange={onChange}
      onBlur={onBlur}
    />
    <FormField
      name="lastName"
      label="Last Name"
      value={values.lastName}
      error={errors.lastName}
      touched={touched.lastName}
      onChange={onChange}
      onBlur={onBlur}
    />
    <FormField
      name="email"
      label="Email"
      type="email"
      value={values.email}
      error={errors.email}
      touched={touched.email}
      onChange={onChange}
      onBlur={onBlur}
    />
  </div>
);

const AddressInfoStep = ({ values, errors, touched, onChange, onBlur }) => (
  <div className="step-content">
    <h2>Address Information</h2>
    <FormField
      name="address"
      label="Street Address"
      value={values.address}
      error={errors.address}
      touched={touched.address}
      onChange={onChange}
      onBlur={onBlur}
    />
    <FormField
      name="city"
      label="City"
      value={values.city}
      error={errors.city}
      touched={touched.city}
      onChange={onChange}
      onBlur={onBlur}
    />
    <FormField
      name="zipCode"
      label="Zip Code"
      value={values.zipCode}
      error={errors.zipCode}
      touched={touched.zipCode}
      onChange={onChange}
      onBlur={onBlur}
    />
  </div>
);

const ReviewStep = ({ values }) => (
  <div className="step-content">
    <h2>Review Your Information</h2>
    <div className="review-section">
      <h3>Personal Information</h3>
      <p><strong>Name:</strong> {values.firstName} {values.lastName}</p>
      <p><strong>Email:</strong> {values.email}</p>
    </div>
    <div className="review-section">
      <h3>Address</h3>
      <p><strong>Address:</strong> {values.address}</p>
      <p><strong>City:</strong> {values.city}</p>
      <p><strong>Zip Code:</strong> {values.zipCode}</p>
    </div>
  </div>
);

// Main multi-step form component
function MultiStepRegistrationForm() {
  const steps = [
    { component: PersonalInfoStep, title: 'Personal Info', fields: ['firstName', 'lastName', 'email'] },
    { component: AddressInfoStep, title: 'Address', fields: ['address', 'city', 'zipCode'] },
    { component: ReviewStep, title: 'Review', fields: [] }
  ];

  const {
    currentStep,
    currentStepIndex,
    isFirstStep,
    isLastStep,
    goToNext,
    goToPrevious,
    goToStep
  } = useMultiStepForm(steps);

  const {
    values,
    errors,
    touched,
    setFieldValue,
    setFieldTouched,
    validateForm,
    submitForm,
    isSubmitting
  } = useAdvancedForm({
    initialValues: {
      firstName: '',
      lastName: '',
      email: '',
      address: '',
      city: '',
      zipCode: ''
    },
    validationSchema: registrationSchema,
    onSubmit: async (values) => {
      console.log('Multi-step form submitted:', values);
    }
  });

  const handleNext = async () => {
    // Validate current step fields
    const currentStepFields = currentStep.fields;
    let isStepValid = true;
    
    for (const field of currentStepFields) {
      setFieldTouched(field, true);
      if (errors[field]) {
        isStepValid = false;
      }
    }
    
    if (isStepValid) {
      goToNext();
    }
  };

  const handleSubmit = async () => {
    const formErrors = await validateForm();
    if (Object.keys(formErrors).length === 0) {
      await submitForm();
    }
  };

  return (
    <div className="multi-step-form">
      {/* Progress indicator */}
      <div className="progress-indicator">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`progress-step ${index <= currentStepIndex ? 'active' : ''}`}
            onClick={() => goToStep(index)}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-title">{step.title}</div>
          </div>
        ))}
      </div>

      {/* Current step content */}
      <div className="step-container">
        <currentStep.component
          values={values}
          errors={errors}
          touched={touched}
          onChange={setFieldValue}
          onBlur={(field) => setFieldTouched(field, true)}
        />
      </div>

      {/* Navigation buttons */}
      <div className="step-navigation">
        {!isFirstStep && (
          <button type="button" onClick={goToPrevious}>
            Previous
          </button>
        )}
        
        {!isLastStep ? (
          <button type="button" onClick={handleNext}>
            Next
          </button>
        ) : (
          <button 
            type="button" 
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        )}
      </div>
    </div>
  );
}
```

## 🔄 Form State Synchronization

### URL State Synchronization

```jsx
import { useSearchParams } from 'react-router-dom';

function useFormWithUrlSync(initialValues) {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Initialize form values from URL params
  const getInitialValues = useCallback(() => {
    const urlValues = { ...initialValues };
    
    for (const [key, value] of searchParams.entries()) {
      if (key in initialValues) {
        // Handle different data types
        if (typeof initialValues[key] === 'boolean') {
          urlValues[key] = value === 'true';
        } else if (typeof initialValues[key] === 'number') {
          urlValues[key] = Number(value);
        } else {
          urlValues[key] = value;
        }
      }
    }
    
    return urlValues;
  }, [initialValues, searchParams]);

  const form = useAdvancedForm({
    initialValues: getInitialValues()
  });

  // Sync form values to URL
  useEffect(() => {
    const params = new URLSearchParams();
    
    Object.entries(form.values).forEach(([key, value]) => {
      if (value !== initialValues[key] && value !== '') {
        params.set(key, String(value));
      }
    });
    
    setSearchParams(params);
  }, [form.values, initialValues, setSearchParams]);

  return form;
}
```

### Local Storage Persistence

```jsx
function useFormWithPersistence(key, initialValues) {
  const [isLoaded, setIsLoaded] = useState(false);
  
  const form = useAdvancedForm({
    initialValues,
    onSubmit: async (values) => {
      // Clear saved form data on successful submit
      localStorage.removeItem(key);
      // Handle submission
    }
  });

  // Load form data from localStorage on mount
  useEffect(() => {
    try {
      const savedData = localStorage.getItem(key);
      if (savedData) {
        const parsedData = JSON.parse(savedData);
        Object.entries(parsedData).forEach(([field, value]) => {
          form.setFieldValue(field, value, false);
        });
      }
    } catch (error) {
      console.error('Error loading form data:', error);
    } finally {
      setIsLoaded(true);
    }
  }, [key]);

  // Save form data to localStorage on change
  useEffect(() => {
    if (!isLoaded) return;
    
    const timeoutId = setTimeout(() => {
      try {
        localStorage.setItem(key, JSON.stringify(form.values));
      } catch (error) {
        console.error('Error saving form data:', error);
      }
    }, 1000); // Debounce saves

    return () => clearTimeout(timeoutId);
  }, [form.values, key, isLoaded]);

  return { ...form, isLoaded };
}
```

## 📁 Advanced File Upload Patterns

### Chunked File Upload

```jsx
function useChunkedFileUpload() {
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadErrors, setUploadErrors] = useState({});
  const [activeUploads, setActiveUploads] = useState(new Set());

  const uploadFileInChunks = useCallback(async (file, options = {}) => {
    const {
      chunkSize = 1024 * 1024, // 1MB chunks
      maxRetries = 3,
      onProgress,
      onComplete,
      onError
    } = options;

    const fileId = `${file.name}-${file.size}-${file.lastModified}`;
    const totalChunks = Math.ceil(file.size / chunkSize);
    
    setActiveUploads(prev => new Set([...prev, fileId]));
    setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

    try {
      // Initialize upload session
      const initResponse = await fetch('/api/upload/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fileName: file.name,
          fileSize: file.size,
          totalChunks,
          mimeType: file.type
        })
      });

      const { uploadId } = await initResponse.json();
      const uploadedChunks = [];

      // Upload chunks
      for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        const start = chunkIndex * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);

        let retryCount = 0;
        let chunkUploaded = false;

        while (retryCount < maxRetries && !chunkUploaded) {
          try {
            const formData = new FormData();
            formData.append('chunk', chunk);
            formData.append('chunkIndex', chunkIndex);
            formData.append('uploadId', uploadId);

            const response = await fetch('/api/upload/chunk', {
              method: 'POST',
              body: formData
            });

            if (response.ok) {
              const chunkResult = await response.json();
              uploadedChunks.push(chunkResult);
              chunkUploaded = true;

              // Update progress
              const progress = Math.round(((chunkIndex + 1) / totalChunks) * 100);
              setUploadProgress(prev => ({ ...prev, [fileId]: progress }));
              
              if (onProgress) {
                onProgress(progress, chunkIndex + 1, totalChunks);
              }
            } else {
              throw new Error(`Chunk upload failed: ${response.statusText}`);
            }
          } catch (error) {
            retryCount++;
            if (retryCount >= maxRetries) {
              throw error;
            }
            // Exponential backoff
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
          }
        }
      }

      // Complete upload
      const completeResponse = await fetch('/api/upload/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          uploadId,
          chunks: uploadedChunks
        })
      });

      const result = await completeResponse.json();
      
      if (onComplete) {
        onComplete(result);
      }

      return result;
    } catch (error) {
      setUploadErrors(prev => ({ ...prev, [fileId]: error.message }));
      if (onError) {
        onError(error);
      }
      throw error;
    } finally {
      setActiveUploads(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
    }
  }, []);

  const cancelUpload = useCallback((fileId) => {
    setActiveUploads(prev => {
      const newSet = new Set(prev);
      newSet.delete(fileId);
      return newSet;
    });
    
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileId];
      return newProgress;
    });
  }, []);

  return {
    uploadFileInChunks,
    cancelUpload,
    uploadProgress,
    uploadErrors,
    activeUploads: Array.from(activeUploads)
  };
}
```

## 🧪 Form Testing Strategies

### Comprehensive Form Testing

```javascript
// Form testing utilities
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

export const formTestUtils = {
  // Fill form fields
  async fillForm(form, values) {
    for (const [field, value] of Object.entries(values)) {
      const input = screen.getByLabelText(new RegExp(field, 'i'));
      await userEvent.clear(input);
      await userEvent.type(input, value);
    }
  },

  // Submit form
  async submitForm() {
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await userEvent.click(submitButton);
  },

  // Check validation errors
  expectValidationError(fieldName, errorMessage) {
    const errorElement = screen.getByText(errorMessage);
    expect(errorElement).toBeInTheDocument();
  },

  // Check field values
  expectFieldValue(fieldName, value) {
    const field = screen.getByLabelText(new RegExp(fieldName, 'i'));
    expect(field).toHaveValue(value);
  }
};

// Test suite example
describe('Advanced Form Component', () => {
  const mockSubmit = jest.fn();
  
  beforeEach(() => {
    mockSubmit.mockClear();
  });

  test('renders all form fields', () => {
    render(<AdvancedForm onSubmit={mockSubmit} />);
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(<AdvancedForm onSubmit={mockSubmit} />);
    
    await formTestUtils.submitForm();
    
    await waitFor(() => {
      formTestUtils.expectValidationError('name', 'Name is required');
      formTestUtils.expectValidationError('email', 'Email is required');
    });
    
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  test('validates email format', async () => {
    render(<AdvancedForm onSubmit={mockSubmit} />);
    
    await formTestUtils.fillForm({
      name: 'John Doe',
      email: 'invalid-email'
    });
    
    await formTestUtils.submitForm();
    
    await waitFor(() => {
      formTestUtils.expectValidationError('email', 'Invalid email format');
    });
  });

  test('submits form with valid data', async () => {
    const validData = {
      name: 'John Doe',
      email: 'john@example.com'
    };
    
    render(<AdvancedForm onSubmit={mockSubmit} />);
    
    await formTestUtils.fillForm(validData);
    await formTestUtils.submitForm();
    
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(validData);
    });
  });

  test('handles async validation', async () => {
    // Mock API response
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ available: false })
      })
    );
    
    render(<AdvancedForm onSubmit={mockSubmit} />);
    
    const emailField = screen.getByLabelText(/email/i);
    await userEvent.type(emailField, 'taken@example.com');
    fireEvent.blur(emailField);
    
    await waitFor(() => {
      formTestUtils.expectValidationError('email', 'Email is already taken');
    });
    
    global.fetch.mockRestore();
  });
});
```

## 🏆 Real-World Case Studies

### E-commerce Checkout Form

```jsx
function EcommerceCheckoutForm({ cart, onSubmit }) {
  const [currentStep, setCurrentStep] = useState('shipping');
  const [paymentMethod, setPaymentMethod] = useState('card');
  
  const checkoutSchema = yup.object().shape({
    // Shipping information
    shipping: yup.object().shape({
      firstName: yup.string().required('First name is required'),
      lastName: yup.string().required('Last name is required'),
      address: yup.string().required('Address is required'),
      city: yup.string().required('City is required'),
      zipCode: yup.string().required('Zip code is required'),
      country: yup.string().required('Country is required')
    }),
    
    // Payment information
    payment: yup.object().shape({
      method: yup.string().oneOf(['card', 'paypal', 'apple_pay']),
      cardNumber: yup.string().when('method', {
        is: 'card',
        then: yup.string().required('Card number is required')
      }),
      expiryDate: yup.string().when('method', {
        is: 'card',
        then: yup.string().required('Expiry date is required')
      }),
      cvv: yup.string().when('method', {
        is: 'card',
        then: yup.string().required('CVV is required')
      })
    })
  });

  const form = useAdvancedForm({
    initialValues: {
      shipping: {
        firstName: '',
        lastName: '',
        address: '',
        city: '',
        zipCode: '',
        country: ''
      },
      payment: {
        method: 'card',
        cardNumber: '',
        expiryDate: '',
        cvv: ''
      },
      billing: {
        sameAsShipping: true
      }
    },
    validationSchema: checkoutSchema,
    onSubmit: async (values) => {
      await onSubmit(values);
    }
  });

  return (
    <div className="checkout-form">
      <div className="checkout-steps">
        <button 
          className={currentStep === 'shipping' ? 'active' : ''}
          onClick={() => setCurrentStep('shipping')}
        >
          Shipping
        </button>
        <button 
          className={currentStep === 'payment' ? 'active' : ''}
          onClick={() => setCurrentStep('payment')}
        >
          Payment
        </button>
        <button 
          className={currentStep === 'review' ? 'active' : ''}
          onClick={() => setCurrentStep('review')}
        >
          Review
        </button>
      </div>

      <form onSubmit={form.handleSubmit}>
        {currentStep === 'shipping' && (
          <ShippingStep 
            values={form.values.shipping}
            errors={form.errors.shipping}
            touched={form.touched.shipping}
            onChange={(field, value) => form.setFieldValue(`shipping.${field}`, value)}
            onBlur={(field) => form.setFieldTouched(`shipping.${field}`, true)}
          />
        )}
        
        {currentStep === 'payment' && (
          <PaymentStep 
            values={form.values.payment}
            errors={form.errors.payment}
            touched={form.touched.payment}
            onChange={(field, value) => form.setFieldValue(`payment.${field}`, value)}
            onBlur={(field) => form.setFieldTouched(`payment.${field}`, true)}
          />
        )}
        
        {currentStep === 'review' && (
          <ReviewStep 
            cart={cart}
            shipping={form.values.shipping}
            payment={form.values.payment}
          />
        )}

        <div className="checkout-actions">
          {currentStep !== 'shipping' && (
            <button type="button" onClick={() => {
              const steps = ['shipping', 'payment', 'review'];
              const currentIndex = steps.indexOf(currentStep);
              setCurrentStep(steps[currentIndex - 1]);
            }}>
              Back
            </button>
          )}
          
          {currentStep === 'review' ? (
            <button type="submit" disabled={form.isSubmitting}>
              {form.isSubmitting ? 'Processing...' : 'Place Order'}
            </button>
          ) : (
            <button type="button" onClick={() => {
              const steps = ['shipping', 'payment', 'review'];
              const currentIndex = steps.indexOf(currentStep);
              setCurrentStep(steps[currentIndex + 1]);
            }}>
              Continue
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
```

This comprehensive guide covers advanced form patterns that are essential for building production-ready React applications. The patterns shown here handle complex real-world scenarios while maintaining performance and user experience standards.
