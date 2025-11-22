"""Authentication utilities for the Telegram bot."""

import logging
from telegram import Update

from config.settings import settings

logger = logging.getLogger(__name__)


async def check_authorization(update: Update) -> bool:
    """
    Check if user is authorized to use the bot.

    Args:
        update: Telegram update object

    Returns:
        True if user is authorized, False otherwise
    """
    if not update.effective_user:
        return False

    user_id = update.effective_user.id
    username = update.effective_user.username or "unknown"

    if user_id not in settings.ALLOWED_USER_IDS:
        logger.warning(
            f"Unauthorized access attempt by user {user_id} (@{username})"
        )

        # Send polite rejection message
        if update.message:
            await update.message.reply_text(
                "⛔️ Sorry, you're not authorized to use this bot.\n\n"
                "This bot is restricted to specific users only. "
                "If you believe you should have access, please contact the administrator."
            )
        elif update.callback_query:
            await update.callback_query.answer(
                "You're not authorized to use this bot.",
                show_alert=True
            )

        return False

    logger.info(f"Authorized user {user_id} (@{username}) accessed the bot")
    return True


def get_user_display_name(update: Update) -> str:
    """
    Get a friendly display name for the user.

    Args:
        update: Telegram update object

    Returns:
        User's display name (first name, username, or 'User')
    """
    if not update.effective_user:
        return "User"

    user = update.effective_user
    if user.first_name:
        return user.first_name
    elif user.username:
        return f"@{user.username}"
    else:
        return "User"
