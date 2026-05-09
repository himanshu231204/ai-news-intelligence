# 📝 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Architecture documentation with Mermaid diagrams
- Comprehensive deployment guides
- API reference documentation

### Changed

- Improved error handling in collectors
- Enhanced LLM fallback routing

### Fixed

- Telegram message formatting issues
- RSS feed parsing edge cases

---

## [1.2.0] - 2025-05-09

### Added

- **Multi-provider LLM routing**: Groq → OpenRouter → Gemini fallback
- **Enhanced deduplication**: ChromaDB with semantic embeddings
- **Newsletter sections**: Major AI News, Open Source, Research, Tools
- **Telegram commands**: /trending, /opensource, /research

### Changed

- Migrated to LangGraph 0.2+ for better workflow management
- Improved ranking algorithm with weighted scoring
- Added more RSS feed sources

### Fixed

- Fixed rate limiting issues with Groq
- Fixed message chunking for long newsletters

---

## [1.1.0] - 2025-03-15

### Added

- **GitHub Trending collector**: Track open-source AI projects
- **Hacker News collector**: Top AI stories
- **Reddit collector**: AI subreddit posts
- **PostgreSQL support**: For persistent storage

### Changed

- Refactored collectors into modular structure
- Improved error handling with retry logic
- Added LangSmith observability

### Fixed

- Fixed timezone issues in scheduler
- Fixed duplicate news detection

---

## [1.0.0] - 2025-01-01

### Added

- **Initial release**: MVP with core features
- **RSS collector**: Multiple AI news feeds
- **LLM summarization**: Groq-powered summaries
- **Telegram bot**: Daily newsletter delivery
- **Docker support**: Containerized deployment

### Changed

- First stable release
- Production-ready code structure

---

## [0.9.0-beta] - 2024-12-01

### Added

- Beta testing phase
- Basic workflow implementation
- Simple Telegram integration

### Changed

- Iterative development based on feedback

---

## [0.5.0-alpha] - 2024-10-01

### Added

- Initial prototype
- Proof of concept for news collection
- Basic LLM integration

---

## 📋 Version History

| Version | Date | Status |
|---------|------|--------|
| 1.2.0 | 2025-05-09 | Current |
| 1.1.0 | 2025-03-15 | Stable |
| 1.0.0 | 2025-01-01 | Stable |
| 0.9.0-beta | 2024-12-01 | Beta |
| 0.5.0-alpha | 2024-10-01 | Alpha |

---

## 🔧 Upgrading

### From 1.1.x to 1.2.0

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update environment variables (if needed)
# New: OPENROUTER_API_KEY, GEMINI_API_KEY
```

### From 1.0.x to 1.1.0

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Optional: Set up PostgreSQL
POSTGRES_URL=postgresql+psycopg://user:pass@host/db
```

---

## 🏷️ Release Types

| Type | Description |
|------|-------------|
| Major | Breaking changes, new features |
| Minor | New features, backward compatible |
| Patch | Bug fixes, no breaking changes |

---

## 📝 Commit Convention

See [CONTRIBUTING.md](CONTRIBUTING.md) for commit message format.

---

*For older versions, see git history*