# Deployment Guide

## Quick Setup Checklist

Before deploying, you need:
- [ ] Telegram Bot Token (you have this ✅)
- [ ] Backend API URL
- [ ] Backend Internal Token (you have this ✅)
- [ ] Your Telegram User ID (get from @userinfobot)

---

## Option 1: Render.com (FREE - RECOMMENDED)

### Step 1: Prepare Repository
```bash
# Commit deployment config
git add render.yaml
git commit -m "Add Render deployment config"
git push
```

### Step 2: Deploy on Render

1. Go to https://render.com
2. Sign up with GitHub (free, no credit card)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repo: `bug-report-bot`
5. Render will detect `render.yaml` automatically
6. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`: `8076859386:AAHmh4V2EG0eIhVTKX6drBbssqP10shZNdU`
   - `BACKEND_API_URL`: Your backend URL
   - `BACKEND_INTERNAL_TOKEN`: `--ocQF6Csi7X-9RHX8FGml1ZapMczsdok4ljQ3rMNpM`
   - `ALLOWED_USER_IDS`: Your Telegram user ID
7. Click "Apply"
8. Wait 2-3 minutes for deployment

**Done!** Your bot is live 24/7.

### Free Tier Limits:
- ✅ 750 hours/month (always on)
- ✅ Auto-deploys on git push
- ✅ SSL/HTTPS included
- ✅ No credit card required

---

## Option 2: Railway.app (FREE $5 credit/month)

### Step 1: Prepare Repository
```bash
git add railway.json
git commit -m "Add Railway deployment config"
git push
```

### Step 2: Deploy on Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `bug-report-bot`
5. Railway will detect Dockerfile automatically
6. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`: `8076859386:AAHmh4V2EG0eIhVTKX6drBbssqP10shZNdU`
   - `BACKEND_API_URL`: Your backend URL
   - `BACKEND_INTERNAL_TOKEN`: `--ocQF6Csi7X-9RHX8FGml1ZapMczsdok4ljQ3rMNpM`
   - `ALLOWED_USER_IDS`: Your Telegram user ID
7. Click "Deploy"

**Done!** Bot is live.

---

## Option 3: Docker on Existing Server

If you want to deploy on the same server as your backend:

```bash
# SSH to your server
ssh user@your-server.com

# Clone repo
git clone https://github.com/vitaliiserbynassisterr/bug-report-bot.git
cd bug-report-bot

# Create .env file
nano .env
# Paste your environment variables

# Run with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down
```

---

## Local Testing (Before Deployment)

### Quick Test (Recommended)
```bash
./start-local.sh
```

### Manual Test
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py

# Press Ctrl+C to stop
```

---

## Troubleshooting

### Bot not responding
1. Check logs on Render/Railway dashboard
2. Verify `TELEGRAM_BOT_TOKEN` is correct
3. Ensure bot is started in @BotFather

### "Not authorized" error
- Verify your Telegram user ID is in `ALLOWED_USER_IDS`
- Get ID from @userinfobot

### Backend API errors
- Check `BACKEND_API_URL` is accessible from Render/Railway
- Verify `BACKEND_INTERNAL_TOKEN` is correct
- Check backend logs

---

## Cost Comparison

| Platform | Free Tier | Always On | Auto Deploy |
|----------|-----------|-----------|-------------|
| **Render.com** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Railway.app** | ✅ $5/month | ✅ Yes | ✅ Yes |
| **Heroku** | ❌ No free tier | - | - |
| **Your VPS** | 💵 $5/month | ✅ Yes | ❌ Manual |

**Recommendation**: Start with Render.com (completely free, no credit card).
