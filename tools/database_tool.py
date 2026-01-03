from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models.database import Meeting
from database.connection import db_manager
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseTool:
    """Tool for database operations"""
    
    def __init__(self):
        self.session = db_manager.get_session()
    
    def get_all_meetings(self) -> List[Dict[str, Any]]:
        """Get all meetings"""
        try:
            meetings = self.session.query(Meeting).all()
            return [meeting.to_dict() for meeting in meetings]
        except Exception as e:
            logger.error(f"Error getting all meetings: {e}")
            return []
        finally:
            self.session.close()
    
    def get_meetings_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Get meetings scheduled for a specific date"""
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            meetings = self.session.query(Meeting).filter(
                and_(
                    Meeting.scheduled_time >= start_of_day,
                    Meeting.scheduled_time < end_of_day,
                    Meeting.status == "scheduled"
                )
            ).all()
            
            return [meeting.to_dict() for meeting in meetings]
        except Exception as e:
            logger.error(f"Error getting meetings by date: {e}")
            return []
    
    def get_meetings_today(self) -> List[Dict[str, Any]]:
        """Get meetings scheduled for today"""
        return self.get_meetings_by_date(datetime.now())
    
    def get_meetings_tomorrow(self) -> List[Dict[str, Any]]:
        """Get meetings scheduled for tomorrow"""
        tomorrow = datetime.now() + timedelta(days=1)
        return self.get_meetings_by_date(tomorrow)
    
    def get_meetings_next_week(self) -> List[Dict[str, Any]]:
        """Get meetings scheduled for next week"""
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            next_week_start = today + timedelta(days=7 - today.weekday())
            next_week_end = next_week_start + timedelta(days=7)
            
            meetings = self.session.query(Meeting).filter(
                and_(
                    Meeting.scheduled_time >= next_week_start,
                    Meeting.scheduled_time < next_week_end,
                    Meeting.status == "scheduled"
                )
            ).all()
            
            return [meeting.to_dict() for meeting in meetings]
        except Exception as e:
            logger.error(f"Error getting meetings next week: {e}")
            return []
    
    def search_meetings(self, keyword: str) -> List[Dict[str, Any]]:
        """Search meetings by keyword in title or description"""
        try:
            meetings = self.session.query(Meeting).filter(
                or_(
                    Meeting.title.ilike(f"%{keyword}%"),
                    Meeting.description.ilike(f"%{keyword}%")
                )
            ).all()
            
            return [meeting.to_dict() for meeting in meetings]
        except Exception as e:
            logger.error(f"Error searching meetings: {e}")
            return []
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new meeting"""
        try:
            # Convert string time to datetime if needed
            if isinstance(meeting_data.get('scheduled_time'), str):
                meeting_data['scheduled_time'] = datetime.fromisoformat(
                    meeting_data['scheduled_time'].replace('Z', '+00:00')
                )
            
            meeting = Meeting(**meeting_data)
            self.session.add(meeting)
            self.session.commit()
            
            logger.info(f"Created new meeting: {meeting.title}")
            return {"success": True, "meeting": meeting.to_dict()}
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating meeting: {e}")
            return {"success": False, "error": str(e)}
    
    def check_meeting_exists(self, time: datetime, title: str = None) -> bool:
        """Check if a meeting exists at a specific time"""
        try:
            time_window_start = time - timedelta(minutes=30)
            time_window_end = time + timedelta(minutes=30)
            
            query = self.session.query(Meeting).filter(
                and_(
                    Meeting.scheduled_time >= time_window_start,
                    Meeting.scheduled_time <= time_window_end,
                    Meeting.status == "scheduled"
                )
            )
            
            if title:
                query = query.filter(Meeting.title.ilike(f"%{title}%"))
            
            return query.count() > 0
        except Exception as e:
            logger.error(f"Error checking meeting existence: {e}")
            return False
    
    def update_meeting_weather(self, meeting_id: int, weather_condition: str) -> bool:
        """Update meeting with weather information"""
        try:
            meeting = self.session.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                meeting.weather_checked = True
                meeting.weather_condition = weather_condition
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating meeting weather: {e}")
            return False