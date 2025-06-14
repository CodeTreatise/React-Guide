# 🌍 Weather App API Integration Implementation Guide

> **Project**: Comprehensive Weather Application with API Integration  
> **Level**: Intermediate  
> **Estimated Time**: 6-8 hours  
> **Focus**: API integration, data fetching, error handling, caching

---

## 🚀 Quick Start (30 minutes)

### Step 1: Setup Project
```bash
npx create-react-app weather-api-app
cd weather-api-app
npm install axios date-fns react-query
npm start
```

### Step 2: Get OpenWeatherMap API Key
1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Create `.env` file in project root:

```env
REACT_APP_WEATHER_API_KEY=your_api_key_here
REACT_APP_WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
REACT_APP_GEOCODING_API_BASE_URL=https://api.openweathermap.org/geo/1.0
```

### Step 3: Basic API Service
```jsx
{% raw %}
// src/services/weatherAPI.js
import axios from 'axios';

const API_KEY = process.env.REACT_APP_WEATHER_API_KEY;
const BASE_URL = process.env.REACT_APP_WEATHER_API_BASE_URL;
const GEO_BASE_URL = process.env.REACT_APP_GEOCODING_API_BASE_URL;

class WeatherAPI {
  constructor() {
    this.api = axios.create({
      baseURL: BASE_URL,
      params: {
        appid: API_KEY,
        units: 'metric'
      },
      timeout: 10000
    });

    this.geoAPI = axios.create({
      baseURL: GEO_BASE_URL,
      params: {
        appid: API_KEY
      },
      timeout: 5000
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      response => response,
      error => {
        console.error('Weather API Error:', error);
        throw this.handleError(error);
      }
    );
  }

  handleError(error) {
    if (error.response) {
      // Server responded with error status
      return new Error(`Weather API Error: ${error.response.data.message || error.response.statusText}`);
    } else if (error.request) {
      // Request made but no response
      return new Error('Network error: Unable to connect to weather service');
    } else {
      // Something else happened
      return new Error('An unexpected error occurred');
    }
  }

  async getCurrentWeather(lat, lon) {
    const response = await this.api.get('/weather', {
      params: { lat, lon }
    });
    return this.transformWeatherData(response.data);
  }

  async getForecast(lat, lon) {
    const response = await this.api.get('/forecast', {
      params: { lat, lon }
    });
    return this.transformForecastData(response.data);
  }

  async searchLocations(query) {
    const response = await this.geoAPI.get('/direct', {
      params: { q: query, limit: 5 }
    });
    return response.data.map(this.transformLocationData);
  }

  async getLocationByCoords(lat, lon) {
    const response = await this.geoAPI.get('/reverse', {
      params: { lat, lon, limit: 1 }
    });
    return response.data[0] ? this.transformLocationData(response.data[0]) : null;
  }

  transformWeatherData(data) {
    return {
      id: data.id,
      location: {
        name: data.name,
        country: data.sys.country,
        coords: {
          lat: data.coord.lat,
          lon: data.coord.lon
        }
      },
      weather: {
        main: data.weather[0].main,
        description: data.weather[0].description,
        icon: data.weather[0].icon
      },
      temperature: {
        current: Math.round(data.main.temp),
        feelsLike: Math.round(data.main.feels_like),
        min: Math.round(data.main.temp_min),
        max: Math.round(data.main.temp_max)
      },
      details: {
        humidity: data.main.humidity,
        pressure: data.main.pressure,
        visibility: data.visibility / 1000, // Convert to km
        windSpeed: data.wind.speed,
        windDirection: data.wind.deg,
        cloudiness: data.clouds.all
      },
      sun: {
        sunrise: data.sys.sunrise * 1000,
        sunset: data.sys.sunset * 1000
      },
      timestamp: data.dt * 1000
    };
  }

  transformForecastData(data) {
    return {
      location: {
        name: data.city.name,
        country: data.city.country,
        coords: {
          lat: data.city.coord.lat,
          lon: data.city.coord.lon
        }
      },
      forecasts: data.list.map(item => ({
        datetime: item.dt * 1000,
        weather: {
          main: item.weather[0].main,
          description: item.weather[0].description,
          icon: item.weather[0].icon
        },
        temperature: {
          current: Math.round(item.main.temp),
          min: Math.round(item.main.temp_min),
          max: Math.round(item.main.temp_max),
          feelsLike: Math.round(item.main.feels_like)
        },
        details: {
          humidity: item.main.humidity,
          windSpeed: item.wind.speed,
          windDirection: item.wind.deg,
          cloudiness: item.clouds.all,
          precipitation: item.rain?.['3h'] || item.snow?.['3h'] || 0
        }
      }))
    };
  }

  transformLocationData(data) {
    return {
      name: data.name,
      state: data.state,
      country: data.country,
      coords: {
        lat: data.lat,
        lon: data.lon
      },
      displayName: `${data.name}${data.state ? `, ${data.state}` : ''}, ${data.country}`
    };
  }
}

export const weatherAPI = new WeatherAPI();
{% endraw %}
```

