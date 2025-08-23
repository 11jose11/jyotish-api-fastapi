# 🌟 Frontend Integration Guide - Jyotiṣa API

## 📋 Overview

This guide explains how to integrate the Jyotiṣa API with your frontend application for displaying panchanga calendars and yogas.

## 🔧 CORS Configuration

The API is configured with comprehensive CORS support for frontend integration:

### Allowed Origins
- `http://localhost:3000` (React/Next.js default)
- `http://localhost:3001` (Alternative React port)
- `http://localhost:5173` (Vite default)
- `http://localhost:8080` (Alternative dev port)
- HTTPS versions of all above
- `127.0.0.1` equivalents

### Allowed Methods
- GET, POST, PUT, DELETE, OPTIONS, PATCH

### Allowed Headers
- Content-Type, Authorization, X-API-Key, Origin, etc.

## 🚀 Quick Start

### 1. Basic API Client Setup

```javascript
// Create API client
const api = new JyotishAPIClient('http://localhost:8000');

// Test connection
const info = await api.getApiInfo();
console.log('API Info:', info);
```

### 2. Get Panchanga for a Date

```javascript
// Get panchanga for Marseille, France
const panchanga = await api.getPanchanga(
    '2024-12-19',  // date
    43.297,        // latitude
    5.3811,        // longitude
    0,             // altitude
    'sunrise'      // reference time
);

console.log('Panchanga:', panchanga);
```

### 3. Calendar Integration

```javascript
const calendar = new JyotishCalendar(api);
calendar.setLocation(43.297, 5.3811); // Marseille

// Get today's panchanga
const today = new Date();
const todayPanchanga = await calendar.getDatePanchanga(today);
const formatted = calendar.formatPanchangaForDisplay(todayPanchanga);
```

## 📅 Calendar Display Examples

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

function PanchangaCalendar({ date, latitude, longitude }) {
    const [panchanga, setPanchanga] = useState(null);
    const [loading, setLoading] = useState(true);
    
    const api = new JyotishAPIClient();
    
    useEffect(() => {
        async function fetchPanchanga() {
            try {
                const data = await api.getPanchanga(
                    date.toISOString().split('T')[0],
                    latitude,
                    longitude
                );
                setPanchanga(data);
            } catch (error) {
                console.error('Error:', error);
            } finally {
                setLoading(false);
            }
        }
        
        fetchPanchanga();
    }, [date, latitude, longitude]);
    
    if (loading) return <div>Loading panchanga...</div>;
    if (!panchanga) return <div>No data available</div>;
    
    return (
        <div className="panchanga-calendar">
            <h3>Panchanga for {panchanga.date}</h3>
            <div className="panchanga-grid">
                <div className="element">
                    <strong>Tithi:</strong> {panchanga.panchanga.tithi.display}
                    <div className="percentage">
                        {panchanga.panchanga.tithi.percentage_remaining}% remaining
                    </div>
                </div>
                <div className="element">
                    <strong>Nakshatra:</strong> {panchanga.panchanga.nakshatra.name}
                    <div className="pada">Pada {panchanga.panchanga.nakshatra.pada}</div>
                </div>
                <div className="element">
                    <strong>Yoga:</strong> {panchanga.panchanga.yoga.name}
                </div>
                <div className="element">
                    <strong>Vara:</strong> {panchanga.panchanga.vara.name}
                </div>
            </div>
        </div>
    );
}
```

### Vue.js Component Example

```vue
<template>
    <div class="panchanga-display">
        <div v-if="loading">Loading panchanga...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else-if="panchanga" class="panchanga-content">
            <h3>Panchanga for {{ panchanga.date }}</h3>
            <div class="elements">
                <div class="element">
                    <strong>Tithi:</strong> {{ panchanga.panchanga.tithi.display }}
                    <div class="percentage">
                        {{ panchanga.panchanga.tithi.percentage_remaining }}% remaining
                    </div>
                </div>
                <div class="element">
                    <strong>Nakshatra:</strong> {{ panchanga.panchanga.nakshatra.name }}
                    <div class="pada">Pada {{ panchanga.panchanga.nakshatra.pada }}</div>
                </div>
                <div class="element">
                    <strong>Yoga:</strong> {{ panchanga.panchanga.yoga.name }}
                </div>
                <div class="element">
                    <strong>Vara:</strong> {{ panchanga.panchanga.vara.name }}
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { JyotishAPIClient } from './jyotish-api-client.js';

export default {
    name: 'PanchangaDisplay',
    props: {
        date: {
            type: Date,
            required: true
        },
        latitude: {
            type: Number,
            required: true
        },
        longitude: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            panchanga: null,
            loading: true,
            error: null,
            api: new JyotishAPIClient()
        };
    },
    async mounted() {
        await this.fetchPanchanga();
    },
    methods: {
        async fetchPanchanga() {
            try {
                this.loading = true;
                this.error = null;
                
                const data = await this.api.getPanchanga(
                    this.date.toISOString().split('T')[0],
                    this.latitude,
                    this.longitude
                );
                
                this.panchanga = data;
            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        }
    },
    watch: {
        date() {
            this.fetchPanchanga();
        },
        latitude() {
            this.fetchPanchanga();
        },
        longitude() {
            this.fetchPanchanga();
        }
    }
};
</script>
```

## 🎨 CSS Styling Examples

### Basic Panchanga Display

```css
.panchanga-calendar {
    font-family: 'Arial', sans-serif;
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.panchanga-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.element {
    background: white;
    padding: 15px;
    border-radius: 6px;
    border-left: 4px solid #4CAF50;
}

.element strong {
    color: #333;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.percentage {
    font-size: 12px;
    color: #666;
    margin-top: 5px;
}

.pada {
    font-size: 12px;
    color: #888;
    margin-top: 3px;
}
```

### Calendar Grid Style

```css
.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;
    background: #ddd;
    padding: 2px;
    border-radius: 8px;
}

