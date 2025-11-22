"""Handler for the /stats command."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.auth import check_authorization
from services.backend_client import backend_client, BackendAPIError
from services.bug_formatter import format_stats

logger = logging.getLogger(__name__)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /stats command - show overall bug statistics.

    Args:
        update: Telegram update object
        context: Callback context
    """
    # Check authorization
    if not await check_authorization(update):
        return

    user_id = update.effective_user.id

    # Send "loading" message
    loading_message = await update.message.reply_text("⏳ Fetching statistics...")

    try:
        # Fetch statistics from backend
        stats = await backend_client.get_bug_stats()

        # Format and send statistics
        stats_message = format_stats(stats)

        await loading_message.edit_text(stats_message, parse_mode="Markdown")

        logger.info(f"User {user_id} fetched bug statistics")

    except BackendAPIError as e:
        logger.error(f"Failed to fetch statistics for user {user_id}: {e}")

        await loading_message.edit_text(
            "❌ **Failed to fetch statistics**\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again later or contact support.",
            parse_mode="Markdown",
        )
