# Complex Forms & Data Visualization Patterns

## Introduction to Complex Form Patterns

Complex forms go beyond simple input fields to include dynamic sections, conditional logic, multi-step workflows, and advanced validation. Combined with data visualization, they create powerful interfaces for data entry, analysis, and reporting.

### Key Challenges

1. **State Management**: Managing complex form state across multiple steps
2. **Validation**: Real-time validation with dependencies
3. **Performance**: Handling large forms without UI lag
4. **User Experience**: Intuitive navigation and error handling
5. **Data Integration**: Connecting forms with visualization components

## Dynamic Form Builder

```jsx
import React, { useState, useCallback, useMemo } from 'react'

const FormFieldTypes = {
  TEXT: 'text',
  EMAIL: 'email',
  NUMBER: 'number',
  SELECT: 'select',
  CHECKBOX: 'checkbox',
  RADIO: 'radio',
  DATE: 'date',
  FILE: 'file',
  TEXTAREA: 'textarea',
  CUSTOM: 'custom',
}

const DynamicFormBuilder = ({ schema, onSubmit, initialData = {} }) => {
  const [formData, setFormData] = useState(initialData)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})

  // Conditional field visibility
  const isFieldVisible = useCallback((field) => {
    if (!field.condition) return true
    
    const { dependsOn, value, operator = 'equals' } = field.condition
    const dependentValue = formData[dependsOn]
    
    switch (operator) {
      case 'equals':
        return dependentValue === value
      case 'notEquals':
        return dependentValue !== value
      case 'contains':
        return Array.isArray(dependentValue) && dependentValue.includes(value)
      case 'greaterThan':
        return Number(dependentValue) > Number(value)
      case 'lessThan':
        return Number(dependentValue) < Number(value)
      default:
        return true
    }
  }, [formData])

  // Field validation
  const validateField = useCallback((field, value) => {
    const errors = []
    
    if (field.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
      errors.push(`${field.label} is required`)
    }
    
    if (field.validation) {
      field.validation.forEach(rule => {
        switch (rule.type) {
          case 'minLength':
            if (value && value.length < rule.value) {
              errors.push(`${field.label} must be at least ${rule.value} characters`)
            }
            break
          case 'maxLength':
            if (value && value.length > rule.value) {
              errors.push(`${field.label} must be no more than ${rule.value} characters`)
            }
            break
          case 'pattern':
            if (value && !new RegExp(rule.value).test(value)) {
              errors.push(rule.message || `${field.label} format is invalid`)
            }
            break
          case 'custom':
            const customError = rule.validator(value, formData)
            if (customError) {
              errors.push(customError)
            }
            break
        }
      })
    }
    
    return errors
  }, [formData])

  const updateField = useCallback((fieldName, value) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }))
    
    // Clear errors when user starts typing
    if (errors[fieldName]) {
      setErrors(prev => ({ ...prev, [fieldName]: [] }))
    }
  }, [errors])

  const handleBlur = useCallback((field) => {
    setTouched(prev => ({ ...prev, [field.name]: true }))
    
    const fieldErrors = validateField(field, formData[field.name])
    setErrors(prev => ({ ...prev, [field.name]: fieldErrors }))
  }, [formData, validateField])

  const visibleFields = useMemo(() => 
    schema.fields.filter(isFieldVisible), 
    [schema.fields, isFieldVisible]
  )

  const renderField = (field) => {
    const value = formData[field.name] || ''
    const fieldErrors = errors[field.name] || []
    const isInvalid = touched[field.name] && fieldErrors.length > 0

    const commonProps = {
      id: field.name,
      name: field.name,
      value,
      onChange: (e) => updateField(field.name, e.target.value),
      onBlur: () => handleBlur(field),
      'aria-invalid': isInvalid,
      'aria-describedby': isInvalid ? `${field.name}-error` : undefined,
    }

    switch (field.type) {
      case FormFieldTypes.TEXT:
      case FormFieldTypes.EMAIL:
      case FormFieldTypes.NUMBER:
      case FormFieldTypes.DATE:
        return (
          <input
            type={field.type}
            placeholder={field.placeholder}
            {...commonProps}
            className={`form-input ${isInvalid ? 'error' : ''}`}
          />
        )

      case FormFieldTypes.TEXTAREA:
        return (
          <textarea
            rows={field.rows || 4}
            placeholder={field.placeholder}
            {...commonProps}
            className={`form-textarea ${isInvalid ? 'error' : ''}`}
          />
        )

      case FormFieldTypes.SELECT:
        return (
          <select {...commonProps} className={`form-select ${isInvalid ? 'error' : ''}`}>
            <option value="">{field.placeholder || 'Select an option'}</option>
            {field.options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        )

      case FormFieldTypes.RADIO:
        return (
          <div className="radio-group">
            {field.options.map(option => (
              <label key={option.value} className="radio-label">
                <input
                  type="radio"
                  name={field.name}
                  value={option.value}
                  checked={value === option.value}
                  onChange={(e) => updateField(field.name, e.target.value)}
                />
                {option.label}
              </label>
            ))}
          </div>
        )

      case FormFieldTypes.CHECKBOX:
        if (field.options) {
          // Multiple checkboxes
          return (
            <div className="checkbox-group">
              {field.options.map(option => (
                <label key={option.value} className="checkbox-label">
                  <input
                    type="checkbox"
                    value={option.value}
                    checked={Array.isArray(value) && value.includes(option.value)}
                    onChange={(e) => {
                      const currentValues = Array.isArray(value) ? value : []
                      const newValues = e.target.checked
                        ? [...currentValues, option.value]
                        : currentValues.filter(v => v !== option.value)
                      updateField(field.name, newValues)
                    }}
                  />
                  {option.label}
                </label>
              ))}
            </div>
          )
        } else {
          // Single checkbox
          return (
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={Boolean(value)}
                onChange={(e) => updateField(field.name, e.target.checked)}
              />
              {field.label}
            </label>
          )
        }

      case FormFieldTypes.FILE:
        return (
          <input
            type="file"
            accept={field.accept}
            multiple={field.multiple}
            onChange={(e) => updateField(field.name, e.target.files)}
            className={`form-file ${isInvalid ? 'error' : ''}`}
          />
        )

      case FormFieldTypes.CUSTOM:
        return field.component({
          value,
          onChange: (newValue) => updateField(field.name, newValue),
          field,
          formData,
        })

      default:
        return null
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validate all visible fields
    const newErrors = {}
    visibleFields.forEach(field => {
      const fieldErrors = validateField(field, formData[field.name])
      if (fieldErrors.length > 0) {
        newErrors[field.name] = fieldErrors
      }
    })
    
    setErrors(newErrors)
    setTouched(
      visibleFields.reduce((acc, field) => ({ ...acc, [field.name]: true }), {})
    )
    
    if (Object.keys(newErrors).length === 0) {
      onSubmit(formData)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="dynamic-form">
      <h2>{schema.title}</h2>
      {schema.description && <p>{schema.description}</p>}
      
      {visibleFields.map(field => (
        <div key={field.name} className="form-group">
          <label htmlFor={field.name} className="form-label">
            {field.label}
            {field.required && <span className="required">*</span>}
          </label>
          
          {renderField(field)}
          
          {field.helpText && (
            <div className="help-text">{field.helpText}</div>
          )}
          
          {touched[field.name] && errors[field.name] && errors[field.name].length > 0 && (
            <div id={`${field.name}-error`} className="error-message" role="alert">
              {errors[field.name].join(', ')}
            </div>
          )}
        </div>
      ))}
      
      <button type="submit" className="submit-button">
        {schema.submitText || 'Submit'}
      </button>
    </form>
  )
}

// Example schema
const exampleSchema = {
  title: 'Dynamic Survey Form',
  description: 'Please fill out all required fields',
  submitText: 'Submit Survey',
  fields: [
    {
      name: 'name',
      type: FormFieldTypes.TEXT,
      label: 'Full Name',
      required: true,
      validation: [
        { type: 'minLength', value: 2 }
      ]
    },
    {
      name: 'email',
      type: FormFieldTypes.EMAIL,
      label: 'Email Address',
      required: true,
      validation: [
        {
          type: 'pattern',
          value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
          message: 'Please enter a valid email address'
        }
      ]
    },
    {
      name: 'hasExperience',
      type: FormFieldTypes.RADIO,
      label: 'Do you have prior experience?',
      required: true,
      options: [
        { label: 'Yes', value: 'yes' },
        { label: 'No', value: 'no' }
      ]
    },
    {
      name: 'yearsExperience',
      type: FormFieldTypes.NUMBER,
      label: 'Years of Experience',
      required: true,
      condition: {
        dependsOn: 'hasExperience',
        value: 'yes'
      },
      validation: [
        { type: 'custom', validator: (value) => value < 0 ? 'Experience cannot be negative' : null }
      ]
    }
  ]
}
```