.calendar-day {
    background: white;
    padding: 10px;
    min-height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.calendar-day:hover {
    background: #f0f0f0;
}

.day-number {
    font-weight: bold;
    font-size: 16px;
}

.panchanga-info {
    font-size: 10px;
    color: #666;
}

.tithi {
    color: #2196F3;
    font-weight: 500;
}

.nakshatra {
    color: #4CAF50;
    font-weight: 500;
}
```

## 🔍 API Endpoints for Calendar

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/panchanga/precise/daily` | GET | Get panchanga for a specific date |
| `/v1/panchanga/precise/ayanamsa` | GET | Get ayanamsa information |
| `/v1/ephemeris/planets` | GET | Get planetary positions |
| `/v1/yogas` | GET | Get yogas information |
| `/info` | GET | Get API information |

### Example Requests

```javascript
// Get monthly panchanga data
async function getMonthlyPanchanga(year, month, lat, lng) {
    const daysInMonth = new Date(year, month, 0).getDate();
    const panchangaData = [];
    
    for (let day = 1; day <= daysInMonth; day++) {
        const date = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        const panchanga = await api.getPanchanga(date, lat, lng);
        panchangaData.push({ date, panchanga });
    }
    
    return panchangaData;
}

// Get yogas for a date range
async function getYogasForRange(startDate, endDate, lat, lng) {
    const yogas = [];
    const current = new Date(startDate);
    const end = new Date(endDate);
    
    while (current <= end) {
        const date = current.toISOString().split('T')[0];
        const yoga = await api.getYogas(date, lat, lng);
        yogas.push({ date, yoga });
        current.setDate(current.getDate() + 1);
    }
    
    return yogas;
}
```

## 🛠️ Error Handling

### CORS Errors
If you encounter CORS errors:

1. **Check origin**: Ensure your frontend URL is in the allowed origins list
2. **Check headers**: Verify you're using the correct headers
3. **Check credentials**: Set `credentials: 'include'` if needed

### API Errors
```javascript
try {
    const panchanga = await api.getPanchanga(date, lat, lng);
} catch (error) {
    if (error.message.includes('CORS')) {
        console.error('CORS error - check origin configuration');
    } else if (error.message.includes('401')) {
        console.error('Authentication required');
    } else {
        console.error('API error:', error.message);
    }
}
```

## 📱 Mobile Considerations

### Responsive Design
```css
@media (max-width: 768px) {
    .panchanga-grid {
        grid-template-columns: 1fr;
    }
    
    .calendar-grid {
        grid-template-columns: repeat(7, 1fr);
        font-size: 12px;
    }
    
    .calendar-day {
        min-height: 60px;
        padding: 5px;
    }
}
```

### Touch-Friendly Interface
```css
.calendar-day {
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
}

.calendar-day:active {
    background: #e0e0e0;
}
```

## 🔒 Security Considerations

### API Key Authentication
```javascript
// Set API key if required
api.setApiKey('your-api-key-here');

// The API key will be automatically included in all requests
const panchanga = await api.getPanchanga(date, lat, lng);
```

### Rate Limiting
The API includes rate limiting. Handle 429 responses:

```javascript
try {
    const data = await api.getPanchanga(date, lat, lng);
} catch (error) {
    if (error.message.includes('429')) {
        // Rate limited - wait and retry
        await new Promise(resolve => setTimeout(resolve, 1000));
        const data = await api.getPanchanga(date, lat, lng);
    }
}
```

## 🚀 Performance Optimization

### Caching
```javascript
// Simple in-memory cache
const cache = new Map();

async function getPanchangaWithCache(date, lat, lng) {
    const key = `${date}-${lat}-${lng}`;
    
    if (cache.has(key)) {
        return cache.get(key);
    }
    
    const panchanga = await api.getPanchanga(date, lat, lng);
    cache.set(key, panchanga);
    
    return panchanga;
}
```

### Batch Requests
```javascript
// Request multiple dates at once
async function getBatchPanchanga(dates, lat, lng) {
    const promises = dates.map(date => 
        api.getPanchanga(date, lat, lng)
    );
    
    return Promise.all(promises);
}
```

## 📞 Support

For issues with frontend integration:

1. Check the API health: `GET /health`
2. Verify CORS configuration: `GET /info`
3. Test with curl: `curl -H "Origin: http://localhost:3000" http://localhost:8000/v1/panchanga/precise/daily`
4. Check browser console for CORS errors

## 🎯 Next Steps

1. **Implement the API client** in your frontend
2. **Create calendar components** for panchanga display
3. **Add location selection** for different cities
4. **Implement caching** for better performance
5. **Add error handling** and loading states
6. **Style your components** for a great user experience

---

**Happy coding! 🌟**

Your Jyotiṣa API is now ready for seamless frontend integration with comprehensive CORS support and detailed panchanga data.
