# Test Suite Documentation

## Overview

This test suite provides comprehensive coverage for the MCQ Generator application, including:
- Authentication routes (register, login, logout)
- Document routes (upload, delete)
- Quiz routes (generate)
- Results routes (save, get data)
- UI routes (all HTML pages)
- Database models (User, Document, Question, QuizSession, Result)

## Test Structure

```
tests/
├── conftest.py           # Test fixtures and configuration
├── test_auth.py          # Authentication route tests
├── test_models.py        # Database model tests
├── test_documents.py     # Document route tests
├── test_quizzes.py       # Quiz route tests
├── test_results.py       # Results route tests
├── test_ui.py            # UI route tests
├── test_extraction.py    # Text extraction tests (existing)
└── test_llm.py           # LLM integration tests (existing)
```

## Running Tests

### Run all tests
```bash
pytest
# or
uv run pytest
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run only unit tests (exclude integration)
```bash
pytest -m "not integration"
```

### Run with verbose output
```bash
pytest -v
```

## Test Fixtures

### Application Fixtures
- `app`: Flask application instance with test database
- `client`: Flask test client
- `db_session`: Database session (auto-rollback after each test)

### User Fixtures
- `test_user`: Standard test user (username: "testuser", email: "test@example.com")
- `test_user2`: Second test user for authorization tests
- `authenticated_client`: Test client with logged-in user

### Data Fixtures
- `test_document`: Document owned by test_user
- `test_document_no_questions`: Document without questions
- `test_questions`: List of 3 questions for test_document

### Mock Fixtures
- `mock_generate_mcq`: Mocks LLM API to return sample questions
- `mock_generate_mcq_empty`: Mocks LLM API to return empty list
- `mock_extract_text`: Mocks text extraction function

### File Fixtures
- `sample_pdf_file`: Temporary PDF file for upload tests
- `sample_docx_file`: Temporary DOCX file for upload tests

## Test Coverage

### Authentication Tests (`test_auth.py`)
- ✅ User registration (success, validation, duplicates)
- ✅ User login (success, invalid credentials, missing fields)
- ✅ User logout (success, unauthenticated access)

### Model Tests (`test_models.py`)
- ✅ User model (creation, password hashing, uniqueness, relationships)
- ✅ Document model (creation, relationships)
- ✅ Question model (creation, types, JSON storage, relationships)
- ✅ QuizSession model (creation, relationships)
- ✅ Result model (creation, relationships)

### Document Route Tests (`test_documents.py`)
- ✅ Document upload (success, missing file, errors, authentication)
- ✅ Document deletion (success, not found, unauthorized, authentication)

### Quiz Route Tests (`test_quizzes.py`)
- ✅ Quiz generation (success, missing params, not found, duplicates, empty results)

### Results Route Tests (`test_results.py`)
- ✅ Save results (success, missing fields, invalid data)
- ✅ Get results data (success, no data, missing params)

### UI Route Tests (`test_ui.py`)
- ✅ Home page
- ✅ Documents page (authenticated, unauthenticated)
- ✅ Upload page (authenticated, unauthenticated)
- ✅ Quiz pages (authenticated, unauthenticated, not found)
- ✅ Results page (authenticated, unauthenticated)

## Testing Best Practices

1. **Test Isolation**: Each test is independent and uses its own database session
2. **Fixtures**: Use fixtures for common setup/teardown
3. **Mocking**: External APIs (LLM) are mocked for fast unit tests
4. **Integration Tests**: Marked with `@pytest.mark.integration` for real API calls
5. **Database**: Uses SQLite in-memory database for fast test execution

## CI Integration

The test suite is configured to run in CI/CD pipelines:
- Runs on every push and pull request
- Excludes integration tests by default (use `-m integration` to run them)
- Includes linting and type checking

## Adding New Tests

When adding new routes or features:

1. Create test functions following the naming pattern: `test_<feature>_<scenario>`
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies (APIs, file system, etc.)
4. Test both success and failure cases
5. Test authentication/authorization requirements
6. Test edge cases and error handling

## Notes

- Tests use in-memory SQLite database for speed
- Authentication redirects (302) are expected for unauthenticated API access
- Mock fixtures ensure tests run without external API dependencies
- Database sessions are automatically rolled back after each test

