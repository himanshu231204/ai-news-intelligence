# AI Intelligence Newsletter Agent - System Architecture

> Production-grade architecture documentation for the AI News Research Agent system.

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph External_Sources
        direction TB
        RSS[RSS Feeds]
        HN[Hacker News]
        GH[GitHub Trending]
        RD[Reddit]
        X[Twitter/X.com]
    end

    subgraph Core_System["AI News Agent Core"]
        direction LR
        API[FastAPI Server]
        LG[LangGraph Orchestrator]
        DB[(PostgreSQL)]
        VS[(Vector Store)]
        LS[LangSmith]
    end

    subgraph Collectors["News Collectors"]
        direction TB
        RC[RSS Collector]
        HNC[HackerNews Collector]
        GHC[GitHub Collector]
        RDC[Reddit Collector]
        XC[Twitter Collector]
    end

    subgraph Processing["Processing Pipeline"]
        direction TB
        MN[Merge Node]
        FN[Filter Node]
        DN[Deduplication Node]
        RN[Rank Node]
        SN[Summarize Node]
        NLG[Newsletter Generator]
    end

    subgraph LLM_Providers["LLM Routing Layer"]
        direction TB
        GROQ[Groq Llama]
        OR[OpenRouter DeepSeek]
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

## 2. Detailed Workflow Diagram

```mermaid
flowchart TD
    START([START]) --> COLLECT[Collect News]
    
    subgraph Collectors_Pipeline["Parallel Collectors"]
        direction TB
        C1[RSS Collector]
        C2[HackerNews Collector]
        C3[GitHub Collector]
        C4[Reddit Collector]
        C5[Twitter Collector]
    end
    
    COLLECT --> Collectors_Pipeline
    
    subgraph Merge_Process["Merge Results"]
        direction LR
        M1[Normalize Data]
        M2[Validate Metadata]
        M3[Add Timestamps]
    end
    
    Collectors_Pipeline --> Merge_Process
    
    subgraph Filter_Process["Filter Low Quality"]
        direction LR
        F1[Remove Spam]
        F2[Filter Non-AI]
        F3[Validate Content]
    end
    
    Merge_Process --> Filter_Process
    
    subgraph Dedupe_Process["Deduplication"]
        direction LR
        D1[Generate Embeddings]
        D2[Semantic Similarity]
        D3[Remove Duplicates]
    end
    
    Filter_Process --> Dedupe_Process
    
    subgraph Rank_Process["Rank News"]
        direction LR
        R1[Calculate Virality]
        R2[Score Technical Impact]
        R3[Detect Trends]
        R4[Apply Weights]
    end
    
    Dedupe_Process --> Rank_Process
    
    subgraph Summarize_Process["Summarize News"]
        direction LR
        S1[Extract Key Info]
        S2[Generate Summary]
        S3[Add Context]
    end
    
    Rank_Process --> Summarize_Process
    
    subgraph Generate_Newsletter["Newsletter Generation"]
        direction LR
        N1[Organize Sections]
        N2[Format Content]
        N3[Add Metadata]
    end
    
    Summarize_Process --> Generate_Newsletter
    
    subgraph Storage["Store Results"]
        direction LR
        ST1[Save to PostgreSQL]
        ST2[Update Vector Store]
        ST3[Log to LangSmith]
    end
    
    Generate_Newsletter --> Storage
    
    subgraph Delivery["Telegram Delivery"]
        direction LR
        DL1[Format Message]
        DL2[Send to Users]
        DL3[Handle Commands]
    end
    
    Storage --> Delivery
    Delivery --> END([END])
```

---

## 3. LangGraph Workflow Diagram

