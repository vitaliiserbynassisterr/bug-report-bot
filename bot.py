"""Main entry point for the Telegram bug reporting bot."""

import logging
import sys

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from config.settings import settings
from handlers.start import start_command, help_command
from handlers.bug_report import (
    start_bug_report,
    receive_description,
    receive_screenshot,
    receive_environment,
    receive_priority,
    receive_console_logs,
    receive_tags,
    handle_confirmation,
    cancel_bug_report,
    ASKING_DESCRIPTION,
    ASKING_SCREENSHOTS,
    ASKING_ENVIRONMENT,
    ASKING_PRIORITY,
    ASKING_CONSOLE_LOGS,
    ASKING_TAGS,
    CONFIRM_SUBMISSION,
)
from handlers.my_bugs import my_bugs_command
from handlers.stats import stats_command

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    try:
        # Validate settings
        logger.info("Initializing Telegram bug reporting bot...")
        logger.info(f"Backend API URL: {settings.BACKEND_API_URL}")
        logger.info(f"Allowed user IDs: {settings.ALLOWED_USER_IDS}")

        # Create application
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        # Bug report conversation handler
        bug_report_handler = ConversationHandler(
            entry_points=[CommandHandler("bug", start_bug_report)],
            states={
                ASKING_DESCRIPTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)
                ],
                ASKING_SCREENSHOTS: [
                    MessageHandler(
                        (filters.PHOTO | filters.TEXT) & ~filters.COMMAND,
                        receive_screenshot,
                    )
                ],
                ASKING_ENVIRONMENT: [
                    CallbackQueryHandler(receive_environment, pattern="^env_")
                ],
                ASKING_PRIORITY: [
                    CallbackQueryHandler(receive_priority, pattern="^priority_")
                ],
                ASKING_CONSOLE_LOGS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_console_logs)
                ],
                ASKING_TAGS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tags)
                ],
                CONFIRM_SUBMISSION: [
                    CallbackQueryHandler(handle_confirmation, pattern="^confirm_")
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_bug_report)],
            per_message=False,
        )

        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(bug_report_handler)
        application.add_handler(CommandHandler("mybugs", my_bugs_command))
        application.add_handler(CommandHandler("stats", stats_command))

        # Start the bot
        logger.info("Bot is starting...")
        application.run_polling(allowed_updates=["message", "callback_query"])

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
