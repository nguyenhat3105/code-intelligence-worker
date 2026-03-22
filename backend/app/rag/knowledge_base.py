import os
import chromadb
from chromadb.utils import embedding_functions

_kb_instance = None

KNOWLEDGE_DOCS = [
    {"id": "py-001", "text": "Python: Use specific exceptions instead of bare except clauses. Always catch the most specific exception type. Example: 'except ValueError:' instead of 'except:'. Bare excepts hide bugs.", "metadata": {"language": "python", "category": "error-handling"}},
    {"id": "py-002", "text": "Python: Never use eval() or exec() with user-provided input. These execute arbitrary code and are security vulnerabilities. Use ast.literal_eval() for safe evaluation.", "metadata": {"language": "python", "category": "security"}},
    {"id": "py-003", "text": "Python: Use 'is None' and 'is not None' instead of '== None'. The 'is' operator checks identity, which is correct for None comparisons.", "metadata": {"language": "python", "category": "style"}},
    {"id": "py-004", "text": "Python: Use logging module instead of print statements in production. Configure logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL. Example: logger = logging.getLogger(__name__)", "metadata": {"language": "python", "category": "style"}},
    {"id": "py-005", "text": "Python: Never hardcode passwords or API keys. Use environment variables: os.environ.get('SECRET_KEY') or config files excluded from version control.", "metadata": {"language": "python", "category": "security"}},
    {"id": "py-006", "text": "Python: Use list comprehensions and generators for better performance. Use generators for large datasets to save memory.", "metadata": {"language": "python", "category": "performance"}},
    {"id": "py-007", "text": "Python: Follow PEP 8. Functions/variables: snake_case. Classes: PascalCase. Constants: UPPER_SNAKE_CASE.", "metadata": {"language": "python", "category": "style"}},
    {"id": "java-001", "text": "Java: Use SLF4J + Logback instead of System.out.println. Define: private static final Logger logger = LoggerFactory.getLogger(ClassName.class);", "metadata": {"language": "java", "category": "style"}},
    {"id": "java-002", "text": "Java: Never catch generic Exception. Catch specific exceptions. Never leave catch blocks empty — at minimum log the error.", "metadata": {"language": "java", "category": "error-handling"}},
    {"id": "java-003", "text": "Java: Use Optional<T> instead of returning null. Makes API contract explicit and prevents NullPointerException.", "metadata": {"language": "java", "category": "null-safety"}},
    {"id": "java-004", "text": "Java: Use StringBuilder for string concatenation in loops. String + in loops creates many intermediate objects. StringBuilder.append() is O(1) amortized.", "metadata": {"language": "java", "category": "performance"}},
    {"id": "java-005", "text": "Java: Follow SOLID principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.", "metadata": {"language": "java", "category": "design"}},
    {"id": "java-006", "text": "Java: Never hardcode credentials. Use environment variables or a secrets manager like HashiCorp Vault.", "metadata": {"language": "java", "category": "security"}},
    {"id": "java-007", "text": "Java: Always close resources with try-with-resources. Example: try (InputStream is = new FileInputStream(file)) { ... }", "metadata": {"language": "java", "category": "resource-management"}},
    {"id": "pytest-001", "text": "pytest: Use fixtures for setup. @pytest.fixture def client(): return TestClient(app). Use conftest.py for shared fixtures.", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-002", "text": "pytest: Use @pytest.mark.parametrize for multiple inputs. @pytest.mark.parametrize('input,expected', [(1,2),(2,4)]) def test_double(input, expected): assert double(input) == expected", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-003", "text": "pytest: Use pytest.raises() for exception testing. with pytest.raises(ValueError, match='invalid'): my_function(-1)", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-004", "text": "pytest: Use unittest.mock for mocking. @patch('module.service') def test_func(mock_svc): mock_svc.return_value = 'mocked'", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "pytest-005", "text": "pytest best practices: AAA pattern (Arrange, Act, Assert). One behavior per test. Descriptive names: test_should_return_error_when_input_is_negative.", "metadata": {"language": "python", "category": "testing", "framework": "pytest"}},
    {"id": "junit-001", "text": "JUnit 5: Use @Test, @BeforeEach, @AfterEach. Use @DisplayName for readable names. @Test @DisplayName('Should return empty list') void testGetUsers() {}", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-002", "text": "JUnit 5: Use @ParameterizedTest with @ValueSource or @CsvSource. @ParameterizedTest @ValueSource(ints={1,2,3}) void testPositive(int n) { assertTrue(n > 0); }", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-003", "text": "JUnit 5: Use assertThrows() for exceptions. Exception ex = assertThrows(IllegalArgumentException.class, () -> service.process(null));", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-004", "text": "JUnit 5 + Mockito: @ExtendWith(MockitoExtension.class). @Mock UserRepository repo; @InjectMocks UserService svc; when(repo.findById(1L)).thenReturn(Optional.of(user));", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "junit-005", "text": "JUnit best practices: AAA pattern. One assertion concept per test. Naming: methodName_stateUnderTest_expectedBehavior.", "metadata": {"language": "java", "category": "testing", "framework": "junit"}},
    {"id": "security-001", "text": "OWASP: Prevent SQL Injection with parameterized queries. Never concatenate user input into SQL. cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))", "metadata": {"language": "all", "category": "security"}},
    {"id": "security-002", "text": "OWASP: Validate and sanitize all user inputs. Check type, length, format, range. Reject invalid input early.", "metadata": {"language": "all", "category": "security"}},
    {"id": "security-003", "text": "OWASP: Use bcrypt, scrypt, or Argon2 for password hashing. Never use MD5/SHA-1. Never store plain-text passwords.", "metadata": {"language": "all", "category": "security"}},
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
                    api_key=api_key, model_name="models/text-embedding-004"
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
        print(f"📚 Ingesting {len(KNOWLEDGE_DOCS)} documents into knowledge base...")
        self.collection.add(
            ids=[d["id"] for d in KNOWLEDGE_DOCS],
            documents=[d["text"] for d in KNOWLEDGE_DOCS],
            metadatas=[d["metadata"] for d in KNOWLEDGE_DOCS],
        )
        print("✅ Knowledge base ready!")

    def search(self, query: str, n_results: int = 3) -> list:
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count())
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [{"content": doc, "metadata": meta} for doc, meta in zip(docs, metas)]


def init_knowledge_base():
    global _kb_instance
    _kb_instance = KnowledgeBase()

def get_knowledge_base() -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