```mermaid
flowchart TB
    START([START]) --> COLLECT[collect_news]
    
    subgraph Parallel_Collectors["Parallel Collectors"]
        direction TB
        PC1[RSS Node]
        PC2[HackerNews Node]
        PC3[GitHub Node]
    end
    
    COLLECT --> Parallel_Collectors
    
    MERGE[merge_results] --> FILTER[filter_low_quality]
    Parallel_Collectors --> MERGE
    
    FILTER --> DEDUP[deduplicate_news]
    
    DEDUP --> RANK[rank_news]
    
    RANK --> SUMMARIZE[summarize_news]
    
    SUMMARIZE --> GENERATE[generate_newsletter]
    
    GENERATE --> STORE[store_results]
    
    STORE --> TELEGRAM[send_telegram]
    
    TELEGRAM --> END([END])
    
    %% Conditional Edges
    MERGE -->|No results| END
    FILTER -->|All filtered| END
    TELEGRAM -->|Failed| RETRY[Retry 3x]
    RETRY --> TELEGRAM
```

---

## 4. LLM Provider Routing Diagram

```mermaid
flowchart TD
    START([LLM Request]) --> CHECK_GROQ{ Groq Available?}
    
    CHECK_GROQ -->|Yes| GROQ_PROCESS[Process with Groq Llama]
    CHECK_GROQ -->|No| CHECK_OR{ OpenRouter Available?}
    
    GROQ_PROCESS --> GROQ_SUCCESS{Success?}
    GROQ_SUCCESS -->|Yes| RETURN_RESULT[Return Result]
    GROQ_SUCCESS -->|No| RATE_LIMIT{Rate Limited?}
    
    RATE_LIMIT -->|Yes| CHECK_OR
    RATE_LIMIT -->|No| RETRY_GROQ[Retry Groq 2x]
    RETRY_GROQ --> GROQ_SUCCESS
    
    CHECK_OR -->|Yes| OR_PROCESS[Process with OpenRouter DeepSeek]
    CHECK_OR -->|No| CHECK_GM{ Gemini Available?}
    
    OR_PROCESS --> OR_SUCCESS{Success?}
    OR_SUCCESS -->|Yes| RETURN_RESULT
    OR_SUCCESS -->|No| CHECK_GM
    
    CHECK_GM -->|Yes| GM_PROCESS[Process with Gemini Flash]
    CHECK_GM -->|No| FALLBACK[Return Error / Cache]
    
    GM_PROCESS --> GM_SUCCESS{Success?}
    GM_SUCCESS -->|Yes| FORMAT[Format Output]
    GM_SUCCESS -->|No| FALLBACK
    
    FORMAT --> RETURN_RESULT
    
    RETURN_RESULT --> END([END])
    
    %% Styling
    style GROQ_PROCESS fill:#90EE90
    style OR_PROCESS fill:#87CEEB
    style GM_PROCESS fill:#DDA0DD
    style FALLBACK fill:#FFB6C1
```

---

## 5. Data Flow Diagram

```mermaid
flowchart LR
    subgraph Sources["Data Sources"]
        RSS_Feed[RSS Feed XML]
        HN_API[HackerNews API]
        GH_API[GitHub API]
        RD_API[Reddit API]
    end
    
    subgraph Collectors["Collectors"]
        RC[RSS Collector]
        HNC[HN Collector]
        GHC[GitHub Collector]
    end
    
    subgraph Normalize["Normalization Layer"]
        JSON[Convert to JSON]
        Validate[Validate Schema]
        Dedupe[Mark Duplicates]
    end
    
    subgraph Storage["Data Storage"]
        PG[(PostgreSQL)]
        VS[(Vector Store)]
    end
    
    subgraph LLM["LLM Processing"]
        Summarize[LLM Summarizer]
        Rank[LLM Ranker]
    end
    
    subgraph Output["Output Layer"]
        Newsletter[Newsletter]
        Telegram[Telegram Message]
    end
    
    RSS_Feed --> RC
    HN_API --> HNC
    GH_API --> GHC
    
    RC --> Normalize
    HNC --> Normalize
    GHC --> Normalize
    
    Normalize --> PG
    Normalize --> VS
    
    PG --> LLM
    VS --> LLM
    
    LLM --> Output
```

---

## 6. Collector Pipeline Diagram

