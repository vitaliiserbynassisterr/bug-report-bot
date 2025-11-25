"""Configuration settings for the Telegram bug reporting bot."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Backend API
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "")
    BACKEND_INTERNAL_TOKEN: str = os.getenv("BACKEND_INTERNAL_TOKEN", "")

    # Authorization
    ALLOWED_USER_IDS: List[int] = []

    # Claude AI Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    AI_AGENT_ENABLED: bool = os.getenv("AI_AGENT_ENABLED", "false").lower() == "true"
    AI_COMPLEXITY_THRESHOLD: str = os.getenv("AI_COMPLEXITY_THRESHOLD", "SIMPLE")

    # GitHub Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO_OWNER: str = os.getenv("GITHUB_REPO_OWNER", "vitaliiserbynassisterr")
    GITHUB_REPO_NAME: str = os.getenv("GITHUB_REPO_NAME", "bug-report-bot")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # API Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # seconds
    RETRY_BACKOFF: float = 2.0  # exponential backoff multiplier

    # Request Timeout
    REQUEST_TIMEOUT: int = 30  # seconds

    def __init__(self):
        """Initialize settings and parse allowed user IDs."""
        self._parse_allowed_users()
        self._validate_settings()

    def _parse_allowed_users(self) -> None:
        """Parse comma-separated allowed user IDs from environment."""
        allowed_ids_str = os.getenv("ALLOWED_USER_IDS", "")
        if allowed_ids_str:
            try:
                self.ALLOWED_USER_IDS = [
                    int(user_id.strip())
                    for user_id in allowed_ids_str.split(",")
                    if user_id.strip()
                ]
            except ValueError as e:
                raise ValueError(f"Invalid ALLOWED_USER_IDS format: {e}")

    def _validate_settings(self) -> None:
        """Validate required settings are present."""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

        if not self.BACKEND_API_URL:
            raise ValueError("BACKEND_API_URL is required")

        if not self.BACKEND_INTERNAL_TOKEN:
            raise ValueError("BACKEND_INTERNAL_TOKEN is required")

        if not self.ALLOWED_USER_IDS:
            raise ValueError("ALLOWED_USER_IDS is required and must contain at least one user ID")


# Global settings instance
settings = Settings()
