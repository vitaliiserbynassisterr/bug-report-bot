"""Formatters for displaying bug information in Telegram messages."""

from typing import Dict, List, Any
from datetime import datetime

from utils.keyboards import (
    get_priority_emoji,
    get_environment_emoji,
    get_status_emoji,
)


def format_bug_summary(bug_data: Dict[str, Any]) -> str:
    """
    Format bug data for confirmation before submission.

    Args:
        bug_data: Dictionary containing bug report data

    Returns:
        Formatted summary string
    """
    title = bug_data.get("title", "N/A")
    environment = bug_data.get("environment", "N/A")
    priority = bug_data.get("priority", "N/A")
    screenshots_count = len(bug_data.get("screenshots", []))
    console_logs = bug_data.get("console_logs", "")
    tags = bug_data.get("tags", [])

    env_emoji = get_environment_emoji(environment)
    priority_emoji = get_priority_emoji(priority)

    summary = f"📋 **Bug Report Summary:**\n\n"
    summary += f"**Title:** {title}\n"
    summary += f"**Environment:** {env_emoji} {environment}\n"
    summary += f"**Priority:** {priority_emoji} {priority}\n"

    if screenshots_count > 0:
        summary += f"**Screenshots:** {screenshots_count} attached\n"
    else:
        summary += f"**Screenshots:** None\n"

    if console_logs:
        summary += f"**Console Logs:** Yes\n"
    else:
        summary += f"**Console Logs:** None\n"

    if tags:
        tags_str = ", ".join(tags)
        summary += f"**Tags:** {tags_str}\n"
    else:
        summary += f"**Tags:** None\n"

    summary += f"\nLooks good?"

    return summary


def format_bug_created(bug_response: Dict[str, Any]) -> str:
    """
    Format response message after bug is successfully created.

    Args:
        bug_response: Response from backend API

    Returns:
        Formatted success message
    """
    # Try to get bug_id from response (backend returns bug_id at root level or in data)
    bug_id = bug_response.get("bug_id") or bug_response.get("data", {}).get("bug_id", "UNKNOWN")
    status = bug_response.get("data", {}).get("status") or bug_response.get("status", "OPEN")

    message = f"✅ **Bug created successfully!**\n\n"
    message += f"**Bug ID:** {bug_id}\n"
    message += f"**Status:** {status}\n\n"
    message += f"You'll be notified when this bug is fixed.\n"
    message += f"Use /mybugs to see all your reports."

    return message


def format_bug_list(bugs: List[Dict[str, Any]]) -> str:
    """
    Format a list of bugs for display.

    Args:
        bugs: List of bug dictionaries

    Returns:
        Formatted bug list string
    """
    if not bugs:
        return "📭 You haven't reported any bugs yet.\n\nUse /bug to create your first bug report!"

    message = "🐛 **Your Recent Bugs:**\n\n"

    for i, bug in enumerate(bugs, 1):
        bug_id = bug.get("bug_id") or bug.get("id", "UNKNOWN")
        title = bug.get("title", "Untitled")
        status = bug.get("status", "UNKNOWN")
        priority = bug.get("priority", "UNKNOWN")
        environment = bug.get("environment", "UNKNOWN")
        created_at = bug.get("created_at", "")

        status_emoji = get_status_emoji(status)
        priority_emoji = get_priority_emoji(priority)
        env_emoji = get_environment_emoji(environment)

        # Format timestamp
        time_ago = _format_time_ago(created_at)

        message += f"{i}. **{bug_id}** {priority_emoji} [{status}]\n"
        message += f"   {title}\n"
        message += f"   {env_emoji} {environment} • {time_ago}\n"

        # Add checkmark for fixed bugs
        if status.upper() in ["FIXED", "CLOSED"]:
            message += f"   ✅\n"

        message += "\n"

    return message


def format_stats(stats: Dict[str, Any]) -> str:
    """
    Format bug statistics for display.

    Args:
        stats: Statistics dictionary from backend

    Returns:
        Formatted statistics string
    """
    message = "📊 **Bug Statistics:**\n\n"

    # Total bugs
    total = stats.get("total", 0)
    message += f"**Total Bugs:** {total}\n\n"

    # By status
    by_status = stats.get("by_status", {})
    if by_status:
        message += "**By Status:**\n"
        for status, count in by_status.items():
            status_emoji = get_status_emoji(status)
            # Escape underscores for Markdown
            status_display = status.replace("_", "\\_")
            message += f"  {status_emoji} {status_display}: {count}\n"
        message += "\n"

    # By priority
    by_priority = stats.get("by_priority", {})
    if by_priority:
        message += "**By Priority:**\n"
        for priority, count in by_priority.items():
            priority_emoji = get_priority_emoji(priority)
            priority_display = priority.replace("_", "\\_")
            message += f"  {priority_emoji} {priority_display}: {count}\n"
        message += "\n"

    # By environment
    by_environment = stats.get("by_environment", {})
    if by_environment:
        message += "**By Environment:**\n"
        for env, count in by_environment.items():
            env_emoji = get_environment_emoji(env)
            env_display = env.replace("_", "\\_")
            message += f"  {env_emoji} {env_display}: {count}\n"

    return message


