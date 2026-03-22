import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""), timeout=60.0)
MODEL = "llama-3.3-70b-versatile"

async def apply_single_fix(code: str, language: str, issue: dict, ui_lang: str = "en") -> str:
    prompt = f"""You are a code refactoring expert. Apply EXACTLY ONE fix to the code.

Issue to fix:
- Line: {issue.get('line', 'unknown')}
- Problem: {issue.get('title', '')}
- Suggestion: {issue.get('suggestion', '')}

Original {language} code:
```{language}
{code}
```

Rules:
1. Fix ONLY the specific issue mentioned above
2. Do NOT change anything else
3. Return ONLY the fixed code, no explanation, no markdown fences"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a precise code refactoring tool. Return only the fixed code."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000, temperature=0.1
    )
    fixed = (response.choices[0].message.content or code).strip()
    if fixed.startswith("```"):
        lines = fixed.split("\n")
        fixed = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return fixed.strip()

async def apply_all_fixes(code: str, language: str, issues: list, ui_lang: str = "en") -> str:
    issues_text = "\n".join([f"{i+1}. Line {iss.get('line','?')}: {iss.get('title','')} — Fix: {iss.get('suggestion','')}" for i, iss in enumerate(issues)])
    prompt = f"""You are a code refactoring expert. Apply ALL the following fixes to the code.

Issues to fix:
{issues_text}

Original {language} code:
```{language}
{code}
```

Rules:
1. Apply ALL fixes listed above
2. Keep overall structure and logic intact
3. Return ONLY the fixed code, no explanation, no markdown fences"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a precise code refactoring tool. Return only the fixed code."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000, temperature=0.1
    )
    fixed = (response.choices[0].message.content or code).strip()
    if fixed.startswith("```"):
        lines = fixed.split("\n")
        fixed = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return fixed.strip()
