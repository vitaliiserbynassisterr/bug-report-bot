"""Handler for the /start and /help commands."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.auth import check_authorization, get_user_display_name

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command - show welcome message and instructions.

    Args:
        update: Telegram update object
        context: Callback context
    """
    # Check authorization
    if not await check_authorization(update):
        return

    user_name = get_user_display_name(update)

    welcome_message = (
        f"👋 **Welcome, {user_name}!**\n\n"
        f"I'm your bug reporting assistant. I'll help you report bugs "
        f"in the application quickly and efficiently.\n\n"
        f"**Available Commands:**\n"
        f"• /bug - Report a new bug (interactive)\n"
        f"• /mybugs - View your bug reports\n"
        f"• /view BUG-001 - View full bug details\n"
        f"• /status BUG-001 FIXED - Update bug status\n"
        f"• /stats - View overall bug statistics\n"
        f"• /help - Show this help message\n"
        f"• /cancel - Cancel current operation\n\n"
        f"**Quick Start:**\n"
        f"Type /bug to start reporting a bug. I'll guide you through the process step by step.\n\n"
        f"Let's squash some bugs! 🐛"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command - show detailed help information.

    Args:
        update: Telegram update object
        context: Callback context
    """
    # Check authorization
    if not await check_authorization(update):
        return

    help_message = (
        "📖 **Bug Reporter Help**\n\n"
        "**Reporting a Bug:**\n"
        "1. Send /bug to start\n"
        "2. Answer questions step-by-step:\n"
        "   • Describe the bug\n"
        "   • Send screenshot(s) or skip\n"
        "   • Select environment (DEV/PROD)\n"
        "   • Select priority level\n"
        "   • Add console logs (optional)\n"
        "   • Add tags (optional)\n"
        "3. Review and confirm\n"
        "4. Get your bug ID\n\n"
        "**Commands:**\n"
        "• /bug - Start new bug report\n"
        "• /mybugs - View your reports\n"
        "• /view BUG-001 - View bug details\n"
        "• /status BUG-001 FIXED - Update status\n"
        "• /stats - View statistics\n"
        "• /cancel - Cancel current operation\n"
        "• /help - Show this message\n\n"
        "**Status Values:**\n"
        "• OPEN - Bug not started\n"
        "• IN\\_PROGRESS - Being worked on\n"
        "• FIXED - Bug resolved\n"
        "• CLOSED - Bug archived\n\n"
        "**Tips:**\n"
        "• You can send multiple screenshots\n"
        "• Type 'skip' to skip optional steps\n"
        "• Use /cancel anytime to abort\n"
        "• Clear descriptions help faster fixes\n\n"
        "Need assistance? Contact your administrator."
    )

    await update.message.reply_text(help_message, parse_mode="Markdown")
    logger.info(f"User {update.effective_user.id} requested help")
