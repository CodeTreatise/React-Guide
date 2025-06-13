# Event Handling & Forms in React

## Table of Contents
1. [Introduction to Event Handling](#introduction-to-event-handling)
2. [React Event System](#react-event-system)
3. [Common Event Types](#common-event-types)
4. [Event Handler Patterns](#event-handler-patterns)
5. [Form Fundamentals](#form-fundamentals)
6. [Controlled Components](#controlled-components)
7. [Uncontrolled Components](#uncontrolled-components)
8. [Form Validation](#form-validation)
9. [Advanced Form Patterns](#advanced-form-patterns)
10. [Form Libraries](#form-libraries)
11. [Best Practices](#best-practices)

---

## Introduction to Event Handling

Event handling in React allows components to respond to user interactions and other events. React provides a synthetic event system that wraps native DOM events with a consistent API across different browsers.

### Basic Event Handling

```jsx
function Button() {
  const handleClick = () => {
    console.log('Button clicked!');
  };

  return (
    <button onClick={handleClick}>
      Click me
    </button>
  );
}
```

### Event Handler with Parameters

```jsx
function UserList({ users, onUserDelete }) {
  const handleDeleteClick = (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      onUserDelete(userId);
    }
  };

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          {user.name}
          <button onClick={() => handleDeleteClick(user.id)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
```

---

## React Event System

React implements a synthetic event system that provides consistent behavior across browsers.

### SyntheticEvent Object

```jsx
function InputExample() {
  const handleChange = (event) => {
    console.log('Event type:', event.type);
    console.log('Target value:', event.target.value);
    console.log('Current target:', event.currentTarget);
    console.log('Native event:', event.nativeEvent);
  };

  return (
    <input 
      type="text" 
      onChange={handleChange} 
      placeholder="Type something..."
    />
  );
}
```

### Preventing Default Behavior

```jsx
function LinkExample() {
  const handleLinkClick = (event) => {
    event.preventDefault();
    console.log('Link clicked, but navigation prevented');
    // Custom navigation logic here
  };

  return (
    <a href="/some-page" onClick={handleLinkClick}>
      Custom Link
    </a>
  );
}
```

### Stopping Event Propagation

```jsx
function NestedExample() {
  const handleParentClick = () => {
    console.log('Parent clicked');
  };

  const handleChildClick = (event) => {
    event.stopPropagation(); // Prevents parent click
    console.log('Child clicked');
  };

  return (
    <div onClick={handleParentClick} style={{ padding: '20px', background: 'lightblue' }}>
      Parent
      <button onClick={handleChildClick}>
        Child Button
      </button>
    </div>
  );
}
```

---

## Common Event Types

### Mouse Events

```jsx
function MouseEventExample() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isMouseDown, setIsMouseDown] = useState(false);

  const handleMouseMove = (event) => {
    setPosition({ x: event.clientX, y: event.clientY });
  };

  const handleMouseDown = () => setIsMouseDown(true);
  const handleMouseUp = () => setIsMouseDown(false);

  const handleDoubleClick = () => {
    alert('Double clicked!');
  };

  const handleContextMenu = (event) => {
    event.preventDefault();
    alert('Right-clicked!');
  };

  return (
    <div
      onMouseMove={handleMouseMove}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onDoubleClick={handleDoubleClick}
      onContextMenu={handleContextMenu}
      style={{
        height: '200px',
        background: isMouseDown ? 'lightcoral' : 'lightgray',
        padding: '20px'
      }}
    >
      <p>Mouse position: ({position.x}, {position.y})</p>
      <p>Mouse down: {isMouseDown ? 'Yes' : 'No'}</p>
    </div>
  );
}
```

### Keyboard Events

```jsx
function KeyboardEventExample() {
  const [lastKey, setLastKey] = useState('');
  const [message, setMessage] = useState('');

  const handleKeyDown = (event) => {
    setLastKey(event.key);
    
    // Handle specific keys
    if (event.key === 'Enter') {
      console.log('Enter pressed');
    } else if (event.key === 'Escape') {
      setMessage('');
    } else if (event.ctrlKey && event.key === 's') {
      event.preventDefault();
      console.log('Ctrl+S pressed - Save action');
    }
  };

  return (
    <div>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type something... (Try Enter, Escape, Ctrl+S)"
      />
      <p>Last key pressed: {lastKey}</p>
      <p>Current message: {message}</p>
    </div>
  );
}
```

---

## Form Fundamentals

Forms are essential for user input in web applications. React provides powerful patterns for handling form data.

### Basic Form Structure

```jsx
function BasicForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log('Form submitted:', formData);
    // Process form data
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name:</label>
        <input
          id="name"
          name="name"
          type="text"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
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

---

## Controlled Components

Controlled components have their form data handled by React state.

### Text Inputs

```jsx
function ControlledTextInput() {
  const [value, setValue] = useState('');

  const handleChange = (event) => {
    setValue(event.target.value);
  };

  return (
    <div>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder="Controlled input"
      />
      <p>Current value: {value}</p>
    </div>
  );
}
```

### Checkboxes and Radio Buttons

```jsx
function ControlledCheckboxRadio() {
  const [preferences, setPreferences] = useState({
    newsletter: false,
    notifications: true,
    theme: 'light'
  });

  const handleCheckboxChange = (event) => {
    const { name, checked } = event.target;
    setPreferences(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handleRadioChange = (event) => {
    setPreferences(prev => ({
      ...prev,
      theme: event.target.value
    }));
  };

  return (
    <form>
      <div>
        <label>
          <input
            type="checkbox"
            name="newsletter"
            checked={preferences.newsletter}
            onChange={handleCheckboxChange}
          />
          Subscribe to newsletter
        </label>
      </div>
      <div>
        <fieldset>
          <legend>Theme preference:</legend>
          <label>
            <input
              type="radio"
              name="theme"
              value="light"
              checked={preferences.theme === 'light'}
              onChange={handleRadioChange}
            />
            Light
          </label>
          <label>
            <input
              type="radio"
              name="theme"
              value="dark"
              checked={preferences.theme === 'dark'}
              onChange={handleRadioChange}
            />
            Dark
          </label>
        </fieldset>
      </div>
    </form>
  );
}
```

---

## Uncontrolled Components

Uncontrolled components manage their own state internally and use refs to access values.

### Basic Uncontrolled Form

```jsx
function UncontrolledForm() {
  const nameRef = useRef();
  const emailRef = useRef();
  const fileRef = useRef();

  const handleSubmit = (event) => {
    event.preventDefault();
    
    const formData = {
      name: nameRef.current.value,
      email: emailRef.current.value,
      file: fileRef.current.files[0]
    };
    
    console.log('Form data:', formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>
          Name:
          <input
            type="text"
            ref={nameRef}
            defaultValue="John Doe"
          />
        </label>
      </div>
      <div>
        <label>
          Email:
          <input
            type="email"
            ref={emailRef}
          />
        </label>
      </div>
      <div>
        <label>
          File:
          <input
            type="file"
            ref={fileRef}
          />
        </label>
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## Form Validation

### Client-Side Validation

```jsx
function ValidatedForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const validateField = (name, value) => {
    let error = '';

    switch (name) {
      case 'username':
        if (!value) {
          error = 'Username is required';
        } else if (value.length < 3) {
          error = 'Username must be at least 3 characters';
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
        }
        break;
      
      case 'confirmPassword':
        if (!value) {
          error = 'Please confirm your password';
        } else if (value !== formData.password) {
          error = 'Passwords do not match';
        }
        break;
    }

    return error;
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    ));

    // Validate field if it has been touched
    if (touched[name]) {
      const error = validateField(name, value);
      setErrors(prev => ({
        ...prev,
        [name]: error
      }));
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    // Validate all fields
    const newErrors = {};
    Object.keys(formData).forEach(key => {
      const error = validateField(key, formData[key]);
      if (error) newErrors[key] = error;
    });

    setErrors(newErrors);
    setTouched(Object.keys(formData).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {}));

    // Submit if no errors
    if (Object.keys(newErrors).length === 0) {
      console.log('Form submitted:', formData);
      alert('Registration successful!');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="username">Username:</label>
        <input
          id="username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          className={errors.username ? 'error' : ''}
        />
        {errors.username && <span className="error-message">{errors.username}</span>}
      </div>

      <div>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          className={errors.email ? 'error' : ''}
        />
        {errors.email && <span className="error-message">{errors.email}</span>}
      </div>

      <div>
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          className={errors.password ? 'error' : ''}
        />
        {errors.password && <span className="error-message">{errors.password}</span>}
      </div>

      <div>
        <label htmlFor="confirmPassword">Confirm Password:</label>
        <input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange}
          className={errors.confirmPassword ? 'error' : ''}
        />
        {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
      </div>

      <button type="submit">Register</button>
    </form>
  );
}
```

---

## Advanced Form Patterns

### Dynamic Form Fields

```jsx
function DynamicForm() {
  const [contacts, setContacts] = useState([
    { id: 1, name: '', email: '', phone: '' }
  ]);

  const addContact = () => {
    const newContact = {
      id: Date.now(),
      name: '',
      email: '',
      phone: ''
    };
    setContacts(prev => [...prev, newContact]);
  };

  const removeContact = (id) => {
    setContacts(prev => prev.filter(contact => contact.id !== id));
  };

  const updateContact = (id, field, value) => {
    setContacts(prev =>
      prev.map(contact =>
        contact.id === id
          ? { ...contact, [field]: value }
          : contact
      )
    );
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log('Contacts:', contacts);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Contact Information</h3>
      {contacts.map((contact, index) => (
        <div key={contact.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
          <h4>Contact {index + 1}</h4>
          <div>
            <input
              type="text"
              placeholder="Name"
              value={contact.name}
              onChange={(e) => updateContact(contact.id, 'name', e.target.value)}
            />
          </div>
          <div>
            <input
              type="email"
              placeholder="Email"
              value={contact.email}
              onChange={(e) => updateContact(contact.id, 'email', e.target.value)}
            />
          </div>
          {contacts.length > 1 && (
            <button
              type="button"
              onClick={() => removeContact(contact.id)}
            >
              Remove Contact
            </button>
          )}
        </div>
      ))}
      
      <button type="button" onClick={addContact}>
        Add Contact
      </button>
      <button type="submit">Submit All Contacts</button>
    </form>
  );
}
```

---

## Form Libraries

### React Hook Form

```jsx
import { useForm } from 'react-hook-form';

function ReactHookFormExample() {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting }
  } = useForm();

  const onSubmit = async (data) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log('Form data:', data);
    alert('Form submitted successfully!');
  };

  const watchAllFields = watch();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input
          {...register('firstName', {
            required: 'First name is required',
            minLength: {
              value: 2,
              message: 'First name must be at least 2 characters'
            }
          })}
          placeholder="First Name"
        />
        {errors.firstName && (
          <span style={{ color: 'red' }}>{errors.firstName.message}</span>
        )}
      </div>

      <div>
        <input
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^\S+@\S+$/i,
              message: 'Invalid email address'
            }
          })}
          type="email"
          placeholder="Email"
        />
        {errors.email && (
          <span style={{ color: 'red' }}>{errors.email.message}</span>
        )}
      </div>

      <div>
        <input
          {...register('age', {
            required: 'Age is required',
            min: {
              value: 18,
              message: 'Must be at least 18 years old'
            },
            max: {
              value: 120,
              message: 'Must be less than 120 years old'
            }
          })}
          type="number"
          placeholder="Age"
        />
        {errors.age && (
          <span style={{ color: 'red' }}>{errors.age.message}</span>
        )}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>

      <div>
        <h4>Form Values (Real-time):</h4>
        <pre>{JSON.stringify(watchAllFields, null, 2)}</pre>
      </div>
    </form>
  );
}
```

### Formik

```jsx
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

const validationSchema = Yup.object({
  name: Yup.string()
    .min(2, 'Too Short!')
    .max(50, 'Too Long!')
    .required('Required'),
  email: Yup.string()
    .email('Invalid email')
    .required('Required'),
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .required('Required')
});

function FormikExample() {
  const initialValues = {
    name: '',
    email: '',
    password: ''
  };

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Form submitted:', values);
      alert('Registration successful!');
      resetForm();
    } catch (error) {
      console.error('Submission error:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ isSubmitting, touched, errors }) => (
        <Form>
          <div>
            <Field
              name="name"
              type="text"
              placeholder="Name"
              style={{
                borderColor: touched.name && errors.name ? 'red' : 'initial'
              }}
            />
            <ErrorMessage name="name" component="div" style={{ color: 'red' }} />
          </div>

          <div>
            <Field
              name="email"
              type="email"
              placeholder="Email"
              style={{
                borderColor: touched.email && errors.email ? 'red' : 'initial'
              }}
            />
            <ErrorMessage name="email" component="div" style={{ color: 'red' }} />
          </div>

          <div>
            <Field
              name="password"
              type="password"
              placeholder="Password"
              style={{
                borderColor: touched.password && errors.password ? 'red' : 'initial'
              }}
            />
            <ErrorMessage name="password" component="div" style={{ color: 'red' }} />
          </div>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        </Form>
      )}
    </Formik>
  );
}
```

---

## Best Practices

### Event Handler Optimization

```jsx
// ❌ Bad: Creates new function on every render
function BadExample({ items, onItemClick }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => onItemClick(item.id)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
}

// ✅ Good: Optimized event handling
function GoodExample({ items, onItemClick }) {
  const handleItemClick = useCallback((event) => {
    const itemId = event.currentTarget.dataset.itemId;
    onItemClick(Number(itemId));
  }, [onItemClick]);

  return (
    <ul>
      {items.map(item => (
        <li
          key={item.id}
          data-item-id={item.id}
          onClick={handleItemClick}
        >
          {item.name}
        </li>
      ))}
    </ul>
  );
}
```

### Accessibility Considerations

```jsx
function AccessibleForm() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <form noValidate>
      <div>
        <label htmlFor="username">
          Username:
        </label>
        <input
          id="username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          aria-describedby={errors.username ? "username-error" : undefined}
          aria-invalid={!!errors.username}
          required
        />
        {errors.username && (
          <div id="username-error" role="alert" aria-live="polite">
            {errors.username}
          </div>
        )}
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## Summary

Event handling and forms are fundamental aspects of React development. Understanding the event system, form patterns, and validation techniques is essential for building interactive user interfaces.

### Key Takeaways

1. **React Event System**: Use SyntheticEvents for consistent cross-browser behavior
2. **Controlled vs Uncontrolled**: Prefer controlled components for form inputs
3. **Event Handler Patterns**: Use useCallback to optimize performance
4. **Form Validation**: Implement both client-side and server-side validation
5. **Accessibility**: Always include proper labels, ARIA attributes, and error handling
6. **Performance**: Debounce inputs and memoize expensive operations
