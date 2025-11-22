"""Unit tests for bot handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes

from handlers.start import start_command, help_command
from handlers.my_bugs import my_bugs_command
from handlers.stats import stats_command
from utils.auth import check_authorization, get_user_display_name


@pytest.fixture
def mock_update():
    """Create a mock Update object."""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create a mock context object."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context


class TestAuthentication:
    """Tests for authentication utilities."""

    @patch("utils.auth.settings")
    @pytest.mark.asyncio
    async def test_check_authorization_authorized_user(self, mock_settings, mock_update):
        """Test that authorized users pass the check."""
        mock_settings.ALLOWED_USER_IDS = [123456789]

        result = await check_authorization(mock_update)

        assert result is True

    @patch("utils.auth.settings")
    @pytest.mark.asyncio
    async def test_check_authorization_unauthorized_user(self, mock_settings, mock_update):
        """Test that unauthorized users are rejected."""
        mock_settings.ALLOWED_USER_IDS = [987654321]  # Different user ID

        result = await check_authorization(mock_update)

        assert result is False
        mock_update.message.reply_text.assert_called_once()
        assert "not authorized" in mock_update.message.reply_text.call_args[0][0]

    def test_get_user_display_name_with_first_name(self, mock_update):
        """Test display name extraction with first name."""
        mock_update.effective_user.first_name = "John"

        name = get_user_display_name(mock_update)

        assert name == "John"

    def test_get_user_display_name_with_username(self, mock_update):
        """Test display name extraction with username only."""
        mock_update.effective_user.first_name = None
        mock_update.effective_user.username = "johndoe"

        name = get_user_display_name(mock_update)

        assert name == "@johndoe"

    def test_get_user_display_name_fallback(self, mock_update):
        """Test display name fallback when no name is available."""
        mock_update.effective_user.first_name = None
        mock_update.effective_user.username = None

        name = get_user_display_name(mock_update)

        assert name == "User"


class TestStartCommand:
    """Tests for /start command handler."""

    @patch("handlers.start.check_authorization")
    @pytest.mark.asyncio
    async def test_start_command_authorized(
        self, mock_check_auth, mock_update, mock_context
    ):
        """Test /start command for authorized user."""
        mock_check_auth.return_value = True

        await start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Welcome" in call_args[0][0]
        assert call_args[1]["parse_mode"] == "Markdown"

    @patch("handlers.start.check_authorization")
    @pytest.mark.asyncio
    async def test_start_command_unauthorized(
        self, mock_check_auth, mock_update, mock_context
    ):
        """Test /start command for unauthorized user."""
        mock_check_auth.return_value = False

        await start_command(mock_update, mock_context)

        # Should not send welcome message
        mock_update.message.reply_text.assert_not_called()


class TestHelpCommand:
    """Tests for /help command handler."""

    @patch("handlers.start.check_authorization")
    @pytest.mark.asyncio
    async def test_help_command_authorized(
        self, mock_check_auth, mock_update, mock_context
    ):
        """Test /help command for authorized user."""
        mock_check_auth.return_value = True

        await help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Help" in call_args[0][0]
        assert call_args[1]["parse_mode"] == "Markdown"


class TestMyBugsCommand:
    """Tests for /mybugs command handler."""

    @patch("handlers.my_bugs.check_authorization")
    @patch("handlers.my_bugs.backend_client")
    @pytest.mark.asyncio
    async def test_mybugs_command_with_bugs(
        self, mock_backend_client, mock_check_auth, mock_update, mock_context
    ):
        """Test /mybugs command when user has bugs."""
        mock_check_auth.return_value = True
        mock_backend_client.get_user_bugs = AsyncMock(
            return_value=[
                {
                    "id": "BUG-001",
                    "title": "Test bug",
                    "status": "OPEN",
                    "priority": "HIGH",
                    "environment": "PROD",
                    "created_at": "2025-11-22T10:00:00Z",
                }
            ]
        )

        await my_bugs_command(mock_update, mock_context)

        # Should show loading message first, then edit with results
        assert mock_update.message.reply_text.call_count == 1
        mock_backend_client.get_user_bugs.assert_called_once_with(123456789, limit=10)

    @patch("handlers.my_bugs.check_authorization")
    @patch("handlers.my_bugs.backend_client")
    @pytest.mark.asyncio
    async def test_mybugs_command_api_error(
        self, mock_backend_client, mock_check_auth, mock_update, mock_context
    ):
        """Test /mybugs command when API fails."""
        from services.backend_client import BackendAPIError

        mock_check_auth.return_value = True
        mock_backend_client.get_user_bugs = AsyncMock(
            side_effect=BackendAPIError("API Error")
        )

        await my_bugs_command(mock_update, mock_context)

        # Should show error message
        mock_update.message.reply_text.assert_called_once()


class TestStatsCommand:
    """Tests for /stats command handler."""

    @patch("handlers.stats.check_authorization")
    @patch("handlers.stats.backend_client")
    @pytest.mark.asyncio
    async def test_stats_command_success(
        self, mock_backend_client, mock_check_auth, mock_update, mock_context
    ):
        """Test /stats command with successful API call."""
        mock_check_auth.return_value = True
        mock_backend_client.get_bug_stats = AsyncMock(
            return_value={
                "total": 100,
                "by_status": {"OPEN": 50, "FIXED": 50},
                "by_priority": {"LOW": 25, "MEDIUM": 50, "HIGH": 25},
            }
        )

        await stats_command(mock_update, mock_context)

        mock_backend_client.get_bug_stats.assert_called_once()
        mock_update.message.reply_text.assert_called_once()

    @patch("handlers.stats.check_authorization")
    @pytest.mark.asyncio
    async def test_stats_command_unauthorized(
        self, mock_check_auth, mock_update, mock_context
    ):
        """Test /stats command for unauthorized user."""
        mock_check_auth.return_value = False

        await stats_command(mock_update, mock_context)

        # Should not proceed
        mock_update.message.reply_text.assert_not_called()
