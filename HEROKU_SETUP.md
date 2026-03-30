# Heroku Deployment Guide

## Prerequisites

1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Create a Heroku account: https://www.heroku.com

## Setup Steps

### 1. Login to Heroku

```bash
heroku login
```

### 2. Create a Heroku App

```bash
heroku create your-app-name
```

Replace `your-app-name` with something unique (e.g., `internship-informer-bot`)

### 3. Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:essential-0 --app your-app-name
```

This automatically sets the `DATABASE_URL` environment variable.

### 4. Set Environment Variables

```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token --app your-app-name
heroku config:set TELEGRAM_CHAT_ID=your_chat_id --app your-app-name
heroku config:set CHECK_INTERVAL=300 --app your-app-name
```

Verify variables were set:
```bash
heroku config --app your-app-name
```

### 5. Deploy from GitHub

**Option A: Automatic Deploys (Recommended)**

1. Go to your Heroku dashboard: https://dashboard.heroku.com/apps
2. Select your app
3. Go to **Deploy** tab
4. Under "Deployment method", click **GitHub**
5. Search for `arvinty/internship_informer` and click **Connect**
6. Enable **Automatic Deploys** from the `main` branch

Now every time you push to GitHub, Heroku deploys automatically!

**Option B: Manual Deploy**

```bash
heroku git:remote --app your-app-name
git push heroku main
```

### 6. Monitor Logs

```bash
heroku logs --tail --app your-app-name
```

## Troubleshooting

### Check if bot is running

```bash
heroku ps --app your-app-name
```

### View recent logs

```bash
heroku logs --app your-app-name
```

### Restart the bot

```bash
heroku restart --app your-app-name
```

### Check environment variables

```bash
heroku config --app your-app-name
```

### Database issues

Check database connection:
```bash
heroku pg:psql --app your-app-name
\dt  # List tables
\q   # Quit
```

## Cost

- **Free tier**: No longer available
- **Eco**: $5/month for dyno + $9/month for PostgreSQL
- **Hobby**: $7/month for dyno + $9/month for PostgreSQL

## Notes

- Heroku's free tier was discontinued in late 2022
- The bot will sleep after 30 minutes of inactivity on paid plans
- For continuous operation, upgrade to at least the Eco plan
- Database is included with the plan

## Updating

Just push to GitHub and Heroku will auto-deploy:
```bash
git push origin main
```

## Useful Commands

```bash
# View app info
heroku info --app your-app-name

# Check resource usage
heroku ps --app your-app-name

# Upgrade dyno type
heroku dyno:type standard-1x --app your-app-name

# View build logs
heroku logs --source app --app your-app-name

# Scale dynos
heroku ps:scale web=1 --app your-app-name
```
