# 📚 API Reference

This document provides detailed API documentation for the AI News Agent.

---

## 🏗️ Core Modules

### Collectors

#### RSS Collector

```python
from app.collectors.rss import RSSCollector

collector = RSSCollector()

# Collect from multiple feeds
news_items = collector.collect([
    "https://rss.example.com/feed.xml",
    "https://another.com/rss"
])

# Returns: List[NewsItem]
```

#### GitHub Collector

```python
from app.collectors.github import GitHubCollector

collector = GitHubCollector()

# Get trending repos
repos = collector.get_trending(language="python", since="daily")

# Returns: List[GitHubRepo]
```

#### HackerNews Collector

```python
from app.collectors.hackernews import HackerNewsCollector

collector = HackerNewsCollector()

# Get top AI stories
stories = collector.get_top_stories(limit=20, tag="ai")

# Returns: List[HackerNewsStory]
```

---

### Graph Workflow

#### State Definition

```python
from typing import TypedDict, List, Dict

class NewsState(TypedDict):
    """State schema for LangGraph workflow."""
    raw_news: List[Dict]           # Raw news from collectors
    unique_news: List[Dict]        # Deduplicated news
    ranked_news: List[Dict]        # Ranked by importance
    summaries: List[str]           # LLM summaries
    newsletter: str                # Final newsletter
    errors: List[str]              # Error messages
```

#### Workflow Builder

```python
from app.graph.builder import build_workflow

# Build the workflow graph
workflow = build_workflow()

# Compile for execution
app = workflow.compile()

# Run the workflow
result = app.invoke({
    "raw_news": [],
    "unique_news": [],
    "ranked_news": [],
    "summaries": [],
    "newsletter": "",
    "errors": []
})
```

---

### Ranking

#### Scorer

```python
from app.ranking.scorer import NewsScorer

scorer = NewsScorer()

# Score a news item
score = scorer.score_item(news_item)

# Returns: float (0.0 - 1.0)

# Score multiple items
ranked = scorer.rank_news(news_items)
# Returns: List[Tuple[NewsItem, float]]
```

#### Deduplication

```python
from app.ranking.deduplication import Deduplicator

dedup = Deduplicator(threshold=0.85)

# Find duplicates
unique_items = dedup.deduplicate(news_items)

# Returns: List[NewsItem]
```

---

### Summarization

#### LLM Summarizer

```python
from app.summarization.summarizer import Summarizer

summarizer = Summarizer()

# Summarize a news item
summary = summarizer.summarize(news_item)

# Returns: str (formatted summary)

# Summarize multiple items
summaries = summarizer.summarize_batch(news_items)
# Returns: List[str]
```

---

### Newsletter

#### Generator

```python
from app.newsletter.generator import NewsletterGenerator

generator = NewsletterGenerator()

# Generate newsletter
newsletter = generator.generate(
    ranked_news=ranked_items,
    summaries=summaries
)

# Returns: str (formatted newsletter)
```

#### Formatter

```python
from app.newsletter.formatter import NewsletterFormatter

formatter = NewsletterFormatter()

# Format for Telegram
messages = formatter.format_for_telegram(newsletter)

# Returns: List[str] (chunked messages)
```

---

### Telegram Bot

#### Bot Setup

```python
from app.telegram.bot import TelegramBot

bot = TelegramBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

# Start polling
bot.run()

# Or set webhook
bot.set_webhook("https://your-domain.com/webhook")
```

#### Command Handlers

```python
from app.telegram.handlers import handle_daily, handle_help

# /daily - Send today's newsletter
await handle_daily(bot, update, context)

# /help - Show help message
await handle_help(bot, update, context)
```

---

### Configuration

#### Settings

```python
from app.config.settings import Settings

# Load settings
settings = Settings()

# Access configuration
print(settings.groq_api_key)
print(settings.telegram_chat_id)
print(settings.newsletter_hour)
```

---

## 🔧 Internal Services

### Database

```python
from app.database.postgres import Database

db = Database()

# Save news item
db.save_news_item(news_item)

# Get recent news
recent = db.get_recent_news(limit=10)

# Save newsletter
db.save_newsletter(newsletter)
```

### Vector Store

```python
from app.memory.vectorstore import VectorStore

store = VectorStore()

# Add embeddings
store.add(news_items)

# Search similar
similar = store.search(query, limit=5)

# Delete old embeddings
store.cleanup(days=30)
```

### Observability

```python
from app.observability.langsmith import setup_tracing

# Setup LangSmith tracing
tracer = setup_tracing(
    project_name="ai-news-agent",
    api_key=os.getenv("LANGCHAIN_API_KEY")
)

# Use in workflow
with tracer.trace("collect_news") as span:
    # Your code here
    pass
```

---

## 📋 Data Models

### NewsItem

```python
class NewsItem(BaseModel):
    title: str
    url: str
    source: str
    timestamp: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = []
```

### RankedItem

```python
class RankedItem(BaseModel):
    news_item: NewsItem
    score: float
    category: str
    rank: int
```

### Newsletter

```python
class Newsletter(BaseModel):
    date: str
    header: str
    sections: List[NewsletterSection]
    footer: str
```

---

## 🔄 Error Handling

### Custom Exceptions

```python
from app.utils.exceptions import (
    CollectorError,
    SummarizationError,
    TelegramError,
    RateLimitError
)

# Handle specific errors
try:
    news = collector.collect(feeds)
except RateLimitError:
    # Wait and retry
    time.sleep(60)
    news = collector.collect(feeds)
except CollectorError as e:
    logger.error(f"Collection failed: {e}")
```

---

## 📝 Type Hints

All public functions include type hints:

```python
def collect_news(feeds: List[str]) -> List[NewsItem]:
    """Collect news from RSS feeds.
    
    Args:
        feeds: List of RSS feed URLs.
        
    Returns:
        List of NewsItem objects.
        
    Raises:
        CollectorError: If collection fails.
    """
    ...
```

---

## 🔒 Security

- All API keys loaded from environment variables
- No secrets stored in code
- Input validation on all endpoints
- Rate limiting on external APIs

---

*Last updated: 2026-05-09*