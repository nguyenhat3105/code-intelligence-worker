import os
import json
from dotenv import load_dotenv
from groq import Groq
from app.tools.static_analyzer import run_static_analysis
from app.tools.rag_search import search_coding_standards, search_test_patterns

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
MODEL = "llama-3.3-70b-versatile"

TOOLS = [
    {
        "type": "function",
        "function": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_coding_standards",
            "description": "Search the knowledge base for relevant coding standards and best practices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "language": {"type": "string"}
                },
                "required": ["query", "language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
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
    }
]

TOOL_MAP = {
    "run_static_analysis": run_static_analysis,
    "search_coding_standards": search_coding_standards,
    "search_test_patterns": search_test_patterns,
}

REVIEW_JSON = """
{
  \"review\": {
    \"summary\": \"brief overall assessment\",
    \"score\": 75,
    \"issues\": [
      {
        \"line\": 12,
        \"severity\": \"HIGH\",
        \"category\": \"Security\",
        \"title\": \"short title\",
        \"description\": \"detailed explanation\",
        \"suggestion\": \"how to fix\"
      }
    ],
    \"positive_aspects\": [\"good things in the code\"]
  }
}"""

TEST_JSON = """
{
  \"tests\": {
    \"framework\": \"pytest or junit\",
    \"summary\": \"test strategy description\",
    \"test_cases\": [
      {
        \"name\": \"test_function_name\",
        \"description\": \"what this test verifies\",
        \"type\": \"unit\",
        \"code\": \"complete test code here\"
      }
    ],
    \"coverage_areas\": [\"areas covered\"]
  }
}"""

BOTH_JSON = """
{
  \"review\": {
    \"summary\": \"brief overall assessment\",
    \"score\": 75,
    \"issues\": [
      {
        \"line\": 12,
        \"severity\": \"HIGH\",
        \"category\": \"Security\",
        \"title\": \"short title\",
        \"description\": \"detailed explanation\",
        \"suggestion\": \"how to fix\"
      }
    ],
    \"positive_aspects\": [\"good things\"]
  },
  \"tests\": {
    \"framework\": \"pytest or junit\",
    \"summary\": \"test strategy description\",
    \"test_cases\": [
      {
        \"name\": \"test_function_name\",
        \"description\": \"what this test verifies\",
        \"type\": \"unit\",
        \"code\": \"complete test code here\"
      }
    ],
    \"coverage_areas\": [\"areas covered\"]
  }
}"""

def build_system_prompt(mode: str) -> str:
    base = """You are an expert Senior Software Engineer acting as a Code Intelligence Worker.
Analyze source code using the available tools and produce structured JSON output.

IMPORTANT:
- You MUST call the tools before giving your final answer
- Always call run_static_analysis first
- Then call search_coding_standards
- If mode includes tests, call search_test_patterns
- Your FINAL response must be ONLY valid JSON, no markdown fences, no explanation
"""
    if mode == "review":
        return base + "\nReturn ONLY this JSON structure (no markdown):" + REVIEW_JSON
    elif mode == "test":
        return base + "\nReturn ONLY this JSON structure (no markdown):" + TEST_JSON
    else:
        return base + "\nReturn ONLY this JSON structure (no markdown):" + BOTH_JSON

async def run_agent(code: str, language: str, mode: str) -> dict:
    framework = "pytest" if language == "python" else "junit"
    messages = [
        {"role": "system", "content": build_system_prompt(mode)},
        {"role": "user", "content": f"""Analyze this {language} code:\n\n```{language}\n{code}\n```\n\nLanguage: {language} | Framework: {framework} | Task: {mode}\nCall all tools first, then return the final JSON result."""}
    ]

    for iteration in range(6):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=4096,
            temperature=0.1,
        )
        message = response.choices[0].message
        messages.append({"role": "assistant", "content": message.content or "", "tool_calls": message.tool_calls})

        if not message.tool_calls:
            print(f"✅ Agent finished after {iteration} tool iterations")
            break

        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            print(f"🔧 Tool: {fn_name}({list(fn_args.keys())})")
            tool_result = TOOL_MAP.get(fn_name, lambda **k: {"error": "unknown"})(**fn_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

    final_text = message.content or ""
    clean = final_text.strip()
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                clean = part
                break
    start = clean.find("{")
    end = clean.rfind("}") + 1
    if start != -1 and end > start:
        clean = clean[start:end]

    try:
        result = json.loads(clean)
        result["language"] = language
        return result
    except json.JSONDecodeError:
        return {
            "language": language,
            "review": {"summary": "Parse error", "score": 50, "issues": [], "positive_aspects": [], "raw": final_text},
            "tests": None
        }
