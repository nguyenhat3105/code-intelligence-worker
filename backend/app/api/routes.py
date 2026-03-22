from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from app.agent.orchestrator import run_agent
from app.agent.code_fixer import preview_single_fix, preview_all_fixes

router = APIRouter()

class AnalyzeRequest(BaseModel):
    code: str; language: str = 'python'; mode: str = 'both'; ui_lang: str = 'en'

class PreviewFixRequest(BaseModel):
    code: str; language: str = 'python'; ui_lang: str = 'en'; issue: dict

class PreviewAllFixesRequest(BaseModel):
    code: str; language: str = 'python'; ui_lang: str = 'en'; issues: list

@router.post('/analyze')
async def analyze_code(req: AnalyzeRequest):
    if not req.code.strip(): raise HTTPException(400, 'Code cannot be empty')
    try:
        return await asyncio.wait_for(run_agent(code=req.code,language=req.language,mode=req.mode,ui_lang=req.ui_lang), timeout=90.0)
    except asyncio.TimeoutError: raise HTTPException(504,'Analysis timed out.')
    except Exception as e: raise HTTPException(500, str(e))

@router.post('/preview-fix')
async def preview_fix(req: PreviewFixRequest):
    if not req.code.strip(): raise HTTPException(400,'Code cannot be empty')
    try:
        return await asyncio.wait_for(preview_single_fix(code=req.code,language=req.language,issue=req.issue,ui_lang=req.ui_lang), timeout=45.0)
    except asyncio.TimeoutError: raise HTTPException(504,'Preview timed out.')
    except Exception as e: raise HTTPException(500, str(e))

@router.post('/preview-all-fixes')
async def preview_all(req: PreviewAllFixesRequest):
    if not req.code.strip(): raise HTTPException(400,'Code cannot be empty')
    if not req.issues: raise HTTPException(400,'No issues provided')
    try:
        return await asyncio.wait_for(preview_all_fixes(code=req.code,language=req.language,issues=req.issues,ui_lang=req.ui_lang), timeout=60.0)
    except asyncio.TimeoutError: raise HTTPException(504,'Preview timed out.')
    except Exception as e: raise HTTPException(500, str(e))

@router.get('/languages')
def get_languages(): return {'languages':['python','java']}
