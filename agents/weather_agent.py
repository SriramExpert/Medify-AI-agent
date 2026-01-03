from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import dateparser
import re
from agents.base_agent import BaseAgent
from tools.weather_tool import WeatherTool
import logging

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    """Agent 1: Weather Intelligence Agent"""
    
    def __init__(self, api_key: str):
        super().__init__(name="WeatherAgent", description="Handles weather queries")
        self.weather_tool = WeatherTool(api_key)
        self.city_patterns = [
            r'in\s+([A-Za-z\s]+?)(?:\s+today|\s+tomorrow|\s+yesterday|$)',
            r'weather\s+in\s+([A-Za-z\s]+)',
            r'forecast\s+for\s+([A-Za-z\s]+)'
        ]
    
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        weather_keywords = [
            'weather', 'temperature', 'forecast', 'humidity',
            'rain', 'sunny', 'cloudy', 'wind', 'storm',
            'hot', 'cold', 'degrees', '°c', '°f'
        ]
        
        return any(keyword in query_lower for keyword in weather_keywords)
    
    async def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process weather-related queries"""
        try:
            # Extract city and time information
            city = self._extract_city(query)
            time_info = self._extract_time(query)
            
            if not city:
                return {
                    "success": False,
                    "error": "Please specify a city. Example: 'What is the weather in London?'",
                    "agent": self.name
                }
            
            logger.info(f"Weather query: {query} -> City: {city}, Time: {time_info}")
            
            # Validate API key before making external calls
            if not self.weather_tool.api_key or self.weather_tool.api_key.strip() == "your_openweather_api_key_here":
                return {
                    "success": False,
                    "error": "OpenWeatherMap API key is missing or placeholder. Please set a valid key in .env.",
                    "agent": self.name
                }

            if time_info["type"] == "current" or time_info["type"] == "today":
                result = self.weather_tool.get_current_weather(city)
            elif time_info["type"] == "forecast":
                result = self.weather_tool.get_forecast(city, days=time_info["days"])
            elif time_info["type"] == "historical":
                result = self.weather_tool.get_historical_weather(city, time_info["date"])
            else:
                # Default to current weather
                result = self.weather_tool.get_current_weather(city)
            
            # Format response
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                    "agent": self.name,
                    "query": query
                }
            
            response = self._format_response(result, query, time_info)
            
            return {
                "success": True,
                "data": result,
                "response": response,
                "agent": self.name,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"Error in WeatherAgent: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process weather query: {str(e)}",
                "agent": self.name
            }
    
    def _extract_city(self, query: str) -> Optional[str]:
        """Extract city name from query"""
        query_lower = query.lower()
        
        # Try patterns
        for pattern in self.city_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                if city and len(city) > 1:  # Basic validation
                    return city.title()
        
        # Fallback: look for known city names
        known_cities = [
            'chennai', 'bengaluru', 'bangalore', 'mumbai', 'delhi',
            'london', 'new york', 'paris', 'tokyo', 'sydney',
            'dubai', 'singapore', 'hong kong', 'berlin', 'toronto'
        ]
        
        for city in known_cities:
            if city in query_lower:
                return city.title()
        
        return None
    
    def _extract_time(self, query: str) -> Dict[str, Any]:
        """Extract time reference from query"""
        query_lower = query.lower()
        
        # Check for specific time references
        if "yesterday" in query_lower:
            date = datetime.now() - timedelta(days=1)
            return {
                "type": "historical",
                "date": date,
                "description": "yesterday"
            }
        elif "tomorrow" in query_lower:
            return {
                "type": "forecast",
                "days": 1,
                "description": "tomorrow"
            }
        elif "today" in query_lower or "now" in query_lower:
            return {
                "type": "current",
                "description": "today"
            }
        elif "next week" in query_lower or "coming week" in query_lower:
            return {
                "type": "forecast",
                "days": 7,
                "description": "next week"
            }
        elif "weekend" in query_lower:
            return {
                "type": "forecast",
                "days": 3,
                "description": "weekend"
            }
        
        # Try to parse with dateparser
        parsed_date = dateparser.parse(query_lower, settings={'PREFER_DATES_FROM': 'future'})
        if parsed_date:
            today = datetime.now().date()
            parsed_date_only = parsed_date.date()
            
            if parsed_date_only == today:
                return {"type": "current", "description": "today"}
            elif parsed_date_only == today + timedelta(days=1):
                return {"type": "forecast", "days": 1, "description": "tomorrow"}
            elif parsed_date_only > today:
                days_diff = (parsed_date_only - today).days
                return {"type": "forecast", "days": min(days_diff, 5), "description": parsed_date.strftime("%Y-%m-%d")}
            elif parsed_date_only < today:
                return {"type": "historical", "date": parsed_date, "description": parsed_date.strftime("%Y-%m-%d")}
        
        # Default to current weather
        return {"type": "current", "description": "current"}
    
    def _format_response(self, weather_data: Dict, query: str, time_info: Dict) -> str:
        """Format weather data into natural language response"""
        
        if "forecasts" in weather_data:  # Forecast response
            city = weather_data["city"]
            country = weather_data.get("country", "")
            location = f"{city}, {country}" if country else city
            
            response = f"Weather forecast for {location}:\n\n"
            
            for i, forecast in enumerate(weather_data["forecasts"]):
                response += f"**{forecast['date']}**: {forecast['weather']}, {forecast['temperature']}°C"
                if forecast.get('probability_of_precipitation', 0) > 0:
                    response += f", {forecast['probability_of_precipitation']:.0f}% chance of rain"
                response += "\n"
                
                # Limit to first 3 days for readability
                if i >= 2:
                    break
            
            return response
        
        elif "date" in weather_data and "date" in time_info:  # Historical response
            return (
                f"Weather in {weather_data['city']} on {time_info['description']}:\n"
                f"Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)\n"
                f"Conditions: {weather_data['weather']}\n"
                f"Humidity: {weather_data['humidity']}%\n"
                f"Wind: {weather_data['wind_speed']} m/s"
            )
        
        else:  # Current weather response
            city = weather_data['city']
            country = weather_data.get('country', '')
            location = f"{city}, {country}" if country else city
            
            return (
                f"Current weather in {location}:\n"
                f"Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)\n"
                f"Conditions: {weather_data['weather']}\n"
                f"Humidity: {weather_data['humidity']}%\n"
                f"Wind: {weather_data['wind_speed']} m/s\n"
                f"Pressure: {weather_data['pressure']} hPa\n"
                f"Sunrise: {weather_data['sunrise']}, Sunset: {weather_data['sunset']}"
            )
    
    def is_good_weather(self, weather_data: Dict) -> bool:
        """Determine if weather is good for outdoor activities"""
        # Simple logic - can be enhanced
        if "weather" in weather_data:
            weather_desc = weather_data["weather"].lower()
            bad_conditions = ["rain", "storm", "thunder", "snow", "heavy", "extreme"]
            
            if any(bad in weather_desc for bad in bad_conditions):
                return False
            
            # Check temperature (comfortable range: 15°C to 30°C)
            temp = weather_data.get("temperature", 20)
            if 15 <= temp <= 30:
                return True
        
        return True