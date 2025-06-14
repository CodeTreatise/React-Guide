# 📊 Project 6: Personal Dashboard - Implementation Guide

> **Level**: Beginner (Week 6)  
> **Prerequisites**: Projects 1-5 completed  
> **Focus**: Integration of all React fundamentals in a comprehensive dashboard application  
> **Estimated Time**: 15-20 hours

---

## 🎯 Project Overview

Build a comprehensive Personal Dashboard that combines all concepts learned from the previous 5 projects. This capstone project integrates portfolio display, interactive counters, weather information, todo management, and contact forms into a unified dashboard experience.

### Skills Integration
- ✅ **Component Architecture** (from Portfolio)
- ✅ **State Management** (from Counter & Todo)
- ✅ **API Integration** (from Weather)
- ✅ **Form Handling** (from Contact Form)
- ✅ **Event Handling** (from all projects)
- ✅ **Conditional Rendering** (from all projects)
- ✅ **Props Management** (from all projects)

---

## 🚀 Quick Start (30 minutes)

### Step 1: Project Setup
```bash
# Create React app
npx create-react-app personal-dashboard
cd personal-dashboard

# Install additional dependencies
npm install lucide-react date-fns

# Start development server
npm start
```

### Step 2: Basic Dashboard Structure
```jsx
// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

// Import all dashboard components
import DashboardHeader from './components/DashboardHeader';
import QuickStats from './components/QuickStats';
import WeatherWidget from './components/WeatherWidget';
import TodoWidget from './components/TodoWidget';
import ContactWidget from './components/ContactWidget';
import PortfolioWidget from './components/PortfolioWidget';

function App() {
  const [user, setUser] = useState({
    name: 'Your Name',
    avatar: 'https://via.placeholder.com/50'
  });

  const [dashboardData, setDashboardData] = useState({
    todos: [],
    weather: null,
    contacts: [],
    stats: {
      completedTodos: 0,
      totalProjects: 6,
      unreadMessages: 0
    }
  });

  return (
    <div className="dashboard">
      <DashboardHeader user={user} />
      <div className="dashboard-grid">
        <QuickStats stats={dashboardData.stats} />
        <WeatherWidget />
        <TodoWidget />
        <ContactWidget />
        <PortfolioWidget />
      </div>
    </div>
  );
}

export default App;
```

### Step 3: Basic Styling
```css
/* src/App.css */
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.dashboard-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.widget {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.widget:hover {
  transform: translateY(-2px);
}
```

---

## 📋 Features to Implement

### Core Dashboard Features
- [x] **Dashboard Header** - User info, current time, navigation
- [x] **Quick Statistics** - Overview cards with key metrics
- [x] **Weather Widget** - Current weather and 5-day forecast
- [x] **Todo Management** - Add, edit, delete, and filter todos
- [x] **Contact Manager** - Store and manage contact information
- [x] **Portfolio Showcase** - Display your projects with links
- [x] **Responsive Design** - Works on desktop, tablet, and mobile
- [x] **Data Persistence** - Save data to localStorage

### Advanced Features
- [x] **Dark/Light Theme Toggle**
- [x] **Widget Customization** - Show/hide widgets
- [x] **Data Export/Import** - Backup and restore data
- [x] **Notification System** - Success/error messages
- [x] **Search Functionality** - Search across todos and contacts
- [x] **Analytics** - Track productivity metrics

---

## 🏗️ Project Structure

```
personal-dashboard/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   │   ├── DashboardHeader.jsx
│   │   │   ├── QuickStats.jsx
│   │   │   └── DashboardSettings.jsx
│   │   ├── Widgets/
│   │   │   ├── WeatherWidget.jsx
│   │   │   ├── TodoWidget.jsx
│   │   │   ├── ContactWidget.jsx
│   │   │   └── PortfolioWidget.jsx
│   │   ├── UI/
│   │   │   ├── Card.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── Modal.jsx
│   │   │   └── NotificationToast.jsx
│   │   └── Forms/
│   │       ├── TodoForm.jsx
│   │       ├── ContactForm.jsx
│   │       └── SettingsForm.jsx
│   ├── hooks/
│   │   ├── useLocalStorage.js
│   │   ├── useWeather.js
│   │   ├── useTodos.js
│   │   └── useNotifications.js
│   ├── utils/
│   │   ├── dateHelpers.js
│   │   ├── storageHelpers.js
│   │   └── validationHelpers.js
│   ├── contexts/
│   │   ├── ThemeContext.js
│   │   └── DashboardContext.js
│   ├── App.js
│   ├── App.css
│   └── index.js
└── package.json
```

