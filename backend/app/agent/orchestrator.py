import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from app.tools.static_analyzer import run_static_analysis
from app.tools.rag_search import search_coding_standards, search_test_patterns

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

# Model fallback list — tries each in order until one works
MODEL_PRIORITY = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
]

TOOLS = [
    {
        "function_declarations": [
            {
                "name": "run_static_analysis",
                "description": "Run static analysis on source code to detect syntax errors, code smells, and bugs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"}
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "search_coding_standards",
                "description": "Search the knowledge base for coding standards and best practices.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "language": {"type": "string"}
                    },
                    "required": ["query", "language"]
                }
            },
            {
                "name": "search_test_patterns",
                "description": "Search for relevant test patterns and examples.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code_context": {"type": "string"},
                        "framework": {"type": "string"}
                    },
                    "required": ["code_context", "framework"]
                }
            }
        ]
    }
]

TOOL_MAP = {
    "run_static_analysis": run_static_analysis,
    "search_coding_standards": search_coding_standards,
    "search_test_patterns": search_test_patterns,
}

REVIEW_JSON = """
{
  "review": {
    "summary": "brief overall assessment",
    "score": 75,
    "issues": [
      {
        "line": 12,
        "severity": "HIGH",
        "category": "Security|Performance|Style|Bug",
        "title": "short title",
        "description": "detailed explanation",
        "suggestion": "how to fix"
      }
    ],
    "positive_aspects": ["good things in the code"]
  }
}
"""

TEST_JSON = """
{
  "tests": {
    "framework": "pytest or junit",
    "summary": "test strategy description",
    "test_cases": [
      {
        "name": "test_function_name",
        "description": "what this test verifies",
        "type": "unit|edge_case|negative",
        "code": "complete test code here"
      }
    ],
    "coverage_areas": ["areas covered"]
  }
}
"""

BOTH_JSON = """
{
  "review": {
    "summary": "brief overall assessment",
    "score": 75,
    "issues": [
      {
        "line": 12,
        "severity": "HIGH",
        "category": "Security|Performance|Style|Bug",
        "title": "short title",
        "description": "detailed explanation",
        "suggestion": "how to fix"
      }
    ],
    "positive_aspects": ["good things"]
  },
  "tests": {
    "framework": "pytest or junit",
    "summary": "test strategy description",
    "test_cases": [
      {
        "name": "test_function_name",
        "description": "what this test verifies",
        "type": "unit|edge_case|negative",
        "code": "complete test code here"
      }
    ],
    "coverage_areas": ["areas covered"]
  }
}
"""

def build_system_prompt(mode: str) -> str:
    base = """You are an expert Senior Software Engineer acting as a Code Intelligence Worker.
Analyze source code using the available tools and produce structured JSON output.

Workflow:
1. Call run_static_analysis to detect raw issues
2. Call search_coding_standards for best practices
3. If generating tests, call search_test_patterns
4. Return ONLY valid JSON, no markdown or extra text.
"""
    if mode == "review":
        return base + "Return this JSON structure:" + REVIEW_JSON
    elif mode == "test":
        return base + "Return this JSON structure:" + TEST_JSON
    else:
        return base + "Return this JSON structure:" + BOTH_JSON

async def _call_model(model_name: str, system_prompt: str, user_message: str):
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
        tools=TOOLS,
    )
    chat = model.start_chat()
    response = chat.send_message(user_message)

    for _ in range(5):
        has_fn = False
        for part in response.parts:
            if hasattr(part, "function_call") and part.function_call.name:
                has_fn = True
                fn_name = part.function_call.name
                fn_args = dict(part.function_call.args)
                print(f"🔧 [{model_name}] {fn_name}({list(fn_args.keys())})")
                tool_result = TOOL_MAP.get(fn_name, lambda **k: {"error": "unknown"})(**fn_args)
                response = chat.send_message(
                    genai.protos.Content(parts=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn_name,
                            response={"result": json.dumps(tool_result)}
                        )
                    )])
                )
        if not has_fn:
            break
    return response

async def run_agent(code: str, language: str, mode: str) -> dict:
    framework = "pytest" if language == "python" else "junit"
    system_prompt = build_system_prompt(mode)
    user_message = f"""Analyze this {language} code:\n\n```{language}\n{code}\n```\n\nLanguage: {language} | Framework: {framework} | Task: {mode}\nUse all tools, then return the final JSON."""

    last_error = None
    final_text = ""
    for model_name in MODEL_PRIORITY:
        try:
            print(f"🤖 Trying model: {model_name}")
            response = await _call_model(model_name, system_prompt, user_message)
            final_text = "".join(p.text for p in response.parts if hasattr(p, "text"))
            clean = final_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            clean = clean.strip()
            result = json.loads(clean)
            result["language"] = language
            print(f"✅ Success with: {model_name}")
            return result
        except json.JSONDecodeError:
            return {
                "language": language,
                "review": {"summary": "Parse error", "score": 0, "issues": [], "positive_aspects": [], "raw": final_text},
                "tests": None
            }
        except Exception as e:
            last_error = str(e)
            print(f"⚠️  {model_name} failed: {e}")
            if "429" in str(e) or "quota" in str(e).lower() or "not found" in str(e).lower() or "404" in str(e):
                continue
            raise

    raise Exception(f"All models exhausted. Last error: {last_error}")
