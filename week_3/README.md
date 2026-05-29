# KYouth Data AI — Week 3 Resume Helper Chatbot

A full-stack chat application that analyses resume skill gaps using AI. Upload your resume as a PDF and the chatbot will identify missing skills based on real job market data.

---

## Project Overview
- **Goal:** Build and containerise a full-stack chatbot with a frontend, backend, and AI model integration
- **Frontend:** Serves the chat UI (FastAPI + Jinja2 + Bootstrap)
- **Backend:** Processes messages and calls AI models (FastAPI)
- **AI Integration:**
  - Gemini (cloud) - extracts skills from resume and finds gaps against job database
  - Ollama (local) - handles general conversation and resume-related questions

---

## Prerequisites
Before running this project, make sure you have:
- `Docker Desktop` installed and running
- `Ollama` installed with `gemma3:1b` pulled:
  ```bash
  ollama pull gemma3:1b

---

## Setup Instructions
1. **Clone the repository**
2. **Configure environment variables**
  Copy the example env file and fill in your values:
```
cp backend/.env.example backend/.env
```
Edit backend/.env:
```
GEMINI_API_KEY=your_gemini_api_key_here
DB_PATH=src/week_2/data/resources/your-db.db
```
3. **Add the required data file**
  Place the jobs database at the DB_PATH
4. **Build and run**
```
docker compose up --build
```
---

## Usage
**Running the app:**
```
docker compose up --build   # first time or after code changes
docker compose up           # subsequent runs (no code changes)
```
**Using the chatbot:**
1. General chat - Type a message and press Send or Enter
2. Ask for skill gap analysis - Type keywords like "find skill gaps" or "skill gap analysis"
3. Upload resume for analysis - Choose a PDF file, then press Send
4. Ask questions about your resume - Upload a PDF and type your question (e.g., "summarise this resume")

**Expected behaviour:**
- PDF uploaded (no message) -> skill gap analysis runs automatically
- PDF uploaded + skill gap keyword -> skill gap analysis
- PDF uploaded + other question -> Ollama answers using the resume as context
- Skill gap keyword without PDF -> bot asks you to upload a PDF
- General message (e.g., "hello") -> Ollama responds conversationally

---

## API / Function Reference
**Backend** — POST /chat
Endpoint: http://localhost:8001/chat

Request payload (JSON):
```
{
  "message": "find skill gaps",
  "pdf_text": "extracted text from resume..."
}
```
Response:
```
{
  "reply": "Skill gaps found: docker, kubernetes, aws..."
}
```

**Frontend** — POST /extract-pdf
Endpoint: http://localhost/extract-pdf

Request: multipart form with a .pdf file
Response:
```
{
  "text": "extracted plain text from the PDF..."
}
```
**Key JavaScript functions (chat_page.html):**
- appendMessage(sender, text) — adds a message bubble to the chat history; right-aligns "You" messages
- sendBtn click handler — extracts PDF text, validates input, sends to backend, displays reply
- Validates that empty PDF (no extractable text) is caught before sending to backend

**Service communication**
- Browser calls localhost/extract-pdf -> frontend container extracts PDF text
- Browser calls localhost:8001/chat -> backend container processes and responds
- Both containers share app-network (bridge) for internal Docker communication
- Ollama on the host machine is reached via host.docker.internal:11434

---

## Data / Assumptions
**Data used**
- jobs_d3_eval.db — SQLite database of job listings with tech_stack column
- Resume — uploaded as PDF by the user, converted to plain text via pypdf

**JSON message structure between frontend and backend:**
```
{ "message": "string", "pdf_text": "string (empty if no PDF)" }
```

**Assumptions:**
1. PDF must be text-based (not a scanned image) - pypdf cannot extract text from image-only PDFs
2. Gemini API key must be valid and have available quota
3. Ollama must be running on the host machine with gemma3:1b pulled
4. Database must be present at backend/src/week_2/data/resources/jobs_d3_eval.db

**Data flow:**
```
User types message + uploads PDF
        ↓
Browser sends PDF to /extract-pdf (frontend)
        ↓
pypdf extracts plain text
        ↓
Browser sends {message, pdf_text} to /chat (backend)
        ↓
Backend routes based on pdf_text and keywords
        ↓
Gemini API or Ollama generates response
        ↓
{"reply": "..."} returned to browser
        ↓
Chat history updated with bot reply
```

---

## Testing
**Backend — test with curl:**
```
# Test general chat
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"hello\", \"pdf_text\": \"\"}"

# Test skill gap keyword without PDF
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"find skill gaps\", \"pdf_text\": \"\"}"

