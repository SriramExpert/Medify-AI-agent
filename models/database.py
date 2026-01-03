from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pytz

Base = declarative_base()

class Meeting(Base):
    """Meeting model for the database"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    location = Column(String(100), nullable=True)
    organizer = Column(String(100), default="System")
    participants = Column(Text, nullable=True)  # JSON string or comma-separated
    status = Column(String(20), default="scheduled")  # scheduled, cancelled, completed
    weather_checked = Column(Boolean, default=False)
    weather_condition = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "scheduled_time": self.scheduled_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "organizer": self.organizer,
            "participants": self.participants,
            "status": self.status,
            "weather_checked": self.weather_checked,
            "weather_condition": self.weather_condition,
            "created_at": self.created_at.isoformat()
        }