### Step 4: Weather Hook
```jsx
{% raw %}
// src/hooks/useWeather.js
import { useState, useEffect, useCallback } from 'react';
import { weatherAPI } from '../services/weatherAPI';
import { cacheService } from '../services/cacheService';

export const useWeather = () => {
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWeatherData = useCallback(async (lat, lon, forceRefresh = false) => {
    setLoading(true);
    setError(null);

    try {
      const cacheKey = `weather_${lat}_${lon}`;
      
      // Check cache first
      if (!forceRefresh) {
        const cachedData = cacheService.get(cacheKey);
        if (cachedData) {
          setCurrentWeather(cachedData.current);
          setForecast(cachedData.forecast);
          setLoading(false);
          return;
        }
      }

      // Fetch fresh data
      const [weatherData, forecastData] = await Promise.all([
        weatherAPI.getCurrentWeather(lat, lon),
        weatherAPI.getForecast(lat, lon)
      ]);

      setCurrentWeather(weatherData);
      setForecast(forecastData);

      // Cache the data
      cacheService.set(cacheKey, {
        current: weatherData,
        forecast: forecastData
      }, 10 * 60 * 1000); // Cache for 10 minutes

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshWeather = useCallback(() => {
    if (currentWeather) {
      const { lat, lon } = currentWeather.location.coords;
      fetchWeatherData(lat, lon, true);
    }
  }, [currentWeather, fetchWeatherData]);

  return {
    currentWeather,
    forecast,
    loading,
    error,
    fetchWeatherData,
    refreshWeather
  };
};
{% endraw %}
```

### Step 5: Basic Weather App
```jsx
// src/components/WeatherApp.jsx
import React, { useState, useEffect } from 'react';
import { useWeather } from '../hooks/useWeather';
import { useGeolocation } from '../hooks/useGeolocation';
import LocationSearch from './LocationSearch/LocationSearch';
import CurrentWeather from './Weather/CurrentWeather';
import WeatherForecast from './Weather/WeatherForecast';
import LoadingSpinner from './UI/LoadingSpinner';
import ErrorMessage from './UI/ErrorMessage';
import './WeatherApp.css';

const WeatherApp = () => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const { currentWeather, forecast, loading, error, fetchWeatherData } = useWeather();
  const { coordinates, loading: geoLoading, error: geoError, getCurrentLocation } = useGeolocation();

  // Load weather for current location on mount
  useEffect(() => {
    getCurrentLocation();
  }, [getCurrentLocation]);

  // Fetch weather when coordinates change
  useEffect(() => {
    if (coordinates) {
      fetchWeatherData(coordinates.latitude, coordinates.longitude);
    }
  }, [coordinates, fetchWeatherData]);

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
    fetchWeatherData(location.coords.lat, location.coords.lon);
  };

  const handleUseCurrentLocation = () => {
    getCurrentLocation();
  };

  if (geoLoading || loading) {
    return <LoadingSpinner message="Loading weather data..." />;
  }

  return (
    <div className="weather-app">
      <header className="weather-header">
        <h1>🌤️ Weather App</h1>
        <LocationSearch 
          onLocationSelect={handleLocationSelect}
          onUseCurrentLocation={handleUseCurrentLocation}
        />
      </header>

      <main className="weather-main">
        {error && <ErrorMessage message={error} />}
        {geoError && <ErrorMessage message={geoError} />}
        
        {currentWeather && (
          <>
            <CurrentWeather weather={currentWeather} />
            {forecast && <WeatherForecast forecast={forecast} />}
          </>
        )}
      </main>
    </div>
  );
};

export default WeatherApp;
```