def format_bug_details(bug: Dict[str, Any]) -> str:
    """
    Format detailed bug information for /view command.

    Args:
        bug: Bug dictionary from backend

    Returns:
        Formatted detailed bug information
    """
    bug_id = bug.get("bug_id") or bug.get("id", "UNKNOWN")
    title = bug.get("title", "Untitled")
    description = bug.get("description", "No description")
    status = bug.get("status", "UNKNOWN")
    priority = bug.get("priority", "UNKNOWN")
    environment = bug.get("environment", "UNKNOWN")
    created_at = bug.get("created_at", "")
    updated_at = bug.get("updated_at", "")
    fixed_at = bug.get("fixed_at", "")
    console_logs = bug.get("console_logs", "")
    tags = bug.get("tags", [])
    screenshots = bug.get("screenshots", [])
    assignee = bug.get("assignee", "")
    github_pr = bug.get("github_pr", "")
    reporter = bug.get("reporter", {})
    notes = bug.get("notes", [])

    # Get emojis
    status_emoji = get_status_emoji(status)
    priority_emoji = get_priority_emoji(priority)
    env_emoji = get_environment_emoji(environment)

    # Build message
    message = f"🐛 **Bug Details**\n\n"
    message += f"**ID:** {bug_id}\n"
    message += f"**Title:** {title}\n\n"
    message += f"**Description:**\n{description}\n\n"
    message += f"**Status:** {status_emoji} {status}\n"
    message += f"**Priority:** {priority_emoji} {priority}\n"
    message += f"**Environment:** {env_emoji} {environment}\n\n"

    # Reporter info
    reporter_name = reporter.get("first_name", "Unknown")
    if reporter.get("username"):
        reporter_name += f" (@{reporter.get('username')})"
    message += f"**Reported by:** {reporter_name}\n"

    # Timestamps
    if created_at:
        time_ago = _format_time_ago(created_at)
        message += f"**Created:** {time_ago}\n"

    if updated_at:
        time_ago = _format_time_ago(updated_at)
        message += f"**Updated:** {time_ago}\n"

    if fixed_at:
        time_ago = _format_time_ago(fixed_at)
        message += f"**Fixed:** {time_ago}\n"

    # Assignee
    if assignee:
        message += f"**Assignee:** {assignee}\n"

    # GitHub PR
    if github_pr:
        message += f"**GitHub PR:** {github_pr}\n"

    message += "\n"

    # Screenshots
    if screenshots:
        message += f"**Screenshots:** {len(screenshots)} attached\n"

    # Console logs
    if console_logs:
        # Truncate if too long
        logs_preview = console_logs[:200] + "..." if len(console_logs) > 200 else console_logs
        message += f"**Console Logs:**\n`{logs_preview}`\n\n"

    # Tags
    if tags:
        tags_str = ", ".join(tags)
        message += f"**Tags:** {tags_str}\n\n"

    # Notes
    if notes:
        message += f"**Notes ({len(notes)}):**\n"
        for i, note in enumerate(notes[:3], 1):  # Show max 3 notes
            author = note.get("author", "Unknown")
            text = note.get("text", "")
            timestamp = note.get("timestamp", "")
            time_ago = _format_time_ago(timestamp) if timestamp else ""

            # Truncate note if too long
            text_preview = text[:100] + "..." if len(text) > 100 else text
            message += f"{i}. **{author}** ({time_ago}):\n   {text_preview}\n"

        if len(notes) > 3:
            message += f"   ... and {len(notes) - 3} more notes\n"

    return message


def _format_time_ago(timestamp_str: str) -> str:
    """
    Format timestamp as relative time (e.g., '2 hours ago').

    Args:
        timestamp_str: ISO format timestamp string

    Returns:
        Formatted relative time string
    """
    if not timestamp_str:
        return "unknown time"

    try:
        # Parse ISO format timestamp
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timestamp.tzinfo)

        delta = now - timestamp
        seconds = delta.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    except Exception:
        return "unknown time"
