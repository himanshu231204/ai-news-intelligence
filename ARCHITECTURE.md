# Architecture

## Flow

```mermaid
flowchart TD
    A[collect_news] --> B[merge_results]
    B --> C[deduplicate_news]
    C --> D[filter_low_quality]
    D --> E[rank_news]
    E --> F[summarize_news]
    F --> G[generate_newsletter]
    G --> H[store_results]
    H --> I[send_telegram]
```

## Components

- Collectors: source adapters
- Ranking: deduplication + scoring
- Summarization: LLM output shaping
- Newsletter: final rendering
- Delivery: Telegram transport
