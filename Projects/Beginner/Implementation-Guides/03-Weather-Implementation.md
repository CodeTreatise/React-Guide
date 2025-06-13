# 🌦️ Weather Dashboard - Implementation Guide

> **Project**: Component Communication & Props Drilling  
> **Difficulty**: Beginner  
> **Duration**: 1-2 days  
> **Focus**: Props drilling, Component communication, Mock data handling

## 🎯 Project Overview

Build a weather dashboard that displays current weather and forecasts for multiple cities. This project teaches component communication, props drilling, and managing shared state between components - essential skills for building larger React applications.

## 🚀 Quick Start (15 minutes)

```bash
# Create your weather dashboard project
npx create-react-app weather-dashboard
cd weather-dashboard

# Install dependencies for icons and mock data
npm install react-icons

# Start development server
npm start

# Your app will open at http://localhost:3000
```

## 🏗️ Architecture Overview

### Component Hierarchy
```
App Component
└── WeatherDashboard Component
    ├── CitySelector Component
    ├── CurrentWeather Component
    │   ├── WeatherCard Component
    │   ├── TemperatureDisplay Component
    │   └── WeatherDetails Component
    └── WeatherForecast Component
        └── ForecastItem Components (Array)
```

### Beginner-Friendly Tech Stack

| Tool | Purpose | Why Perfect for Beginners |
|------|---------|---------------------------|
| **Mock Data** | Weather Information | Focus on React concepts, not API complexity |
| **React Icons** | Weather Icons | Professional weather symbols |
| **Props Drilling** | Data Flow | Learn fundamental React data passing |
| **Conditional Rendering** | Dynamic UI | Show/hide elements based on data |

### Project Structure
```
weather-dashboard/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── WeatherDashboard.js
│   │   ├── CitySelector.js
│   │   ├── CurrentWeather.js
│   │   ├── WeatherCard.js
│   │   ├── TemperatureDisplay.js
│   │   ├── WeatherDetails.js
│   │   ├── WeatherForecast.js
│   │   └── ForecastItem.js
│   ├── data/
│   │   └── mockWeatherData.js
│   ├── styles/
│   │   ├── WeatherDashboard.css
│   │   ├── CurrentWeather.css
│   │   └── WeatherForecast.css
│   ├── App.js
│   ├── App.css
│   └── index.js
└── package.json
```

## 📋 Step-by-Step Implementation

### Step 1: Understanding Props Drilling (5 minutes)

Before we code, let's understand component communication:

```jsx
// What is Props Drilling?
// Passing data from parent → child → grandchild components

// Example:
function GrandParent() {
  const data = "Hello World";
  return <Parent data={data} />;
}

function Parent({ data }) {
  return <Child data={data} />;
}

function Child({ data }) {
  return <div>{data}</div>;
}
```

### Step 2: Create Mock Weather Data

```javascript
// src/data/mockWeatherData.js
export const mockWeatherData = {
  cities: [
    {
      id: 1,
      name: "New York",
      country: "USA",
      current: {
        temperature: 22,
        condition: "sunny",
        humidity: 65,
        windSpeed: 12,
        pressure: 1013,
        feelsLike: 25,
        uvIndex: 6,
        visibility: 10
      },
      forecast: [
        {
          day: "Today",
          high: 25,
          low: 18,
          condition: "sunny",
          precipitation: 0
        },
        {
          day: "Tomorrow",
          high: 23,
          low: 16,
          condition: "cloudy",
          precipitation: 20
        },
        {
          day: "Wednesday",
          high: 20,
          low: 14,
          condition: "rainy",
          precipitation: 80
        },
        {
          day: "Thursday",
          high: 24,
          low: 17,
          condition: "partly-cloudy",
          precipitation: 10
        },
        {
          day: "Friday",
          high: 26,
          low: 19,
          condition: "sunny",
          precipitation: 0
        }
      ]
    },
    {
      id: 2,
      name: "London",
      country: "UK",
      current: {
        temperature: 15,
        condition: "cloudy",
        humidity: 78,
        windSpeed: 8,
        pressure: 1008,
        feelsLike: 13,
        uvIndex: 3,
        visibility: 8
      },
      forecast: [
        {
          day: "Today",
          high: 17,
          low: 12,
          condition: "cloudy",
          precipitation: 15
        },
        {
          day: "Tomorrow",
          high: 14,
          low: 9,
          condition: "rainy",
          precipitation: 75
        },
        {
          day: "Wednesday",
          high: 16,
          low: 11,
          condition: "partly-cloudy",
          precipitation: 30
        },
        {
          day: "Thursday",
          high: 18,
          low: 13,
          condition: "sunny",
          precipitation: 5
        },
        {
          day: "Friday",
          high: 19,
          low: 14,
          condition: "sunny",
          precipitation: 0
        }
      ]
    },
    {
      id: 3,
      name: "Tokyo",
      country: "Japan",
      current: {
        temperature: 28,
        condition: "partly-cloudy",
        humidity: 72,
        windSpeed: 6,
        pressure: 1015,
        feelsLike: 31,
        uvIndex: 7,
        visibility: 12
      },
      forecast: [
        {
          day: "Today",
          high: 30,
          low: 24,
          condition: "partly-cloudy",
          precipitation: 25
        },
        {
          day: "Tomorrow",
          high: 32,
          low: 26,
          condition: "sunny",
          precipitation: 5
        },
        {
          day: "Wednesday",
          high: 29,
          low: 23,
          condition: "rainy",
          precipitation: 85
        },
        {
          day: "Thursday",
          high: 27,
          low: 21,
          condition: "cloudy",
          precipitation: 40
        },
        {
          day: "Friday",
          high: 31,
          low: 25,
          condition: "sunny",
          precipitation: 0
        }
      ]
    }
  ]
};

// Weather condition mappings for icons
export const weatherIcons = {
  sunny: "☀️",
  cloudy: "☁️",
  "partly-cloudy": "⛅",
  rainy: "🌧️",
  stormy: "⛈️",
  snowy: "❄️",
  foggy: "🌫️"
};
```