---

## 🎨 Component Implementation

### 1. Dashboard Header Component
```jsx
{% raw %}
// src/components/Dashboard/DashboardHeader.jsx
import React, { useState, useEffect } from 'react';
import { Sun, Moon, Settings, User } from 'lucide-react';
import { format } from 'date-fns';

const DashboardHeader = ({ user, onThemeToggle, isDarkMode }) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <header className="dashboard-header">
      <div className="header-left">
        <div className="user-info">
          <img src={user.avatar} alt="User Avatar" className="user-avatar" />
          <div>
            <h1>Welcome back, {user.name}!</h1>
            <p className="current-time">
              {format(currentTime, 'EEEE, MMMM d, yyyy - HH:mm:ss')}
            </p>
          </div>
        </div>
      </div>
      
      <div className="header-right">
        <button
          className="theme-toggle"
          onClick={onThemeToggle}
          title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        
        <button className="settings-btn" title="Dashboard Settings">
          <Settings size={20} />
        </button>
      </div>
    </header>
  );
};

export default DashboardHeader;
{% endraw %}
```

### 2. Quick Statistics Widget
```jsx
{% raw %}
// src/components/Dashboard/QuickStats.jsx
import React from 'react';
import { CheckCircle, Briefcase, MessageCircle, TrendingUp } from 'lucide-react';

const QuickStats = ({ stats }) => {
  const statItems = [
    {
      icon: <CheckCircle size={24} />,
      label: 'Completed Todos',
      value: stats.completedTodos,
      color: '#10b981'
    },
    {
      icon: <Briefcase size={24} />,
      label: 'Active Projects',
      value: stats.totalProjects,
      color: '#3b82f6'
    },
    {
      icon: <MessageCircle size={24} />,
      label: 'New Messages',
      value: stats.unreadMessages,
      color: '#f59e0b'
    },
    {
      icon: <TrendingUp size={24} />,
      label: 'Productivity',
      value: `${stats.productivity}%`,
      color: '#8b5cf6'
    }
  ];

  return (
    <div className="widget quick-stats">
      <h3 className="widget-title">Quick Overview</h3>
      <div className="stats-grid">
        {statItems.map((item, index) => (
          <div key={index} className="stat-item">
            <div 
              className="stat-icon"
              style={{ color: item.color }}
            >
              {item.icon}
            </div>
            <div className="stat-content">
              <div className="stat-value">{item.value}</div>
              <div className="stat-label">{item.label}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuickStats;
{% endraw %}
```

