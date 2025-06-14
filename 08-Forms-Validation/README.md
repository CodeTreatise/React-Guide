# Module 8: Forms and Validation

> **Duration:** Week 8  
> **Difficulty:** Intermediate  
> **Prerequisites:** Modules 1-7 (JavaScript, React Fundamentals, Hooks, State Management, Routing)

## 🎯 Learning Objectives

By the end of this module, you will master:

- **Controlled vs Uncontrolled Components** - Understanding the two approaches to form handling in React
- **Form State Management** - Managing complex form state with hooks and libraries
- **Input Validation** - Client-side validation patterns and strategies
- **Form Libraries** - Using popular form libraries (Formik, React Hook Form, React Final Form)
- **File Uploads** - Handling file inputs and uploads in React
- **Dynamic Forms** - Building forms that change based on user input
- **Form Performance** - Optimizing form rendering and validation
- **Accessibility** - Making forms accessible and user-friendly
- **Error Handling** - Displaying and managing form errors effectively
- **Custom Form Components** - Building reusable form components

## 📋 Module Content Overview

### Core Concepts

1. **Form Fundamentals**
   - Controlled vs Uncontrolled Components
   - Form submission handling
   - Input types and attributes
   - Form validation basics

2. **State Management in Forms**
   - Managing form state with useState
   - Handling multiple inputs
   - Form state normalization
   - Performance considerations

3. **Validation Strategies**
   - Client-side validation
   - Server-side validation integration
   - Real-time vs on-submit validation
   - Custom validation rules

4. **Form Libraries**
   - Formik - Complete form solution
   - React Hook Form - Performance-focused
   - React Final Form - Subscription-based
   - Yup - Schema validation

5. **Advanced Form Patterns**
   - Dynamic form fields
   - Nested forms and field arrays
   - Multi-step forms (wizards)
   - Conditional field rendering

## 🛠 Controlled vs Uncontrolled Components

### Controlled Components
In controlled components, form data is handled by React state:

```jsx
import React, { useState } from 'react';

function ControlledForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Process form data
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name:</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      
      <div>
        <label htmlFor="message">Message:</label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          rows={4}
        />
      </div>
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Uncontrolled Components
In uncontrolled components, form data is handled by the DOM:

```jsx
import React, { useRef } from 'react';

