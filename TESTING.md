# 🧪 Testing Guide

Comprehensive test suite for the AI News Research Agent pipeline.

---

## 📋 Test Structure

```
tests/
├── conftest.py                # Pytest fixtures and configuration
├── test_smoke.py              # Smoke tests
├── test_collectors.py         # News collection tests
├── test_deduplication.py      # Deduplication logic tests
├── test_ranking.py            # Ranking/scoring tests
├── test_filtering.py          # Quality filtering tests
├── test_summarization.py      # LLM summarization tests
├── test_newsletter.py         # Newsletter generation tests
├── test_workflow.py           # LangGraph workflow integration
├── test_error_handling.py     # Error resilience tests
└── test_integration.py        # End-to-end integration tests
```

---

## 🚀 Running Tests

### All Tests
```bash
pytest
```

### Verbose Output
```bash
pytest -v
```

### With Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_collectors.py -v
```

### Specific Test Class
```bash
pytest tests/test_collectors.py::TestGitHubCollector -v
```

### Specific Test Function
```bash
pytest tests/test_collectors.py::TestGitHubCollector::test_github_collector_success -v
```

### Run Only Async Tests
```bash
pytest -m asyncio -v
```

### Run With Timeout
```bash
pytest --timeout=60
```

### Parallel Execution
```bash
pytest -n auto
```

---

## 📊 Coverage

### Generate Coverage Report
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

### View HTML Report
```bash
# Coverage report is in coverage_html_report/index.html
open coverage_html_report/index.html
```

### Coverage Targets
- Line coverage: 80%+
- Branch coverage: 75%+
- Excluded: Abstract methods, __repr__, edge cases

---

## 🧬 Test Categories

### 1. **Collectors** (`test_collectors.py`)
Tests for all news sources:
- GitHub trending
- Hacker News
- Reddit
- RSS feeds
- arXiv
- Dev.to
- Product Hunt
- Twitter

**Key Tests:**
- Success scenarios
- Network errors
- Timeout handling
- Data validation
- Parallel execution

### 2. **Deduplication** (`test_deduplication.py`)
Tests for duplicate removal:
- Exact URL duplicates
- Semantic similarity
- Title matching
- Content comparison

**Key Tests:**
- Exact duplicates removed
- Similarity threshold tuning
- Metadata preservation
- Performance with large batches

### 3. **Ranking** (`test_ranking.py`)
Tests for news importance scoring:
- Virality metrics
- Age consideration
- Source credibility
- Keyword importance

**Key Tests:**
- Scoring factors
- Sorting order
- Missing fields handling
- Performance

### 4. **Filtering** (`test_filtering.py`)
Tests for quality filtering:
- Low quality removal
- Spam detection
- Content length validation
- Source credibility

**Key Tests:**
- Content quality metrics
- Threshold tuning
- Unicode handling
- Performance

### 5. **Summarization** (`test_summarization.py`)
Tests for LLM summarization:
- Article summarization
- Key point extraction
- Conciseness
- Format validation

**Key Tests:**
- Single/batch summarization
- Long content handling
- Metadata preservation
- Quality metrics

### 6. **Newsletter** (`test_newsletter.py`)
Tests for newsletter generation:
- Section headers
- Article links
- Formatting
- Length control

**Key Tests:**
- Structure validation
- Markdown formatting
- Special characters
- Unicode support

### 7. **Workflow** (`test_workflow.py`)
Tests for LangGraph integration:
- Graph compilation
- Node execution
- State transitions
- Error propagation

**Key Tests:**
- Workflow building
- State management
- Conditional routing
- Checkpointing

### 8. **Error Handling** (`test_error_handling.py`)
Tests for resilience:
- Collector failures
- API errors
- Timeout handling
- Graceful degradation

**Key Tests:**
- Partial failures
- Error recovery
- Logging
- Edge cases

---

## ✅ Test Checklist

### Before Deployment
- [ ] All tests pass: `pytest`
- [ ] Coverage > 80%: `pytest --cov=app`
- [ ] No linting errors: `ruff check app/`
- [ ] Types correct: `mypy app/`
- [ ] Security scan: `bandit -r app/`

### Pre-commit Hook
```bash
#!/bin/bash
pytest --cov=app --cov-fail-under=80
ruff check app/
black --check app/
```

---

## 🔍 Debugging Tests

### Verbose Output
```bash
pytest -v -s  # -s shows print statements
```

### Stop on First Failure
```bash
pytest -x
```

### Run Last Failed Tests
```bash
pytest --lf
```

### Run Failed + Changed Tests
```bash
pytest --ff
```

### Debugging a Specific Test
```bash
pytest -vv -s tests/test_collectors.py::TestGitHubCollector::test_github_collector_success
```

---

## 📈 Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Collectors | 85% | Pending |
| Deduplication | 90% | Pending |
| Ranking | 85% | Pending |
| Filtering | 80% | Pending |
| Summarization | 75% | Pending |
| Newsletter | 90% | Pending |
| Workflow | 80% | Pending |
| Error Handling | 85% | Pending |
| **Overall** | **80%+** | **Pending** |

---

## 🐛 Common Issues

### Tests Hang
```bash
# Use timeout
pytest --timeout=60
```

### Async Tests Fail
```bash
# Ensure pytest-asyncio installed
pip install pytest-asyncio>=0.24.0
```

### Import Errors
```bash
# Ensure PYTHONPATH includes repo root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Mock Not Working
```bash
# Check import path matches actual module
# Use relative imports in mocks
```

---

## 🔄 Continuous Integration

GitHub Actions CI runs tests on:
- Python 3.10, 3.11, 3.12
- Linux, macOS, Windows
- Every push and PR

**CI Pipeline:**
1. Test (all Python versions)
2. Lint (ruff, black, mypy)
3. Validate (config, security)
4. Integration (end-to-end)
5. Docker build check

---

## 📝 Writing New Tests

### Test Template
```python
import pytest
from unittest.mock import patch, MagicMock

class TestFeature:
    """Test feature description"""
    
    def test_happy_path(self):
        """Test successful scenario"""
        # Arrange
        data = {"key": "value"}
        
        # Act
        result = process(data)
        
        # Assert
        assert result is not None
    
    def test_error_case(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            process({"invalid": "data"})
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operation"""
        result = await async_function()
        assert result is not None
```

### Best Practices
✅ **DO:**
- Use descriptive test names
- Test one thing per test
- Use fixtures for setup
- Mock external dependencies
- Test edge cases
- Include error cases

❌ **DON'T:**
- Test implementation details
- Use hardcoded values
- Make network calls
- Use real API keys
- Ignore failures
- Skip slow tests without marking

---

## 🎯 Test Priorities

**High Priority** (Must Pass):
- Workflow building
- State management
- Error handling
- Newsletter generation

**Medium Priority** (Should Pass):
- Collectors
- Deduplication
- Ranking
- Newsletter formatting

**Low Priority** (Nice to Have):
- Performance tests
- Load tests
- Edge case handling

---

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**Happy Testing! 🚀**