### Step 3: Create the Main Weather Dashboard Component

```jsx
// src/components/WeatherDashboard.js
import React, { useState } from 'react';
import CitySelector from './CitySelector';
import CurrentWeather from './CurrentWeather';
import WeatherForecast from './WeatherForecast';
import { mockWeatherData } from '../data/mockWeatherData';
import './WeatherDashboard.css';

const WeatherDashboard = () => {
  const [selectedCityId, setSelectedCityId] = useState(1);
  
  // Find the selected city data
  const selectedCity = mockWeatherData.cities.find(
    city => city.id === selectedCityId
  );

  const handleCityChange = (cityId) => {
    setSelectedCityId(cityId);
  };

  return (
    <div className="weather-dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">🌦️ Weather Dashboard</h1>
        <p className="dashboard-subtitle">
          Stay updated with current weather and forecasts
        </p>
      </div>

      <CitySelector
        cities={mockWeatherData.cities}
        selectedCityId={selectedCityId}
        onCityChange={handleCityChange}
      />

      {selectedCity && (
        <div className="weather-content">
          <CurrentWeather
            cityName={selectedCity.name}
            country={selectedCity.country}
            currentWeather={selectedCity.current}
          />
          
          <WeatherForecast
            cityName={selectedCity.name}
            forecast={selectedCity.forecast}
          />
        </div>
      )}
    </div>
  );
};

export default WeatherDashboard;
```

**Key Learning Points:**
- **State Management**: Using `useState` to track selected city
- **Props Drilling**: Passing data down through multiple component levels
- **Data Finding**: Using `Array.find()` to locate specific data
- **Conditional Rendering**: Only showing weather when city is selected

### Step 4: Create the City Selector Component

```jsx
// src/components/CitySelector.js
import React from 'react';
import { FaMapMarkerAlt } from 'react-icons/fa';

const CitySelector = ({ cities, selectedCityId, onCityChange }) => {
  return (
    <div className="city-selector">
      <div className="selector-header">
        <FaMapMarkerAlt className="location-icon" />
        <span className="selector-label">Select City:</span>
      </div>
      
      <div className="city-buttons">
        {cities.map((city) => (
          <button
            key={city.id}
            className={`city-button ${
              selectedCityId === city.id ? 'active' : ''
            }`}
            onClick={() => onCityChange(city.id)}
          >
            <span className="city-name">{city.name}</span>
            <span className="city-country">{city.country}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CitySelector;
```

**Key Learning Points:**
- **Event Handling**: Calling parent function `onCityChange`
- **Dynamic Classes**: Adding `active` class conditionally
- **Array Mapping**: Creating buttons for each city
- **Component Props**: Receiving and using props from parent

### Step 5: Create the Current Weather Component

