"""AgentRouter Multi-Agent Orchestrator for AI Newsletter.

This module provides multi-agent orchestration using AgentRouter's
ManagerAgent and Worker agents for different newsletter tasks.

Agents:
- NewsletterManager: Orchestrates the entire newsletter workflow
- CollectorAgent: Gathers news from various sources
- FilterAgent: Filters and deduplicates news items
- RankerAgent: Ranks news by importance
- SummarizerAgent: Summarizes news articles
- FormatterAgent: Formats the final newsletter
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Global manager instance
_manager: Optional[Any] = None


class NewsletterOrchestrator:
    """Multi-agent orchestrator using AgentRouter for newsletter generation."""

    def __init__(self):
        self.settings = get_settings()
        self.manager = None
        self.workers = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the AgentRouter manager and worker agents."""
        if self._initialized:
            logger.info("Orchestrator already initialized")
            return

        if not self.settings.agentrouter_api_key:
            logger.warning("AgentRouter API key not configured. Using fallback mode.")
            self._initialized = False
            return

        try:
            from agentrouter import ManagerAgent, tool

            # Create the manager agent
            self.manager = ManagerAgent(
                name="newsletter_manager",
                api_key=self.settings.agentrouter_api_key,
                model=self.settings.agentrouter_model,
                backstory="""You are a senior AI newsletter editor with 10+ years of experience.
You oversee the entire newsletter creation process, coordinating specialized agents
to collect, filter, rank, summarize, and format AI news into a professional daily newsletter.
You ensure quality, consistency, and timely delivery.""",
                goal="Coordinate a team of specialized agents to produce a high-quality AI newsletter.",
                instruction="""You coordinate the following worker agents:
1. collector - Gathers news from RSS, GitHub, Hacker News, Reddit, and other sources
2. filter - Removes duplicates and low-quality content
3. ranker - Ranks news by importance, relevance, and virality
4. summarizer - Creates concise, informative summaries of articles
5. formatter - Produces the final formatted newsletter

For each newsletter:
1. Ask collector to gather raw news
2. Ask filter to clean the news
3. Ask ranker to prioritize the news
4. Ask summarizer to create summaries
5. Ask formatter to create the final newsletter

Always verify the quality before proceeding to the next step.""",
                temperature=0.7,
                max_iterations=50,
            )

            # Create worker agents
            self.workers["collector"] = self.manager.create_worker(
                name="CollectorAgent",
                role="News Collection Specialist - Gathers AI news from RSS feeds, GitHub trending, Hacker News, Reddit, and other sources.",
            )

            self.workers["filter"] = self.manager.create_worker(
                name="FilterAgent",
                role="Content Filtering Specialist - Removes duplicates and filters low-quality content.",
            )

            self.workers["ranker"] = self.manager.create_worker(
                name="RankerAgent",
                role="News Ranking Specialist - Ranks news by importance, relevance, virality, and impact.",
            )

            self.workers["summarizer"] = self.manager.create_worker(
                name="SummarizerAgent",
                role="Content Summarization Specialist - Creates concise summaries of AI news articles.",
            )

            self.workers["formatter"] = self.manager.create_worker(
                name="FormatterAgent",
                role="Newsletter Formatting Specialist - Formats the final newsletter with proper structure.",
            )

            self._initialized = True
            logger.info("AgentRouter orchestrator initialized successfully")

        except ImportError:
            logger.error(
                "AgentRouter package not installed. Run: pip install agentrouter"
            )
            self._initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize AgentRouter: {e}")
            self._initialized = False

    async def run_workflow(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run the newsletter workflow using AgentRouter agents.

        Args:
            news_items: List of raw news items to process

        Returns:
            Dictionary with processed news, summaries, and formatted newsletter
        """
        if not self._initialized or not self.manager:
            logger.warning("AgentRouter not initialized. Using fallback workflow.")
            return await self._fallback_workflow(news_items)

        try:
            # Step 1: Filter news
            logger.info("Running filter agent...")
            filter_result = await self._run_worker(
                "filter",
                f"Filter and deduplicate these news items. Remove duplicates and low-quality content.\n\nNews items:\n{self._format_news_items(news_items)}",
            )

            # Step 2: Rank news
            logger.info("Running ranker agent...")
            ranked_items = await self._run_worker(
                "ranker",
                f"Rank these news items by importance, relevance, and impact. Prioritize breaking news.\n\n{filter_result}",
            )

            # Step 3: Summarize news
            logger.info("Running summarizer agent...")
            summaries = await self._run_worker(
                "summarizer",
                f"Create concise summaries for each news item. Focus on key insights and why it matters.\n\n{ranked_items}",
            )

            # Step 4: Format newsletter
            logger.info("Running formatter agent...")
            newsletter = await self._run_worker(
                "formatter",
                f"Format the final newsletter with proper structure and sections.\n\nSummaries:\n{summaries}",
            )

            return {
                "ranked_items": ranked_items,
                "summaries": summaries,
                "newsletter": newsletter,
                "agent_used": True,
            }

        except Exception as e:
            logger.error(f"AgentRouter workflow failed: {e}. Using fallback.")
            return await self._fallback_workflow(news_items)

    async def _run_worker(self, worker_name: str, task: str) -> str:
        """Run a specific worker agent with a task.

        Args:
            worker_name: Name of the worker agent
            task: Task description

        Returns:
            Agent's response
        """
        if worker_name not in self.workers:
            raise ValueError(f"Unknown worker: {worker_name}")

        worker = self.workers[worker_name]
        messages = [{"role": "user", "content": task}]

        response = await worker.execute(messages)

        if hasattr(response, "choices"):
            return response["choices"][0]["message"]["content"]
        return str(response)

    async def _fallback_workflow(
        self, news_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fallback workflow when AgentRouter is not available.

        Args:
            news_items: List of raw news items

        Returns:
            Processed results
        """
        logger.info("Using fallback workflow (no AgentRouter)")

        # Return items as-is for processing by LangGraph
        return {
            "ranked_items": news_items,
            "summaries": [],
            "newsletter": "",
            "agent_used": False,
        }

    def _format_news_items(self, items: List[Dict[str, Any]]) -> str:
        """Format news items for agent consumption.

        Args:
            items: List of news items

        Returns:
            Formatted string
        """
        formatted = []
        for i, item in enumerate(items, 1):
            title = item.get("title", "Untitled")
            source = item.get("source", "unknown")
            url = item.get("url", "")
            formatted.append(f"{i}. {title} ({source}) - {url}")
        return "\n".join(formatted)


def get_orchestrator() -> NewsletterOrchestrator:
    """Get or create the global orchestrator instance.

    Returns:
        NewsletterOrchestrator instance
    """
    global _manager
    if _manager is None:
        _manager = NewsletterOrchestrator()
    return _manager


async def initialize_orchestrator() -> None:
    """Initialize the orchestrator."""
    orchestrator = get_orchestrator()
    await orchestrator.initialize()
