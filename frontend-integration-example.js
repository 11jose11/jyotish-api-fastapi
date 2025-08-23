/**
 * Frontend Integration Example for Jyotiṣa API
 * 
 * This file shows how to integrate with the Jyotiṣa API from your frontend
 * for calendar and panchanga display.
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change to your API URL
const API_VERSION = 'v1';

// API Client Class
class JyotishAPIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
        this.apiKey = null; // Set if you have API key authentication
    }

    // Set API key for authentication
    setApiKey(apiKey) {
        this.apiKey = apiKey;
    }

    // Generic request method with CORS handling
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        };

        // Add API key if available
        if (this.apiKey) {
            defaultHeaders['X-API-Key'] = this.apiKey;
        }

        const config = {
            method: 'GET',
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
            credentials: 'include', // Include cookies if needed
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Get API information
    async getApiInfo() {
        return this.request('/info');
    }

    // Get ayanamsa information
    async getAyanamsa(date, time = '12:00:00') {
        return this.request(`/${API_VERSION}/panchanga/precise/ayanamsa?date=${date}&time=${time}`);
    }

    // Get precise panchanga for a date and location
    async getPanchanga(date, latitude, longitude, altitude = 0, referenceTime = 'sunrise') {
        const params = new URLSearchParams({
            date,
            latitude: latitude.toString(),
            longitude: longitude.toString(),
            altitude: altitude.toString(),
            reference_time: referenceTime
        });
        
        return this.request(`/${API_VERSION}/panchanga/precise/daily?${params}`);
    }

    // Get planetary positions
    async getPlanetaryPositions(whenUTC, planets = 'Sun,Moon,Mercury,Venus,Mars,Jupiter,Saturn,Rahu,Ketu') {
        const params = new URLSearchParams({
            when_utc: whenUTC,
            planets
        });
        
        return this.request(`/${API_VERSION}/ephemeris/planets?${params}`);
    }

    // Get sunrise/sunset times
    async getSunriseSunset(date, latitude, longitude, altitude = 0) {
        const params = new URLSearchParams({
            date,
            latitude: latitude.toString(),
            longitude: longitude.toString(),
            altitude: altitude.toString()
        });
        
        const [sunrise, sunset] = await Promise.all([
            this.request(`/${API_VERSION}/panchanga/precise/sunrise?${params}`),
            this.request(`/${API_VERSION}/panchanga/precise/sunset?${params}`)
        ]);
        
        return { sunrise, sunset };
    }

    // Get yogas information
    async getYogas(date, latitude, longitude) {
        const params = new URLSearchParams({
            date,
            latitude: latitude.toString(),
            longitude: longitude.toString()
        });
        
        return this.request(`/${API_VERSION}/yogas?${params}`);
    }
}

// Calendar Integration Example
class JyotishCalendar {
    constructor(apiClient) {
        this.api = apiClient;
        this.currentDate = new Date();
        this.selectedLocation = {
            latitude: 43.297,  // Marseille, France
            longitude: 5.3811,
            altitude: 0
        };
    }

    // Set location for calculations
    setLocation(latitude, longitude, altitude = 0) {
        this.selectedLocation = { latitude, longitude, altitude };
    }

    // Get panchanga for a specific date
    async getDatePanchanga(date) {
        const dateStr = date.toISOString().split('T')[0];
        
        try {
            const panchanga = await this.api.getPanchanga(
                dateStr,
                this.selectedLocation.latitude,
                this.selectedLocation.longitude,
                this.selectedLocation.altitude
            );
            
            return panchanga;
        } catch (error) {
            console.error('Failed to get panchanga:', error);
            return null;
        }
    }

    // Get monthly panchanga data
    async getMonthlyPanchanga(year, month) {
        const daysInMonth = new Date(year, month, 0).getDate();
        const panchangaData = [];
        
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month - 1, day);
            const panchanga = await this.getDatePanchanga(date);
            
            if (panchanga) {
                panchangaData.push({
                    date: date.toISOString().split('T')[0],
                    panchanga
                });
            }
        }
        
        return panchangaData;
    }

    // Format panchanga for display
    formatPanchangaForDisplay(panchanga) {
        if (!panchanga) return null;
        
        const { tithi, nakshatra, yoga, karana, vara } = panchanga.panchanga;
        
        return {
            date: panchanga.date,
            sunrise: panchanga.sunrise_time,
            sunset: panchanga.sunset_time,
            tithi: {
                name: tithi.name,
                display: tithi.display,
                percentage: tithi.percentage_remaining
            },
            nakshatra: {
                name: nakshatra.name,
                pada: nakshatra.pada,
                percentage: nakshatra.percentage_remaining
            },
            yoga: {
                name: yoga.name,
                percentage: yoga.percentage_remaining
            },
            karana: {
                name: karana.name,
                percentage: karana.percentage_remaining
            },
            vara: vara.name
        };
    }
}

// Usage Examples

// 1. Basic API Usage
async function basicUsage() {
    const api = new JyotishAPIClient();
    
    try {
        // Get API info
        const info = await api.getApiInfo();
        console.log('API Info:', info);
        
        // Get ayanamsa
        const ayanamsa = await api.getAyanamsa('2024-12-19', '08:05:56');
        console.log('Ayanamsa:', ayanamsa);
        
        // Get panchanga for Marseille
        const panchanga = await api.getPanchanga('2024-12-19', 43.297, 5.3811);
        console.log('Panchanga:', panchanga);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// 2. Calendar Integration
async function calendarIntegration() {
    const api = new JyotishAPIClient();
    const calendar = new JyotishCalendar(api);
    
    // Set location (Marseille, France)
    calendar.setLocation(43.297, 5.3811);
    
    try {
        // Get today's panchanga
        const today = new Date();
        const todayPanchanga = await calendar.getDatePanchanga(today);
        const formatted = calendar.formatPanchangaForDisplay(todayPanchanga);
        
        console.log('Today\'s Panchanga:', formatted);
        
        // Get monthly data (example for December 2024)
        const monthlyData = await calendar.getMonthlyPanchanga(2024, 12);
        console.log('Monthly Panchanga Data:', monthlyData);
        
    } catch (error) {
        console.error('Calendar Error:', error);
    }
}

// 3. React/Vue Integration Example
function ReactComponentExample() {
    return `
    // React Component Example
    import React, { useState, useEffect } from 'react';
    
    function JyotishCalendar({ date, latitude, longitude }) {
        const [panchanga, setPanchanga] = useState(null);
        const [loading, setLoading] = useState(true);
        const [error, setError] = useState(null);
        
        const api = new JyotishAPIClient();
        
        useEffect(() => {
            async function fetchPanchanga() {
                try {
                    setLoading(true);
                    const data = await api.getPanchanga(
                        date.toISOString().split('T')[0],
                        latitude,
                        longitude
                    );
                    setPanchanga(data);
                } catch (err) {
                    setError(err.message);
                } finally {
                    setLoading(false);
                }
            }
            
            fetchPanchanga();
        }, [date, latitude, longitude]);
        
        if (loading) return <div>Loading panchanga...</div>;
        if (error) return <div>Error: {error}</div>;
        if (!panchanga) return <div>No data available</div>;
        
        return (
            <div className="panchanga-display">
                <h3>Panchanga for {panchanga.date}</h3>
                <div className="panchanga-elements">
                    <div className="element">
                        <strong>Tithi:</strong> {panchanga.panchanga.tithi.display} 
                        ({panchanga.panchanga.tithi.percentage_remaining}% remaining)
                    </div>
                    <div className="element">
                        <strong>Nakshatra:</strong> {panchanga.panchanga.nakshatra.name} 
                        Pada {panchanga.panchanga.nakshatra.pada}
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
    `;
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { JyotishAPIClient, JyotishCalendar };
}

// Auto-run examples if in browser
if (typeof window !== 'undefined') {
    console.log('Jyotiṣa API Frontend Integration Examples');
    console.log('Run basicUsage() or calendarIntegration() to test');
    
    // Make functions globally available
    window.JyotishAPIClient = JyotishAPIClient;
    window.JyotishCalendar = JyotishCalendar;
    window.basicUsage = basicUsage;
    window.calendarIntegration = calendarIntegration;
}
