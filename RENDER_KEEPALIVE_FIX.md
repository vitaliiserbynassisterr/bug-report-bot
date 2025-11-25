# Render Free Tier Keepalive Issue

## Problem
Render free tier services can become idle/paused, causing the bot to stop polling.

## Evidence
- Bot stops polling after some time
- No errors in logs
- Flask health check still responds (port is open)
- But Telegram polling stopped

## Solution 1: External Keepalive Service (Recommended)

Use a free cron service to ping your health check endpoint every 10 minutes.

### Option A: UptimeRobot (Free)
1. Sign up at https://uptimerobot.com (free)
2. Add monitor:
   - Type: HTTP(S)
   - URL: https://bug-report-bot.onrender.com/health
   - Interval: 5 minutes
3. This keeps Render awake

### Option B: Cron-Job.org (Free)
1. Sign up at https://cron-job.org
2. Create job:
   - URL: https://bug-report-bot.onrender.com/health
   - Schedule: Every 10 minutes

## Solution 2: Self-Ping (Add to bot.py)

Add periodic self-ping to keep service active:

```python
# In bot.py, add this before main()

import threading
import time
import httpx

def keepalive_ping():
    """Ping health check endpoint every 5 minutes to keep Render awake."""
    while True:
        try:
            time.sleep(300)  # 5 minutes
            port = int(os.environ.get('PORT', 10000))
            httpx.get(f"http://localhost:{port}/health", timeout=5)
            logger.debug("Keepalive ping sent")
        except Exception as e:
            logger.error(f"Keepalive ping failed: {e}")

# In main(), before application.run_polling():
keepalive_thread = threading.Thread(target=keepalive_ping, daemon=True)
keepalive_thread.start()
```

## Solution 3: Upgrade to Paid Tier ($7/month)

Render paid tier doesn't have idle/sleep issues.

## Recommended Approach

**For Production:**
1. Use UptimeRobot (free external keepalive)
2. Monitor uptime and get alerts
3. No code changes needed

**For Development:**
- Accept that free tier sleeps
- Restart manually when needed
- Use paid tier when ready for production

## Monitoring

Add uptime monitoring:
- UptimeRobot: https://uptimerobot.com
- StatusCake: https://statuscake.com (free)
- Pingdom: https://pingdom.com (free tier)

These services will:
1. Ping your bot every 5-10 minutes
2. Keep it awake on Render
3. Alert you if it goes down
4. Show uptime statistics
