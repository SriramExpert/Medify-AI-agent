import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WeatherTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """Get latitude and longitude for a city"""
        geocode_url = f"http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": city,
            "limit": 1,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(geocode_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    "lat": data[0]["lat"],
                    "lon": data[0]["lon"],
                    "city": data[0]["name"],
                    "country": data[0]["country"]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting coordinates for {city}: {e}")
            return None
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city"""
        coords = self.get_coordinates(city)
        if not coords:
            return {"error": f"Could not find city: {city}"}
        
        url = f"{self.base_url}/weather"
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "appid": self.api_key,
            "units": "metric",  # Celsius
            "lang": "en"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._format_current_weather(data, coords["city"])
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return {"error": f"Weather API error: {str(e)}"}
    
    def get_forecast(self, city: str, days: int = 1) -> Dict[str, Any]:
        """Get forecast for specific number of days (up to 5)"""
        coords = self.get_coordinates(city)
        if not coords:
            return {"error": f"Could not find city: {city}"}
        
        url = f"{self.base_url}/forecast"
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8  # 8 forecasts per day
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._format_forecast(data, coords["city"], days)
        except Exception as e:
            logger.error(f"Error getting forecast: {e}")
            return {"error": f"Forecast API error: {str(e)}"}
    
    def get_historical_weather(self, city: str, date: datetime) -> Dict[str, Any]:
        """Get historical weather for a specific date (last 5 days)"""
        coords = self.get_coordinates(city)
        if not coords:
            return {"error": f"Could not find city: {city}"}
        
        # OpenWeatherMap One Call API 3.0 for historical data
        timestamp = int(date.timestamp())
        url = f"{self.base_url}/onecall/timemachine"
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "dt": timestamp,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._format_historical_weather(data, coords["city"], date)
        except Exception as e:
            logger.error(f"Error getting historical weather: {e}")
            return {"error": f"Historical weather not available for {date.strftime('%Y-%m-%d')}"}
    
    def _format_current_weather(self, data: Dict, city: str) -> Dict[str, Any]:
        """Format current weather response"""
        return {
            "city": city,
            "country": data.get("sys", {}).get("country", ""),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "weather": data["weather"][0]["description"].title(),
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg", 0),
            "visibility": data.get("visibility", 0),
            "cloudiness": data["clouds"]["all"],
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
            "timestamp": datetime.fromtimestamp(data["dt"]).isoformat(),
            "request_time": datetime.now().isoformat()
        }
    
    def _format_forecast(self, data: Dict, city: str, days: int) -> Dict[str, Any]:
        """Format forecast response"""
        forecasts = []
        for item in data["list"][:days * 8:8]:  # Get one forecast per day
            forecast = {
                "date": datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d"),
                "time": datetime.fromtimestamp(item["dt"]).strftime("%H:%M"),
                "temperature": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "weather": item["weather"][0]["description"].title(),
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"],
                "probability_of_precipitation": item.get("pop", 0) * 100  # Convert to percentage
            }
            forecasts.append(forecast)
        
        return {
            "city": city,
            "country": data["city"]["country"],
            "forecast_days": days,
            "forecasts": forecasts,
            "request_time": datetime.now().isoformat()
        }
    
    def _format_historical_weather(self, data: Dict, city: str, date: datetime) -> Dict[str, Any]:
        """Format historical weather response"""
        if "current" not in data:
            return {"error": "Historical data not available"}
        
        return {
            "city": city,
            "date": date.strftime("%Y-%m-%d"),
            "temperature": data["current"]["temp"],
            "feels_like": data["current"]["feels_like"],
            "weather": data["current"]["weather"][0]["description"].title(),
            "humidity": data["current"]["humidity"],
            "pressure": data["current"]["pressure"],
            "wind_speed": data["current"]["wind_speed"],
            "request_time": datetime.now().isoformat()
        }