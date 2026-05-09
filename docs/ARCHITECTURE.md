# AI Intelligence Newsletter Agent - System Architecture

> Production-grade architecture documentation for the AI News Research Agent system.
> Updated with optimizations for API rate limits and token efficiency.

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph External_Sources
        direction TB
        RSS[RSS Feeds]
        HN[Hacker News]
        GH[GitHub Trending]
        ArXiv[ArXiv Papers]
        DEV[DEV.to]
    end

    subgraph Core_System["AI News Agent Core"]
        direction LR
        API[FastAPI Server]
        LG[LangGraph Orchestrator]
        DB[(SQLite)]
        VS[(ChromaDB)]
        LS[LangSmith]
    end

    subgraph Collectors["News Collectors"]
        direction TB
        RC[RSS Collector]
        HNC[HackerNews Collector]
        GHC[GitHub Collector]
        AC[ArXiv Collector]
        DC[DEV.to Collector]
    end

    subgraph Processing["Processing Pipeline"]
        direction TB
        MN[Merge Node]
        KF[keyword_filter]
        DN[Deduplication Node]
        FN[Filter Node]
        RN[Rank Node]
        SN[summarize_news]
        NLG[Newsletter Generator]
    end

    subgraph LLM_Providers["LLM Routing Layer"]
        direction TB
        GROQ[Groq Llama]
        OR[OpenRouter 5 Models]
        GM[Gemini Flash]
    end

    subgraph Telegram_Delivery["Telegram Bot"]
        TBot[Telegram Bot]
        Handlers[Command Handlers]
    end

    External_Sources --> Collectors
    Collectors --> Processing
    Processing --> Core_System
    Core_System --> LLM_Providers
    LLM_Providers --> Processing
    Core_System --> DB
    Core_System --> VS
    Core_System --> LS
    NLG --> Telegram_Delivery
```

---

## 2. Optimized Workflow Diagram

```mermaid
flowchart TD
    START([START]) --> COLLECT[collect_news]
    
    subgraph Collectors_Pipeline["Parallel Collectors"]
        direction TB
        C1[RSS Collector]
        C2[HackerNews Collector]
        C3[GitHub Collector]
        C4[ArXiv Collector]
        C5[DEV.to Collector]
    end
    
    COLLECT --> Collectors_Pipeline
    
    MERGE[merge_results] --> KF[keyword_filter]
    Collectors_Pipeline --> MERGE
    
    KF --> DN[deduplicate_news]
    
    DN --> FN[filter_low_quality]
    
    FN --> RN[rank_news]
    
    RN --> SN[summarize_news]
    
    SN --> NLG[generate_newsletter]
    
    NLG --> LNL[generate_linkedin]
    
    LNL --> STORE[store_results]
    
    STORE --> TELEGRAM[send_telegram]
    
    TELEGRAM --> END([END])
    
    %% AgentRouter Path
    COLLECT -->|AgentRouter Available| AGENT[agent_workflow]
    AGENT -->|Success| LNL
    AGENT -->|Failed| MERGE
```

---

## 3. Key Optimizations

### 3.1 Local Keyword Filtering
- **Before LLM calls** - Filters 46% of non-AI articles
- Uses high-signal keywords: OpenAI, Anthropic, Claude, GPT-5, Gemini, LangGraph, etc.
- No LLM needed - pure Python filtering

### 3.2 Batch Summarization
- **10 articles per LLM call** instead of 1-by-1
- 90% fewer API calls
- Uses asyncio semaphore (max 2 concurrent)

### 3.3 Token Optimization
- Only sends: title + short summary (200 chars) + source
- Does NOT send full article content

### 3.4 Provider Fallback Chain
```mermaid
flowchart TD
    START[LLM Request] --> GROQ[Groq llama-3.3-70b-versatile]
    GROQ -->|429 Rate Limit| OR1[OpenRouter Model 1]
    OR1 -->|429/404| OR2[OpenRouter Model 2]
    OR2 -->|429/404| OR3[OpenRouter Model 3]
    OR3 -->|429/404| OR4[OpenRouter Model 4]
    OR4 -->|429/404| OR5[OpenRouter Model 5]
    OR5 -->|Failed| FALLBACK[Deterministic Template]
    
    GROQ -->|Success| RETURN[Return Result]
    OR1 -->|Success| RETURN
    OR2 -->|Success| RETURN
    OR3 -->|Success| RETURN
    OR4 -->|Success| RETURN
    OR5 -->|Success| RETURN
