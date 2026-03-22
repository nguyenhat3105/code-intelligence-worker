import os
import numpy as np

_kb_instance = None

KNOWLEDGE_DOCS = [
    {"id": "py-001", "text": "Python: Use specific exceptions instead of bare except clauses. Always catch the most specific exception type. Example: 'except ValueError:' instead of 'except:'. Bare excepts hide bugs.", "metadata": {"language": "python", "category": "error-handling"}},
    {"id": "py-002", "text": "Python: Never use eval() or exec() with user-provided input. These execute arbitrary code and are security vulnerabilities. Use ast.literal_eval() for safe evaluation.", "metadata": {"language": "python", "category": "security"}},
    {"id": "py-003", "text": "Python: Use 'is None' and 'is not None' instead of '== None'. The 'is' operator checks identity, which is correct for None comparisons.", "metadata": {"language": "python", "category": "style"}},
    {"id": "py-004", "text": "Python: Use logging module instead of print statements in production. Configure logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.", "metadata": {"language": "python", "category": "style"}},
    {"id": "py-005", "text": "Python: Never hardcode passwords or API keys. Use environment variables: os.environ.get('SECRET_KEY') or config files excluded from version control.", "metadata": {"language": "python", "category": "security"}},
    {"id": "py-006", "text": "Python: Use list comprehensions and generators for better performance. Use generators for large datasets to save memory.", "metadata": {"language": "python", "category": "performance"}},
    {"id": "py-007", "text": "Python: Follow PEP 8. Functions/variables: snake_case. Classes: PascalCase. Constants: UPPER_SNAKE_CASE.", "metadata": {"language": "python", "category": "style"}},
    {"id": "java-001", "text": "Java: Use SLF4J + Logback instead of System.out.println. Define: private static final Logger logger = LoggerFactory.getLogger(ClassName.class);", "metadata": {"language": "java", "category": "style"}},
    {"id": "java-002", "text": "Java: Never catch generic Exception. Catch specific exceptions. Never leave catch blocks empty — at minimum log the error.", "metadata": {"language": "java", "category": "error-handling"}},
    {"id": "java-003", "text": "Java: Use Optional<T> instead of returning null. Makes API contract explicit and prevents NullPointerException.", "metadata": {"language": "java", "category": "null-safety"}},
    {"id": "java-004", "text": "Java: Use StringBuilder for string concatenation in loops. String + in loops creates many intermediate objects.", "metadata": {"language": "java", "category": "performance"}},
    {"id": "java-005", "text": "Java: Follow SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.", "metadata": {"language": "java", "category": "design"}},
    {"id": "java-006", "text": "Java: Never hardcode credentials. Use environment variables or a secrets manager like HashiCorp Vault.", "metadata": {"language": "java", "category": "security"}},
    {"id": "java-007", "text": "Java: Always close resources with try-with-resources. Example: try (InputStream is = new FileInputStream(file)) { ... }", "metadata": {"language": "java", "category": "resource-management"}},
    {"id": "pytest-001", "text": "pytest: Use fixtures for setup. @pytest.fixture def client(): return TestClient(app). Use conftest.py for shared fixtures.", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-002", "text": "pytest: Use @pytest.mark.parametrize for multiple inputs. @pytest.mark.parametrize('input,expected', [(1,2),(2,4)]) def test_double(input, expected): assert double(input) == expected", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-003", "text": "pytest: Use pytest.raises() for exception testing. with pytest.raises(ValueError, match='invalid'): my_function(-1)", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-004", "text": "pytest: Use unittest.mock for mocking. @patch('module.service') def test_func(mock_svc): mock_svc.return_value = 'mocked'", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-005", "text": "pytest best practices: AAA pattern (Arrange, Act, Assert). One behavior per test. Descriptive test names.", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "junit-001", "text": "JUnit 5: Use @Test, @BeforeEach, @AfterEach. Use @DisplayName for readable names.", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-002", "text": "JUnit 5: Use @ParameterizedTest with @ValueSource or @CsvSource for data-driven tests.", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-003", "text": "JUnit 5: Use assertThrows() for exceptions. Exception ex = assertThrows(IllegalArgumentException.class, () -> service.process(null));", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-004", "text": "JUnit 5 + Mockito: @ExtendWith(MockitoExtension.class). @Mock UserRepository repo; @InjectMocks UserService svc; when(repo.findById(1L)).thenReturn(Optional.of(user));", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-005", "text": "JUnit best practices: AAA pattern. One assertion concept per test. Naming: methodName_stateUnderTest_expectedBehavior.", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "security-001", "text": "OWASP: Prevent SQL Injection with parameterized queries. Never concatenate user input into SQL. cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))", "metadata": {"language": "all", "category": "security"}},
    {"id": "security-002", "text": "OWASP: Validate and sanitize all user inputs. Check type, length, format, range. Reject invalid input early.", "metadata": {"language": "all", "category": "security"}},
    {"id": "security-003", "text": "OWASP: Use bcrypt, scrypt, or Argon2 for password hashing. Never use MD5/SHA-1. Never store plain-text passwords.", "metadata": {"language": "all", "category": "security"}},
]


def _simple_embed(text: str, dim: int = 128) -> np.ndarray:
    """Lightweight trigram-hashing embedding — no external model, no C++ needed."""
    vec = np.zeros(dim, dtype=np.float32)
    text_lower = text.lower()
    for i in range(len(text_lower) - 2):
        h = hash(text_lower[i:i+3]) % dim
        vec[h] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


class KnowledgeBase:
    def __init__(self):
        self._documents = []
        self._metadatas = []
        self._index = None
        self._dim = 128
        self._setup()

    def _setup(self):
        import faiss
        self._faiss = faiss
        self._index = faiss.IndexFlatIP(self._dim)
        self._ingest()

    def _ingest(self):
        print(f"📚 Building knowledge base with {len(KNOWLEDGE_DOCS)} documents...")
        vectors = []
        for doc in KNOWLEDGE_DOCS:
            self._documents.append(doc["text"])
            self._metadatas.append(doc["metadata"])
            vectors.append(_simple_embed(doc["text"], self._dim))
        matrix = np.stack(vectors).astype(np.float32)
        self._index.add(matrix)
        print(f"✅ Knowledge base ready! ({self._index.ntotal} vectors indexed)")

    def search(self, query: str, n_results: int = 3) -> list:
        query_vec = _simple_embed(query, self._dim).reshape(1, -1)
        k = min(n_results, self._index.ntotal)
        distances, indices = self._index.search(query_vec, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:
                results.append({
                    "content": self._documents[idx],
                    "metadata": self._metadatas[idx],
                    "score": float(dist)
                })
        return results


def init_knowledge_base():
    global _kb_instance
    _kb_instance = KnowledgeBase()


def get_knowledge_base() -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