function UncontrolledForm() {
  const formRef = useRef();
  const nameRef = useRef();
  const emailRef = useRef();
  const messageRef = useRef();

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const formData = {
      name: nameRef.current.value,
      email: emailRef.current.value,
      message: messageRef.current.value
    };
    
    console.log('Form submitted:', formData);
    // Process form data
    
    // Reset form
    formRef.current.reset();
  };

  return (
    <form ref={formRef} onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name:</label>
        <input
          type="text"
          id="name"
          name="name"
          ref={nameRef}
          defaultValue=""
          required
        />
      </div>
      
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          ref={emailRef}
          defaultValue=""
          required
        />
      </div>
      
      <div>
        <label htmlFor="message">Message:</label>
        <textarea
          id="message"
          name="message"
          ref={messageRef}
          defaultValue=""
          rows={4}
        />
      </div>
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

## ✅ Form Validation Patterns

### Basic Validation with State

```jsx
import React, { useState } from 'react';

function ValidatedForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const validateField = (name, value) => {
    let error = '';
    
    switch (name) {
      case 'name':
        if (!value.trim()) {
          error = 'Name is required';
        } else if (value.trim().length < 2) {
          error = 'Name must be at least 2 characters';
        }
        break;
        
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!value) {
          error = 'Email is required';
        } else if (!emailRegex.test(value)) {
          error = 'Please enter a valid email';
        }
        break;
        
      case 'password':
        if (!value) {
          error = 'Password is required';
        } else if (value.length < 8) {
          error = 'Password must be at least 8 characters';
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          error = 'Password must contain uppercase, lowercase, and number';
        }
        break;
        
      case 'confirmPassword':
        if (!value) {
          error = 'Please confirm your password';
        } else if (value !== formData.password) {
          error = 'Passwords do not match';
        }
        break;
        
      default:
        break;
    }
    
    return error;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Real-time validation
    if (touched[name]) {
      const error = validateField(name, value);
      setErrors(prev => ({
        ...prev,
        [name]: error
      }));
    }
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    
    const error = validateField(name, value);
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate all fields
    const newErrors = {};
    Object.keys(formData).forEach(key => {
      const error = validateField(key, formData[key]);
      if (error) {
        newErrors[key] = error;
      }
    });
    
    setErrors(newErrors);
    setTouched(Object.keys(formData).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {}));
    
    // If no errors, submit
    if (Object.keys(newErrors).length === 0) {
      console.log('Form submitted:', formData);
      // Process form submission
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div className="form-field">
        <label htmlFor="name">Name *</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          onBlur={handleBlur}
          className={errors.name ? 'error' : ''}
        />
        {errors.name && touched.name && (
          <span className="error-message">{errors.name}</span>
        )}
      </div>
      
      <div className="form-field">
        <label htmlFor="email">Email *</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          className={errors.email ? 'error' : ''}
        />
        {errors.email && touched.email && (
          <span className="error-message">{errors.email}</span>
        )}
      </div>
      
      <div className="form-field">
        <label htmlFor="password">Password *</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          className={errors.password ? 'error' : ''}
        />
        {errors.password && touched.password && (
          <span className="error-message">{errors.password}</span>
        )}
      </div>
      
      <div className="form-field">
        <label htmlFor="confirmPassword">Confirm Password *</label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          className={errors.confirmPassword ? 'error' : ''}
        />
        {errors.confirmPassword && touched.confirmPassword && (
          <span className="error-message">{errors.confirmPassword}</span>
        )}
      </div>
      
      <button 
        type="submit"
        disabled={Object.keys(errors).some(key => errors[key])}
      >
        Register
      </button>
    </form>
  );
}
```

## 📚 Popular Form Libraries

### React Hook Form
Performant forms with easy validation:

```jsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Validation schema
const schema = yup.object({
  name: yup.string().required('Name is required').min(2, 'Name too short'),
  email: yup.string().required('Email is required').email('Invalid email'),
  age: yup.number().positive().integer().required('Age is required'),
});

function ReactHookFormExample() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      name: '',
      email: '',
      age: ''
    }
  });

  const onSubmit = async (data) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Form submitted:', data);
      reset();
    } catch (error) {
      console.error('Submission error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="name">Name</label>
        <input
          {...register('name')}
          type="text"
          id="name"
        />
        {errors.name && (
          <span className="error">{errors.name.message}</span>
        )}
      </div>
      
      <div>
        <label htmlFor="email">Email</label>
        <input
          {...register('email')}
          type="email"
          id="email"
        />
        {errors.email && (
          <span className="error">{errors.email.message}</span>
        )}
      </div>
      
      <div>
        <label htmlFor="age">Age</label>
        <input
          {...register('age')}
          type="number"
          id="age"
        />
        {errors.age && (
          <span className="error">{errors.age.message}</span>
        )}
      </div>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

### Formik Example
Full-featured form library:

```jsx
import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

const validationSchema = Yup.object({
  firstName: Yup.string()
    .max(15, 'Must be 15 characters or less')
    .required('Required'),
  lastName: Yup.string()
    .max(20, 'Must be 20 characters or less')
    .required('Required'),
  email: Yup.string()
    .email('Invalid email address')
    .required('Required'),
  jobType: Yup.string()
    .oneOf(['designer', 'development', 'product', 'other'], 'Invalid Job Type')
    .required('Required'),
});

function FormikExample() {
  return (
    <Formik
      initialValues={{
        firstName: '',
        lastName: '',
        email: '',
        jobType: ''
      }}
      validationSchema={validationSchema}
      onSubmit={(values, { setSubmitting, resetForm }) => {
        setTimeout(() => {
          console.log('Form submitted:', values);
          setSubmitting(false);
          resetForm();
        }, 400);
      }}
    >
      {({ isSubmitting }) => (
        <Form>
          <div>
            <label htmlFor="firstName">First Name</label>
            <Field name="firstName" type="text" />
            <ErrorMessage name="firstName" component="div" className="error" />
          </div>
          
          <div>
            <label htmlFor="lastName">Last Name</label>
            <Field name="lastName" type="text" />
            <ErrorMessage name="lastName" component="div" className="error" />
          </div>
          
          <div>
            <label htmlFor="email">Email Address</label>
            <Field name="email" type="email" />
            <ErrorMessage name="email" component="div" className="error" />
          </div>
          
          <div>
            <label htmlFor="jobType">Job Type</label>
            <Field name="jobType" as="select">
              <option value="">Select a job type</option>
              <option value="designer">Designer</option>
              <option value="development">Developer</option>
              <option value="product">Product Manager</option>
              <option value="other">Other</option>
            </Field>
            <ErrorMessage name="jobType" component="div" className="error" />
          </div>
          
          <button type="submit" disabled={isSubmitting}>
            Submit
          </button>
        </Form>
      )}
    </Formik>
  );
}
```

## 📁 File Upload Handling

```jsx
{% raw %}
import React, { useState } from 'react';

function FileUploadForm() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [dragActive, setDragActive] = useState(false);

  const handleFiles = (files) => {
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(file => {
      // Validate file type and size
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
      const maxSize = 5 * 1024 * 1024; // 5MB
      
      return validTypes.includes(file.type) && file.size <= maxSize;
    });
    
    setSelectedFiles(prev => [...prev, ...validFiles]);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (file, index) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        setUploadProgress(prev => ({
          ...prev,
          [index]: progress
        }));
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      // Actual upload would be here
      // const response = await fetch('/api/upload', {
      //   method: 'POST',
      //   body: formData
      // });
      
      console.log(`${file.name} uploaded successfully`);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const uploadAllFiles = () => {
    selectedFiles.forEach((file, index) => {
      uploadFile(file, index);
    });
  };

  return (
    <div className="file-upload-form">
      <div
        className={`drop-zone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          multiple
          accept="image/*,.pdf"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-input" className="file-input-label">
          <div className="drop-zone-content">
            <p>Drag and drop files here or click to select</p>
            <p className="file-types">Supported: Images (JPG, PNG, GIF), PDF - Max 5MB</p>
          </div>
        </label>
      </div>
      
      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <h3>Selected Files:</h3>
          {selectedFiles.map((file, index) => (
            <div key={index} className="file-item">
              <div className="file-info">
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
              
              {uploadProgress[index] !== undefined && (
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${uploadProgress[index]}%` }}
                  />
                  <span className="progress-text">
                    {uploadProgress[index]}%
                  </span>
                </div>
              )}
              
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="remove-file"
                disabled={uploadProgress[index] !== undefined}
              >
                ×
              </button>
            </div>
          ))}
          
          <button
            type="button"
            onClick={uploadAllFiles}
            className="upload-button"
            disabled={selectedFiles.length === 0}
          >
            Upload All Files
          </button>
        </div>
      )}
    </div>
  );
}
{% endraw %}
```

## 🔄 Dynamic Forms

```jsx
{% raw %}
import React, { useState } from 'react';

