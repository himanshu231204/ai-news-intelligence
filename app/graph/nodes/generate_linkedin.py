"""
Generate LinkedIn Newsletter Node

Generates long-form LinkedIn newsletter for scheduled runs only.
Does NOT run for on-demand Telegram bot commands.
"""

from app.graph.state import NewsState
from app.newsletter.linkedin_generator import build_linkedin_newsletter
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def generate_linkedin_node(state: NewsState) -> NewsState:
    """Generate LinkedIn newsletter for scheduled runs.

    This node only runs when IS_SCHEDULED_RUN=true.
    It generates a long-form professional newsletter for LinkedIn publishing.

    Args:
        state: Current workflow state

    Returns:
        Updated state with linkedin_newsletter
    """
    logger.info("Starting LinkedIn newsletter generation")

    ranked_news = state.ranked_news
    summaries = state.summaries

    if not ranked_news or not summaries:
        logger.warning("No ranked news or summaries available for LinkedIn newsletter")
        state.linkedin_newsletter = "⚠️ No content available for LinkedIn newsletter."
        state.linkedin_saved = False
        return state

    try:
        # Generate LinkedIn newsletter
        linkedin_content = await build_linkedin_newsletter(
            items=ranked_news,
            summaries=summaries,
        )

        state.linkedin_newsletter = linkedin_content
        logger.info(f"LinkedIn newsletter generated: {len(linkedin_content)} chars")

    except Exception as e:
        logger.error(f"Failed to generate LinkedIn newsletter: {e}")
        state.linkedin_newsletter = f"⚠️ LinkedIn newsletter generation failed: {str(e)}"
        state.linkedin_saved = False

    return state
