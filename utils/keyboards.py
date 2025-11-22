"""Keyboard utilities for creating Telegram inline keyboards."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_environment_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for environment selection.

    Returns:
        InlineKeyboardMarkup with DEV and PROD options
    """
    keyboard = [
        [
            InlineKeyboardButton("🔧 DEV", callback_data="env_DEV"),
            InlineKeyboardButton("🚀 PROD", callback_data="env_PROD"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_priority_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for priority selection.

    Returns:
        InlineKeyboardMarkup with LOW, MEDIUM, HIGH, CRITICAL options
    """
    keyboard = [
        [InlineKeyboardButton("🟢 Low", callback_data="priority_LOW")],
        [InlineKeyboardButton("🟡 Medium", callback_data="priority_MEDIUM")],
        [InlineKeyboardButton("🔴 High", callback_data="priority_HIGH")],
        [InlineKeyboardButton("💀 Critical", callback_data="priority_CRITICAL")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for bug report confirmation.

    Returns:
        InlineKeyboardMarkup with Submit, Edit, and Cancel options
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Submit", callback_data="confirm_submit"),
            InlineKeyboardButton("✏️ Edit", callback_data="confirm_edit"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="confirm_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_priority_emoji(priority: str) -> str:
    """
    Get emoji representation for priority level.

    Args:
        priority: Priority level (LOW, MEDIUM, HIGH, CRITICAL)

    Returns:
        Emoji string
    """
    priority_emojis = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🔴",
        "CRITICAL": "💀",
    }
    return priority_emojis.get(priority.upper(), "⚪️")


def get_environment_emoji(environment: str) -> str:
    """
    Get emoji representation for environment.

    Args:
        environment: Environment name (DEV, PROD)

    Returns:
        Emoji string
    """
    env_emojis = {
        "DEV": "🔧",
        "PROD": "🚀",
    }
    return env_emojis.get(environment.upper(), "❓")


def get_skip_done_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for skip/done actions (used for screenshots).

    Returns:
        InlineKeyboardMarkup with Skip and Done options
    """
    keyboard = [
        [
            InlineKeyboardButton("⏭️ Skip", callback_data="skip_action"),
            InlineKeyboardButton("✅ Done", callback_data="done_action"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard with just Skip button (for console logs and tags).

    Returns:
        InlineKeyboardMarkup with Skip option
    """
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data="skip_action")]]
    return InlineKeyboardMarkup(keyboard)


def get_status_emoji(status: str) -> str:
    """
    Get emoji representation for bug status.

    Args:
        status: Bug status

    Returns:
        Emoji string
    """
    status_emojis = {
        "OPEN": "🐛",
        "IN_PROGRESS": "🔧",
        "FIXED": "✅",
        "CLOSED": "📦",
        "WONTFIX": "🚫",
        "DUPLICATE": "👯",
    }
    return status_emojis.get(status.upper(), "❓")
