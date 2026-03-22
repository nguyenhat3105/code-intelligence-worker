from app.rag.knowledge_base import get_knowledge_base

def search_coding_standards(query: str, language: str) -> dict:
    kb = get_knowledge_base()
    results = kb.search(f"{language} {query}", n_results=3)
    return {"query": query, "language": language, "standards": results}

def search_test_patterns(code_context: str, framework: str) -> dict:
    kb = get_knowledge_base()
    results = kb.search(f"{framework} test pattern {code_context}", n_results=3)
    return {"framework": framework, "patterns": results}
