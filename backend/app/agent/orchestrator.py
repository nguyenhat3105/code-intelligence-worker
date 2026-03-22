import os
import json
import google.generativeai as genai
from app.tools.static_analyzer import run_static_analysis
from app.tools.rag_search import search_coding_standards, search_test_patterns

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

TOOLS = [
    {
        "function_declarations": [
            {
                "name": "run_static_analysis",
                "description": "Run static analysis on the source code to detect syntax errors, code smells, and potential bugs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Source code to analyze"},
                        "language": {"type": "string", "description": "Programming language: python or java"}
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "search_coding_standards",
                "description": "Search the knowledge base for relevant coding standards, best practices, and guidelines.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query about coding standards"},
                        "language": {"type": "string", "description": "Programming language"}
                    },
                    "required": ["query", "language"]
                }
            },
            {
                "name": "search_test_patterns",
                "description": "Search for relevant test patterns and examples for the given code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code_context": {"type": "string", "description": "Brief description of what the code does"},
                        "framework": {"type": "string", "description": "Test framework: pytest or junit"}
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

def build_system_prompt(mode: str) -> str:
    base = """You are an expert Senior Software Engineer acting as a Code Intelligence Worker.
Your job is to analyze source code using available tools and produce structured JSON output.

ALWAYS follow this workflow:
1. Call run_static_analysis first to detect raw issues
2. Call search_coding_standards to find relevant best practices
3. If generating tests, call search_test_patterns for patterns
4. Synthesize all results into the final JSON response

You MUST respond with valid JSON only (no markdown, no explanation outside JSON).
"""
    if mode == "review":
        return base + """
Return this exact JSON structure:
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
    "positive_aspects": ["list of good things in the code"]
  }
}
"""
    elif mode == "test":
        return base + """
Return this exact JSON structure:
{
  "tests": {
    "framework": "pytest or junit",
    "summary": "brief description of test strategy",
    "test_cases": [
      {
        "name": "test_function_name",
        "description": "what this test verifies",
        "type": "unit|edge_case|negative",
        "code": "complete test code here"
      }
    ],
    "coverage_areas": ["list of areas covered by tests"]
  }
}
"""
    else:
        return base + """
Return this exact JSON structure:
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
    "positive_aspects": ["list of good things in the code"]
  },
  "tests": {
    "framework": "pytest or junit",
    "summary": "brief description of test strategy",
    "test_cases": [
      {
        "name": "test_function_name",
        "description": "what this test verifies",
        "type": "unit|edge_case|negative",
        "code": "complete test code here"
      }
    ],
    "coverage_areas": ["list of areas covered by tests"]
  }
}
"""

async def run_agent(code: str, language: str, mode: str) -> dict:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=build_system_prompt(mode),
        tools=TOOLS,
    )

    framework = "pytest" if language == "python" else "junit"
    user_message = f"""Analyze the following {language} code:

```{language}
{code}
```

Language: {language}
Test framework: {framework}
Task: {"Code review only" if mode == "review" else "Generate tests only" if mode == "test" else "Code review AND test generation"}

Use all available tools, then return the final JSON result."""

    chat = model.start_chat()
    response = chat.send_message(user_message)

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        has_function_call = False

        for part in response.parts:
            if hasattr(part, "function_call") and part.function_call.name:
                has_function_call = True
                fn_name = part.function_call.name
                fn_args = dict(part.function_call.args)

                print(f"🔧 Tool called: {fn_name}({fn_args})")

                if fn_name in TOOL_MAP:
                    tool_result = TOOL_MAP[fn_name](**fn_args)
                else:
                    tool_result = {"error": f"Unknown tool: {fn_name}"}

                response = chat.send_message(
                    genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fn_name,
                                response={"result": json.dumps(tool_result)}
                            )
                        )]
                    )
                )

        if not has_function_call:
            break

    final_text = ""
    for part in response.parts:
        if hasattr(part, "text"):
            final_text += part.text

    clean = final_text.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        result = json.loads(clean)
        result["language"] = language
        return result
    except json.JSONDecodeError:
        return {
            "language": language,
            "review": {"summary": "Parse error", "score": 0, "issues": [], "positive_aspects": [], "raw": final_text},
            "tests": None
        }
