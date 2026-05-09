"""
Google Drive Integration

Production-ready Google Drive and Google Docs API client.
Uses service account authentication for secure, scalable access.

Features:
- Create Google Docs
- Update existing docs
- List documents in folder
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
            # Parse JSON string from environment
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
        """Generate date-based filename.

        Returns:
            Filename in format: AI_Intelligence_Brief_YYYY_MM_DD.md
        """
        today = datetime.now()
        return f"AI_Intelligence_Brief_{today.strftime('%Y_%m_%d')}.md"

    def get_existing_doc(self, filename: str) -> Optional[Dict]:
        """Check if document already exists in the folder.

        Args:
            filename: Name of the document to find

        Returns:
            Document dict if found, None otherwise
        """
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

    def create_document(
        self,
        content: str,
        title: str,
    ) -> Optional[str]:
        """Create a new Google Doc in the specified folder.

        Args:
            content: Document content (markdown/text)
            title: Document title

        Returns:
            Document URL if successful, None otherwise
        """
        try:
            # Create file metadata
            file_metadata = {
                "name": title,
                "mimeType": "application/vnd.google-apps.document",
                "parents": [self.folder_id],
            }

            # Convert content to Google Docs format
            # For simplicity, we'll create a simple text document
            # In production, you might want to use the Docs API to create
            # formatted documents with proper headings, etc.

            # Create the document
            doc = (
                self.drive_service.files()
                .create(
                    body=file_metadata,
                    fields="id, webViewLink",
                )
                .execute()
            )

            doc_id = doc.get("id")
            logger.info(f"Created Google Doc: {title} (ID: {doc_id})")

            # Update content using Docs API
            if content:
                self._update_document_content(doc_id, content)

            web_link = doc.get("webViewLink")
            logger.info(f"Document URL: {web_link}")
            return web_link

        except HttpError as e:
            logger.error(f"Error creating Google Doc: {e}")
            return None

    def _update_document_content(self, doc_id: str, content: str):
        """Update document content using Google Docs API.

        Args:
            doc_id: Document ID
            content: New content
        """
        try:
            # Convert plain text to document format
            # This creates a simple document with the content
            requests = [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content,
                    }
                }
            ]

            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": requests},
            ).execute()

            logger.info(f"Updated document content for: {doc_id}")

        except HttpError as e:
            logger.error(f"Error updating document content: {e}")
            # Content was created, just log the error

    def update_document(self, doc_id: str, content: str) -> bool:
        """Update an existing Google Doc's content.

        Args:
            doc_id: Document ID to update
            content: New content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear existing content and insert new content
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
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content,
                    }
                },
            ]

            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": requests},
            ).execute()

            logger.info(f"Updated existing document: {doc_id}")
            return True

        except HttpError as e:
            logger.error(f"Error updating document: {e}")
            return False

    def save_newsletter(self, content: str) -> Optional[str]:
        """Save newsletter to Google Drive, creating or updating.

        Args:
            content: Newsletter content

        Returns:
            Document URL if successful, None otherwise
        """
        filename = self.generate_filename()

        # Check if document already exists
        existing = self.get_existing_doc(filename)

        if existing:
            # Update existing document
            doc_id = existing["id"]
            success = self.update_document(doc_id, content)
            if success:
                # Get the web view link
                doc = (
                    self.drive_service.files()
                    .get(fileId=doc_id, fields="webViewLink")
                    .execute()
                )
                logger.info(f"Updated existing newsletter: {filename}")
                return doc.get("webViewLink")
            return None
        else:
            # Create new document
            url = self.create_document(content, filename)
            if url:
                logger.info(f"Created new newsletter: {filename}")
            return url


def get_google_drive_client() -> Optional[GoogleDriveClient]:
    """Get or create Google Drive client based on settings.

    Returns:
        GoogleDriveClient instance if enabled, None otherwise
    """
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
