"""Backend API client for interacting with the bug tracking API."""

import logging
from typing import Dict, List, Optional, Any
import asyncio

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class BackendAPIError(Exception):
    """Custom exception for backend API errors."""

    pass


class BackendClient:
    """Client for interacting with the backend bug tracking API."""

    def __init__(self):
        """Initialize the backend client."""
        self.base_url = settings.BACKEND_API_URL.rstrip("/")
        self.headers = {
            "X-Internal-Token": settings.BACKEND_INTERNAL_TOKEN,
            "Content-Type": "application/json",
        }
        self.timeout = httpx.Timeout(settings.REQUEST_TIMEOUT)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the backend API with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            BackendAPIError: If the request fails after all retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(settings.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=self.headers,
                        json=data,
                        params=params,
                    )

                    # Log request details
                    logger.info(
                        f"{method} {url} - Status: {response.status_code}"
                    )

                    # Raise for HTTP errors
                    response.raise_for_status()

                    return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error on attempt {attempt + 1}/{settings.MAX_RETRIES}: "
                    f"{e.response.status_code} - {e.response.text}"
                )

                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise BackendAPIError(
                        f"Client error: {e.response.status_code} - {e.response.text}"
                    )

                # Retry on server errors (5xx)
                if attempt < settings.MAX_RETRIES - 1:
                    delay = settings.RETRY_DELAY * (settings.RETRY_BACKOFF ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise BackendAPIError(
                        f"Server error after {settings.MAX_RETRIES} attempts: "
                        f"{e.response.status_code}"
                    )

            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.error(
                    f"Request error on attempt {attempt + 1}/{settings.MAX_RETRIES}: {e}"
                )

                if attempt < settings.MAX_RETRIES - 1:
                    delay = settings.RETRY_DELAY * (settings.RETRY_BACKOFF ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise BackendAPIError(
                        f"Network error after {settings.MAX_RETRIES} attempts: {str(e)}"
                    )

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise BackendAPIError(f"Unexpected error: {str(e)}")

        raise BackendAPIError("Request failed after all retries")

    async def create_bug(self, bug_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new bug report.

        Args:
            bug_data: Bug report data including:
                - title: Bug description
                - environment: DEV or PROD
                - priority: LOW, MEDIUM, HIGH, CRITICAL
                - screenshots: List of screenshot metadata
                - console_logs: Optional console logs
                - tags: Optional list of tags
                - reporter: Reporter information (telegram_id, username, etc.)

        Returns:
            Created bug data with ID

        Raises:
            BackendAPIError: If the request fails
        """
        logger.info(f"Creating bug: {bug_data.get('title', 'N/A')}")
        return await self._make_request("POST", "/bugs/", data=bug_data)

    async def get_user_bugs(
        self, telegram_user_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get bugs reported by a specific Telegram user.

        Args:
            telegram_user_id: Telegram user ID
            limit: Maximum number of bugs to return

        Returns:
            List of bug reports

        Raises:
            BackendAPIError: If the request fails
        """
        logger.info(f"Fetching bugs for user {telegram_user_id}")
        params = {
            "reporter.telegram_id": telegram_user_id,
            "limit": limit,
            "sort": "-created_at",  # Most recent first
        }
        response = await self._make_request("GET", "/bugs/", params=params)

        # Handle different possible response formats
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "data" in response:
            return response["data"]
        elif isinstance(response, dict) and "bugs" in response:
            return response["bugs"]
        else:
            logger.warning(f"Unexpected response format: {response}")
            return []

    async def get_bug_stats(self) -> Dict[str, Any]:
        """
        Get overall bug statistics.

        Returns:
            Statistics data including counts by status, priority, etc.

        Raises:
            BackendAPIError: If the request fails
        """
        logger.info("Fetching bug statistics")
        return await self._make_request("GET", "/bugs/stats")

    async def update_bug_status(
        self, bug_id: str, status: str, assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update bug status and optionally assign it.

        Args:
            bug_id: Bug identifier (e.g., BUG-001)
            status: New status (OPEN, IN_PROGRESS, FIXED, CLOSED)
            assignee: Optional assignee name

        Returns:
            Updated bug data

        Raises:
            BackendAPIError: If the request fails
        """
        logger.info(f"Updating bug {bug_id} to status {status}")

        update_data = {"status": status}
        if assignee:
            update_data["assignee"] = assignee

        return await self._make_request("PATCH", f"/bugs/{bug_id}", data=update_data)


# Global client instance
backend_client = BackendClient()