function DynamicForm() {
  const [formFields, setFormFields] = useState([
    { id: 1, type: 'text', name: 'name', label: 'Name', value: '', required: true }
  ]);
  
  const [formType, setFormType] = useState('contact');

  const fieldTypes = {
    text: { type: 'text', placeholder: 'Enter text' },
    email: { type: 'email', placeholder: 'Enter email' },
    number: { type: 'number', placeholder: 'Enter number' },
    textarea: { type: 'textarea', placeholder: 'Enter description' },
    select: { type: 'select', options: ['Option 1', 'Option 2', 'Option 3'] },
    checkbox: { type: 'checkbox', label: 'Check this box' },
    radio: { type: 'radio', options: ['Choice 1', 'Choice 2', 'Choice 3'] }
  };

  const formTemplates = {
    contact: [
      { type: 'text', name: 'name', label: 'Full Name', required: true },
      { type: 'email', name: 'email', label: 'Email', required: true },
      { type: 'text', name: 'subject', label: 'Subject', required: true },
      { type: 'textarea', name: 'message', label: 'Message', required: true }
    ],
    survey: [
      { type: 'text', name: 'name', label: 'Your Name', required: true },
      { type: 'radio', name: 'rating', label: 'Overall Rating', required: true },
      { type: 'checkbox', name: 'features', label: 'Liked Features', required: false },
      { type: 'textarea', name: 'feedback', label: 'Additional Feedback', required: false }
    ],
    application: [
      { type: 'text', name: 'firstName', label: 'First Name', required: true },
      { type: 'text', name: 'lastName', label: 'Last Name', required: true },
      { type: 'email', name: 'email', label: 'Email', required: true },
      { type: 'text', name: 'phone', label: 'Phone', required: true },
      { type: 'select', name: 'position', label: 'Position', required: true },
      { type: 'textarea', name: 'experience', label: 'Experience', required: true }
    ]
  };

  const addField = (fieldType) => {
    const newField = {
      id: Date.now(),
      type: fieldType,
      name: `field_${Date.now()}`,
      label: `New ${fieldType} Field`,
      value: '',
      required: false,
      ...fieldTypes[fieldType]
    };
    
    setFormFields(prev => [...prev, newField]);
  };

  const removeField = (id) => {
    setFormFields(prev => prev.filter(field => field.id !== id));
  };

  const updateField = (id, updates) => {
    setFormFields(prev => 
      prev.map(field => 
        field.id === id ? { ...field, ...updates } : field
      )
    );
  };

  const loadTemplate = (templateType) => {
    const template = formTemplates[templateType];
    const fieldsWithIds = template.map((field, index) => ({
      ...field,
      id: Date.now() + index,
      value: ''
    }));
    
    setFormFields(fieldsWithIds);
    setFormType(templateType);
  };

  const handleFieldChange = (id, value) => {
    updateField(id, { value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const formData = {};
    formFields.forEach(field => {
      formData[field.name] = field.value;
    });
    
    console.log('Dynamic form submitted:', formData);
  };

  const renderField = (field) => {
    const { id, type, name, label, value, required, options, placeholder } = field;
    
    switch (type) {
      case 'textarea':
        return (
          <textarea
            id={name}
            name={name}
            value={value}
            onChange={(e) => handleFieldChange(id, e.target.value)}
            placeholder={placeholder}
            required={required}
            rows={4}
          />
        );
        
      case 'select':
        return (
          <select
            id={name}
            name={name}
            value={value}
            onChange={(e) => handleFieldChange(id, e.target.value)}
            required={required}
          >
            <option value="">Select an option</option>
            {options?.map((option, index) => (
              <option key={index} value={option}>{option}</option>
            ))}
          </select>
        );
        
      case 'radio':
        return (
          <div className="radio-group">
            {options?.map((option, index) => (
              <label key={index} className="radio-option">
                <input
                  type="radio"
                  name={name}
                  value={option}
                  checked={value === option}
                  onChange={(e) => handleFieldChange(id, e.target.value)}
                  required={required}
                />
                {option}
              </label>
            ))}
          </div>
        );
        
      case 'checkbox':
        return (
          <label className="checkbox-label">
            <input
              type="checkbox"
              name={name}
              checked={value === true}
              onChange={(e) => handleFieldChange(id, e.target.checked)}
              required={required}
            />
            {label}
          </label>
        );
        
      default:
        return (
          <input
            type={type}
            id={name}
            name={name}
            value={value}
            onChange={(e) => handleFieldChange(id, e.target.value)}
            placeholder={placeholder}
            required={required}
          />
        );
    }
  };

  return (
    <div className="dynamic-form-builder">
      <div className="form-builder-controls">
        <h3>Form Builder</h3>
        
        <div className="templates">
          <h4>Load Template:</h4>
          <button onClick={() => loadTemplate('contact')}>Contact Form</button>
          <button onClick={() => loadTemplate('survey')}>Survey Form</button>
          <button onClick={() => loadTemplate('application')}>Application Form</button>
        </div>
        
        <div className="add-fields">
          <h4>Add Field:</h4>
          {Object.keys(fieldTypes).map(fieldType => (
            <button
              key={fieldType}
              onClick={() => addField(fieldType)}
              className="add-field-btn"
            >
              + {fieldType}
            </button>
          ))}
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="dynamic-form">
        <h2>Dynamic Form ({formType})</h2>
        
        {formFields.map(field => (
          <div key={field.id} className="form-field-container">
            <div className="field-controls">
              <input
                type="text"
                value={field.label}
                onChange={(e) => updateField(field.id, { label: e.target.value })}
                className="field-label-input"
              />
              <label className="required-checkbox">
                <input
                  type="checkbox"
                  checked={field.required}
                  onChange={(e) => updateField(field.id, { required: e.target.checked })}
                />
                Required
              </label>
              <button
                type="button"
                onClick={() => removeField(field.id)}
                className="remove-field-btn"
              >
                Remove
              </button>
            </div>
            
            <div className="form-field">
              <label htmlFor={field.name}>
                {field.label} {field.required && '*'}
              </label>
              {renderField(field)}
            </div>
          </div>
        ))}
        
        <button type="submit" className="submit-btn">
          Submit Form
        </button>
      </form>
    </div>
  );
}
{% endraw %}
```

## 🎨 Form Styling and UX

```css
/* Form styling examples */
.form-field {
  margin-bottom: 1rem;
}

.form-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-field input,
.form-field textarea,
.form-field select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-field input:focus,
.form-field textarea:focus,
.form-field select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-field input.error,
.form-field textarea.error,
.form-field select.error {
  border-color: #ef4444;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.submit-btn {
  background-color: #3b82f6;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s ease-in-out;
}

.drop-zone.active {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.progress-bar {
  width: 100%;
  height: 1rem;
  background-color: #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background-color: #10b981;
  transition: width 0.3s ease-in-out;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 500;
}
```

## 🧪 Testing Forms

```jsx
// Form testing with React Testing Library
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ControlledForm } from './ControlledForm';

describe('ControlledForm', () => {
  test('renders form fields correctly', () => {
    render(<ControlledForm />);
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  test('updates input values on change', async () => {
    const user = userEvent.setup();
    render(<ControlledForm />);
    
    const nameInput = screen.getByLabelText(/name/i);
    const emailInput = screen.getByLabelText(/email/i);
    
    await user.type(nameInput, 'John Doe');
    await user.type(emailInput, 'john@example.com');
    
    expect(nameInput).toHaveValue('John Doe');
    expect(emailInput).toHaveValue('john@example.com');
  });

  test('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<ValidatedForm />);
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });
  });

  test('submits form with valid data', async () => {
    const mockSubmit = jest.fn();
    const user = userEvent.setup();
    
    render(<ControlledForm onSubmit={mockSubmit} />);
    
    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'john@example.com');
    await user.type(screen.getByLabelText(/message/i), 'Test message');
    
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        message: 'Test message'
      });
    });
  });
});
```

## ♿ Accessibility Best Practices

1. **Proper Labels**
   - Use `<label>` elements or `aria-label`
   - Associate labels with form controls using `htmlFor`

2. **Error Handling**
   - Use `aria-describedby` for error messages
   - Ensure error messages are announced by screen readers

3. **Required Fields**
   - Mark required fields clearly
   - Use `aria-required="true"`

4. **Form Structure**
   - Use fieldsets for related form controls
   - Provide clear form instructions

```jsx
function AccessibleForm() {
  const [errors, setErrors] = useState({});

  return (
    <form>
      <fieldset>
        <legend>Personal Information</legend>
        
        <div className="form-field">
          <label htmlFor="name">
            Full Name <span aria-label="required">*</span>
          </label>
          <input
            type="text"
            id="name"
            name="name"
            aria-required="true"
            aria-describedby={errors.name ? "name-error" : undefined}
            aria-invalid={errors.name ? "true" : "false"}
          />
          {errors.name && (
            <div id="name-error" role="alert" className="error-message">
              {errors.name}
            </div>
          )}
        </div>
      </fieldset>
      
      <button type="submit" aria-describedby="submit-help">
        Submit Application
      </button>
      <div id="submit-help" className="form-help">
        Review your information before submitting
      </div>
    </form>
  );
}
```

## 📋 Assessment Checklist

### Basic Form Handling ✅
- [ ] Create controlled components with useState
- [ ] Handle form submission and prevent default behavior
- [ ] Manage multiple input types (text, email, select, textarea, checkbox, radio)
- [ ] Implement uncontrolled components with useRef
- [ ] Handle form reset and initial values

### Validation Implementation ✅
- [ ] Implement client-side validation with custom logic
- [ ] Create real-time validation (onChange) and on-blur validation
- [ ] Display validation errors with proper styling
- [ ] Prevent form submission with validation errors
- [ ] Handle touched/untouched field states

### Form Libraries Integration ✅
- [ ] Set up and use React Hook Form with validation
- [ ] Implement Formik with Yup schema validation
- [ ] Compare performance between different form libraries
- [ ] Handle complex form state with libraries
- [ ] Implement custom form components with libraries

### Advanced Form Features ✅
- [ ] Build file upload functionality with drag-and-drop
- [ ] Create dynamic forms with add/remove fields
- [ ] Implement multi-step forms (wizards)
- [ ] Handle nested forms and field arrays
- [ ] Build conditional field rendering

### Form UX and Accessibility ✅
- [ ] Style forms with proper visual feedback
- [ ] Implement loading states and submit feedback
- [ ] Add accessibility attributes and proper labeling
- [ ] Create responsive form layouts
- [ ] Handle form errors gracefully

## 🚀 Practice Projects

### Project 1: User Registration Form
Build a complete user registration form with:
- Personal information fields
- Password strength validation
- Terms acceptance checkbox
- Real-time validation feedback
- Accessible error handling

### Project 2: Dynamic Survey Builder
Create a survey builder that allows:
- Adding/removing different question types
- Question reordering with drag-and-drop
- Conditional question logic
- Form preview and testing
- Data export functionality

### Project 3: Multi-Step Application Form
Build a job application form with:
- Personal details step
- Work experience step
- File upload for resume/portfolio
- Review and confirmation step
- Progress indicator and navigation

## 📚 Additional Resources

### Documentation
- [React Forms Guide](https://react.dev/reference/react-dom/components/form)
- [React Hook Form Documentation](https://react-hook-form.com/)
- [Formik Documentation](https://formik.org/docs/overview)
- [Yup Validation Schema](https://github.com/jquense/yup)

### Articles & Tutorials
- [The Complete Guide to React Forms](https://blog.logrocket.com/react-forms-guide/)
- [Form Validation in React](https://www.robinwieruch.de/react-form-validation/)
- [React Hook Form vs Formik](https://blog.bitsrc.io/react-hook-form-vs-formik-a-technical-and-performance-comparison-47746bef1335)

### Tools & Libraries
- **Validation**: Yup, Joi, Zod, Vest
- **Form Libraries**: React Hook Form, Formik, React Final Form
- **File Upload**: React Dropzone, Uppy
- **UI Components**: React Select, React Datepicker

---

**Next Module:** [Module 9: Advanced State Management](../09-Advanced-State-Management/README.md)  
**Previous Module:** [Module 7: Routing](../07-Routing/README.md)

> 💡 **Pro Tip:** Start with controlled components and basic validation, then gradually introduce form libraries as your forms become more complex. Focus on user experience and accessibility from the beginning.
