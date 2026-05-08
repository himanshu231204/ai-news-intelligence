# AI News Research Agent - AGENTS.md

## Project Overview

This project is an AI-powered autonomous research and newsletter generation system.

The system collects AI-related news and updates from multiple sources such as:
- X.com (Twitter)
- Reddit
- Hacker News
- RSS feeds
- GitHub Trending

The workflow filters, ranks, summarizes, and generates a high-quality AI newsletter every 24 hours.

The final newsletter is delivered through a Telegram bot.

The system is built using:
- LangGraph
- LangChain
- LangSmith
- FastAPI
- PostgreSQL
- ChromaDB/FAISS
- Telegram Bot API

---

# PRIMARY OBJECTIVE

Build a production-ready AI agent system that:

1. Collects AI news automatically
2. Filters low-quality information
3. Removes duplicate news
4. Ranks news by importance
5. Summarizes updates using LLMs
6. Generates a professional newsletter
7. Sends results to Telegram
8. Supports personalization
9. Supports future multi-agent architecture
10. Supports future SaaS monetization

---

# CORE ENGINEERING PRINCIPLES

## 1. Modular Architecture

Every component must be isolated and reusable.

Do NOT create monolithic files.

Use separate modules for:
- collectors
- ranking
- summarization
- memory
- Telegram
- prompts
- workflows

---

## 2. LangGraph-First Design

This project MUST use LangGraph as the orchestration engine.

The workflow should use:
- StateGraph
- Nodes
- Edges
- Parallel execution
- Conditional routing
- Checkpointers
- Memory

Avoid linear scripts.

---

## 3. Multi-Agent Friendly

The architecture should support future migration to:
- supervisor agents
- specialized agents
- collaborative agent workflows

Every major workflow stage should be independently replaceable.

---

## 4. Production-Ready Code

Code should include:
- type hints
- docstrings
- logging
- retry handling
- error handling
- async support where useful

Avoid toy-project code.

---

# RECOMMENDED PROJECT STRUCTURE

```text
ai-news-agent/
│
├── app/
│   ├── graph/
│   │   ├── workflow.py
│   │   ├── state.py
│   │   ├── builder.py
│   │   └── nodes/
│   │
│   ├── collectors/
│   │   ├── twitter.py
│   │   ├── reddit.py
│   │   ├── rss.py
│   │   ├── github.py
│   │   └── hackernews.py
│   │
│   ├── ranking/
│   │   ├── scorer.py
│   │   ├── deduplication.py
│   │   └── embeddings.py
│   │
│   ├── summarization/
│   │   ├── summarizer.py
│   │   └── prompts.py
│   │
│   ├── newsletter/
│   │   ├── generator.py
│   │   └── formatter.py
│   │
│   ├── telegram/
│   │   ├── bot.py
│   │   └── handlers.py
│   │
│   ├── memory/
│   │   ├── checkpoint.py
│   │   └── vectorstore.py
│   │
│   ├── database/
│   │   ├── postgres.py
│   │   └── models.py
│   │
│   ├── observability/
│   │   └── langsmith.py
│   │
│   ├── scheduler/
│   │   └── jobs.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   └── utils/
│
├── tests/
│
├── docker/
│
├── requirements.txt
│
├── .env
│
├── main.py
│
└── AGENTS.md
```

---

# SYSTEM WORKFLOW

## Main Workflow

```text
START
  │
  ▼
collect_news
  │
  ▼
merge_results
  │
  ▼
deduplicate_news
  │
  ▼
filter_low_quality
  │
  ▼
rank_news
  │
  ▼
summarize_news
  │
  ▼
generate_newsletter
  │
  ▼
store_results
  │
  ▼
send_telegram
  │
  ▼
END
```

---

# LANGGRAPH REQUIREMENTS

The workflow MUST:

* use StateGraph
* support parallel nodes
* support retries
* support async execution
* support future human-in-the-loop workflows
* support checkpointing
* support persistent memory

---

# GRAPH STATE SCHEMA

Use strongly typed state.

Example:

```python
from typing import TypedDict, List, Dict

class NewsState(TypedDict):
    raw_news: List[Dict]
    unique_news: List[Dict]
    ranked_news: List[Dict]
    summaries: List[str]
    newsletter: str
    errors: List[str]
```

---

# AGENT DEFINITIONS

## 1. Source Collection Agent

Responsibilities:

* collect news from external sources
* normalize data
* validate metadata

Sources:

* X.com
* Reddit
* Hacker News
* RSS
* GitHub Trending

