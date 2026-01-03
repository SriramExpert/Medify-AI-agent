from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
# Add to imports
from fastapi import UploadFile, File, Form
import shutil
from pathlib import Path

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default"
    session_id: str = "default"

class MeetingRequest(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_time: str  # ISO format
    duration_minutes: Optional[int] = 60
    location: Optional[str] = "Conference Room"
    check_weather: Optional[bool] = False
    city: Optional[str] = "London"

@router.post("/query")
async def process_query(request: Request, query_request: QueryRequest):
    """Process user query through agent orchestrator"""
    try:
        orchestrator = request.app.state.orchestrator
        result = await orchestrator.route_query(query_request.query, query_request.user_id)
        
        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/agents")
async def list_agents(request: Request):
    """List all available agents and their status"""
    try:
        orchestrator = request.app.state.orchestrator
        return orchestrator.get_agent_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")

@router.post("/weather")
async def weather_endpoint(request: Request, query_request: QueryRequest):
    """Direct weather query endpoint"""
    try:
        weather_agent = request.app.state.weather_agent
        result = await weather_agent.process(query_request.query)
        
        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")

@router.get("/meetings")
async def get_meetings(
    request: Request,
    date: Optional[str] = None,
    search: Optional[str] = None
):
    """Get meetings with optional filtering"""
    try:
        db_agent = request.app.state.db_agent
        
        if search:
            query = f"search meetings about {search}"
        elif date:
            query = f"meetings on {date}"
        else:
            query = "meetings today"
        
        result = await db_agent.process(query)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/meetings/schedule")
async def schedule_meeting(request: Request, meeting_request: MeetingRequest):
    """Schedule a new meeting"""
    try:
        meeting_agent = request.app.state.meeting_agent
        
        # Create query for the agent
        query_parts = [f"Schedule a meeting titled '{meeting_request.title}'"]
        
        if meeting_request.description:
            query_parts.append(f"about {meeting_request.description}")
        
        query_parts.append(f"at {meeting_request.scheduled_time}")
        query_parts.append(f"for {meeting_request.duration_minutes} minutes")
        
        if meeting_request.location:
            query_parts.append(f"at {meeting_request.location}")
        
        if meeting_request.check_weather:
            query_parts.append(f"and verify weather in {meeting_request.city}")
        
        query = " ".join(query_parts)
        
        result = await meeting_agent.process(query)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meeting scheduling error: {str(e)}")

@router.get("/test")
async def test_endpoints(request: Request):
    """Test all agents with sample queries"""
    test_queries = [
        ("Weather", "What is the weather in London today?"),
        ("Database", "Show meetings scheduled tomorrow"),
        ("Meeting", "Verify tomorrow's weather and schedule a team meeting"),
        ("Database", "Do we have any meetings today?"),
        ("Weather", "What was the weather in Bengaluru yesterday?"),
        ("Database", "List meetings next week"),
        ("Meeting", "Schedule a project review meeting tomorrow at 2 PM"),
        ("Database", "Is there any review meeting?")
    ]
    
    results = []
    orchestrator = request.app.state.orchestrator
    
    for agent_type, query in test_queries:
        try:
            result = await orchestrator.route_query(query)
            results.append({
                "agent_type": agent_type,
                "query": query,
                "success": result.get("success", False),
                "agent_used": result.get("agent", "unknown"),
                "response_preview": str(result.get("response", ""))[:100] + "..." if result.get("response") else "No response"
            })
        except Exception as e:
            results.append({
                "agent_type": agent_type,
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    return {
        "test_results": results,
        "total_tests": len(test_queries),
        "successful": sum(1 for r in results if r.get("success", False))
    }


# Add new routes
    @router.post("/document/upload")
    async def upload_document(
        request: Request,
        file: UploadFile = File(...),
        description: str = Form(None)
    ):
        """Upload and process a document"""
        try:
            document_agent = request.app.state.document_agent
            if not document_agent:
                 raise HTTPException(status_code=503, detail="Document agent is not available (missing dependencies)")

            # Check file type
            allowed_extensions = ['.pdf', '.txt', '.docx']
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
                )
            
            # Read file content
            content = await file.read()
            
            # Process with document agent
            result = await document_agent.process(
                query=f"Upload document {file.filename}",
                file_content=content,
                filename=file.filename
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Document upload error: {str(e)}")
    
    @router.post("/document/query")
    async def query_document(
        request: Request,
        query_request: QueryRequest
    ):
        """Query the uploaded document"""
        try:
            document_agent = request.app.state.document_agent
            if not document_agent:
                 raise HTTPException(status_code=503, detail="Document agent is not available (missing dependencies)")

            # Check if document is loaded
            if not document_agent.current_document:
                raise HTTPException(
                    status_code=400,
                    detail="No document loaded. Please upload a document first."
                )
            
            result = await document_agent.process(query_request.query)
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Document query error: {str(e)}")
    
    @router.get("/document/status")
    async def document_status(request: Request):
        """Get status of currently loaded document"""
        try:
            document_agent = request.app.state.document_agent
            if not document_agent:
                 return {"loaded": False, "status": "unavailable"}

            return {
                "loaded": document_agent.current_document is not None,
                "filename": document_agent.current_filename,
                "characters": len(document_agent.current_document) if document_agent.current_document else 0,
                "has_vector_store": document_agent.document_tool.vector_store is not None
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting document status: {str(e)}")
    
    @router.delete("/document/clear")
    async def clear_document(request: Request):
        """Clear the currently loaded document"""
        try:
            document_agent = request.app.state.document_agent
            if not document_agent:
                 raise HTTPException(status_code=503, detail="Document agent is not available")

            document_agent.clear_document()
            
            return {
                "success": True,
                "message": "Document cleared successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error clearing document: {str(e)}")
    
    @router.post("/document/example")
    async def load_example_document(request: Request):
        """Load an example resume document"""
        try:
            document_agent = request.app.state.document_agent
            if not document_agent:
                 raise HTTPException(status_code=503, detail="Document agent is not available")
            
            # Example resume text
            example_resume = """
            JOHN DOE - SOFTWARE ENGINEER
            Contact: john.doe@email.com | (123) 456-7890 | LinkedIn: linkedin.com/in/johndoe
            
            SUMMARY
            Senior Software Engineer with 8+ years of experience in building scalable web applications.
            Specialized in Python, FastAPI, and cloud technologies. Proven track record of leading
            teams and delivering high-quality software solutions.
            
            EXPERIENCE
            Senior Software Engineer - Tech Solutions Inc. (2020-Present)
            • Led development of microservices architecture handling 1M+ daily requests
            • Implemented CI/CD pipeline reducing deployment time by 70%
            • Mentored 5 junior developers
            • Technologies: Python, FastAPI, PostgreSQL, Docker, AWS
            
            Software Engineer - Innovate Corp (2016-2020)
            • Developed REST APIs for mobile and web applications
            • Optimized database queries improving performance by 40%
            • Collaborated with product team on feature planning
            • Technologies: Python, Django, MySQL, React
            
            EDUCATION
            Master of Science in Computer Science - Stanford University (2016)
            Bachelor of Technology in Computer Engineering - MIT (2014)
            
            SKILLS
            • Programming: Python, JavaScript, TypeScript, SQL
            • Frameworks: FastAPI, Django, React, Node.js
            • Tools: Docker, Kubernetes, AWS, Git, Jenkins
            • Databases: PostgreSQL, MySQL, MongoDB, Redis
            
            CERTIFICATIONS
            • AWS Certified Solutions Architect
            • Google Cloud Professional Developer
            • Python Institute PCAP
            
            PROJECTS
            • Agentic AI Chatbot: Built a multi-agent AI system with weather, document, and scheduling capabilities
            • E-commerce Platform: Developed scalable microservices architecture serving 500k users
            • Real-time Analytics Dashboard: Created dashboard for monitoring system metrics
            
            LANGUAGES
            • English (Native)
            • Spanish (Fluent)
            • French (Intermediate)
            """
            
            # Process the example resume
            success = document_agent.document_tool.create_vector_store(
                example_resume, 
                "Example_Resume.txt"
            )
            
            if success:
                document_agent.current_document = example_resume
                document_agent.current_filename = "Example_Resume.txt"
                
                return {
                    "success": True,
                    "message": "Example resume loaded successfully",
                    "filename": "Example_Resume.txt",
                    "summary": document_agent._analyze_document(example_resume)
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to load example document")
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading example: {str(e)}")