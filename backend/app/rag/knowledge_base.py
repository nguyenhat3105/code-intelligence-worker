import os
import chromadb
from chromadb.utils import embedding_functions

_kb_instance = None

KNOWLEDGE_DOCS = [
    {"id": "py-001", "text": "Python: Use specific exceptions instead of bare except clauses. Always catch the most specific exception type possible. Example: use 'except ValueError:' instead of 'except:'. Bare excepts hide bugs and make debugging difficult.", "metadata": {"language": "python", "category": "error-handling"}},
    {"id": "py-002", "text": "Python: Never use eval() or exec() with user-provided input. These functions execute arbitrary code and are a major security vulnerability. Use ast.literal_eval() for safe evaluation of Python literals.", "metadata": {"language": "python", "category": "security"}},
    {"id": "py-003", "text": "Python: Use 'is None' and 'is not None' instead of '== None'. The 'is' operator checks identity, which is correct for None comparisons.", "metadata": {"language": "python", "category": "style"}},
    {"id": "py-004", "text": "Python: Use logging module instead of print statements in production code. Configure logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL). Example: import logging; logger = logging.getLogger(__name__); logger.info('message')", "metadata": {"language": "python", "category": "style"}},
    {"id": "py-005", "text": "Python: Never hardcode passwords, API keys, or secrets in source code. Use environment variables (os.environ.get('SECRET_KEY')) or configuration files excluded from version control.", "metadata": {"language": "python", "category": "security"}},
    {"id": "py-006", "text": "Python: Use list comprehensions and generator expressions for better performance and readability. Use generators for large datasets to save memory.", "metadata": {"language": "python", "category": "performance"}},
    {"id": "py-007", "text": "Python: Follow PEP 8 naming conventions. Functions and variables: snake_case. Classes: PascalCase. Constants: UPPER_SNAKE_CASE.", "metadata": {"language": "python", "category": "style"}},
    {"id": "java-001", "text": "Java: Always use a logging framework (SLF4J + Logback, or Log4j2) instead of System.out.println or printStackTrace(). Define a logger per class: private static final Logger logger = LoggerFactory.getLogger(ClassName.class);", "metadata": {"language": "java", "category": "style"}},
    {"id": "java-002", "text": "Java: Never catch generic Exception or Throwable unless at the top-level boundary. Catch specific exceptions. Never leave catch blocks empty — at minimum log the error.", "metadata": {"language": "java", "category": "error-handling"}},
    {"id": "java-003", "text": "Java: Use Optional<T> to represent values that may be absent instead of returning null. This makes the API contract explicit and prevents NullPointerException.", "metadata": {"language": "java", "category": "null-safety"}},
    {"id": "java-004", "text": "Java: Use StringBuilder for string concatenation in loops. String concatenation with + inside loops creates many intermediate objects. StringBuilder.append() is O(1) amortized.", "metadata": {"language": "java", "category": "performance"}},
    {"id": "java-005", "text": "Java: Follow SOLID principles. Single Responsibility: one class, one reason to change. Open/Closed: open for extension, closed for modification.", "metadata": {"language": "java", "category": "design"}},
    {"id": "java-006", "text": "Java: Never hardcode credentials, database URLs, or secrets. Use environment variables or a secrets manager like HashiCorp Vault or AWS Secrets Manager.", "metadata": {"language": "java", "category": "security"}},
    {"id": "java-007", "text": "Java: Always close resources (streams, connections) using try-with-resources. Example: try (InputStream is = new FileInputStream(file)) { ... }.", "metadata": {"language": "java", "category": "resource-management"}},
    {"id": "pytest-001", "text": "pytest pattern: Use fixtures for test setup and teardown. @pytest.fixture def client(): return TestClient(app). Use conftest.py for shared fixtures.", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-002", "text": "pytest pattern: Use @pytest.mark.parametrize for testing multiple input scenarios. Example: @pytest.mark.parametrize('input,expected', [(1, 2), (2, 4)]) def test_double(input, expected): assert double(input) == expected", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-003", "text": "pytest pattern: Use pytest.raises() for testing exceptions. Example: with pytest.raises(ValueError, match='invalid input'): my_function(-1).", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-004", "text": "pytest pattern: Use unittest.mock or pytest-mock for mocking external dependencies. @patch('module.external_service') def test_func(mock_service): mock_service.return_value = 'mocked'", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-005", "text": "pytest best practices: Follow AAA pattern — Arrange, Act, Assert. Test one behavior per test. Name tests descriptively: test_should_return_error_when_input_is_negative.", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "junit-001", "text": "JUnit 5 pattern: Use @Test, @BeforeEach, @AfterEach annotations. Use @DisplayName for readable test names. Example: @Test @DisplayName('Should return empty list when no users exist') void testGetUsers() {}", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-002", "text": "JUnit 5 pattern: Use @ParameterizedTest with @ValueSource or @CsvSource for data-driven tests. Example: @ParameterizedTest @ValueSource(ints = {1, 2, 3}) void testPositive(int num) { assertTrue(num > 0); }", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-003", "text": "JUnit 5 pattern: Use assertThrows() for exception testing. Example: Exception ex = assertThrows(IllegalArgumentException.class, () -> service.process(null)); assertEquals('Input cannot be null', ex.getMessage());", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-004", "text": "JUnit 5 pattern: Use Mockito for mocking. @ExtendWith(MockitoExtension.class). @Mock UserRepository userRepo; @InjectMocks UserService userService; when(userRepo.findById(1L)).thenReturn(Optional.of(user));", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-005", "text": "JUnit best practices: Follow AAA pattern (Arrange-Act-Assert). One assertion concept per test. Test method names: methodName_stateUnderTest_expectedBehavior.", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "security-001", "text": "OWASP: Prevent SQL Injection by always using parameterized queries or prepared statements. Never concatenate user input into SQL strings. Example (Python): cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))", "metadata": {"language": "all", "category": "security"}},
    {"id": "security-002", "text": "OWASP: Validate and sanitize all user inputs. Check type, length, format, and range. Reject invalid input early. Never trust data from external sources.", "metadata": {"language": "all", "category": "security"}},
    {"id": "security-003", "text": "OWASP: Use bcrypt, scrypt, or Argon2 for password hashing. Never use MD5 or SHA-1 for passwords. Never store plain-text passwords.", "metadata": {"language": "all", "category": "security"}},
]


class KnowledgeBase:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = None
        self._setup()

    def _setup(self):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            try:
                ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                    api_key=api_key,
                    model_name="models/text-embedding-004"
                )
                self.collection = self.client.get_or_create_collection(
                    name="coding_standards", embedding_function=ef
                )
            except Exception:
                self._use_default_embeddings()
        else:
            self._use_default_embeddings()

        if self.collection.count() == 0:
            self._ingest()

    def _use_default_embeddings(self):
        self.collection = self.client.get_or_create_collection(name="coding_standards")

    def _ingest(self):
        print(f"📚 Ingesting {len(KNOWLEDGE_DOCS)} documents...")
        self.collection.add(
            ids=[doc["id"] for doc in KNOWLEDGE_DOCS],
            documents=[doc["text"] for doc in KNOWLEDGE_DOCS],
            metadatas=[doc["metadata"] for doc in KNOWLEDGE_DOCS],
        )
        print("✅ Knowledge base ready!")

    def search(self, query: str, n_results: int = 3) -> list:
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        return [{"content": doc, "metadata": meta} for doc, meta in zip(documents, metadatas)]


def init_knowledge_base():
    global _kb_instance
    _kb_instance = KnowledgeBase()

def get_knowledge_base() -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
