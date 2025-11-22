"""Handler for updating bug status."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.auth import check_authorization
from services.backend_client import backend_client, BackendAPIError

logger = logging.getLogger(__name__)

# Valid status values
VALID_STATUSES = ["OPEN", "IN_PROGRESS", "FIXED", "CLOSED"]


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /status command - update bug status.

    Usage: /status BUG-001 FIXED

    Args:
        update: Telegram update object
        context: Callback context
    """
    # Check authorization
    if not await check_authorization(update):
        return

    user_id = update.effective_user.id

    # Parse command arguments
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Invalid usage**\n\n"
            "**Usage:** `/status BUG-001 FIXED`\n\n"
            "**Valid statuses:**\n"
            "• OPEN\n"
            "• IN\\_PROGRESS\n"
            "• FIXED\n"
            "• CLOSED\n\n"
            "**Example:**\n"
            "`/status BUG-001 FIXED`",
            parse_mode="Markdown"
        )
        return

    bug_id = context.args[0].upper()
    new_status = context.args[1].upper()

    # Validate status
    if new_status not in VALID_STATUSES:
        await update.message.reply_text(
            f"❌ **Invalid status:** `{new_status}`\n\n"
            f"**Valid statuses:**\n"
            f"• OPEN\n"
            f"• IN\\_PROGRESS\n"
            f"• FIXED\n"
            f"• CLOSED",
            parse_mode="Markdown"
        )
        return

    # Send loading message
    loading_message = await update.message.reply_text(
        f"⏳ Updating {bug_id} to {new_status}..."
    )

    try:
        # Update bug status via backend
        result = await backend_client.update_bug_status(bug_id, new_status)

        # Format success message
        success_message = (
            f"✅ **Bug updated successfully!**\n\n"
            f"**Bug ID:** {bug_id}\n"
            f"**New Status:** {new_status}\n"
        )

        # Add fixed timestamp if status is FIXED
        if new_status == "FIXED" and result.get("data", {}).get("fixed_at"):
            success_message += f"**Fixed At:** Just now\n"

        await loading_message.edit_text(success_message, parse_mode="Markdown")

        logger.info(
            f"User {user_id} updated bug {bug_id} to status {new_status}"
        )

    except BackendAPIError as e:
        logger.error(f"Failed to update bug {bug_id}: {e}")

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
                f"❌ **Failed to update bug**\n\n"
                f"Error: {str(e)}\n\n"
                f"Please try again later.",
                parse_mode="Markdown"
            )