```mermaid
flowchart TB
    START([Daily Trigger]) --> SCHEDULER[Scheduler]
    
    subgraph RSS_Collector["RSS Collector"]
        direction TB
        RSS1[Fetch Feed URLs]
        RSS2[Parse XML/Atom]
        RSS3[Extract Metadata]
        RSS4[Filter AI Content]
    end
    
    subgraph HN_Collector["HackerNews Collector"]
        direction TB
        HN1[Call HN API]
        HN2[Get Top Stories]
        HN3[Fetch Comments]
        HN4[Filter AI Tags]
    end
    
    subgraph GitHub_Collector["GitHub Collector"]
        direction TB
        GH1[Call GitHub API]
        GH2[Get Trending Repos]
        GH3[Filter by Language]
        GH4[Extract Metadata]
    end
    
    subgraph Merge_Node["Merge Node"]
        direction TB
        M1[Collect All Results]
        M2[Normalize Fields]
        M3[Add Source Tags]
        M4[Sort by Date]
    end
    
    SCHEDULER --> RSS_Collector
    SCHEDULER --> HN_Collector
    SCHEDULER --> GitHub_Collector
    
    RSS_Collector --> Merge_Node
    HN_Collector --> Merge_Node
    GitHub_Collector --> Merge_Node
    
    Merge_Node --> OUTPUT[Combined News List]
    
    %% Error Handling
    RSS_Collector -->|Error| LOG_RSS[Log Error]
    HN_Collector -->|Error| LOG_HN[Log Error]
    GitHub_Collector -->|Error| LOG_GH[Log Error]
    
    LOG_RSS --> CONTINUE1[Continue]
    LOG_HN --> CONTINUE2[Continue]
    LOG_GH --> CONTINUE3[Continue]
    
    CONTINUE1 --> Merge_Node
    CONTINUE2 --> Merge_Node
    CONTINUE3 --> Merge_Node
```

---

## 7. Newsletter Generation Pipeline

```mermaid
flowchart TB
    INPUT[Ranked News Items] --> CATEGORIZE[Categorize News]
    
    subgraph Categories["News Categories"]
        direction TB
        CAT1[Major AI Updates]
        CAT2[Open Source Launches]
        CAT3[Research Highlights]
        CAT4[Trending Discussions]
        CAT5[Tools Worth Watching]
    end
    
    CATEGORIZE --> Categories
    
    subgraph Per_Category["Per-Category Processing"]
        direction LR
        PC1[Select Top Items]
        PC2[Generate Summaries]
        PC3[Add Context]
        PC4[Format Output]
    end
    
    Categories --> Per_Category
    
    subgraph Assembly["Newsletter Assembly"]
        direction TB
        A1[Add Header]
        A2[Combine Sections]
        A3[Add Footer]
        A4[Apply Formatting]
    end
    
    Per_Category --> Assembly
    
    subgraph Final_Format["Final Formatting"]
        direction LR
        FF1[LLM Polish]
        FF2[Add Emojis]
        FF3[Validate Length]
        FF4[Generate Preview]
    end
    
    Assembly --> Final_Format
    
    Final_Format --> OUTPUT[Final Newsletter]
    
    %% Quality Gates
    FF1 -->|Poor Quality| REGENERATE[Regenerate]
    REGENERATE --> FF1
```

---

## 8. Telegram Delivery Workflow

```mermaid
flowchart TD
    START([Newsletter Ready]) --> FORMAT[Format for Telegram]
    
    subgraph Format["Message Formatting"]
        direction TB
        F1[Split Long Messages]
        F2[Add Markdown]
        F3[Add Preview]
        F4[Add Navigation]
    end
    
    FORMAT --> Format
    
    subgraph Send["Send Process"]
        direction TB
        S1[Get Subscriber List]
        S2[Batch Messages]
        S3[Send to Each User]
        S4[Track Delivery]
    end
    
    Format --> Send
    
    subgraph Commands["Command Handlers"]
        direction TB
        C1[/daily - Send Daily]
        C2[/trending - Send Trending]
        C3[/opensource - OS Projects]
        C4[/research - Research Papers]
        C5[/subscribe - Subscribe]
        C6[/unsubscribe - Unsubscribe]
    end
    
    Send --> Commands
    
    subgraph User_Interaction["User Interactions"]
        direction TB
        U1[User Sends Command]
        U2[Parse Command]
        U3[Execute Handler]
        U4[Send Response]
    end
    
    Commands --> User_Interaction
    
    User_Interaction --> END([END])
    
    %% Error Handling
    Send -->|Failed| RETRY[Retry 3x]
    RETRY -->|Success| Track_Delivery[Track Delivery]
    RETRY -->|Failed| LOG_ERROR[Log Error]
    LOG_ERROR --> ALERT[Alert Admin]
```

