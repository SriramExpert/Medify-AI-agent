from database.connection import db_manager
from models.database import Meeting
from datetime import datetime, timedelta
import pytz

def init_database():
    """Initialize database with sample data"""
    db_manager.connect()
    db_manager.create_tables()
    
    # Add sample meetings if table is empty
    session = db_manager.get_session()
    try:
        count = session.query(Meeting).count()
        if count == 0:
            # Add sample meetings
            sample_meetings = [
                Meeting(
                    title="Team Standup",
                    description="Daily team sync",
                    scheduled_time=datetime.now(pytz.UTC) + timedelta(hours=2),
                    duration_minutes=30,
                    location="Conference Room A",
                    organizer="John Doe",
                    participants="john@email.com,jane@email.com,alex@email.com"
                ),
                Meeting(
                    title="Project Review",
                    description="Monthly project review meeting",
                    scheduled_time=datetime.now(pytz.UTC) + timedelta(days=1),
                    duration_minutes=60,
                    location="Virtual",
                    organizer="Jane Smith",
                    participants="jane@email.com,mark@email.com,sara@email.com"
                ),
                Meeting(
                    title="Client Presentation",
                    description="Presentation for new client",
                    scheduled_time=datetime.now(pytz.UTC) + timedelta(days=3),
                    duration_minutes=90,
                    location="Client Office",
                    organizer="Alex Johnson",
                    participants="alex@email.com,client@email.com"
                )
            ]
            
            session.add_all(sample_meetings)
            session.commit()
            print(f"Added {len(sample_meetings)} sample meetings")
        
        print("Database initialized successfully")
    except Exception as e:
        session.rollback()
        print(f"Error initializing database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_database()