### 3. Weather Widget (Enhanced from Project 3)
```jsx
// src/components/Widgets/WeatherWidget.jsx
import React, { useState, useEffect } from 'react';
import { Cloud, Sun, CloudRain, MapPin, Thermometer } from 'lucide-react';

const WeatherWidget = () => {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWeatherData();
  }, []);

  const fetchWeatherData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get user's location
      const position = await getCurrentPosition();
      const { latitude, longitude } = position.coords;

      // Fetch current weather and forecast
      const [currentWeather, weatherForecast] = await Promise.all([
        fetchCurrentWeather(latitude, longitude),
        fetchWeatherForecast(latitude, longitude)
      ]);

      setWeather(currentWeather);
      setForecast(weatherForecast);
    } catch (err) {
      setError('Failed to fetch weather data');
      console.error('Weather fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentPosition = () => {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject);
    });
  };

  const fetchCurrentWeather = async (lat, lon) => {
    // Mock API call - replace with actual weather API
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          location: 'New York, NY',
          temperature: 22,
          condition: 'Partly Cloudy',
          humidity: 65,
          windSpeed: 12,
          icon: 'partly-cloudy'
        });
      }, 1000);
    });
  };

  const fetchWeatherForecast = async (lat, lon) => {
    // Mock forecast data
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { day: 'Today', high: 24, low: 18, condition: 'Sunny' },
          { day: 'Tomorrow', high: 26, low: 20, condition: 'Cloudy' },
          { day: 'Wed', high: 23, low: 17, condition: 'Rainy' },
          { day: 'Thu', high: 25, low: 19, condition: 'Sunny' },
          { day: 'Fri', high: 22, low: 16, condition: 'Partly Cloudy' }
        ]);
      }, 1000);
    });
  };

  const getWeatherIcon = (condition) => {
    switch (condition.toLowerCase()) {
      case 'sunny':
        return <Sun size={32} color="#f59e0b" />;
      case 'cloudy':
      case 'partly cloudy':
        return <Cloud size={32} color="#6b7280" />;
      case 'rainy':
        return <CloudRain size={32} color="#3b82f6" />;
      default:
        return <Sun size={32} color="#f59e0b" />;
    }
  };

  if (loading) {
    return (
      <div className="widget weather-widget">
        <h3 className="widget-title">Weather</h3>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading weather data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="widget weather-widget">
        <h3 className="widget-title">Weather</h3>
        <div className="error-state">
          <p>{error}</p>
          <button onClick={fetchWeatherData} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="widget weather-widget">
      <h3 className="widget-title">Weather</h3>
      
      {weather && (
        <div className="current-weather">
          <div className="weather-main">
            <div className="weather-icon">
              {getWeatherIcon(weather.condition)}
            </div>
            <div className="weather-info">
              <div className="temperature">
                {weather.temperature}°C
              </div>
              <div className="condition">{weather.condition}</div>
              <div className="location">
                <MapPin size={14} />
                {weather.location}
              </div>
            </div>
          </div>
          
          <div className="weather-details">
            <div className="detail-item">
              <span>Humidity</span>
              <span>{weather.humidity}%</span>
            </div>
            <div className="detail-item">
              <span>Wind</span>
              <span>{weather.windSpeed} km/h</span>
            </div>
          </div>
        </div>
      )}

      {forecast.length > 0 && (
        <div className="weather-forecast">
          <h4>5-Day Forecast</h4>
          <div className="forecast-list">
            {forecast.map((day, index) => (
              <div key={index} className="forecast-item">
                <div className="forecast-day">{day.day}</div>
                <div className="forecast-icon">
                  {getWeatherIcon(day.condition)}
                </div>
                <div className="forecast-temps">
                  <span className="high">{day.high}°</span>
                  <span className="low">{day.low}°</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WeatherWidget;
```

### 4. Todo Widget (Enhanced from Project 4)
```jsx
{% raw %}
// src/components/Widgets/TodoWidget.jsx
import React, { useState, useEffect } from 'react';
import { Plus, Check, Trash2, Edit3, Filter } from 'lucide-react';

const TodoWidget = ({ onStatsUpdate }) => {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState('');
  const [filter, setFilter] = useState('all');
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  useEffect(() => {
    // Load todos from localStorage
    const savedTodos = localStorage.getItem('dashboard-todos');
    if (savedTodos) {
      setTodos(JSON.parse(savedTodos));
    }
  }, []);

  useEffect(() => {
    // Save todos to localStorage
    localStorage.setItem('dashboard-todos', JSON.stringify(todos));
    
    // Update dashboard stats
    const completedCount = todos.filter(todo => todo.completed).length;
    onStatsUpdate && onStatsUpdate({ completedTodos: completedCount });
  }, [todos, onStatsUpdate]);

  const addTodo = (e) => {
    e.preventDefault();
    if (newTodo.trim()) {
      const todo = {
        id: Date.now(),
        text: newTodo.trim(),
        completed: false,
        createdAt: new Date().toISOString(),
        priority: 'medium'
      };
      setTodos([todo, ...todos]);
      setNewTodo('');
    }
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  const startEditing = (id, text) => {
    setEditingId(id);
    setEditText(text);
  };

  const saveEdit = () => {
    setTodos(todos.map(todo =>
      todo.id === editingId ? { ...todo, text: editText } : todo
    ));
    setEditingId(null);
    setEditText('');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditText('');
  };

  const filteredTodos = todos.filter(todo => {
    switch (filter) {
      case 'active':
        return !todo.completed;
      case 'completed':
        return todo.completed;
      default:
        return true;
    }
  });

  return (
    <div className="widget todo-widget">
      <div className="widget-header">
        <h3 className="widget-title">Todo Manager</h3>
        <div className="todo-stats">
          {todos.filter(t => !t.completed).length} remaining
        </div>
      </div>

      <form onSubmit={addTodo} className="todo-form">
        <input
          type="text"
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          placeholder="Add a new todo..."
          className="todo-input"
        />
        <button type="submit" className="add-btn">
          <Plus size={18} />
        </button>
      </form>

      <div className="todo-filters">
        {['all', 'active', 'completed'].map(filterType => (
          <button
            key={filterType}
            className={`filter-btn ${filter === filterType ? 'active' : ''}`}
            onClick={() => setFilter(filterType)}
          >
            {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
          </button>
        ))}
      </div>

      <div className="todo-list">
        {filteredTodos.length === 0 ? (
          <div className="empty-state">
            <p>No todos found</p>
          </div>
        ) : (
          filteredTodos.map(todo => (
            <div key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
              {editingId === todo.id ? (
                <div className="todo-edit">
                  <input
                    type="text"
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') saveEdit();
                      if (e.key === 'Escape') cancelEdit();
                    }}
                    autoFocus
                  />
                  <div className="edit-actions">
                    <button onClick={saveEdit} className="save-btn">
                      <Check size={14} />
                    </button>
                    <button onClick={cancelEdit} className="cancel-btn">
                      ×
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="todo-content">
                    <input
                      type="checkbox"
                      checked={todo.completed}
                      onChange={() => toggleTodo(todo.id)}
                      className="todo-checkbox"
                    />
                    <span className="todo-text">{todo.text}</span>
                  </div>
                  <div className="todo-actions">
                    <button
                      onClick={() => startEditing(todo.id, todo.text)}
                      className="edit-btn"
                      title="Edit todo"
                    >
                      <Edit3 size={14} />
                    </button>
                    <button
                      onClick={() => deleteTodo(todo.id)}
                      className="delete-btn"
                      title="Delete todo"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>

      {todos.length > 0 && (
        <div className="todo-summary">
          <div className="summary-stats">
            <span>{todos.filter(t => t.completed).length} completed</span>
            <span>•</span>
            <span>{todos.length} total</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default TodoWidget;
{% endraw %}
```

