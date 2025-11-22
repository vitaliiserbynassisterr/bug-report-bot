"""Handler for viewing detailed bug information."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.auth import check_authorization
from services.backend_client import backend_client, BackendAPIError
from services.bug_formatter import format_bug_details

logger = logging.getLogger(__name__)


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /view command - show detailed bug information.

    Usage: /view BUG-001

    Args:
        update: Telegram update object
        context: Callback context
    """
    # Check authorization
    if not await check_authorization(update):
        return

    user_id = update.effective_user.id

    # Parse command arguments
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ **Invalid usage**\n\n"
            "**Usage:** `/view BUG-001`\n\n"
            "**Example:**\n"
            "`/view BUG-001`",
            parse_mode="Markdown"
        )
        return

    bug_id = context.args[0].upper()

    # Send loading message
    loading_message = await update.message.reply_text(
        f"⏳ Fetching bug {bug_id}..."
    )

    try:
        # Fetch bug details from backend
        bug = await backend_client.get_bug(bug_id)

        # Format and send bug details
        bug_details = format_bug_details(bug)

        await loading_message.edit_text(bug_details, parse_mode="Markdown")

        logger.info(f"User {user_id} viewed bug {bug_id}")

    except BackendAPIError as e:
        logger.error(f"Failed to fetch bug {bug_id}: {e}")

        # Check if it's a 404 (bug not found)
        if "404" in str(e) or "not found" in str(e).lower():
            await loading_message.edit_text(
                f"❌ **Bug not found**\n\n"
                f"Bug `{bug_id}` doesn't exist.\n"
                f"Use /mybugs to see your bugs.",
                parse_mode="Markdown"
            )
        else:
            await loading_message.edit_text(
                f"❌ **Failed to fetch bug**\n\n"
                f"Error: {str(e)}\n\n"
                f"Please try again later.",
                parse_mode="Markdown"
            )
