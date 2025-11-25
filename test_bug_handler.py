#!/usr/bin/env python3
"""Test bug handler to see if it works."""

import asyncio
from unittest.mock import Mock, AsyncMock
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes
from handlers.bug_report import start_bug_report

async def test():
    """Test the bug handler."""

    # Create mock update
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 286711062
    update.effective_user.username = "serbyn"
    update.effective_user.first_name = "Vitalii"
    update.effective_user.last_name = "Serbyn"

    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()

    # Create mock context
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}

    try:
        result = await start_bug_report(update, context)
        print(f"✅ Handler executed successfully!")
        print(f"   Result: {result}")
        print(f"   Reply called: {update.message.reply_text.called}")
        if update.message.reply_text.called:
            print(f"   Reply args: {update.message.reply_text.call_args}")
    except Exception as e:
        print(f"❌ Handler failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