---

## 📚 Complete Implementation

### 1. Advanced Hooks

#### Geolocation Hook
```jsx
// src/hooks/useGeolocation.js
import { useState, useCallback } from 'react';

export const useGeolocation = () => {
  const [coordinates, setCoordinates] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getCurrentLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      return;
    }

    setLoading(true);
    setError(null);

    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000 // 5 minutes
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoordinates({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
        setLoading(false);
      },
      (error) => {
        let errorMessage = 'Failed to get location';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access denied by user';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out';
            break;
          default:
            errorMessage = 'An unknown error occurred';
            break;
        }
        
        setError(errorMessage);
        setLoading(false);
      },
      options
    );
  }, []);

  return {
    coordinates,
    loading,
    error,
    getCurrentLocation
  };
};
```

#### Cache Service Hook
```jsx
{% raw %}
// src/services/cacheService.js
class CacheService {
  constructor() {
    this.cache = new Map();
    this.defaultTTL = 10 * 60 * 1000; // 10 minutes
  }

  set(key, data, ttl = this.defaultTTL) {
    const item = {
      data,
      timestamp: Date.now(),
      ttl
    };
    
    this.cache.set(key, item);
    
    // Also save to localStorage for persistence
    try {
      localStorage.setItem(`weather_cache_${key}`, JSON.stringify(item));
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  }

  get(key) {
    let item = this.cache.get(key);
    
    // If not in memory, try localStorage
    if (!item) {
      try {
        const stored = localStorage.getItem(`weather_cache_${key}`);
        if (stored) {
          item = JSON.parse(stored);
          this.cache.set(key, item);
        }
      } catch (error) {
        console.warn('Failed to load from localStorage:', error);
      }
    }

    if (!item) return null;

    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.delete(key);
      return null;
    }

    return item.data;
  }

  delete(key) {
    this.cache.delete(key);
    localStorage.removeItem(`weather_cache_${key}`);
  }

  clear() {
    this.cache.clear();
    // Clear localStorage items
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('weather_cache_')) {
        localStorage.removeItem(key);
      }
    });
  }

  // Clean expired items
  cleanup() {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.delete(key);
      }
    }
  }
}

export const cacheService = new CacheService();

// Cleanup expired items every 5 minutes
setInterval(() => {
  cacheService.cleanup();
}, 5 * 60 * 1000);
{% endraw %}
```

#### Network Status Hook
```jsx
// src/hooks/useNetworkStatus.js
import { useState, useEffect } from 'react';

export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      if (wasOffline) {
        // Trigger data refresh when coming back online
        setWasOffline(false);
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      setWasOffline(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [wasOffline]);

  return { isOnline, wasOffline };
};
```

### 2. Advanced Components

#### Location Search Component
```jsx
// src/components/LocationSearch/LocationSearch.jsx
import React, { useState, useEffect, useRef } from 'react';
import { weatherAPI } from '../../services/weatherAPI';
import { useDebounce } from '../../hooks/useDebounce';
import LocationSuggestions from './LocationSuggestions';
import './LocationSearch.css';

const LocationSearch = ({ onLocationSelect, onUseCurrentLocation }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState(null);
  
  const debouncedQuery = useDebounce(query, 300);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Search for locations when debounced query changes
  useEffect(() => {
    if (debouncedQuery.length >= 3) {
      searchLocations(debouncedQuery);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [debouncedQuery]);

  // Handle clicks outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target) &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const searchLocations = async (searchQuery) => {
    setLoading(true);
    setError(null);

    try {
      const results = await weatherAPI.searchLocations(searchQuery);
      setSuggestions(results);
      setShowSuggestions(results.length > 0);
    } catch (err) {
      setError('Failed to search locations');
      setSuggestions([]);
      setShowSuggestions(false);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    setError(null);
  };

  const handleSuggestionSelect = (location) => {
    setQuery(location.displayName);
    setShowSuggestions(false);
    onLocationSelect(location);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (suggestions.length > 0) {
      handleSuggestionSelect(suggestions[0]);
    }
  };

  const handleCurrentLocationClick = () => {
    setQuery('');
    onUseCurrentLocation();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  return (
    <div className="location-search">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-container">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            placeholder="Search for a city..."
            className="search-input"
          />
          
          {loading && <div className="search-loading">🔄</div>}
          
          <button
            type="button"
            onClick={handleCurrentLocationClick}
            className="current-location-btn"
            title="Use current location"
          >
            📍
          </button>
        </div>

        {error && <div className="search-error">{error}</div>}

        {showSuggestions && suggestions.length > 0 && (
          <LocationSuggestions
            ref={suggestionsRef}
            suggestions={suggestions}
            onSelect={handleSuggestionSelect}
            query={query}
          />
        )}
      </form>
    </div>
  );
};

export default LocationSearch;
```

#### Location Suggestions Component
```jsx
{% raw %}
// src/components/LocationSearch/LocationSuggestions.jsx
import React, { forwardRef } from 'react';
import './LocationSuggestions.css';

const LocationSuggestions = forwardRef(({ suggestions, onSelect, query }, ref) => {
  const highlightText = (text, highlight) => {
    if (!highlight) return text;
    
    const parts = text.split(new RegExp(`(${highlight})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === highlight.toLowerCase() ? (
        <mark key={index}>{part}</mark>
      ) : (
        part
      )
    );
  };

  return (
    <div ref={ref} className="location-suggestions">
      {suggestions.map((location, index) => (
        <button
          key={`${location.coords.lat}-${location.coords.lon}`}
          onClick={() => onSelect(location)}
          className="suggestion-item"
        >
          <div className="suggestion-name">
            {highlightText(location.displayName, query)}
          </div>
          <div className="suggestion-coords">
            {location.coords.lat.toFixed(2)}, {location.coords.lon.toFixed(2)}
          </div>
        </button>
      ))}
    </div>
  );
});

LocationSuggestions.displayName = 'LocationSuggestions';

export default LocationSuggestions;
{% endraw %}
```

#### Current Weather Component
```jsx
// src/components/Weather/CurrentWeather.jsx
import React from 'react';
import { format } from 'date-fns';
import { getWeatherIcon, getWindDirection } from '../../utils/weatherHelpers';
import './CurrentWeather.css';

