#!/usr/bin/env python3
"""Debug script to check bot status and test connectivity."""

import asyncio
import sys
from telegram import Bot
from config.settings import settings

async def debug_bot():
    """Check bot status and configuration."""
    print("=" * 60)
    print("Telegram Bot Debug")
    print("=" * 60)

    # Create bot instance
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    try:
        # Get bot info
        print("\n1. Checking bot info...")
        me = await bot.get_me()
        print(f"   ✅ Bot connected successfully!")
        print(f"   Bot username: @{me.username}")
        print(f"   Bot ID: {me.id}")
        print(f"   Bot name: {me.first_name}")

        # Check webhook
        print("\n2. Checking webhook status...")
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            print(f"   ⚠️  WEBHOOK IS SET: {webhook_info.url}")
            print(f"   This might cause issues with polling!")
            print(f"   Pending updates: {webhook_info.pending_update_count}")
            print(f"\n   To fix: Run 'await bot.delete_webhook()' or restart Render bot")
        else:
            print(f"   ✅ No webhook set (polling mode)")
            print(f"   Pending updates: {webhook_info.pending_update_count}")

        # Check configuration
        print("\n3. Configuration:")
        print(f"   Backend API: {settings.BACKEND_API_URL}")
        print(f"   Allowed user IDs: {settings.ALLOWED_USER_IDS}")

        # Get recent updates
        print("\n4. Checking for recent updates...")
        updates = await bot.get_updates(limit=5)
        if updates:
            print(f"   Found {len(updates)} recent updates:")
            for update in updates:
                if update.message:
                    user = update.message.from_user
                    text = update.message.text or "[media]"
                    print(f"   - From user {user.id} (@{user.username}): {text}")
        else:
            print("   No recent updates")

        # Test authorization
        print("\n5. Authorization check:")
        if settings.ALLOWED_USER_IDS:
            print(f"   Authorized user IDs: {settings.ALLOWED_USER_IDS}")
            print(f"\n   💡 To find your Telegram user ID:")
            print(f"      1. Message @userinfobot on Telegram")
            print(f"      2. Or check the logs when you send a message")
        else:
            print("   ⚠️  WARNING: No allowed user IDs configured!")

        print("\n" + "=" * 60)
        print("Debug complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(debug_bot())
