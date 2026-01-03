from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
from dotenv import load_dotenv
# Add to imports
from agents.weather_agent import WeatherAgent
from agents.db_agent import DatabaseAgent
from agents.meeting_agent import MeetingAgent
from agents.orchestrator import AgentOrchestrator
from database.connection import db_manager
try:
    from agents.document_agent import DocumentAgent
    document_agent_available = True
except ImportError:
    DocumentAgent = None
    document_agent_available = False
    print("Warning: DocumentAgent could not be imported (missing dependencies)")

from api.routes import router as api_router
from app.config import settings

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    global document_agent_available
    # Startup
    print("Starting Agentic AI Chatbot...")
    
    # Initialize database
    db_manager.connect()
    db_manager.create_tables()
    
    # Initialize agents
    weather_agent = WeatherAgent(
        api_key=os.getenv("OPENWEATHER_API_KEY", "")
    )
    db_agent = DatabaseAgent()
    meeting_agent = MeetingAgent(weather_agent)
    
    document_agent = None
    if document_agent_available:
        try:
            document_agent = DocumentAgent(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                upload_dir="static/uploads"
            )
        except Exception as e:
            print(f"Failed to initialize DocumentAgent: {e}")
            document_agent_available = False
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    orchestrator.register_agent(weather_agent)
    orchestrator.register_agent(db_agent)
    orchestrator.register_agent(meeting_agent)
    if document_agent_available and document_agent:
        orchestrator.register_agent(document_agent)
    
    # Store in app state
    app.state.orchestrator = orchestrator
    app.state.weather_agent = weather_agent
    app.state.db_agent = db_agent
    app.state.meeting_agent = meeting_agent
    app.state.document_agent = document_agent
    
    print("All 4 agents initialized successfully!")
    yield
    
    # Shutdown
    print("Shutting down...")
    # Close database connections if needed

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Chatbot",
    description="Multi-agent AI chatbot with weather, document, and scheduling capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic AI Chatbot API",
        "version": "1.0.0",
        "agents": ["Weather", "Database", "Meeting", "Document"],
        "endpoints": {
            "health": "/health",
            "agents": "/api/agents",
            "query": "/api/query",
            "weather": "/api/weather",
            "meetings": "/api/meetings"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if db_manager.engine else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }