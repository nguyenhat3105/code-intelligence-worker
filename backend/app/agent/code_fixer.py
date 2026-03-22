import os
import json
import difflib
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""), timeout=60.0)
MODEL = "llama-3.3-70b-versatile"

def compute_diff(old_code: str, new_code: str) -> list:
    old_lines = old_code.splitlines()
    new_lines = new_code.splitlines()
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    result = []; old_num = 1; new_num = 1
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for line in old_lines[i1:i2]:
                result.append({'type':'unchanged','line_old':old_num,'line_new':new_num,'content':line}); old_num+=1; new_num+=1
        elif tag == 'delete':
            for line in old_lines[i1:i2]:
                result.append({'type':'removed','line_old':old_num,'line_new':None,'content':line}); old_num+=1
        elif tag == 'insert':
            for line in new_lines[j1:j2]:
                result.append({'type':'added','line_old':None,'line_new':new_num,'content':line}); new_num+=1
        elif tag == 'replace':
            for line in old_lines[i1:i2]:
                result.append({'type':'removed','line_old':old_num,'line_new':None,'content':line}); old_num+=1
            for line in new_lines[j1:j2]:
                result.append({'type':'added','line_old':None,'line_new':new_num,'content':line}); new_num+=1
    return result

def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith('```'):
        lines = t.split('\n')
        t = '\n'.join(lines[1:-1] if lines[-1].strip()=='```' else lines[1:])
    start, end = t.find('{'), t.rfind('}')+1
    if start != -1 and end > start: return t[start:end]
    return t

async def preview_single_fix(code: str, language: str, issue: dict, ui_lang: str = 'en') -> dict:
    is_vi = ui_lang == 'vi'
    lang_instr = 'Respond in Vietnamese for reason, pros, cons, what_changed fields.' if is_vi else 'Respond in English.'
    prompt = f"""Fix this ONE issue in the code.

Issue: Line {issue.get('line','?')} | {issue.get('severity','')} | {issue.get('title','')}
Description: {issue.get('description','')}
Suggestion: {issue.get('suggestion','')}

Code:
```{language}
{code}
```

{lang_instr}

Return ONLY JSON:
{{"fixed_code":"...","reason":"why this fix is needed","what_changed":"exact location and what was changed","pros":["benefit1","benefit2"],"cons":["tradeoff1"]}}"""
    resp = client.chat.completions.create(model=MODEL, messages=[{"role":"system","content":"Code refactoring expert. Return only JSON."},{"role":"user","content":prompt}], max_tokens=2000, temperature=0.1)
    raw = _strip_fences(resp.choices[0].message.content or '')
    try:
        data = json.loads(raw)
        fc = data.get('fixed_code', code)
        if fc.strip().startswith('```'):
            lines = fc.strip().split('\n'); fc = '\n'.join(lines[1:-1] if lines[-1].strip()=='```' else lines[1:])
        diff = compute_diff(code, fc.strip())
        return {'fixed_code':fc.strip(),'diff':diff,'reason':data.get('reason',''),'what_changed':data.get('what_changed',''),'pros':data.get('pros',[]),'cons':data.get('cons',[]),'changes_count':sum(1 for d in diff if d['type']!='unchanged')}
    except Exception as e:
        return {'fixed_code':code,'diff':[],'reason':str(e),'what_changed':'','pros':[],'cons':[],'changes_count':0}

async def preview_all_fixes(code: str, language: str, issues: list, ui_lang: str = 'en') -> dict:
    is_vi = ui_lang == 'vi'
    lang_instr = 'Respond in Vietnamese for reason, pros, cons, what_changed fields.' if is_vi else 'Respond in English.'
    issues_text = '\n'.join([f"{i+1}. L{iss.get('line','?')} [{iss.get('severity','')}] {iss.get('title','')} — {iss.get('suggestion','')}" for i,iss in enumerate(issues)])
    prompt = f"""Fix ALL issues in the code.

Issues:\n{issues_text}\n
Code:\n```{language}\n{code}\n```\n\n{lang_instr}\n\nReturn ONLY JSON:\n{{"fixed_code":"...","reason":"summary of all changes","what_changed":"all specific changes made","pros":["b1","b2"],"cons":["t1"]}}"""
    resp = client.chat.completions.create(model=MODEL, messages=[{"role":"system","content":"Code refactoring expert. Return only JSON."},{"role":"user","content":prompt}], max_tokens=3000, temperature=0.1)
    raw = _strip_fences(resp.choices[0].message.content or '')
    try:
        data = json.loads(raw)
        fc = data.get('fixed_code', code)
        if fc.strip().startswith('```'):
            lines = fc.strip().split('\n'); fc = '\n'.join(lines[1:-1] if lines[-1].strip()=='```' else lines[1:])
        diff = compute_diff(code, fc.strip())
        return {'fixed_code':fc.strip(),'diff':diff,'reason':data.get('reason',''),'what_changed':data.get('what_changed',''),'pros':data.get('pros',[]),'cons':data.get('cons',[]),'changes_count':sum(1 for d in diff if d['type']!='unchanged')}
    except Exception as e:
        return {'fixed_code':code,'diff':[],'reason':str(e),'what_changed':'','pros':[],'cons':[],'changes_count':0}

# backward compat
async def apply_single_fix(code,language,issue,ui_lang='en'):
    r = await preview_single_fix(code,language,issue,ui_lang); return r['fixed_code']
async def apply_all_fixes(code,language,issues,ui_lang='en'):
    r = await preview_all_fixes(code,language,issues,ui_lang); return r['fixed_code']
