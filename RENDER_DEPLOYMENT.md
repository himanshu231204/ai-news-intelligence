# 🚀 Deploying to Render (Free)

This guide walks you through deploying the AI News Agent to [Render.com](https://render.com) on the free tier.

## Why Render?

- **Free tier**: 750 compute hours/month (enough for daily newsletters)
- **No credit card required** for free tier (just signup)
- **Auto-deploys** from GitHub
- **Easy environment variables** management
- **No persistent database needed** (we use in-memory checkpoints)

## Prerequisites

- GitHub account
- Render account (free signup)
- API keys: Groq, Telegram (get free at https://console.groq.com and @BotFather on Telegram)

---

## Step 1: Push to GitHub

```bash
git push origin main
```

Your repo: `https://github.com/himanshu231204/ai-news-intelligence`

---

## Step 2: Create Render Account

1. Go to https://render.com
2. Click **Sign up** with GitHub
3. Authorize access to your repos

---

## Step 3: Create a New Web Service

1. Dashboard → **New** → **Web Service**
2. Connect repository → Select `ai-news-intelligence`
3. Fill in:
   - **Name**: `ai-news-agent`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py --mode workflow`
4. Click **Create Web Service**

The app will start building (takes ~2 min)

---

## Step 4: Set Environment Variables

In Render dashboard:

1. Go to your service → **Environment**
2. Add these as **Secret** (not Public):

```
GROQ_API_KEY=your_groq_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

Optional (for LangSmith tracing):
```
LANGCHAIN_API_KEY=your_langchain_api_key_here
```

3. Click **Save changes**

The service will redeploy automatically.

---

## Step 5: Trigger Daily Newsletter

Since Render free web services sleep after 15 minutes of inactivity, we use **cron jobs** to wake them up and run the newsletter.

### Option A: Use Render Cron Jobs (Recommended)

1. Dashboard → **New** → **Cron Job**
2. Fill in:
   - **Name**: `ai-news-daily`
   - **Runtime**: Python 3.11
   - **Schedule**: `0 9 * * *` (daily at 9 AM UTC)
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python main.py --mode workflow`
3. Connect the same repository
4. Set same environment variables
5. Click **Create Cron Job**

The cron job will run once daily, wake up the service, collect news, and send via Telegram.

### Option B: External Cron Service (Free)

Use a free external cron service like https://www.cron-job.org:

```
Service URL: https://your-render-service-url/
Schedule: Daily at 9 AM UTC
```

(Not recommended—Render cron jobs are simpler)

---

## Step 6: Verify It Works

1. Trigger manually:
   ```bash
   curl -X POST https://your-service.onrender.com/
   ```

2. Check logs:
   - Dashboard → Service → **Logs**
   - Look for: `Newsletter sent to Telegram`

3. You should receive a message in Telegram!

---

## Limitations on Free Tier

| Feature | Free | Notes |
|---------|------|-------|
| Web service runtime | 750 hrs/month | Enough for daily runs |
| Cron job runtime | 750 hrs/month | Recommended for scheduling |
| Database | None | We use in-memory (no persistence) |
| Build time | ~2 min | First deploy only |
| Restart time | ~30 sec | Each cold start |

**Note**: Free web services spin down after 15 min of inactivity. Cron jobs are the best way to keep them running regularly.

---

## Upgrade Path (If Needed)

If you want persistent databases or higher uptime, upgrade to **Starter** ($7/month):
- Includes managed PostgreSQL
- Always-on web services
- Can enable `USE_POSTGRES_CHECKPOINT=true` for state persistence

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

### "Service spinning down too fast"
- This is normal on free tier
- Use Cron Jobs to schedule runs instead of keeping service alive

### "Out of compute hours"
- Free tier gets 750 hours/month = ~25 hours/day average
- If you exceed, upgrade to Starter or wait for monthly reset

---

## Monitoring

1. **Render Logs**:
   - Dashboard → Service → Logs
   - Check for errors

2. **LangSmith** (optional):
   - Set `LANGCHAIN_API_KEY` for full tracing
   - View at https://smith.langchain.com

3. **Telegram**:
   - Check your chat for newsletters
   - /start command shows available commands

---

## Cost Breakdown (Free Tier)

- **Groq API**: Free (rate limited)
- **Telegram Bot**: Free
- **Render hosting**: Free (750 hrs/month)
- **Embeddings**: Free (local HuggingFace)
- **Total**: **$0/month**

---

## Next Steps

- [ ] Push repo to GitHub
- [ ] Create Render account
- [ ] Connect repository
- [ ] Set environment variables
- [ ] Create Cron Job
- [ ] Test first run
- [ ] Verify Telegram messages

---

## Support

- **Render Docs**: https://render.com/docs
- **Python on Render**: https://render.com/docs/deploy-python
- **Cron Jobs**: https://render.com/docs/cron-jobs
- **GitHub Issues**: Submit bugs to this repo

---

**You're all set! Your AI News Agent is now running 24/7 on Render. 🎉**