### 5. Complete Dashboard Styling
```css
/* src/App.css */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  line-height: 1.6;
  color: #333;
}

/* Dashboard Layout */
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  transition: all 0.3s ease;
}

.dashboard.dark {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

/* Dashboard Header */
.dashboard-header {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.user-info h1 {
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.current-time {
  opacity: 0.8;
  font-size: 0.9rem;
}

.header-right {
  display: flex;
  gap: 10px;
}

.theme-toggle,
.settings-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.theme-toggle:hover,
.settings-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Dashboard Grid */
.dashboard-grid {
  max-width: 1200px;
  margin: 20px auto 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

/* Widget Base Styles */
.widget {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.widget:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.widget-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 15px;
  color: #1f2937;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

/* Quick Stats Widget */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.stat-item:hover {
  background: #e2e8f0;
}

.stat-icon {
  padding: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.stat-label {
  font-size: 0.85rem;
  color: #6b7280;
}

/* Weather Widget */
.weather-widget {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  color: white;
}

.weather-widget .widget-title {
  color: white;
}

.current-weather {
  margin-bottom: 20px;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.weather-icon {
  padding: 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.temperature {
  font-size: 2.5rem;
  font-weight: bold;
}

.condition {
  font-size: 1rem;
  opacity: 0.9;
}

.location {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-top: 5px;
}

.weather-details {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.weather-forecast h4 {
  margin-bottom: 10px;
  color: white;
}

.forecast-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.forecast-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 80px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.forecast-day {
  font-size: 0.8rem;
  opacity: 0.9;
}

.forecast-temps {
  display: flex;
  gap: 5px;
  font-size: 0.85rem;
}

.forecast-temps .high {
  font-weight: bold;
}

.forecast-temps .low {
  opacity: 0.7;
}

/* Todo Widget */
.todo-form {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.todo-input {
  flex: 1;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.todo-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.add-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.add-btn:hover {
  background: #2563eb;
}

.todo-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: #f3f4f6;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.todo-list {
  max-height: 300px;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.todo-item:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.todo-item.completed {
  opacity: 0.6;
  background: #f0f9ff;
}

.todo-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.todo-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.todo-text {
  flex: 1;
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
}

.todo-actions {
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.edit-btn:hover {
  background: #dbeafe;
  color: #3b82f6;
}

.delete-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

.todo-edit {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.todo-edit input {
  flex: 1;
  padding: 8px;
  border: 2px solid #3b82f6;
  border-radius: 4px;
}

.edit-actions {
  display: flex;
  gap: 5px;
}

.save-btn,
.cancel-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.save-btn {
  color: #10b981;
}

.cancel-btn {
  color: #dc2626;
}

.todo-summary {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.summary-stats {
  display: flex;
  justify-content: center;
  gap: 10px;
  font-size: 0.85rem;
  color: #6b7280;
}

.todo-stats {
  font-size: 0.85rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
}

/* Loading and Error States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    margin-top: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .forecast-list {
    justify-content: center;
  }
  
  .user-info {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .widget {
    padding: 15px;
  }
  
  .dashboard-header {
    padding: 15px;
  }
  
  .todo-form {
    flex-direction: column;
  }
  
  .add-btn {
    align-self: stretch;
  }
}
```

