# Test Suite

## Overview

Comprehensive pytest-based test suite for the Azure OpenAI Master Agent System.

## Structure

```
tests/
├── conftest.py                  # Pytest configuration and shared fixtures
├── test_conversation_history.py # Unit tests for conversation history
├── test_config.py               # Unit tests for configuration
├── test_utils.py                # Unit tests for utilities
├── test_integration.py          # Integration tests (requires API)
└── README.md                    # This file
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
Tests for individual components without external dependencies:
- `test_conversation_history.py` - ConversationHistory class
- `test_config.py` - Configuration management
- `test_utils.py` - System monitoring and utilities

### Integration Tests (`@pytest.mark.integration`)
Tests that verify full system integration:
- `test_integration.py` - Master Agent workflows
- Requires Azure OpenAI API access
- Tests agent routing, context preservation, multi-agent workflows

## Running Tests

### Install Dependencies
```bash
cd /Users/josephbalsamo/Development/Work/gradingAgent/grading-agent
source .venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories

**Unit Tests Only (no API required):**
```bash
pytest -m unit
```

**Integration Tests Only (requires API):**
```bash
pytest -m integration
```

**Exclude Slow Tests:**
```bash
pytest -m "not slow"
```

**Exclude Tests Requiring API:**
```bash
pytest -m "not requires_api"
```

### Run Specific Test Files
```bash
pytest tests/test_conversation_history.py
pytest tests/test_integration.py
pytest tests/test_config.py
```

### Run with Coverage
```bash
pytest --cov=modules --cov-report=html
```

This generates a coverage report in `htmlcov/index.html`.

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

## Test Markers

Tests are marked with decorators to categorize them:

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (slower, may need API)
- `@pytest.mark.requires_api` - Requires Azure OpenAI API access
- `@pytest.mark.slow` - Slow-running tests

## Fixtures

Shared fixtures are defined in `conftest.py`:

### Session-Scoped Fixtures
- `project_root_dir` - Project root directory path
- `sample_test_messages` - Sample messages for testing
- `sample_analysis_query` - Sample analysis query
- `sample_grading_query` - Sample grading query

### Function-Scoped Fixtures
- `clean_conversation_history` - Cleans up history before/after test
- `conversation_history` - Fresh ConversationHistory instance
- `master_agent` - Fresh MasterAgent instance (requires API)

## Writing New Tests

### Unit Test Template
```python
import pytest

@pytest.mark.unit
class TestMyComponent:
    """Test MyComponent functionality."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        component = MyComponent()
        
        # Act
        result = component.do_something()
        
        # Assert
        assert result is not None
```

### Integration Test Template
```python
import pytest

@pytest.mark.integration
@pytest.mark.requires_api
class TestMyIntegration:
    """Integration tests for my feature."""
    
    def test_full_workflow(self, master_agent):
        """Test full workflow."""
        # Arrange
        input_data = "test input"
        
        # Act
        result = master_agent.chat(input_data)
        
        # Assert
        assert result is not None
        assert len(result) > 0
```

## Test Coverage Goals

- **Unit Tests**: > 80% coverage
- **Integration Tests**: Cover all major workflows
- **Edge Cases**: Test error handling and edge cases
- **Regression Tests**: Add tests for fixed bugs

## Common Issues

### Tests Fail Due to Missing .env

Ensure `.env` file is configured with Azure OpenAI credentials:
```bash
cp .env.template .env
# Edit .env with your credentials
```

### Import Errors

Ensure you're running from the project root and virtual environment is activated:
```bash
cd /Users/josephbalsamo/Development/Work/gradingAgent/grading-agent
source .venv/bin/activate
```

### API Rate Limiting

If integration tests fail due to rate limiting:
- Use `pytest -m "unit"` to run only unit tests
- Add delays between API calls
- Use `@pytest.mark.slow` for tests that hit rate limits

### Conversation History File Conflicts

The `clean_conversation_history` fixture should handle cleanup automatically. If you encounter issues:
```bash
rm data/conversation_history.json
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -m unit  # Only unit tests in CI
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Use Fixtures**: Leverage fixtures for setup/teardown
3. **Mark Tests**: Use markers to categorize tests
4. **Clear Names**: Test names should describe what they test
5. **AAA Pattern**: Arrange, Act, Assert
6. **Fast Tests**: Keep unit tests fast (< 1 second each)
7. **Cleanup**: Always clean up resources in fixtures
8. **Documentation**: Add docstrings to test classes and functions

## Contributing

When adding new features:
1. Write unit tests first (TDD approach)
2. Add integration tests for workflows
3. Update this README if adding new test categories
4. Ensure all tests pass before committing
5. Aim for high test coverage (> 80%)

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Markers](https://docs.pytest.org/en/stable/mark.html)
- [Coverage.py](https://coverage.readthedocs.io/)
