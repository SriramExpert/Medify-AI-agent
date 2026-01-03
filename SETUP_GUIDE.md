# Medify: Comprehensive Setup & Run Guide

Medify is an Agentic AI Chatbot project featuring four intelligent agents: Weather, Database, Meeting, and Document. This guide ensures you can run the entire system smoothly.

## 🚀 Quick Start

### 1. Prerequisites
- **Docker Desktop**: Installed and running (for the Backend and Database).
- **Node.js (v18+)**: Installed (for the Frontend).

### 2. Environment Configuration
Create or edit the `.env` file in the root directory:

```env
# Weather API (Get your key at openweathermap.org)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# OpenAI (Optional - used for Document Agent)
OPENAI_API_KEY=your_openai_api_key_here

# Database (Default for Docker setup)
DATABASE_URL=postgresql://user:password@db:5432/agentic_db
```

---

## 🛠️ Running the Application

### Phase 1: Backend (Docker)
The backend uses FastAPI and PostgreSQL.
1. Open a terminal in the project root.
2. Run the following command:
   ```bash
   docker-compose up --build
   ```
3. Verify it's running:
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Phase 2: Frontend (React)
The frontend is a modern React UI built with Vite.
1. Open a **new** terminal.
2. Navigate to the frontend folder:
   ```bash
   cd frontend/medify_frontend
   ```
3. Install dependencies and start:
   ```bash
   npm install
   npm run dev
   ```
4. Access the UI: [http://localhost:5174](http://localhost:5174)

---

## 🤖 Interacting with Agents

| Agent | What to Ask |
| :--- | :--- |
| **Weather** | "What is the weather in London?" |
| **Meeting** | "Schedule a meeting for tomorrow at 2 PM." |
| **Database** | "Show me all confirmed meetings." |
| **Document** | "Upload resume.pdf" -> "What are the skills?" |

---

## 📂 Project Structure
- **/app**: Main FastAPI application logic.
- **/agents**: Individual AI agent implementations (Weather, DB, etc.).
- **/frontend**: React + Vite source code.
- **docker-compose.yml**: Orchestration for the API and Database.

---

## ❓ Troubleshooting
- **API Key Errors**: Ensure your `.env` variables don't have spaces around the `=`.
- **Database Connection**: If the API fails to connect, wait 10 seconds for the DB container to fully initialize.
- **Port Conflict**: If port `5174` is busy, check the terminal output for the new port number.
