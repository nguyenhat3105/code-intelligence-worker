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
                pylint_issues = json.loads(result.stdout)
                for issue in pylint_issues[:10]:
                    issues.append({
                        "line": issue.get("line", 0),
                        "type": issue.get("type", "warning"),
                        "message": issue.get("message", ""),
                        "symbol": issue.get("symbol", ""),
                        "tool": "pylint"
                    })
            except:
                pass
    except:
        pass
    finally:
        os.unlink(tmp_path)
    issues.extend(_basic_python_checks(code))
    return {"language": "python", "total_issues": len(issues), "issues": issues[:15]}

def _basic_python_checks(code: str) -> list:
    issues = []
    lines = code.split("\n")
    patterns = [
        (r"except\s*:", "Bare except clause catches all exceptions", "WARNING", "bare-except"),
        (r"eval\s*\(", "Use of eval() is a security risk", "ERROR", "security"),
        (r"exec\s*\(", "Use of exec() is a security risk", "ERROR", "security"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password detected", "ERROR", "security"),
        (r"TODO|FIXME|HACK", "Unresolved TODO/FIXME comment", "INFO", "code-quality"),
        (r"print\s*\(", "Consider using logging instead of print", "INFO", "style"),
        (r"import \*", "Wildcard import is not recommended", "WARNING", "style"),
        (r"== None", "Use 'is None' instead of '== None'", "WARNING", "style"),
        (r"== True|== False", "Use truthiness check instead of == True/False", "WARNING", "style"),
    ]
    for i, line in enumerate(lines, 1):
        for pattern, message, severity, symbol in patterns:
            if re.search(pattern, line):
                issues.append({"line": i, "type": severity, "message": message, "symbol": symbol, "tool": "basic-checker"})
    return issues

def _analyze_java(code: str) -> dict:
    issues = []
    lines = code.split("\n")
    patterns = [
        (r"catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}", "Empty catch block", "HIGH", "error-handling"),
        (r"System\.out\.print", "Use a logger instead of System.out.print", "INFO", "style"),
        (r"e\.printStackTrace\(\)", "Avoid printStackTrace(), use a logger", "WARNING", "style"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password detected", "HIGH", "security"),
        (r"TODO|FIXME|HACK", "Unresolved TODO/FIXME comment", "INFO", "code-quality"),
        (r"==\s*null|null\s*==", "Potential NullPointerException risk", "WARNING", "null-check"),
        (r"new\s+\w+\(\)", "Consider using factory methods or dependency injection", "INFO", "design"),
        (r"catch\s*\(Exception", "Catching generic Exception is not recommended", "WARNING", "error-handling"),
        (r"public\s+\w+\s+\w+\(.*\)\s*throws\s+Exception", "Avoid declaring 'throws Exception'", "WARNING", "design"),
    ]
    for i, line in enumerate(lines, 1):
        for pattern, message, severity, symbol in patterns:
            if re.search(pattern, line):
                issues.append({"line": i, "type": severity, "message": message, "symbol": symbol, "tool": "java-checker"})
    return {"language": "java", "total_issues": len(issues), "issues": issues[:15]}
