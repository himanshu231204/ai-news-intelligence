"""
Save LinkedIn Newsletter to Google Drive Node

Saves the generated LinkedIn newsletter to Google Drive.
Only runs if Google Drive integration is enabled.
"""

from app.graph.state import NewsState
from app.integrations.google_drive import get_google_drive_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def save_linkedin_node(state: NewsState) -> NewsState:
    """Save LinkedIn newsletter to Google Drive.

    This node:
    - Only runs if ENABLE_GOOGLE_DRIVE=true
    - Saves the LinkedIn newsletter as a Google Doc
    - Updates existing doc if found, creates new if not

    Args:
        state: Current workflow state

    Returns:
        Updated state with google_doc_link and linkedin_saved
    """
    logger.info("Starting Google Drive save for LinkedIn newsletter")

    # Check if there's content to save
    if not state.linkedin_newsletter:
        logger.warning("No LinkedIn newsletter content to save")
        state.google_doc_link = ""
        state.linkedin_saved = False
        return state

    # Check for error message
    if state.linkedin_newsletter.startswith("⚠️"):
        logger.warning("LinkedIn newsletter contains error, skipping save")
        state.google_doc_link = ""
        state.linkedin_saved = False
        return state

    try:
        # Get Google Drive client
        drive_client = get_google_drive_client()

        if drive_client is None:
            logger.info("Google Drive integration not enabled or not configured")
            state.google_doc_link = ""
            state.linkedin_saved = False
            return state

        # Save to Google Drive
        doc_url = drive_client.save_newsletter(state.linkedin_newsletter)

        if doc_url:
            state.google_doc_link = doc_url
            state.linkedin_saved = True
            logger.info(f"LinkedIn newsletter saved to Google Drive: {doc_url}")
        else:
            state.google_doc_link = ""
            state.linkedin_saved = False
            logger.error("Failed to save LinkedIn newsletter to Google Drive")

    except Exception as e:
        logger.error(f"Error saving LinkedIn newsletter to Google Drive: {e}")
        state.google_doc_link = ""
        state.linkedin_saved = False

    return state
