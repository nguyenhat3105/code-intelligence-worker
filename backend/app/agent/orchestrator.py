import os
import json
from dotenv import load_dotenv
from groq import Groq
from app.tools.static_analyzer import run_static_analysis
from app.tools.rag_search import search_coding_standards, search_test_patterns

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY", ""),
    timeout=60.0,
)

MODEL = "llama-3.3-70b-versatile"

TOOLS = [
    {"type": "function", "function": {"name": "run_static_analysis", "description": "Run static analysis on source code.", "parameters": {"type": "object", "properties": {"code": {"type": "string"}, "language": {"type": "string"}}, "required": ["code", "language"]}}},
    {"type": "function", "function": {"name": "search_coding_standards", "description": "Search knowledge base for coding standards.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "language": {"type": "string"}}, "required": ["query", "language"]}}},
    {"type": "function", "function": {"name": "search_test_patterns", "description": "Search for test patterns.", "parameters": {"type": "object", "properties": {"code_context": {"type": "string"}, "framework": {"type": "string"}}, "required": ["code_context", "framework"]}}}
]

TOOL_MAP = {
    "run_static_analysis": run_static_analysis,
    "search_coding_standards": search_coding_standards,
    "search_test_patterns": search_test_patterns,
}

BOTH_JSON = """{\n  \"review\": {\n    \"summary\": \"brief assessment\",\n    \"score\": 75,\n    \"issues\": [{\"line\": 1, \"severity\": \"HIGH\", \"category\": \"Security\", \"title\": \"t\", \"description\": \"d\", \"suggestion\": \"s\"}],\n    \"positive_aspects\": [\"good\"]\n  },\n  \"tests\": {\n    \"framework\": \"pytest\",\n    \"summary\": \"strategy\",\n    \"test_cases\": [{\"name\": \"test_x\", \"description\": \"d\", \"type\": \"unit\", \"code\": \"def test_x(): pass\"}],\n    \"coverage_areas\": [\"area\"]\n  }\n}"""

REVIEW_JSON = """{\n  \"review\": {\n    \"summary\": \"brief assessment\",\n    \"score\": 75,\n    \"issues\": [{\"line\": 1, \"severity\": \"HIGH\", \"category\": \"Security\", \"title\": \"t\", \"description\": \"d\", \"suggestion\": \"s\"}],\n    \"positive_aspects\": [\"good\"]\n  }\n}"""

TEST_JSON = """{\n  \"tests\": {\n    \"framework\": \"pytest\",\n    \"summary\": \"strategy\",\n    \"test_cases\": [{\"name\": \"test_x\", \"description\": \"d\", \"type\": \"unit\", \"code\": \"def test_x(): pass\"}],\n    \"coverage_areas\": [\"area\"]\n  }\n}"""

def build_system_prompt(mode: str) -> str:
    schema = REVIEW_JSON if mode == "review" else TEST_JSON if mode == "test" else BOTH_JSON
    return f"""You are a Senior Software Engineer doing code analysis.\nUse the provided tools, then return ONLY raw JSON (no markdown, no ```json).\n\nSTEPS:\n1. Call run_static_analysis\n2. Call search_coding_standards\n3. If tests needed, call search_test_patterns\n4. Return ONLY this JSON schema (filled with real data):\n{schema}"""

async def run_agent(code: str, language: str, mode: str) -> dict:
    framework = "pytest" if language == "python" else "junit"
    messages = [
        {"role": "system", "content": build_system_prompt(mode)},
        {"role": "user", "content": f"Analyze this {language} code:\n\n```{language}\n{code[:3000]}\n```\n\nLanguage: {language}, Framework: {framework}, Mode: {mode}"}
    ]
    print(f"\ud83d\ude80 Groq agent | model={MODEL} | mode={mode}")
    final_message = None
    for iteration in range(8):
        print(f"  iter {iteration+1}")
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto", max_tokens=3000, temperature=0.1)
        message = response.choices[0].message
        final_message = message
        assistant_msg = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            assistant_msg["tool_calls"] = message.tool_calls
        messages.append(assistant_msg)
        if not message.tool_calls:
            print("  \u2705 Done")
            break
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments)
            except:
                fn_args = {}
            print(f"  \ud83d\udd27 {fn_name}")
            tool_result = TOOL_MAP.get(fn_name, lambda **k: {"error": "unknown"})(**fn_args)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tool_result)[:2000]})
    final_text = (final_message.content or "") if final_message else ""
    clean = final_text.strip()
    if "```" in clean:
        for part in clean.split("```"):
            p = part.strip().lstrip("json").strip()
            if p.startswith("{"):
                clean = p; break
    start, end = clean.find("{"), clean.rfind("}") + 1
    if start != -1 and end > start:
        clean = clean[start:end]
    try:
        result = json.loads(clean)
        result["language"] = language
        return result
    except:
        return {"language": language, "review": {"summary": f"Parse error. Raw: {final_text[:200]}", "score": 50, "issues": [], "positive_aspects": []}, "tests": None}