## Multi-Step Form with Progress

```jsx
const MultiStepForm = ({ steps, onComplete, initialData = {} }) => {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState(initialData)
  const [stepData, setStepData] = useState({})
  const [completedSteps, setCompletedSteps] = useState(new Set())

  const totalSteps = steps.length
  const progress = ((currentStep + 1) / totalSteps) * 100

  const updateStepData = (stepIndex, data) => {
    setStepData(prev => ({ ...prev, [stepIndex]: data }))
    setFormData(prev => ({ ...prev, ...data }))
  }

  const validateStep = async (stepIndex) => {
    const step = steps[stepIndex]
    if (step.validate) {
      return await step.validate(stepData[stepIndex] || {}, formData)
    }
    return true
  }

  const goToNext = async () => {
    const isValid = await validateStep(currentStep)
    if (isValid) {
      setCompletedSteps(prev => new Set([...prev, currentStep]))
      if (currentStep < totalSteps - 1) {
        setCurrentStep(currentStep + 1)
      } else {
        onComplete(formData)
      }
    }
  }

  const goToPrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const goToStep = (stepIndex) => {
    if (stepIndex <= Math.max(...completedSteps) + 1) {
      setCurrentStep(stepIndex)
    }
  }

  const currentStepComponent = steps[currentStep]

  return (
    <div className="multi-step-form">
      {/* Progress Bar */}
      <div className="progress-container">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="step-indicators">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`step-indicator ${
                index === currentStep ? 'current' : 
                completedSteps.has(index) ? 'completed' : 
                'pending'
              }`}
              onClick={() => goToStep(index)}
            >
              <span className="step-number">{index + 1}</span>
              <span className="step-title">{step.title}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Content */}
      <div className="step-content">
        <h2>{currentStepComponent.title}</h2>
        {currentStepComponent.description && (
          <p>{currentStepComponent.description}</p>
        )}
        
        <currentStepComponent.component
          data={stepData[currentStep] || {}}
          onChange={(data) => updateStepData(currentStep, data)}
          formData={formData}
        />
      </div>

      {/* Navigation */}
      <div className="step-navigation">
        <button
          type="button"
          onClick={goToPrevious}
          disabled={currentStep === 0}
          className="btn btn-secondary"
        >
          Previous
        </button>
        
        <button
          type="button"
          onClick={goToNext}
          className="btn btn-primary"
        >
          {currentStep === totalSteps - 1 ? 'Complete' : 'Next'}
        </button>
      </div>
    </div>
  )
}

// Example step components
const PersonalInfoStep = ({ data, onChange }) => {
  const updateField = (field, value) => {
    onChange({ ...data, [field]: value })
  }

  return (
    <div>
      <input
        type="text"
        placeholder="First Name"
        value={data.firstName || ''}
        onChange={(e) => updateField('firstName', e.target.value)}
      />
      <input
        type="text"
        placeholder="Last Name"
        value={data.lastName || ''}
        onChange={(e) => updateField('lastName', e.target.value)}
      />
    </div>
  )
}

const ContactInfoStep = ({ data, onChange }) => {
  const updateField = (field, value) => {
    onChange({ ...data, [field]: value })
  }

  return (
    <div>
      <input
        type="email"
        placeholder="Email"
        value={data.email || ''}
        onChange={(e) => updateField('email', e.target.value)}
      />
      <input
        type="tel"
        placeholder="Phone"
        value={data.phone || ''}
        onChange={(e) => updateField('phone', e.target.value)}
      />
    </div>
  )
}

const multiStepConfig = [
  {
    title: 'Personal Information',
    description: 'Tell us about yourself',
    component: PersonalInfoStep,
    validate: (data) => {
      return data.firstName && data.lastName
    }
  },
  {
    title: 'Contact Information',
    description: 'How can we reach you?',
    component: ContactInfoStep,
    validate: (data) => {
      return data.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)
    }
  }
]
```

