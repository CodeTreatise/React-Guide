# File Upload and Dynamic Forms

> **Advanced File Handling, Dynamic Form Generation, and Complex User Interactions**

## 🎯 Overview

This comprehensive guide covers advanced file upload patterns, dynamic form generation, complex user interactions, and real-world implementations for modern React applications.

## 📋 Table of Contents

1. [File Upload Patterns](#file-upload-patterns)
2. [Drag and Drop Implementation](#drag-and-drop-implementation)
3. [Multiple File Handling](#multiple-file-handling)
4. [File Validation and Processing](#file-validation-and-processing)
5. [Dynamic Form Generation](#dynamic-form-generation)
6. [Conditional Field Rendering](#conditional-field-rendering)
7. [Form Builder Implementation](#form-builder-implementation)
8. [Progressive Enhancement](#progressive-enhancement)

## 📁 File Upload Patterns

### Basic File Upload with React Hook Form

```jsx
import { useForm, useController } from 'react-hook-form';
import { useState } from 'react';

// Custom File Input Component
const FileInput = ({ control, name, accept, multiple = false, ...props }) => {
  const {
    field: { onChange, value, ...field },
    fieldState: { error }
  } = useController({
    name,
    control,
    rules: props.rules
  });

  const [preview, setPreview] = useState(null);

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = multiple ? Array.from(files) : files[0];
      onChange(file);
      
      // Generate preview for images
      if (!multiple && files[0] && files[0].type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(files[0]);
      }
    }
  };

  return (
    <div className="file-input-container">
      <input
        {...field}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileChange}
        className={error ? 'error' : ''}
      />
      {error && <span className="error">{error.message}</span>}
      {preview && (
        <div className="file-preview">
          <img src={preview} alt="Preview" style={{ maxWidth: '200px', maxHeight: '200px' }} />
        </div>
      )}
    </div>
  );
};

function BasicFileUploadForm() {
  const { control, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    const formData = new FormData();
    
    // Append other form data
    Object.keys(data).forEach(key => {
      if (key !== 'file' && key !== 'documents') {
        formData.append(key, data[key]);
      }
    });

    // Append files
    if (data.file) {
      formData.append('file', data.file);
    }
    
    if (data.documents) {
      data.documents.forEach((doc, index) => {
        formData.append(`documents[${index}]`, doc);
      });
    }

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        console.log('Files uploaded successfully');
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} encType="multipart/form-data">
      <div>
        <label>Profile Picture</label>
        <FileInput
          control={control}
          name="file"
          accept="image/*"
          rules={{
            required: 'Profile picture is required',
            validate: {
              fileSize: (file) => {
                if (file && file.size > 5 * 1024 * 1024) {
                  return 'File size must be less than 5MB';
                }
                return true;
              },
              fileType: (file) => {
                if (file && !file.type.startsWith('image/')) {
                  return 'Only image files are allowed';
                }
                return true;
              }
            }
          }}
        />
      </div>

      <div>
        <label>Supporting Documents</label>
        <FileInput
          control={control}
          name="documents"
          accept=".pdf,.doc,.docx"
          multiple
          rules={{
            validate: {
              maxFiles: (files) => {
                if (files && files.length > 5) {
                  return 'Maximum 5 files allowed';
                }
                return true;
              },
              totalSize: (files) => {
                if (files) {
                  const totalSize = files.reduce((sum, file) => sum + file.size, 0);
                  if (totalSize > 10 * 1024 * 1024) {
                    return 'Total file size must be less than 10MB';
                  }
                }
                return true;
              }
            }
          }}
        />
      </div>

      <button type="submit">Upload Files</button>
    </form>
  );
}
```

### Advanced File Upload with Progress

```jsx
import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';

const AdvancedFileUpload = () => {
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadStatus, setUploadStatus] = useState({});
  const abortControllers = useRef({});

  const { register, handleSubmit, setValue, watch } = useForm();
  const files = watch('files');

  const uploadFile = async (file, index) => {
    const controller = new AbortController();
    abortControllers.current[index] = controller;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadStatus(prev => ({ ...prev, [index]: 'uploading' }));

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
        signal: controller.signal,
        // Custom XMLHttpRequest for progress tracking
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(prev => ({ ...prev, [index]: percentCompleted }));
        }
      });

      if (response.ok) {
        setUploadStatus(prev => ({ ...prev, [index]: 'success' }));
        setUploadProgress(prev => ({ ...prev, [index]: 100 }));
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        setUploadStatus(prev => ({ ...prev, [index]: 'cancelled' }));
      } else {
        setUploadStatus(prev => ({ ...prev, [index]: 'error' }));
        console.error('Upload error:', error);
      }
    }
  };

  const uploadFileWithProgress = (file, index) => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', file);

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentCompleted = Math.round((event.loaded * 100) / event.total);
          setUploadProgress(prev => ({ ...prev, [index]: percentCompleted }));
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          setUploadStatus(prev => ({ ...prev, [index]: 'success' }));
          resolve(xhr.response);
        } else {
          setUploadStatus(prev => ({ ...prev, [index]: 'error' }));
          reject(new Error('Upload failed'));
        }
      });

      xhr.addEventListener('error', () => {
        setUploadStatus(prev => ({ ...prev, [index]: 'error' }));
        reject(new Error('Upload failed'));
      });

      xhr.addEventListener('abort', () => {
        setUploadStatus(prev => ({ ...prev, [index]: 'cancelled' }));
        reject(new Error('Upload cancelled'));
      });

      // Store xhr for cancellation
      abortControllers.current[index] = xhr;

      setUploadStatus(prev => ({ ...prev, [index]: 'uploading' }));
      xhr.open('POST', '/api/upload');
      xhr.send(formData);
    });
  };

  const cancelUpload = (index) => {
    const controller = abortControllers.current[index];
    if (controller) {
      if (controller.abort) {
        controller.abort(); // XMLHttpRequest
      } else {
        controller.abort(); // AbortController
      }
      delete abortControllers.current[index];
    }
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setValue('files', selectedFiles);
    
    // Reset progress and status
    setUploadProgress({});
    setUploadStatus({});
  };

  const startUpload = async () => {
    if (!files) return;

    const uploadPromises = files.map((file, index) => 
      uploadFileWithProgress(file, index)
    );

    try {
      await Promise.all(uploadPromises);
      console.log('All files uploaded successfully');
    } catch (error) {
      console.error('Some uploads failed:', error);
    }
  };

  const renderFileList = () => {
    if (!files) return null;

    return files.map((file, index) => (
      <div key={index} className="file-item">
        <div className="file-info">
          <span className="file-name">{file.name}</span>
          <span className="file-size">{formatFileSize(file.size)}</span>
        </div>
        
        <div className="upload-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${uploadProgress[index] || 0}%` }}
            />
          </div>
          <span className="progress-text">
            {uploadProgress[index] || 0}%
          </span>
        </div>
        
        <div className="upload-status">
          {uploadStatus[index] === 'uploading' && (
            <button onClick={() => cancelUpload(index)}>Cancel</button>
          )}
          {uploadStatus[index] === 'success' && <span>✓ Complete</span>}
          {uploadStatus[index] === 'error' && <span>✗ Failed</span>}
          {uploadStatus[index] === 'cancelled' && <span>Cancelled</span>}
        </div>
      </div>
    ));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="advanced-file-upload">
      <div className="file-input-section">
        <input
          type="file"
          multiple
          onChange={handleFileSelect}
          className="file-input"
        />
        {files && files.length > 0 && (
          <button onClick={startUpload} className="upload-button">
            Upload All Files
          </button>
        )}
      </div>
      
      <div className="file-list">
        {renderFileList()}
      </div>
    </div>
  );
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
```

## 🎯 Drag and Drop Implementation

### Advanced Drag and Drop File Upload

```jsx
import { useState, useRef, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const DragDropFileUpload = ({ onFilesAdded, acceptedTypes, maxSize, maxFiles }) => {
  const [draggedFiles, setDraggedFiles] = useState([]);
  const [errors, setErrors] = useState([]);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setErrors([]);
    
    if (rejectedFiles.length > 0) {
      const errorMessages = rejectedFiles.map(({ file, errors }) => ({
        fileName: file.name,
        errors: errors.map(error => error.message)
      }));
      setErrors(errorMessages);
    }

    if (acceptedFiles.length > 0) {
      setDraggedFiles(prev => [...prev, ...acceptedFiles]);
      onFilesAdded?.(acceptedFiles);
    }
  }, [onFilesAdded]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    maxSize,
    maxFiles,
    multiple: true
  });

  const removeFile = (fileToRemove) => {
    setDraggedFiles(files => files.filter(file => file !== fileToRemove));
  };

  const getDropzoneClassName = () => {
    let className = 'dropzone';
    if (isDragActive) className += ' active';
    if (isDragAccept) className += ' accept';
    if (isDragReject) className += ' reject';
    return className;
  };

  return (
    <div className="drag-drop-container">
      <div {...getRootProps({ className: getDropzoneClassName() })}>
        <input {...getInputProps()} />
        <div className="dropzone-content">
          {isDragActive ? (
            <p>Drop the files here...</p>
          ) : (
            <div>
              <p>Drag 'n' drop files here, or click to select files</p>
              <em>(Maximum {maxFiles} files, {formatFileSize(maxSize)} each)</em>
            </div>
          )}
        </div>
      </div>

      {errors.length > 0 && (
        <div className="upload-errors">
          <h4>Upload Errors:</h4>
          {errors.map((error, index) => (
            <div key={index} className="error-item">
              <strong>{error.fileName}:</strong>
              <ul>
                {error.errors.map((err, errIndex) => (
                  <li key={errIndex}>{err}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {draggedFiles.length > 0 && (
        <div className="file-preview">
          <h4>Selected Files:</h4>
          {draggedFiles.map((file, index) => (
            <FilePreviewItem
              key={index}
              file={file}
              onRemove={() => removeFile(file)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const FilePreviewItem = ({ file, onRemove }) => {
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (file.type.startsWith('image/')) {
      setIsLoading(true);
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
        setIsLoading(false);
      };
      reader.readAsDataURL(file);
    }
  }, [file]);

  return (
    <div className="file-preview-item">
      <div className="file-thumbnail">
        {isLoading ? (
          <div className="loading">Loading...</div>
        ) : preview ? (
          <img src={preview} alt={file.name} />
        ) : (
          <div className="file-icon">📄</div>
        )}
      </div>
      
      <div className="file-details">
        <div className="file-name">{file.name}</div>
        <div className="file-size">{formatFileSize(file.size)}</div>
        <div className="file-type">{file.type || 'Unknown'}</div>
      </div>
      
      <button onClick={onRemove} className="remove-button">
        ✕
      </button>
    </div>
  );
};

// Usage example
function DragDropUploadForm() {
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('idle');

  const handleFilesAdded = (newFiles) => {
    setFiles(prev => [...prev, ...newFiles]);
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploadStatus('uploading');
    
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`files[${index}]`, file);
    });

    try {
      const response = await fetch('/api/upload-multiple', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        setUploadStatus('success');
        setFiles([]);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      setUploadStatus('error');
      console.error('Upload error:', error);
    }
  };

  return (
    <div className="drag-drop-form">
      <DragDropFileUpload
        onFilesAdded={handleFilesAdded}
        acceptedTypes={{
          'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
          'application/pdf': ['.pdf'],
          'application/msword': ['.doc'],
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        }}
        maxSize={5 * 1024 * 1024} // 5MB
        maxFiles={10}
      />

      {files.length > 0 && (
        <div className="upload-actions">
          <p>{files.length} file(s) selected</p>
          <button 
            onClick={uploadFiles}
            disabled={uploadStatus === 'uploading'}
          >
            {uploadStatus === 'uploading' ? 'Uploading...' : 'Upload Files'}
          </button>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="success-message">Files uploaded successfully!</div>
      )}
      
      {uploadStatus === 'error' && (
        <div className="error-message">Upload failed. Please try again.</div>
      )}
    </div>
  );
}
```

### Custom Drag and Drop Hook

```jsx
import { useState, useRef, useCallback } from 'react';

const useDragAndDrop = (onDrop) => {
  const [dragState, setDragState] = useState({
    isDragging: false,
    isOver: false,
    canDrop: false
  });
  
  const dragCounter = useRef(0);
  const dropRef = useRef(null);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    
    dragCounter.current++;
    
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragState(prev => ({ 
        ...prev, 
        isDragging: true, 
        isOver: true,
        canDrop: true 
      }));
    }
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    
    dragCounter.current--;
    
    if (dragCounter.current === 0) {
      setDragState(prev => ({ 
        ...prev, 
        isDragging: false, 
        isOver: false,
        canDrop: false 
      }));
    }
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Change cursor to indicate drop zone
    e.dataTransfer.dropEffect = 'copy';
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    
    setDragState({
      isDragging: false,
      isOver: false,
      canDrop: false
    });
    
    dragCounter.current = 0;
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files);
      onDrop(files);
      e.dataTransfer.clearData();
    }
  }, [onDrop]);

  const getDragProps = useCallback(() => ({
    ref: dropRef,
    onDragEnter: handleDragEnter,
    onDragLeave: handleDragLeave,
    onDragOver: handleDragOver,
    onDrop: handleDrop
  }), [handleDragEnter, handleDragLeave, handleDragOver, handleDrop]);

  return {
    ...dragState,
    getDragProps
  };
};

// Usage example
function CustomDragDropComponent() {
  const [files, setFiles] = useState([]);

  const handleDrop = useCallback((droppedFiles) => {
    setFiles(prev => [...prev, ...droppedFiles]);
  }, []);

  const { isDragging, isOver, canDrop, getDragProps } = useDragAndDrop(handleDrop);

  return (
    <div 
      {...getDragProps()}
      className={`custom-drop-zone ${isDragging ? 'dragging' : ''} ${isOver ? 'over' : ''}`}
    >
      {isDragging ? (
        <p>Drop files here!</p>
      ) : (
        <p>Drag and drop files here</p>
      )}
      
      {files.length > 0 && (
        <ul>
          {files.map((file, index) => (
            <li key={index}>{file.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## 🔧 Dynamic Form Generation

### Schema-Based Dynamic Forms

```jsx
import { useForm, useFieldArray } from 'react-hook-form';
import { useState } from 'react';

// Form field schema structure
const formSchema = {
  title: "User Registration",
  sections: [
    {
      title: "Personal Information",
      fields: [
        {
          name: "firstName",
          type: "text",
          label: "First Name",
          required: true,
          validation: {
            minLength: 2,
            maxLength: 50
          }
        },
        {
          name: "lastName",
          type: "text",
          label: "Last Name",
          required: true,
          validation: {
            minLength: 2,
            maxLength: 50
          }
        },
        {
          name: "email",
          type: "email",
          label: "Email Address",
          required: true,
          validation: {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
          }
        },
        {
          name: "age",
          type: "number",
          label: "Age",
          required: true,
          validation: {
            min: 18,
            max: 120
          }
        }
      ]
    },
    {
      title: "Contact Information",
      fields: [
        {
          name: "phone",
          type: "tel",
          label: "Phone Number",
          required: false
        },
        {
          name: "address",
          type: "textarea",
          label: "Address",
          required: false,
          rows: 3
        },
        {
          name: "country",
          type: "select",
          label: "Country",
          required: true,
          options: [
            { value: "us", label: "United States" },
            { value: "ca", label: "Canada" },
            { value: "uk", label: "United Kingdom" }
          ]
        }
      ]
    },
    {
      title: "Preferences",
      fields: [
        {
          name: "newsletter",
          type: "checkbox",
          label: "Subscribe to newsletter"
        },
        {
          name: "notifications",
          type: "radio",
          label: "Notification Preference",
          options: [
            { value: "email", label: "Email" },
            { value: "sms", label: "SMS" },
            { value: "none", label: "None" }
          ]
        },
        {
          name: "interests",
          type: "multiselect",
          label: "Interests",
          options: [
            { value: "tech", label: "Technology" },
            { value: "sports", label: "Sports" },
            { value: "music", label: "Music" },
            { value: "travel", label: "Travel" }
          ]
        }
      ]
    }
  ]
};

// Dynamic field renderer
const DynamicField = ({ field, register, errors, control }) => {
  const { name, type, label, required, validation, options, rows } = field;

  const getValidationRules = () => {
    const rules = { required: required ? `${label} is required` : false };
    
    if (validation) {
      if (validation.minLength) {
        rules.minLength = {
          value: validation.minLength,
          message: `${label} must be at least ${validation.minLength} characters`
        };
      }
      if (validation.maxLength) {
        rules.maxLength = {
          value: validation.maxLength,
          message: `${label} must not exceed ${validation.maxLength} characters`
        };
      }
      if (validation.min) {
        rules.min = {
          value: validation.min,
          message: `${label} must be at least ${validation.min}`
        };
      }
      if (validation.max) {
        rules.max = {
          value: validation.max,
          message: `${label} must not exceed ${validation.max}`
        };
      }
      if (validation.pattern) {
        rules.pattern = {
          value: validation.pattern,
          message: `${label} format is invalid`
        };
      }
    }
    
    return rules;
  };

  const renderField = () => {
    switch (type) {
      case 'text':
      case 'email':
      case 'tel':
      case 'number':
        return (
          <input
            {...register(name, getValidationRules())}
            type={type}
            className={errors[name] ? 'error' : ''}
          />
        );

      case 'textarea':
        return (
          <textarea
            {...register(name, getValidationRules())}
            rows={rows || 3}
            className={errors[name] ? 'error' : ''}
          />
        );

      case 'select':
        return (
          <select
            {...register(name, getValidationRules())}
            className={errors[name] ? 'error' : ''}
          >
            <option value="">Select {label}</option>
            {options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'checkbox':
        return (
          <label className="checkbox-label">
            <input
              {...register(name)}
              type="checkbox"
            />
            {label}
          </label>
        );

      case 'radio':
        return (
          <div className="radio-group">
            {options?.map(option => (
              <label key={option.value} className="radio-label">
                <input
                  {...register(name, getValidationRules())}
                  type="radio"
                  value={option.value}
                />
                {option.label}
              </label>
            ))}
          </div>
        );

      case 'multiselect':
        return (
          <Controller
            name={name}
            control={control}
            rules={getValidationRules()}
            render={({ field: { onChange, value } }) => (
              <div className="multiselect">
                {options?.map(option => (
                  <label key={option.value} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={value?.includes(option.value) || false}
                      onChange={(e) => {
                        const newValue = value || [];
                        if (e.target.checked) {
                          onChange([...newValue, option.value]);
                        } else {
                          onChange(newValue.filter(v => v !== option.value));
                        }
                      }}
                    />
                    {option.label}
                  </label>
                ))}
              </div>
            )}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="form-field">
      {type !== 'checkbox' && <label>{label}{required && ' *'}</label>}
      {renderField()}
      {errors[name] && <span className="error">{errors[name].message}</span>}
    </div>
  );
};

// Dynamic form component
function DynamicForm({ schema }) {
  const { register, handleSubmit, control, formState: { errors } } = useForm();

  const onSubmit = (data) => {
    console.log('Dynamic form data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="dynamic-form">
      <h2>{schema.title}</h2>
      
      {schema.sections.map((section, sectionIndex) => (
        <div key={sectionIndex} className="form-section">
          <h3>{section.title}</h3>
          
          {section.fields.map((field, fieldIndex) => (
            <DynamicField
              key={fieldIndex}
              field={field}
              register={register}
              errors={errors}
              control={control}
            />
          ))}
        </div>
      ))}
      
      <button type="submit">Submit</button>
    </form>
  );
}

// Usage
function DynamicFormExample() {
  return <DynamicForm schema={formSchema} />;
}
```

### Form Builder with Visual Editor

```jsx
import { useState, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

// Field type definitions
const fieldTypes = {
  text: { label: 'Text Input', icon: '📝' },
  email: { label: 'Email Input', icon: '📧' },
  number: { label: 'Number Input', icon: '🔢' },
  textarea: { label: 'Text Area', icon: '📄' },
  select: { label: 'Select Dropdown', icon: '📋' },
  checkbox: { label: 'Checkbox', icon: '☑️' },
  radio: { label: 'Radio Button', icon: '⚪' },
  file: { label: 'File Upload', icon: '📁' }
};

// Field configuration component
const FieldConfigurator = ({ field, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editingField, setEditingField] = useState(field);

  const handleSave = () => {
    onUpdate(editingField);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditingField(field);
    setIsEditing(false);
  };

  return (
    <div className="field-configurator">
      {!isEditing ? (
        <div className="field-preview">
          <div className="field-header">
            <span>{fieldTypes[field.type]?.icon} {field.label || 'Untitled Field'}</span>
            <div className="field-actions">
              <button onClick={() => setIsEditing(true)}>Edit</button>
              <button onClick={onDelete}>Delete</button>
            </div>
          </div>
          <div className="field-type">{fieldTypes[field.type]?.label}</div>
        </div>
      ) : (
        <div className="field-editor">
          <div className="editor-row">
            <label>Label:</label>
            <input
              value={editingField.label}
              onChange={(e) => setEditingField(prev => ({ ...prev, label: e.target.value }))}
            />
          </div>
          
          <div className="editor-row">
            <label>Name:</label>
            <input
              value={editingField.name}
              onChange={(e) => setEditingField(prev => ({ ...prev, name: e.target.value }))}
            />
          </div>
          
          <div className="editor-row">
            <label>Required:</label>
            <input
              type="checkbox"
              checked={editingField.required || false}
              onChange={(e) => setEditingField(prev => ({ ...prev, required: e.target.checked }))}
            />
          </div>
          
          {(editingField.type === 'select' || editingField.type === 'radio') && (
            <div className="editor-row">
              <label>Options:</label>
              <OptionsEditor
                options={editingField.options || []}
                onChange={(options) => setEditingField(prev => ({ ...prev, options }))}
              />
            </div>
          )}
          
          <div className="editor-actions">
            <button onClick={handleSave}>Save</button>
            <button onClick={handleCancel}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
};

// Options editor for select and radio fields
const OptionsEditor = ({ options, onChange }) => {
  const addOption = () => {
    onChange([...options, { value: '', label: '' }]);
  };

  const updateOption = (index, field, value) => {
    const newOptions = [...options];
    newOptions[index] = { ...newOptions[index], [field]: value };
    onChange(newOptions);
  };

  const removeOption = (index) => {
    onChange(options.filter((_, i) => i !== index));
  };

  return (
    <div className="options-editor">
      {options.map((option, index) => (
        <div key={index} className="option-row">
          <input
            placeholder="Value"
            value={option.value}
            onChange={(e) => updateOption(index, 'value', e.target.value)}
          />
          <input
            placeholder="Label"
            value={option.label}
            onChange={(e) => updateOption(index, 'label', e.target.value)}
          />
          <button onClick={() => removeOption(index)}>×</button>
        </div>
      ))}
      <button onClick={addOption}>Add Option</button>
    </div>
  );
};

// Main form builder component
const FormBuilder = () => {
  const [formFields, setFormFields] = useState([]);
  const [formTitle, setFormTitle] = useState('New Form');

  const generateFieldId = () => `field_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const addField = (type) => {
    const newField = {
      id: generateFieldId(),
      type,
      name: `field_${formFields.length + 1}`,
      label: `${fieldTypes[type].label} ${formFields.length + 1}`,
      required: false
    };
    
    if (type === 'select' || type === 'radio') {
      newField.options = [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2' }
      ];
    }
    
    setFormFields(prev => [...prev, newField]);
  };

  const updateField = (fieldId, updatedField) => {
    setFormFields(prev => prev.map(field => 
      field.id === fieldId ? { ...field, ...updatedField } : field
    ));
  };

  const deleteField = (fieldId) => {
    setFormFields(prev => prev.filter(field => field.id !== fieldId));
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(formFields);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setFormFields(items);
  };

  const generateFormJSON = () => {
    return {
      title: formTitle,
      fields: formFields.map(({ id, ...field }) => field)
    };
  };

  const exportForm = () => {
    const formJSON = generateFormJSON();
    const blob = new Blob([JSON.stringify(formJSON, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${formTitle.replace(/\s+/g, '_').toLowerCase()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="form-builder">
      <div className="builder-header">
        <input
          value={formTitle}
          onChange={(e) => setFormTitle(e.target.value)}
          className="form-title-input"
        />
        <button onClick={exportForm}>Export Form</button>
      </div>

      <div className="builder-content">
        <div className="field-palette">
          <h3>Field Types</h3>
          {Object.entries(fieldTypes).map(([type, config]) => (
            <button
              key={type}
              onClick={() => addField(type)}
              className="field-type-button"
            >
              {config.icon} {config.label}
            </button>
          ))}
        </div>

        <div className="form-canvas">
          <h3>Form Preview</h3>
          {formFields.length === 0 ? (
            <div className="empty-canvas">
              <p>No fields added yet. Select a field type from the palette to get started.</p>
            </div>
          ) : (
            <DragDropContext onDragEnd={onDragEnd}>
              <Droppable droppableId="form-fields">
                {(provided) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className="form-fields-list"
                  >
                    {formFields.map((field, index) => (
                      <Draggable key={field.id} draggableId={field.id} index={index}>
                        {(provided) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className="draggable-field"
                          >
                            <FieldConfigurator
                              field={field}
                              onUpdate={(updatedField) => updateField(field.id, updatedField)}
                              onDelete={() => deleteField(field.id)}
                            />
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
          )}
        </div>

        <div className="form-preview">
          <h3>Live Preview</h3>
          <DynamicForm schema={generateFormJSON()} />
        </div>
      </div>
    </div>
  );
};
```

## 📱 Progressive Enhancement

### Responsive Dynamic Forms

```jsx
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';

const ResponsiveDynamicForm = ({ schema, breakpoints = { mobile: 768, tablet: 1024 } }) => {
  const [screenSize, setScreenSize] = useState('desktop');
  const [currentStep, setCurrentStep] = useState(0);
  const { register, handleSubmit, formState: { errors } } = useForm();

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width < breakpoints.mobile) {
        setScreenSize('mobile');
      } else if (width < breakpoints.tablet) {
        setScreenSize('tablet');
      } else {
        setScreenSize('desktop');
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoints]);

  const isMobile = screenSize === 'mobile';
  const sections = schema.sections || [];

  const nextStep = () => {
    if (currentStep < sections.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = (data) => {
    console.log('Responsive form data:', data);
  };

  // Mobile: Show one section at a time
  if (isMobile) {
    return (
      <div className="responsive-form mobile">
        <div className="mobile-header">
          <h2>{schema.title}</h2>
          <div className="progress">
            Step {currentStep + 1} of {sections.length}
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="mobile-section">
            <h3>{sections[currentStep]?.title}</h3>
            {sections[currentStep]?.fields.map((field, index) => (
              <DynamicField
                key={index}
                field={field}
                register={register}
                errors={errors}
              />
            ))}
          </div>

          <div className="mobile-navigation">
            {currentStep > 0 && (
              <button type="button" onClick={prevStep}>
                Previous
              </button>
            )}
            {currentStep < sections.length - 1 ? (
              <button type="button" onClick={nextStep}>
                Next
              </button>
            ) : (
              <button type="submit">Submit</button>
            )}
          </div>
        </form>
      </div>
    );
  }

  // Desktop/Tablet: Show all sections
  return (
    <div className={`responsive-form ${screenSize}`}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <h2>{schema.title}</h2>
        
        <div className="form-grid">
          {sections.map((section, sectionIndex) => (
            <div key={sectionIndex} className="form-section">
              <h3>{section.title}</h3>
              {section.fields.map((field, fieldIndex) => (
                <DynamicField
                  key={fieldIndex}
                  field={field}
                  register={register}
                  errors={errors}
                />
              ))}
            </div>
          ))}
        </div>
        
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

// Auto-save functionality
const useAutoSave = (formData, delay = 2000) => {
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);

  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (Object.keys(formData).length > 0) {
        setIsSaving(true);
        try {
          await saveFormData(formData);
          setLastSaved(new Date());
        } catch (error) {
          console.error('Auto-save failed:', error);
        } finally {
          setIsSaving(false);
        }
      }
    }, delay);

    return () => clearTimeout(timeoutId);
  }, [formData, delay]);

  return { isSaving, lastSaved };
};

const saveFormData = async (data) => {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(resolve, 500);
  });
};

// Form with auto-save
const AutoSaveForm = ({ schema }) => {
  const { register, handleSubmit, watch, formState: { errors } } = useForm();
  const watchedData = watch();
  const { isSaving, lastSaved } = useAutoSave(watchedData);

  const onSubmit = (data) => {
    console.log('Final form submission:', data);
  };

  return (
    <div className="auto-save-form">
      <div className="auto-save-status">
        {isSaving && <span>Saving...</span>}
        {lastSaved && !isSaving && (
          <span>Last saved: {lastSaved.toLocaleTimeString()}</span>
        )}
      </div>

      <ResponsiveDynamicForm schema={schema} />
    </div>
  );
};
```

## 📊 Best Practices Summary

### File Upload Best Practices

1. **Validation**
   - Validate file types and sizes on both client and server
   - Provide clear error messages for failed validations
   - Use progressive validation (client-side first, then server-side)

2. **User Experience**
   - Show upload progress for large files
   - Provide file previews when possible
   - Allow users to cancel uploads
   - Support drag and drop functionality

3. **Performance**
   - Implement chunked uploads for large files
   - Use compression when appropriate
   - Provide resumable uploads for reliability

4. **Security**
   - Validate file types on server-side
   - Scan uploaded files for malware
   - Store files securely with proper access controls

### Dynamic Forms Best Practices

1. **Schema Design**
   - Use clear, consistent field type definitions
   - Implement proper validation rules
   - Support conditional field rendering

2. **Performance**
   - Memoize expensive computations
   - Use virtual scrolling for large forms
   - Implement lazy loading for complex field types

3. **Accessibility**
   - Ensure proper labeling and ARIA attributes
   - Support keyboard navigation
   - Provide clear focus indicators

4. **Mobile Optimization**
   - Use responsive design patterns
   - Implement step-by-step navigation on mobile
   - Optimize touch interactions

This comprehensive guide provides the foundation for implementing advanced file upload and dynamic form features in modern React applications.
