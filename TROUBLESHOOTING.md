# Troubleshooting Guide

## Bot Not Responding to Commands

### Issue: Telegram bot doesn't respond when I send /bug or other commands

#### Possible Causes & Solutions:

### 1. Multiple Bot Instances Running (MOST COMMON)

**Problem:** Both local bot and Render bot are running, competing for updates.

**Symptoms:**
- Bot seems online but doesn't respond
- No logs appear when you send commands
- Pending updates accumulate

**Solution:**
```bash
# Stop local bot
pkill -f "python.*bot.py"

# Clear pending updates
python clear_updates.py

# Try command again in Telegram
```

---

### 2. Pending Updates Stuck

**Problem:** Old updates are blocking new ones.

**Solution:**
```bash
# Run the debug script
python debug_bot.py

# If it shows "Pending updates: X" where X > 0, clear them:
python clear_updates.py
```

---

### 3. Authorization Issue

**Problem:** Your Telegram user ID is not in `ALLOWED_USER_IDS`.

**Symptoms:**
- Bot responds with "Sorry, you're not authorized"
- OR no response at all

**Solution:**
```bash
# Find your Telegram user ID:
# 1. Message @userinfobot on Telegram
# 2. Or run: python debug_bot.py

# Add your user ID to Render environment variables:
# ALLOWED_USER_IDS=286711062,YOUR_USER_ID
```

---

### 4. Webhook Conflict

**Problem:** Webhook is set but bot is trying to use polling mode.

**Symptoms:**
- Bot starts but doesn't receive updates
- Debug script shows "WEBHOOK IS SET"

**Solution:**
```python
# Create fix_webhook.py
import asyncio
from telegram import Bot
from config.settings import settings

async def fix():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted")

asyncio.run(fix())
```

Then restart Render bot.

---

### 5. Render Bot Not Actually Running

**Problem:** Deployment succeeded but bot crashed after startup.

**Check:**
1. Go to Render dashboard
2. Check logs for errors
3. Look for "Application started" message

**Common startup errors:**
- Missing environment variables
- Invalid API tokens
- Database connection issues

---

## Diagnostic Commands

### Quick Health Check
```bash
# Check if bot is reachable
python debug_bot.py
```

### Clear Stuck Updates
```bash
python clear_updates.py
```

### Check Render Logs
```bash
# Option 1: Render dashboard → Your service → Logs tab
# Option 2: Render CLI
render logs bug-report-bot
```

### Test Bot Locally
```bash
# Stop Render bot first!
# Then run locally:
source venv/bin/activate
python bot.py
```

**⚠️ IMPORTANT:** Never run local and Render bots simultaneously!

---

## Environment Variable Checklist

### Required Variables (Render):
```env
TELEGRAM_BOT_TOKEN=8076859386:AAHmh4V2EG0eIhVTKX6drBbssqP10shZNdU
BACKEND_API_URL=https://dev.api.assisterr.ai/api/v1
BACKEND_INTERNAL_TOKEN=E13YnvrdKtgi3brgUa1FmMfNGBkHVkj2
ALLOWED_USER_IDS=286711062
LOG_LEVEL=INFO
```

### Optional Variables:
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxx  # For AI features
GITHUB_TOKEN=ghp_xxx  # For auto-fix features
```

---

## Common Error Messages

### "Sorry, you're not authorized"
- **Cause:** Your user ID not in `ALLOWED_USER_IDS`
- **Fix:** Add your Telegram user ID to environment variable

### "Failed to connect to backend API"
- **Cause:** `BACKEND_API_URL` is wrong or backend is down
- **Fix:** Verify backend URL and check backend health

### "Bot is starting..." but no response
- **Cause:** Webhook conflict or multiple instances
- **Fix:** Clear webhook, stop local bot, restart Render

### No logs when sending commands
- **Cause:** Updates going to different bot instance
- **Fix:** Clear pending updates, ensure only one instance running

---

## Best Practices

### Development Workflow
1. **Local testing:** Set `BACKEND_API_URL=http://localhost:8001/api/v1`
2. **Before deploying:** Commit changes, push to GitHub
3. **After deploying:** Stop local bot immediately
4. **Clear updates:** Run `python clear_updates.py`
5. **Test on Telegram:** Send /start to verify

### Deployment Checklist
- [ ] All environment variables set on Render
- [ ] Local bot stopped (`pkill -f python.*bot.py`)
- [ ] Pending updates cleared (`python clear_updates.py`)
- [ ] Render logs show "Application started"
- [ ] Test /start command works
- [ ] Test /bug command works

### Monitoring
- Check Render logs regularly
- Monitor Render dashboard for crashes
- Keep an eye on API costs (Anthropic, if enabled)

---

## Debug Scripts

### debug_bot.py
Comprehensive bot health check:
- Bot connectivity
- Webhook status
- Pending updates
- Configuration
- Authorization setup

### clear_updates.py
Clears pending Telegram updates that may be blocking new ones.

### Usage:
```bash
# Health check
python debug_bot.py

# Clear updates
python clear_updates.py
```

---

## Still Having Issues?

1. **Check Render logs** - Most errors appear there
2. **Verify environment variables** - Especially BACKEND_API_URL
3. **Test authorization** - Message @userinfobot to get your Telegram ID
4. **Clear updates** - Run clear_updates.py
5. **Restart Render service** - Sometimes needed after env var changes

## Contact

If you continue experiencing issues:
1. Check GitHub Issues: https://github.com/vitaliiserbynassisterr/bug-report-bot/issues
2. Review Render logs for specific errors
3. Verify backend API is accessible
