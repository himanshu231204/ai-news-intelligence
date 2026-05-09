# 🔧 Troubleshooting Guide

This guide helps resolve common issues with the AI News Agent.

---

## 🚨 Quick Diagnostics

Run this to check your setup:

```bash
# Validate production setup
python validate_production.py

# Check environment
python -c "from app.config.settings import Settings; s = Settings(); print('Config OK')"

# Test collectors
python -c "from app.collectors.rss import RSSCollector; print('Collectors OK')"
```

---

## ❌ Common Issues

### 1. Groq API Errors

#### "Rate limit exceeded"

**Cause**: Too many requests to Groq API.

**Solution**:
```python
# Add to .env for fallback
OPENROUTER_API_KEY=your_openrouter_key

# Or wait 60 seconds between runs
```

#### "Invalid API key"

**Cause**: Incorrect or expired Groq key.

**Solution**:
1. Go to [console.groq.com](https://console.groq.com)
2. Verify your API key
3. Update `.env` with correct key

---

### 2. Telegram Errors

#### "Bot not found"

**Cause**: Invalid bot token.

**Solution**:
1. Check token format: `123456:ABC-DEF...`
2. Regenerate at @BotFather
3. Update `TELEGRAM_BOT_TOKEN` in `.env`

#### "Chat not found"

**Cause**: Invalid chat ID.

**Solution**:
1. Message @userinfobot on Telegram
2. Copy your numeric ID
3. Update `TELEGRAM_CHAT_ID` in `.env`

#### "Message too long"

**Cause**: Newsletter exceeds Telegram's 4096 char limit.

**Solution**:
The system automatically chunks messages. If still failing:
```python
# In .env, reduce max items
MAX_NEWS_ITEMS=10
```

---

### 3. Database Errors

#### "Database locked"

**Cause**: SQLite concurrent access issue.

**Solution**:
```python
# Use PostgreSQL instead
POSTGRES_URL=postgresql+psycopg://user:pass@host:5432/db
USE_POSTGRES_CHECKPOINT=true
```

#### "Table not found"

**Cause**: Database not initialized.

**Solution**:
```bash
# Delete old database and restart
rm newsletter.db
python main.py --mode workflow
```

---

### 4. Collector Errors

#### "Connection timeout"

**Cause**: Network issue or source unavailable.

**Solution**:
```python
# Increase timeout in collector
# Default is 30 seconds
# Check source availability manually
```

#### "Parse error"

**Cause**: Malformed RSS/API response.

**Solution**:
1. Check the feed URL in browser
2. Remove problematic source from config
3. Report issue on GitHub

---

### 5. Memory Issues

#### "Out of memory"

**Cause**: Too many embeddings in ChromaDB.

**Solution**:
```python
# Clean up old embeddings
from app.memory.vectorstore import VectorStore
store = VectorStore()
store.cleanup(days=7)  # Keep only 7 days
```

---

### 6. LangGraph Errors

#### "Invalid state schema"

**Cause**: State doesn't match expected schema.

**Solution**:
```python
# Ensure state has all required fields
state = {
    "raw_news": [],
    "unique_news": [],
    "ranked_news": [],
    "summaries": [],
    "newsletter": "",
    "errors": []
}
```

---

## 🐛 Debug Mode

Enable detailed logging:

```env
LOG_LEVEL=DEBUG
```

Run with verbose output:

```bash
python main.py --mode workflow --verbose
```

---

## 📊 Health Checks

### Check All Services

```python
# validate_production.py
import os
from app.config.settings import Settings

def validate():
    s = Settings()
    
    # Check required vars
    assert s.groq_api_key, "GROQ_API_KEY not set"
    assert s.telegram_bot_token, "TELEGRAM_BOT_TOKEN not set"
    assert s.telegram_chat_id, "TELEGRAM_CHAT_ID not set"
    
    print("✅ All checks passed!")

validate()
```

---

## 🔧 Reset Environment

If all else fails:

```bash
# 1. Delete caches
rm -rf .pytest_cache .ruff_cache __pycache__
rm -rf app/__pycache__ tests/__pycache__

# 2. Delete databases
rm -f newsletter.db
rm -rf chroma_data

# 3. Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Run fresh
python main.py --mode workflow
```

---

## 📞 Getting Help

If you're still stuck:

1. **Search existing issues**: [GitHub Issues](https://github.com/yourusername/ai-news-agent/issues)
2. **Ask on discussions**: [GitHub Discussions](https://github.com/yourusername/ai-news-agent/discussions)
3. **Create new issue**: Include:
   - Python version
   - Operating system
   - Full error message
   - Steps to reproduce

---

*Last updated: 2026-05-09*