# 🎯 Deployment Checklist

Your AI News Agent is **production-ready**. Follow these steps to deploy to Render.

---

## ✅ Pre-Deployment Checklist

### Local Setup (Already Done ✓)
- [x] Repository initialized on GitHub
- [x] Free embeddings (HuggingFace) configured
- [x] PostgreSQL made optional (free tier mode)
- [x] Telegram integration ready
- [x] LangGraph workflow compiled (10 nodes)
- [x] Docker configuration prepared
- [x] Environment validation passed

### Your Action Items (Complete These)

#### Step 1: Get API Keys (5 minutes)
- [ ] **Groq API Key**
  - Go to https://console.groq.com
  - Sign up / Log in
  - Create API key
  - Copy to clipboard

- [ ] **Telegram Bot Token**
  - Open Telegram, find @BotFather
  - Send `/newbot`
  - Follow prompts, get token
  - Copy to clipboard

- [ ] **Telegram Chat ID**
  - Open Telegram, find @userinfobot
  - Send `/start`
  - Get your numeric chat ID
  - Copy to clipboard

#### Step 2: Deploy to Render (5 minutes)
- [ ] Sign up to https://render.com (use GitHub login)
- [ ] Click **New** → **Web Service**
- [ ] Select repository: `ai-news-intelligence`
- [ ] Set configuration:
  - Name: `ai-news-agent`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python main.py --mode workflow`
  - Plan: **Free**
- [ ] Add environment variables (mark as **Secret**):
  - `GROQ_API_KEY=` (from step 1)
  - `TELEGRAM_BOT_TOKEN=` (from step 1)
  - `TELEGRAM_CHAT_ID=` (from step 1)
- [ ] Click **Create Web Service**
- [ ] Wait for build (2-3 minutes)
- [ ] Check logs for: `Newsletter sent to Telegram`

#### Step 3: Schedule Daily Runs (2 minutes)
- [ ] In Render dashboard, click **New** → **Cron Job**
- [ ] Set configuration:
  - Name: `ai-news-daily`
  - Schedule: `0 9 * * *` (daily at 9 AM UTC)
  - Select same repository
  - Build Command: `pip install -r requirements.txt`
  - Run Command: `python main.py --mode workflow`
- [ ] Add same environment variables
- [ ] Click **Create Cron Job**

#### Step 4: Verify It Works (1 minute)
- [ ] Open your Telegram chat
- [ ] Look for first newsletter message
- [ ] Confirm you received news summary

---

## 📊 System Status

| Component | Status | Notes |
|-----------|--------|-------|
| Graph Workflow | ✅ 10 nodes compiled | DAG fully wired |
| Embeddings | ✅ HuggingFace local | Free, 384-dim vectors |
| Vector Store | ✅ ChromaDB ready | Semantic deduplication |
| Checkpointer | ✅ In-memory (default) | PostgreSQL optional |
| Telegram | ✅ Ready | Polling mode |
| Collectors | ✅ 8 sources | Async parallel collection |
| LLM | ✅ Groq free | Llama-3.3-70b |

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Quick start, modes, API keys |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & workflow |
| [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) | Detailed Render setup (you are here) |
| [AGENTS.md](AGENTS.md) | Agent definitions, responsibilities |
| [CLAUDE.md](CLAUDE.md) | Development commands reference |

---

## 🔧 If Things Go Wrong

### Build fails on Render
- Check logs: Dashboard → Service → Logs
- Verify `requirements.txt` is in repo root
- Ensure no uncommitted changes: `git status`

### No Telegram messages
- Verify token is correct (test with curl)
- Check Telegram chat ID
- Review logs for errors

### Service keeps spinning down
- This is normal on free tier (15 min inactivity)
- Use Render Cron Jobs to keep it alive (recommended)
- Or use external cron service

### Embeddings not working
- Check HuggingFace model downloads (~80MB first time)
- Ensure internet connection is stable
- Wait for model cache to populate

---

## 💰 Cost Summary

**Total Monthly Cost: $0**

| Service | Cost | Usage |
|---------|------|-------|
| Groq API | $0 | Free tier (rate limited) |
| Render Hosting | $0 | Free tier (750 hrs/month) |
| Telegram Bot | $0 | Official API |
| HuggingFace | $0 | Free tier |
| **Total** | **$0** | **Completely free** |

---

## 🚀 Next Steps

1. **Complete the checklist above** ↑
2. **Verify first run** (check your Telegram)
3. **Monitor logs** in Render dashboard
4. **Enjoy daily AI news!**

---

## 📞 Need Help?

- **Render Docs**: https://render.com/docs
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Groq API**: https://console.groq.com/docs
- **Telegram Bot**: https://core.telegram.org/bots

---

**Everything is ready. You just need to complete the 4 checklist steps above. Total time: ~15 minutes. Let's go! 🎉**
