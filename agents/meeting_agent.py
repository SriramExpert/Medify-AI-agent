from typing import Dict, Any
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from agents.weather_agent import WeatherAgent
from tools.database_tool import DatabaseTool
import logging
import re

logger = logging.getLogger(__name__)

class MeetingAgent(BaseAgent):
    """Agent 3: Meeting Scheduling + Weather Reasoning Agent"""
    
    def __init__(self, weather_agent: WeatherAgent):
        super().__init__(name="MeetingAgent", description="Schedules meetings with weather consideration")
        self.weather_agent = weather_agent
        self.db_tool = DatabaseTool()
        self.default_meeting_duration = 60  # minutes
        self.default_location = "Conference Room"
    
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        schedule_keywords = [
            'schedule', 'plan', 'arrange', 'organize', 'book',
            'set up', 'create', 'add meeting', 'new meeting',
            'verify weather', 'check weather', 'weather good',
            'team meeting', 'meeting if weather'
        ]
        
        return any(keyword in query_lower for keyword in schedule_keywords)
    
    async def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process meeting scheduling queries with weather check"""
        try:
            query_lower = query.lower()
            
            # Extract meeting details
            meeting_details = self._extract_meeting_details(query)
            
            # Check if weather verification is needed
            if 'weather' in query_lower or 'verify' in query_lower:
                return await self._schedule_with_weather_check(meeting_details)
            else:
                return await self._simple_schedule(meeting_details)
                
        except Exception as e:
            logger.error(f"Error in MeetingAgent: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to schedule meeting: {str(e)}",
                "agent": self.name
            }
    
    async def _schedule_with_weather_check(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule meeting with weather verification"""
        try:
            # Extract city for weather check
            city = details.get('city', 'London')  # Default city
            
            # Get weather for the scheduled time
            if details.get('time') == 'tomorrow':
                weather_query = f"What is the weather in {city} tomorrow?"
            else:
                weather_query = f"What is the weather in {city} today?"
            
            # Get weather information
            weather_result = await self.weather_agent.process(weather_query)
            
            if not weather_result["success"]:
                return {
                    "success": False,
                    "error": "Could not verify weather conditions",
                    "agent": self.name
                }
            
            # Check if weather is good
            is_good_weather = self.weather_agent.is_good_weather(weather_result.get("data", {}))
            weather_condition = weather_result.get("data", {}).get("weather", "Unknown")
            
            # Check for existing meetings
            meeting_time = self._parse_meeting_time(details)
            meeting_exists = self.db_tool.check_meeting_exists(meeting_time, details.get('title'))
            
            if meeting_exists:
                response = (
                    f"A meeting already exists around {meeting_time.strftime('%I:%M %p')}.\n"
                    f"Weather condition: {weather_condition}\n"
                    f"Weather is {'GOOD' if is_good_weather else 'NOT GOOD'} for outdoor activities."
                )
                
                return {
                    "success": False,
                    "response": response,
                    "agent": self.name,
                    "weather_checked": True,
                    "is_good_weather": is_good_weather,
                    "existing_meeting": True
                }
            
            # Schedule meeting if weather is good
            if is_good_weather:
                # Create meeting
                meeting_data = {
                    "title": details.get('title', 'Team Meeting'),
                    "description": details.get('description', 'Scheduled by AI Agent'),
                    "scheduled_time": meeting_time.isoformat(),
                    "duration_minutes": details.get('duration', self.default_meeting_duration),
                    "location": details.get('location', self.default_location),
                    "organizer": "AI Assistant",
                    "weather_checked": True,
                    "weather_condition": weather_condition
                }
                
                result = self.db_tool.create_meeting(meeting_data)
                
                if result["success"]:
                    response = (
                        f"✅ Meeting scheduled successfully!\n"
                        f"Title: {meeting_data['title']}\n"
                        f"Time: {meeting_time.strftime('%A, %B %d at %I:%M %p')}\n"
                        f"Location: {meeting_data['location']}\n"
                        f"Weather: {weather_condition} (Good for meeting)\n"
                        f"Meeting ID: {result['meeting']['id']}"
                    )
                    
                    return {
                        "success": True,
                        "response": response,
                        "agent": self.name,
                        "meeting": result['meeting'],
                        "weather_checked": True,
                        "is_good_weather": True
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to create meeting in database",
                        "agent": self.name
                    }
            else:
                # Weather is bad, don't schedule
                response = (
                    f"❌ Cannot schedule meeting due to bad weather.\n"
                    f"Weather condition: {weather_condition}\n"
                    f"Recommendation: Schedule for another day or move indoors."
                )
                
                return {
                    "success": False,
                    "response": response,
                    "agent": self.name,
                    "weather_checked": True,
                    "is_good_weather": False,
                    "recommendation": "Reschedule or move indoors"
                }
                
        except Exception as e:
            logger.error(f"Error in weather-based scheduling: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to schedule with weather check: {str(e)}",
                "agent": self.name
            }
    
    async def _simple_schedule(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule meeting without weather check"""
        try:
            meeting_time = self._parse_meeting_time(details)
            
            # Check for existing meetings
            meeting_exists = self.db_tool.check_meeting_exists(meeting_time, details.get('title'))
            
            if meeting_exists:
                return {
                    "success": False,
                    "response": f"A meeting already exists around {meeting_time.strftime('%I:%M %p')}.",
                    "agent": self.name,
                    "existing_meeting": True
                }
            
            # Create meeting
            meeting_data = {
                "title": details.get('title', 'Team Meeting'),
                "description": details.get('description', 'Scheduled by AI Agent'),
                "scheduled_time": meeting_time.isoformat(),
                "duration_minutes": details.get('duration', self.default_meeting_duration),
                "location": details.get('location', self.default_location),
                "organizer": "AI Assistant"
            }
            
            result = self.db_tool.create_meeting(meeting_data)
            
            if result["success"]:
                response = (
                    f"✅ Meeting scheduled successfully!\n"
                    f"Title: {meeting_data['title']}\n"
                    f"Time: {meeting_time.strftime('%A, %B %d at %I:%M %p')}\n"
                    f"Location: {meeting_data['location']}\n"
                    f"Meeting ID: {result['meeting']['id']}"
                )
                
                return {
                    "success": True,
                    "response": response,
                    "agent": self.name,
                    "meeting": result['meeting']
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "agent": self.name
                }
                
        except Exception as e:
            logger.error(f"Error in simple scheduling: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to schedule meeting: {str(e)}",
                "agent": self.name
            }
    
    def _extract_meeting_details(self, query: str) -> Dict[str, Any]:
        """Extract meeting details from natural language query"""
        details = {
            "title": "Team Meeting",
            "time": "today",
            "duration": self.default_meeting_duration,
            "location": self.default_location,
            "city": "London"  # Default for weather check
        }
        
        query_lower = query.lower()
        
        # Extract title
        title_patterns = [
            r'schedule\s+(?:a|an)?\s*(.+?)\s+(?:meeting|at|for)',
            r'meeting\s+(?:about|on|for)\s+(.+)',
            r'(.+?)\s+meeting'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, query_lower)
            if match:
                title = match.group(1).strip()
                if len(title) > 3:  # Avoid very short titles
                    details["title"] = title.title()
                    break
        
        # Extract time
        if 'tomorrow' in query_lower:
            details["time"] = "tomorrow"
        elif 'today' in query_lower:
            details["time"] = "today"
        elif 'next week' in query_lower:
            details["time"] = "next_week"
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(?:minute|min|hour|hr)', query_lower)
        if duration_match:
            duration = int(duration_match.group(1))
            if 'hour' in query_lower or 'hr' in query_lower:
                duration *= 60  # Convert hours to minutes
            details["duration"] = min(duration, 240)  # Max 4 hours
        
        # Extract location
        location_match = re.search(r'at\s+(.+?)(?:\s+tomorrow|\s+today|$)', query_lower)
        if location_match:
            details["location"] = location_match.group(1).title()
        
        # Extract city for weather (if mentioned)
        city_match = re.search(r'in\s+([A-Za-z\s]+?)(?:\s+today|\s+tomorrow|$)', query_lower)
        if city_match:
            details["city"] = city_match.group(1).title()
        
        return details
    
    def _parse_meeting_time(self, details: Dict[str, Any]) -> datetime:
        """Parse meeting time from details"""
        now = datetime.now()
        
        if details["time"] == "tomorrow":
            meeting_time = now + timedelta(days=1)
            # Default time: 10 AM tomorrow
            meeting_time = meeting_time.replace(hour=10, minute=0, second=0, microsecond=0)
        elif details["time"] == "next_week":
            # Next Monday at 10 AM
            days_ahead = 7 - now.weekday()  # Monday is 0
            meeting_time = now + timedelta(days=days_ahead)
            meeting_time = meeting_time.replace(hour=10, minute=0, second=0, microsecond=0)
        else:
            # Today, 2 hours from now
            meeting_time = now + timedelta(hours=2)
        
        return meeting_time