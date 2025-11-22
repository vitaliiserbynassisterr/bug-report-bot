"""Handler for interactive bug report creation."""

import logging
from typing import Dict, Any
from telegram import Update, PhotoSize
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from utils.auth import check_authorization
from utils.keyboards import (
    get_environment_keyboard,
    get_priority_keyboard,
    get_confirmation_keyboard,
)
from services.backend_client import backend_client, BackendAPIError
from services.bug_formatter import format_bug_summary, format_bug_created

logger = logging.getLogger(__name__)

# Conversation states
ASKING_DESCRIPTION = 0
ASKING_SCREENSHOTS = 1
ASKING_ENVIRONMENT = 2
ASKING_PRIORITY = 3
ASKING_CONSOLE_LOGS = 4
ASKING_TAGS = 5
CONFIRM_SUBMISSION = 6


async def start_bug_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the bug report conversation.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        Next conversation state
    """
    # Check authorization
    if not await check_authorization(update):
        return ConversationHandler.END

    # Initialize bug data in user context
    context.user_data["bug_data"] = {
        "screenshots": [],
        "reporter": {
            "telegram_id": update.effective_user.id,
            "username": update.effective_user.username,
            "first_name": update.effective_user.first_name,
            "last_name": update.effective_user.last_name,
        },
    }

    await update.message.reply_text(
        "🐛 **Let's report a bug!**\n\n"
        "Please describe the bug you encountered.\n"
        "Be as specific as possible.\n\n"
        "_(Type /cancel to abort at any time)_",
        parse_mode="Markdown",
    )

    logger.info(f"User {update.effective_user.id} started bug report")
    return ASKING_DESCRIPTION


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive bug description and ask for screenshots.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        Next conversation state
    """
    description = update.message.text.strip()

    if not description or len(description) < 10:
        await update.message.reply_text(
            "⚠️ Please provide a more detailed description (at least 10 characters)."
        )
        return ASKING_DESCRIPTION

    # Save description (use as both title and description for backend)
    # Title: truncate to first 200 chars if needed
    title = description[:200] if len(description) > 200 else description
    context.user_data["bug_data"]["title"] = title
    context.user_data["bug_data"]["description"] = description

    await update.message.reply_text(
        "📸 **Screenshots**\n\n"
        "Send one or more screenshots of the bug.\n"
        "You can send multiple photos in a row.\n\n"
        "Type 'skip' or 'done' when finished.",
        parse_mode="Markdown",
    )

    return ASKING_SCREENSHOTS


async def receive_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive screenshots from the user.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        Same state to allow multiple screenshots or next state
    """
    logger.info(f"Received message in screenshot handler. Has text: {update.message.text is not None}, Has photo: {update.message.photo is not None}")

    # Check if user wants to skip or finish
    if update.message.text:
        text = update.message.text.strip().lower()
        logger.info(f"User sent text: '{text}'")
        if text in ["skip", "done", "finish", "next"]:
            screenshot_count = len(context.user_data["bug_data"]["screenshots"])
            if screenshot_count > 0:
                await update.message.reply_text(
                    f"✅ Received {screenshot_count} screenshot(s)."
                )
            else:
                await update.message.reply_text("📝 No screenshots added.")

            # Ask for environment
            await update.message.reply_text(
                "🌍 **Environment**\n\n"
                "In which environment did you encounter this bug?",
                reply_markup=get_environment_keyboard(),
                parse_mode="Markdown",
            )
            return ASKING_ENVIRONMENT

    # Receive photo
    if update.message.photo:
        # Get the largest photo size
        photo: PhotoSize = update.message.photo[-1]

        screenshot_data = {
            "file_id": photo.file_id,
            "file_unique_id": photo.file_unique_id,
            "width": photo.width,
            "height": photo.height,
            "file_size": photo.file_size,
        }

        context.user_data["bug_data"]["screenshots"].append(screenshot_data)

        count = len(context.user_data["bug_data"]["screenshots"])
        await update.message.reply_text(
            f"✅ Screenshot {count} received!\n\n"
            f"Send more screenshots or type 'done' to continue."
        )

        return ASKING_SCREENSHOTS

    await update.message.reply_text(
        "⚠️ Please send a photo or type 'skip'/'done' to continue."
    )
    return ASKING_SCREENSHOTS


async def receive_environment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive environment selection via callback query.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    # Extract environment from callback data (format: "env_DEV" or "env_PROD")
    environment = query.data.split("_")[1]
    context.user_data["bug_data"]["environment"] = environment

    await query.edit_message_text(
        f"✅ Environment: {environment}\n\n"
        f"🎯 **Priority Level**\n\n"
        f"How critical is this bug?",
        parse_mode="Markdown",
    )

    # Send priority keyboard in a new message
    await query.message.reply_text(
        "Select priority:", reply_markup=get_priority_keyboard()
    )

    return ASKING_PRIORITY


async def receive_priority(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive priority selection via callback query.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    # Extract priority from callback data (format: "priority_LOW", etc.)
    priority = query.data.split("_")[1]
    context.user_data["bug_data"]["priority"] = priority

    await query.edit_message_text(f"✅ Priority: {priority}")

    await query.message.reply_text(
        "📋 **Console Logs**\n\n"
        "Do you have any console logs or error messages?\n"
        "Paste them here or type 'skip'.",
        parse_mode="Markdown",
    )

    return ASKING_CONSOLE_LOGS


async def receive_console_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive console logs or skip.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        Next conversation state
    """
    text = update.message.text.strip()

    if text.lower() not in ["skip", "no", "none"]:
        context.user_data["bug_data"]["console_logs"] = text
        await update.message.reply_text("✅ Console logs saved.")
    else:
        await update.message.reply_text("📝 No console logs added.")

    await update.message.reply_text(
        "🏷️ **Tags**\n\n"
        "Add tags to categorize this bug (comma-separated).\n"
        "Examples: UI, mobile, authentication\n\n"
        "Type 'skip' to skip.",
        parse_mode="Markdown",
    )

    return ASKING_TAGS


