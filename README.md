# Intern Job Bot - Telegram Notification Service

Automatically monitor internships on internsg.com and receive Telegram notifications when new positions are posted.

## Features

- 🔍 Automated scraping of internsg.com job listings
- 📱 Real-time Telegram notifications for new postings
- 💾 PostgreSQL database to track seen jobs and prevent duplicates
- 🐳 Docker containerized for easy deployment
- 🚀 Ready for fly.io deployment
- ⏱️ Configurable check intervals

## Prerequisites

Before you start, you'll need:

1. **Telegram Bot Token** - Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. **Telegram Chat ID** - Send a message to your bot and get your chat ID from the bot updates
3. **Railway Account** - Sign up at [railway.app](https://railway.app)

## Local Setup

### 1. Get Your Telegram Credentials

**Create a Telegram Bot:**
1. Open Telegram and search for `@BotFather`
2. Send `/start` and then `/newbot`
3. Follow the prompts to create your bot
4. Save the API token provided

**Get Your Chat ID:**
1. Start a chat with your newly created bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Send a message to your bot
4. Refresh the URL - your chat ID is in the `chat.id` field

### 2. Clone and Setup

```bash
git clone <your-repo-url>
cd intern-bot
cp .env.example .env
```

### 3. Configure .env

Edit `.env` with your credentials:

```env
TELEGRAM_BOT_TOKEN=123456:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
DB_USER=intern_bot
DB_PASSWORD=your_secure_password
DB_NAME=intern_jobs
CHECK_INTERVAL=300
```

### 4. Run with Docker Compose

```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f bot
```

Stop:
```bash
docker-compose down
```

## Railway Deployment

### Step 1: Prepare Your Repository

Push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/intern-bot.git
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `intern-bot` repository
4. Railway will automatically detect the Dockerfile

### Step 3: Configure Environment Variables

In Railway dashboard:

1. Go to your project
2. Select the service
3. Click "Variables" tab
4. Add the following environment variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DATABASE_URL=postgresql://user:password@host:port/dbname
CHECK_INTERVAL=300
```

### Step 4: Add PostgreSQL Database

1. In Railway project, click "New"
2. Select "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` in your environment

### Step 5: Deploy

Railway will automatically deploy when you push to the main branch.

View logs:
- Click on your service in Railway dashboard
- Select "Logs" tab

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | Required |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `CHECK_INTERVAL` | Seconds between job checks | 300 |

## How It Works

1. **Scraping**: The bot uses Playwright to load the internsg.com jobs page (JavaScript-rendered content)
2. **Deduplication**: Each job is hashed based on title, company, and URL to prevent duplicate notifications
3. **Storage**: New jobs are stored in PostgreSQL with timestamps
4. **Notification**: When a new job is found, a formatted Telegram message is sent
5. **Tracking**: Notified jobs are marked to avoid re-notification

## Troubleshooting

### Bot not sending notifications

1. Check the bot token is correct: `https://api.telegram.org/botYOUR_TOKEN/getMe`
2. Verify chat ID is correct
3. Check logs: `docker-compose logs bot`

### Database connection errors

1. Ensure PostgreSQL is running
2. Check `DATABASE_URL` format
3. Verify database credentials

### No jobs found

The job selectors might need adjustment based on website changes. Edit the `scrape_jobs()` method in `bot.py` to match current HTML structure.

## Development

### Update Scraping Logic

If internsg.com changes their HTML structure, update the selectors in `bot.py`:

```python
async def scrape_jobs(self) -> List[Dict]:
    # Modify these selectors to match the website
    job_elements = await page.query_selector_all('your-selector-here')
```

### Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

## License

MIT License

## Support

For issues or improvements, please open an issue on GitHub.
