# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

| Goal | Command | Notes |
|------|---------|-------|
| **Create virtual environment** | `python -m venv .venv` | Windows PowerShell example in README. |
| **Activate environment** | `.venv\Scripts\Activate.ps1` (PowerShell)  <br>`.venv\Scripts\activate` (cmd) | Activate before any other command. |
| **Install dependencies** | `pip install -r requirements.txt` | All third‑party packages are listed in `requirements.txt`. |
| **Run the application** | `python main.py` | Entry point is `main.py` at the repo root. |
| **Run the full test suite** | `pytest` | Uses `pytest` (>=8.3). |
| **Run a single test file** | `pytest tests/test_smoke.py` | Replace with the desired test path. |
| **Run a single test function** | `pytest tests/test_smoke.py::test_newsletter_generation_smoke` | Append `::function_name`. |
| **Lint / type‑check** | No dedicated linter is shipped. Use `ruff` or `mypy` manually if desired (not required for core workflow). |
| **Re‑run the workflow without rebuilding** | `python -m app.graph.builder` (or import `build_graph` in a REPL) | Useful for quick iteration while debugging. |
| **View environment variables** | `python -c "from dotenv import load_dotenv; load_dotenv(); import os, pprint; pprint.pprint(dict(os.environ))"` | `.env` is copied from `.env.example` during setup. |

## High‑Level Architecture & Structure

### 1. LangGraph‑driven Pipeline
The core of the system is a **LangGraph** state machine that processes news items step‑by‑step.
- **State Definition** – `app/graph/state.py` defines `NewsState`, a TypedDict holding collections for each processing stage (`raw_news`, `merged_news`, `unique_news`, `filtered_news`, `ranked_news`, `summaries`, `newsletter`, plus `errors` and generic `metadata`).
- **Workflow Construction** – `app/graph/workflow.py` builds a `StateGraph` wiring the nodes in the exact order of the data flow (collect → merge → deduplicate → filter → rank → summarize → generate newsletter → store → send).
- **Checkpoint Support** – `app/graph/builder.py` wraps the workflow with a `MemorySaver` checkpoint, enabling state persistence across runs.

### 2. Nodes (Processing Steps)
Each node lives in `app/graph/nodes/` and follows a simple contract: receive a `NewsState`, return an updated copy.
- **collect_news_node** (`collect_news.py`) – Asynchronously gathers raw articles from eight external collectors via `asyncio.gather`. Errors are captured in `state["errors"]`.
- **merge_results_node** – Copies `raw_news` to `merged_news` (placeholder for future normalization).
- **deduplicate_news_node** – Calls `app/ranking/deduplication.py` to drop duplicates by URL or title.
- **filter_low_quality_node**, **rank_news_node**, **summarize_news_node**, **generate_newsletter_node**, **store_results_node**, **send_telegram_node** – Implement subsequent transformations; they are imported in the workflow but their bodies are not needed for a high‑level overview.

### 3. Collectors (Data Sources)
All source adapters live under `app/collectors/`. Each provides a coroutine returning a list of `NewsItem` dicts:
- `github.py` – Trending GitHub repos.
- `hackernews.py` – Top Hacker News stories.
- `reddit.py` – Posts from configured subreddits.
- `rss.py` – Feedparser‑based RSS aggregation.
- `twitter.py` – Recent tweets (requires API credentials).
- `arxiv.py` – Recent arXiv pre‑prints.
- `devto.py` – Articles from dev.to.
- `producthunt.py` – Latest Product Hunt tools.

These are imported in `collect_news.py` and executed in parallel.

### 4. Ranking & Deduplication
- **Deduplication** (`app/ranking/deduplication.py`) removes items with identical `url` or `title`.
- **Scoring** (in `app/ranking/scorer.py`) assigns a `score` to each `NewsItem` based on configurable heuristics (not detailed here). The result is stored in `ranked_news`.

### 5. Summarization & Newsletter Generation
- Prompt templates live in `app/summarization/prompts.py`. They drive LLM calls that produce per‑item summaries (`summaries` list).
- `generate_newsletter_node` concatenates the headline, item summaries, and optional “why it matters” sections into a single markdown string stored in `newsletter`.

### 6. Persistence & Delivery
- **store_results_node** – Persists the generated newsletter (e.g., writes to a file or database) and optionally upserts vector embeddings via `app/memory/vectorstore.py` (currently a placeholder).
- **send_telegram_node** – Sends the final newsletter through the Telegram Bot API using the `python-telegram-bot` library.

### 7. Tests
Only a smoke test exists (`tests/test_smoke.py`) which verifies that `build_newsletter([], [])` contains the expected header. Additional tests can be added per node.

### 8. Entry Point
The repository’s entry point is `main.py` (not shown but referenced in the README). It typically:
1. Calls `build_graph()` from `app/graph/builder.py`.
2. Executes the compiled graph, optionally passing configuration from environment variables (`.env`).

## Important Repository Files

| File | Reason to Read |
|------|----------------|
| `README.md` | Quick‑start steps, environment setup, and how to run the app. |
| `ARCHITECTURE.md` | Visual flow diagram and component summary. |
| `app/graph/workflow.py` | Full ordering of nodes; essential for understanding data progression. |
| `app/graph/state.py` | Structure of shared state across nodes. |
| `app/graph/nodes/collect_news.py` | Shows async collector orchestration and error handling. |
| `app/ranking/deduplication.py` | Example of a pure‑function transformation. |
| `requirements.txt` | Lists all external dependencies needed for runtime and testing. |

## Development Tips Specific to This Repo

- **State immutability**: Nodes copy the incoming `state` (`dict(state)`) before mutating – keep this pattern when adding new nodes.
- **Async collectors**: When adding a new source, implement it as an async function returning `list[NewsItem]` and include it in the `asyncio.gather` call in `collect_news_node`.
- **Checkpointing**: The `MemorySaver` checkpoint persists between graph executions; avoid side‑effects that bypass the state dict.
- **Error aggregation**: Errors from collectors are appended to `state["errors"]`; downstream nodes may decide to abort or continue based on this list.
- **Vectorstore placeholder**: `app/memory/vectorstore.py` currently does nothing; replace with real FAISS/Chroma integration only after confirming embedding workflow.

---
*Future Claude instances should read this `CLAUDE.md` first to understand the repo’s command shortcuts, the LangGraph‑driven pipeline, and where to look for state definitions and node implementations.*