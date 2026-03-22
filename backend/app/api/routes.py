from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agent.orchestrator import run_agent

router = APIRouter()

class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"  # python | java
    mode: str = "both"        # review | test | both

class AnalyzeResponse(BaseModel):
    review: dict | None = None
    tests: dict | None = None
    language: str

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    try:
        result = await run_agent(
            code=request.code,
            language=request.language,
            mode=request.mode
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
def get_languages():
    return {"languages": ["python", "java"]}
