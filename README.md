# 🚀 Agentic AI Chatbot - Complete Implementation
A sophisticated multi-agent AI system that intelligently routes queries, selects tools, and orchestrates workflows between specialized agents. This Python backend implements a complete agentic architecture where AI agents reason, make decisions, fetch data, and respond autonomously.

# Agentic AI Workflow Chatbot 🚀

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/6f193d0f-ac9c-4192-ba7b-7f4b2acdc8c9" />

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/5e63197a-fa5a-48b7-b675-302a1b7e527d" />

<img width="1918" height="1078" alt="Image" src="https://github.com/user-attachments/assets/24659198-8e5d-423a-9899-5f111670bb00" />

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/c0b54523-15d8-4cfd-b39f-8d1b4e3f1f34" />

<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/48079440-1101-4515-a7a2-c66afb11579d" />

# Demo Video:
I have uploaded the video in google drive can you please refer it through the link

https://drive.google.com/file/d/1jbAyxJJe2n9Sm8r9MUTBEZH2Qxbg0l9F/view?usp=sharing

# 🐳 Docker Deployment
The entire system is containerized and deployed as Docker containers:
# Pull and run locally
docker pull yourusername/agentic-ai-chatbot:latest
docker run -p 8000:8000 -e OPENWEATHER_API_KEY=your_key yourusername/agentic-ai-chatbot

## ✨ Features

### 🤖 **4 Intelligent Agents:**
1. 🌤️ Weather Intelligence Agent
  - Function: Real-time weather data with OpenWeatherMap API
  
  - Features: Natural language date parsing, city extraction, multi-day forecasts
  
  - Example: "What was the weather in Bengaluru yesterday?"

2. 📄 Document Understanding + Web Intelligence Agent
  - Function: Document processing with web search fallback
  
  - Features: PDF/TXT/DOCX upload, vector-based Q&A, Google search integration
  
  - Example: Upload resume → "What skills are mentioned?" → Falls back to web if not found

3. 📅 Meeting Scheduling + Weather Reasoning Agent
  - Function: Intelligent meeting scheduling with weather consideration
  
  - Features: Weather verification, conflict checking, automatic scheduling
  
  - Example: "Verify tomorrow's weather and schedule team meeting if good"

4. 💾 Natural Language → Database Query Agent
  - Function: Converts natural language to database operations
  
  - Features: Pattern-based NLU, meeting management, temporal queries
  
  - Example: "Show all meetings scheduled tomorrow"


# 🏗️ System Architecture
    ┌─────────────────────────────────────────────────────┐
    │                 User Interface                      │
    └──────────────────────────┬──────────────────────────┘
                               │
    ┌──────────────────────────▼──────────────────────────┐
    │           Agent Orchestrator (FastAPI)              │
    │  ┌──────────────────────────────────────────────┐  │
    │  │ 1. Query Analysis & Agent Selection          │  │
    │  │ 2. Tool Execution Coordination               │  │
    │  │ 3. Response Aggregation & Formatting         │  │
    │  └──────────────────────────────────────────────┘  │
    └──────────┬──────────────┬──────────────┬───────────┘
               │              │              │
        ┌──────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │ Weather    │ │ Document  │ │ Meeting   │
        │ Agent      │ │ Agent     │ │ Agent     │
        └──────┬─────┘ └─────┬─────┘ └─────┬─────┘
               │              │              │
        ┌──────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │OpenWeather │ │PDF/TXT    │ │Database   │
        │   API      │ │Processing │ │  Agent    │
        └────────────┘ └─────┬─────┘ └─────┬─────┘
                             │              │
                      ┌──────▼─────┐ ┌─────▼─────┐
                      │Web Search  │ │PostgreSQL │
                      │ (Fallback) │ │ Database  │
                      └────────────┘ └───────────┘

