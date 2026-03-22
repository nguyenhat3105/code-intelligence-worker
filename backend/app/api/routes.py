from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
from app.agent.orchestrator import run_agent
from app.agent.code_fixer import apply_single_fix, apply_all_fixes

router = APIRouter()

class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"
    mode: str = "both"
    ui_lang: str = "en"

class ApplySingleFixRequest(BaseModel):
    code: str
    language: str = "python"
    ui_lang: str = "en"
    issue: dict

class ApplyAllFixesRequest(BaseModel):
    code: str
    language: str = "python"
    ui_lang: str = "en"
    issues: list

@router.post("/analyze")
async def analyze_code(request: AnalyzeRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    try:
        result = await asyncio.wait_for(run_agent(code=request.code, language=request.language, mode=request.mode, ui_lang=request.ui_lang), timeout=90.0)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Analysis timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-fix")
async def apply_fix(request: ApplySingleFixRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    try:
        fixed_code = await asyncio.wait_for(apply_single_fix(code=request.code, language=request.language, issue=request.issue, ui_lang=request.ui_lang), timeout=30.0)
        return {"fixed_code": fixed_code, "language": request.language}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Fix timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-all-fixes")
async def apply_all(request: ApplyAllFixesRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if not request.issues:
        raise HTTPException(status_code=400, detail="No issues provided")
    try:
        fixed_code = await asyncio.wait_for(apply_all_fixes(code=request.code, language=request.language, issues=request.issues, ui_lang=request.ui_lang), timeout=60.0)
        return {"fixed_code": fixed_code, "language": request.language}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Fix timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
def get_languages():
    return {"languages": ["python", "java"]}
