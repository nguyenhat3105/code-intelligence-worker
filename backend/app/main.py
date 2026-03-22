from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.rag.knowledge_base import init_knowledge_base

app = FastAPI(title="Code Intelligence Worker", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("🚀 Initializing Knowledge Base...")
    init_knowledge_base()
    print("✅ Knowledge Base ready!")

app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "service": "Code Intelligence Worker", "llm": "Groq/llama-3.3-70b"}