### 🧠 **Agentic Workflow:**
- Intelligent query routing
- Multi-agent collaboration
- Context-aware responses
- Fallback mechanisms

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **AI/ML**: LangChain, OpenAI (optional), FAISS
- **Document Processing**: PyPDF2, python-docx
- **APIs**: OpenWeatherMap, Google Search
- **Orchestration**: Custom agent orchestrator
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start


### Prerequisites
- Python 3.9+
- Docker & Docker Compose (recommended)
- OpenWeatherMap API key (free tier)
  
# 🔧 Configuration
Environment Variables
Create a .env file with:

Required
- OPENWEATHER_API_KEY=your_openweather_api_key_here

Database (for local development)
- DATABASE_URL=postgresql://user:password@localhost:5432/agentic_db

Optional - for enhanced features
- OPENAI_API_KEY=your_openai_api_key_here

Server Configuration
  - HOST=0.0.0.0
  - PORT=8000
  - DEBUG=True

# Get API Keys
1. OpenWeatherMap: Sign up at openweathermap.org/api (Free tier available)

2. OpenAI (Optional): Get from platform.openai.com for enhanced document processing

# 📁 Project Structure
    
    Medify/
    ├── app/                    # FastAPI application
    │   ├── main.py           # Application entry point
    │   ├── config.py         # Configuration settings
    │   └── dependencies.py   # Shared dependencies
    ├── agents/               # All 4 AI agents
    │   ├── weather_agent.py
    │   ├── document_agent.py
    │   ├── meeting_agent.py
    │   ├── db_agent.py
    │   └── orchestrator.py  # Intelligent agent router
    ├── tools/                # Agent tools
    │   ├── weather_tool.py  # OpenWeatherMap integration
    │   ├── database_tool.py # PostgreSQL operations
    │   ├── document_tool.py # PDF/text processing
    │   └── search_tool.py   # Google search fallback
    ├── api/                  # API routes
    ├── database/             # Database models & connection
    ├── frontend/ 
    ├── tests/               # Comprehensive test suite
    ├── static/              # Uploads directory
    ├── images/              # Screenshots and diagrams
    ├── Dockerfile           # Container configuration
    ├── docker-compose.yml   # Multi-service setup
    ├── requirements.txt     # Python dependencies
    └── README.md           # This file

# 🎯 Key Features
✅ Intelligent Agent Orchestration
  - Automatic query analysis and agent selection
  
  - Priority-based agent routing
  
  - Fallback mechanisms for error handling
  
  - Context-aware response generation

✅ Production-Ready Architecture
  - Docker containerization
  
  - PostgreSQL with connection pooling
  
  - Async/await for high concurrency
  
  - Comprehensive error handling
  
  - Health checks and monitoring

✅ Comprehensive Testing
  - Unit tests for all agents
  
  - Integration tests for API endpoints
  
  - End-to-end workflow testing
  
  - 90%+ test coverage

✅ Developer Friendly
  - Interactive API documentation (Swagger UI)
  
  - Detailed logging
  
  - Environment-based configuration
  
  - Easy extension points for new agents

# 🚨 Troubleshooting

Common Issues & Solutions
1. Weather API not working
   # Check API key is set
       echo $OPENWEATHER_API_KEY

  # Test API directly
        curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
2. Database connection issues:
      # Check if PostgreSQL is running
        docker ps | grep postgres
  
      # Test database connection
        python -c "from database.connection import db_manager; db_manager.connect()"
3. Document upload failing
  # Check file permissions
    ls -la static/uploads/
  
  # Ensure file type is supported (.pdf, .txt, .docx)
4. View logs
   # Docker logs
       docker-compose logs -f api
  
  # Application logs
      tail -f logs/app.log

# 🙏 Acknowledgments
  - OpenWeatherMap for weather data
  
  - FastAPI for the excellent web framework
  
  - LangChain for AI orchestration patterns
  
  - Render for free hosting tier

# 📞 Contact & Support
For questions, issues, or contributions:

GitHub Issues: Create an issue

Email: srirampalani106@gmail.com

LinkedIn: https://www.linkedin.com/in/sriram-sriram/