const CurrentWeather = ({ weather }) => {
  const {
    location,
    weather: weatherInfo,
    temperature,
    details,
    sun,
    timestamp
  } = weather;

  return (
    <div className="current-weather">
      <div className="weather-header">
        <div className="location-info">
          <h2>{location.name}, {location.country}</h2>
          <p className="last-updated">
            Last updated: {format(new Date(timestamp), 'MMM dd, HH:mm')}
          </p>
        </div>
        
        <div className="weather-icon">
          {getWeatherIcon(weatherInfo.icon, 'large')}
        </div>
      </div>

      <div className="weather-main">
        <div className="temperature-section">
          <div className="current-temp">
            {temperature.current}°C
          </div>
          <div className="temp-description">
            <div className="weather-description">
              {weatherInfo.description}
            </div>
            <div className="feels-like">
              Feels like {temperature.feelsLike}°C
            </div>
            <div className="temp-range">
              {temperature.min}° / {temperature.max}°
            </div>
          </div>
        </div>

        <div className="weather-details">
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">💧 Humidity</span>
              <span className="detail-value">{details.humidity}%</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">🌪️ Wind</span>
              <span className="detail-value">
                {details.windSpeed} m/s {getWindDirection(details.windDirection)}
              </span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">📊 Pressure</span>
              <span className="detail-value">{details.pressure} hPa</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">👁️ Visibility</span>
              <span className="detail-value">{details.visibility} km</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">☁️ Cloudiness</span>
              <span className="detail-value">{details.cloudiness}%</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">🌅 Sunrise</span>
              <span className="detail-value">
                {format(new Date(sun.sunrise), 'HH:mm')}
              </span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">🌇 Sunset</span>
              <span className="detail-value">
                {format(new Date(sun.sunset), 'HH:mm')}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurrentWeather;
```

#### Weather Forecast Component
```jsx
{% raw %}
// src/components/Weather/WeatherForecast.jsx
import React, { useState } from 'react';
import { format, isSameDay } from 'date-fns';
import { getWeatherIcon } from '../../utils/weatherHelpers';
import './WeatherForecast.css';

const WeatherForecast = ({ forecast }) => {
  const [selectedDay, setSelectedDay] = useState(0);

  // Group forecasts by day
  const dailyForecasts = forecast.forecasts.reduce((acc, item) => {
    const date = new Date(item.datetime);
    const dateKey = format(date, 'yyyy-MM-dd');
    
    if (!acc[dateKey]) {
      acc[dateKey] = {
        date: date,
        forecasts: []
      };
    }
    
    acc[dateKey].forecasts.push(item);
    return acc;
  }, {});

  const days = Object.values(dailyForecasts).slice(0, 7); // Next 7 days

  // Get daily summary (min/max temp, most common weather)
  const getDailySummary = (dayForecasts) => {
    const temps = dayForecasts.map(f => f.temperature.current);
    const weatherCounts = {};
    
    dayForecasts.forEach(f => {
      const weather = f.weather.main;
      weatherCounts[weather] = (weatherCounts[weather] || 0) + 1;
    });
    
    const mostCommonWeather = Object.keys(weatherCounts).reduce((a, b) => 
      weatherCounts[a] > weatherCounts[b] ? a : b
    );
    
    return {
      minTemp: Math.min(...temps),
      maxTemp: Math.max(...temps),
      weather: dayForecasts.find(f => f.weather.main === mostCommonWeather)?.weather || dayForecasts[0].weather
    };
  };

  const formatDay = (date) => {
    if (isSameDay(date, new Date())) return 'Today';
    if (isSameDay(date, new Date(Date.now() + 86400000))) return 'Tomorrow';
    return format(date, 'EEE');
  };

  return (
    <div className="weather-forecast">
      <h3>7-Day Forecast</h3>
      
      <div className="forecast-tabs">
        {days.map((day, index) => {
          const summary = getDailySummary(day.forecasts);
          
          return (
            <button
              key={format(day.date, 'yyyy-MM-dd')}
              onClick={() => setSelectedDay(index)}
              className={`forecast-tab ${index === selectedDay ? 'active' : ''}`}
            >
              <div className="tab-day">{formatDay(day.date)}</div>
              <div className="tab-date">{format(day.date, 'MMM dd')}</div>
              <div className="tab-icon">
                {getWeatherIcon(summary.weather.icon, 'small')}
              </div>
              <div className="tab-temps">
                <span className="tab-max">{summary.maxTemp}°</span>
                <span className="tab-min">{summary.minTemp}°</span>
              </div>
            </button>
          );
        })}
      </div>

      {days[selectedDay] && (
        <div className="forecast-details">
          <h4>{format(days[selectedDay].date, 'EEEE, MMMM dd')}</h4>
          
          <div className="hourly-forecast">
            {days[selectedDay].forecasts.map((forecast, index) => (
              <div key={index} className="hourly-item">
                <div className="hourly-time">
                  {format(new Date(forecast.datetime), 'HH:mm')}
                </div>
                
                <div className="hourly-icon">
                  {getWeatherIcon(forecast.weather.icon, 'small')}
                </div>
                
                <div className="hourly-temp">
                  {forecast.temperature.current}°C
                </div>
                
                <div className="hourly-desc">
                  {forecast.weather.description}
                </div>
                
                <div className="hourly-details">
                  <div>💧 {forecast.details.humidity}%</div>
                  <div>🌪️ {forecast.details.windSpeed} m/s</div>
                  {forecast.details.precipitation > 0 && (
                    <div>🌧️ {forecast.details.precipitation}mm</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WeatherForecast;
{% endraw %}
```

### 3. Utility Functions

#### Weather Helpers
```jsx
// src/utils/weatherHelpers.js
export const getWeatherIcon = (iconCode, size = 'medium') => {
  const iconMap = {
    '01d': '☀️', // clear sky day
    '01n': '🌙', // clear sky night
    '02d': '⛅', // few clouds day
    '02n': '☁️', // few clouds night
    '03d': '☁️', // scattered clouds
    '03n': '☁️',
    '04d': '☁️', // broken clouds
    '04n': '☁️',
    '09d': '🌦️', // shower rain
    '09n': '🌧️',
    '10d': '🌦️', // rain day
    '10n': '🌧️', // rain night
    '11d': '⛈️', // thunderstorm
    '11n': '⛈️',
    '13d': '🌨️', // snow
    '13n': '🌨️',
    '50d': '🌫️', // mist
    '50n': '🌫️'
  };

  const icon = iconMap[iconCode] || '❓';
  
  const sizeStyles = {
    small: { fontSize: '1.2rem' },
    medium: { fontSize: '2rem' },
    large: { fontSize: '4rem' }
  };

  return <span style={sizeStyles[size]}>{icon}</span>;
};

export const getWindDirection = (degrees) => {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
};

export const getWeatherConditionColor = (weatherMain) => {
  const colorMap = {
    'Clear': '#FFD700',
    'Clouds': '#87CEEB',
    'Rain': '#4682B4',
    'Drizzle': '#6495ED',
    'Thunderstorm': '#483D8B',
    'Snow': '#F0F8FF',
    'Mist': '#D3D3D3',
    'Smoke': '#696969',
    'Haze': '#F5DEB3',
    'Dust': '#DEB887',
    'Fog': '#708090',
    'Sand': '#F4A460',
    'Ash': '#2F4F4F',
    'Squall': '#8B008B',
    'Tornado': '#8B0000'
  };
  
  return colorMap[weatherMain] || '#87CEEB';
};

export const getAirQualityIndex = (aqi) => {
  const levels = [
    { min: 0, max: 50, label: 'Good', color: '#00E400' },
    { min: 51, max: 100, label: 'Moderate', color: '#FFFF00' },
    { min: 101, max: 150, label: 'Unhealthy for Sensitive Groups', color: '#FF7E00' },
    { min: 151, max: 200, label: 'Unhealthy', color: '#FF0000' },
    { min: 201, max: 300, label: 'Very Unhealthy', color: '#8F3F97' },
    { min: 301, max: 500, label: 'Hazardous', color: '#7E0023' }
  ];
  
  return levels.find(level => aqi >= level.min && aqi <= level.max) || levels[0];
};

export const convertTemperature = (celsius, unit) => {
  switch (unit) {
    case 'fahrenheit':
      return Math.round((celsius * 9/5) + 32);
    case 'kelvin':
      return Math.round(celsius + 273.15);
    default:
      return Math.round(celsius);
  }
};

export const formatPressure = (pressure, unit = 'hPa') => {
  switch (unit) {
    case 'inHg':
      return (pressure * 0.02953).toFixed(2);
    case 'mmHg':
      return (pressure * 0.75006).toFixed(0);
    default:
      return pressure;
  }
};
```

### 4. Styling

#### Main App Styles
```css
/* src/components/WeatherApp.css */
.weather-app {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 20px;
}

.weather-header {
  text-align: center;
  margin-bottom: 30px;
}

.weather-header h1 {
  font-size: 2.5rem;
  margin-bottom: 20px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.weather-main {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (max-width: 768px) {
  .weather-app {
    padding: 10px;
  }
  
  .weather-header h1 {
    font-size: 2rem;
  }
}
```

#### Location Search Styles
```css
/* src/components/LocationSearch/LocationSearch.css */
.location-search {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  position: relative;
}

.search-form {
  position: relative;
}

.search-input-container {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 25px;
  padding: 5px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  position: relative;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 20px;
  color: #333;
  background: transparent;
}

.search-input::placeholder {
  color: #999;
}

.search-loading {
  padding: 10px;
  color: #666;
  animation: spin 1s linear infinite;
}

.current-location-btn {
  background: #74b9ff;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 16px;
}

.current-location-btn:hover {
  background: #0984e3;
  transform: scale(1.05);
}

.search-error {
  color: #ff6b6b;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
  background: rgba(255, 107, 107, 0.1);
  padding: 8px;
  border-radius: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

#### Location Suggestions Styles
```css
/* src/components/LocationSearch/LocationSuggestions.css */
.location-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  z-index: 1000;
  margin-top: 5px;
  overflow: hidden;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  width: 100%;
  padding: 15px 20px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.suggestion-item:hover {
  background-color: #f8f9fa;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.suggestion-name mark {
  background-color: #74b9ff;
  color: white;
  padding: 2px 4px;
  border-radius: 3px;
}

.suggestion-coords {
  font-size: 12px;
  color: #666;
}
```

#### Current Weather Styles
```css
/* src/components/Weather/CurrentWeather.css */
.current-weather {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.location-info h2 {
  font-size: 1.8rem;
  margin: 0 0 5px 0;
  font-weight: 600;
}

.last-updated {
  font-size: 14px;
  opacity: 0.7;
  margin: 0;
}

.weather-icon {
  font-size: 4rem;
}

.weather-main {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
  align-items: start;
}

.temperature-section {
  text-align: center;
}

.current-temp {
  font-size: 4rem;
  font-weight: 300;
  line-height: 1;
  margin-bottom: 10px;
}

.weather-description {
  font-size: 1.2rem;
  text-transform: capitalize;
  margin-bottom: 5px;
}

.feels-like {
  font-size: 1rem;
  opacity: 0.8;
  margin-bottom: 10px;
}

.temp-range {
  font-size: 1.1rem;
  opacity: 0.9;
}

.weather-details {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-label {
  font-size: 14px;
  opacity: 0.8;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .current-weather {
    padding: 20px;
  }
  
  .weather-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 15px;
  }
  
  .weather-main {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .current-temp {
    font-size: 3rem;
  }
  
  .detail-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

#### Weather Forecast Styles
```css
/* src/components/Weather/WeatherForecast.css */
.weather-forecast {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.weather-forecast h3 {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.forecast-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.forecast-tab {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 15px;
  min-width: 120px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
  text-align: center;
}

.forecast-tab:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.forecast-tab.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.tab-day {
  font-weight: 600;
  margin-bottom: 5px;
}

.tab-date {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 10px;
}

.tab-icon {
  margin-bottom: 10px;
}

.tab-temps {
  display: flex;
  justify-content: space-between;
}

.tab-max {
  font-weight: 600;
}

.tab-min {
  opacity: 0.7;
}

.forecast-details {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
}

.forecast-details h4 {
  margin: 0 0 20px 0;
  font-size: 1.2rem;
}

.hourly-forecast {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.hourly-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 15px;
  text-align: center;
  transition: all 0.2s ease;
}

.hourly-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.hourly-time {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
}

.hourly-icon {
  margin-bottom: 8px;
}

.hourly-temp {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 5px;
}

.hourly-desc {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 10px;
  text-transform: capitalize;
}

.hourly-details {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 11px;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .weather-forecast {
    padding: 20px;
  }
  
  .forecast-tabs {
    gap: 5px;
  }
  
  .forecast-tab {
    min-width: 100px;
    padding: 10px;
  }
  
  .hourly-forecast {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
  }
}
```

---

## 🧪 Testing the Implementation

### Test Checklist
- [ ] **API Integration**: Weather data loads correctly from OpenWeatherMap
- [ ] **Error Handling**: Network errors and API errors are handled gracefully
- [ ] **Geolocation**: Current location detection works
- [ ] **Location Search**: Search autocomplete works with debouncing
- [ ] **Caching**: Data is cached and loaded from cache when available
- [ ] **Offline Support**: App works with cached data when offline
- [ ] **Responsive Design**: UI adapts to different screen sizes
- [ ] **Loading States**: Loading indicators show during API calls
- [ ] **Forecast Display**: 7-day forecast displays correctly
- [ ] **Weather Icons**: Icons match weather conditions
- [ ] **Temperature Units**: Temperature displays in correct units
- [ ] **Performance**: App loads quickly with proper optimization

### API Testing
```jsx
// Test API endpoints manually
const testWeatherAPI = async () => {
  try {
    // Test current weather
    const weather = await weatherAPI.getCurrentWeather(40.7128, -74.0060); // New York
    console.log('Current weather:', weather);
    
    // Test forecast
    const forecast = await weatherAPI.getForecast(40.7128, -74.0060);
    console.log('Forecast:', forecast);
    
    // Test location search
    const locations = await weatherAPI.searchLocations('New York');
    console.log('Locations:', locations);
    
  } catch (error) {
    console.error('API test failed:', error);
  }
};
```

---

## 🔧 Troubleshooting

### Common Issues

**1. API Key not working**
```env
# Make sure .env file is in project root
REACT_APP_WEATHER_API_KEY=your_actual_api_key_here

# Restart development server after adding .env
npm start
```

**2. CORS errors**
```jsx
// OpenWeatherMap API should work from browser, but if you get CORS errors:
// Option 1: Use a proxy in package.json
"proxy": "https://api.openweathermap.org"

// Option 2: Use a CORS proxy service (not recommended for production)
const PROXY_URL = 'https://cors-anywhere.herokuapp.com/';
const API_URL = PROXY_URL + 'https://api.openweathermap.org/data/2.5/weather';
```

**3. Location permission denied**
```jsx
// Handle geolocation permission gracefully
const handleLocationError = (error) => {
  switch (error.code) {
    case error.PERMISSION_DENIED:
      setError('Location access denied. Please search for a city manually.');
      break;
    case error.POSITION_UNAVAILABLE:
      setError('Location information is unavailable. Using default location.');
      break;
    default:
      setError('An error occurred while retrieving location.');
  }
};
```

**4. API rate limiting**
```jsx
// Implement exponential backoff
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
};
```

**5. Cache not working**
```jsx
// Check localStorage availability
const isLocalStorageAvailable = () => {
  try {
    localStorage.setItem('test', 'test');
    localStorage.removeItem('test');
    return true;
  } catch {
    return false;
  }
};
```

---

## 🎓 Learning Objectives

### API Integration Mastery
- ✅ **HTTP Client Setup**: Configuring axios with interceptors and error handling
- ✅ **Data Transformation**: Converting API responses to application format
- ✅ **Error Handling**: Graceful handling of network and API errors
- ✅ **Retry Logic**: Implementing exponential backoff for failed requests

### Advanced Data Fetching
- ✅ **Caching Strategies**: Implementing memory and localStorage caching
- ✅ **Loading States**: Managing loading indicators and skeleton screens
- ✅ **Optimistic Updates**: Providing immediate feedback while requests complete
- ✅ **Debouncing**: Optimizing search requests with debounced input

### Performance Optimization
- ✅ **Request Deduplication**: Preventing duplicate API calls
- ✅ **Data Normalization**: Organizing API responses efficiently
- ✅ **Lazy Loading**: Loading components only when needed
- ✅ **Memory Management**: Proper cleanup of timeouts and intervals

### User Experience
- ✅ **Offline Support**: Handling network connectivity issues
- ✅ **Progressive Enhancement**: Working without JavaScript features
- ✅ **Accessibility**: Screen reader support and keyboard navigation
- ✅ **Responsive Design**: Adapting to different screen sizes

---

## 🚀 Next Steps

1. **Add More Weather Data**: Air quality, UV index, weather alerts
2. **Implement Maps**: Interactive weather maps with overlays
3. **Add Notifications**: Weather alerts and push notifications
4. **Historical Data**: Show weather history and trends
5. **Weather Widgets**: Customizable dashboard widgets
6. **Social Features**: Share weather updates and photos
7. **Weather Radar**: Animated radar and satellite imagery
8. **Multi-language Support**: Internationalization for global users

This implementation demonstrates advanced API integration patterns and provides a solid foundation for building data-driven applications with external APIs.
