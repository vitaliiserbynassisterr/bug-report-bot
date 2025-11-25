#!/usr/bin/env python3
"""Clear pending Telegram updates."""

import asyncio
from telegram import Bot
from config.settings import settings

async def clear_updates():
    """Clear all pending updates by fetching them with high offset."""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    print("Clearing pending Telegram updates...")

    # Get all pending updates
    updates = await bot.get_updates()

    if not updates:
        print("✅ No pending updates to clear")
        return

    print(f"Found {len(updates)} pending updates")

    # Clear them by getting updates with offset of last update + 1
    last_update_id = updates[-1].update_id
    await bot.get_updates(offset=last_update_id + 1, timeout=1)

    print(f"✅ Cleared {len(updates)} pending updates")
    print("\nNow try sending /start or /bug to your bot on Telegram!")

if __name__ == "__main__":
    asyncio.run(clear_updates())