---

## 9. Error Handling + Fallback Workflow

```mermaid
flowchart TB
    START([Any Node Execution]) --> EXECUTE[Execute Node]
    
    EXECUTE --> SUCCESS{Success?}
    
    %% Success Path
    SUCCESS -->|Yes| NEXT[Continue to Next Node]
    
    %% Error Path
    SUCCESS -->|No| CHECK_ERROR{Error Type?}
    
    subgraph Retry_Logic["Retry Logic"]
        direction TB
        R1[Retry Attempt 1]
        R2[Retry Attempt 2]
        R3[Retry Attempt 3]
    end
    
    CHECK_ERROR -->|Timeout| Retry_Logic
    CHECK_ERROR -->|Rate Limit| FALLBACK_LLM[Fallback LLM]
    CHECK_ERROR -->|Network| Retry_Logic
    CHECK_ERROR -->|Invalid Data| SKIP[Skip Item]
    
    Retry_Logic --> RETRY_SUCCESS{Retry Success?}
    RETRY_SUCCESS -->|Yes| NEXT
    RETRY_SUCCESS -->|No| FALLBACK_LLM
    
    FALLBACK_LLM --> FALLBACK_SUCCESS{Fallback Success?}
    FALLBACK_SUCCESS -->|Yes| NEXT
    FALLBACK_SUCCESS -->|No| LOG_ERROR[Log Error]
    
    SKIP --> LOG_SKIP[Log Skipped Item]
    LOG_SKIP --> NEXT
    
    subgraph Circuit_Breaker["Circuit Breaker"]
        direction TB
        CB1[Track Failures]
        CB2[Threshold: 5 failures]
        CB3[Open Circuit]
        CB4[After 60s, Try Again]
    end
    
    LOG_ERROR --> Circuit_Breaker
    Circuit_Breaker --> NEXT
    
    NEXT --> END_NODE([Continue Workflow])
    
    %% Global Error Handler
    LOG_ERROR --> GLOBAL_LOG[Global Error Log]
    GLOBAL_LOG --> ALERT_ADMIN[Alert Admin]
    ALERT_ADMIN --> NOTIFY[Send Notification]
```

---

## 10. Deployment Architecture

```mermaid
flowchart TB
    subgraph Cloud_Provider["Cloud Infrastructure"]
        direction TB
        LB[Load Balancer]
        
        subgraph Docker_Container["Docker Container"]
            direction LR
            FastAPI[FastAPI App]
            LangGraph[LangGraph Runtime]
            Workers[Background Workers]
            Scheduler[Scheduler]
        end
        
        DB[(PostgreSQL)]
        VectorDB[(ChromaDB/FAISS)]
        Cache[(Redis Cache)]
    end
    
    subgraph External_Services["External Services"]
        direction LR
        Telegram[Telegram API]
        LLM_Services[LLM Providers]
        LangSmith[LangSmith]
    end
    
    subgraph Monitoring["Monitoring & Logging"]
        direction LR
        Logs[Log Aggregation]
        Metrics[Metrics Collector]
        Alerts[Alert Manager]
    end
    
    LB --> Docker_Container
    Docker_Container --> DB
    Docker_Container --> VectorDB
    Docker_Container --> Cache
    Docker_Container --> External_Services
    Docker_Container --> Monitoring
    
    subgraph Environment["Environment Variables"]
        direction TB
        ENV1[OPENAI_API_KEY]
        ENV2[GROQ_API_KEY]
        ENV3[TELEGRAM_BOT_TOKEN]
        ENV4[POSTGRES_URL]
        ENV5[LANGCHAIN_API_KEY]
    end
    
    ENV1 --> Docker_Container
    ENV2 --> Docker_Container
    ENV3 --> Docker_Container
    ENV4 --> Docker_Container
    ENV5 --> Docker_Container
```

---

## 11. State Graph Schema

