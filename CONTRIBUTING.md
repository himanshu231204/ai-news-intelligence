# 🤝 Contributing to AI News Agent

Thank you for your interest in contributing to the AI News Agent project!

This document provides guidelines for contributing to this project. Following these guidelines helps us maintain quality and makes collaboration easier.

---

## 📋 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## 🏗️ How to Contribute

### Reporting Bugs

1. **Check existing issues** - Search for similar bugs
2. **Create a new issue** - Use the bug report template
3. **Include details**:
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs

### Suggesting Features

1. **Search existing proposals** - Avoid duplicates
2. **Open a discussion** - Use GitHub Discussions
3. **Describe the feature**:
   - Use case
   - Expected behavior
   - Alternative solutions

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** - Follow our coding standards
4. **Write tests** - Ensure coverage
5. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add new collector for X source"
   ```
6. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

---

## 🧱 Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/ai-news-agent.git
cd ai-news-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Copy environment
cp .env.example .env
# Edit .env with your test keys
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_collectors.py -v

# Run in watch mode
pytest tests/ --watch
```

### Code Quality

```bash
# Lint with ruff
ruff check app/ tests/

# Format with black
black app/ tests/

# Type check with mypy
mypy app/

# Security audit
bandit -r app/
```

---

## 📐 Coding Standards

### Python Style

- Follow **PEP 8** with **Black** formatting
- Use **type hints** everywhere
- Add **docstrings** to all public functions
- Maximum line length: **88 characters**

### Example

```python
from typing import List, Optional
from pydantic import BaseModel


class NewsItem(BaseModel):
    """Represents a single news item from a source."""
    
    title: str
    url: str
    source: str
    timestamp: Optional[str] = None
    content: Optional[str] = None


def collect_from_rss(feeds: List[str]) -> List[NewsItem]:
    """Collect news items from RSS feeds.
    
    Args:
        feeds: List of RSS feed URLs.
        
    Returns:
        List of NewsItem objects.
        
    Raises:
        RSSParseError: If feed parsing fails.
    """
    results: List[NewsItem] = []
    for feed in feeds:
        items = _parse_feed(feed)
        results.extend(items)
    return results
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `news_items` |
| Functions | snake_case | `collect_news()` |
| Classes | PascalCase | `NewsCollector` |
| Constants | UPPER_SNAKE | `MAX_ITEMS` |
| Private | _prefix | `_internal_func()` |

### Import Order

```python
# Standard library
import os
import sys
from typing import List, Optional

# Third party
import feedparser
import requests
from pydantic import BaseModel

# Local application
from app.collectors import RSSCollector
from app.graph import workflow
```

---

## 🧪 Testing Standards

### Test Structure

```python
# tests/test_collectors.py
import pytest
from app.collectors.rss import RSSCollector


class TestRSSCollector:
    """Tests for RSS Collector."""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance."""
        return RSSCollector()
    
    def test_parse_valid_feed(self, collector):
        """Test parsing a valid RSS feed."""
        result = collector.collect(["https://example.com/feed.xml"])
        assert len(result) > 0
        assert result[0].title is not None
    
    def test_invalid_feed_handling(self, collector):
        """Test handling of invalid feed URLs."""
        with pytest.raises(FeedParseError):
            collector.collect(["https://invalid-url"])
```

### Test Coverage

- Minimum **80% coverage** for new code
- Test edge cases and error conditions
- Use **pytest fixtures** for setup
- Mock external APIs

---

## 📝 Commit Messages

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting |
| `refactor` | Code refactoring |
| `test` | Tests |
| `chore` | Maintenance |

### Examples

```bash
# Feature
git commit -m "feat(collectors): add Reddit collector"

# Bug fix
git commit -m "fix(telegram): resolve message formatting issue"

# Documentation
git commit -m "docs: update API reference"

# Refactor
git commit -m "refactor(ranking): simplify scoring algorithm"
```

---

## 🔄 Pull Request Process

### Before Submitting

1. **Run tests** - All tests must pass
2. **Check coverage** - Maintain or improve coverage
3. **Lint code** - No ruff/black violations
4. **Update docs** - If needed
5. **Rebase on main** - Ensure clean history

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process

1. **Automated checks** - CI runs tests/lint
2. **Code review** - Maintainer reviews
3. **Feedback** - Address comments
4. **Merge** - Approved and merged

---

## 🏛️ Architecture Guidelines

See [AGENTS.md](AGENTS.md) for detailed architecture guidelines.

### Key Principles

1. **Modular** - Keep components isolated
2. **LangGraph-first** - Use DAG workflows
3. **Type-safe** - Use TypedDict, Pydantic
4. **Testable** - Dependency injection
5. **Documented** - Clear docstrings

---

## 💬 Getting Help

- **GitHub Issues** - For bugs and features
- **GitHub Discussions** - For questions
- **Discord** - Join our community (link in README)

---

## 🙏 Acknowledgments

Thank you to all contributors who help make this project better!

---

*Last updated: 2026-05-09*