```jsx
// src/components/CurrentWeather.js
import React from 'react';
import WeatherCard from './WeatherCard';
import TemperatureDisplay from './TemperatureDisplay';
import WeatherDetails from './WeatherDetails';
import './CurrentWeather.css';

const CurrentWeather = ({ cityName, country, currentWeather }) => {
  return (
    <div className="current-weather">
      <div className="weather-header">
        <h2 className="location-title">
          {cityName}, {country}
        </h2>
        <p className="weather-timestamp">
          Updated: {new Date().toLocaleTimeString()}
        </p>
      </div>

      <div className="weather-main">
        <WeatherCard
          temperature={currentWeather.temperature}
          condition={currentWeather.condition}
          feelsLike={currentWeather.feelsLike}
        />
        
        <TemperatureDisplay
          temperature={currentWeather.temperature}
          feelsLike={currentWeather.feelsLike}
          condition={currentWeather.condition}
        />
      </div>

      <WeatherDetails
        humidity={currentWeather.humidity}
        windSpeed={currentWeather.windSpeed}
        pressure={currentWeather.pressure}
        uvIndex={currentWeather.uvIndex}
        visibility={currentWeather.visibility}
      />
    </div>
  );
};

export default CurrentWeather;
```

### Step 6: Create the Weather Card Component

```jsx
// src/components/WeatherCard.js
import React from 'react';
import { weatherIcons } from '../data/mockWeatherData';

const WeatherCard = ({ temperature, condition, feelsLike }) => {
  const getWeatherIcon = (condition) => {
    return weatherIcons[condition] || '🌡️';
  };

  const getConditionText = (condition) => {
    return condition.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="weather-card">
      <div className="weather-icon">
        {getWeatherIcon(condition)}
      </div>
      
      <div className="weather-info">
        <div className="temperature-main">
          {temperature}°C
        </div>
        <div className="condition-text">
          {getConditionText(condition)}
        </div>
        <div className="feels-like">
          Feels like {feelsLike}°C
        </div>
      </div>
    </div>
  );
};

export default WeatherCard;
```

### Step 7: Create the Temperature Display Component

```jsx
// src/components/TemperatureDisplay.js
import React from 'react';
import { FaThermometerHalf, FaEye } from 'react-icons/fa';

const TemperatureDisplay = ({ temperature, feelsLike, condition }) => {
  const getTemperatureColor = (temp) => {
    if (temp >= 30) return '#ff4444'; // Hot - Red
    if (temp >= 20) return '#ff8800'; // Warm - Orange
    if (temp >= 10) return '#4488ff'; // Cool - Blue
    return '#8844ff'; // Cold - Purple
  };

  const getTemperatureDescription = (temp) => {
    if (temp >= 30) return 'Hot';
    if (temp >= 20) return 'Warm';
    if (temp >= 10) return 'Cool';
    return 'Cold';
  };

  return (
    <div className="temperature-display">
      <div className="temp-gauge">
        <div className="temp-circle">
          <FaThermometerHalf 
            className="temp-icon"
            style={{ color: getTemperatureColor(temperature) }}
          />
          <div className="temp-value">{temperature}°</div>
        </div>
        <div className="temp-description">
          {getTemperatureDescription(temperature)}
        </div>
      </div>
      
      <div className="temp-details">
        <div className="detail-item">
          <FaEye className="detail-icon" />
          <span>Feels like {feelsLike}°C</span>
        </div>
      </div>
    </div>
  );
};

export default TemperatureDisplay;
```

### Step 8: Create the Weather Details Component