```mermaid
classDiagram
    class NewsState {
        +List[Dict] raw_news
        +List[Dict] unique_news
        +List[Dict] ranked_news
        +List[str] summaries
        +str newsletter
        +List[str] errors
    }
    
    class CollectorResult {
        +str title
        +str url
        +str source
        +datetime timestamp
        +str content
    }
    
    class RankedItem {
        +Dict news
        +float score
        +str category
        +int rank
    }
    
    class Newsletter {
        +str date
        +str header
        +List[Section] sections
        +str footer
    }
    
    NewsState --> CollectorResult
    NewsState --> RankedItem
    NewsState --> Newsletter
```

---

## 12. Component Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant TelegramBot
    participant FastAPI
    participant LangGraph
    participant Collectors
    participant LLM
    participant Database
    participant VectorStore
    
    User->>TelegramBot: /daily command
    TelegramBot->>FastAPI: Forward command
    FastAPI->>LangGraph: Trigger workflow
    
    par Parallel Collection
        LangGraph->>Collectors: Collect from RSS
        LangGraph->>Collectors: Collect from HN
        LangGraph->>Collectors: Collect from GitHub
    end
    
    Collectors-->>LangGraph: Raw news data
    
    LangGraph->>VectorStore: Deduplicate
    VectorStore-->>LangGraph: Unique items
    
    LangGraph->>LLM: Rank news
    LLM-->>LangGraph: Ranked items
    
    LangGraph->>LLM: Summarize items
    LLM-->>LangGraph: Summaries
    
    LangGraph->>LLM: Generate newsletter
    LLM-->>LangGraph: Formatted newsletter
    
    LangGraph->>Database: Store results
    Database-->>LangGraph: Confirm storage
    
    LangGraph->>TelegramBot: Send newsletter
    TelegramBot->>User: Deliver message
    
    Note over LangGraph,LangSmith: All steps traced in LangSmith
```

---

## 13. Async Execution Flow

```mermaid
flowchart TB
    TRIGGER[Scheduled Trigger / Manual] --> QUEUE[Task Queue]
    
    subgraph Worker_Pool["Worker Pool"]
        direction LR
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]
    end
    
    QUEUE --> Worker_Pool
    
    subgraph Tasks["Async Tasks"]
        direction TB
        T1[Collect RSS]
        T2[Collect HN]
        T3[Collect GitHub]
        T4[LLM Processing]
        T5[Telegram Send]
    end
    
    Worker_Pool --> Tasks
    
    subgraph Sync["Synchronization"]
        direction LR
        S1[Lock Manager]
        S2[Result Aggregator]
        S3[State Manager]
    end
    
    Tasks --> Sync
    
    Sync --> COMPLETE[Task Complete]
    
    %% Parallel execution indicator
    T1 -.->|async| T2
    T2 -.->|async| T3
    T3 -.->|async| T4
```

---

## 14. System Component Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| Orchestration | LangGraph | Workflow management |
| API Server | FastAPI | REST endpoints |
| Database | PostgreSQL | Persistent storage |
| Vector Store | ChromaDB/FAISS | Semantic search |
| Observability | LangSmith | Tracing & monitoring |
| Messaging | Telegram Bot | User delivery |
| LLM Primary | Groq Llama | Fast processing |
| LLM Fallback | OpenRouter DeepSeek | Rate limit handling |
| LLM Formatting | Gemini Flash | Final polish |

---

## 15. Environment Configuration

```mermaid
flowchart LR
    subgraph Config["Configuration"]
        direction TB
        ENV[.env file]
        Pydantic[pydantic Settings]
        Secrets[Secrets Manager]
    end
    
    subgraph Validation["Validation"]
        direction LR
        V1[Type Check]
        V2[Required Fields]
        V3[Default Values]
    end
    
    subgraph Injection["Dependency Injection"]
        direction LR
        I1[FastAPI Depends]
        I2[LangGraph Context]
        I3[Service Classes]
    end
    
    ENV --> Pydantic
    Pydantic --> Validation
    Validation --> Injection
```

---

*Document Version: 1.0*
*Generated for: AI Intelligence Newsletter Agent*
*Architecture: Production-Ready Multi-Agent System*