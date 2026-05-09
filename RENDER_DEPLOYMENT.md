# 🚀 Deploying to Render (Free)

This guide walks you through deploying the AI News Agent to [Render.com](https://render.com) on the free tier.

## Why Render?

- **Free tier**: 750 compute hours/month (enough for daily newsletters)
- **No credit card required** for free tier (just signup)
- **Auto-deploys** from GitHub
- **Easy environment variables** management
- **Optimized for API efficiency** - our optimizations reduce API calls by 90%

## Prerequisites

- GitHub account
- Render account (free signup)
- API keys: Groq, OpenRouter, Gemini, Telegram

---

## Step 1: Push to GitHub

```bash
git add .
git commit -m "Setup for Render deployment"
git push origin main
```

---

## Step 2: Create Render Account

1. Go to https://render.com
2. Click **Sign up** with GitHub
3. Authorize access to your repos

---

## Step 3: Create a Background Worker (Recommended)

We use a **Background Worker** instead of Web Service because:
- Better for scheduled tasks
- Runs continuously without spinning down
- More suitable for long-running newsletter generation

1. Dashboard → **New** → **Background Worker**
2. Connect repository → Select your repo
3. Fill in:
   - **Name**: `news-agent-scheduler`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py --mode scheduler --scheduled`
4. Click **Create Worker**

---

## Step 4: Set Environment Variables

In Render dashboard:

1. Go to your worker → **Environment**
2. Add these as **Secret**:

### Required Variables
```
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### Optional Variables
```
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_TRACING_V2=true
GOOGLE_SERVICE_ACCOUNT_JSON={"your_json_here"}
```

3. Click **Save Changes**

The worker will redeploy automatically.

---

## Step 5: Configure Scheduler

The worker runs 24/7 but we need to set when to send the newsletter.

In your worker environment, add:
```
NEWSLETTER_HOUR=9
NEWSLETTER_MINUTE=0
```

This runs at 9:00 AM UTC daily.

---

## Step 6: Verify It Works

1. Check logs:
   - Dashboard → Worker → **Logs**
   - Look for: `Workflow completed successfully`

2. You should receive a newsletter in Telegram!

---

## Alternative: Use Cron Job (If Worker Not Available)

If you prefer using Render's cron job feature:

1. Dashboard → **New** → **Cron Job**
2. Fill in:
   - **Name**: `ai-news-daily`
   - **Runtime**: Python 3.11
   - **Schedule**: `0 9 * * *` (daily at 9 AM UTC)
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python main.py --mode workflow --scheduled`
3. Connect the same repository
4. Set same environment variables
5. Click **Create Cron Job**

---

## Optimizations for Free Tier

Our system is optimized to work within free tier limits:

| Optimization | Benefit |
|-------------|---------|
| **Keyword Filtering** | Filters 46% of articles BEFORE LLM calls |
| **Batch Summarization** | 90% fewer API calls (10 articles per call) |
| **Token Optimization** | Sends only title + short summary |
| **Caching** | 7-day SQLite cache reduces redundant calls |
| **Rate Limiting** | Exponential backoff prevents 429 errors |

---

## Limitations on Free Tier

| Feature | Free | Notes |
|---------|------|-------|
| Worker runtime | 750 hrs/month | Enough for daily newsletters |
| Cron job runtime | 750 hrs/month | Alternative option |
| Build time | ~3 min | First deploy only |
| Memory | 512 MB | Sufficient for our workload |

---

## Troubleshooting

### "Service build failed"
- Check Python version (need 3.10+)
- Check `requirements.txt` is in repo root
- Check logs in Render dashboard

### "Newsletter not sending"
- Verify Telegram token is correct (@BotFather)
- Check Telegram chat ID (@userinfobot)
- View logs for errors

### "Rate limit errors"
- This is expected on free tier
- Our optimizations handle this automatically with exponential backoff

### "Out of compute hours"
- Free tier gets 750 hours/month
- If you exceed, upgrade to paid plan or wait for monthly reset

---

## Monitoring

1. **Render Logs**:
   - Dashboard → Worker → Logs
   - Check for errors

2. **LangSmith** (optional):
   - Set `LANGCHAIN_API_KEY` for full tracing
   - View at https://smith.langchain.com

3. **Telegram**:
   - Check your chat for newsletters

---

## Cost Breakdown (Free Tier)

- **Groq API**: Free (rate limited)
- **OpenRouter API**: Free (fallback)
- **Gemini API**: Free (formatting)
- **Telegram Bot**: Free
- **Render hosting**: Free (750 hrs/month)
- **Embeddings**: Free (local HuggingFace)
- **Total**: **$0/month**

---

## Next Steps

- [ ] Push repo to GitHub
- [ ] Create Render account
- [ ] Connect repository
- [ ] Create Background Worker
- [ ] Set environment variables
- [ ] Test first run
- [ ] Verify Telegram messages

---

## Support

- **Render Docs**: https://render.com/docs
- **Python on Render**: https://render.com/docs/deploy-python
- **Cron Jobs**: https://render.com/docs/cron-jobs

---

**You're all set! Your AI News Agent is now running 24/7 on Render. 🎉**