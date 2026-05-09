# 📦 Installation Guide

This guide covers setting up the AI News Agent for local development.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | Required |
| Git | 2.0+ | For version control |
| Docker | 24.0+ | Optional, for containerized setup |
| PostgreSQL | 15+ | Optional, for production |

---

## Quick Start (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-news-agent.git
cd ai-news-agent
```

### 2. Create Virtual Environment

**Windows (PowerShell)**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your API keys (see below)
```

### 5. Run the Application

```bash
# One-shot workflow
python main.py --mode workflow

# Or with scheduler
python main.py --mode scheduler
```

---

## 🔑 API Keys Setup

### Groq API (Required)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up/Login
3. Create API key
4. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxx
   ```

### Telegram Bot (Required)

1. Open Telegram
2. Search for @BotFather
3. Send `/newbot`
4. Follow prompts, get token
5. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   ```

### Get Your Chat ID

1. Search @userinfobot on Telegram
2. Send any message
3. Get your numeric ID
4. Add to `.env`:
   ```
   TELEGRAM_CHAT_ID=123456789
   ```

### LangSmith (Optional)

1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Create API key
3. Add to `.env`:
   ```
   LANGCHAIN_API_KEY=ls_xxxxxxxxxxxxx
   LANGCHAIN_TRACING_V2=true
   ```

---

## 🐳 Docker Installation

### Option 1: Docker Compose (Recommended)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Manual Docker Build

```bash
# Build image
docker build -t ai-news-agent .

# Run container
docker run -d \
  --name ai-news-agent \
  -p 8000:8000 \
  --env-file .env \
  ai-news-agent
```

---

## 🐘 PostgreSQL Setup (Optional)

For production, use PostgreSQL instead of SQLite:

```bash
# Create database
createdb news_agent

# Update .env
POSTGRES_URL=postgresql+psycopg://user:password@localhost:5432/news_agent
USE_POSTGRES_CHECKPOINT=true
```

---

## 📋 Environment Variables

See [.env.example](../.env.example) for all configuration options.

### Required Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGCHAIN_API_KEY` | - | LangSmith for tracing |
| `POSTGRES_URL` | SQLite | PostgreSQL connection |
| `CHROMA_PATH` | ./chroma_data | Vector store path |
| `LOG_LEVEL` | INFO | Logging level |

---

## 🧪 Verify Installation

```bash
# Run tests
pytest tests/ -v

# Run smoke test
python main.py --mode workflow

# Validate production setup
python validate_production.py
```

---

## 🚨 Troubleshooting

### Common Issues

**ImportError: No module named 'feedparser'**
```bash
pip install -r requirements.txt
```

**Groq API Error: Rate limit exceeded**
- Wait 1 minute, retry
- Or add OpenRouter as fallback

**Telegram bot not responding**
- Check bot token
- Start bot with /start command

**Database error**
- Check PostgreSQL connection
- Or use SQLite: remove POSTGRES_URL

---

## 📚 Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Read [API_REFERENCE.md](API_REFERENCE.md) for API details

---

## 💻 Development Setup

For contributors:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run linting
ruff check app/ tests/

# Run formatters
black app/ tests/

# Run type checking
mypy app/
```

---

*Last updated: 2026-05-09*