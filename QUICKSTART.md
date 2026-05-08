# 🚀 Quick Start Guide - AI News Research Agent

Get the system running in 5 minutes!

## Prerequisites

- Python 3.10+
- API Keys: OpenAI, Groq, Telegram

## Step 1: Clone & Setup (1 min)

```bash
# Clone/extract project
cd ai-news-agent

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Get API Keys (2 min)

### OpenAI (Embeddings) - Required
```
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy the key
```

### Groq (LLM) - Required
```
1. Go to https://console.groq.com/keys
2. Create new API key
3. Copy the key
```

### Telegram Bot - Required
```
1. Open Telegram and search for @BotFather
2. Send /newbot
3. Follow prompts to create bot
4. Copy the bot token
5. Send @userinfobot to get your chat ID
```

## Step 3: Configure (1 min)

```bash
# Copy template
cp .env.example .env

# Edit with your keys
# Windows:   notepad .env
# Mac/Linux: nano .env

# Required variables to update:
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
TELEGRAM_BOT_TOKEN=123:ABC...
TELEGRAM_CHAT_ID=987654321
```

## Step 4: Validate (1 min)

```bash
python validate_production.py
```

This will check all components are working correctly.

## Step 5: Run! (Choose one)

### Option A: Generate one newsletter now
```bash
python main.py --mode workflow
```

### Option B: Run 24/7 scheduler (newsletter every day at 9 AM)
```bash
python main.py --mode scheduler
```

### Option C: Start Telegram bot (interactive commands)
```bash
python main.py --mode bot
```

Then in Telegram:
- `/start` - Show commands
- `/daily` - Get today's newsletter
- `/trending` - Trending topics
- `/opensource` - Open source launches
- `/research` - Research highlights

---

## 🐳 Using Docker (Alternative)

```bash
# Make deploy script executable
chmod +x deploy.sh

# Start all services (includes PostgreSQL)
./deploy.sh up

# View logs
./deploy.sh logs

# Stop
./deploy.sh down
```

---

## ✅ Verify It's Working

Watch the logs:
```bash
# If running directly
python main.py --mode workflow

# If using Docker
./deploy.sh logs
```

You should see:
```
INFO | collect_news | Starting collection from 8 sources
INFO | deduplicate | Deduplicated 180 items -> 125 unique
INFO | summarize | Generated 25 summaries
INFO | Newsletter sent to Telegram
```

---

## 🔧 Troubleshooting

### "No module named 'app'"
```bash
# Make sure you're in the project root directory
cd ai-news-agent
```

### "OPENAI_API_KEY not found"
```bash
# Verify .env is in project root
ls -la .env

# Check it has your key
cat .env | grep OPENAI_API_KEY
```

### "Telegram send failed"
```bash
# Verify credentials
# 1. Bot token starts with numbers:
# 2. Chat ID is 9-10 digits
# 3. Get fresh token from @BotFather if needed
```

### "PostgreSQL connection failed"
```bash
# It's optional - system uses in-memory by default
# Leave POSTGRES_URL empty unless you have a database
```

---

## 📊 Next Steps

1. **Customize newsletter** - Edit `app/newsletter/formatter.py`
2. **Add sources** - Create new collectors in `app/collectors/`
3. **Change schedule** - Update `NEWSLETTER_HOUR` in `.env`
4. **Monitor performance** - Enable `LANGCHAIN_API_KEY` for LangSmith
5. **Deploy to cloud** - Use `docker/docker-compose.yml`

---

## 📖 Documentation

- **Full Setup** - See [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)
- **Architecture** - See [AGENTS.md](AGENTS.md)
- **System Design** - See [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🆘 Need Help?

1. Run validation: `python validate_production.py`
2. Check logs carefully for specific errors
3. Verify all API keys are correct
4. Make sure you have internet connection
5. Try single workflow mode first: `python main.py --mode workflow`

---

**You're all set! 🎉**

The system is now collecting and summarizing AI news 24/7.
