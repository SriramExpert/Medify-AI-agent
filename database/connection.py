from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
    
    def connect(self):
        """Create database engine and session factory"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                echo=settings.DEBUG
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Database connection established")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_session(self):
        """Get a database session"""
        if not self.SessionLocal:
            self.connect()
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables"""
        from models.database import Base
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

# Global database instance
db_manager = DatabaseManager()