```jsx
// src/components/WeatherDetails.js
import React from 'react';
import { 
  FaTint, 
  FaWind, 
  FaCompress, 
  FaSun, 
  FaEye 
} from 'react-icons/fa';

const WeatherDetails = ({ 
  humidity, 
  windSpeed, 
  pressure, 
  uvIndex, 
  visibility 
}) => {
  const getUVIndexLevel = (uv) => {
    if (uv <= 2) return { level: 'Low', color: '#4caf50' };
    if (uv <= 5) return { level: 'Moderate', color: '#ff9800' };
    if (uv <= 7) return { level: 'High', color: '#f44336' };
    if (uv <= 10) return { level: 'Very High', color: '#9c27b0' };
    return { level: 'Extreme', color: '#673ab7' };
  };

  const uvInfo = getUVIndexLevel(uvIndex);

  return (
    <div className="weather-details">
      <h3 className="details-title">Weather Details</h3>
      
      <div className="details-grid">
        <div className="detail-card">
          <div className="detail-header">
            <FaTint className="detail-icon humidity" />
            <span className="detail-label">Humidity</span>
          </div>
          <div className="detail-value">{humidity}%</div>
          <div className="detail-bar">
            <div 
              className="detail-fill humidity-fill"
              style={{ width: `${humidity}%` }}
            ></div>
          </div>
        </div>

        <div className="detail-card">
          <div className="detail-header">
            <FaWind className="detail-icon wind" />
            <span className="detail-label">Wind Speed</span>
          </div>
          <div className="detail-value">{windSpeed} km/h</div>
          <div className="wind-description">
            {windSpeed < 5 ? 'Light breeze' : 
             windSpeed < 15 ? 'Moderate wind' : 'Strong wind'}
          </div>
        </div>

        <div className="detail-card">
          <div className="detail-header">
            <FaCompress className="detail-icon pressure" />
            <span className="detail-label">Pressure</span>
          </div>
          <div className="detail-value">{pressure} hPa</div>
          <div className="pressure-trend">
            {pressure > 1013 ? '↗️ High' : 
             pressure < 1000 ? '↘️ Low' : '→ Normal'}
          </div>
        </div>

        <div className="detail-card">
          <div className="detail-header">
            <FaSun className="detail-icon uv" />
            <span className="detail-label">UV Index</span>
          </div>
          <div className="detail-value">
            {uvIndex}
            <span 
              className="uv-level"
              style={{ color: uvInfo.color }}
            >
              {uvInfo.level}
            </span>
          </div>
        </div>

        <div className="detail-card">
          <div className="detail-header">
            <FaEye className="detail-icon visibility" />
            <span className="detail-label">Visibility</span>
          </div>
          <div className="detail-value">{visibility} km</div>
          <div className="visibility-description">
            {visibility >= 10 ? 'Excellent' : 
             visibility >= 5 ? 'Good' : 'Poor'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeatherDetails;
```

### Step 9: Create the Weather Forecast Component

```jsx
// src/components/WeatherForecast.js
import React from 'react';
import ForecastItem from './ForecastItem';
import './WeatherForecast.css';

const WeatherForecast = ({ cityName, forecast }) => {
  return (
    <div className="weather-forecast">
      <div className="forecast-header">
        <h3 className="forecast-title">
          5-Day Forecast for {cityName}
        </h3>
        <p className="forecast-subtitle">
          Plan ahead with detailed weather predictions
        </p>
      </div>

      <div className="forecast-list">
        {forecast.map((day, index) => (
          <ForecastItem
            key={index}
            day={day.day}
            high={day.high}
            low={day.low}
            condition={day.condition}
            precipitation={day.precipitation}
            isToday={index === 0}
          />
        ))}
      </div>
    </div>
  );
};

export default WeatherForecast;
```

### Step 10: Create the Forecast Item Component

```jsx
// src/components/ForecastItem.js
import React from 'react';
import { weatherIcons } from '../data/mockWeatherData';
import { FaUmbrella } from 'react-icons/fa';

const ForecastItem = ({ 
  day, 
  high, 
  low, 
  condition, 
  precipitation, 
  isToday 
}) => {
  const getWeatherIcon = (condition) => {
    return weatherIcons[condition] || '🌡️';
  };

  const getPrecipitationColor = (chance) => {
    if (chance >= 70) return '#2196f3'; // High - Blue
    if (chance >= 40) return '#ff9800'; // Medium - Orange
    if (chance >= 10) return '#4caf50'; // Low - Green
    return '#9e9e9e'; // None - Gray
  };

  return (
    <div className={`forecast-item ${isToday ? 'today' : ''}`}>
      <div className="forecast-day">
        <span className="day-name">{day}</span>
        {isToday && <span className="today-badge">Today</span>}
      </div>

      <div className="forecast-icon">
        {getWeatherIcon(condition)}
      </div>

      <div className="forecast-temps">
        <span className="temp-high">{high}°</span>
        <span className="temp-divider">/</span>
        <span className="temp-low">{low}°</span>
      </div>

      <div className="forecast-precipitation">
        <FaUmbrella 
          className="rain-icon"
          style={{ color: getPrecipitationColor(precipitation) }}
        />
        <span className="rain-chance">{precipitation}%</span>
      </div>

      <div className="forecast-condition">
        {condition.split('-').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ')}
      </div>
    </div>
  );
};

export default ForecastItem;
```

### Step 11: Add Comprehensive Styling