## Data Visualization Integration

```jsx
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer 
} from 'recharts'

const FormWithVisualization = () => {
  const [formData, setFormData] = useState({
    category: '',
    values: [],
    dateRange: { start: '', end: '' }
  })
  const [visualizationData, setVisualizationData] = useState([])
  const [chartType, setChartType] = useState('bar')

  // Process form data for visualization
  const processDataForVisualization = useCallback((data) => {
    // Transform form data into chart-ready format
    return data.values.map((value, index) => ({
      name: `Item ${index + 1}`,
      value: Number(value),
      category: data.category
    }))
  }, [])

  useEffect(() => {
    if (formData.values.length > 0) {
      setVisualizationData(processDataForVisualization(formData))
    }
  }, [formData, processDataForVisualization])

  const addValue = () => {
    setFormData(prev => ({
      ...prev,
      values: [...prev.values, '']
    }))
  }

  const updateValue = (index, value) => {
    setFormData(prev => ({
      ...prev,
      values: prev.values.map((v, i) => i === index ? value : v)
    }))
  }

  const removeValue = (index) => {
    setFormData(prev => ({
      ...prev,
      values: prev.values.filter((_, i) => i !== index)
    }))
  }

  const renderChart = () => {
    if (visualizationData.length === 0) return null

    const commonProps = {
      width: '100%',
      height: 300,
      data: visualizationData
    }

    switch (chartType) {
      case 'bar':
        return (
          <ResponsiveContainer {...commonProps}>
            <BarChart data={visualizationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'line':
        return (
          <ResponsiveContainer {...commonProps}>
            <LineChart data={visualizationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer {...commonProps}>
            <PieChart>
              <Pie
                data={visualizationData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {visualizationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={`hsl(${index * 45}, 70%, 50%)`} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )

      default:
        return null
    }
  }

  return (
    <div className="form-with-visualization">
      <div className="form-section">
        <h2>Data Entry Form</h2>
        
        <div className="form-group">
          <label>Category:</label>
          <select
            value={formData.category}
            onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
          >
            <option value="">Select Category</option>
            <option value="sales">Sales</option>
            <option value="marketing">Marketing</option>
            <option value="development">Development</option>
          </select>
        </div>

        <div className="form-group">
          <label>Values:</label>
          {formData.values.map((value, index) => (
            <div key={index} className="value-input-group">
              <input
                type="number"
                value={value}
                onChange={(e) => updateValue(index, e.target.value)}
                placeholder="Enter value"
              />
              <button type="button" onClick={() => removeValue(index)}>
                Remove
              </button>
            </div>
          ))}
          <button type="button" onClick={addValue}>
            Add Value
          </button>
        </div>

        <div className="form-group">
          <label>Chart Type:</label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
          >
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
            <option value="pie">Pie Chart</option>
          </select>
        </div>
      </div>

      <div className="visualization-section">
        <h2>Live Preview</h2>
        {renderChart()}
        
        {visualizationData.length === 0 && (
          <div className="empty-state">
            Add some values to see the visualization
          </div>
        )}
      </div>
    </div>
  )
}
```

