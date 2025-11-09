"""
Real-time Air Quality API Integration
Fetches live air pollution data from OpenWeatherMap Air Pollution API
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

class AirQualityAPI:
    """Interface for real-time air quality data from OpenWeatherMap"""
    
    # WHO Air Quality Guidelines (2021)
    WHO_PM25_ANNUAL = 5  # μg/m³
    WHO_PM25_24H = 15    # μg/m³
    WHO_PM10_ANNUAL = 15  # μg/m³
    WHO_PM10_24H = 45     # μg/m³
    WHO_NO2_ANNUAL = 10   # μg/m³
    WHO_SO2_24H = 40      # μg/m³
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            api_key: OpenWeatherMap API key. If None, will look for OPENWEATHER_API_KEY env var
                    If not found, will use demo mode with simulated data
        """
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY', 'DEMO_MODE')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.demo_mode = self.api_key == 'DEMO_MODE'
        
        if self.demo_mode:
            print("⚠️  Running in DEMO MODE - Using simulated data")
            print("   To use real data, set OPENWEATHER_API_KEY environment variable")
    
    def geocode_city(self, city_name: str, country_code: Optional[str] = None) -> Optional[Dict]:
        """
        Get coordinates for a city name
        
        Args:
            city_name: Name of the city (e.g., "London", "New York")
            country_code: Optional ISO 3166 country code (e.g., "GB", "US")
        
        Returns:
            Dictionary with lat, lon, name, country or None if not found
        """
        if self.demo_mode:
            return self._demo_geocode(city_name)
        
        try:
            query = f"{city_name}"
            if country_code:
                query += f",{country_code}"
            
            url = f"{self.base_url}/weather"
            params = {
                'q': query,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon'],
                    'name': data['name'],
                    'country': data['sys']['country']
                }
            else:
                print(f"Geocoding error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error geocoding city: {e}")
            return None
    
    def get_current_air_quality(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current air quality data for coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dictionary with air quality data or None if error
        """
        if self.demo_mode:
            return self._demo_air_quality(lat, lon)
        
        try:
            url = f"{self.base_url}/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_air_quality_response(data)
            else:
                print(f"Air quality API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching air quality: {e}")
            return None
    
    def get_air_quality_forecast(self, lat: float, lon: float) -> Optional[List[Dict]]:
        """
        Get air quality forecast for next 5 days
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            List of air quality forecasts or None if error
        """
        if self.demo_mode:
            return self._demo_forecast(lat, lon)
        
        try:
            url = f"{self.base_url}/air_pollution/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                for item in data.get('list', []):
                    forecasts.append(self._parse_forecast_item(item))
                return forecasts
            else:
                print(f"Forecast API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def search_city_by_location(self, city_name: str, country_code: Optional[str] = None) -> Optional[Dict]:
        """
        Search for a city and get its current air quality
        
        Args:
            city_name: Name of the city
            country_code: Optional country code
        
        Returns:
            Complete air quality data including location info
        """
        # First geocode the city
        location = self.geocode_city(city_name, country_code)
        
        if not location:
            return None
        
        # Get air quality for the location
        air_quality = self.get_current_air_quality(location['lat'], location['lon'])
        
        if not air_quality:
            return None
        
        # Combine location and air quality data
        return {
            'location': location,
            'air_quality': air_quality,
            'timestamp': datetime.now().isoformat()
        }
    
    def _parse_air_quality_response(self, data: Dict) -> Dict:
        """Parse OpenWeatherMap air quality response"""
        if not data.get('list'):
            return None
        
        item = data['list'][0]
        components = item['components']
        aqi = item['main']['aqi']
        
        pm25 = components.get('pm2_5', 0)
        pm10 = components.get('pm10', 0)
        
        return {
            'aqi': aqi,
            'aqi_level': self._get_aqi_level(aqi),
            'pm2_5': pm25,
            'pm10': pm10,
            'no2': components.get('no2', 0),
            'so2': components.get('so2', 0),
            'co': components.get('co', 0),
            'o3': components.get('o3', 0),
            'nh3': components.get('nh3', 0),
            'who_pm25_compliant': pm25 <= self.WHO_PM25_24H,
            'who_pm10_compliant': pm10 <= self.WHO_PM10_24H,
            'timestamp': datetime.fromtimestamp(item['dt']).isoformat()
        }
    
    def _parse_forecast_item(self, item: Dict) -> Dict:
        """Parse a single forecast item"""
        components = item['components']
        aqi = item['main']['aqi']
        
        return {
            'timestamp': datetime.fromtimestamp(item['dt']).isoformat(),
            'aqi': aqi,
            'aqi_level': self._get_aqi_level(aqi),
            'pm2_5': components.get('pm2_5', 0),
            'pm10': components.get('pm10', 0),
            'no2': components.get('no2', 0),
            'so2': components.get('so2', 0)
        }
    
    def _get_aqi_level(self, aqi: int) -> Dict:
        """Get AQI level description and color"""
        levels = {
            1: {'level': 'Good', 'color': '#00e400', 'description': 'Air quality is satisfactory'},
            2: {'level': 'Fair', 'color': '#ffff00', 'description': 'Air quality is acceptable'},
            3: {'level': 'Moderate', 'color': '#ff7e00', 'description': 'Sensitive groups may experience health effects'},
            4: {'level': 'Poor', 'color': '#ff0000', 'description': 'Everyone may begin to experience health effects'},
            5: {'level': 'Very Poor', 'color': '#8f3f97', 'description': 'Health alert: everyone may experience serious effects'}
        }
        return levels.get(aqi, levels[1])
    
    # Demo mode methods for testing without API key
    def _demo_geocode(self, city_name: str) -> Dict:
        """Demo geocoding with common cities"""
        import random
        
        demo_cities = {
            'london': {'lat': 51.5074, 'lon': -0.1278, 'name': 'London', 'country': 'GB'},
            'paris': {'lat': 48.8566, 'lon': 2.3522, 'name': 'Paris', 'country': 'FR'},
            'tokyo': {'lat': 35.6762, 'lon': 139.6503, 'name': 'Tokyo', 'country': 'JP'},
            'new york': {'lat': 40.7128, 'lon': -74.0060, 'name': 'New York', 'country': 'US'},
            'beijing': {'lat': 39.9042, 'lon': 116.4074, 'name': 'Beijing', 'country': 'CN'},
            'delhi': {'lat': 28.6139, 'lon': 77.2090, 'name': 'Delhi', 'country': 'IN'},
            'mumbai': {'lat': 19.0760, 'lon': 72.8777, 'name': 'Mumbai', 'country': 'IN'},
            'sydney': {'lat': -33.8688, 'lon': 151.2093, 'name': 'Sydney', 'country': 'AU'},
            'berlin': {'lat': 52.5200, 'lon': 13.4050, 'name': 'Berlin', 'country': 'DE'},
            'madrid': {'lat': 40.4168, 'lon': -3.7038, 'name': 'Madrid', 'country': 'ES'},
        }
        
        city_lower = city_name.lower()
        if city_lower in demo_cities:
            return demo_cities[city_lower]
        
        # Return a random location for unknown cities
        return {
            'lat': random.uniform(-60, 60),
            'lon': random.uniform(-180, 180),
            'name': city_name.title(),
            'country': 'XX'
        }
    
    def _demo_air_quality(self, lat: float, lon: float) -> Dict:
        """Generate demo air quality data"""
        import random
        
        # Simulate varying air quality
        aqi = random.randint(1, 5)
        pm25 = random.uniform(5, 150) if aqi > 2 else random.uniform(0, 35)
        pm10 = pm25 * random.uniform(1.2, 2.0)
        
        return {
            'aqi': aqi,
            'aqi_level': self._get_aqi_level(aqi),
            'pm2_5': round(pm25, 2),
            'pm10': round(pm10, 2),
            'no2': round(random.uniform(0, 100), 2),
            'so2': round(random.uniform(0, 50), 2),
            'co': round(random.uniform(100, 1000), 2),
            'o3': round(random.uniform(0, 100), 2),
            'nh3': round(random.uniform(0, 20), 2),
            'who_pm25_compliant': pm25 <= self.WHO_PM25_24H,
            'who_pm10_compliant': pm10 <= self.WHO_PM10_24H,
            'timestamp': datetime.now().isoformat()
        }
    
    def _demo_forecast(self, lat: float, lon: float) -> List[Dict]:
        """Generate demo forecast data"""
        import random
        from datetime import timedelta
        
        forecasts = []
        base_time = datetime.now()
        
        for i in range(24):  # 24 hours forecast
            timestamp = base_time + timedelta(hours=i)
            aqi = random.randint(1, 5)
            pm25 = random.uniform(5, 100) if aqi > 2 else random.uniform(0, 35)
            
            forecasts.append({
                'timestamp': timestamp.isoformat(),
                'aqi': aqi,
                'aqi_level': self._get_aqi_level(aqi),
                'pm2_5': round(pm25, 2),
                'pm10': round(pm25 * random.uniform(1.2, 2.0), 2),
                'no2': round(random.uniform(0, 100), 2),
                'so2': round(random.uniform(0, 50), 2)
            })
        
        return forecasts