```css
/* src/styles/WeatherDashboard.css */
.weather-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  min-height: 100vh;
  color: white;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.dashboard-title {
  font-size: 3rem;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.dashboard-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
}

.city-selector {
  background: rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
}

.selector-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.location-icon {
  color: #ff7675;
  font-size: 1.2rem;
}

.city-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.city-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 1.5rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.city-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.city-button.active {
  border-color: #00b894;
  background: rgba(0, 184, 148, 0.3);
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.city-name {
  font-weight: 600;
  font-size: 1.1rem;
}

.city-country {
  font-size: 0.9rem;
  opacity: 0.8;
}

.weather-content {
  display: grid;
  gap: 2rem;
}

@media (max-width: 768px) {
  .weather-dashboard {
    padding: 1rem;
  }
  
  .dashboard-title {
    font-size: 2rem;
  }
  
  .city-buttons {
    justify-content: center;
  }
}
```

```css
/* src/styles/CurrentWeather.css */
.current-weather {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.weather-header {
  text-align: center;
  margin-bottom: 2rem;
}

.location-title {
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
  color: white;
}

.weather-timestamp {
  opacity: 0.8;
  margin: 0;
  font-size: 0.9rem;
}

.weather-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.weather-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.weather-icon {
  font-size: 4rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.temperature-main {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.condition-text {
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
  color: #fdcb6e;
}

.feels-like {
  opacity: 0.8;
  font-size: 1rem;
}

.temperature-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.temp-gauge {
  text-align: center;
  margin-bottom: 1rem;
}

.temp-circle {
  position: relative;
  margin-bottom: 1rem;
}

.temp-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.temp-value {
  font-size: 2rem;
  font-weight: bold;
}

.temp-description {
  font-size: 1.1rem;
  color: #fdcb6e;
  font-weight: 600;
}

.weather-details {
  margin-top: 2rem;
}

.details-title {
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  text-align: center;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.detail-icon {
  font-size: 1.2rem;
}

.detail-icon.humidity { color: #74b9ff; }
.detail-icon.wind { color: #a29bfe; }
.detail-icon.pressure { color: #fd79a8; }
.detail-icon.uv { color: #fdcb6e; }
.detail-icon.visibility { color: #00b894; }

.detail-label {
  font-weight: 600;
  font-size: 0.9rem;
}

.detail-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.detail-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.detail-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.humidity-fill {
  background: linear-gradient(90deg, #74b9ff, #0984e3);
}

.uv-level {
  font-size: 0.8rem;
  font-weight: normal;
  margin-left: 0.5rem;
}

@media (max-width: 768px) {
  .weather-main {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .weather-card {
    flex-direction: column;
    text-align: center;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
}
```

```css
/* src/styles/WeatherForecast.css */
.weather-forecast {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.forecast-header {
  text-align: center;
  margin-bottom: 2rem;
}

.forecast-title {
  font-size: 1.8rem;
  margin: 0 0 0.5rem 0;
  color: white;
}

.forecast-subtitle {
  opacity: 0.8;
  margin: 0;
  font-size: 1rem;
}

.forecast-list {
  display: grid;
  gap: 1rem;
}

.forecast-item {
  display: grid;
  grid-template-columns: 1fr auto auto auto 1fr;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.forecast-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.forecast-item.today {
  border-color: #00b894;
  background: rgba(0, 184, 148, 0.2);
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3);
}

.forecast-day {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.day-name {
  font-weight: 600;
  font-size: 1.1rem;
}

.today-badge {
  background: #00b894;
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: bold;
}

.forecast-icon {
  font-size: 2rem;
  text-align: center;
}

.forecast-temps {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 1.2rem;
}

.temp-high {
  font-weight: bold;
  color: #fdcb6e;
}

.temp-divider {
  opacity: 0.6;
}

.temp-low {
  opacity: 0.8;
}

.forecast-precipitation {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.rain-icon {
  font-size: 0.9rem;
}

.rain-chance {
  font-size: 0.9rem;
  font-weight: 600;
}

.forecast-condition {
  text-align: right;
  font-size: 0.9rem;
  opacity: 0.9;
  font-weight: 500;
}

@media (max-width: 768px) {
  .forecast-item {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 0.5rem;
  }
  
  .forecast-day {
    justify-content: center;
  }
  
  .forecast-condition {
    text-align: center;
  }
}
```

### Step 12: Update App.js to Use the Weather Dashboard

```jsx
// src/App.js
import React from 'react';
import WeatherDashboard from './components/WeatherDashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <WeatherDashboard />
    </div>
  );
}

export default App;
```

