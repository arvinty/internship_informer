# Fly.io Deployment Guide

Deploy your Telegram bot on Fly.io's free tier in minutes.

## Prerequisites

1. Create a Fly.io account: https://fly.io
2. Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/

## Quick Deploy

### 1. Install Fly CLI

**Windows (via Scoop):**
```powershell
scoop install flyctl
```

**Or download:** https://github.com/superfly/flyctl/releases

### 2. Login to Fly.io

```bash
flyctl auth login
```

Opens your browser to authenticate.

### 3. Deploy from GitHub

```bash
cd "c:\Users\arvin\Downloads\intern bot"
flyctl launch
```

Choose these options:
- App name: `internship-informer` (or your choice)
- Region: `sin` (Singapore) or `sjc` (San Jose) - pick closest to you
- Postgres database: **Yes**
- Deploy now: **Yes**

### 4. Set Environment Variables

```bash
flyctl config set -a internship-informer TELEGRAM_BOT_TOKEN=your_bot_token
flyctl config set -a internship-informer TELEGRAM_CHAT_ID=your_chat_id
flyctl config set -a internship-informer CHECK_INTERVAL=300
```

Or via dashboard: https://fly.io/dashboard → select app → Variables

### 5. View Logs

```bash
flyctl logs -a internship-informer
```

### 6. Verify Database Connection

```bash
flyctl postgres connect -a internship-informer
```

Then in psql:
```sql
\dt  -- List tables
\q  -- Quit
```

## Auto-Deploy from GitHub

After initial `flyctl launch`:

1. Go to https://fly.io/dashboard
2. Select your app
3. Go to **Settings** → **GitHub Integration**
4. Click **Authorize GitHub**
5. Select repo: `arvinty/internship_informer`
6. Enable auto-deploy from `main` branch

Now every push to GitHub deploys automatically!

## Useful Commands

```bash
# View app status
flyctl status -a internship-informer

# Restart app
flyctl restart -a internship-informer

# SSH into running app
flyctl ssh console -a internship-informer

# Scale instances
flyctl scale count 1 -a internship-informer

# View environment variables
flyctl config list -a internship-informer

# View logs (last 100 lines)
flyctl logs -a internship-informer -n 100

# Follow logs in real-time
flyctl logs -a internship-informer -f
```

## Troubleshooting

### Bot not starting

Check logs:
```bash
flyctl logs -a internship-informer
```

Look for database connection errors.

### Database issues

Connect to PostgreSQL:
```bash
flyctl postgres connect -a internship-informer
```

Check if `jobs` table exists:
```sql
SELECT * FROM information_schema.tables WHERE table_schema = 'public';
```

### Redeploy after code changes

If you have GitHub integration enabled, just push:
```bash
git push origin main
```

Otherwise, deploy manually:
```bash
flyctl deploy -a internship-informer
```

## Free Tier Limits

- 3 shared-cpu-1x 256MB VMs
- 3 PostgreSQL databases (3GB total)
- 160GB egress/month
- Sufficient for this bot

## Cost

**Free** - Yes, fully free tier included!

## Updating Bot Code

### Option 1: Auto-deploy from GitHub (recommended)
Just push to GitHub:
```bash
git push origin main
```

### Option 2: Manual deploy
```bash
flyctl deploy -a internship-informer
```

## Monitoring

View real-time metrics:
```bash
flyctl status -a internship-informer
```

Or via dashboard: https://fly.io/dashboard

## Next Steps

1. Deploy with `flyctl launch`
2. Set environment variables
3. Enable GitHub auto-deploy
4. Done! Bot runs continuously on free tier