# Test skill gap analysis with resume text
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"\", \"pdf_text\": \"Python, SQL, machine learning\"}"
```

**Frontend — manual test cases:**
1. General message	
  Type "hello", press Send  -> *Ollama replies conversationally*
2. Keyword without PDF	
  Type "find skill gaps", press Send    -> *Bot asks for PDF*
3. PDF only	
  Select PDF, press Send without typing -> *Skill gaps listed*
4. PDF + keyword	
  Select PDF, type "find skill gaps", press Send	-> *Skill gaps listed*
5. PDF + other question	
  Select PDF, type "summarise this resume", press Send	-> *Ollama summarises*
6. Image-only PDF	
  Upload scanned PDF	-> *Error message shown, no request sent*
7. Enter key	
  Type message, press Enter	-> *Same as clicking Send*

**Verifying Docker communication:**
```
docker compose ps          # check both containers are Up
docker logs week_3-backend-1   # check backend logs for errors
```

---

## Limitation
1. No chat history persistence: refreshing the page clears all messages
2. Image-based PDFs not supported: scanned PDFs return no text; only text-based PDFs work
3. Ollama model size: `gemma3:1b` is a small model; responses may be less accurate than larger models
4. Gemini rate limits — skill gap analysis may fail silently if API quota is exceeded

---



## Architecture Reflection
**Design Choices**
1. Frontend/backend separation 
  - Splitting the UI and AI logic into two services makes each part easier to maintain and update independently. 
  - Changing the AI model in the backend does not require touching the frontend.
2. Docker containerisation 
  - Each service runs in its own isolated container with its own dependencies. 
  - Ensures the app runs the same on any machine.

**Trade-offs**
1. Keyword routing over intent classification - faster and predictable, but less flexible than using an LLM to classify intent.
2. Local Ollama over a cloud model - avoids API costs for general chat, but requires Ollama to be running on the host machine, which adds a setup dependency.

**Improvements**
- Add a database to persist chat history across sessions
- Replace keyword routing with LLM-based intent detection for more natural conversations
- Deploy to the cloud (Railway) so the app is accessible without running locally
- Add support for scanned PDFs using OCR

### Reflection on Microservices

**Why Microservices for this Application?**

The decision to split frontend and backend into separate services was driven by several factors:

**Benefits Achieved:**

| Benefit | Description |
|---------|-------------|
| **Independent Development** | Frontend and backend can be developed in isolation. Changes to one don't break the other as long as the API contract remains intact. |
| **Technology Flexibility** | Frontend uses Jinja2 templates (could be swapped for React/Vue). Backend uses FastAPI (could be swapped for Django/Flask). Each service can evolve independently. |
| **Focused Responsibility** | Frontend handles UI rendering and user input collection. Backend handles PDF processing, AI integration, and business logic. Clear separation makes debugging easier. |
| **Scalability Options** | Backend can scale to multiple instances under high load while frontend remains a single instance (typically sufficient for this use case). |

**Trade-offs Encountered:**

| Trade-off | Impact | Mitigation |
|-----------|--------|------------|
| Network Latency | ~1-5ms per request | Acceptable for chat application where users expect some delay |
| CORS Configuration | Required extra setup for cross-origin requests | Proper middleware configuration in FastAPI |
| Environment Variables | More variables to manage across services | .env files plus docker-compose for centralized management |
| Debugging Complexity | Need to check logs from multiple containers | `docker compose logs` command provides aggregated view |

### Reflection on Containerization

**Why Docker?**

Containerization was chosen over traditional deployment for these reasons:

**Key Benefits Realized:**

1. **Environment Consistency**
   - Same behavior across development (Windows/WSL) and production (Linux)
   - Identical Python version (3.14) and dependencies everywhere
   - Eliminates "works on my machine" problems

2. **Dependency Isolation**
   - No conflicts with system Python packages
   - Each container has its own isolated filesystem
   - Clean uninstall (just remove containers)

3. **Reproducible Builds**
   - Same image generated every time from Dockerfile
   - No surprises when deploying to different environments
   - Layer caching for faster rebuilds

4. **Simplified Onboarding**
   - New developers only need Docker installed
   - No Python environment setup required
   - Single command to start the entire application

**Challenges Faced and Solved:**

| Challenge | Solution | Lesson Learned |
|-----------|----------|----------------|
| Ollama Connectivity | Used `extra_hosts` and `OLLAMA_HOST=0.0.0.0` | Container-to-host communication requires special configuration |
| Build Times (30-60s) | Leveraged Docker layer caching | Order Dockerfile layers from least to most frequently changed |
| Resource Usage (~1.5GB) | Acceptable for modern hardware | Consider resource limits for production deployments |

### Reflection on Deployment

**Current Deployment Strategy:**

```bash
# Single command deploys entire stack
docker compose up -d