## Real-time Data Form

```jsx
const RealTimeDataForm = () => {
  const [metrics, setMetrics] = useState({
    cpu: 0,
    memory: 0,
    network: 0,
    storage: 0
  })
  const [alerts, setAlerts] = useState([])
  const [thresholds, setThresholds] = useState({
    cpu: 80,
    memory: 85,
    network: 70,
    storage: 90
  })
  const [historicalData, setHistoricalData] = useState([])

  // Simulate real-time data
  useEffect(() => {
    const interval = setInterval(() => {
      const newMetrics = {
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        network: Math.random() * 100,
        storage: Math.random() * 100
      }

      setMetrics(newMetrics)

      // Add to historical data
      setHistoricalData(prev => {
        const newData = {
          timestamp: new Date(),
          ...newMetrics
        }
        return [...prev.slice(-19), newData] // Keep last 20 data points
      })

      // Check for alerts
      Object.entries(newMetrics).forEach(([key, value]) => {
        if (value > thresholds[key]) {
          setAlerts(prev => [...prev, {
            id: Date.now() + Math.random(),
            type: 'warning',
            message: `${key.toUpperCase()} usage is above threshold: ${value.toFixed(1)}%`,
            timestamp: new Date()
          }])
        }
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [thresholds])

  // Clear old alerts
  useEffect(() => {
    const interval = setInterval(() => {
      setAlerts(prev => prev.filter(alert => 
        Date.now() - alert.timestamp.getTime() < 10000 // Keep for 10 seconds
      ))
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const updateThreshold = (metric, value) => {
    setThresholds(prev => ({ ...prev, [metric]: Number(value) }))
  }

  const MetricGauge = ({ label, value, threshold, color }) => {
    const percentage = Math.min(value, 100)
    const isAlert = value > threshold

    return (
      <div className={`metric-gauge ${isAlert ? 'alert' : ''}`}>
        <div className="gauge-header">
          <span className="metric-label">{label}</span>
          <span className="metric-value">{value.toFixed(1)}%</span>
        </div>
        <div className="gauge-bar">
          <div 
            className="gauge-fill"
            style={{ 
              width: `${percentage}%`,
              backgroundColor: isAlert ? '#e74c3c' : color
            }}
          />
          <div 
            className="threshold-marker"
            style={{ left: `${threshold}%` }}
          />
        </div>
        <div className="threshold-control">
          <label>Threshold:</label>
          <input
            type="range"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => updateThreshold(label.toLowerCase(), e.target.value)}
          />
          <span>{threshold}%</span>
        </div>
      </div>
    )
  }

  return (
    <div className="real-time-dashboard">
      <div className="metrics-grid">
        <MetricGauge 
          label="CPU" 
          value={metrics.cpu} 
          threshold={thresholds.cpu}
          color="#3498db"
        />
        <MetricGauge 
          label="Memory" 
          value={metrics.memory} 
          threshold={thresholds.memory}
          color="#2ecc71"
        />
        <MetricGauge 
          label="Network" 
          value={metrics.network} 
          threshold={thresholds.network}
          color="#f39c12"
        />
        <MetricGauge 
          label="Storage" 
          value={metrics.storage} 
          threshold={thresholds.storage}
          color="#9b59b6"
        />
      </div>

      <div className="historical-chart">
        <h3>Historical Data</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={historicalData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={(time) => new Date(time).toLocaleTimeString()}
            />
            <YAxis domain={[0, 100]} />
            <Tooltip 
              labelFormatter={(time) => new Date(time).toLocaleString()}
            />
            <Legend />
            <Line type="monotone" dataKey="cpu" stroke="#3498db" name="CPU %" />
            <Line type="monotone" dataKey="memory" stroke="#2ecc71" name="Memory %" />
            <Line type="monotone" dataKey="network" stroke="#f39c12" name="Network %" />
            <Line type="monotone" dataKey="storage" stroke="#9b59b6" name="Storage %" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="alerts-panel">
        <h3>Active Alerts</h3>
        {alerts.length === 0 ? (
          <div className="no-alerts">No active alerts</div>
        ) : (
          <div className="alerts-list">
            {alerts.map(alert => (
              <div key={alert.id} className={`alert alert-${alert.type}`}>
                <span className="alert-message">{alert.message}</span>
                <span className="alert-time">
                  {alert.timestamp.toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

## Form Analytics Dashboard

```jsx
const FormAnalyticsDashboard = ({ formSubmissions }) => {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
    end: new Date()
  })
  const [selectedMetric, setSelectedMetric] = useState('submissions')

  // Process analytics data
  const analyticsData = useMemo(() => {
    const filtered = formSubmissions.filter(submission => {
      const date = new Date(submission.timestamp)
      return date >= dateRange.start && date <= dateRange.end
    })

    // Group by date
    const groupedByDate = filtered.reduce((acc, submission) => {
      const date = new Date(submission.timestamp).toDateString()
      if (!acc[date]) {
        acc[date] = []
      }
      acc[date].push(submission)
      return acc
    }, {})

    // Calculate metrics
    return Object.entries(groupedByDate).map(([date, submissions]) => ({
      date,
      submissions: submissions.length,
      completionRate: submissions.filter(s => s.completed).length / submissions.length * 100,
      averageTime: submissions.reduce((sum, s) => sum + s.timeSpent, 0) / submissions.length,
      dropoffRate: submissions.filter(s => !s.completed).length / submissions.length * 100
    }))
  }, [formSubmissions, dateRange])

  const summaryStats = useMemo(() => {
    const total = formSubmissions.length
    const completed = formSubmissions.filter(s => s.completed).length
    const avgTime = formSubmissions.reduce((sum, s) => sum + s.timeSpent, 0) / total

    return {
      totalSubmissions: total,
      completionRate: (completed / total * 100).toFixed(1),
      averageTime: (avgTime / 1000 / 60).toFixed(1), // Convert to minutes
      dropoffRate: ((total - completed) / total * 100).toFixed(1)
    }
  }, [formSubmissions])

  const fieldAnalytics = useMemo(() => {
    const fieldErrors = {}
    const fieldTimes = {}

    formSubmissions.forEach(submission => {
      submission.fieldData?.forEach(field => {
        if (!fieldErrors[field.name]) {
          fieldErrors[field.name] = 0
          fieldTimes[field.name] = []
        }
        if (field.hasError) {
          fieldErrors[field.name]++
        }
        fieldTimes[field.name].push(field.timeSpent)
      })
    })

    return Object.keys(fieldErrors).map(fieldName => ({
      field: fieldName,
      errorRate: (fieldErrors[fieldName] / formSubmissions.length * 100).toFixed(1),
      avgTime: (fieldTimes[fieldName].reduce((sum, time) => sum + time, 0) / fieldTimes[fieldName].length / 1000).toFixed(1)
    }))
  }, [formSubmissions])

  return (
    <div className="form-analytics-dashboard">
      <div className="dashboard-header">
        <h2>Form Analytics Dashboard</h2>
        <div className="date-range-picker">
          <input
            type="date"
            value={dateRange.start.toISOString().split('T')[0]}
            onChange={(e) => setDateRange(prev => ({ ...prev, start: new Date(e.target.value) }))}
          />
          <span>to</span>
          <input
            type="date"
            value={dateRange.end.toISOString().split('T')[0]}
            onChange={(e) => setDateRange(prev => ({ ...prev, end: new Date(e.target.value) }))}
          />
        </div>
      </div>

      <div className="summary-cards">
        <div className="summary-card">
          <h3>Total Submissions</h3>
          <div className="metric-value">{summaryStats.totalSubmissions}</div>
        </div>
        <div className="summary-card">
          <h3>Completion Rate</h3>
          <div className="metric-value">{summaryStats.completionRate}%</div>
        </div>
        <div className="summary-card">
          <h3>Average Time</h3>
          <div className="metric-value">{summaryStats.averageTime} min</div>
        </div>
        <div className="summary-card">
          <h3>Dropoff Rate</h3>
          <div className="metric-value">{summaryStats.dropoffRate}%</div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-controls">
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
          >
            <option value="submissions">Submissions</option>
            <option value="completionRate">Completion Rate</option>
            <option value="averageTime">Average Time</option>
            <option value="dropoffRate">Dropoff Rate</option>
          </select>
        </div>

        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={analyticsData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey={selectedMetric} 
              stroke="#8884d8" 
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="field-analytics">
        <h3>Field Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={fieldAnalytics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="field" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="errorRate" fill="#e74c3c" name="Error Rate %" />
            <Bar dataKey="avgTime" fill="#3498db" name="Avg Time (s)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
```

## Performance Optimization

```jsx
// Optimized form field component
const OptimizedFormField = React.memo(({ 
  field, 
  value, 
  onChange, 
  onBlur, 
  error 
}) => {
  const debouncedOnChange = useMemo(
    () => debounce(onChange, 300),
    [onChange]
  )

  useEffect(() => {
    return () => {
      debouncedOnChange.cancel()
    }
  }, [debouncedOnChange])

  return (
    <div className="form-field">
      <input
        type={field.type}
        value={value}
        onChange={(e) => debouncedOnChange(e.target.value)}
        onBlur={onBlur}
        placeholder={field.placeholder}
      />
      {error && <div className="error">{error}</div>}
    </div>
  )
}, (prevProps, nextProps) => {
  return (
    prevProps.value === nextProps.value &&
    prevProps.error === nextProps.error &&
    prevProps.field === nextProps.field
  )
})

// Virtual scrolling for large forms
const VirtualizedFormFields = ({ fields, formData, onChange }) => {
  const [visibleFields, setVisibleFields] = useState([])
  const containerRef = useRef()

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter(entry => entry.isIntersecting)
          .map(entry => entry.target.dataset.fieldIndex)
        setVisibleFields(visible)
      },
      { rootMargin: '100px' }
    )

    const fieldElements = containerRef.current?.querySelectorAll('[data-field-index]')
    fieldElements?.forEach(el => observer.observe(el))

    return () => observer.disconnect()
  }, [fields])

  return (
    <div ref={containerRef} className="virtualized-form">
      {fields.map((field, index) => (
        <div key={field.name} data-field-index={index}>
          {visibleFields.includes(index.toString()) ? (
            <OptimizedFormField
              field={field}
              value={formData[field.name]}
              onChange={(value) => onChange(field.name, value)}
            />
          ) : (
            <div style={{ height: '60px' }} /> // Placeholder
          )}
        </div>
      ))}
    </div>
  )
}
```

## Accessibility Features

```jsx
const AccessibleComplexForm = ({ schema, onSubmit }) => {
  const [currentSection, setCurrentSection] = useState(0)
  const [announcements, setAnnouncements] = useState([])
  const announcementRef = useRef()

  const announce = (message) => {
    setAnnouncements(prev => [...prev, { id: Date.now(), message }])
    setTimeout(() => {
      setAnnouncements(prev => prev.slice(1))
    }, 5000)
  }

  const handleSectionChange = (newSection) => {
    setCurrentSection(newSection)
    announce(`Now viewing section ${newSection + 1}: ${schema.sections[newSection].title}`)
  }

  const handleFieldError = (fieldName, error) => {
    announce(`Error in ${fieldName}: ${error}`)
  }

  return (
    <div className="accessible-form">
      {/* Screen reader announcements */}
      <div
        ref={announcementRef}
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {announcements.map(announcement => (
          <div key={announcement.id}>{announcement.message}</div>
        ))}
      </div>

      {/* Skip navigation */}
      <a href="#form-content" className="skip-link">
        Skip to form content
      </a>

      {/* Form navigation */}
      <nav aria-label="Form sections" className="form-navigation">
        <ol>
          {schema.sections.map((section, index) => (
            <li key={index}>
              <button
                type="button"
                onClick={() => handleSectionChange(index)}
                aria-current={currentSection === index ? 'step' : undefined}
                className={currentSection === index ? 'current' : ''}
              >
                {section.title}
              </button>
            </li>
          ))}
        </ol>
      </nav>

      {/* Form content */}
      <main id="form-content" className="form-content">
        <h1>{schema.title}</h1>
        
        {/* Progress indicator */}
        <div className="progress-indicator" role="progressbar" 
             aria-valuenow={currentSection + 1} 
             aria-valuemin="1" 
             aria-valuemax={schema.sections.length}>
          <span className="sr-only">
            Step {currentSection + 1} of {schema.sections.length}
          </span>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${((currentSection + 1) / schema.sections.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Current section */}
        <section aria-labelledby={`section-${currentSection}-title`}>
          <h2 id={`section-${currentSection}-title`}>
            {schema.sections[currentSection].title}
          </h2>
          
          {/* Section fields */}
          <fieldset>
            <legend className="sr-only">
              {schema.sections[currentSection].title} fields
            </legend>
            
            {/* Form fields would go here */}
          </fieldset>
        </section>
      </main>
    </div>
  )
}
```

## Testing Complex Forms

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('Dynamic Form Builder', () => {
  const mockSchema = {
    title: 'Test Form',
    fields: [
      {
        name: 'email',
        type: 'email',
        label: 'Email',
        required: true,
        validation: [
          {
            type: 'pattern',
            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Invalid email format'
          }
        ]
      }
    ]
  }

  test('validates required fields', async () => {
    const user = userEvent.setup()
    const mockSubmit = jest.fn()

    render(
      <DynamicFormBuilder
        schema={mockSchema}
        onSubmit={mockSubmit}
      />
    )

    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })

    expect(mockSubmit).not.toHaveBeenCalled()
  })

  test('validates email format', async () => {
    const user = userEvent.setup()
    const mockSubmit = jest.fn()

    render(
      <DynamicFormBuilder
        schema={mockSchema}
        onSubmit={mockSubmit}
      />
    )

    const emailInput = screen.getByLabelText(/email/i)
    await user.type(emailInput, 'invalid-email')
    await user.tab() // Trigger blur

    await waitFor(() => {
      expect(screen.getByText(/invalid email format/i)).toBeInTheDocument()
    })
  })

  test('submits valid form data', async () => {
    const user = userEvent.setup()
    const mockSubmit = jest.fn()

    render(
      <DynamicFormBuilder
        schema={mockSchema}
        onSubmit={mockSubmit}
      />
    )

    const emailInput = screen.getByLabelText(/email/i)
    await user.type(emailInput, 'test@example.com')

    const submitButton = screen.getByRole('button', { name: /submit/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        email: 'test@example.com'
      })
    })
  })
})

describe('Multi-Step Form', () => {
  test('navigates between steps', async () => {
    const user = userEvent.setup()
    const mockSteps = [
      { title: 'Step 1', component: () => <div>Step 1 Content</div> },
      { title: 'Step 2', component: () => <div>Step 2 Content</div> }
    ]

    render(
      <MultiStepForm steps={mockSteps} onComplete={jest.fn()} />
    )

    expect(screen.getByText('Step 1 Content')).toBeInTheDocument()

    const nextButton = screen.getByRole('button', { name: /next/i })
    await user.click(nextButton)

    expect(screen.getByText('Step 2 Content')).toBeInTheDocument()
  })
})
```

## Conclusion

Complex forms and data visualization patterns require careful consideration of:

**Form Architecture:**
- Dynamic field generation and conditional logic
- Multi-step workflows with validation
- Real-time data integration and processing
- Performance optimization for large forms

**Visualization Integration:**
- Live data binding between forms and charts
- Real-time updates and monitoring
- Interactive dashboards and analytics
- Responsive design for different screen sizes

**Best Practices:**
- Implement comprehensive validation and error handling
- Optimize performance with virtualization and memoization
- Ensure accessibility with proper ARIA attributes and navigation
- Provide thorough testing coverage for complex interactions
- Design intuitive user experiences with clear progress indicators

These patterns enable the creation of sophisticated applications that combine powerful data entry capabilities with meaningful visualization, providing users with immediate feedback and insights into their data.