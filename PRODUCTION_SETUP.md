# 🧠 AI News Research Agent - Production Guide

A production-ready autonomous AI research agent that collects, filters, ranks, and delivers curated AI news via Telegram every 24 hours.

## 📋 Overview

This system is built with:
- **LangGraph** - Agent orchestration with state management
- **ChromaDB** - Semantic embeddings for intelligent deduplication
- **PostgreSQL** - Persistent state checkpointing
- **Telegram Bot API** - Newsletter delivery
- **OpenAI/Groq** - LLM-powered summarization

## 🎯 Core Features

✅ **Multi-Source Collection**
- RSS feeds
- GitHub Trending
- Hacker News
- Reddit discussions
- ArXiv research papers
- Dev.to articles
- Product Hunt launches

✅ **Intelligent Processing**
- Semantic deduplication with embeddings
- Quality filtering and ranking
- Automated summarization
- Duplicate detection via ChromaDB

✅ **Production Ready**
- Persistent checkpointing (PostgreSQL)
- Retry logic with exponential backoff
- Comprehensive error handling
- LangSmith observability integration

✅ **Multiple Execution Modes**
- Single run: `python main.py --mode workflow`
- 24/7 Scheduler: `python main.py --mode scheduler`
- Telegram Bot: `python main.py --mode bot`

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.10+
python --version

# Virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# or
source .venv/bin/activate  # Mac/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
# Required:
#   - OPENAI_API_KEY (for embeddings)
#   - GROQ_API_KEY (for summarization)
#   - TELEGRAM_BOT_TOKEN (from BotFather)
#   - TELEGRAM_CHAT_ID (your chat ID)
# Optional:
#   - POSTGRES_URL (for persistent checkpointing)
#   - LANGCHAIN_API_KEY (for observability)
```

### 4. Setup Database (Optional but Recommended)

```bash
# PostgreSQL setup
createdb news_agent

# Update POSTGRES_URL in .env
POSTGRES_URL=postgresql+psycopg://user:password@localhost:5432/news_agent
```

### 5. Run the System

**Option A: Single Newsletter Run**
```bash
python main.py --mode workflow
```

**Option B: 24-Hour Scheduler**
```bash
python main.py --mode scheduler
```

**Option C: Telegram Bot (Interactive Commands)**
```bash
python main.py --mode bot
```

---

## 📊 System Architecture

### Workflow Pipeline

```
START
  │
  ├─→ collect_news (parallel collection from 8 sources)
  │
  ├─→ merge_results (combine all sources)
  │
  ├─→ deduplicate_news (semantic + URL-based dedup)
  │
  ├─→ filter_low_quality (filter non-AI news)
  │
  ├─→ rank_news (score by importance & virality)
  │
  ├─→ summarize_news (LLM-powered summaries)
  │
  ├─→ generate_newsletter (format & structure)
  │
  ├─→ store_results (save to database)
  │
  ├─→ send_telegram (deliver to Telegram)
  │
  END
```

### Component Architecture

```
┌─────────────────────────────────────────────┐
│         Telegram Bot Interface              │
│  /start, /daily, /trending, /research       │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│     LangGraph Workflow Orchestrator         │
│   (State Management + Checkpointing)        │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──┐  ┌──────▼──┐  ┌────▼────┐
│ Data │  │ Process │  │ Storage  │
│Layer │  │ Layer   │  │ Layer    │
└──────┘  └─────────┘  └──────────┘
    │           │            │
┌───▼──────┐ ┌──▼─────────┐ ┌───▼──────┐
│Collectors│ │Ranking &   │ │PostgreSQL │
│(8 src)   │ │Summ. LLMs  │ │ChromaDB   │
└──────────┘ └────────────┘ └───────────┘
```

### Data Flow

```
Raw News (8 sources)
       │
       ▼
Merged News (combined)
       │
       ▼
Unique News (deduped with ChromaDB embeddings)
       │
       ▼
Filtered News (AI-relevant only)
       │
       ▼
Ranked News (sorted by importance)
       │
       ▼
Summarized News (LLM summaries)
       │
       ▼
Newsletter (formatted & structured)
       │
       ▼
Telegram (delivered to user)
```

---

## ⚙️ Configuration Guide

### Required Environment Variables

```env
# LLM Services
OPENAI_API_KEY=sk-...              # For embeddings (REQUIRED)
GROQ_API_KEY=gsk_...               # For summarization (REQUIRED)

# Telegram
TELEGRAM_BOT_TOKEN=123:ABC...      # From BotFather (REQUIRED)
TELEGRAM_CHAT_ID=123456789         # Your chat ID (REQUIRED)

# Observability (Optional)
LANGCHAIN_API_KEY=lsv2_...         # For tracing
LANGCHAIN_TRACING_V2=true
```

### Optional Configuration

```env
# Database (defaults to in-memory if not set)
POSTGRES_URL=postgresql+psycopg://...

# Vector Store
CHROMA_PATH=./chroma_data

# Scheduler
NEWSLETTER_HOUR=9
NEWSLETTER_MINUTE=0

