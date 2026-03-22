import subprocess
import tempfile
import os
import re

def run_static_analysis(code: str, language: str) -> dict:
    if language == "python":
        return _analyze_python(code)
    elif language == "java":
        return _analyze_java(code)
    return {"issues": [], "language": language}

def _analyze_python(code: str) -> dict:
    issues = []
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ["pylint", tmp_path, "--output-format=json", "--disable=C0114,C0115,C0116"],
            capture_output=True, text=True, timeout=15
        )
        import json
        if result.stdout.strip():
            try:
                for issue in json.loads(result.stdout)[:10]:
                    issues.append({
                        "line": issue.get("line", 0),
                        "type": issue.get("type", "warning"),
                        "message": issue.get("message", ""),
                        "symbol": issue.get("symbol", ""),
                        "tool": "pylint"
                    })
            except Exception:
                pass
    except Exception:
        pass
    finally:
        os.unlink(tmp_path)
    issues.extend(_basic_python_checks(code))
    return {"language": "python", "total_issues": len(issues), "issues": issues[:15]}

def _basic_python_checks(code: str) -> list:
    issues = []
    patterns = [
        (r"except\s*:", "Bare except clause", "WARNING", "bare-except"),
        (r"eval\s*\(", "Use of eval() is a security risk", "ERROR", "security"),
        (r"exec\s*\(", "Use of exec() is a security risk", "ERROR", "security"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password", "ERROR", "security"),
        (r"TODO|FIXME|HACK", "Unresolved TODO/FIXME", "INFO", "code-quality"),
        (r"print\s*\(", "Use logging instead of print", "INFO", "style"),
        (r"import \*", "Wildcard import not recommended", "WARNING", "style"),
        (r"== None", "Use 'is None' instead", "WARNING", "style"),
        (r"== True|== False", "Use truthiness check", "WARNING", "style"),
    ]
    for i, line in enumerate(code.split("\n"), 1):
        for pattern, message, severity, symbol in patterns:
            if re.search(pattern, line):
                issues.append({"line": i, "type": severity, "message": message, "symbol": symbol, "tool": "basic-checker"})
    return issues

def _analyze_java(code: str) -> dict:
    issues = []
    patterns = [
        (r"catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}", "Empty catch block", "HIGH", "error-handling"),
        (r"System\.out\.print", "Use a logger instead", "INFO", "style"),
        (r"e\.printStackTrace\(\)", "Avoid printStackTrace()", "WARNING", "style"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password", "HIGH", "security"),
        (r"TODO|FIXME|HACK", "Unresolved TODO/FIXME", "INFO", "code-quality"),
        (r"==\s*null|null\s*==", "Potential NullPointerException", "WARNING", "null-check"),
        (r"catch\s*\(Exception", "Catching generic Exception", "WARNING", "error-handling"),
        (r"public\s+\w+\s+\w+\(.*\)\s*throws\s+Exception", "Avoid throws Exception", "WARNING", "design"),
    ]
    for i, line in enumerate(code.split("\n"), 1):
        for pattern, message, severity, symbol in patterns:
            if re.search(pattern, line):
                issues.append({"line": i, "type": severity, "message": message, "symbol": symbol, "tool": "java-checker"})
    return {"language": "java", "total_issues": len(issues), "issues": issues[:15]}