---

## 📱 Complete App Integration

```jsx
{% raw %}
// src/App.js - Complete Integration
import React, { useState, useEffect } from 'react';
import './App.css';

// Import all components
import DashboardHeader from './components/Dashboard/DashboardHeader';
import QuickStats from './components/Dashboard/QuickStats';
import WeatherWidget from './components/Widgets/WeatherWidget';
import TodoWidget from './components/Widgets/TodoWidget';
import ContactWidget from './components/Widgets/ContactWidget';
import PortfolioWidget from './components/Widgets/PortfolioWidget';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [user, setUser] = useState({
    name: 'John Doe',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face'
  });

  const [dashboardStats, setDashboardStats] = useState({
    completedTodos: 0,
    totalProjects: 6,
    unreadMessages: 3,
    productivity: 85
  });

  useEffect(() => {
    // Load theme preference
    const savedTheme = localStorage.getItem('dashboard-theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  const handleThemeToggle = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    localStorage.setItem('dashboard-theme', newTheme ? 'dark' : 'light');
  };

  const handleStatsUpdate = (newStats) => {
    setDashboardStats(prev => ({ ...prev, ...newStats }));
  };

  return (
    <div className={`dashboard ${isDarkMode ? 'dark' : ''}`}>
      <DashboardHeader 
        user={user} 
        onThemeToggle={handleThemeToggle}
        isDarkMode={isDarkMode}
      />
      
      <div className="dashboard-grid">
        <QuickStats stats={dashboardStats} />
        <WeatherWidget />
        <TodoWidget onStatsUpdate={handleStatsUpdate} />
        <ContactWidget />
        <PortfolioWidget />
      </div>
    </div>
  );
}

export default App;
{% endraw %}
```

---

## 🎯 Learning Objectives Achieved

### Core React Concepts
- ✅ **Component Composition** - Multiple reusable components working together
- ✅ **State Management** - Local state, derived state, and state lifting
- ✅ **Props Management** - Data flow between parent and child components
- ✅ **Event Handling** - User interactions and form submissions
- ✅ **Conditional Rendering** - Dynamic UI based on state and data
- ✅ **Lists and Keys** - Rendering dynamic lists efficiently
- ✅ **Side Effects** - API calls, timers, and data persistence
- ✅ **Form Handling** - Controlled components and validation

### Integration Skills
- ✅ **Component Communication** - Data flow between sibling components
- ✅ **State Synchronization** - Keeping related data in sync
- ✅ **Error Handling** - Graceful error states and recovery
- ✅ **Performance** - Efficient rendering and state updates
- ✅ **User Experience** - Loading states, transitions, and feedback

---

## 🚀 Enhancement Ideas

### Beginner Enhancements
- [ ] Add more widget types (calendar, notes, quotes)
- [ ] Implement widget reordering (drag and drop)
- [ ] Add data export/import functionality
- [ ] Create custom themes and color schemes
- [ ] Add keyboard shortcuts for common actions

### Advanced Features
- [ ] Real-time synchronization with backend
- [ ] User authentication and profiles
- [ ] Multiple dashboard layouts
- [ ] Widget customization options
- [ ] Progressive Web App features

---

## 📚 Key Takeaways

1. **Component Architecture**: Learn to structure complex applications with multiple interconnected components
2. **State Management**: Understand when to lift state up and how to manage data flow
3. **Integration Patterns**: Practice combining different features into cohesive user experience
4. **User Experience**: Focus on loading states, error handling, and responsive design
5. **Code Organization**: Structure code for maintainability and scalability

This capstone project demonstrates mastery of fundamental React concepts and prepares you for intermediate-level development with more complex state management and advanced patterns.

---

**🎉 Congratulations!** You've completed all 6 Beginner React projects. You're now ready to move on to [Intermediate Projects](../../Intermediate/README.md) where you'll learn advanced hooks, context, routing, and more complex patterns.