async def receive_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive tags or skip, then show summary for confirmation.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        Next conversation state
    """
    text = update.message.text.strip()

    if text.lower() not in ["skip", "no", "none"]:
        # Parse comma-separated tags
        tags = [tag.strip() for tag in text.split(",") if tag.strip()]
        context.user_data["bug_data"]["tags"] = tags
        await update.message.reply_text(f"✅ Added {len(tags)} tag(s).")
    else:
        await update.message.reply_text("📝 No tags added.")

    # Show summary
    bug_data = context.user_data["bug_data"]
    summary = format_bug_summary(bug_data)

    await update.message.reply_text(
        summary, reply_markup=get_confirmation_keyboard(), parse_mode="Markdown"
    )

    return CONFIRM_SUBMISSION


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user's confirmation choice.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        End conversation or ask for edit
    """
    query = update.callback_query
    await query.answer()

    action = query.data.split("_")[1]  # submit, edit, or cancel

    if action == "submit":
        await query.edit_message_text("⏳ Submitting bug report...")

        # Submit to backend
        try:
            bug_data = context.user_data["bug_data"]
            response = await backend_client.create_bug(bug_data)

            success_message = format_bug_created(response)
            await query.message.reply_text(success_message, parse_mode="Markdown")

            logger.info(
                f"User {update.effective_user.id} successfully created bug: "
                f"{response.get('id', 'UNKNOWN')}"
            )

            # Clear user data
            context.user_data.clear()
            return ConversationHandler.END

        except BackendAPIError as e:
            logger.error(f"Failed to create bug: {e}")
            await query.message.reply_text(
                "❌ **Failed to submit bug report**\n\n"
                f"Error: {str(e)}\n\n"
                "Please try again later or contact support.\n"
                "Your data has been saved locally.",
                parse_mode="Markdown",
            )
            return ConversationHandler.END

    elif action == "edit":
        await query.edit_message_text(
            "✏️ To edit the bug report, please start over with /bug.\n"
            "This report has been cancelled."
        )
        context.user_data.clear()
        return ConversationHandler.END

    elif action == "cancel":
        await query.edit_message_text("❌ Bug report cancelled.")
        context.user_data.clear()
        return ConversationHandler.END

    return ConversationHandler.END


async def cancel_bug_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel the bug report conversation.

    Args:
        update: Telegram update object
        context: Callback context

    Returns:
        End conversation state
    """
    await update.message.reply_text(
        "❌ Bug report cancelled.\n\n" "Use /bug to start a new report anytime."
    )

    # Clear user data
    context.user_data.clear()
    logger.info(f"User {update.effective_user.id} cancelled bug report")

    return ConversationHandler.END
