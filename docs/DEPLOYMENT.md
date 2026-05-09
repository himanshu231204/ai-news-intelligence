# 🚀 Deployment Guide

This guide covers deploying the AI News Agent to production environments.

---

## 🏭 Deployment Options

| Platform | Cost | Difficulty | Best For |
|----------|------|------------|----------|
| Render | Free | Easy | Beginners |
| Railway | $5/mo | Easy | Small projects |
| Docker | Varies | Medium | Self-hosted |
| Kubernetes | Varies | Hard | Enterprise |

---

## ☁️ Render Deployment (Free Tier)

### Step 1: Prepare Repository

```bash
# Ensure these files exist:
# - main.py
# - requirements.txt
# - .env.example
# - docker/Dockerfile
# - render.yaml (optional)
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 3: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize repository access

### Step 4: Create Web Service

1. Click **New** → **Web Service**
2. Select your repository
3. Configure:

| Setting | Value |
|---------|-------|
| Name | ai-news-agent |
| Region | Oregon (or closest) |
| Branch | main |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python main.py --mode workflow` |

4. Click **Create Web Service**

### Step 5: Set Environment Variables

In Render dashboard, go to **Environment** and add:

```
GROQ_API_KEY=your_groq_key
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
LANGCHAIN_API_KEY=your_langsmith_key  # optional
```

### Step 6: Create Cron Job (Optional)

For daily newsletters:

1. Click **New** → **Cron Job**
2. Configure:

| Setting | Value |
|---------|-------|
| Name | daily-newsletter |
| Schedule | `0 9 * * *` (9 AM daily) |
| Command | `python main.py --mode workflow` |

3. Select your web service as the target

---

## 🚂 Railway Deployment

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Step 2: Initialize Project

```bash
railway init
# Select "Empty Project"
```

### Step 3: Add Database (Optional)

```bash
railway add postgres
```

### Step 4: Deploy

```bash
railway up
```

### Step 5: Set Environment

```bash
railway variables set GROQ_API_KEY=xxx
railway variables set TELEGRAM_BOT_TOKEN=xxx
railway variables set TELEGRAM_CHAT_ID=xxx
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--mode", "workflow"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    env_file:
      - .env
    volumes:
      - ./chroma_data:/app/chroma_data
      - ./newsletter.db:/app/newsletter.db

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: news_agent
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Build & Run

```bash
# Build
docker build -t ai-news-agent .

# Run
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## ☸️ Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-news-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-news-agent
  template:
    metadata:
      labels:
        app: ai-news-agent
    spec:
      containers:
      - name: app
        image: your-registry/ai-news-agent:latest
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: groq-api-key
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: telegram-bot-token
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Apply

```bash
kubectl apply -f deployment.yaml
```

---

## 🔒 Production Checklist

Before going live:

- [ ] All API keys are environment variables
- [ ] No hardcoded secrets in code
- [ ] HTTPS enabled (if using custom domain)
- [ ] Logging configured
- [ ] Error monitoring set up
- [ ] Backups configured (for PostgreSQL)
- [ ] Health checks implemented

---

## 📊 Environment Variables for Production

```env
# Required
GROQ_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id

# Database
POSTGRES_URL=postgresql+psycopg://user:pass@host:5432/db

# Observability
LANGCHAIN_API_KEY=your_key
LANGCHAIN_TRACING_V2=true

# Logging
LOG_LEVEL=INFO
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

- Use multiple workers with task queue (Celery/Redis)
- Separate collectors from processors

### Vertical Scaling

- Increase memory for ChromaDB
- Use GPU for embedding generation

### Caching

- Cache LLM responses
- Cache RSS feed results

---

## 🔧 Health Checks

Add to your deployment:

```python
# health.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-news-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-news-agent/discussions)

---

*Last updated: 2026-05-09*