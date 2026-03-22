# 🧠 Code Intelligence Worker

AI-powered **Code Review + Test Generation** for Python and Java.

## Tech Stack
- **Backend**: Python / FastAPI
- **AI Agent**: Google Gemini 1.5 Flash (function calling)
- **RAG**: ChromaDB + Google text-embedding-004
- **Frontend**: React + Vite

---

## ⚡ Quick Start

### 1. Get Free Gemini API Key
Visit https://aistudio.google.com → Sign in → Get API Key (free tier: 15 req/min)

### 2. Backend
```bash
cd backend
cp .env.example .env
# Edit .env → add your GEMINI_API_KEY

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## Architecture

```
User (React UI)
    │
    ▼ POST /api/analyze
FastAPI Backend
    │
    ▼
AI Agent (Gemini 1.5 Flash)
    ├── Tool 1: run_static_analysis  (pylint / regex)
    ├── Tool 2: search_coding_standards  (ChromaDB RAG)
    └── Tool 3: search_test_patterns     (ChromaDB RAG)
    │
    ▼
Structured JSON Response
    │
    ▼
UI: Code Review Tab + Test Cases Tab
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Analyze code (review + tests) |
| GET | `/health` | Health check |
| GET | `/api/languages` | Supported languages |

### Request
```json
{
  "code": "your source code",
  "language": "python",
  "mode": "both"
}
```

### Response
```json
{
  "language": "python",
  "review": {
    "summary": "...",
    "score": 65,
    "issues": [...],
    "positive_aspects": [...]
  },
  "tests": {
    "framework": "pytest",
    "test_cases": [...],
    "coverage_areas": [...]
  }
}
```

## Knowledge Base (RAG)
27 curated documents covering:
- Python & Java coding standards (Google Style Guide)
- OWASP security guidelines
- pytest & JUnit 5 test patterns
- Clean Code principles
