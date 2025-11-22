"""Handler for the /mybugs command."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.auth import check_authorization
from services.backend_client import backend_client, BackendAPIError
from services.bug_formatter import format_bug_list

logger = logging.getLogger(__name__)


async def my_bugs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /mybugs command - show user's bug reports.

    Args:
        update: Telegram update object
        context: Callback context
    """
    # Check authorization
    if not await check_authorization(update):
        return

    user_id = update.effective_user.id

    # Send "loading" message
    loading_message = await update.message.reply_text("⏳ Fetching your bug reports...")

    try:
        # Fetch bugs from backend
        bugs = await backend_client.get_user_bugs(user_id, limit=10)

        # Format and send bug list
        bug_list_message = format_bug_list(bugs)

        await loading_message.edit_text(bug_list_message, parse_mode="Markdown")

        logger.info(
            f"User {user_id} fetched their bugs - found {len(bugs)} bug(s)"
        )

    except BackendAPIError as e:
        logger.error(f"Failed to fetch bugs for user {user_id}: {e}")

        await loading_message.edit_text(
            "❌ **Failed to fetch bug reports**\n\n"
            f"Error: {str(e)}\n\n"
            "Please try again later or contact support.",
            parse_mode="Markdown",
        )