```

### 3.5 Caching
- SQLite-based summary cache (7-day TTL)
- Reduces redundant API calls

### 3.6 Rate Limiting
- Exponential backoff: 2s → 4s → 8s (capped)
- Max 3 retries per provider

---

## 4. LLM Provider Routing

```mermaid
flowchart TD
    START([LLM Request]) --> CHECK_CACHE{Cache Hit?}
    CHECK_CACHE -->|Yes| RETURN_CACHE[Return Cached]
    CHECK_CACHE -->|No| GROQ[Groq Primary]
    
    GROQ --> GROQ_SUCCESS{Success?}
    GROQ_SUCCESS -->|Yes| CACHE_SET[Cache Result]
    GROQ_SUCCESS -->|No| RATE_LIMIT{Rate Limited?}
    
    RATE_LIMIT -->|Yes| BACKOFF[Exponential Backoff]
    BACKOFF --> GROQ_RETRY[Retry Groq]
    GROQ_RETRY --> GROQ_SUCCESS
    
    RATE_LIMIT -->|No| OR[OpenRouter Fallback]
    
    OR --> OR_SUCCESS{Success?}
    OR_SUCCESS -->|Yes| CACHE_SET
    OR_SUCCESS -->|No| TRY_NEXT[Try Next Model]
    
    TRY_NEXT -->|More Models| OR
    TRY_NEXT -->|All Failed| TEMPLATE[Template Fallback]
    
    CACHE_SET --> RETURN
    TEMPLATE --> RETURN
    RETURN_CACHE --> END([END])
```

---

## 5. Data Flow

```mermaid
flowchart LR
    subgraph Sources["Data Sources"]
        RSS_Feed[RSS Feeds]
        HN_API[HackerNews API]
        GH_API[GitHub API]
        ArXiv_API[ArXiv API]
    end
    
    subgraph Collectors["Collectors"]
        RC[RSS Collector]
        HNC[HN Collector]
        GHC[GitHub Collector]
    end
    
    subgraph Processing["Processing Pipeline"]
        MERGE[Merge Results]
        KF[keyword_filter]
        DEDUP[Deduplication]
        FILTER[Quality Filter]
        RANK[Rank]
    end
    
    subgraph LLM["LLM Processing"]
        BATCH[Batch Summarizer]
        ROUTER[LLM Router]
    end
    
    subgraph Output["Output Layer"]
        TELEGRAM[Telegram Newsletter]
        LINKEDIN[LinkedIn Newsletter]
        DRIVE[Google Drive]
    end
    
    RSS_Feed --> RC
    HN_API --> HNC
    GH_API --> GHC
    
    RC --> MERGE
    HNC --> MERGE
    GHC --> MERGE
    
    MERGE --> KF
    KF --> DEDUP
    DEDUP --> FILTER
    FILTER --> RANK
    
    RANK --> BATCH
    BATCH --> ROUTER
    
    ROUTER --> TELEGRAM
    ROUTER --> LINKEDIN
    LINKEDIN --> DRIVE
```

---

## 6. Newsletter Format

```mermaid
flowchart TB
    INPUT[Ranked News] --> CATEGORIZE[Categorize]
    
    CATEGORIZE --> SECTIONS[6 Sections]
    
    SECTIONS -->|Breaking| B1[Title + URL]
    SECTIONS -->|Model Releases| B2[Title + URL]
    SECTIONS -->|AI Agents| B3[Title + URL]
    SECTIONS -->|Research| B4[Title + URL]
    SECTIONS -->|Open Source| B5[Title + URL]
    SECTIONS -->|Products| B6[Title + URL]
    
    B1 --> FOOTER[Add Footer]
    B2 --> FOOTER
    B3 --> FOOTER
    B4 --> FOOTER
    B5 --> FOOTER
    B6 --> FOOTER
    
    FOOTER --> OUTPUT[Telegram + LinkedIn]
    
    FOOTER -->|Links| PROFILE[LinkedIn Profile]
    FOOTER -->|Links| GITHUB[GitHub]
    FOOTER -->|Links| SUBSCRIBE[LinkedIn Newsletter]
```

---

## 7. Telegram Delivery

```mermaid
flowchart TD
    START([Newsletter Ready]) --> FORMAT[Format Markdown]
    
    FORMAT --> SPLIT[Split if >3800 chars]
    
    SPLIT --> SEND[Send via Telegram API]
    
    SEND --> SUCCESS{Success?}
    SUCCESS -->|Yes| TRACK[Track Delivery]
    SUCCESS -->|No| RETRY[Retry 3x]
    
    RETRY --> RETRY_SUCCESS{Retry Success?}
    RETRY_SUCCESS -->|Yes| TRACK
    RETRY_SUCCESS -->|No| LOG[Log Error]
    
    TRACK --> END([END])
    
    subgraph Commands["Command Handlers"]
        C1["/daily"]
        C2["/trending"]
        C3["/subscribe"]
        C4["/unsubscribe"]
    end
    
    SEND --> Commands
```

---

## 8. Telegram Delivery Workflow

```mermaid
flowchart TD
    START([Newsletter Ready]) --> VALIDATE{Validate Message}
    
    VALIDATE -->|Empty| SKIP[Skip Send]
    VALIDATE -->|Valid| FORMAT[Format Markdown]
    
    FORMAT --> COLLAPSE[Collapse Duplicate Footers]
    
    COLLAPSE --> SPLIT{Split if >3800 chars?}
    
    SPLIT -->|Yes| CHUNK[Split into Chunks]
    SPLIT -->|No| SINGLE[Single Message]
    
    CHUNK --> SEND_LOOP[Send Chunk 1..N]
    SINGLE --> SEND_LOOP
    
    SEND_LOOP --> SEND_CHUNK[Send via Telegram API]
    
    SEND_CHUNK --> SUCCESS{Success?}
    SUCCESS -->|Yes| LOG[Log Delivery]
    SUCCESS -->|No| RETRY[Retry 3x with Backoff]
    
    RETRY --> RETRY_SUCCESS{Retry Success?}
    RETRY_SUCCESS -->|Yes| LOG
    RETRY_SUCCESS -->|No| ERROR[Log Error & Continue]
    
    LOG --> END([END])
    
    subgraph Commands["Command Handlers"]
        C1["/start"]
        C2["/help"]
        C3["/sources"]
        C4["/developerinfo"]
        C5["/daily"]
        C6["/trending"]
        C7["/opensource"]
        C8["/research"]
    end
    
    START -.-> Commands