---

## 2. Deduplication Agent

Responsibilities:

* generate embeddings
* compare semantic similarity
* remove duplicate news

Use:

* OpenAI embeddings
* ChromaDB or FAISS

---

## 3. Ranking Agent

Responsibilities:

* rank importance
* detect trending topics
* score news quality

Ranking factors:

* virality
* technical importance
* community attention
* model releases
* open-source launches

---

## 4. Summarization Agent

Responsibilities:

* summarize articles
* explain importance
* generate concise outputs

Output format:

```text
Title:
Summary:
Why it matters:
Source:
```

---

## 5. Newsletter Generation Agent

Responsibilities:

* create final formatted newsletter
* organize sections
* generate readable output

Sections:

* Major AI News
* Open Source Launches
* Research Highlights
* Trending Discussions
* Tools Worth Watching

---

## 6. Telegram Delivery Agent

Responsibilities:

* send newsletters
* handle commands
* manage subscriptions

Commands:

* /daily
* /trending
* /opensource
* /research

---

# DATA COLLECTION RULES

## Important

Do NOT scrape aggressively.

Respect:

* rate limits
* robots.txt
* API restrictions

Prefer official APIs where possible.

---

# SOURCE PRIORITY

Priority order:

1. RSS feeds
2. GitHub Trending
3. Hacker News
4. Reddit
5. X.com

Build MVP without Twitter first.

---

# MEMORY REQUIREMENTS

The system should remember:

* previously sent news
* user interests
* duplicate articles
* ranking history

Use:

* LangGraph checkpointers
* PostgreSQL
* vector database

---

# OBSERVABILITY

Use LangSmith for:

* tracing
* debugging
* token tracking
* latency monitoring
* workflow analysis

Every important node should be traceable.

---

# ERROR HANDLING

The workflow should NEVER fail completely if one source fails.

Example:

```text
twitter collector fails
    ↓
continue workflow
```

Add:

* retries
* logging
* fallback handling

---

# PERFORMANCE REQUIREMENTS

The system should:

* support async execution
* support parallel collectors
* minimize LLM calls
* cache repeated operations

---

# SECURITY REQUIREMENTS

Never hardcode:

* API keys
* Telegram tokens
* DB credentials

Use:

* .env
* pydantic settings

---

# ENVIRONMENT VARIABLES

Required variables:

```env
OPENAI_API_KEY=
GROQ_API_KEY=
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
TELEGRAM_BOT_TOKEN=
POSTGRES_URL=
```

---

# RECOMMENDED MODELS

## Fast + Cheap

* Gemini Flash
* Groq Llama

## Premium

* GPT-5
* Claude

---

# DATABASE REQUIREMENTS

## PostgreSQL

Store:

* articles
* summaries
* rankings
* user settings
* newsletter history

---

# VECTOR DATABASE

Use:

* ChromaDB
  OR
* FAISS

Purpose:

* semantic search
* deduplication
* personalization

---

# PERSONALIZATION SUPPORT

Future architecture should support:

```python
preferences = {
    "topics": [
        "AI agents",
        "LangGraph",
        "Open-source LLMs"
    ]
}
```

The ranking system should prioritize matching interests.

---

# TELEGRAM UX RULES

Messages should:

* be concise
* readable
* properly formatted
* mobile friendly

Avoid giant text blocks.

---

# NEWSLETTER FORMAT

Example:

```text
🧠 AI Daily Brief — {date}

🔥 Major AI Updates
...

🚀 Open Source Launches
...

📚 Research Highlights
...

💡 Worth Watching
...
```

---

# DEVELOPMENT RULES

## ALWAYS:

* use type hints
* write modular code
* keep nodes independent
* add logging
* write reusable prompts
* keep prompts isolated

## NEVER:

* hardcode secrets
* write giant files
* tightly couple modules
* duplicate logic
* mix business logic with infrastructure

---

# FUTURE ROADMAP

## Phase 1

* RSS collection
* basic summarization
* Telegram delivery

## Phase 2

* Reddit
* GitHub trending
* ranking system

## Phase 3

* Twitter integration
* personalization
* vector memory

## Phase 4

* multi-agent supervisor architecture
* SaaS dashboard
* subscriptions
* real-time alerts

---

# FINAL ENGINEERING GOAL

The final system should evolve into:

```text
Personal AI Intelligence Platform
```

NOT just a newsletter bot.

Focus on:

* information quality
* ranking
* personalization
* automation
* scalability
* modular agents
