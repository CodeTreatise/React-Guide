# Validation Patterns and Schema Design

> **Advanced Validation Strategies, Schema Design, and Error Handling**

## 🎯 Overview

This comprehensive guide covers advanced validation patterns, schema design principles, custom validation logic, and sophisticated error handling strategies for React forms.

## 📋 Table of Contents

1. [Schema-Based Validation](#schema-based-validation)
2. [Custom Validation Patterns](#custom-validation-patterns)
3. [Async Validation](#async-validation)
4. [Cross-Field Validation](#cross-field-validation)
5. [Conditional Validation](#conditional-validation)
6. [Real-Time Validation](#real-time-validation)
7. [Error Handling Strategies](#error-handling-strategies)
8. [Internationalization](#internationalization)
9. [Performance Optimization](#performance-optimization)

## 🏗 Schema-Based Validation

### Yup Schema Design

```jsx
import * as yup from 'yup';

// Basic Schema
const userSchema = yup.object().shape({
  firstName: yup
    .string()
    .required('First name is required')
    .min(2, 'First name must be at least 2 characters')
    .max(50, 'First name must not exceed 50 characters')
    .matches(/^[a-zA-Z\s]*$/, 'First name can only contain letters'),
  
  lastName: yup
    .string()
    .required('Last name is required')
    .min(2, 'Last name must be at least 2 characters')
    .max(50, 'Last name must not exceed 50 characters')
    .matches(/^[a-zA-Z\s]*$/, 'Last name can only contain letters'),
  
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email address')
    .lowercase()
    .trim(),
  
  age: yup
    .number()
    .required('Age is required')
    .positive('Age must be a positive number')
    .integer('Age must be a whole number')
    .min(18, 'Must be at least 18 years old')
    .max(120, 'Age must be realistic'),
  
  password: yup
    .string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain uppercase, lowercase, number and special character'
    ),
  
  confirmPassword: yup
    .string()
    .required('Please confirm your password')
    .oneOf([yup.ref('password')], 'Passwords must match'),
  
  phoneNumber: yup
    .string()
    .required('Phone number is required')
    .matches(
      /^(\+\d{1,3}[- ]?)?\d{10}$/,
      'Please enter a valid phone number'
    ),
  
  website: yup
    .string()
    .url('Please enter a valid URL')
    .nullable()
    .transform(value => value || null),
  
  birthDate: yup
    .date()
    .required('Birth date is required')
    .max(new Date(), 'Birth date cannot be in the future')
    .min(new Date('1900-01-01'), 'Birth date is too far in the past'),
  
  termsAccepted: yup
    .boolean()
    .required('You must accept the terms and conditions')
    .oneOf([true], 'You must accept the terms and conditions')
});

// Advanced Schema with Custom Methods
const advancedUserSchema = yup.object().shape({
  email: yup
    .string()
    .required('Email is required')
    .email('Invalid email format')
    .test('email-availability', 'Email is already taken', async (value) => {
      if (!value) return true;
      // Simulate API call
      const isAvailable = await checkEmailAvailability(value);
      return isAvailable;
    }),
  
  username: yup
    .string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must not exceed 20 characters')
    .matches(/^[a-zA-Z0-9_]*$/, 'Username can only contain letters, numbers, and underscores')
    .test('username-availability', 'Username is already taken', async (value) => {
      if (!value) return true;
      const isAvailable = await checkUsernameAvailability(value);
      return isAvailable;
    }),
  
  profilePicture: yup
    .mixed()
    .nullable()
    .test('fileSize', 'File size too large', (value) => {
      if (!value) return true;
      return value.size <= 5 * 1024 * 1024; // 5MB
    })
    .test('fileType', 'Invalid file type', (value) => {
      if (!value) return true;
      return ['image/jpeg', 'image/png', 'image/gif'].includes(value.type);
    })
});

// Async functions for validation
async function checkEmailAvailability(email) {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      const unavailableEmails = ['admin@example.com', 'test@example.com'];
      resolve(!unavailableEmails.includes(email));
    }, 500);
  });
}

async function checkUsernameAvailability(username) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const unavailableUsernames = ['admin', 'root', 'user'];
      resolve(!unavailableUsernames.includes(username));
    }, 500);
  });
}
```

### Zod Schema Design

```jsx
import { z } from 'zod';

// Basic Zod Schema
const userSchemaZod = z.object({
  firstName: z
    .string()
    .min(2, 'First name must be at least 2 characters')
    .max(50, 'First name must not exceed 50 characters')
    .regex(/^[a-zA-Z\s]*$/, 'First name can only contain letters'),
  
  lastName: z
    .string()
    .min(2, 'Last name must be at least 2 characters')
    .max(50, 'Last name must not exceed 50 characters')
    .regex(/^[a-zA-Z\s]*$/, 'Last name can only contain letters'),
  
  email: z
    .string()
    .email('Please enter a valid email address')
    .transform(val => val.toLowerCase().trim()),
  
  age: z
    .number()
    .int('Age must be a whole number')
    .min(18, 'Must be at least 18 years old')
    .max(120, 'Age must be realistic'),
  
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain uppercase, lowercase, number and special character'
    ),
  
  confirmPassword: z.string(),
  
  phoneNumber: z
    .string()
    .regex(/^(\+\d{1,3}[- ]?)?\d{10}$/, 'Please enter a valid phone number'),
  
  website: z
    .string()
    .url('Please enter a valid URL')
    .optional()
    .or(z.literal('')),
  
  birthDate: z
    .date()
    .max(new Date(), 'Birth date cannot be in the future')
    .min(new Date('1900-01-01'), 'Birth date is too far in the past'),
  
  termsAccepted: z
    .boolean()
    .refine(val => val === true, 'You must accept the terms and conditions')
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
});

// Advanced Zod Schema with Custom Validations
const advancedUserSchemaZod = z.object({
  email: z
    .string()
    .email('Invalid email format')
    .refine(async (email) => {
      const isAvailable = await checkEmailAvailability(email);
      return isAvailable;
    }, 'Email is already taken'),
  
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must not exceed 20 characters')
    .regex(/^[a-zA-Z0-9_]*$/, 'Username can only contain letters, numbers, and underscores')
    .refine(async (username) => {
      const isAvailable = await checkUsernameAvailability(username);
      return isAvailable;
    }, 'Username is already taken'),
  
  profilePicture: z
    .instanceof(File)
    .optional()
    .refine(file => !file || file.size <= 5 * 1024 * 1024, 'File size too large')
    .refine(
      file => !file || ['image/jpeg', 'image/png', 'image/gif'].includes(file.type),
      'Invalid file type'
    )
});
```

## 🔧 Custom Validation Patterns

### Custom Validation Hooks

```jsx
{% raw %}
{% raw %}
import { useState, useCallback } from 'react';

// Custom validation hook
export const useValidation = (validationRules) => {
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const validateField = useCallback((name, value) => {
    const rules = validationRules[name];
    if (!rules) return '';

    for (const rule of rules) {
      const error = rule(value);
      if (error) return error;
    }
    return '';
  }, [validationRules]);

  const validateForm = useCallback((values) => {
    const newErrors = {};
    let isValid = true;

    Object.keys(validationRules).forEach(fieldName => {
      const error = validateField(fieldName, values[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [validateField, validationRules]);

  const setFieldTouched = useCallback((name, isTouched = true) => {
    setTouched(prev => ({ ...prev, [name]: isTouched }));
  }, []);

  const setFieldError = useCallback((name, error) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors({});
    setTouched({});
  }, []);

  return {
    errors,
    touched,
    validateField,
    validateForm,
    setFieldTouched,
    setFieldError,
    clearErrors
  };
};

// Validation rule creators
export const required = (message = 'This field is required') => (value) => {
  if (!value || (typeof value === 'string' && !value.trim())) {
    return message;
  }
  return '';
};

export const minLength = (min, message) => (value) => {
  if (value && value.length < min) {
    return message || `Must be at least ${min} characters`;
  }
  return '';
};

export const maxLength = (max, message) => (value) => {
  if (value && value.length > max) {
    return message || `Must not exceed ${max} characters`;
  }
  return '';
};

export const pattern = (regex, message) => (value) => {
  if (value && !regex.test(value)) {
    return message || 'Invalid format';
  }
  return '';
};

export const email = (message = 'Invalid email address') => (value) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (value && !emailRegex.test(value)) {
    return message;
  }
  return '';
};

export const numeric = (message = 'Must be a number') => (value) => {
  if (value && isNaN(Number(value))) {
    return message;
  }
  return '';
};

export const min = (minVal, message) => (value) => {
  if (value && Number(value) < minVal) {
    return message || `Must be at least ${minVal}`;
  }
  return '';
};

export const max = (maxVal, message) => (value) => (value) => {
  if (value && Number(value) > maxVal) {
    return message || `Must not exceed ${maxVal}`;
  }
  return '';
};

// Usage example
const validationRules = {
  firstName: [
    required('First name is required'),
    minLength(2, 'First name must be at least 2 characters'),
    maxLength(50, 'First name must not exceed 50 characters'),
    pattern(/^[a-zA-Z\s]*$/, 'First name can only contain letters')
  ],
  email: [
    required('Email is required'),
    email('Please enter a valid email address')
  ],
  age: [
    required('Age is required'),
    numeric('Age must be a number'),
    min(18, 'Must be at least 18 years old'),
    max(120, 'Age must be realistic')
  ]
};

function CustomValidationForm() {
  const [values, setValues] = useState({
    firstName: '',
    email: '',
    age: ''
  });

  const { errors, touched, validateField, validateForm, setFieldTouched } = useValidation(validationRules);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
    
    if (touched[name]) {
      validateField(name, value);
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    setFieldTouched(name);
    validateField(name, value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const isValid = validateForm(values);
    
    if (isValid) {
      console.log('Form is valid:', values);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          name="firstName"
          value={values.firstName}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="First Name"
          className={errors.firstName && touched.firstName ? 'error' : ''}
        />
        {errors.firstName && touched.firstName && (
          <span className="error">{errors.firstName}</span>
        )}
      </div>

      <div>
        <input
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Email"
          className={errors.email && touched.email ? 'error' : ''}
        />
        {errors.email && touched.email && (
          <span className="error">{errors.email}</span>
        )}
      </div>

      <div>
        <input
          name="age"
          type="number"
          value={values.age}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Age"
          className={errors.age && touched.age ? 'error' : ''}
        />
        {errors.age && touched.age && (
          <span className="error">{errors.age}</span>
        )}
      </div>

      <button type="submit">Submit</button>
    </form>
  );
}
{% endraw %}
{% endraw %}
```

## ⚡ Async Validation

### Debounced Async Validation

```jsx
import { useState, useCallback, useRef } from 'react';
import { useForm } from 'react-hook-form';

// Custom hook for debounced async validation
const useAsyncValidation = (asyncValidator, delay = 500) => {
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState('');
  const timeoutRef = useRef();

  const validate = useCallback((value) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setIsValidating(true);
    setValidationError('');

    timeoutRef.current = setTimeout(async () => {
      try {
        const error = await asyncValidator(value);
        setValidationError(error || '');
      } catch (err) {
        setValidationError('Validation failed');
      } finally {
        setIsValidating(false);
      }
    }, delay);
  }, [asyncValidator, delay]);

  return { validate, isValidating, validationError };
};

// Async validation functions
const validateEmailAsync = async (email) => {
  if (!email) return '';
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const unavailableEmails = ['admin@example.com', 'test@example.com'];
  return unavailableEmails.includes(email) ? 'Email is already taken' : '';
};

const validateUsernameAsync = async (username) => {
  if (!username) return '';
  
  await new Promise(resolve => setTimeout(resolve, 800));
  
  const unavailableUsernames = ['admin', 'root', 'user'];
  return unavailableUsernames.includes(username) ? 'Username is already taken' : '';
};

function AsyncValidationForm() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm();
  
  const emailValue = watch('email');
  const usernameValue = watch('username');

  const {
    validate: validateEmail,
    isValidating: isValidatingEmail,
    validationError: emailValidationError
  } = useAsyncValidation(validateEmailAsync);

  const {
    validate: validateUsername,
    isValidating: isValidatingUsername,
    validationError: usernameValidationError
  } = useAsyncValidation(validateUsernameAsync);

  // Trigger validation when values change
  React.useEffect(() => {
    if (emailValue) {
      validateEmail(emailValue);
    }
  }, [emailValue, validateEmail]);

  React.useEffect(() => {
    if (usernameValue) {
      validateUsername(usernameValue);
    }
  }, [usernameValue, validateUsername]);

  const onSubmit = (data) => {
    // Check for async validation errors before submitting
    if (emailValidationError || usernameValidationError) {
      console.error('Form has validation errors');
      return;
    }
    
    console.log('Async validation form data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Email</label>
        <input
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^\S+@\S+$/i,
              message: 'Invalid email format'
            }
          })}
          type="email"
          className={errors.email || emailValidationError ? 'error' : ''}
        />
        {isValidatingEmail && <span className="validating">Checking email...</span>}
        {errors.email && <span className="error">{errors.email.message}</span>}
        {emailValidationError && <span className="error">{emailValidationError}</span>}
      </div>

      <div>
        <label>Username</label>
        <input
          {...register('username', {
            required: 'Username is required',
            minLength: { value: 3, message: 'Username must be at least 3 characters' }
          })}
          className={errors.username || usernameValidationError ? 'error' : ''}
        />
        {isValidatingUsername && <span className="validating">Checking username...</span>}
        {errors.username && <span className="error">{errors.username.message}</span>}
        {usernameValidationError && <span className="error">{usernameValidationError}</span>}
      </div>

      <button type="submit">Submit</button>
    </form>
  );
}
```

### Server-Side Validation Integration

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';

// API service for validation
const validationAPI = {
  validateField: async (fieldName, value) => {
    const response = await fetch('/api/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field: fieldName, value })
    });
    
    const result = await response.json();
    return result.error || null;
  },
  
  validateForm: async (formData) => {
    const response = await fetch('/api/validate-form', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    
    const result = await response.json();
    return result.errors || {};
  }
};

function ServerValidationForm() {
  const { register, handleSubmit, setError, clearErrors, formState: { errors, isSubmitting } } = useForm();
  const [serverErrors, setServerErrors] = useState({});

  const handleFieldValidation = async (fieldName, value) => {
    if (!value) return;
    
    try {
      const error = await validationAPI.validateField(fieldName, value);
      if (error) {
        setServerErrors(prev => ({ ...prev, [fieldName]: error }));
      } else {
        setServerErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors[fieldName];
          return newErrors;
        });
      }
    } catch (err) {
      console.error('Validation error:', err);
    }
  };

  const onSubmit = async (data) => {
    try {
      // Clear previous server errors
      setServerErrors({});
      clearErrors();

      // Perform server-side validation
      const serverValidationErrors = await validationAPI.validateForm(data);
      
      if (Object.keys(serverValidationErrors).length > 0) {
        // Set server validation errors
        Object.entries(serverValidationErrors).forEach(([field, error]) => {
          setError(field, { message: error });
        });
        return;
      }

      // Submit the form
      const response = await fetch('/api/submit-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        console.log('Form submitted successfully');
      } else {
        const errorData = await response.json();
        console.error('Submission error:', errorData);
      }
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Email</label>
        <input
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^\S+@\S+$/i,
              message: 'Invalid email format'
            }
          })}
          onBlur={(e) => handleFieldValidation('email', e.target.value)}
          type="email"
          className={errors.email || serverErrors.email ? 'error' : ''}
        />
        {errors.email && <span className="error">{errors.email.message}</span>}
        {serverErrors.email && <span className="error">{serverErrors.email}</span>}
      </div>

      <div>
        <label>Username</label>
        <input
          {...register('username', {
            required: 'Username is required',
            minLength: { value: 3, message: 'Username must be at least 3 characters' }
          })}
          onBlur={(e) => handleFieldValidation('username', e.target.value)}
          className={errors.username || serverErrors.username ? 'error' : ''}
        />
        {errors.username && <span className="error">{errors.username.message}</span>}
        {serverErrors.username && <span className="error">{serverErrors.username}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

## 🔗 Cross-Field Validation

### Password Confirmation Example

```jsx
{% raw %}
{% raw %}
import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';

const passwordValidationSchema = yup.object().shape({
  password: yup
    .string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain uppercase, lowercase, number and special character'
    ),
  confirmPassword: yup
    .string()
    .required('Please confirm your password')
    .oneOf([yup.ref('password')], 'Passwords must match'),
  currentPassword: yup
    .string()
    .required('Current password is required')
    .test('not-same', 'New password must be different from current password', function(value) {
      return value !== this.parent.password;
    })
});

function PasswordForm() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    resolver: yupResolver(passwordValidationSchema)
  });

  const password = watch('password');
  const confirmPassword = watch('confirmPassword');

  const onSubmit = (data) => {
    console.log('Password form data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Current Password</label>
        <input
          {...register('currentPassword')}
          type="password"
          className={errors.currentPassword ? 'error' : ''}
        />
        {errors.currentPassword && (
          <span className="error">{errors.currentPassword.message}</span>
        )}
      </div>

      <div>
        <label>New Password</label>
        <input
          {...register('password')}
          type="password"
          className={errors.password ? 'error' : ''}
        />
        {errors.password && (
          <span className="error">{errors.password.message}</span>
        )}
        
        {/* Password strength indicator */}
        {password && (
          <div className="password-strength">
            <PasswordStrengthIndicator password={password} />
          </div>
        )}
      </div>

      <div>
        <label>Confirm New Password</label>
        <input
          {...register('confirmPassword')}
          type="password"
          className={errors.confirmPassword ? 'error' : ''}
        />
        {errors.confirmPassword && (
          <span className="error">{errors.confirmPassword.message}</span>
        )}
        
        {/* Visual feedback for password match */}
        {confirmPassword && (
          <div className={`password-match ${password === confirmPassword ? 'match' : 'no-match'}`}>
            {password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
          </div>
        )}
      </div>

      <button type="submit">Update Password</button>
    </form>
  );
}

// Password strength indicator component
function PasswordStrengthIndicator({ password }) {
  const calculateStrength = (pwd) => {
    let strength = 0;
    const checks = [
      /[a-z]/, // lowercase
      /[A-Z]/, // uppercase
      /\d/,    // numbers
      /[@$!%*?&]/, // special characters
      /.{8,}/  // minimum length
    ];
    
    checks.forEach(check => {
      if (check.test(pwd)) strength++;
    });
    
    return strength;
  };

  const strength = calculateStrength(password);
  const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
  const strengthColors = ['#ff4444', '#ff8800', '#ffaa00', '#88aa00', '#44aa44'];

  return (
    <div className="strength-indicator">
      <div className="strength-bar">
        <div 
          className="strength-fill"
          style={{
            width: `${(strength / 5) * 100}%`,
            backgroundColor: strengthColors[strength - 1] || '#ddd'
          }}
        />
      </div>
      <span className="strength-label">
        {strength > 0 ? strengthLabels[strength - 1] : 'Enter password'}
      </span>
    </div>
  );
}
{% endraw %}
{% endraw %}
```

### Date Range Validation

```jsx
import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';

const dateRangeSchema = yup.object().shape({
  startDate: yup
    .date()
    .required('Start date is required')
    .min(new Date(), 'Start date cannot be in the past'),
  
  endDate: yup
    .date()
    .required('End date is required')
    .min(yup.ref('startDate'), 'End date must be after start date')
    .test('max-duration', 'Duration cannot exceed 365 days', function(value) {
      const { startDate } = this.parent;
      if (!startDate || !value) return true;
      
      const diffTime = Math.abs(value - startDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays <= 365;
    }),
  
  eventType: yup
    .string()
    .required('Event type is required'),
  
  // Conditional validation based on event type
  participants: yup
    .number()
    .when('eventType', {
      is: 'conference',
      then: yup.number().min(10, 'Conference must have at least 10 participants'),
      otherwise: yup.number().min(1, 'Must have at least 1 participant')
    })
    .max(1000, 'Cannot exceed 1000 participants')
});

function DateRangeForm() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    resolver: yupResolver(dateRangeSchema)
  });

  const startDate = watch('startDate');
  const endDate = watch('endDate');
  const eventType = watch('eventType');

  // Calculate duration
  const calculateDuration = () => {
    if (!startDate || !endDate) return null;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
  };

  const duration = calculateDuration();

  const onSubmit = (data) => {
    console.log('Date range form data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Event Type</label>
        <select {...register('eventType')} className={errors.eventType ? 'error' : ''}>
          <option value="">Select event type</option>
          <option value="meeting">Meeting</option>
          <option value="workshop">Workshop</option>
          <option value="conference">Conference</option>
          <option value="training">Training</option>
        </select>
        {errors.eventType && (
          <span className="error">{errors.eventType.message}</span>
        )}
      </div>

      <div>
        <label>Start Date</label>
        <input
          {...register('startDate')}
          type="date"
          className={errors.startDate ? 'error' : ''}
        />
        {errors.startDate && (
          <span className="error">{errors.startDate.message}</span>
        )}
      </div>

      <div>
        <label>End Date</label>
        <input
          {...register('endDate')}
          type="date"
          className={errors.endDate ? 'error' : ''}
        />
        {errors.endDate && (
          <span className="error">{errors.endDate.message}</span>
        )}
        
        {duration && (
          <div className="duration-info">
            Duration: {duration} day{duration !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      <div>
        <label>Number of Participants</label>
        <input
          {...register('participants', { valueAsNumber: true })}
          type="number"
          className={errors.participants ? 'error' : ''}
        />
        {errors.participants && (
          <span className="error">{errors.participants.message}</span>
        )}
        
        {eventType === 'conference' && (
          <div className="info">
            Conferences require a minimum of 10 participants
          </div>
        )}
      </div>

      <button type="submit">Create Event</button>
    </form>
  );
}
```

## 🔀 Conditional Validation

### Dynamic Validation Rules

```jsx
import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';

// Dynamic schema based on user type
const createValidationSchema = (userType) => {
  const baseSchema = {
    userType: yup.string().required('User type is required'),
    firstName: yup.string().required('First name is required'),
    lastName: yup.string().required('Last name is required'),
    email: yup.string().email().required('Email is required')
  };

  if (userType === 'business') {
    return yup.object().shape({
      ...baseSchema,
      companyName: yup.string().required('Company name is required'),
      taxId: yup.string().required('Tax ID is required'),
      businessAddress: yup.string().required('Business address is required'),
      numberOfEmployees: yup
        .number()
        .required('Number of employees is required')
        .min(1, 'Must have at least 1 employee')
    });
  }

  if (userType === 'individual') {
    return yup.object().shape({
      ...baseSchema,
      dateOfBirth: yup
        .date()
        .required('Date of birth is required')
        .max(new Date(), 'Date of birth cannot be in the future'),
      socialSecurityNumber: yup
        .string()
        .matches(/^\d{3}-\d{2}-\d{4}$/, 'Invalid SSN format')
    });
  }

  if (userType === 'nonprofit') {
    return yup.object().shape({
      ...baseSchema,
      organizationName: yup.string().required('Organization name is required'),
      taxExemptNumber: yup.string().required('Tax exempt number is required'),
      missionStatement: yup
        .string()
        .required('Mission statement is required')
        .min(50, 'Mission statement must be at least 50 characters')
    });
  }

  return yup.object().shape(baseSchema);
};

function ConditionalValidationForm() {
  const [userType, setUserType] = useState('');
  
  const schema = createValidationSchema(userType);
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  // Reset form when user type changes
  useEffect(() => {
    reset();
  }, [userType, reset]);

  const onSubmit = (data) => {
    console.log('Conditional validation form data:', data);
  };

  const renderConditionalFields = () => {
    switch (userType) {
      case 'business':
        return (
          <>
            <div>
              <label>Company Name</label>
              <input
                {...register('companyName')}
                className={errors.companyName ? 'error' : ''}
              />
              {errors.companyName && (
                <span className="error">{errors.companyName.message}</span>
              )}
            </div>

            <div>
              <label>Tax ID</label>
              <input
                {...register('taxId')}
                className={errors.taxId ? 'error' : ''}
              />
              {errors.taxId && (
                <span className="error">{errors.taxId.message}</span>
              )}
            </div>

            <div>
              <label>Business Address</label>
              <textarea
                {...register('businessAddress')}
                className={errors.businessAddress ? 'error' : ''}
              />
              {errors.businessAddress && (
                <span className="error">{errors.businessAddress.message}</span>
              )}
            </div>

            <div>
              <label>Number of Employees</label>
              <input
                {...register('numberOfEmployees', { valueAsNumber: true })}
                type="number"
                className={errors.numberOfEmployees ? 'error' : ''}
              />
              {errors.numberOfEmployees && (
                <span className="error">{errors.numberOfEmployees.message}</span>
              )}
            </div>
          </>
        );

      case 'individual':
        return (
          <>
            <div>
              <label>Date of Birth</label>
              <input
                {...register('dateOfBirth')}
                type="date"
                className={errors.dateOfBirth ? 'error' : ''}
              />
              {errors.dateOfBirth && (
                <span className="error">{errors.dateOfBirth.message}</span>
              )}
            </div>

            <div>
              <label>Social Security Number</label>
              <input
                {...register('socialSecurityNumber')}
                placeholder="XXX-XX-XXXX"
                className={errors.socialSecurityNumber ? 'error' : ''}
              />
              {errors.socialSecurityNumber && (
                <span className="error">{errors.socialSecurityNumber.message}</span>
              )}
            </div>
          </>
        );

      case 'nonprofit':
        return (
          <>
            <div>
              <label>Organization Name</label>
              <input
                {...register('organizationName')}
                className={errors.organizationName ? 'error' : ''}
              />
              {errors.organizationName && (
                <span className="error">{errors.organizationName.message}</span>
              )}
            </div>

            <div>
              <label>Tax Exempt Number</label>
              <input
                {...register('taxExemptNumber')}
                className={errors.taxExemptNumber ? 'error' : ''}
              />
              {errors.taxExemptNumber && (
                <span className="error">{errors.taxExemptNumber.message}</span>
              )}
            </div>

            <div>
              <label>Mission Statement</label>
              <textarea
                {...register('missionStatement')}
                className={errors.missionStatement ? 'error' : ''}
                rows={4}
              />
              {errors.missionStatement && (
                <span className="error">{errors.missionStatement.message}</span>
              )}
            </div>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>User Type</label>
        <select
          {...register('userType')}
          value={userType}
          onChange={(e) => setUserType(e.target.value)}
          className={errors.userType ? 'error' : ''}
        >
          <option value="">Select user type</option>
          <option value="individual">Individual</option>
          <option value="business">Business</option>
          <option value="nonprofit">Non-profit</option>
        </select>
        {errors.userType && (
          <span className="error">{errors.userType.message}</span>
        )}
      </div>

      <div>
        <label>First Name</label>
        <input
          {...register('firstName')}
          className={errors.firstName ? 'error' : ''}
        />
        {errors.firstName && (
          <span className="error">{errors.firstName.message}</span>
        )}
      </div>

      <div>
        <label>Last Name</label>
        <input
          {...register('lastName')}
          className={errors.lastName ? 'error' : ''}
        />
        {errors.lastName && (
          <span className="error">{errors.lastName.message}</span>
        )}
      </div>

      <div>
        <label>Email</label>
        <input
          {...register('email')}
          type="email"
          className={errors.email ? 'error' : ''}
        />
        {errors.email && (
          <span className="error">{errors.email.message}</span>
        )}
      </div>

      {renderConditionalFields()}

      <button type="submit">Submit</button>
    </form>
  );
}
```

## ⚡ Real-Time Validation

### Live Validation with Visual Feedback

```jsx
{% raw %}
{% raw %}
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';

function RealTimeValidationForm() {
  const { register, watch, formState: { errors }, handleSubmit } = useForm({
    mode: 'onChange'
  });

  const watchedValues = watch();
  const [fieldValidation, setFieldValidation] = useState({});

  // Real-time validation logic
  const validateFieldRealTime = (fieldName, value) => {
    switch (fieldName) {
      case 'email':
        if (!value) return { status: 'neutral', message: '' };
        if (!/^\S+@\S+$/i.test(value)) {
          return { status: 'error', message: 'Invalid email format' };
        }
        return { status: 'success', message: 'Valid email' };

      case 'password':
        if (!value) return { status: 'neutral', message: '' };
        
        const strength = calculatePasswordStrength(value);
        if (strength < 3) {
          return { status: 'warning', message: `Password strength: ${getStrengthLabel(strength)}` };
        }
        return { status: 'success', message: `Password strength: ${getStrengthLabel(strength)}` };

      case 'confirmPassword':
        if (!value) return { status: 'neutral', message: '' };
        if (value !== watchedValues.password) {
          return { status: 'error', message: 'Passwords do not match' };
        }
        return { status: 'success', message: 'Passwords match' };

      case 'username':
        if (!value) return { status: 'neutral', message: '' };
        if (value.length < 3) {
          return { status: 'error', message: 'Username too short' };
        }
        if (!/^[a-zA-Z0-9_]*$/.test(value)) {
          return { status: 'error', message: 'Invalid characters' };
        }
        return { status: 'success', message: 'Username available' };

      default:
        return { status: 'neutral', message: '' };
    }
  };

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[@$!%*?&]/.test(password)) strength++;
    return strength;
  };

  const getStrengthLabel = (strength) => {
    const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    return labels[strength] || 'Very Weak';
  };

  // Update field validation on value change
  useEffect(() => {
    const newValidation = {};
    Object.entries(watchedValues).forEach(([fieldName, value]) => {
      newValidation[fieldName] = validateFieldRealTime(fieldName, value);
    });
    setFieldValidation(newValidation);
  }, [watchedValues]);

  const getFieldClassName = (fieldName) => {
    const validation = fieldValidation[fieldName];
    if (!validation) return '';
    return `validation-${validation.status}`;
  };

  const onSubmit = (data) => {
    console.log('Real-time validation form data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="real-time-form">
      <div className="field-group">
        <label>Username</label>
        <input
          {...register('username', {
            required: 'Username is required',
            minLength: { value: 3, message: 'Username must be at least 3 characters' }
          })}
          className={getFieldClassName('username')}
        />
        <div className="field-feedback">
          {fieldValidation.username && (
            <span className={`feedback ${fieldValidation.username.status}`}>
              {fieldValidation.username.message}
            </span>
          )}
          {errors.username && (
            <span className="error">{errors.username.message}</span>
          )}
        </div>
      </div>

      <div className="field-group">
        <label>Email</label>
        <input
          {...register('email', {
            required: 'Email is required',
            pattern: { value: /^\S+@\S+$/i, message: 'Invalid email' }
          })}
          type="email"
          className={getFieldClassName('email')}
        />
        <div className="field-feedback">
          {fieldValidation.email && (
            <span className={`feedback ${fieldValidation.email.status}`}>
              {fieldValidation.email.message}
            </span>
          )}
          {errors.email && (
            <span className="error">{errors.email.message}</span>
          )}
        </div>
      </div>

      <div className="field-group">
        <label>Password</label>
        <input
          {...register('password', {
            required: 'Password is required',
            minLength: { value: 8, message: 'Password must be at least 8 characters' }
          })}
          type="password"
          className={getFieldClassName('password')}
        />
        <div className="field-feedback">
          {fieldValidation.password && (
            <span className={`feedback ${fieldValidation.password.status}`}>
              {fieldValidation.password.message}
            </span>
          )}
          {errors.password && (
            <span className="error">{errors.password.message}</span>
          )}
        </div>
        
        {/* Password strength bar */}
        {watchedValues.password && (
          <div className="password-strength-bar">
            <div 
              className="strength-fill"
              style={{
                width: `${(calculatePasswordStrength(watchedValues.password) / 5) * 100}%`
              }}
            />
          </div>
        )}
      </div>

      <div className="field-group">
        <label>Confirm Password</label>
        <input
          {...register('confirmPassword', {
            required: 'Please confirm your password'
          })}
          type="password"
          className={getFieldClassName('confirmPassword')}
        />
        <div className="field-feedback">
          {fieldValidation.confirmPassword && (
            <span className={`feedback ${fieldValidation.confirmPassword.status}`}>
              {fieldValidation.confirmPassword.message}
            </span>
          )}
          {errors.confirmPassword && (
            <span className="error">{errors.confirmPassword.message}</span>
          )}
        </div>
      </div>

      <button type="submit">Submit</button>
    </form>
  );
}

// CSS for real-time validation
const styles = `
.real-time-form .field-group {
  margin-bottom: 1rem;
}

.real-time-form input.validation-success {
  border-color: #4CAF50;
  background-color: #f8fff8;
}

.real-time-form input.validation-error {
  border-color: #f44336;
  background-color: #fff8f8;
}

.real-time-form input.validation-warning {
  border-color: #ff9800;
  background-color: #fffbf8;
}

.field-feedback .feedback.success {
  color: #4CAF50;
}

.field-feedback .feedback.error {
  color: #f44336;
}

.field-feedback .feedback.warning {
  color: #ff9800;
}

.password-strength-bar {
  height: 4px;
  background-color: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}

.strength-fill {
  height: 100%;
  background: linear-gradient(to right, #f44336, #ff9800, #4CAF50);
  transition: width 0.3s ease;
}
`;
{% endraw %}
{% endraw %}
```

## 🌍 Internationalization

### Multi-Language Validation Messages

```jsx
{% raw %}
{% raw %}
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Validation messages in different languages
const validationMessages = {
  en: {
    required: 'This field is required',
    email: 'Please enter a valid email address',
    minLength: (min) => `Must be at least ${min} characters`,
    maxLength: (max) => `Must not exceed ${max} characters`,
    passwordMatch: 'Passwords must match',
    invalidFormat: 'Invalid format'
  },
  es: {
    required: 'Este campo es obligatorio',
    email: 'Por favor ingrese una dirección de correo válida',
    minLength: (min) => `Debe tener al menos ${min} caracteres`,
    maxLength: (max) => `No debe exceder ${max} caracteres`,
    passwordMatch: 'Las contraseñas deben coincidir',
    invalidFormat: 'Formato inválido'
  },
  fr: {
    required: 'Ce champ est obligatoire',
    email: 'Veuillez saisir une adresse e-mail valide',
    minLength: (min) => `Doit contenir au moins ${min} caractères`,
    maxLength: (max) => `Ne doit pas dépasser ${max} caractères`,
    passwordMatch: 'Les mots de passe doivent correspondre',
    invalidFormat: 'Format invalide'
  }
};

// Create localized schema
const createLocalizedSchema = (locale = 'en') => {
  const messages = validationMessages[locale] || validationMessages.en;
  
  return yup.object().shape({
    firstName: yup
      .string()
      .required(messages.required)
      .min(2, messages.minLength(2))
      .max(50, messages.maxLength(50)),
    
    lastName: yup
      .string()
      .required(messages.required)
      .min(2, messages.minLength(2))
      .max(50, messages.maxLength(50)),
    
    email: yup
      .string()
      .required(messages.required)
      .email(messages.email),
    
    password: yup
      .string()
      .required(messages.required)
      .min(8, messages.minLength(8)),
    
    confirmPassword: yup
      .string()
      .required(messages.required)
      .oneOf([yup.ref('password')], messages.passwordMatch)
  });
};

function InternationalizedForm({ locale = 'en' }) {
  const schema = createLocalizedSchema(locale);
  
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  const onSubmit = (data) => {
    console.log('Internationalized form data:', data);
  };

  // Field labels in different languages
  const labels = {
    en: {
      firstName: 'First Name',
      lastName: 'Last Name',
      email: 'Email',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      submit: 'Submit'
    },
    es: {
      firstName: 'Nombre',
      lastName: 'Apellido',
      email: 'Correo Electrónico',
      password: 'Contraseña',
      confirmPassword: 'Confirmar Contraseña',
      submit: 'Enviar'
    },
    fr: {
      firstName: 'Prénom',
      lastName: 'Nom de famille',
      email: 'E-mail',
      password: 'Mot de passe',
      confirmPassword: 'Confirmer le mot de passe',
      submit: 'Soumettre'
    }
  };

  const currentLabels = labels[locale] || labels.en;

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>{currentLabels.firstName}</label>
        <input
          {...register('firstName')}
          className={errors.firstName ? 'error' : ''}
        />
        {errors.firstName && (
          <span className="error">{errors.firstName.message}</span>
        )}
      </div>

      <div>
        <label>{currentLabels.lastName}</label>
        <input
          {...register('lastName')}
          className={errors.lastName ? 'error' : ''}
        />
        {errors.lastName && (
          <span className="error">{errors.lastName.message}</span>
        )}
      </div>

      <div>
        <label>{currentLabels.email}</label>
        <input
          {...register('email')}
          type="email"
          className={errors.email ? 'error' : ''}
        />
        {errors.email && (
          <span className="error">{errors.email.message}</span>
        )}
      </div>

      <div>
        <label>{currentLabels.password}</label>
        <input
          {...register('password')}
          type="password"
          className={errors.password ? 'error' : ''}
        />
        {errors.password && (
          <span className="error">{errors.password.message}</span>
        )}
      </div>

      <div>
        <label>{currentLabels.confirmPassword}</label>
        <input
          {...register('confirmPassword')}
          type="password"
          className={errors.confirmPassword ? 'error' : ''}
        />
        {errors.confirmPassword && (
          <span className="error">{errors.confirmPassword.message}</span>
        )}
      </div>

      <button type="submit">{currentLabels.submit}</button>
    </form>
  );
}

// Usage with locale switching
function LocalizedFormApp() {
  const [locale, setLocale] = useState('en');

  return (
    <div>
      <div className="locale-switcher">
        <button onClick={() => setLocale('en')}>English</button>
        <button onClick={() => setLocale('es')}>Español</button>
        <button onClick={() => setLocale('fr')}>Français</button>
      </div>
      
      <InternationalizedForm locale={locale} />
    </div>
  );
}
{% endraw %}
{% endraw %}
```

## 🚀 Performance Optimization

### Optimized Validation Strategies

```jsx
import { useMemo, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { debounce } from 'lodash';

// Memoized validation schema
const useValidationSchema = () => {
  return useMemo(() => yup.object().shape({
    // Schema definition here
  }), []);
};

// Debounced validation hook
const useDebouncedValidation = (validationFn, delay = 300) => {
  return useCallback(
    debounce(validationFn, delay),
    [validationFn, delay]
  );
};

function OptimizedValidationForm() {
  const schema = useValidationSchema();
  
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
    mode: 'onBlur', // Validate on blur instead of onChange for better performance
    reValidateMode: 'onChange'
  });

  // Debounced async validation
  const debouncedAsyncValidation = useDebouncedValidation(
    useCallback(async (value) => {
      // Async validation logic
      const result = await validateAsync(value);
      return result;
    }, []),
    500
  );

  const onSubmit = (data) => {
    console.log('Optimized form data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}

// Validation performance monitoring
const ValidationPerformanceMonitor = ({ children }) => {
  const [metrics, setMetrics] = useState({
    validationCount: 0,
    averageTime: 0,
    slowValidations: []
  });

  const trackValidation = useCallback((fieldName, startTime, endTime) => {
    const duration = endTime - startTime;
    
    setMetrics(prev => ({
      validationCount: prev.validationCount + 1,
      averageTime: (prev.averageTime * prev.validationCount + duration) / (prev.validationCount + 1),
      slowValidations: duration > 100 
        ? [...prev.slowValidations, { fieldName, duration }]
        : prev.slowValidations
    }));
  }, []);

  return (
    <div>
      {children}
      <div className="performance-metrics">
        <h4>Validation Performance</h4>
        <p>Total validations: {metrics.validationCount}</p>
        <p>Average time: {metrics.averageTime.toFixed(2)}ms</p>
        <p>Slow validations: {metrics.slowValidations.length}</p>
      </div>
    </div>
  );
};
```

## 📚 Best Practices Summary

### Validation Strategy Guidelines

1. **Choose the Right Approach**
   - Use schema-based validation for complex forms
   - Implement field-level validation for simple forms
   - Consider performance implications of validation timing

2. **Error Handling**
   - Provide clear, actionable error messages
   - Display errors near relevant fields
   - Use consistent error styling and messaging

3. **User Experience**
   - Implement real-time feedback for better UX
   - Use visual indicators for validation status
   - Provide helpful hints and suggestions

4. **Performance**
   - Debounce expensive validations
   - Use field-level validation when possible
   - Monitor validation performance

5. **Accessibility**
   - Use proper ARIA attributes for error messages
   - Ensure error messages are announced by screen readers
   - Provide clear focus management

6. **Internationalization**
   - Support multiple languages for global applications
   - Use proper date/number formatting for different locales
   - Consider cultural differences in validation rules

This comprehensive guide provides the foundation for implementing robust, performant, and user-friendly validation patterns in React applications.
