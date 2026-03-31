# Intern Job Bot - Telegram Notification Service

Automatically monitor internships on internsg.com and receive Telegram notifications when new positions are posted.

## Features

- 🔍 Automated scraping of internsg.com job listings
- 📱 Real-time Telegram notifications for new postings
- 💾 PostgreSQL database to track seen jobs and prevent duplicates
- 🐳 Docker containerized for easy deployment
- 🚀 Ready for Fly.io deployment
- ⏱️ Configurable check intervals

## Prerequisites

Before you start, you'll need:

1. **Telegram Bot Token** - Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. **Telegram Chat ID** - Send a message to your bot and get your chat ID from the bot updates
3. **Fly.io Account** - Sign up at [fly.io](https://fly.io)

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
DATABASE_URL=postgresql://user:password@localhost:5432/intern_jobs
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

## Fly.io Deployment

### Step 1: Install Fly CLI

Download and install the Fly CLI from [fly.io/docs/getting-started/installing-flyctl](https://fly.io/docs/getting-started/installing-flyctl/)

### Step 2: Authenticate with Fly.io

```bash
flyctl auth login
```

### Step 3: Initialize Your App

In your project directory:

```bash
flyctl launch
```

This will:
- Create a `fly.toml` configuration file
- Detect your Dockerfile
- Prompt you to set up PostgreSQL

When prompted, select:
- **App name**: Choose a name (e.g., `internship-informer-bot`)
- **Region**: Select your preferred region
- **Add PostgreSQL?**: Yes (Fly.io will provision a database)

### Step 4: Set Environment Variables

```bash
flyctl secrets set TELEGRAM_BOT_TOKEN=your_bot_token
flyctl secrets set TELEGRAM_CHAT_ID=your_chat_id
```

Fly.io will automatically set `DATABASE_URL` from the PostgreSQL database it created.

### Step 5: Deploy

```bash
flyctl deploy
```

To monitor deployment:
```bash
flyctl logs
```

## Managing Your Deployment

### View logs
```bash
flyctl logs
```

### Check status
```bash
flyctl status
```

### Update environment variables
```bash
flyctl secrets set VARIABLE_NAME=value
```

### Scale (if needed)
```bash
flyctl scale count=1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | Required |
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by Fly.io |
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
3. Check logs: `flyctl logs`

### Database connection errors

1. Ensure DATABASE_URL is set correctly
2. Check Fly.io PostgreSQL status: `flyctl postgres status`
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

### Running Tests

```bash
# Run all tests
python -m pytest tests/test_telegram_notifications.py -v

# Run specific test
python -m pytest tests/test_telegram_notifications.py::TestTelegramNotifications::test_notification_speed -v
```

## License

MIT License

## Support

For issues or improvements, please open an issue on GitHub.
