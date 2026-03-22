from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from app.agent.orchestrator import run_agent

router = APIRouter()

class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"
    mode: str = "both"
    ui_lang: str = "en"

@router.post("/analyze")
async def analyze_code(request: AnalyzeRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    try:
        result = await asyncio.wait_for(
            run_agent(code=request.code, language=request.language, mode=request.mode, ui_lang=request.ui_lang),
            timeout=90.0
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Analysis timed out. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
def get_languages():
    return {"languages": ["python", "java"]}