```css
/* src/App.css */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
               'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  min-height: 100vh;
}

.App {
  min-height: 100vh;
}
```

## 🛠️ Common Issues & Troubleshooting

### Issue 1: "Props not updating correctly"
**Explanation:** Make sure props are being passed correctly through the component hierarchy
```jsx
// ✅ Correct - pass props explicitly
<CurrentWeather
  cityName={selectedCity.name}
  country={selectedCity.country}
  currentWeather={selectedCity.current}
/>

// ❌ Incorrect - missing props
<CurrentWeather city={selectedCity} />
```

### Issue 2: "Component not re-rendering when city changes"
**Solution:** Ensure state is properly managed in parent component
```jsx
// ✅ Correct - state change triggers re-render
const [selectedCityId, setSelectedCityId] = useState(1);

// ❌ Incorrect - using regular variable
let selectedCityId = 1;
```

### Issue 3: "Weather icons not showing"
**Solution:** Check that the condition names match the weatherIcons object
```jsx
// Make sure your data uses these exact condition names:
// "sunny", "cloudy", "partly-cloudy", "rainy", "stormy", "snowy", "foggy"
```

### Issue 4: "CSS styles not applying"
**Solution:** Make sure CSS files are imported correctly
```jsx
// ✅ Correct - import CSS files
import './WeatherDashboard.css';
import './CurrentWeather.css';
import './WeatherForecast.css';
```

## 📱 Making It Mobile-Friendly

The styles already include responsive design, but here are the key concepts:

```css
/* Grid layouts that stack on mobile */
@media (max-width: 768px) {
  .weather-main {
    grid-template-columns: 1fr; /* Stack vertically */
  }
  
  .forecast-item {
    grid-template-columns: 1fr; /* Simplify layout */
    text-align: center;
  }
}
```

## 🌟 Enhancement Ideas

### Beginner Level:
1. **Add more cities** to the mock data
2. **Change color themes** based on weather condition
3. **Add weather alerts** for extreme conditions

### Intermediate Level:
1. **Add search functionality** for cities
2. **Include hourly forecast** in addition to daily
3. **Add weather maps** or background images

### Advanced Level:
1. **Connect to real weather API** (OpenWeatherMap)
2. **Add geolocation** to detect user's city
3. **Include weather notifications** and alerts

## ✅ Success Criteria

### Functionality Checklist:
- [ ] **City Selection**: Can switch between different cities
- [ ] **Weather Display**: Shows current weather with all details
- [ ] **Forecast**: Displays 5-day weather forecast
- [ ] **Icons**: Weather icons display correctly for each condition
- [ ] **Responsive Design**: Works well on mobile and desktop

### Learning Objectives Met:
- [ ] **Props Drilling**: Comfortable passing data through multiple component levels
- [ ] **Component Communication**: Understand parent-child communication patterns
- [ ] **Mock Data**: Can work with complex data structures
- [ ] **Conditional Rendering**: Show/hide elements based on state
- [ ] **Event Handling**: Handle user interactions across components

## 🎓 Concepts Learned

### React Fundamentals:
- **Props Drilling**: Passing data through multiple component levels
- **Component Communication**: Parent-child data flow patterns
- **State Management**: Managing shared state at the right level
- **Event Bubbling**: Handling events from child components
- **Conditional Rendering**: Dynamic UI based on data

### JavaScript Skills:
- **Array Methods**: `find()`, `map()`, `filter()` for data manipulation
- **Object Destructuring**: Extracting values from nested objects
- **Template Literals**: String formatting and interpolation
- **Date Handling**: Working with timestamps and formatting

### CSS Techniques:
- **CSS Grid**: Complex responsive layouts
- **Backdrop Filter**: Modern blur effects
- **CSS Variables**: Consistent theming
- **Media Queries**: Mobile-responsive design
- **Flexbox**: Component alignment and spacing

## 📚 What's Next?

After completing this project, you're ready for:

1. **Project 4: Todo List Manager** - Learn CRUD operations and array state management
2. **Real API Integration** - Connect to actual weather services
3. **Advanced State Management** - Explore Context API for global state
4. **Data Persistence** - Save user preferences and favorite cities

---

**Congratulations!** 🎉 You've mastered component communication and props drilling! This weather dashboard demonstrates how to structure larger React applications with multiple interacting components.

**Next**: [Todo List Implementation Guide](./04-Todo-Implementation.md)
