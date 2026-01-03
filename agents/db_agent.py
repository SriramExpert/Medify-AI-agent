from typing import Dict, Any
import re
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from tools.database_tool import DatabaseTool
import logging
import dateparser

logger = logging.getLogger(__name__)

class DatabaseAgent(BaseAgent):
    """Agent 4: Natural Language to Database Query Agent"""
    
    def __init__(self):
        super().__init__(name="DatabaseAgent", description="Handles database queries for meetings")
        self.db_tool = DatabaseTool()
        self.patterns = {
            'today': r'(today|now|current|right now)',
            'tomorrow': r'(tomorrow|next day|day after)',
            'this_week': r'(this week|current week|week)',
            'next_week': r'(next week|following week|upcoming week)',
            'search': r'(search|find|look for|query)\s+(.+)',
            'all': r'(all|every|list|show)\s+meetings',
            'specific_date': r'(on|for|at)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
        }
    
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle the query"""
        query_lower = query.lower()
        meeting_keywords = [
            'meeting', 'schedule', 'calendar', 'appointment',
            'review', 'standup', 'presentation', 'conference',
            'show', 'list', 'find', 'search', 'today', 'tomorrow',
            'week', 'when', 'where', 'what meetings'
        ]
        
        return any(keyword in query_lower for keyword in meeting_keywords)
    
    async def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process database-related queries"""
        try:
            query_lower = query.lower()
            
            # Route to appropriate handler
            if re.search(self.patterns['today'], query_lower):
                meetings = self.db_tool.get_meetings_today()
                response = self._format_today_response(meetings)
                
            elif re.search(self.patterns['tomorrow'], query_lower):
                meetings = self.db_tool.get_meetings_tomorrow()
                response = self._format_tomorrow_response(meetings)
                
            elif re.search(self.patterns['next_week'], query_lower):
                meetings = self.db_tool.get_meetings_next_week()
                response = self._format_next_week_response(meetings)
                
            elif re.search(self.patterns['all'], query_lower):
                meetings = self.db_tool.get_all_meetings()
                response = self._format_all_response(meetings)
                
            elif match := re.search(self.patterns['search'], query_lower):
                keyword = match.group(2)
                meetings = self.db_tool.search_meetings(keyword)
                response = self._format_search_response(meetings, keyword)
                
            elif match := re.search(self.patterns['specific_date'], query_lower):
                date_str = match.group(2)
                date = dateparser.parse(date_str)
                if date:
                    meetings = self.db_tool.get_meetings_by_date(date)
                    response = self._format_date_response(meetings, date)
                else:
                    response = "Could not understand the date. Please try again."
                    meetings = []
            else:
                # Default: show today's meetings
                meetings = self.db_tool.get_meetings_today()
                response = self._format_today_response(meetings)
            
            # Determine confidence
            confidence = 0.9 if meetings else 0.6
            
            return {
                "success": True,
                "data": meetings,
                "response": response,
                "agent": self.name,
                "confidence": confidence,
                "count": len(meetings)
            }
            
        except Exception as e:
            logger.error(f"Error in DatabaseAgent: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process database query: {str(e)}",
                "agent": self.name
            }
    
    def _format_today_response(self, meetings: list) -> str:
        if not meetings:
            return "No meetings scheduled for today."
        
        response = f"You have {len(meetings)} meeting(s) today:\n\n"
        for i, meeting in enumerate(meetings, 1):
            time = datetime.fromisoformat(meeting['scheduled_time']).strftime("%I:%M %p")
            response += f"{i}. **{meeting['title']}**\n"
            response += f"   Time: {time}\n"
            response += f"   Location: {meeting['location'] or 'Not specified'}\n"
            response += f"   Duration: {meeting['duration_minutes']} minutes\n"
            if meeting['description']:
                response += f"   Description: {meeting['description'][:100]}...\n"
            response += "\n"
        
        return response
    
    def _format_tomorrow_response(self, meetings: list) -> str:
        if not meetings:
            return "No meetings scheduled for tomorrow."
        
        response = f"You have {len(meetings)} meeting(s) tomorrow:\n\n"
        for i, meeting in enumerate(meetings, 1):
            time = datetime.fromisoformat(meeting['scheduled_time']).strftime("%I:%M %p")
            response += f"{i}. **{meeting['title']}**\n"
            response += f"   Time: {time}\n"
            response += f"   Location: {meeting['location'] or 'Not specified'}\n"
            response += "\n"
        
        return response
    
    def _format_next_week_response(self, meetings: list) -> str:
        if not meetings:
            return "No meetings scheduled for next week."
        
        response = f"You have {len(meetings)} meeting(s) next week:\n\n"
        # Group by day
        meetings_by_day = {}
        for meeting in meetings:
            meeting_time = datetime.fromisoformat(meeting['scheduled_time'])
            day = meeting_time.strftime("%A, %B %d")
            if day not in meetings_by_day:
                meetings_by_day[day] = []
            meetings_by_day[day].append(meeting)
        
        for day, day_meetings in meetings_by_day.items():
            response += f"**{day}**:\n"
            for meeting in day_meetings:
                time = datetime.fromisoformat(meeting['scheduled_time']).strftime("%I:%M %p")
                response += f"  • {meeting['title']} at {time}\n"
            response += "\n"
        
        return response
    
    def _format_all_response(self, meetings: list) -> str:
        if not meetings:
            return "No meetings found in the system."
        
        response = f"Found {len(meetings)} meeting(s) in total:\n\n"
        # Group by status or date
        for i, meeting in enumerate(meetings[:10], 1):  # Limit to first 10
            time = datetime.fromisoformat(meeting['scheduled_time']).strftime("%Y-%m-%d %I:%M %p")
            response += f"{i}. **{meeting['title']}**\n"
            response += f"   Scheduled: {time}\n"
            response += f"   Status: {meeting['status'].title()}\n"
            response += "\n"
        
        if len(meetings) > 10:
            response += f"... and {len(meetings) - 10} more meetings."
        
        return response
    
    def _format_search_response(self, meetings: list, keyword: str) -> str:
        if not meetings:
            return f"No meetings found matching '{keyword}'."
        
        response = f"Found {len(meetings)} meeting(s) matching '{keyword}':\n\n"
        for i, meeting in enumerate(meetings, 1):
            time = datetime.fromisoformat(meeting['scheduled_time']).strftime("%Y-%m-%d %I:%M %p")
            response += f"{i}. **{meeting['title']}**\n"
            response += f"   Time: {time}\n"
            response += f"   Description: {meeting['description'][:150] if meeting['description'] else 'No description'}...\n"
            response += "\n"
        
        return response
    
    def _format_date_response(self, meetings: list, date: datetime) -> str:
        date_str = date.strftime("%A, %B %d, %Y")
        
        if not meetings:
            return f"No meetings scheduled on {date_str}."
        
        response = f"You have {len(meetings)} meeting(s) on {date_str}:\n\n"
        for i, meeting in enumerate(meetings, 1):
            time = datetime.fromisoformat(meeting['scheduled_time']).strftime("%I:%M %p")
            response += f"{i}. **{meeting['title']}**\n"
            response += f"   Time: {time}\n"
            response += f"   Location: {meeting['location'] or 'Not specified'}\n"
            response += "\n"
        
        return response