```

### 8.1 Message Processing Pipeline

| Step | Description | Implementation |
|------|-------------|----------------|
| **Validation** | Skip empty messages | `if not message.strip()` |
| **Footer Deduplication** | Collapse repeated footer blocks | `_collapse_footer()` function |
| **Markdown Formatting** | Parse mode: Markdown | `parse_mode: "Markdown"` |
| **Message Splitting** | Split at 3800 chars | `textwrap.wrap()` |
| **Chunk Sending** | Send each chunk sequentially | `requests.post()` with retry |
| **Error Handling** | 3 retries with 2s backoff | `@sync_retry` decorator |

### 8.2 Command Handlers

| Command | Description | Response |
|---------|-------------|----------|
| `/start` | Welcome message | Bot introduction & commands |
| `/help` | Help menu | All available commands |
| `/sources` | List news sources | Configured RSS, GitHub, HN sources |
| `/developerinfo` | Developer info | LinkedIn, GitHub, tech stack |
| `/daily` | Full newsletter | Runs workflow, sends complete newsletter |
| `/trending` | Top 5 trending | Filters by score, sends top 5 |
| `/opensource` | Open source projects | Filters by keywords (github, repo, oss) |
| `/research` | Research papers | Filters by keywords (arxiv, paper, research) |

### 8.3 Workflow Execution

```mermaid
sequenceDiagram
    participant User
    participant Bot
    participant Workflow
    participant LLM
    participant Telegram_API
    
    User->>Bot: /daily command
    Bot->>Bot: Send "Collecting AI news..."
    Bot->>Workflow: Run LangGraph workflow
    Workflow->>LLM: Process & summarize news
    LLM-->>Workflow: Return newsletter
    Workflow-->>Bot: Newsletter result
    Bot->>Bot: Delete progress message
    Bot->>Telegram_API: Send newsletter chunks
    Telegram_API-->>Bot: Success
    Bot-->>User: Newsletter message(s)
```

### 8.4 Error Handling

- **Empty message**: Skip sending, log warning
- **Missing config**: Skip sending, log warning
- **API failure**: Retry 3 times with exponential backoff (2s → 4s → 8s)
- **Chunk failure**: Continue with remaining chunks, log errors
- **Workflow failure**: Return error message to user

### 8.5 Configuration Requirements

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot API token from @BotFather | Yes |
| `TELEGRAM_CHAT_ID` | Target chat ID for newsletters | Yes |

---

## 9. Component Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| Orchestration | LangGraph | Workflow management |
| API Server | FastAPI | REST endpoints |
| Database | SQLite | Persistent storage |
| Vector Store | ChromaDB | Semantic search/dedup |
| Observability | LangSmith | Tracing & monitoring |
| Messaging | Telegram Bot | User delivery |
| LLM Primary | Groq Llama | Fast processing |
| LLM Fallback | OpenRouter (5 models) | Rate limit handling |
| LLM Formatting | Gemini Flash | Final polish |
| Caching | SQLite | Summary cache (7-day TTL) |

---

## 10. Environment Variables

```mermaid
flowchart LR
    subgraph Config["Configuration"]
        direction TB
        ENV[.env file]
        Settings[pydantic Settings]
    end
    
    ENV --> Settings
    
    subgraph Variables["Required Variables"]
        direction TB
        V1[GROQ_API_KEY]
        V2[OPENROUTER_API_KEY]
        V3[TELEGRAM_BOT_TOKEN]
        V4[TELEGRAM_CHAT_ID]
        V5[GOOGLE_SERVICE_ACCOUNT]
    end
    
    Settings --> Variables
```

---

## 11. State Schema

```mermaid
classDiagram
    class NewsState {
        +List[NewsItem] raw_news
        +List[NewsItem] merged_news
        +List[NewsItem] unique_news
        +List[NewsItem] filtered_news
        +List[NewsItem] ranked_news
        +List[str] summaries
        +str newsletter
        +str linkedin_newsletter
        +str google_doc_link
        +List[str] errors
        +Dict metadata
    }
    
    class NewsItem {
        +str source
        +str title
        +str url
        +datetime published_at
        +float score
        +str summary
        +str company
        +str category
        +float importance_score
    }
    
    NewsState --> NewsItem
```

---

*Document Version: 2.0*
*Updated: May 2026*
*Key Changes: Added keyword filtering, batch summarization, provider fallbacks, caching*