# Newsletter Settings
MIN_NEWS_ITEMS=5
MAX_NEWS_ITEMS=20
SIMILARITY_THRESHOLD=0.85
```

---

## 🤖 Telegram Bot Commands

Once the bot is running (`python main.py --mode bot`):

- `/start` - Show welcome message and available commands
- `/daily` - Generate and send today's AI newsletter
- `/trending` - Show trending discussion topics
- `/opensource` - Show open-source project launches
- `/research` - Show research highlights and papers

---

## 📁 Project Structure

```
ai-news-agent/
│
├── app/
│   ├── collectors/          # Data collection (8 sources)
│   ├── ranking/             # Scoring & deduplication
│   ├── summarization/       # LLM summaries
│   ├── newsletter/          # Formatting & generation
│   ├── graph/               # LangGraph workflow
│   ├── telegram/            # Bot & message handling
│   ├── memory/              # Checkpointing & vectorstore
│   ├── database/            # ORM models & queries
│   ├── scheduler/           # Job scheduling
│   ├── config/              # Settings management
│   └── utils/               # Logging, retry logic
│
├── tests/                   # Unit & integration tests
├── docker/                  # Docker configuration
│
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── .env.example             # Configuration template
└── README.md                # This file
```

---

## 🔧 Production Deployment

### Using Docker

```bash
# Build image
docker build -f docker/Dockerfile -t ai-news-agent .

# Run with scheduler
docker run -d \
  --name news-agent \
  -e TELEGRAM_BOT_TOKEN=... \
  -e OPENAI_API_KEY=... \
  -e GROQ_API_KEY=... \
  -v ./chroma_data:/app/chroma_data \
  ai-news-agent python main.py --mode scheduler
```

### Using Systemd (Linux)

Create `/etc/systemd/system/news-agent.service`:

```ini
[Unit]
Description=AI News Research Agent
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/news-agent
ExecStart=/opt/news-agent/.venv/bin/python main.py --mode scheduler
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable news-agent
sudo systemctl start news-agent
sudo systemctl status news-agent
```

---

## 📊 Monitoring & Observability

### LangSmith Integration

Set `LANGCHAIN_TRACING_V2=true` to enable tracing:

```bash
# View traces at https://smith.langchain.com
```

### Logging

Logs are written to stdout with timestamps:

```
2024-05-09 09:00:15 | INFO | collect_news | Starting collection from 8 sources
2024-05-09 09:01:30 | INFO | dedup_news | Deduplicated 180 items -> 125 unique
2024-05-09 09:02:45 | INFO | summarize | Generated 25 summaries in 45s
```

### Database Queries

Check stored newsletters:

```bash
sqlite3 newsletter.db "SELECT created_at, LENGTH(newsletter_text) FROM newsletter_runs LIMIT 10;"
```

---

## 🛠 Troubleshooting

### "ChromaDB initialization failed"

**Solution:** Ensure write permissions to `./chroma_data` directory

```bash
chmod -R 755 ./chroma_data
```

### "No OpenAI API key configured"

**Solution:** Add to `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

### "Telegram message failed"

**Solution:** Verify credentials:
```bash
# Get bot token from BotFather (@BotFather on Telegram)
# Get chat ID from @userinfobot
```

### "PostgreSQL connection failed"

**Solution:** Test connection:
```bash
psql postgresql+psycopg://user:password@localhost:5432/news_agent
```

---

## 📈 Performance Tips

1. **Use PostgreSQL** for persistent checkpointing (faster than in-memory)
2. **Cache embeddings** in ChromaDB (no re-embedding of seen articles)
3. **Enable LangSmith** for debugging slow nodes
4. **Adjust similarity threshold** (0.85 is good default; higher = stricter)
5. **Run scheduler mode** for 24/7 operations (vs. single run)

---

## 🔐 Security Considerations

⚠️ **Never commit `.env` to git** - use `.env.example` for templates

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "chroma_data/" >> .gitignore
```

Use environment variable management:

```bash
# Option 1: GitHub Secrets (if using CI/CD)
# Option 2: Docker Secrets (if using Docker)
# Option 3: AWS Secrets Manager (if using cloud)
```

---

## 📝 API Keys & Signup

Get your API keys from:

| Service | Link | Cost |
|---------|------|------|
| OpenAI | https://platform.openai.com/api-keys | $0.02 per 1M input tokens |
| Groq | https://console.groq.com/keys | Free tier available |
| Telegram Bot | @BotFather on Telegram | Free |
| LangSmith | https://smith.langchain.com | Free tier |
| PostgreSQL | Self-hosted or cloud | Varies |

---

## 🤝 Contributing

To extend the system:

1. Add new collectors in `app/collectors/`
2. Add new ranking factors in `app/ranking/scorer.py`
3. Customize summaries in `app/summarization/prompts.py`
4. Modify newsletter format in `app/newsletter/formatter.py`

---

## 📄 License

MIT License - Feel free to modify and distribute

---

## 🎓 Learning Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Telegram Bot API](https://core.telegram.org/bots)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

## 💡 Roadmap

- [ ] Web dashboard for newsletter preview
- [ ] User preferences & personalization
- [ ] Multi-language support
- [ ] Email delivery option
- [ ] Slack integration
- [ ] SaaS subscription model
- [ ] Advanced analytics

---

**Questions?** Check `AGENTS.md` for system architecture and engineering principles.

**Last Updated:** May 9, 2024
