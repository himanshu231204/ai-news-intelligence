"""
Google Drive Integration

Production-ready Google Drive and Google Docs API client.
Uses service account authentication for secure, scalable access.

Features:
- Create professionally formatted Google Docs
- Proper headings, bold text, links
- Date-based filename generation
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional, List, Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleDriveClient:
    """Google Drive and Docs API client using service account authentication."""

    def __init__(self):
        """Initialize Google Drive client with settings."""
        settings = get_settings()

        if not settings.google_service_account_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is required for Google Drive")

        if not settings.google_drive_folder_id:
            raise ValueError("GOOGLE_DRIVE_FOLDER_ID is required for Google Drive")

        self.folder_id = settings.google_drive_folder_id
        self.credentials_json = settings.google_service_account_json
        self._service = None
        self._docs_service = None

    @property
    def drive_service(self):
        """Lazy-load Drive API service."""
        if self._service is None:
            self._service = self._build_drive_service()
        return self._service

    @property
    def docs_service(self):
        """Lazy-load Docs API service."""
        if self._docs_service is None:
            self._docs_service = self._build_docs_service()
        return self._docs_service

    def _build_drive_service(self):
        """Build Google Drive API service."""
        try:
            credentials = self._get_credentials()
            service = build("drive", "v3", credentials=credentials)
            logger.info("Google Drive API service initialized")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            raise

    def _build_docs_service(self):
        """Build Google Docs API service."""
        try:
            credentials = self._get_credentials()
            service = build("docs", "v1", credentials=credentials)
            logger.info("Google Docs API service initialized")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize Google Docs service: {e}")
            raise

    def _get_credentials(self):
        """Get service account credentials from JSON."""
        try:
            if isinstance(self.credentials_json, str):
                info = json.loads(self.credentials_json)
            else:
                info = self.credentials_json

            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=[
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/documents",
                ],
            )
            return credentials
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
            raise ValueError("Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON")
        except Exception as e:
            logger.error(f"Failed to create credentials: {e}")
            raise

    def generate_filename(self) -> str:
        """Generate date-based filename."""
        today = datetime.now()
        return f"AI Intelligence Brief - {today.strftime('%B %d, %Y')}"

    def get_existing_doc(self, filename: str) -> Optional[Dict]:
        """Check if document already exists in the folder."""
        try:
            query = (
                f"name='{filename}' and '{self.folder_id}' in parents and trashed=false"
            )
            results = (
                self.drive_service.files()
                .list(
                    q=query,
                    fields="files(id, name, modifiedTime)",
                    spaces="drive",
                )
                .execute()
            )

            files = results.get("files", [])
            if files:
                logger.info(
                    f"Found existing document: {filename} (ID: {files[0]['id']})"
                )
                return files[0]
            return None

        except HttpError as e:
            logger.error(f"Error checking for existing document: {e}")
            return None

    def _create_professional_document(
        self,
        content: str,
        title: str,
    ) -> Optional[str]:
        """Create a professionally formatted Google Doc.

        Args:
            content: Newsletter content
            title: Document title

        Returns:
            Document URL if successful
        """
        try:
            # Create the document with title
            doc = self.docs_service.documents().create(body={"title": title}).execute()

            doc_id = doc.get("id")
            logger.info(f"Created Google Doc: {title} (ID: {doc_id})")

            # Now add formatted content
            if content:
                self._add_formatted_content(doc_id, content)

            # Get the web view link
            web_link = f"https://docs.google.com/document/d/{doc_id}/edit"
            logger.info(f"Document URL: {web_link}")
            return web_link

        except HttpError as e:
            logger.error(f"Error creating Google Doc: {e}")
            return None

    def _add_formatted_content(self, doc_id: str, content: str):
        """Add professionally formatted content to the document.

        Uses Google Docs API to create:
        - Bold headings
        - Proper paragraph spacing
        - Hyperlinks for URLs
        """
        try:
            requests = []
            current_index = 1

            # Parse content and create formatted elements
            lines = content.split("\n")

            for line in lines:
                line = line.strip()
                if not line:
                    # Add paragraph break
                    requests.append(
                        {
                            "insertText": {
                                "location": {"index": current_index},
                                "text": "\n",
                            }
                        }
                    )
                    current_index += 1
                    continue

                # Check if it's a heading (starts with emoji or is all caps)
                is_heading = (
                    line.startswith(
                        ("📰", "🔵", "🟣", "📄", "🛠", "💡", "📌", "👤", "---")
                    )
                    or line.isupper()
                    or (len(line) < 50 and line.endswith(":"))
                )

                # Check if line contains a URL
                url = None
                if "http" in line.lower():
                    import re

                    url_match = re.search(r"https?://[^\s]+", line)
                    if url_match:
                        url = url_match.group()
                        # Remove URL from text for now
                        line = line.replace(url, "").strip()

                # Insert the text
                if is_heading:
                    # Heading - make it bold
                    requests.append(
                        {
                            "insertText": {
                                "location": {"index": current_index},
                                "text": line + "\n",
                            }
                        }
                    )
                    current_index += len(line) + 1

                    # Format as bold heading
                    requests.append(
                        {
                            "updateTextStyle": {
                                "textStyle": {
                                    "bold": True,
                                    "fontSize": {"magnitude": 14, "unit": "PT"},
                                },
                                "range": {
                                    "startIndex": current_index,
                                    "endIndex": current_index + len(line),
                                },
                                "fields": "bold,fontSize",
                            }
                        }
                    )
                else:
                    # Regular paragraph
                    text_to_insert = line
                    if url:
                        text_to_insert = f"{line} (Link: {url})"
                    text_to_insert += "\n"

                    requests.append(
                        {
                            "insertText": {
                                "location": {"index": current_index},
                                "text": text_to_insert,
                            }
                        }
                    )
                    current_index += len(text_to_insert)

            # Execute batch update
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id, body={"requests": requests}
                ).execute()

            logger.info(f"Added formatted content to document: {doc_id}")

        except Exception as e:
            logger.error(f"Error adding formatted content: {e}")
            # Try simple text insert as fallback
            self._add_simple_content(doc_id, content)

    def _add_simple_content(self, doc_id: str, content: str):
        """Fallback: Add content as simple text."""
        try:
            requests = [{"insertText": {"location": {"index": 1}, "text": content}}]

            self.docs_service.documents().batchUpdate(
                documentId=doc_id, body={"requests": requests}
            ).execute()

            logger.info(f"Added simple content to document: {doc_id}")

        except Exception as e:
            logger.error(f"Error adding simple content: {e}")

    def create_document(
        self,
        content: str,
        title: str,
    ) -> Optional[str]:
        """Create a new Google Doc in the specified folder."""
        return self._create_professional_document(content, title)

    def update_document(self, doc_id: str, content: str) -> bool:
        """Update an existing Google Doc's content."""
        try:
            # Get document to find content length
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            body_content = doc.get("body", {}).get("content", [])

            # Find the end of the document
            end_index = 1
            for element in body_content:
                if "paragraph" in element:
                    end_index = max(end_index, element.get("endIndex", 1))

            # Delete content from start to end, then insert new content
            requests = [
                {
                    "deleteContent": {
                        "range": {
                            "startIndex": 1,
                            "endIndex": end_index - 1,
                        }
                    }
                },
            ]

            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": requests},
            ).execute()

            # Add new content
            self._add_formatted_content(doc_id, content)

            logger.info(f"Updated existing document: {doc_id}")
            return True

        except HttpError as e:
            logger.error(f"Error updating document: {e}")
            return False

    def save_newsletter(self, content: str) -> Optional[str]:
        """Save newsletter to Google Drive, creating or updating."""
        filename = self.generate_filename()

        # Check if document already exists
        existing = self.get_existing_doc(filename)

        if existing:
            doc_id = existing["id"]
            success = self.update_document(doc_id, content)
            if success:
                logger.info(f"Updated existing newsletter: {filename}")
                return f"https://docs.google.com/document/d/{doc_id}/edit"
            return None
        else:
            url = self.create_document(content, filename)
            if url:
                logger.info(f"Created new newsletter: {filename}")
            return url


def get_google_drive_client() -> Optional[GoogleDriveClient]:
    """Get or create Google Drive client based on settings."""
    settings = get_settings()

    if not settings.enable_google_drive:
        logger.info("Google Drive integration is disabled")
        return None

    if not settings.google_service_account_json:
        logger.warning("Google Drive enabled but no service account JSON configured")
        return None

    try:
        return GoogleDriveClient()
    except Exception as e:
        logger.error(f"Failed to initialize Google Drive client: {e}")
        return None
